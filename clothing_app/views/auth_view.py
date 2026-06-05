"""로그인 / 회원가입 화면."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import card, primary_button, section_title

try:
    from api_client import signup_user_backend, login_user_backend
except Exception:
    # 백엔드 없이도 테스트 가능하게
    def signup_user_backend(user):
        return {"error": "backend not available"}
    def login_user_backend(user_id, password):
        return {"error": "backend not available"}


def build_login_view(page, go, set_user):
    """로그인 화면. 성공 시 set_user(user_dict) 호출 후 홈으로."""

    user_id_tf = ft.TextField(
        label="아이디",
        hint_text="아이디를 입력하세요",
        border_radius=RADIUS["md"],
        filled=True,
        bgcolor=COLORS["card_bg"],
        border_color=COLORS["border"],
        text_size=FONT["body"],
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
    )
    password_tf = ft.TextField(
        label="비밀번호",
        hint_text="비밀번호를 입력하세요",
        password=True,
        can_reveal_password=True,
        border_radius=RADIUS["md"],
        filled=True,
        bgcolor=COLORS["card_bg"],
        border_color=COLORS["border"],
        text_size=FONT["body"],
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
    )

    error_text = ft.Text("", size=FONT["body_sm"], color=COLORS["pink"])

    def on_login(_):
        uid = (user_id_tf.value or "").strip()
        pwd = (password_tf.value or "").strip()
        if not uid or not pwd:
            error_text.value = "아이디와 비밀번호를 입력해주세요"
            page.update()
            return

        result = login_user_backend(uid, pwd)
        if "error" in result:
            error_text.value = f"로그인 실패: {result.get('error', '알 수 없는 오류')}"
            page.update()
            return

        # 로그인 성공
        set_user(result)
        page.open(
            ft.SnackBar(
                content=ft.Text(f"{result.get('nickname', uid)}님 환영합니다!"),
                bgcolor=COLORS["green"],
            )
        )
        go("/")

    def on_guest(_):
        # 게스트 모드
        set_user({"user_id": "guest", "nickname": "게스트", "style": "캐주얼"})
        go("/")

    return ft.Column(
        [
            ft.Container(height=SPACE["xxl"]),
            # 로고/타이틀
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECKROOM_ROUNDED,
                                color="white",
                                size=44,
                            ),
                            width=80, height=80,
                            bgcolor=COLORS["primary"],
                            border_radius=20,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(height=SPACE["md"]),
                        ft.Text(
                            "옷 추천 앱",
                            size=FONT["heading"],
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"],
                        ),
                        ft.Text(
                            "오늘의 코디를 추천받아보세요",
                            size=FONT["body_sm"],
                            color=COLORS["text_secondary"],
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                padding=ft.padding.symmetric(vertical=SPACE["lg"]),
            ),
            # 로그인 폼
            ft.Container(
                content=card(
                    ft.Column(
                        [
                            section_title("로그인"),
                            ft.Container(height=4),
                            user_id_tf,
                            password_tf,
                            error_text,
                            ft.Container(height=4),
                            primary_button("로그인", on_login,
                                           ft.Icons.LOGIN_ROUNDED),
                            ft.TextButton(
                                "회원가입",
                                on_click=lambda e: go("/signup"),
                                style=ft.ButtonStyle(
                                    color=COLORS["primary"],
                                ),
                            ),
                            ft.TextButton(
                                "게스트로 시작하기",
                                on_click=on_guest,
                                style=ft.ButtonStyle(
                                    color=COLORS["text_secondary"],
                                ),
                            ),
                        ],
                        spacing=SPACE["sm"],
                    )
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["lg"]),
            ),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )


def build_signup_view(page, go):
    """회원가입 화면."""

    user_id_tf = ft.TextField(
        label="아이디",
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
    )
    username_tf = ft.TextField(
        label="이름",
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        prefix_icon=ft.Icons.BADGE_OUTLINED,
    )
    nickname_tf = ft.TextField(
        label="닉네임",
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        prefix_icon=ft.Icons.FACE_OUTLINED,
    )
    password_tf = ft.TextField(
        label="비밀번호", password=True, can_reveal_password=True,
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
    )
    style_dd = ft.Dropdown(
        label="선호 스타일", value="캐주얼",
        options=[ft.dropdown.Option(s) for s in ["캐주얼", "포멀", "스트릿", "미니멀", "스포티"]],
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
    )

    error_text = ft.Text("", size=FONT["body_sm"], color=COLORS["pink"])

    def on_signup(_):
        if not all([user_id_tf.value, username_tf.value, nickname_tf.value, password_tf.value]):
            error_text.value = "모든 항목을 입력해주세요"
            page.update()
            return

        result = signup_user_backend({
            "user_id": user_id_tf.value.strip(),
            "username": username_tf.value.strip(),
            "nickname": nickname_tf.value.strip(),
            "password": password_tf.value.strip(),
            "style": style_dd.value,
        })

        if "error" in result:
            error_text.value = f"회원가입 실패: {result.get('error')}"
            page.update()
            return

        page.open(
            ft.SnackBar(
                content=ft.Text("회원가입 완료! 로그인해주세요"),
                bgcolor=COLORS["green"],
            )
        )
        go("/login")

    return ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=COLORS["text_primary"],
                            on_click=lambda e: go("/login"),
                        ),
                        ft.Text("회원가입",
                                size=FONT["title"],
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["text_primary"]),
                        ft.Container(width=40),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["md"], vertical=SPACE["sm"]),
                bgcolor=COLORS["card_bg"],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        card(
                            ft.Column(
                                [
                                    section_title("정보 입력"),
                                    ft.Container(height=4),
                                    user_id_tf,
                                    username_tf,
                                    nickname_tf,
                                    password_tf,
                                    style_dd,
                                    error_text,
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        ft.Container(
                            content=primary_button(
                                "가입하기", on_signup,
                                ft.Icons.CHECK_ROUNDED,
                            ),
                            padding=ft.padding.only(top=SPACE["sm"]),
                        ),
                    ],
                    spacing=SPACE["md"],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["lg"], vertical=SPACE["lg"]),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
