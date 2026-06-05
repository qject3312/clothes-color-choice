"""프로필 화면."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, primary_button, section_title

try:
    from api_client import get_clothes_from_backend
except Exception:
    def get_clothes_from_backend(user_id="guest"):
        return []


def build_profile_view(page, go, current_user, logout_fn):
    user_id = current_user.get("user_id", "guest")
    nickname = current_user.get("nickname", "게스트")
    username = current_user.get("username", "")
    style = current_user.get("style", "캐주얼")

    try:
        clothes = get_clothes_from_backend(user_id)
        if not isinstance(clothes, list):
            clothes = []
    except Exception:
        clothes = []

    def get_category(item):
        return item.get("category", "") if isinstance(item, dict) else getattr(item, "category", "")

    tops_count = len([c for c in clothes if get_category(c) == "상의"])
    bottoms_count = len([c for c in clothes if get_category(c) == "하의"])
    outers_count = len([c for c in clothes if get_category(c) == "아우터"])

    def stat_box(label, count, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(count), size=FONT["heading"],
                        weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=FONT["caption"], color=COLORS["text_secondary"]),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=SPACE["md"], expand=True,
        )

    def info_row(label, value):
        return ft.Row([
            ft.Text(label, size=FONT["body_sm"],
                    color=COLORS["text_secondary"], width=80),
            ft.Text(value or "-", size=FONT["body"],
                    color=COLORS["text_primary"],
                    weight=ft.FontWeight.W_500),
        ])

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
                              style=ft.ButtonStyle(color=COLORS["pink"])),
            ],
        )
        page.open(dlg)

    return ft.Column(
        [
            top_bar("내 정보", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Icon(ft.Icons.PERSON_ROUNDED,
                                                    color=COLORS["primary"], size=44),
                                    width=90, height=90,
                                    bgcolor=COLORS["primary_soft"],
                                    border_radius=45,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(height=SPACE["sm"]),
                                ft.Text(nickname, size=FONT["title"],
                                        weight=ft.FontWeight.BOLD,
                                        color=COLORS["text_primary"]),
                                ft.Text(f"{style} 스타일", size=FONT["body_sm"],
                                        color=COLORS["text_secondary"]),
                            ], spacing=2,
                               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=SPACE["lg"],
                        ),
                        card(ft.Column([
                            section_title("내 옷장 통계"),
                            ft.Container(height=4),
                            ft.Row([
                                stat_box("상의", tops_count, COLORS["primary"]),
                                ft.Container(width=1, height=40, bgcolor=COLORS["border"]),
                                stat_box("하의", bottoms_count, COLORS["green"]),
                                ft.Container(width=1, height=40, bgcolor=COLORS["border"]),
                                stat_box("아우터", outers_count, COLORS["pink"]),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ], spacing=SPACE["sm"])),
                        card(ft.Column([
                            section_title("내 정보"),
                            ft.Container(height=4),
                            info_row("아이디", user_id),
                            info_row("이름", username),
                            info_row("닉네임", nickname),
                            info_row("스타일", style),
                        ], spacing=SPACE["sm"])),
                        ft.Container(
                            content=primary_button(
                                "로그아웃", confirm_logout,
                                ft.Icons.LOGOUT_ROUNDED,
                                color=COLORS["pink"],
                            ),
                            padding=ft.padding.only(top=SPACE["sm"]),
                        ) if user_id != "guest" else ft.Container(),
                    ],
                    spacing=SPACE["md"],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["lg"], vertical=SPACE["md"]),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
