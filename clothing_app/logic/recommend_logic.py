"""
recommend_logic.py

점수 기반 옷 추천 로직
- 색상 조합
- 온도 적합도
- 체형/키/몸무게
- 피부톤/퍼스널 컬러
- 선호 스타일
- 코디 완성도
- 사진 대표색 자동 추출 보조 함수

기존 코드와 충돌을 줄이기 위해 item/user 객체가 dict든 class든 모두 처리합니다.
"""

from itertools import product
from math import isfinite
from collections import Counter

# -----------------------------
# 공통 유틸
# -----------------------------

NEUTRAL_COLORS = {"검정", "흰색", "회색", "아이보리", "베이지", "네이비"}
DARK_COLORS = {"검정", "네이비", "차콜", "진회색", "브라운", "카키"}
LIGHT_COLORS = {"흰색", "아이보리", "베이지", "연회색", "하늘색", "핑크", "크림"}
WARM_COLORS = {"베이지", "브라운", "카멜", "카키", "아이보리", "크림", "노랑", "오렌지", "빨강"}
COOL_COLORS = {"검정", "흰색", "회색", "네이비", "파랑", "하늘색", "보라", "버건디", "핑크"}


def get_value(obj, *names, default=None):
    """dict/class 모두에서 안전하게 값을 꺼냅니다."""
    if obj is None:
        return default
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj.get(name, default)
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_color(color):
    color = normalize_text(color)
    aliases = {
        "black": "검정", "white": "흰색", "gray": "회색", "grey": "회색",
        "navy": "네이비", "beige": "베이지", "brown": "브라운",
        "red": "빨강", "pink": "핑크", "yellow": "노랑",
        "blue": "파랑", "green": "초록", "khaki": "카키",
        "아이보리색": "아이보리", "하양": "흰색", "흰": "흰색",
        "검은색": "검정", "검정색": "검정", "까만색": "검정",
        "남색": "네이비", "곤색": "네이비",
    }
    return aliases.get(color, color)


def item_category(item):
    return normalize_text(get_value(item, "category", "type", default=""))


def item_detail(item):
    return normalize_text(get_value(item, "detail", "sub_category", "subtype", "name", default=""))


def item_color(item):
    return normalize_color(get_value(item, "color_name", "color", "main_color", default=""))


def item_feature(item):
    return normalize_text(get_value(item, "feature", "fit", "material", default=""))


def item_style(item):
    raw = get_value(item, "style", "styles", "fashion_style", default="")
    if isinstance(raw, (list, tuple, set)):
        return [normalize_text(x) for x in raw if normalize_text(x)]
    if not raw:
        return []
    return [x.strip() for x in str(raw).replace("/", ",").split(",") if x.strip()]


def user_styles(user):
    raw = get_value(user, "styles", "preferred_styles", "style", "fashion_styles", default="")
    if isinstance(raw, (list, tuple, set)):
        return [normalize_text(x) for x in raw if normalize_text(x)]
    if not raw:
        return []
    # DB에 "캐주얼,미니멀" 또는 "캐주얼/미니멀"로 저장된 경우 처리
    return [x.strip() for x in str(raw).replace("/", ",").split(",") if x.strip()]


# -----------------------------
# 기존 색상 설명 함수 유지/확장
# -----------------------------

