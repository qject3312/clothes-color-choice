"""색상 기반 코디 추천 (BaseItemRecommendUI Flet 이식).

원본: ui/base_item_recommend_ui.py
- 옷 하나(상의/하의/아우터)를 기준으로 나머지 옷의 색상·종류를 추천.
- 색상 규칙(COLOR_RULES), 색상 별칭(ALIAS), 체형/스타일 반영(TYPE_RULES) 로직을 100% 그대로 옮겼습니다.
- UI만 Flet 디자인 토큰(theme/components)에 맞춰 다시 그렸습니다.
"""
import flet as ft
from views.theme import C, R, S, F
from views.components import (card, top_bar, btn_primary, btn_secondary,
                               section, cloth_image, empty_state, badge)

try:
    from api_client import save_outfit_backend
except Exception:
    def save_outfit_backend(o, uid="guest"): return {}


# ─────────────────────────────────────────────
# 안전한 값 읽기 (dict / Clothing 객체 모두 지원) - 원본 _get 계열
# ─────────────────────────────────────────────
def _get(item, name, default=""):
    if item is None:
        return default
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _color(item):
    return str(_get(item, "color_name", _get(item, "color", "")) or "").strip()


def _category(item):
    return str(_get(item, "category", "") or "").strip()


def _detail(item):
    return str(_get(item, "detail", "") or "").strip()


def _feature(item):
    return str(_get(item, "feature", "") or "").strip()


def _serialize_cloth(item):
    """코디 저장 시 Clothing 객체 → dict (recommend_view 와 동일 규약)."""
    if item is None:
        return None
    if isinstance(item, dict):
        d = dict(item)
        if "hex" not in d:
            d["hex"] = d.get("color_hex", d.get("hex_code", "#cccccc"))
        return d
    return {
        "id":         _get(item, "id", _get(item, "clothing_id", None)),
        "category":   _category(item),
        "detail":     _detail(item),
        "feature":    _feature(item),
        "color_name": _color(item),
        "hex":        _get(item, "hex", _get(item, "hex_code", "#cccccc")),
        "color_hex":  _get(item, "hex", _get(item, "hex_code", "#cccccc")),
        "image_path": _get(item, "image_path", ""),
    }


def _get_uid(app_state):
    u = app_state.get("user") or app_state.get("current_user")
    if u and isinstance(u, dict):
        return u.get("user_id", "guest")
    return "guest"


