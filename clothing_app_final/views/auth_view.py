"""로그인 / 회원가입 화면."""
import flet as ft
from views.theme import C, R, S, F, STYLE_OPTIONS
from views.components import card, btn_primary, btn_secondary, field, dropdown, section

try:
    from api_client import login_user_backend, signup_user_backend
except Exception:
    def login_user_backend(uid, pw): return {"error": "backend off"}
    def signup_user_backend(u): return {"error": "backend off"}


def build_login(page, go, set_user, load_clothes):
    uid_tf  = field("아이디", icon=ft.Icons.PERSON_OUTLINE_ROUNDED)
    pwd_tf  = field("비밀번호", password=True, icon=ft.Icons.LOCK_OUTLINE_ROUNDED)

    def on_login(_):
        uid = (uid_tf.value or "").strip()
        pwd = (pwd_tf.value or "").strip()
        if not uid or not pwd:
            page.open(ft.SnackBar(ft.Text("아이디와 비밀번호를 입력해 주세요."), bgcolor=C["danger"]))
            return
        r = login_user_backend(uid, pwd)
        if isinstance(r, dict) and ("detail" in r or "error" in r):
            msg = r.get("detail") or r.get("error", "로그인 실패")
            page.open(ft.SnackBar(ft.Text(str(msg)), bgcolor=C["danger"]))
            return
        set_user(r); load_clothes()
        page.open(ft.SnackBar(ft.Text(f"{r.get('name', uid)}님 환영합니다!"), bgcolor=C["success"]))
        go("/")

    def on_guest(_):
        set_user({"user_id":"guest","name":"게스트","gender":"미입력","height":"미입력",
                  "weight":"미입력","body_type":"미입력","skin_tone":"미입력",
                  "personal_color":"미입력","styles":["미선택"]})
        load_clothes(); go("/")

    return ft.Container(
        content=ft.Column([
            ft.Container(height=S["xl"]),
            ft.Column([
                ft.Container(
                    content=ft.Icon(ft.Icons.CHECKROOM_ROUNDED, color="white", size=40),
                    width=76, height=76, bgcolor=C["primary"],
                    border_radius=20, alignment=ft.alignment.center,
                ),
                ft.Container(height=S["sm"]),
                ft.Text("핏픽", size=F["xxl"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Text("맞춤 옷 코디 추천", size=F["sm"], color=C["subtext"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            ft.Container(height=S["lg"]),
            ft.Container(
                content=card(ft.Column([
                    section("로그인"),
                    ft.Container(height=S["xs"]),
                    uid_tf, pwd_tf,
                    ft.Container(height=S["xs"]),
                    btn_primary("로그인", on_login, ft.Icons.LOGIN_ROUNDED),
                    ft.ElevatedButton(
                        content=ft.Text("회원가입", color="white", weight=ft.FontWeight.BOLD, size=F["md"]),
                        on_click=lambda e: go("/signup"),
                        style=ft.ButtonStyle(
                            bgcolor=C["success"],
                            shape=ft.RoundedRectangleBorder(radius=R["md"]),
                            padding=ft.padding.symmetric(vertical=13),
                        ), width=9999,
                    ),
                    ft.TextButton("게스트로 시작", on_click=on_guest,
                                  style=ft.ButtonStyle(color=C["subtext"])),
                ], spacing=S["sm"])),
                padding=ft.padding.symmetric(horizontal=S["lg"]),
            ),
        ], scroll=ft.ScrollMode.AUTO),
        expand=True,
    )


def build_signup(page, go, set_user, load_clothes):
    selected_styles = set()

    uid_tf   = field("아이디",    icon=ft.Icons.PERSON_OUTLINE_ROUNDED)
    pwd_tf   = field("비밀번호",  password=True, icon=ft.Icons.LOCK_OUTLINE_ROUNDED)
    name_tf  = field("이름",      icon=ft.Icons.BADGE_OUTLINED)
    height_tf= field("키 (cm)",   hint="예: 170")
    weight_tf= field("몸무게 (kg)",hint="예: 65")
    gender_dd= dropdown("성별",  "미입력", ["미입력","남성","여성","기타"])
    body_dd  = dropdown("체형",  "미입력", ["미입력","마른 체형","보통 체형","근육형","통통한 체형"])
    skin_dd  = dropdown("피부톤","미입력", ["미입력","밝은 피부톤","중간 피부톤","어두운 피부톤","붉은기 있는 피부톤"])
    color_dd = dropdown("퍼스널 컬러","미입력",["미입력","봄 웜","여름 쿨","가을 웜","겨울 쿨"])

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
                                     C["primary_dk"] if sel else "transparent"),
            ))

    render_styles()

    def do_signup(skip=False):
        uid  = (uid_tf.value or "").strip()
        pwd  = (pwd_tf.value or "").strip()
        name = (name_tf.value or "").strip() or uid
        if not uid or not pwd:
            page.open(ft.SnackBar(ft.Text("아이디와 비밀번호는 필수입니다."), bgcolor=C["danger"]))
            return
        user = {"user_id":uid,"password":pwd,"name":name,
                "gender":   "미입력" if skip else gender_dd.value,
                "height":   "미입력" if skip else ((height_tf.value or "").strip() or "미입력"),
                "weight":   "미입력" if skip else ((weight_tf.value or "").strip() or "미입력"),
                "body_type":"미입력" if skip else body_dd.value,
                "skin_tone":"미입력" if skip else skin_dd.value,
                "personal_color":"미입력" if skip else color_dd.value,
                "styles":   ["미선택"] if skip else (list(selected_styles) or ["미선택"])}
        r = signup_user_backend(user)
        if isinstance(r, dict) and ("detail" in r or "error" in r):
            page.open(ft.SnackBar(ft.Text(str(r.get("detail") or r.get("error"))), bgcolor=C["danger"]))
            return
        set_user(r); load_clothes()
        page.open(ft.SnackBar(ft.Text("가입 완료!"), bgcolor=C["success"]))
        go("/")

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=C["text"],
                              on_click=lambda e: go("/login")),
                ft.Text("회원가입", size=F["lg"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Container(width=40),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=C["card"],
            padding=ft.padding.symmetric(horizontal=S["sm"], vertical=S["sm"]),
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("원하는 정보만 입력해도 가입할 수 있습니다.",
                        size=F["sm"], color=C["subtext"]),
                card(ft.Column([section("필수 정보"), ft.Container(height=4),
                                uid_tf, pwd_tf, name_tf], spacing=S["sm"])),
                card(ft.Column([section("선택 정보"), ft.Container(height=4),
                                gender_dd, height_tf, weight_tf,
                                body_dd, skin_dd, color_dd], spacing=S["sm"])),
                card(ft.Column([
                    section("추구하는 패션"),
                    ft.Text("여러 개 선택 가능", size=F["xs"], color=C["hint"]),
                    ft.Container(height=4),
                    style_row,
                ], spacing=S["sm"])),
                btn_primary("회원가입 완료", lambda e: do_signup(False), ft.Icons.CHECK_ROUNDED),
                btn_primary("선택 정보 건너뛰기", lambda e: do_signup(True),
                            color=C["indigo"]),
                ft.TextButton("로그인 화면으로", on_click=lambda e: go("/login"),
                              style=ft.ButtonStyle(color=C["subtext"])),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)