def get_color_style_info(color_name):
    color_name = normalize_color(color_name)
    rules = {
        "검정": {
            "recommended": ["흰색", "회색", "베이지", "카키", "네이비"],
            "avoid": ["짙은브라운"],
            "reason": "검정은 무채색이라 대부분의 색과 잘 어울리고 안정적인 코디를 만들기 쉽습니다.",
            "avoid_reason": "너무 어두운 색끼리 겹치면 전체가 답답해 보일 수 있습니다."
        },
        "흰색": {
            "recommended": ["검정", "네이비", "베이지", "카키"],
            "avoid": ["형광색"],
            "reason": "흰색은 밝고 깔끔해서 명도 차이를 주기 좋은 기본 색입니다.",
            "avoid_reason": "형광색과 만나면 흰색의 깔끔한 느낌이 약해질 수 있습니다."
        },
        "회색": {
            "recommended": ["검정", "흰색", "네이비", "베이지"],
            "avoid": ["탁한갈색"],
            "reason": "회색은 차분한 색이라 대부분의 기본 색과 무난하게 어울립니다.",
            "avoid_reason": "탁한 갈색과 겹치면 전체적으로 흐릿해 보일 수 있습니다."
        },
        "네이비": {
            "recommended": ["흰색", "베이지", "회색", "카키"],
            "avoid": ["짙은파랑", "보라"],
            "reason": "네이비는 단정하고 깔끔한 분위기를 만들기 좋은 색입니다.",
            "avoid_reason": "비슷하게 어두운 푸른 계열과 겹치면 색 차이가 애매해 보일 수 있습니다."
        },
        "베이지": {
            "recommended": ["검정", "흰색", "네이비", "브라운", "카키"],
            "avoid": ["형광노랑"],
            "reason": "베이지는 부드러운 톤이라 자연스러운 코디를 만들기 쉽습니다.",
            "avoid_reason": "지나치게 튀는 색과 조합하면 차분한 분위기가 깨질 수 있습니다."
        },
        "카키": {
            "recommended": ["검정", "아이보리", "베이지", "흰색", "브라운"],
            "avoid": ["선명한빨강"],
            "reason": "카키는 자연 계열 색이라 무난하면서도 스타일 있는 조합이 가능합니다.",
            "avoid_reason": "강한 빨강과 만나면 대비가 너무 커질 수 있습니다."
        },
        "브라운": {
            "recommended": ["베이지", "아이보리", "흰색", "카키"],
            "avoid": ["검정"],
            "reason": "브라운은 따뜻한 느낌이라 부드러운 색과 잘 어울립니다.",
            "avoid_reason": "아주 진한 검정과 붙으면 브라운의 따뜻한 느낌이 줄어듭니다."
        },
        "빨강": {
            "recommended": ["검정", "흰색", "회색", "네이비"],
            "avoid": ["초록"],
            "reason": "빨강은 포인트 색이라 무채색과 매치하면 깔끔하게 살아납니다.",
            "avoid_reason": "초록과는 대비가 너무 강해 일상 코디에 부담이 될 수 있습니다."
        },
        "핑크": {
            "recommended": ["흰색", "회색", "네이비", "베이지"],
            "avoid": ["선명한초록"],
            "reason": "핑크는 부드러운 느낌이 있어 밝고 차분한 색과 잘 어울립니다.",
            "avoid_reason": "강한 초록과 만나면 색 충돌이 커질 수 있습니다."
        },
        "노랑": {
            "recommended": ["검정", "흰색", "네이비", "회색"],
            "avoid": ["형광초록"],
            "reason": "노랑은 시선이 가는 색이라 기본 색과 조합했을 때 더 안정적입니다.",
            "avoid_reason": "너무 강한 밝은색끼리 만나면 눈에 부담이 될 수 있습니다."
        },
        "파랑": {
            "recommended": ["흰색", "회색", "베이지", "검정"],
            "avoid": ["짙은보라"],
            "reason": "파랑은 시원하고 깔끔한 이미지를 주는 색입니다.",
            "avoid_reason": "어두운 유사 계열과 겹치면 전체가 무거워 보일 수 있습니다."
        },
        "초록": {
            "recommended": ["검정", "베이지", "흰색", "브라운"],
            "avoid": ["강한빨강"],
            "reason": "초록은 자연스러운 색이라 베이지, 브라운 계열과 잘 어울립니다.",
            "avoid_reason": "강한 빨강과는 대비가 커서 난이도가 높습니다."
        }
    }

    return rules.get(color_name, {
        "recommended": ["검정", "흰색", "회색", "베이지", "네이비"],
        "avoid": ["너무 강한 원색 조합"],
        "reason": "중립적인 색 조합을 우선 추천합니다.",
        "avoid_reason": "강한 색끼리 만나면 코디가 복잡해 보일 수 있습니다."
    })


def explain_match(top_name, bottom_name):
    top_name = normalize_color(top_name)
    bottom_name = normalize_color(bottom_name)

    good_pairs = {
        ("검정", "흰색"): "강한 명도 차이를 활용한 가장 기본적인 조합입니다.",
        ("검정", "베이지"): "어두운 상의와 부드러운 하의 조합으로 안정적입니다.",
        ("네이비", "베이지"): "단정하고 깔끔한 분위기를 주는 대표 조합입니다.",
        ("흰색", "네이비"): "깔끔하면서도 부담 없는 조합입니다.",
        ("카키", "베이지"): "자연 계열 톤온톤 조합으로 부드럽고 세련된 느낌을 줍니다.",
        ("회색", "검정"): "차분한 무채색 조합이라 실패 확률이 낮습니다.",
        ("빨강", "검정"): "포인트 컬러를 무채색으로 눌러줘 균형이 좋습니다.",
        ("핑크", "회색"): "부드럽고 안정적인 이미지가 잘 살아납니다.",
        ("베이지", "브라운"): "따뜻한 톤온톤 조합으로 자연스럽고 안정적입니다.",
        ("아이보리", "카키"): "밝은 상의와 차분한 하의가 균형을 잡아줍니다.",
    }

    bad_pairs = {
        ("빨강", "초록"): "대비가 너무 강해서 일상 코디로는 부담스러울 수 있습니다.",
        ("초록", "빨강"): "대비가 너무 강해서 일상 코디로는 부담스러울 수 있습니다.",
        ("카키", "빨강"): "톤이 충돌해 전체적으로 어수선해 보일 수 있습니다.",
        ("검정", "브라운"): "둘 다 어두운 톤이면 답답해 보일 수 있습니다."
    }

    if (top_name, bottom_name) in good_pairs:
        return True, good_pairs[(top_name, bottom_name)]
    if (bottom_name, top_name) in good_pairs:
        return True, good_pairs[(bottom_name, top_name)]
    if (top_name, bottom_name) in bad_pairs:
        return False, bad_pairs[(top_name, bottom_name)]

    if top_name == bottom_name:
        return True, "같은 계열 색상으로 통일감을 줄 수 있습니다."
    if top_name in NEUTRAL_COLORS or bottom_name in NEUTRAL_COLORS:
        return True, "무채색 또는 기본색이 포함되어 있어 전체적으로 안정적인 코디를 만들기 쉽습니다."

    return True, "무난한 조합이지만 신발이나 아우터에 무채색을 더하면 더 자연스럽습니다."