# ─────────────────────────────────────────────
# 추천 규칙 (원본 그대로)
# ─────────────────────────────────────────────
COLOR_RULES = {
    "흰색": {"top": ["네이비", "검정", "베이지", "하늘색"], "bottom": ["중청", "연청", "검정", "네이비", "베이지"], "outer": ["네이비", "베이지", "회색", "카키"], "mood": "깔끔하고 대부분의 옷과 잘 어울리는 기본 색입니다."},
    "검정": {"top": ["흰색", "회색", "베이지", "하늘색"], "bottom": ["중청", "회색", "카키", "베이지"], "outer": ["회색", "베이지", "카키", "데님"], "mood": "차분하고 안정적이라 밝은 색을 섞으면 답답함이 줄어듭니다."},
    "파랑": {"top": ["흰색", "아이보리", "회색", "네이비"], "bottom": ["흰색", "베이지", "회색", "검정"], "outer": ["아이보리", "베이지", "네이비", "회색"], "mood": "청량한 느낌이 강해서 흰색, 회색, 베이지와 조합하면 깔끔합니다."},
    "네이비": {"top": ["흰색", "하늘색", "회색", "아이보리"], "bottom": ["흰색", "베이지", "회색", "중청"], "outer": ["베이지", "회색", "아이보리"], "mood": "단정한 느낌이 강해서 학교, 출근, 데일리에 모두 무난합니다."},
    "베이지": {"top": ["흰색", "검정", "네이비", "브라운"], "bottom": ["중청", "흰색", "브라운", "카키"], "outer": ["브라운", "네이비", "카키", "아이보리"], "mood": "부드러운 색이라 브라운 계열이나 네이비와 잘 맞습니다."},
    "회색": {"top": ["흰색", "검정", "네이비", "파랑"], "bottom": ["검정", "중청", "네이비", "흰색"], "outer": ["검정", "네이비", "베이지"], "mood": "튀지 않고 차분해서 무채색 또는 네이비와 안정적으로 어울립니다."},
    "노랑": {"top": ["흰색", "아이보리", "네이비", "회색"], "bottom": ["중청", "연청", "흰색", "베이지", "검정"], "outer": ["아이보리", "네이비", "데님"], "mood": "밝은 포인트 색이라 나머지는 기본색으로 눌러주면 좋습니다."},
    "빨강": {"top": ["흰색", "아이보리", "검정", "회색", "네이비"], "bottom": ["중청", "연청", "검정", "베이지", "회색"], "outer": ["검정", "네이비", "데님", "회색", "아이보리"], "mood": "빨강은 시선이 강한 포인트 색이라 나머지는 흰색, 검정, 데님처럼 차분한 색으로 맞추면 안정적입니다."},
    "브라운": {"top": ["흰색", "아이보리", "베이지", "네이비"], "bottom": ["중청", "아이보리", "베이지", "카키"], "outer": ["베이지", "아이보리", "카키"], "mood": "따뜻한 느낌이 강해서 아이보리, 베이지 계열과 자연스럽습니다."},
    "보라": {"top": ["흰색", "회색", "아이보리", "검정"], "bottom": ["검정", "중청", "흰색", "회색"], "outer": ["회색", "검정", "아이보리"], "mood": "보라색은 포인트가 강하므로 나머지는 차분한 색이 좋습니다."},
}

ALIAS = {
    "청": "파랑", "청바지": "파랑", "데님": "파랑", "중청": "파랑", "연청": "파랑", "진청": "네이비",
    "하양": "흰색", "화이트": "흰색", "아이보리": "흰색", "크림": "흰색",
    "검정색": "검정", "검은색": "검정", "블랙": "검정",
    "남색": "네이비", "곤색": "네이비",
    "그레이": "회색", "연회색": "회색", "차콜": "회색",
    "카멜": "브라운", "갈색": "브라운",
    "노란색": "노랑", "옐로우": "노랑",
    "빨간색": "빨강", "빨강색": "빨강", "레드": "빨강", "버건디": "빨강",
    "퍼플": "보라", "보라색": "보라",
}

COLOR_SWATCH = {
    "흰색": "#f7f7f7", "아이보리": "#f3ead7", "검정": "#222222", "회색": "#9ca3af", "네이비": "#1e3a8a",
    "베이지": "#d6b98c", "브라운": "#8b5a2b", "카키": "#7c8450", "파랑": "#2563eb", "하늘색": "#93c5fd",
    "중청": "#3b82f6", "연청": "#bfdbfe", "노랑": "#facc15", "빨강": "#ef4444", "데님": "#315f9d", "보라": "#8b5cf6",
}

DARK_SWATCH = {"검정", "네이비", "브라운", "파랑", "보라", "데님"}

TYPE_RULES = {
    "상의": {
        "데일리": ["기본 반팔", "긴팔 티셔츠", "맨투맨"],
        "출근": ["셔츠", "니트", "깔끔한 긴팔"],
        "데이트": ["니트", "셔츠", "가디건"],
        "학교": ["맨투맨", "후드", "기본 반팔"],
        "운동": ["기능성 반팔", "후드", "트레이닝 상의"],
        "기본": ["기본 반팔", "셔츠", "니트"],
    },
    "하의": {
        "데일리": ["청바지", "와이드 팬츠", "면바지"],
        "출근": ["슬랙스", "일자핏 팬츠", "면바지"],
        "데이트": ["슬랙스", "청바지", "와이드 팬츠"],
        "학교": ["청바지", "조거팬츠", "와이드 팬츠"],
        "운동": ["트레이닝 팬츠", "조거팬츠", "반바지"],
        "기본": ["청바지", "슬랙스", "와이드 팬츠"],
    },
    "아우터": {
        "데일리": ["가디건", "자켓", "후드집업"],
        "출근": ["블레이저", "코트", "가디건"],
        "데이트": ["가디건", "자켓", "코트"],
        "학교": ["후드집업", "자켓", "가디건"],
        "운동": ["바람막이", "후드집업", "트레이닝 자켓"],
        "기본": ["가디건", "자켓", "코트"],
    },
}


