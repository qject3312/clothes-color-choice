"""프로필 화면 + 프로필 수정 화면."""
import flet as ft
from views.theme import C, R, S, F, STYLE_OPTIONS
from views.components import (card, top_bar, btn_primary, btn_secondary,
                               section, field, dropdown)

try:
    from api_client import update_user_backend
except Exception:
    def update_user_backend(u): return {"error": "off"}


def build_profile(page, go, app_state, logout_fn):
    user = app_state.get("user") or app_state.get("current_user") or {}
    clothes = app_state.get("clothes", [])

    styles = user.get("styles", ["미선택"])
    if isinstance(styles, str): styles = [styles]

    from collections import Counter
    cat_cnt = Counter(
        (c.get("category") if isinstance(c,dict) else getattr(c,"category","")) or "기타"
        for c in clothes
    )

    def info_row(label, value):
        return ft.Row([
            ft.Text(label, size=F["sm"], weight=ft.FontWeight.BOLD,
                    color=C["subtext"], width=90),
            ft.Text(str(value or "미입력"), size=F["sm"], color=C["text"], expand=True),
        ])

    def stat_box(label, count, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(count), size=F["xxl"], weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=F["xs"], color=C["subtext"]),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True, padding=S["md"],
        )

    def confirm_logout(_):
        def do_logout(e):
            page.close(dlg)
            logout_fn()
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("로그아웃하시겠어요?", weight=ft.FontWeight.BOLD),
            actions=[
                ft.TextButton("취소", on_click=lambda e: page.close(dlg)),
                ft.TextButton("로그아웃", on_click=do_logout,
                              style=ft.ButtonStyle(color=C["danger"])),
            ],
        )
        page.open(dlg)

    is_guest = user.get("user_id") in (None, "", "guest")

    return ft.Column([
        top_bar(page, "사용자 정보", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                # 프로필 헤더
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON_ROUNDED,
                                            color=C["primary"], size=40),
                            width=80, height=80,
                            bgcolor=C["primary_soft"],
                            border_radius=40,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(height=S["sm"]),
                        ft.Text(user.get("name", "사용자"),
                                size=F["xl"], weight=ft.FontWeight.BOLD, color=C["text"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    padding=ft.padding.symmetric(vertical=S["lg"]),
                ),
                # 옷장 통계
                card(ft.Column([
                    section("내 옷장 통계"),
                    ft.Container(height=4),
                    ft.Row([
                        stat_box("상의",    cat_cnt.get("상의",0),    C["primary"]),
                        ft.Container(width=1, height=40, bgcolor=C["border"]),
                        stat_box("하의",    cat_cnt.get("하의",0),    C["success"]),
                        ft.Container(width=1, height=40, bgcolor=C["border"]),
                        stat_box("아우터",  cat_cnt.get("아우터",0),  C["pink"]),
                        ft.Container(width=1, height=40, bgcolor=C["border"]),
                        stat_box("전체",    len(clothes),             C["indigo"]),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=S["sm"])),
                # 정보 카드
                card(ft.Column([
                    section("내 정보"),
                    ft.Container(height=4),
                    info_row("아이디",       user.get("user_id","")),
                    info_row("이름",         user.get("name","")),
                    info_row("성별",         user.get("gender","")),
                    info_row("키",           user.get("height","")),
                    info_row("몸무게",       user.get("weight","")),
                    info_row("체형",         user.get("body_type","")),
                    info_row("피부톤",       user.get("skin_tone","")),
                    info_row("퍼스널컬러",   user.get("personal_color","")),
                    info_row("추구 패션",    ", ".join(styles)),
                ], spacing=S["sm"])),
                # 버튼
                btn_primary("정보 수정", lambda e: go("/edit_profile"),
                            ft.Icons.EDIT_ROUNDED)
                if not is_guest else ft.Container(),

                btn_primary("로그아웃", confirm_logout,
                            ft.Icons.LOGOUT_ROUNDED, C["danger"])
                if not is_guest else ft.Container(),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["md"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


def build_edit_profile(page, go, app_state):
    user = dict(app_state.get("user") or app_state.get("current_user") or {})
    if not user:
        go("/"); return ft.Container()

    selected_styles = set()
    raw_styles = user.get("styles", [])
    if isinstance(raw_styles, str): raw_styles = [raw_styles]
    for s in raw_styles:
        if s != "미선택": selected_styles.add(s)

    def _val(key, default=""):
        v = user.get(key, default)
        return "" if v in ("미입력", None) else str(v)

    name_tf   = field("이름",          value=_val("name"))
    height_tf = field("키 (cm)",       value=_val("height"))
    weight_tf = field("몸무게 (kg)",   value=_val("weight"))
    gender_dd = dropdown("성별",        user.get("gender","미입력"),
                          ["미입력","남성","여성","기타"])
    body_dd   = dropdown("체형",        user.get("body_type","미입력"),
                          ["미입력","마른 체형","보통 체형","근육형","통통한 체형"])
    skin_dd   = dropdown("피부톤",      user.get("skin_tone","미입력"),
                          ["미입력","밝은 피부톤","중간 피부톤","어두운 피부톤","붉은기 있는 피부톤"])
    pc_dd     = dropdown("퍼스널 컬러", user.get("personal_color","미입력"),
                          ["미입력","봄 웜","여름 쿨","가을 웜","겨울 쿨"])

    style_row = ft.Row(wrap=True, spacing=6, run_spacing=6)

    def render_styles():
        style_row.controls.clear()
        for sname, scolor in STYLE_OPTIONS:
            sel = sname in selected_styles
            def make_tap(s):
                def tap(_):
                    if s in selected_styles: selected_styles.remove(s)
                    else: selected_styles.add(s)
                    render_styles(); page.update()
                return tap
            style_row.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text(sname, size=F["sm"], weight=ft.FontWeight.W_700,
                            color="white" if sel else C["text"]),
                    ft.Text("✓" if sel else "", size=F["xs"],
                            color="white" if sel else "transparent"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                width=132, height=56,
                bgcolor=C["primary"] if sel else scolor,
                border_radius=R["md"], alignment=ft.alignment.center,
                on_click=make_tap(sname), ink=True,
                border=ft.border.all(3 if sel else 0,
                                     "#1a6ee8" if sel else "transparent"),
            ))

    render_styles()

    def on_save(_):
        name   = (name_tf.value   or "").strip() or user.get("user_id","사용자")
        height = (height_tf.value or "").strip()
        weight = (weight_tf.value or "").strip()

        user["name"]           = name
        user["gender"]         = gender_dd.value
        user["height"]         = height or "미입력"
        user["weight"]         = weight or "미입력"
        user["body_type"]      = body_dd.value
        user["skin_tone"]      = skin_dd.value
        user["personal_color"] = pc_dd.value
        user["styles"]         = list(selected_styles) if selected_styles else ["미선택"]

        uid = user.get("user_id")
        if uid and uid != "guest":
            result = update_user_backend(user)
            if isinstance(result, dict) and "error" not in result and "detail" not in result:
                # 서버에서 최신값 반영
                user.update(result)
            elif isinstance(result, dict) and "detail" in result:
                page.open(ft.SnackBar(
                    ft.Text(f"저장 실패: {result['detail']}"), bgcolor=C["danger"]))
                return

        # app_state에 반영
        if "user" in app_state:
            app_state["user"] = user
        if "current_user" in app_state:
            app_state["current_user"] = user

        page.open(ft.SnackBar(ft.Text("수정 완료!"), bgcolor=C["success"]))
        go("/profile")

    return ft.Column([
        top_bar(page, "사용자 정보 수정", on_back=lambda: go("/profile")),
        ft.Container(
            content=ft.Column([
                # 아이디 (읽기 전용)
                card(ft.Column([
                    ft.Row([
                        ft.Text("아이디", size=F["sm"], weight=ft.FontWeight.BOLD,
                                color=C["subtext"], width=70),
                        ft.Text(user.get("user_id",""), size=F["body"], color=C["text"]),
                    ]),
                ], spacing=S["sm"])),
                card(ft.Column([
                    section("기본 정보"), ft.Container(height=4),
                    name_tf, gender_dd, height_tf, weight_tf,
                    body_dd, skin_dd, pc_dd,
                ], spacing=S["sm"])),
                card(ft.Column([
                    section("추구하는 패션"),
                    ft.Text("여러 개 선택 가능", size=F["xs"], color=C["hint"]),
                    ft.Container(height=4),
                    style_row,
                ], spacing=S["sm"])),
                btn_primary("수정 저장", on_save,
                            ft.Icons.CHECK_ROUNDED, C["success"]),
                btn_secondary("취소", lambda e: go("/profile")),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)