# -----------------------------
# 온도 추천
# -----------------------------

def get_temperature_recommendation(temp):
    try:
        temp = float(temp)
    except Exception:
        temp = 22

    if temp >= 28:
        return {
            "top": ["반팔", "민소매", "린넨", "얇은 셔츠"],
            "bottom": ["반바지", "얇은 바지", "린넨 팬츠"],
            "outer": [],
            "reason": "매우 더운 날씨라 통풍이 잘 되는 얇은 옷이 좋습니다.",
            "avoid": "두꺼운 니트, 패딩, 기모류"
        }
    elif temp >= 23:
        return {
            "top": ["반팔", "셔츠", "얇은 긴팔"],
            "bottom": ["청바지", "슬랙스", "반바지", "면바지"],
            "outer": ["얇은 가디건", "얇은 셔츠"],
            "reason": "조금 더운 날씨라 가벼운 상의 위주가 좋고, 얇은 겉옷 정도면 충분합니다.",
            "avoid": "두꺼운 코트, 패딩"
        }
    elif temp >= 17:
        return {
            "top": ["긴팔", "맨투맨", "셔츠", "니트"],
            "bottom": ["청바지", "슬랙스", "면바지"],
            "outer": ["가디건", "얇은 자켓", "후드집업"],
            "reason": "선선한 날씨라 긴팔이나 가벼운 겉옷이 잘 맞습니다.",
            "avoid": "민소매, 한겨울용 패딩"
        }
    elif temp >= 10:
        return {
            "top": ["긴팔", "니트", "맨투맨", "후드"],
            "bottom": ["청바지", "슬랙스", "두꺼운 바지"],
            "outer": ["자켓", "코트", "후리스", "가죽자켓"],
            "reason": "쌀쌀한 날씨라 보온이 되는 상의와 겉옷이 필요합니다.",
            "avoid": "반팔 단독 착용"
        }
    else:
        return {
            "top": ["니트", "기모 맨투맨", "후드"],
            "bottom": ["두꺼운 바지", "기모 바지"],
            "outer": ["패딩", "두꺼운 코트", "후리스"],
            "reason": "추운 날씨라 보온이 가장 중요합니다.",
            "avoid": "반팔, 반바지, 얇은 셔츠"
        }


# -----------------------------
# 점수 계산
# -----------------------------

PERSONAL_COLOR_RULES = {
    "봄웜": ["아이보리", "크림", "베이지", "핑크", "노랑", "오렌지", "카멜"],
    "봄 웜": ["아이보리", "크림", "베이지", "핑크", "노랑", "오렌지", "카멜"],
    "여름쿨": ["흰색", "회색", "하늘색", "파랑", "네이비", "핑크"],
    "여름 쿨": ["흰색", "회색", "하늘색", "파랑", "네이비", "핑크"],
    "가을웜": ["베이지", "브라운", "카키", "카멜", "머스타드", "아이보리"],
    "가을 웜": ["베이지", "브라운", "카키", "카멜", "머스타드", "아이보리"],
    "겨울쿨": ["검정", "흰색", "네이비", "버건디", "회색", "파랑"],
    "겨울 쿨": ["검정", "흰색", "네이비", "버건디", "회색", "파랑"],
}


def score_color(outfit):
    """색상 조합 25점"""
    items = [x for x in outfit.values() if x is not None]
    colors = [item_color(x) for x in items if item_color(x)]

    if len(colors) <= 1:
        return 16, ["색상 정보가 적어 기본 점수를 적용했습니다."]

    score = 12
    reasons = []

    # 상의-하의 중심 조합
    top = outfit.get("top")
    bottom = outfit.get("bottom")
    if top and bottom:
        ok, reason = explain_match(item_color(top), item_color(bottom))
        if ok:
            score += 8
        else:
            score -= 4
        reasons.append(reason)

    # 무채색/기본색 포함
    if any(c in NEUTRAL_COLORS for c in colors):
        score += 3
        reasons.append("무채색 또는 기본색이 포함되어 전체 조합이 안정적입니다.")

    # 너무 많은 강한 색 방지
    non_neutral = [c for c in colors if c not in NEUTRAL_COLORS]
    if len(set(non_neutral)) >= 3:
        score -= 3
        reasons.append("강한 색이 여러 개 섞여 있어 약간 복잡해 보일 수 있습니다.")

    # 같은 색 과다 사용
    most_common_count = Counter(colors).most_common(1)[0][1]
    if most_common_count >= 3:
        score -= 2
        reasons.append("비슷한 색이 많이 반복되어 단조로울 수 있습니다.")

    return max(0, min(25, score)), reasons[:3]


