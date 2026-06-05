def get_color_style_info(color_name):
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
        "recommended": ["검정", "흰색", "회색", "베이지"],
        "avoid": ["너무 강한 원색 조합"],
        "reason": "중립적인 색 조합을 우선 추천합니다.",
        "avoid_reason": "강한 색끼리 만나면 코디가 복잡해 보일 수 있습니다."
    })


def explain_match(top_name, bottom_name):
    good_pairs = {
        ("검정", "흰색"): "강한 명도 차이를 활용한 가장 기본적인 조합입니다.",
        ("검정", "베이지"): "어두운 상의와 부드러운 하의 조합으로 안정적입니다.",
        ("네이비", "베이지"): "단정하고 깔끔한 분위기를 주는 대표 조합입니다.",
        ("흰색", "네이비"): "깔끔하면서도 부담 없는 조합입니다.",
        ("카키", "베이지"): "자연 계열 톤온톤 조합으로 부드럽고 세련된 느낌을 줍니다.",
        ("회색", "검정"): "차분한 무채색 조합이라 실패 확률이 낮습니다.",
        ("빨강", "검정"): "포인트 컬러를 무채색으로 눌러줘 균형이 좋습니다.",
        ("핑크", "회색"): "부드럽고 안정적인 이미지가 잘 살아납니다."
    }

    bad_pairs = {
        ("빨강", "초록"): "대비가 너무 강해서 일상 코디로는 부담스러울 수 있습니다.",
        ("카키", "빨강"): "톤이 충돌해 전체적으로 어수선해 보일 수 있습니다.",
        ("검정", "브라운"): "둘 다 어두운 톤이면 답답해 보일 수 있습니다."
    }

    if (top_name, bottom_name) in good_pairs:
        return True, good_pairs[(top_name, bottom_name)]
    if (top_name, bottom_name) in bad_pairs:
        return False, bad_pairs[(top_name, bottom_name)]

    if top_name == bottom_name:
        return True, "같은 계열 색상으로 통일감을 줄 수 있습니다."
    if top_name in ["검정", "흰색", "회색"] or bottom_name in ["검정", "흰색", "회색"]:
        return True, "무채색이 포함되어 있어 전체적으로 안정적인 코디를 만들기 쉽습니다."

    return True, "무난한 조합이지만 신발이나 아우터에 무채색을 더하면 더 자연스럽습니다."


def get_temperature_recommendation(temp):
    if temp >= 28:
        return {
            "top": ["반팔", "민소매"],
            "bottom": ["반바지", "얇은 바지"],
            "outer": [],
            "reason": "매우 더운 날씨라 통풍이 잘 되는 얇은 옷이 좋습니다.",
            "avoid": "두꺼운 니트, 패딩, 기모류"
        }
    elif temp >= 23:
        return {
            "top": ["반팔", "셔츠"],
            "bottom": ["청바지", "슬랙스", "반바지"],
            "outer": ["얇은 가디건"],
            "reason": "조금 더운 날씨라 가벼운 상의 위주가 좋고, 얇은 겉옷 정도면 충분합니다.",
            "avoid": "두꺼운 코트, 패딩"
        }
    elif temp >= 17:
        return {
            "top": ["긴팔", "맨투맨", "셔츠"],
            "bottom": ["청바지", "슬랙스"],
            "outer": ["가디건", "얇은 자켓"],
            "reason": "선선한 날씨라 긴팔이나 가벼운 겉옷이 잘 맞습니다.",
            "avoid": "민소매, 한겨울용 패딩"
        }
    elif temp >= 10:
        return {
            "top": ["긴팔", "니트", "맨투맨"],
            "bottom": ["청바지", "슬랙스"],
            "outer": ["자켓", "코트", "후리스"],
            "reason": "쌀쌀한 날씨라 보온이 되는 상의와 겉옷이 필요합니다.",
            "avoid": "반팔 단독 착용"
        }
    else:
        return {
            "top": ["니트", "기모 맨투맨"],
            "bottom": ["두꺼운 바지"],
            "outer": ["패딩", "두꺼운 코트", "후리스"],
            "reason": "추운 날씨라 보온이 가장 중요합니다.",
            "avoid": "반팔, 반바지, 얇은 셔츠"
        }
    
def is_good_color_match(color1, color2):
    neutral_colors = ["검정", "흰색", "회색", "베이지", "네이비", "미분석"]

    if color1 in neutral_colors or color2 in neutral_colors:
        return True, "무채색 또는 기본 색상이 포함되어 안정적인 조합입니다."

    good_matches = [
        ("파랑", "흰색"),
        ("파랑", "베이지"),
        ("네이비", "흰색"),
        ("네이비", "회색"),
        ("카키", "흰색"),
        ("카키", "검정"),
        ("브라운", "베이지"),
        ("브라운", "흰색"),
        ("빨강", "검정"),
        ("초록", "베이지"),
    ]

    for a, b in good_matches:
        if (color1 == a and color2 == b) or (color1 == b and color2 == a):
            return True, f"{color1}와 {color2}는 서로 잘 어울리는 색 조합입니다."

    return False, f"{color1}와 {color2}는 강한 조합일 수 있어 무채색 아이템과 함께 매치하는 것이 좋습니다."


def recommend_outfit(clothes):
    tops = [item for item in clothes if item.category == "상의"]
    bottoms = [item for item in clothes if item.category == "하의"]
    outers = [item for item in clothes if item.category == "아우터"]

    if not tops or not bottoms:
        return {
            "success": False,
            "message": "추천을 위해서는 최소한 상의와 하의를 등록해야 합니다.",
            "top": None,
            "bottom": None,
            "outer": None,
            "reason": ""
        }

    for top in tops:
        for bottom in bottoms:
            is_good, reason = is_good_color_match(top.color_name, bottom.color_name)

            if is_good:
                return {
                    "success": True,
                    "message": "추천 코디를 찾았습니다.",
                    "top": top,
                    "bottom": bottom,
                    "outer": outers[0] if outers else None,
                    "reason": reason
                }

    return {
        "success": True,
        "message": "기본 추천 코디입니다.",
        "top": tops[0],
        "bottom": bottoms[0],
        "outer": outers[0] if outers else None,
        "reason": "완벽한 색 조합은 아니지만, 등록된 옷 중 기본 조합으로 추천합니다."
    }


def recommend_by_temperature(clothes, temperature):
    if temperature >= 28:
        preferred_details = ["반팔", "민소매", "반바지", "얇은 바지"]
    elif temperature >= 23:
        preferred_details = ["반팔", "셔츠", "얇은 바지", "청바지"]
    elif temperature >= 17:
        preferred_details = ["긴팔", "셔츠", "맨투맨", "청바지", "슬랙스", "가디건", "얇은 자켓"]
    elif temperature >= 10:
        preferred_details = ["니트", "맨투맨", "후드티", "청바지", "슬랙스", "자켓", "집업"]
    else:
        preferred_details = ["기모 맨투맨", "후드티", "두꺼운 바지", "패딩", "코트", "후리스"]

    filtered_clothes = [
        item for item in clothes
        if item.detail in preferred_details
    ]

    if len(filtered_clothes) >= 2:
        result = recommend_outfit(filtered_clothes)
        if result["success"]:
            result["message"] = f"{temperature}도 날씨에 맞는 추천 코디입니다."
            return result

    result = recommend_outfit(clothes)
    if result["success"]:
        result["message"] = f"{temperature}도 기준으로 필터링된 옷이 부족해 전체 옷장에서 추천했습니다."

    return result