# ─────────────────────────────────────────────
# 로직 함수 (원본 메서드 그대로 옮김)
# ─────────────────────────────────────────────
def _simple_category(item):
    text = f"{_category(item)} {_detail(item)}"
    if "상의" in text or any(k in text for k in ["반팔", "긴팔", "셔츠", "니트", "맨투맨", "후드", "블라우스"]):
        return "상의"
    if "하의" in text or any(k in text for k in ["바지", "청바지", "슬랙스", "반바지", "치마", "조거"]):
        return "하의"
    if "아우터" in text or any(k in text for k in ["자켓", "재킷", "코트", "패딩", "가디건", "후리스", "집업", "점퍼"]):
        return "아우터"
    return _category(item)


def _base_clothes(clothes):
    return [c for c in (clothes or []) if _simple_category(c) in ["상의", "하의", "아우터"]]


def _normalize_color(color, detail=""):
    text = f"{color} {detail}"
    for key, value in ALIAS.items():
        if key in text:
            return value
    if color in COLOR_RULES:
        return color
    # 알 수 없는 색상을 흰색으로 잘못 표시하지 않고, 기본 추천 규칙만 사용합니다.
    return color or "기본"


def _preferred_style_key(user):
    raw = user.get("styles", "") or user.get("style", "") or ""
    text = raw if isinstance(raw, str) else ",".join(raw)
    for key in ["데일리", "출근", "데이트", "학교", "운동"]:
        if key in text:
            return key
    return "기본"


def _recommend_types(target_category, base_item, user):
    style_key = _preferred_style_key(user)
    types = list(TYPE_RULES.get(target_category, {}).get(
        style_key, TYPE_RULES.get(target_category, {}).get("기본", [])))
    body_type = user.get("body_type", "미입력")
    base_detail = _detail(base_item)

    if target_category == "하의":
        if body_type == "마른 체형":
            types = ["와이드 팬츠", "청바지", "조거팬츠"]
        elif body_type == "통통한 체형":
            types = ["일자핏 팬츠", "슬랙스", "와이드 팬츠"]
        elif body_type == "근육형":
            types = ["일자핏 팬츠", "청바지", "조거팬츠"]
    elif target_category == "상의":
        if body_type == "마른 체형":
            types = ["오버핏 맨투맨", "니트", "후드"]
        elif body_type == "통통한 체형":
            types = ["정핏 셔츠", "깔끔한 긴팔", "니트"]
        elif body_type == "근육형":
            types = ["정핏 반팔", "셔츠", "맨투맨"]
    elif target_category == "아우터":
        if body_type == "통통한 체형":
            types = ["롱코트", "블레이저", "깔끔한 자켓"]
        elif "반팔" in base_detail:
            types = ["가디건", "얇은 자켓", "후드집업"]

    clean = []
    for t in types:
        if t not in clean:
            clean.append(t)
    return clean[:3]


def _profile_note(user):
    bits = []
    if user.get("body_type") and user.get("body_type") != "미입력":
        bits.append(user.get("body_type"))
    style_key = _preferred_style_key(user)
    if style_key != "기본":
        bits.append(f"{style_key} 스타일")
    if user.get("personal_color") and user.get("personal_color") != "미입력":
        bits.append(user.get("personal_color"))
    return " · ".join(bits) if bits else "기본 프로필 기준"