def score_temperature(outfit, temp):
    """온도 적합도 20점. 입력 기온이 추천 순위에 확실히 반영되도록 가중치를 강하게 둡니다."""
    try:
        temp = float(temp)
    except Exception:
        temp = 22

    score = 10
    reasons = []
    rec = get_temperature_recommendation(temp)

    warm_keywords = ["패딩", "코트", "후리스", "기모", "두꺼", "니트", "후드", "가죽자켓", "자켓", "재킷"]
    cool_keywords = ["반팔", "민소매", "반바지", "린넨", "얇은", "시원", "통풍"]

    for part, item in outfit.items():
        if item is None:
            continue
        detail = item_detail(item)
        feature = item_feature(item)
        color = item_color(item)
        text = f"{detail} {feature} {color}"

        good_keywords = rec.get(part, [])
        if any(k in text for k in good_keywords):
            score += 4
            reasons.append(f"{detail}은(는) 현재 기온에 잘 맞습니다.")

        if temp >= 28:
            if any(k in text for k in warm_keywords):
                score -= 9
                reasons.append("더운 날씨에는 두꺼운 옷이나 아우터가 답답할 수 있습니다.")
            if any(k in text for k in cool_keywords):
                score += 5
                reasons.append("더운 날씨에 가볍고 통풍이 좋은 아이템이 포함되었습니다.")
        elif temp >= 23:
            if any(k in text for k in ["패딩", "두꺼", "기모", "코트"]):
                score -= 6
                reasons.append("따뜻한 날씨에는 두꺼운 아이템보다 가벼운 옷이 더 적합합니다.")
        elif temp <= 10:
            if any(k in text for k in cool_keywords):
                score -= 9
                reasons.append("추운 날씨에는 얇은 옷이나 짧은 옷이 부족할 수 있습니다.")
            if any(k in text for k in warm_keywords):
                score += 5
                reasons.append("추운 날씨에 보온성 있는 아이템이 포함되었습니다.")
        elif temp <= 16:
            if any(k in text for k in ["반팔", "민소매", "반바지"]):
                score -= 5
                reasons.append("쌀쌀한 날씨에는 짧은 옷 단독 착용이 조금 추울 수 있습니다.")

    has_outer = outfit.get("outer") is not None
    if temp <= 16 and has_outer:
        score += 5
        reasons.append("쌀쌀한 날씨에 아우터가 포함되어 보온성이 좋습니다.")
    elif temp <= 12 and not has_outer:
        score -= 7
        reasons.append("추운 날씨라 아우터가 있으면 더 적합합니다.")
    elif temp >= 27 and has_outer:
        score -= 7
        reasons.append("더운 날씨라 아우터는 제외하는 편이 더 좋습니다.")
    elif temp >= 27 and not has_outer:
        score += 3
        reasons.append("더운 날씨라 아우터 없이 가볍게 입는 구성이 좋습니다.")

    if not reasons:
        reasons.append(rec["reason"])

    return max(0, min(20, score)), reasons[:3]

def score_body(user, outfit):
    """체형/키/몸무게 적합도 20점"""
    body_type = normalize_text(get_value(user, "body_type", "body", default=""))
    try:
        height = float(get_value(user, "height", default=0) or 0)
        weight = float(get_value(user, "weight", default=0) or 0)
    except Exception:
        height, weight = 0, 0

    score = 10
    reasons = []
    items = [x for x in outfit.values() if x is not None]
    texts = " ".join([f"{item_detail(x)} {item_feature(x)} {item_color(x)}" for x in items])

    if "마른" in body_type:
        if any(k in texts for k in ["오버핏", "레이어드", "맨투맨", "후드", "니트"]):
            score += 5
            reasons.append("마른 체형에는 약간의 볼륨감이 있는 핏이 균형을 잡아줍니다.")
        if "슬림" in texts:
            score -= 2
            reasons.append("너무 슬림한 핏은 체형이 더 말라 보일 수 있습니다.")

    elif any(k in body_type for k in ["통통", "큰", "하체", "상체"]):
        if any(item_color(x) in DARK_COLORS for x in items):
            score += 4
            reasons.append("어두운 색이 포함되어 실루엣이 깔끔하게 정리됩니다.")
        if any(k in texts for k in ["정핏", "스트레이트", "슬랙스"]):
            score += 4
            reasons.append("정돈된 핏이 체형을 자연스럽게 보완합니다.")
        if "오버핏" in texts:
            score -= 1
            reasons.append("과한 오버핏은 오히려 부피감이 커 보일 수 있습니다.")

    elif any(k in body_type for k in ["근육", "운동"]):
        if any(k in texts for k in ["정핏", "슬림", "셔츠", "반팔"]):
            score += 5
            reasons.append("근육형 체형에는 깔끔한 핏이 장점을 살려줍니다.")

    else:
        score += 3
        reasons.append("기본적인 상하의 균형이 무난한 조합입니다.")

    # 키가 작은 편이면 상하의 색 대비 과다 감점
    top = outfit.get("top")
    bottom = outfit.get("bottom")
    if height and height < 165 and top and bottom:
        top_c, bottom_c = item_color(top), item_color(bottom)
        if (top_c in LIGHT_COLORS and bottom_c in DARK_COLORS) or (top_c in DARK_COLORS and bottom_c in LIGHT_COLORS):
            score -= 2
            reasons.append("키가 작은 편이라면 상하의 대비가 너무 크지 않은 조합이 더 길어 보일 수 있습니다.")

    return max(0, min(20, score)), reasons[:3]


