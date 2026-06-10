"""추천/코디 관련 화면들 - 버그 수정 버전."""
import flet as ft
from views.theme import C, R, S, F
from views.components import (card, top_bar, btn_primary, btn_secondary,
                               section, cloth_image, empty_state)

try:
    from logic.recommend_logic import recommend_outfits, format_item
except Exception:
    def recommend_outfits(*a, **k): return []
    def format_item(x): return str(x)

try:
    from api_client import delete_saved_outfit_backend, save_outfit_backend
except Exception:
    def delete_saved_outfit_backend(oid, uid): return {}
    def save_outfit_backend(o, uid="guest"): return {}


def _get(item, key, default=""):
    """dict/Clothing 객체 모두에서 안전하게 값 읽기."""
    if item is None:
        return default
    if isinstance(item, dict):
        return item.get(key, default) or default
    return getattr(item, key, default) or default


def _serialize_cloth(cloth):
    """Clothing 객체 → dict. 코디 저장 시 반드시 사용."""
    if cloth is None:
        return None
    if isinstance(cloth, dict):
        d = dict(cloth)
        if "hex" not in d:
            d["hex"] = d.get("color_hex", "#cccccc")
        return d
    return {
        "category":   getattr(cloth, "category", ""),
        "detail":     getattr(cloth, "detail", ""),
        "feature":    getattr(cloth, "feature", ""),
        "color_name": getattr(cloth, "color_name", ""),
        "hex":        getattr(cloth, "hex", getattr(cloth, "hex_code", "#cccccc")),
        "color_hex":  getattr(cloth, "hex", getattr(cloth, "hex_code", "#cccccc")),
        "image_path": getattr(cloth, "image_path", ""),
        "id":         getattr(cloth, "id", getattr(cloth, "clothing_id", None)),
    }


def _serialize_outfit(outfit):
    """outfit dict 안의 Clothing 객체들을 모두 dict로 직렬화."""
    if not isinstance(outfit, dict):
        return {}
    result = {}
    cloth_keys = ["top", "bottom", "outer", "shoe", "shoes", "accessory"]
    for k, v in outfit.items():
        if k in cloth_keys:
            result[k] = _serialize_cloth(v)
        else:
            result[k] = v
    return result


def _get_uid(app_state):
    u = app_state.get("user") or app_state.get("current_user")
    if u and isinstance(u, dict):
        return u.get("user_id", "guest")
    return "guest"