def _build_result(base_item, user):
    cat = _simple_category(base_item)
    base_color = _normalize_color(_color(base_item), _detail(base_item))
    rules = COLOR_RULES.get(base_color, {
        "top": ["흰색", "검정", "회색", "베이지", "네이비"],
        "bottom": ["중청", "검정", "베이지", "회색", "네이비"],
        "outer": ["검정", "네이비", "베이지", "회색", "데님"],
        "mood": "등록한 색상을 기준으로 기본색과 데님 중심의 안정적인 조합을 추천했습니다.",
    })
    targets = [("상의", "top"), ("하의", "bottom"), ("아우터", "outer")]
    targets = [(name, key) for name, key in targets if name != cat]
    recs, type_recs = {}, {}
    for name, key in targets:
        recs[name] = rules.get(key, ["흰색", "검정", "베이지"])[0:4]
        type_recs[name] = _recommend_types(name, base_item, user)
    return {
        "base_item": base_item,
        "base_category": cat,
        "base_color": base_color,
        "recommendations": recs,
        "type_recommendations": type_recs,
        "mood": rules.get("mood", "기본 색상 중심으로 안정적인 조합을 추천했습니다."),
        "profile_note": _profile_note(user),
    }


def _matching_owned_text(result, clothes):
    lines = []
    for name, colors in result["recommendations"].items():
        matches = []
        for item in _base_clothes(clothes):
            if _simple_category(item) == name and any(c in (_color(item) + _detail(item)) for c in colors):
                matches.append(f"{_color(item)} {_detail(item)}")
        if matches:
            lines.append(f"{name}: " + ", ".join(matches[:3]))
    return "\n".join(lines) if lines else "추천 색상과 정확히 맞는 등록 옷은 아직 없지만, 위 색상을 기준으로 새 코디를 구성할 수 있습니다."


def _pseudo_item(category, colors, types=None):
    detail = "추천: " + ", ".join((types or [])[:2]) if types else "추천 종류"
    return {"category": category, "detail": detail, "feature": "색상/종류 추천 결과",
            "color_name": ", ".join(colors[:4]), "image_path": ""}