def score_personal_color(user, outfit):
    """피부톤/퍼스널컬러 15점"""
    skin_tone = normalize_text(get_value(user, "skin_tone", "skin", default=""))
    personal = normalize_text(get_value(user, "personal_color", "personal", default=""))

    items = [x for x in outfit.values() if x is not None]
    colors = [item_color(x) for x in items if item_color(x)]

    score = 7
    reasons = []

    preferred = []
    for key, values in PERSONAL_COLOR_RULES.items():
        if key and key in personal:
            preferred = values
            break

    if preferred:
        matched = [c for c in colors if c in preferred]
        if matched:
            score += min(6, len(set(matched)) * 3)
            reasons.append(f"{', '.join(sorted(set(matched)))} 색상이 퍼스널 컬러와 잘 어울립니다.")

    if "웜" in skin_tone and any(c in WARM_COLORS for c in colors):
        score += 3
        reasons.append("웜톤 피부에 어울리는 따뜻한 계열 색이 포함되어 있습니다.")
    elif "쿨" in skin_tone and any(c in COOL_COLORS for c in colors):
        score += 3
        reasons.append("쿨톤 피부에 어울리는 차가운 계열 색이 포함되어 있습니다.")
    elif not reasons:
        reasons.append("피부톤 정보가 부족해 기본 색상 균형을 중심으로 평가했습니다.")

    return max(0, min(15, score)), reasons[:3]


def score_style(user, outfit):
    """선호 스타일 15점"""
    pref = set(user_styles(user))
    if not pref:
        return 8, ["선호 스타일 정보가 없어 무난한 스타일 점수를 적용했습니다."]

    items = [x for x in outfit.values() if x is not None]
    styles = set()
    for item in items:
        styles.update(item_style(item))

    # item에 style 정보가 없으면 detail/feature로 추론
    text = " ".join([f"{item_detail(x)} {item_feature(x)}" for x in items])
    inferred = set()
    inference_rules = {
        "캐주얼": ["맨투맨", "후드", "청바지", "반팔", "스니커즈"],
        "미니멀": ["슬랙스", "셔츠", "니트", "코트", "무지"],
        "스트릿": ["오버핏", "후드", "와이드", "카고"],
        "댄디": ["셔츠", "슬랙스", "자켓", "코트"],
        "스포티": ["트레이닝", "운동화", "집업", "져지"],
        "힙": ["오버핏", "와이드", "카고", "크롭"],
    }
    for style, keywords in inference_rules.items():
        if any(k in text for k in keywords):
            inferred.add(style)

    all_styles = styles | inferred
    matched = pref & all_styles

    if matched:
        return 15, [f"선호 스타일({', '.join(sorted(matched))})이 코디에 반영되었습니다."]
    if all_styles:
        return 7, [f"코디 스타일은 {', '.join(sorted(all_styles))}에 가깝지만 선호 스타일과는 차이가 있습니다."]
    return 8, ["스타일 태그가 부족해 기본 점수를 적용했습니다."]