# ─── 공통: 옷 아이템 행 (이미지 + 텍스트) ───
def item_row(label, cloth):
    if cloth is None:
        return ft.Row([
            ft.Container(ft.Text(f"{label}:", size=F["sm"], weight=ft.FontWeight.BOLD,
                                  color=C["subtext"]), width=60),
            ft.Text("없음", size=F["sm"], color=C["hint"]),
        ], spacing=8)

    ip     = _get(cloth, "image_path")
    detail = _get(cloth, "detail")
    cname  = _get(cloth, "color_name")
    img    = cloth_image(ip, size=46, radius=8)

    return ft.Row([
        ft.Container(ft.Text(f"{label}:", size=F["sm"], weight=ft.FontWeight.BOLD,
                              color=C["subtext"]), width=60),
        img,
        ft.Text(f"{detail} / {cname}", size=F["sm"], color=C["subtext"],
                expand=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)


# ─────────────────────────────────────────────
# 맞춤 추천 (RecommendUI)
# ─────────────────────────────────────────────
def build_recommend(page, go, app_state):
    temp_tf = ft.TextField(
        value="22", label="현재 기온 (℃)", width=110,
        border_radius=R["md"], filled=True,
        bgcolor=C["card"], border_color=C["border"],
        focused_border_color=C["primary"],
        text_align=ft.TextAlign.CENTER, text_size=F["body"],
    )

    situation_state = {"v": "데일리"}
    situations = ["데일리", "출근", "데이트", "학교", "운동", "중요한 날"]

    result_col    = ft.Column(spacing=S["md"])
    situation_row = ft.Row(wrap=True, spacing=6, run_spacing=6)

    def render_situations():
        situation_row.controls = [
            ft.Container(
                content=ft.Text(s, size=F["xs"], weight=ft.FontWeight.W_600,
                                color="white" if s == situation_state["v"] else C["text"]),
                bgcolor=C["primary"] if s == situation_state["v"] else C["muted"],
                border_radius=R["full"],
                padding=ft.padding.symmetric(horizontal=12, vertical=7),
                on_click=lambda e, s=s: [
                    situation_state.update({"v": s}),
                    render_situations(),
                    do_recommend(),
                    page.update(),
                ],
                ink=True,
            ) for s in situations
        ]

    def do_recommend():
        result_col.controls.clear()
        try:
            temp = float(temp_tf.value or "22")
        except Exception:
            temp = 22
        clothes = app_state.get("clothes", [])
        if not clothes:
            result_col.controls.append(
                empty_state(ft.Icons.CHECKROOM_OUTLINED, "먼저 옷을 등록해 주세요.",
                             "상의와 하의가 최소 1개씩 있어야 합니다.",
                             "옷 등록하러 가기", lambda e: go("/register"))
            )
            page.update(); return
        user = app_state.get("user") or app_state.get("current_user") or {}
        recs = recommend_outfits(user, clothes, temp=temp,
                                  situation=situation_state["v"], top_n=3)
        if not recs:
            result_col.controls.append(
                ft.Container(
                    content=ft.Text("추천 조합을 만들기 위한 옷이 부족합니다.",
                                    size=F["body"], color=C["subtext"],
                                    text_align=ft.TextAlign.CENTER),
                    padding=ft.padding.symmetric(vertical=30),
                )
            )
        else:
            for idx, r in enumerate(recs, 1):
                result_col.controls.append(make_result_card(idx, r))
        page.update()

    def make_result_card(rank, result):
        score  = result.get("score", 0)
        outfit = result.get("outfit", {})
        medal  = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        items_col = ft.Column([
            item_row("상의",    outfit.get("top")),
            item_row("하의",    outfit.get("bottom")),
            item_row("아우터",  outfit.get("outer")),
            item_row("신발",    outfit.get("shoe") or outfit.get("shoes")),
            item_row("악세서리",outfit.get("accessory")),
        ], spacing=8)

        reasons = result.get("summary", [])[:4]

        def show_detail(_):
            details = result.get("details", {})
            detail_rows = [
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{name}: {int(round(d['score']))}/{d['max']}점",
                                size=F["sm"], weight=ft.FontWeight.BOLD, color=C["text"]),
                        *[ft.Text(f"- {r}", size=F["xs"], color=C["subtext"])
                          for r in d.get("reasons", [])[:2]],
                    ], spacing=2),
                    bgcolor=C["card"], border_radius=R["md"],
                    border=ft.border.all(1, C["border"]), padding=S["md"],
                )
                for name, d in details.items()
            ]
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"총점 {score}점", weight=ft.FontWeight.BOLD, color=C["primary"]),
                content=ft.Column(detail_rows, scroll=ft.ScrollMode.AUTO,
                                   height=400, spacing=S["sm"]),
                actions=[ft.TextButton("닫기", on_click=lambda e: page.close(dlg))],
            )
            page.open(dlg)

        def do_save(_):
            saved = _serialize_outfit(dict(result))
            saved["source_label"] = "오늘의 맞춤 코디 추천"
            saved["source"] = "recommend"
            try:
                r = save_outfit_backend(saved, _get_uid(app_state))
                if isinstance(r, dict) and "id" in r:
                    saved["id"] = r["id"]
            except Exception:
                pass
            app_state.setdefault("saved_outfits", []).insert(0, saved)
            page.open(ft.SnackBar(ft.Text("저장 완료!"), bgcolor=C["success"]))

        return card(ft.Column([
            ft.Row([
                ft.Text(f"{medal} 추천 코디 {rank}위", size=F["md"],
                        weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Text(f"{score}점", size=F["md"],
                        weight=ft.FontWeight.BOLD, color=C["primary"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Container(content=items_col, bgcolor=C["bg"],
                         border_radius=R["sm"], padding=S["md"]),
            ft.Container(
                content=ft.Column([
                    ft.Text("추천 이유", size=F["sm"], weight=ft.FontWeight.BOLD, color=C["text"]),
                    *[ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=C["success"], size=14),
                        ft.Text(r, size=F["xs"], color=C["subtext"], expand=True),
                    ], spacing=6) for r in reasons],
                ], spacing=4),
                padding=ft.padding.only(top=8),
            ),
            ft.Row([
                ft.ElevatedButton(
                    "추천 근거 보기", on_click=show_detail,
                    style=ft.ButtonStyle(
                        bgcolor=C["primary_soft"], color=C["primary"],
                        shape=ft.RoundedRectangleBorder(radius=R["md"]),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10)),
                ),
                ft.ElevatedButton(
                    "코디 저장", on_click=do_save,
                    style=ft.ButtonStyle(
                        bgcolor=C["success"], color="white",
                        shape=ft.RoundedRectangleBorder(radius=R["md"]),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10)),
                ),
            ], spacing=8),
        ], spacing=S["sm"]))

    render_situations()
    do_recommend()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=C["text"],
                              on_click=lambda e: go("/")),
                ft.Text("맞춤 코디 추천", size=F["lg"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Container(width=40),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=C["card"],
            padding=ft.padding.symmetric(horizontal=S["sm"], vertical=S["sm"]),
        ),
        ft.Container(
            content=ft.Column([
                card(ft.Column([
                    section("추천 조건"),
                    ft.Container(height=4),
                    ft.Row([
                        ft.Text("현재 기온(℃)", size=F["sm"],
                                weight=ft.FontWeight.BOLD, color=C["text"]),
                        temp_tf,
                        btn_primary("다시 추천", lambda e: do_recommend(),
                                    ft.Icons.REFRESH_ROUNDED, expand=False),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    situation_row,
                ], spacing=S["sm"])),
                result_col,
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 사용자 맞춤 코디 (PersonalRecommendUI) - 원본 그대로 구현
# ─────────────────────────────────────────────
def build_personal_recommend(page, go, app_state):
    """원본 personal_recommend_ui.py 100% 이식.
    사용자 정보 카드 + 자체 점수 계산(퍼스널컬러·체형·스타일 반영).
    """
    user   = app_state.get("user") or app_state.get("current_user") or {}
    clothes= app_state.get("clothes", [])

    styles = user.get("styles", ["미선택"])
    if isinstance(styles, str):
        styles = [styles]

    # ─── 사용자 정보 표시 카드 ───
    user_info_lines = [
        f"이름: {user.get('name', '미입력')}",
        f"추구 패션: {', '.join(styles)}",
        f"체형: {user.get('body_type', '미입력')}",
        f"피부톤: {user.get('skin_tone', '미입력')}",
        f"퍼스널 컬러: {user.get('personal_color', '미입력')}",
    ]

    # ─── 점수 계산 (원본 calc_score 그대로) ───
    def calc_score(cloth):
        score   = 50
        reasons = []
        feature    = _get(cloth, "feature")
        color_name = _get(cloth, "color_name")
        personal_c = user.get("personal_color", "미입력")
        body_type  = user.get("body_type", "미입력")

        for s in styles:
            if s != "미선택" and s in feature:
                score += 20
                reasons.append(f"선호하는 {s} 스타일과 맞습니다.")
                break

        pc_map = {
            "봄 웜":  ["베이지","아이보리","노랑","핑크","하늘색"],
            "여름 쿨":["흰색","회색","네이비","하늘색","파랑"],
            "가을 웜":["베이지","브라운","카키","아이보리"],
            "겨울 쿨":["검정","흰색","네이비","파랑","회색"],
        }
        if personal_c in pc_map and color_name in pc_map[personal_c]:
            score += 15
            label = {"봄 웜":"밝고 부드러운","여름 쿨":"차분하고 시원한",
                     "가을 웜":"따뜻한 계열의","겨울 쿨":"선명하고 깔끔한"}.get(personal_c,"")
            reasons.append(f"{personal_c}톤에 어울리는 {label} 색상입니다.")

        bt_map = {
            "마른 체형":    (["오버핏","와이드"], "자연스러운 실루엣을 줄 수 있는 핏입니다."),
            "보통 체형":    (["정핏","보통"],     "무난하게 어울리는 기본 핏입니다."),
            "통통한 체형":  (["정핏","일자핏","롱기장"], "체형을 안정적으로 잡아주는 핏입니다."),
        }
        if body_type in bt_map:
            kws, msg = bt_map[body_type]
            if any(k in feature for k in kws):
                score += 10
                reasons.append(msg)

        if not reasons:
            reasons.append("등록된 옷 중 기본 조합에 무난하게 사용할 수 있습니다.")
        return score, reasons

    def pick_best(category):
        cats = [c for c in clothes
                if (_get(c,"category") == category)]
        if not cats:
            return None, 0, [f"등록된 {category}가 없습니다."]
        best = max(cats, key=lambda c: calc_score(c)[0])
        sc, rs = calc_score(best)
        return best, sc, rs

    top,   top_sc,   top_r   = pick_best("상의")
    bot,   bot_sc,   bot_r   = pick_best("하의")
    outer, outer_sc, outer_r = pick_best("아우터")
    shoes, shoes_sc, shoes_r = pick_best("신발")
    acc,   acc_sc,   acc_r   = pick_best("악세서리")

    if not top and not bot:
        return ft.Column([
            top_bar(page, "사용자 맞춤 코디", on_back=lambda: go("/")),
            empty_state(ft.Icons.CHECKROOM_OUTLINED, "옷을 먼저 등록해 주세요.",
                        "상의와 하의가 최소 1개씩 있어야 합니다.",
                        "옷 등록하러 가기", lambda e: go("/register")),
        ], spacing=0, expand=True)

    def draw_cloth_card(label, cloth, sc, reasons):
        if cloth is None:
            return ft.Container(
                content=ft.Text(f"{label}: 등록된 옷 없음", size=F["sm"], color=C["hint"]),
                padding=ft.padding.symmetric(vertical=4),
            )
        ip = _get(cloth, "image_path")
        return ft.Container(
            content=ft.Row([
                cloth_image(ip, size=54, radius=8),
                ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(label, size=F["xs"],
                                            weight=ft.FontWeight.W_700, color=C["primary"]),
                            bgcolor=C["primary_soft"], border_radius=R["full"],
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                        ft.Text(_get(cloth,"detail"), size=F["md"],
                                weight=ft.FontWeight.W_700, color=C["text"]),
                    ], spacing=6),
                    ft.Text(f"점수: {sc}점", size=F["xs"], color=C["primary"],
                            weight=ft.FontWeight.W_600),
                    *[ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                                color=C["success"], size=12),
                        ft.Text(r, size=F["xs"], color=C["subtext"], expand=True),
                    ], spacing=4) for r in reasons[:2]],
                ], spacing=3, expand=True),
            ], spacing=S["md"], vertical_alignment=ft.CrossAxisAlignment.START),
            bgcolor=C["bg"], border_radius=R["md"],
            padding=S["md"],
        )

    def do_save(_):
        outfit_raw = {
            "top": top, "bottom": bot, "outer": outer,
            "shoes": shoes, "accessory": acc,
        }
        outfit = _serialize_outfit(outfit_raw)
        parts = []
        if styles and styles != ["미선택"]:
            parts.append(f"{', '.join(styles)} 스타일 선호 반영")
        if user.get("personal_color","미입력") != "미입력":
            parts.append(f"퍼스널 컬러 {user.get('personal_color')} 고려")
        if top and bot:
            parts.append(f"{_get(top,'detail')} + {_get(bot,'detail')} 조합")
        outfit["reason"] = " ".join(parts) or "사용자 맞춤 코디"
        outfit["source_label"] = "사용자 맞춤 코디"
        outfit["source"] = "personal"
        try:
            r = save_outfit_backend(outfit, _get_uid(app_state))
            if isinstance(r, dict) and "id" in r:
                outfit["id"] = r["id"]
        except Exception:
            pass
        app_state.setdefault("saved_outfits", []).insert(0, outfit)
        page.open(ft.SnackBar(ft.Text("저장 완료!"), bgcolor=C["success"]))

    return ft.Column([
        top_bar(page, "사용자 맞춤 코디", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                # 반영된 사용자 정보 카드
                card(ft.Column([
                    section("반영된 사용자 정보"),
                    ft.Container(height=4),
                    *[ft.Text(line, size=F["sm"], color=C["subtext"])
                      for line in user_info_lines],
                ], spacing=4)),
                # 추천 결과
                card(ft.Column([
                    section("추천 코디"),
                    ft.Container(height=4),
                    draw_cloth_card("상의",    top,   top_sc,   top_r),
                    draw_cloth_card("하의",    bot,   bot_sc,   bot_r),
                    draw_cloth_card("아우터",  outer, outer_sc, outer_r),
                    draw_cloth_card("신발",    shoes, shoes_sc, shoes_r),
                    draw_cloth_card("악세서리",acc,   acc_sc,   acc_r),
                ], spacing=S["sm"])),
                btn_primary("이 코디 저장하기", do_save,
                            ft.Icons.FAVORITE_ROUNDED, C["success"]),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 코디해보기 (CoordinationUI)
# ─────────────────────────────────────────────
def build_coordination(page, go, app_state):
    selected = {"top":None,"bottom":None,"outer":None,"shoes":None,"accessory":None}
    cat_map  = [("top","상의","상의"),("bottom","하의","하의"),
                ("outer","아우터","아우터"),("shoes","신발","신발"),
                ("accessory","악세서리","악세서리")]

    preview_col = ft.Column(spacing=4)
    select_col  = ft.Column(spacing=S["md"])

    def get_clothes(cat):
        return [c for c in app_state.get("clothes", [])
                if _get(c,"category") == cat]

    def refresh():
        preview_col.controls = [
            ft.Row([
                ft.Container(ft.Text(f"{title}:", size=F["sm"], weight=ft.FontWeight.BOLD,
                                      color=C["subtext"]), width=60),
                *(
                    [cloth_image(_get(selected[key],"image_path"), 36, 6),
                     ft.Text(f"{_get(selected[key],'detail')} / {_get(selected[key],'color_name')}",
                             size=F["sm"], color=C["text"])]
                    if selected[key] else
                    [ft.Text("선택 안 함", size=F["sm"], color=C["hint"])]
                ),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            for key, title, _ in cat_map
        ]

        select_col.controls.clear()
        for key, title, cat in cat_map:
            cl = get_clothes(cat)
            chips = ft.Row(wrap=True, spacing=6, run_spacing=6)
            for cloth in cl:
                is_sel = selected[key] is cloth
                def make_choose(k, c):
                    def choose(_):
                        selected[k] = None if selected[k] is c else c
                        refresh(); page.update()
                    return choose
                ip = _get(cloth, "image_path")
                chips.controls.append(ft.Container(
                    content=ft.Row([
                        cloth_image(ip, 28, 5) if ip
                        else ft.Container(width=28, height=28,
                                          bgcolor=_get(cloth,"hex","#ccc"),
                                          border_radius=5),
                        ft.Column([
                            ft.Text(_get(cloth,"detail"), size=F["xs"],
                                    weight=ft.FontWeight.W_700,
                                    color="white" if is_sel else C["text"]),
                            ft.Text(_get(cloth,"color_name"), size=F["xs"],
                                    color="white" if is_sel else C["subtext"]),
                        ], spacing=0),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=C["primary"] if is_sel else C["card"],
                    border_radius=R["md"],
                    border=ft.border.all(1, C["primary"] if is_sel else C["border"]),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    on_click=make_choose(key, cloth), ink=True,
                ))
            if not cl:
                chips.controls.append(
                    ft.Text(f"등록된 {title}가 없습니다.", size=F["xs"], color=C["hint"])
                )
            select_col.controls.append(card(ft.Column([
                section(title), ft.Container(height=4), chips,
            ], spacing=S["sm"])))
        page.update()

    def do_save(_):
        if selected["top"] is None or selected["bottom"] is None:
            page.open(ft.SnackBar(
                ft.Text("코디를 저장하려면 상의와 하의를 반드시 선택해야 합니다."),
                bgcolor=C["danger"]))
            return
        parts = [
            f"{_get(selected['top'],'detail')} 상의와 {_get(selected['bottom'],'detail')} 하의를 조합했습니다."
        ]
        if selected["outer"]:
            parts.append(f"아우터로 {_get(selected['outer'],'detail')}를 더했습니다.")
        if selected["shoes"]:
            parts.append(f"신발은 {_get(selected['shoes'],'detail')}을 선택했습니다.")
        if selected["accessory"]:
            parts.append(f"악세서리로 {_get(selected['accessory'],'detail')}를 더했습니다.")
        outfit_raw = {k: selected[k] for k in ["top","bottom","outer","shoes","accessory"]}
        outfit = _serialize_outfit(outfit_raw)
        outfit["reason"] = " ".join(parts)
        outfit["source_label"] = "코디해보기 직접 선택"
        outfit["source"] = "manual"
        try:
            r = save_outfit_backend(outfit, _get_uid(app_state))
            if isinstance(r, dict) and "id" in r:
                outfit["id"] = r["id"]
        except Exception:
            pass
        app_state.setdefault("saved_outfits", []).insert(0, outfit)
        page.open(ft.SnackBar(ft.Text("저장 완료!"), bgcolor=C["success"]))

    refresh()

    return ft.Column([
        top_bar(page, "코디해보기", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                card(ft.Column([
                    section("현재 선택한 코디"),
                    ft.Container(height=4),
                    preview_col,
                ], spacing=S["sm"])),
                select_col,
                ft.Row([
                    btn_primary("이 코디 저장하기", do_save,
                                ft.Icons.FAVORITE_ROUNDED, C["success"]),
                    ft.Container(width=S["sm"]),
                    ft.ElevatedButton("나의 코디 확인",
                        on_click=lambda e: go("/outfit"),
                        style=ft.ButtonStyle(
                            bgcolor=C["primary"], color="white",
                            shape=ft.RoundedRectangleBorder(radius=R["md"]),
                            padding=ft.padding.symmetric(vertical=14),
                            elevation=2), expand=True),
                ]),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 온도별 추천 (TemperatureUI)
# ─────────────────────────────────────────────
def build_temperature(page, go, app_state):
    temp_tf = ft.TextField(
        label="현재 온도 (예: 12)",
        border_radius=R["md"], filled=True,
        bgcolor=C["card"], border_color=C["border"],
        focused_border_color=C["primary"],
        text_align=ft.TextAlign.CENTER, text_size=F["xl"],
    )
    result_col   = ft.Column(spacing=S["md"])
    preview_col2 = ft.Column(spacing=4)
    selected_items = {"top":None,"bottom":None,"outer":None,"shoes":None,"accessory":None}

    def get_temp_info(temp):
        if temp <= 5:
            return {"reason":"5℃ 이하의 추운 날씨라 보온성이 높은 옷을 추천합니다.",
                    "rules":{"상의":["기모 맨투맨","니트","후드티","긴팔","맨투맨"],
                              "하의":["두꺼운 바지","청바지","슬랙스","면바지"],
                              "아우터":["패딩","두꺼운 코트","코트"],
                              "신발":["운동화","스니커즈","구두","로퍼","부츠"]}}
        elif temp <= 11:
            return {"reason":"6~11℃는 쌀쌀한 날씨입니다.",
                    "rules":{"상의":["니트","맨투맨","후드티","긴팔","셔츠"],
                              "하의":["청바지","슬랙스","면바지","두꺼운 바지"],
                              "아우터":["코트","후리스","자켓","점퍼","집업"],
                              "신발":["운동화","스니커즈","구두","로퍼","부츠"]}}
        elif temp <= 16:
            return {"reason":"12~16℃는 선선한 날씨입니다.",
                    "rules":{"상의":["긴팔","셔츠","맨투맨","니트","후드티"],
                              "하의":["청바지","슬랙스","면바지","조거팬츠"],
                              "아우터":["가디건","자켓","얇은 자켓","집업"],
                              "신발":["운동화","스니커즈","구두","로퍼"]}}
        elif temp <= 22:
            return {"reason":"17~22℃는 온화한 날씨입니다.",
                    "rules":{"상의":["긴팔","셔츠","블라우스","맨투맨","니트"],
                              "하의":["청바지","슬랙스","면바지","얇은 바지","치마"],
                              "아우터":["얇은 가디건","얇은 자켓","가디건"],
                              "신발":["운동화","스니커즈","구두","로퍼"]}}
        elif temp <= 27:
            return {"reason":"23~27℃는 따뜻한 날씨입니다.",
                    "rules":{"상의":["반팔","셔츠","블라우스","민소매"],
                              "하의":["얇은 바지","청바지","반바지","치마"],
                              "아우터":["얇은 가디건","얇은 자켓"],
                              "신발":["운동화","스니커즈","로퍼","샌들"]}}
        else:
            return {"reason":"28℃ 이상은 더운 날씨입니다.",
                    "rules":{"상의":["반팔","민소매"],
                              "하의":["반바지","치마","얇은 바지"],
                              "아우터":[],
                              "신발":["운동화","스니커즈","샌들","슬리퍼"]}}

    def refresh_preview():
        lm = {"top":"상의","bottom":"하의","outer":"아우터","shoes":"신발","accessory":"악세서리"}
        preview_col2.controls = [
            ft.Row([
                ft.Container(ft.Text(f"{lm[k]}:", size=F["sm"],
                                      weight=ft.FontWeight.BOLD, color=C["subtext"]), width=60),
                *(
                    [cloth_image(_get(selected_items[k],"image_path"), 32, 6),
                     ft.Text(f"{_get(selected_items[k],'detail')} / {_get(selected_items[k],'color_name')}",
                             size=F["sm"], color=C["text"])]
                    if selected_items[k] else
                    [ft.Text("선택 안 함", size=F["sm"], color=C["hint"])]
                ),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            for k in ["top","bottom","outer","shoes","accessory"]
        ]

    def do_recommend(_=None):
        result_col.controls.clear()
        try:
            temp = float(temp_tf.value or "0")
        except Exception:
            page.open(ft.SnackBar(ft.Text("온도는 숫자로 입력해 주세요."), bgcolor=C["danger"]))
            return
        info = get_temp_info(temp)
        for k in selected_items: selected_items[k] = None
        refresh_preview()

        result_col.controls.append(card(ft.Column([
            section("추천 이유"), ft.Container(height=4),
            ft.Text(info["reason"], size=F["sm"], color=C["subtext"]),
        ], spacing=S["sm"])))

        key_map = {"상의":"top","하의":"bottom","아우터":"outer","신발":"shoes"}
        for cat_name, key in key_map.items():
            allowed  = info["rules"].get(cat_name, [])
            if not allowed: continue
            matching = [c for c in app_state.get("clothes", [])
                        if _get(c,"category") == cat_name and _get(c,"detail") in allowed]
            if not matching: continue
            chips = ft.Row(wrap=True, spacing=6, run_spacing=6)
            for cloth in matching:
                is_sel = selected_items[key] is cloth
                def make_ch(k, c):
                    def ch(_):
                        selected_items[k] = None if selected_items[k] is c else c
                        refresh_preview(); page.update()
                    return ch
                ip = _get(cloth, "image_path")
                chips.controls.append(ft.Container(
                    content=ft.Row([
                        cloth_image(ip, 28, 5) if ip
                        else ft.Container(width=28, height=28,
                                          bgcolor=_get(cloth,"hex","#ccc"),
                                          border_radius=5),
                        ft.Column([
                            ft.Text(_get(cloth,"detail"), size=F["xs"],
                                    weight=ft.FontWeight.W_700,
                                    color="white" if is_sel else C["text"]),
                            ft.Text(_get(cloth,"color_name"), size=F["xs"],
                                    color="white" if is_sel else C["subtext"]),
                        ], spacing=0),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=C["primary"] if is_sel else C["card"],
                    border_radius=R["md"],
                    border=ft.border.all(1, C["primary"] if is_sel else C["border"]),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    on_click=make_ch(key, cloth), ink=True,
                ))
            result_col.controls.append(card(ft.Column([
                section(cat_name), ft.Container(height=4), chips,
            ], spacing=S["sm"])))

        result_col.controls.append(card(ft.Column([
            section("현재 선택"), ft.Container(height=4), preview_col2,
        ], spacing=S["sm"])))
        result_col.controls.append(
            btn_primary("이 코디 저장하기", lambda e: do_temp_save(),
                         ft.Icons.FAVORITE_ROUNDED, C["success"])
        )
        page.update()

    def do_temp_save():
        if not selected_items["top"] or not selected_items["bottom"]:
            page.open(ft.SnackBar(ft.Text("상의와 하의를 선택해 주세요."), bgcolor=C["danger"]))
            return
        outfit = _serialize_outfit(dict(selected_items))
        outfit["reason"] = f"온도 {temp_tf.value}℃ 기준 추천 코디"
        outfit["source_label"] = "온도 기반 추천"
        outfit["source"] = "temperature"
        try:
            r = save_outfit_backend(outfit, _get_uid(app_state))
            if isinstance(r, dict) and "id" in r:
                outfit["id"] = r["id"]
        except Exception:
            pass
        app_state.setdefault("saved_outfits", []).insert(0, outfit)
        page.open(ft.SnackBar(ft.Text("저장 완료!"), bgcolor=C["success"]))

    return ft.Column([
        top_bar(page, "온도별 옷 추천", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                card(ft.Column([
                    section("현재 온도를 입력하세요"),
                    ft.Container(height=6),
                    temp_tf,
                    ft.Text("예: 5, 12, 20, 30", size=F["xs"], color=C["hint"]),
                    ft.Container(height=4),
                    btn_primary("추천 받기", do_recommend, ft.Icons.THERMOSTAT_ROUNDED),
                ], spacing=S["sm"])),
                result_col,
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 오늘의 추천 코디 (TodayRecommendUI)
# ─────────────────────────────────────────────
def build_today(page, go, app_state):
    user    = app_state.get("user") or app_state.get("current_user") or {}
    clothes = app_state.get("clothes", [])
    styles  = user.get("styles", ["미선택"])
    if isinstance(styles, str): styles = [styles]

    def score_cloth(cloth):
        score = 50; reasons = []
        feature    = _get(cloth, "feature")
        color_name = _get(cloth, "color_name")
        pc = user.get("personal_color", "미입력")
        bt = user.get("body_type",      "미입력")

        for s in styles:
            if s != "미선택" and s in feature:
                score += 20
                reasons.append(f"선호하는 {s} 스타일과 맞습니다.")
                break

        pc_map = {
            "봄 웜":  ["베이지","아이보리","노랑","핑크","하늘색"],
            "여름 쿨":["흰색","회색","네이비","하늘색","파랑"],
            "가을 웜":["베이지","브라운","카키","아이보리"],
            "겨울 쿨":["검정","흰색","네이비","파랑","회색"],
        }
        if pc in pc_map and color_name in pc_map[pc]:
            score += 15
            reasons.append(f"{pc}톤에 어울리는 색상입니다.")

        bt_map = {
            "마른 체형":   (["오버핏","와이드"],       "자연스러운 실루엣을 줄 수 있는 핏입니다."),
            "보통 체형":   (["정핏","보통"],            "무난하게 어울리는 기본 핏입니다."),
            "통통한 체형": (["정핏","일자핏","롱기장"], "체형을 안정적으로 잡아주는 핏입니다."),
        }
        if bt in bt_map:
            kws, msg = bt_map[bt]
            if any(k in feature for k in kws):
                score += 10
                reasons.append(msg)

        if not reasons:
            reasons.append("오늘 코디에 무난하게 사용할 수 있습니다.")
        return score, reasons

    def pick_best(cat):
        cats = [c for c in clothes if _get(c,"category") == cat]
        if not cats: return None, 0, []
        best = max(cats, key=lambda c: score_cloth(c)[0])
        sc, rs = score_cloth(best)
        return best, sc, rs

    top,   _, top_r   = pick_best("상의")
    bot,   _, bot_r   = pick_best("하의")
    outer, _, out_r   = pick_best("아우터")
    shoes, _, shoe_r  = pick_best("신발")
    acc,   _, acc_r   = pick_best("악세서리")

    if not top and not bot:
        return ft.Column([
            top_bar(page, "오늘의 추천 코디", on_back=lambda: go("/")),
            empty_state(ft.Icons.CHECKROOM_OUTLINED, "옷을 먼저 등록해 주세요.",
                        "상의와 하의가 최소 1개씩 있어야 합니다.",
                        "옷 등록하러 가기", lambda e: go("/register")),
        ], spacing=0, expand=True)

    def do_save(_):
        outfit_raw = {"top":top,"bottom":bot,"outer":outer,"shoes":shoes,"accessory":acc}
        outfit = _serialize_outfit(outfit_raw)
        parts = []
        if styles and styles != ["미선택"]:
            parts.append(f"{', '.join(styles)} 스타일 선호 반영")
        pc = user.get("personal_color","미입력")
        if pc != "미입력": parts.append(f"퍼스널 컬러 {pc} 고려")
        if top and bot:
            parts.append(f"{_get(top,'detail')} + {_get(bot,'detail')} 기본 코디")
        outfit["reason"] = " ".join(parts) or "오늘의 추천 코디"
        outfit["source_label"] = "오늘의 추천 코디"
        outfit["source"] = "today"
        try:
            r = save_outfit_backend(outfit, _get_uid(app_state))
            if isinstance(r, dict) and "id" in r:
                outfit["id"] = r["id"]
        except Exception:
            pass
        app_state.setdefault("saved_outfits",[]).insert(0, outfit)
        page.open(ft.SnackBar(ft.Text("저장 완료!"), bgcolor=C["success"]))

    cloth_rows = [
        item_row(lb, cl)
        for lb, cl in [("상의",top),("하의",bot),("아우터",outer),("신발",shoes),("악세서리",acc)]
        if cl is not None or lb in ("상의","하의")
    ]
    all_reasons = []
    for rs in [top_r, bot_r, out_r]:
        if rs: all_reasons.extend(rs[:1])

    return ft.Column([
        top_bar(page, "오늘의 추천 코디", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                ft.Text("등록된 옷과 사용자 정보를 기준으로 오늘 입기 좋은 코디를 추천합니다.",
                        size=F["sm"], color=C["subtext"]),
                card(ft.Column([
                    section("오늘의 추천"),
                    ft.Container(height=4),
                    *cloth_rows,
                ], spacing=S["sm"])),
                card(ft.Column([
                    section("추천 이유"), ft.Container(height=4),
                    *[ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                                      color=C["success"], size=14),
                              ft.Text(r, size=F["xs"], color=C["subtext"], expand=True)],
                             spacing=6) for r in all_reasons],
                ], spacing=4)),
                btn_primary("이 코디 저장하기", do_save,
                            ft.Icons.FAVORITE_ROUNDED, C["success"]),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 저장 코디 (OutfitUI)
# ─────────────────────────────────────────────
def build_outfit(page, go, app_state):
    outfits = app_state.get("saved_outfits", [])

    if not outfits:
        return ft.Column([
            top_bar(page, "나의 코디 확인", on_back=lambda: go("/")),
            empty_state(ft.Icons.STYLE_OUTLINED, "저장한 코디가 없습니다.",
                        "오늘의 추천/코디해보기에서 저장해 보세요.",
                        "코디해보기", lambda e: go("/coordination"), C["gray"]),
        ], spacing=0, expand=True)

    groups = [
        ("오늘의 맞춤 코디 추천", []),
        ("사용자 맞춤 코디", []),
        ("오늘의 추천 코디", []),
        ("코디해보기 직접 선택", []),
        ("온도 기반 추천", []),
        ("기타 저장 코디", []),
    ]
    gmap = {n: items for n, items in groups}
    label_map = {
        "recommend": "오늘의 맞춤 코디 추천",
        "personal":  "사용자 맞춤 코디",
        "today":     "오늘의 추천 코디",
        "manual":    "코디해보기 직접 선택",
        "temperature":"온도 기반 추천",
    }
    for outfit in outfits:
        lbl = outfit.get("source_label") or label_map.get(outfit.get("source",""), "기타 저장 코디")
        if lbl not in gmap: lbl = "기타 저장 코디"
        gmap[lbl].append(outfit)

    def make_outfit_card(outfit, idx, sec_name):
        items_col = ft.Column([
            item_row(lb, outfit.get(k1) or outfit.get(k2))
            for lb, k1, k2 in [
                ("상의","top","top"),("하의","bottom","bottom"),
                ("아우터","outer","outer"),("신발","shoes","shoe"),
                ("악세서리","accessory","accessory"),
            ]
        ], spacing=8)

        def on_delete(_):
            def confirm(e):
                page.close(dlg)
                oid = outfit.get("id")
                if oid:
                    try:
                        delete_saved_outfit_backend(oid, _get_uid(app_state))
                    except Exception:
                        pass
                if outfit in app_state.get("saved_outfits", []):
                    app_state["saved_outfits"].remove(outfit)
                go("/outfit")
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("삭제하시겠어요?", weight=ft.FontWeight.BOLD),
                actions=[
                    ft.TextButton("취소", on_click=lambda e: page.close(dlg)),
                    ft.TextButton("삭제", on_click=confirm,
                                  style=ft.ButtonStyle(color=C["danger"])),
                ],
            )
            page.open(dlg)

        return card(ft.Column([
            ft.Row([
                ft.Text(f"코디 {idx}", size=F["md"],
                        weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Container(
                    content=ft.Text(sec_name, size=F["xs"],
                                    weight=ft.FontWeight.W_700, color=C["primary"]),
                    bgcolor=C["primary_soft"], border_radius=R["full"],
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                ),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=C["danger"],
                              icon_size=18, on_click=on_delete),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(content=items_col, bgcolor=C["bg"],
                         border_radius=R["sm"], padding=S["md"]),
            ft.Text(outfit.get("reason",""), size=F["xs"],
                    color=C["subtext"], max_lines=3),
        ], spacing=S["sm"]))

    cards = []
    for sec_name, sec_outfits in groups:
        if not sec_outfits: continue
        cards.append(ft.Text(sec_name, size=F["md"],
                              weight=ft.FontWeight.BOLD, color=C["text"]))
        for i, o in enumerate(sec_outfits, 1):
            cards.append(make_outfit_card(o, i, sec_name))

    return ft.Column([
        top_bar(page, "나의 코디 확인", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column(cards, spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)