# ─────────────────────────────────────────────
# Flet 뷰
# ─────────────────────────────────────────────
def build_base_recommend(page, go, app_state):
    user    = app_state.get("user") or app_state.get("current_user") or {}
    clothes = app_state.get("clothes", [])
    base_pool = _base_clothes(clothes)

    # ─── 옷이 하나도 없으면 빈 화면 ───
    if not base_pool:
        return ft.Column([
            top_bar(page, "색상 기반 코디 추천", on_back=lambda: go("/")),
            empty_state(
                ft.Icons.PALETTE_OUTLINED,
                "추천에 사용할 옷을 먼저 등록해 주세요.",
                "상의 · 하의 · 아우터 중 하나 이상이 있어야 색상 추천이 가능합니다.",
                "옷 등록하러 가기", lambda e: go("/register"),
            ),
        ], spacing=0, expand=True)

    # ─── 상태 ───
    state = {"category": "상의", "key": None}
    result_holder = ft.Column(spacing=S["md"])

    item_dropdown = ft.Dropdown(
        label="기준이 될 옷",
        border_radius=R["md"], filled=True,
        bgcolor=C["card"], border_color=C["border"],
        focused_border_color=C["primary"], text_size=F["body"],
    )

    def _items_in(cat):
        return [c for c in base_pool if _simple_category(c) == cat]

    def _label_map(items):
        m, labels = {}, []
        for idx, item in enumerate(items):
            feat = _feature(item)
            if feat.strip() in ["", "없음", "특징 없음", "None"]:
                feat = ""
            label = f"{idx + 1}. {_color(item)} {_detail(item)}" + (f" ({feat[:12]})" if feat else "")
            m[label] = item
            labels.append(label)
        return m, labels

    item_map = {}

    def refresh_dropdown():
        nonlocal item_map
        items = _items_in(state["category"])
        item_map, labels = _label_map(items)
        item_dropdown.options = [ft.dropdown.Option(l) for l in labels]
        if labels:
            state["key"] = labels[0]
            item_dropdown.value = labels[0]
            item_dropdown.disabled = False
            item_dropdown.hint_text = None
        else:
            state["key"] = None
            item_dropdown.value = None
            item_dropdown.disabled = True
            item_dropdown.hint_text = f"등록된 {state['category']}가 없습니다."
        page.update()

    def on_dropdown_change(e):
        state["key"] = item_dropdown.value

    item_dropdown.on_change = on_dropdown_change

    # ─── 카테고리 탭 ───
    def cat_button(cat):
        selected = state["category"] == cat
        return ft.Container(
            content=ft.Text(cat, size=F["sm"], weight=ft.FontWeight.BOLD,
                            color="white" if selected else C["subtext"]),
            bgcolor=C["primary"] if selected else C["muted"],
            border_radius=R["full"],
            padding=ft.padding.symmetric(horizontal=18, vertical=9),
            on_click=lambda e, c=cat: change_category(c),
            ink=True,
        )

    tab_row = ft.Row(spacing=8)

    def rebuild_tabs():
        tab_row.controls = [cat_button(c) for c in ["상의", "하의", "아우터"]]

    def change_category(cat):
        state["category"] = cat
        result_holder.controls = []
        rebuild_tabs()
        refresh_dropdown()

    # ─── 색상 칩 / 종류 칩 ───
    def color_chip(name):
        bg = COLOR_SWATCH.get(name, C["muted"])
        fg = "white" if name in DARK_SWATCH else C["text"]
        return ft.Container(
            content=ft.Text(name, size=F["xs"], weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg, border_radius=R["full"],
            border=ft.border.all(1, C["border"]),
            padding=ft.padding.symmetric(horizontal=12, vertical=5),
        )

    def type_chip(name):
        return ft.Container(
            content=ft.Text(name, size=F["xs"], weight=ft.FontWeight.BOLD, color=C["primary"]),
            bgcolor=C["primary_soft"], border_radius=R["full"],
            padding=ft.padding.symmetric(horizontal=12, vertical=5),
        )

    def target_box(name, colors, types):
        return ft.Container(
            content=ft.Column([
                ft.Text(name, size=F["md"], weight=ft.FontWeight.W_700, color=C["text"]),
                ft.Text("추천 종류", size=F["xs"], weight=ft.FontWeight.BOLD, color=C["subtext"]),
                ft.Row([type_chip(t) for t in types[:3]], wrap=True, spacing=6, run_spacing=6),
                ft.Container(height=2),
                ft.Text("추천 색상", size=F["xs"], weight=ft.FontWeight.BOLD, color=C["subtext"]),
                ft.Row([color_chip(c) for c in colors[:4]], wrap=True, spacing=6, run_spacing=6),
            ], spacing=6),
            bgcolor=C["bg"], border_radius=R["md"],
            border=ft.border.all(1, C["border"]),
            padding=S["md"],
        )

    # ─── 추천 결과 그리기 ───
    def draw_result(result):
        base = result["base_item"]
        base_preview = ft.Container(
            content=ft.Row([
                cloth_image(_get(base, "image_path", ""), size=54, radius=8),
                ft.Column([
                    badge("기준 옷"),
                    ft.Text(f"{result['base_category']} / {_color(base)} {_detail(base)}",
                            size=F["sm"], weight=ft.FontWeight.W_600, color=C["text"],
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=4, expand=True),
            ], spacing=S["md"], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=C["bg"], border_radius=R["md"], padding=S["md"],
        )

        target_boxes = []
        for name, colors in result["recommendations"].items():
            types = result.get("type_recommendations", {}).get(name, [])
            target_boxes.append(target_box(name, colors, types))

        result_card = card(ft.Column([
            ft.Row([
                section("추천 결과"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.BOOKMARK_ADD_ROUNDED, color="white", size=16),
                        ft.Text("저장", color="white", weight=ft.FontWeight.BOLD, size=F["sm"]),
                    ], tight=True, spacing=4),
                    on_click=lambda e: do_save(result),
                    style=ft.ButtonStyle(
                        bgcolor=C["success"],
                        shape=ft.RoundedRectangleBorder(radius=R["md"]),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    ),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            base_preview,
            ft.Text(f"{result['base_color']} 계열: {result['mood']}",
                    size=F["sm"], color=C["subtext"]),
            ft.Text(f"반영 정보: {result.get('profile_note', '기본 프로필 기준')}",
                    size=F["xs"], weight=ft.FontWeight.BOLD, color=C["primary"]),
            ft.Container(height=2),
            *target_boxes,
            ft.Container(height=2),
            section("내 옷장 매칭", color=C["text"]),
            ft.Text(_matching_owned_text(result, clothes),
                    size=F["sm"], color=C["subtext"]),
        ], spacing=S["sm"]))

        result_holder.controls = [result_card]
        page.update()

    # ─── 추천 실행 ───
    def do_recommend(_=None):
        item = item_map.get(state["key"])
        if not item:
            page.open(ft.SnackBar(ft.Text("기준이 될 옷을 선택해 주세요."), bgcolor=C["danger"]))
            return
        draw_result(_build_result(item, user))

    # ─── 저장 (원본 _save 규약 그대로) ───
    def do_save(result):
        if not result:
            return
        base_item = result["base_item"]
        outfit = {
            "source": "base_color",
            "source_label": "색상 기반 코디 추천",
            "reason": f"{_color(base_item)} {_detail(base_item)}을 기준으로 상의/하의/아우터 색상과 종류를 추천해 저장했습니다.",
        }
        key_map = {"상의": "top", "하의": "bottom", "아우터": "outer"}
        base_cat = result["base_category"]
        outfit[key_map[base_cat]] = _serialize_cloth(base_item)
        for kor, key in key_map.items():
            if key not in outfit and kor in result["recommendations"]:
                outfit[key] = _pseudo_item(
                    kor,
                    result["recommendations"][kor],
                    result.get("type_recommendations", {}).get(kor, []),
                )
        try:
            r = save_outfit_backend(outfit, _get_uid(app_state))
            if isinstance(r, dict) and "id" in r:
                outfit["id"] = r["id"]
        except Exception:
            pass
        app_state.setdefault("saved_outfits", []).insert(0, outfit)
        page.open(ft.SnackBar(ft.Text("색상 기반 추천 코디를 저장했습니다."), bgcolor=C["success"]))

    # 초기 구성
    rebuild_tabs()

    column = ft.Column([
        top_bar(page, "색상 기반 코디 추천", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                # 설명 카드
                card(ft.Column([
                    section("옷 하나를 기준으로 색상 조합 추천"),
                    ft.Text("등록한 상의 · 하의 · 아우터 중 하나를 고르면 나머지 옷의 색상과 종류를 함께 추천합니다.",
                            size=F["sm"], color=C["subtext"]),
                ], spacing=6)),
                # 선택 카드
                card(ft.Column([
                    section("기준이 될 옷 선택"),
                    tab_row,
                    item_dropdown,
                    btn_primary("색상 추천받기", do_recommend, ft.Icons.AUTO_AWESOME_ROUNDED),
                ], spacing=S["sm"])),
                # 결과
                result_holder,
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)

    # 드롭다운 초기 채우기 (page에 추가된 뒤 update가 호출되도록 지연)
    items = _items_in(state["category"])
    item_map, labels = _label_map(items)
    item_dropdown.options = [ft.dropdown.Option(l) for l in labels]
    if labels:
        state["key"] = labels[0]
        item_dropdown.value = labels[0]
    else:
        item_dropdown.disabled = True
        item_dropdown.hint_text = f"등록된 {state['category']}가 없습니다."

    return column