SITUATION_RULES = {
    "데일리": {
        "good": ["맨투맨", "후드", "청바지", "반팔", "긴팔", "스니커즈", "운동화", "가디건", "면바지", "와이드"],
        "bad": ["정장", "구두", "블레이저"],
        "reason": "데일리 상황에는 편하고 부담 없는 아이템이 잘 맞습니다."
    },
    "출근": {
        "good": ["셔츠", "슬랙스", "자켓", "재킷", "블레이저", "코트", "니트", "로퍼", "구두", "가디건", "검정", "네이비", "회색", "베이지"],
        "bad": ["반바지", "민소매", "후드", "트레이닝", "찢어진", "크롭"],
        "reason": "출근에는 단정한 색과 셔츠, 슬랙스, 자켓 계열이 안정적입니다."
    },
    "데이트": {
        "good": ["니트", "셔츠", "가디건", "코트", "슬랙스", "스커트", "아이보리", "베이지", "핑크", "하늘색", "브라운"],
        "bad": ["트레이닝", "후리스", "패딩", "운동복"],
        "reason": "데이트에는 부드러운 색감과 깔끔한 핏의 아이템이 좋은 인상을 줍니다."
    },
    "학교": {
        "good": ["맨투맨", "후드", "청바지", "면바지", "스니커즈", "운동화", "가디건", "백팩", "반팔", "긴팔"],
        "bad": ["정장", "구두", "너무 화려"],
        "reason": "학교에서는 활동하기 편한 캐주얼 아이템이 자연스럽습니다."
    },
    "운동": {
        "good": ["트레이닝", "운동화", "반팔", "민소매", "집업", "져지", "후드집업", "레깅스", "스포티", "조거"],
        "bad": ["코트", "구두", "슬랙스", "셔츠", "니트"],
        "reason": "운동 상황에는 움직임이 편하고 가벼운 스포티 아이템이 적합합니다."
    },
    "중요한 날": {
        "good": ["셔츠", "슬랙스", "자켓", "재킷", "블레이저", "코트", "구두", "로퍼", "검정", "네이비", "흰색", "아이보리"],
        "bad": ["후드", "트레이닝", "반바지", "민소매", "찢어진"],
        "reason": "중요한 날에는 단정하고 정리된 아이템을 우선 추천합니다."
    },
}


def score_situation(outfit, situation="데일리"):
    """상황 적합도 15점"""
    situation = normalize_text(situation) or "데일리"
    rule = SITUATION_RULES.get(situation, SITUATION_RULES["데일리"])
    items = [x for x in outfit.values() if x is not None]
    texts = []
    for item in items:
        texts.append(f"{item_category(item)} {item_detail(item)} {item_feature(item)} {item_color(item)} {' '.join(item_style(item))}")
    joined = " ".join(texts)

    score = 7
    reasons = []
    matched_good = [k for k in rule["good"] if k and k in joined]
    matched_bad = [k for k in rule["bad"] if k and k in joined]

    if matched_good:
        score += min(8, len(set(matched_good)) * 2)
        reasons.append(f"{situation} 상황에 어울리는 요소({', '.join(sorted(set(matched_good))[:3])})가 포함되어 있습니다.")
    if matched_bad:
        score -= min(7, len(set(matched_bad)) * 3)
        reasons.append(f"{situation} 상황에는 {', '.join(sorted(set(matched_bad))[:2])} 아이템이 조금 덜 어울릴 수 있습니다.")
    if not reasons:
        reasons.append(rule["reason"])

    return max(0, min(15, score)), reasons[:3]

def score_completeness(outfit):
    """코디 완성도 5점"""
    required = ["top", "bottom"]
    score = 0
    reasons = []

    if all(outfit.get(x) is not None for x in required):
        score += 3
        reasons.append("상의와 하의가 모두 포함되어 기본 코디 구성이 완성되었습니다.")
    if outfit.get("shoe") is not None:
        score += 1
        reasons.append("신발까지 포함되어 실제 착장 완성도가 높습니다.")
    if outfit.get("outer") is not None:
        score += 1
        reasons.append("아우터가 포함되어 레이어드 구성이 가능합니다.")

    return max(0, min(5, score)), reasons[:2]


def calculate_outfit_score(user, outfit, temp=22, situation="데일리"):
    """총점 100점과 세부 점수/이유를 반환합니다."""
    color, color_reasons = score_color(outfit)
    weather, weather_reasons = score_temperature(outfit, temp)
    body, body_reasons = score_body(user, outfit)
    personal, personal_reasons = score_personal_color(user, outfit)
    style, style_reasons = score_style(user, outfit)
    situation_score, situation_reasons = score_situation(outfit, situation)
    complete, complete_reasons = score_completeness(outfit)

    total = color + weather + body + personal + style + situation_score + complete

    return {
        "total": int(round(total)),
        "details": {
            "색상 조합": {"score": color, "max": 25, "reasons": color_reasons},
            "온도 적합도": {"score": weather, "max": 20, "reasons": weather_reasons},
            "체형 보완": {"score": body, "max": 20, "reasons": body_reasons},
            "퍼스널 컬러": {"score": personal, "max": 15, "reasons": personal_reasons},
            "선호 스타일": {"score": style, "max": 15, "reasons": style_reasons},
            "상황 적합도": {"score": situation_score, "max": 15, "reasons": situation_reasons},
            "코디 완성도": {"score": complete, "max": 5, "reasons": complete_reasons},
        }
    }


# -----------------------------
# 코디 생성
# -----------------------------

def group_clothes_by_category(clothes):
    groups = {"top": [], "bottom": [], "outer": [], "shoe": [], "etc": []}

    for item in clothes or []:
        cat = item_category(item)
        detail = item_detail(item)

        text = f"{cat} {detail}"

        if "상의" in text or any(k in text for k in ["반팔", "긴팔", "셔츠", "니트", "맨투맨", "후드"]):
            groups["top"].append(item)
        elif "하의" in text or any(k in text for k in ["바지", "슬랙스", "청바지", "반바지", "스커트"]):
            groups["bottom"].append(item)
        elif "아우터" in text or any(k in text for k in ["자켓", "재킷", "코트", "패딩", "가디건", "후리스", "집업"]):
            groups["outer"].append(item)
        elif "신발" in text or any(k in text for k in ["운동화", "스니커즈", "구두", "부츠", "로퍼"]):
            groups["shoe"].append(item)
        else:
            groups["etc"].append(item)

    return groups


