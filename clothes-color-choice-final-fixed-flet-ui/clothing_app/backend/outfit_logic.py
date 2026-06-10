def color_score(color1, color2):
    good_pairs = [
        ("베이지", "네이비"),
        ("베이지", "청색"),
        ("흰색", "검정"),
        ("흰색", "네이비"),
        ("검정", "회색"),
        ("카키", "베이지"),
        ("브라운", "아이보리"),
        ("회색", "검정"),
    ]

    bad_pairs = [
        ("빨강", "초록"),
        ("검정", "브라운"),
        ("형광색", "형광색"),
    ]

    if (color1, color2) in good_pairs or (color2, color1) in good_pairs:
        return 90, "색 조합이 안정적이고 자연스럽습니다."

    if (color1, color2) in bad_pairs or (color2, color1) in bad_pairs:
        return 45, "색 대비가 강하거나 어두운 색끼리 겹쳐 답답해 보일 수 있습니다."

    if color1 in ["검정", "흰색", "회색"] or color2 in ["검정", "흰색", "회색"]:
        return 80, "무채색이 포함되어 있어 전체적으로 무난합니다."

    return 70, "크게 어색하지 않은 기본 조합입니다."


def type_score(top_type, bottom_type, outer_type="", shoes_type=""):
    score = 70
    reasons = []

    good_type_pairs = {
        ("니트", "청바지"): "니트와 청바지는 캐주얼하면서 부드러운 조합입니다.",
        ("후드", "청바지"): "후드와 청바지는 편한 캐주얼 스타일에 잘 맞습니다.",
        ("후드", "조거팬츠"): "후드와 조거팬츠는 스포티한 캐주얼 조합입니다.",
        ("셔츠", "슬랙스"): "셔츠와 슬랙스는 단정하고 포멀한 조합입니다.",
        ("코트", "슬랙스"): "코트와 슬랙스는 미니멀하고 깔끔한 조합입니다.",
    }

    bad_type_pairs = {
        ("셔츠", "반바지"): "셔츠와 반바지는 스타일 방향이 달라 어색할 수 있습니다.",
        ("코트", "반바지"): "코트와 반바지는 계절감이 맞지 않을 수 있습니다.",
        ("패딩", "반바지"): "패딩과 반바지는 보온성과 계절감이 충돌합니다.",
    }

    pairs = [
        (top_type, bottom_type),
        (outer_type, bottom_type),
    ]

    for pair in pairs:
        if pair in good_type_pairs:
            score += 12
            reasons.append(good_type_pairs[pair])
        if pair in bad_type_pairs:
            score -= 20
            reasons.append(bad_type_pairs[pair])

    score = max(0, min(100, score))

    if not reasons:
        reasons.append("옷 종류 조합은 전체적으로 무난합니다.")

    return score, " ".join(reasons)


def season_style_score(season, style_mood, top_type, bottom_type, outer_type):
    score = 75
    reasons = []

    if season == "겨울" and outer_type in ["패딩", "코트"]:
        score += 15
        reasons.append("겨울에는 패딩이나 코트가 계절감에 잘 맞습니다.")

    if season == "여름" and bottom_type == "반바지":
        score += 15
        reasons.append("여름에는 반바지가 계절감에 잘 맞습니다.")

    if season == "여름" and outer_type in ["패딩", "코트"]:
        score -= 30
        reasons.append("여름에 패딩이나 코트는 계절감이 맞지 않습니다.")

    if style_mood == "캐주얼" and top_type in ["티셔츠", "후드"]:
        score += 10
        reasons.append("캐주얼 스타일에는 티셔츠나 후드가 잘 어울립니다.")

    if style_mood == "포멀" and top_type == "셔츠" and bottom_type == "슬랙스":
        score += 15
        reasons.append("포멀 스타일에는 셔츠와 슬랙스 조합이 적절합니다.")

    score = max(0, min(100, score))

    if not reasons:
        reasons.append("계절과 스타일 면에서 크게 어색하지 않습니다.")

    return score, " ".join(reasons)


def evaluate_outfit(data):
    c_score, c_reason = color_score(data.top_color, data.bottom_color)
    t_score, t_reason = type_score(
        data.top_type,
        data.bottom_type,
        data.outer_type,
        data.shoes_type
    )
    s_score, s_reason = season_style_score(
        data.season,
        data.style_mood,
        data.top_type,
        data.bottom_type,
        data.outer_type
    )

    total = int(c_score * 0.5 + t_score * 0.3 + s_score * 0.2)

    reason = f"{c_reason} {t_reason} {s_reason}"

    return {
        "total_score": total,
        "color_score": c_score,
        "type_score": t_score,
        "season_style_score": s_score,
        "reason": reason
    }


def make_search_keyword(top_color, top_type, bottom_color, bottom_type):
    return f"{top_color} {top_type} {bottom_color} {bottom_type} outfit"
    
def recommend_by_cloth(category, color_name, detail):
    color_recommend_map = {
        "하늘색": {
            "bottom": ["흰색", "베이지", "연청", "네이비"],
            "shoes": ["흰색", "아이보리", "회색"],
            "reason": "하늘색은 밝고 시원한 느낌이 강해서 흰색, 베이지, 네이비 계열과 잘 어울립니다."
        },
        "베이지": {
            "bottom": ["청색", "네이비", "검정", "브라운"],
            "shoes": ["흰색", "브라운", "아이보리"],
            "reason": "베이지는 부드럽고 차분한 색이라 청색, 네이비, 브라운 계열과 자연스럽게 어울립니다."
        },
        "검정": {
            "bottom": ["흰색", "회색", "청색", "카키"],
            "shoes": ["흰색", "검정", "회색"],
            "reason": "검정은 기본 색상이라 대부분의 색과 잘 맞지만, 흰색이나 회색을 함께 쓰면 깔끔한 느낌이 납니다."
        },
        "흰색": {
            "bottom": ["청색", "검정", "베이지", "카키"],
            "shoes": ["흰색", "검정", "브라운"],
            "reason": "흰색은 가장 무난한 색이라 청바지, 검정, 베이지 계열과 쉽게 조합할 수 있습니다."
        },
        "네이비": {
            "bottom": ["베이지", "회색", "흰색", "청색"],
            "shoes": ["흰색", "브라운", "검정"],
            "reason": "네이비는 차분한 색이라 베이지, 회색, 흰색과 조합하면 안정적인 느낌을 줍니다."
        }
    }

    default_result = {
        "bottom": ["검정", "흰색", "청색", "베이지"],
        "shoes": ["흰색", "검정", "회색"],
        "reason": "입력한 색상에 대한 세부 규칙은 아직 없지만, 기본적으로 무난한 색 조합을 추천합니다."
    }

    result = color_recommend_map.get(color_name, default_result)

    return {
        "base_category": category,
        "base_color": color_name,
        "base_detail": detail,
        "recommended_bottom_colors": result["bottom"],
        "recommended_shoes_colors": result["shoes"],
        "reason": result["reason"]
    }