def generate_outfit_candidates(clothes, include_optional=True):
    groups = group_clothes_by_category(clothes)

    tops = groups["top"]
    bottoms = groups["bottom"]
    outers = groups["outer"] if include_optional else []
    shoes = groups["shoe"] if include_optional else []

    if not tops or not bottoms:
        return []

    # 아우터/신발은 없어도 추천 가능하게 None 포함
    outer_options = [None] + outers
    shoe_options = [None] + shoes

    candidates = []
    for top, bottom, outer, shoe in product(tops, bottoms, outer_options, shoe_options):
        candidates.append({
            "top": top,
            "bottom": bottom,
            "outer": outer,
            "shoe": shoe
        })

    return candidates


def recommend_outfits(user, clothes, temp=22, situation="데일리", top_n=3, offset=0):
    """모든 조합을 점수화하고 offset부터 TOP N 추천 결과를 반환합니다."""
    candidates = generate_outfit_candidates(clothes)
    results = []

    for outfit in candidates:
        score = calculate_outfit_score(user, outfit, temp=temp, situation=situation)
        results.append({
            "outfit": outfit,
            "score": score["total"],
            "details": score["details"],
            "summary": build_recommendation_summary(outfit, score)
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    # 같은 조합이 반복되는 것 방지
    filtered = []
    used_pairs = set()

    def item_identity(item):
        value = get_value(item, "id", "clothing_id", default=None)
        return value if value is not None else id(item)

    for result in results:
        top_id = item_identity(result["outfit"].get("top"))
        bottom_id = item_identity(result["outfit"].get("bottom"))
        outer_id = item_identity(result["outfit"].get("outer"))
        shoe_id = item_identity(result["outfit"].get("shoe"))
        pair = (top_id, bottom_id, outer_id, shoe_id)
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        filtered.append(result)

    if not filtered:
        return []

    count = max(0, min(int(top_n), len(filtered)))
    start = int(offset or 0) % len(filtered)
    return [filtered[(start + index) % len(filtered)] for index in range(count)]


def build_recommendation_summary(outfit, score_info):
    """추천 카드에 바로 보이는 핵심 이유를 만듭니다.
    화면에서는 이유가 4개 정도만 보이므로, 사용자가 직접 선택한 상황과
    온도 조건이 뒤로 밀리지 않도록 먼저 보여줍니다.
    """
    reasons = []
    details = score_info.get("details", {})

    # 사용자가 직접 입력/선택한 조건을 우선 표시
    for key in ["상황 적합도", "온도 적합도"]:
        data = details.get(key, {})
        for reason in data.get("reasons", []):
            if reason and reason not in reasons:
                reasons.append(reason)

    # 그 다음 코디 품질 관련 이유를 이어서 표시
    for key in ["색상 조합", "체형 보완", "퍼스널 컬러", "선호 스타일", "코디 완성도"]:
        data = details.get(key, {})
        for reason in data.get("reasons", []):
            if reason and reason not in reasons:
                reasons.append(reason)
                break

    return reasons[:5]


def format_item(item):
    if item is None:
        return "없음"
    detail = item_detail(item)
    color = item_color(item)
    feature = item_feature(item)
    parts = [x for x in [color, detail, feature] if x]
    return " ".join(parts) if parts else "정보 없음"


# -----------------------------
# 사진 대표색 자동 추출 보조 함수
# -----------------------------

BASIC_COLOR_TABLE = {
    "검정": (20, 20, 20),
    "흰색": (245, 245, 245),
    "회색": (140, 140, 140),
    "네이비": (20, 35, 80),
    "베이지": (210, 185, 140),
    "아이보리": (240, 230, 200),
    "브라운": (120, 75, 35),
    "카키": (95, 105, 65),
    "빨강": (200, 35, 45),
    "핑크": (235, 130, 170),
    "노랑": (230, 205, 50),
    "파랑": (50, 110, 200),
    "하늘색": (120, 180, 230),
    "초록": (50, 150, 80),
    "보라": (120, 80, 160),
    "버건디": (110, 20, 45),
}


def rgb_to_basic_color(rgb):
    import colorsys

    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s < 0.12:
        if v < 0.20:
            return "검정"
        if v > 0.86:
            return "흰색"
        return "회색"
    if 0.52 <= h <= 0.72:
        if v < 0.34:
            return "네이비"
        if v > 0.72 and s < 0.55:
            return "하늘색"
        return "파랑"

    best_name = "회색"
    best_dist = float("inf")
    for name, target in BASIC_COLOR_TABLE.items():
        dist = sum((rgb[i] - target[i]) ** 2 for i in range(3))
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name


def extract_dominant_colors(image_path, color_count=3):
    """
    사진에서 대표색을 뽑아 [(색이름, '#RRGGBB'), ...] 형태로 반환합니다.

    개선 내용
    1) 사진 전체가 아니라 중앙 영역을 우선 분석해서 배경 영향을 줄입니다.
    2) 빨강/파랑처럼 채도가 있는 옷은 채도가 높은 픽셀을 우선 사용합니다.
    3) 흰색/검정/회색 옷도 등록할 수 있도록, 채도 높은 픽셀이 적으면 무채색 후보를 사용합니다.
    4) 비중이 높은 색상 순서대로 최대 3개를 반환합니다.
    """
    from PIL import Image
    import colorsys

    img = Image.open(image_path).convert("RGB")
    img.thumbnail((300, 300))
    w, h = img.size

    # 테두리에서 연결되는 배경을 먼저 제거해 흰색/회색 배경이 대표색이 되는 일을 줄입니다.
    try:
        from logic.photo_analysis import foreground_pixels

        fg_img, fg_mask = foreground_pixels(image_path, max_size=300)
        img = fg_img
        w, h = img.size
        all_pixels = [
            img.getpixel((x, y))
            for y in range(h)
            for x in range(w)
            if fg_mask[y][x]
        ]
    except Exception:
        all_pixels = []

    # 배경 분리가 어려운 사진은 중앙 80%를 사용합니다.
    if len(all_pixels) < max(80, int(w * h * 0.01)):
        crop_ratio = 0.80
        left = int(w * (1 - crop_ratio) / 2)
        top = int(h * (1 - crop_ratio) / 2)
        right = int(w * (1 + crop_ratio) / 2)
        bottom = int(h * (1 + crop_ratio) / 2)
        all_pixels = list(img.crop((left, top, right, bottom)).getdata())

    colorful_pixels = []
    neutral_pixels = []

    for r, g, b in all_pixels:
        # 완전한 흰 배경/완전한 검정 그림자는 먼저 제외
        if r > 248 and g > 248 and b > 248:
            continue
        if r < 8 and g < 8 and b < 8:
            continue

        # RGB -> HSV. s는 채도, v는 밝기
        h_val, s_val, v_val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

        # 너무 어두운 그림자, 너무 밝은 흰 배경 일부 제거
        if v_val < 0.08:
            continue
        if v_val > 0.97 and s_val < 0.08:
            continue

        # 채도 있는 색상은 옷의 실제 색일 가능성이 높음
        if s_val >= 0.22 and v_val >= 0.14:
            colorful_pixels.append((r, g, b))
        # 흰색/검정/회색 옷도 가능하므로 무채색 후보는 따로 보관
        elif 0.14 <= v_val <= 0.95:
            neutral_pixels.append((r, g, b))

    # 채도 있는 픽셀이 충분하면 배경 무채색은 버리고 색상 픽셀만 사용
    # 빨간 티셔츠 + 검은 배경 같은 사진에서 핵심적으로 필요함
    if len(colorful_pixels) >= max(80, int(len(all_pixels) * 0.04)):
        filtered = colorful_pixels
    else:
        filtered = colorful_pixels + neutral_pixels

    # 중앙 영역에서 충분히 못 찾으면 전체 이미지로 한 번 더 보완
    if not filtered:
        filtered = [p for p in img.getdata() if not (p[0] > 248 and p[1] > 248 and p[2] > 248)]
    if not filtered:
        filtered = list(img.getdata())

    # 색을 적당히 묶기. 단위를 너무 크게 잡으면 빨강이 갈색/검정으로 뭉개질 수 있음.
    def quantize(c):
        step = 18
        return tuple(max(0, min(255, int(round(v / step) * step))) for v in c)

    counter = Counter(quantize(c) for c in filtered)

    selected = []

    def color_distance(c1, c2):
        return sum((c1[i] - c2[i]) ** 2 for i in range(3)) ** 0.5

    for rgb, _count in counter.most_common(60):
        rgb = tuple(max(0, min(255, int(v))) for v in rgb)

        # 거의 같은 색이 여러 번 나오는 것만 방지하고, 같은 계열의 명암 차이는 허용
        if any(color_distance(rgb, prev_rgb) < 34 for prev_rgb, _ in selected):
            continue

        hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)
        selected.append((rgb, hex_code))
        if len(selected) >= color_count:
            break

    result = [(rgb_to_basic_color(rgb), hex_code) for rgb, hex_code in selected]

    # 혹시 3개가 안 나오면 기존 방식처럼 전체 이미지에서 보충
    if len(result) < color_count:
        for rgb, _count in Counter(quantize(c) for c in img.getdata()).most_common(60):
            rgb = tuple(max(0, min(255, int(v))) for v in rgb)
            hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)
            if any(hex_code == old_hex for _, old_hex in result):
                continue
            result.append((rgb_to_basic_color(rgb), hex_code))
            if len(result) >= color_count:
                break

    return result
