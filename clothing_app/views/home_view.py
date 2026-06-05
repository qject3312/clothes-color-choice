"""홈 화면. 6개 메뉴 카드 + 사용자 정보."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT

try:
    from api_client import get_clothes_from_backend
except Exception:
    def get_clothes_from_backend(user_id="guest"):
        return []


def build_home_view(page, go, current_user, logout_fn):
    """홈 화면."""

    user_id = current_user.get("user_id", "guest")
    nickname = current_user.get("nickname", "게스트")

    # 옷 개수 조회 시도
    try:
        clothes = get_clothes_from_backend(user_id)
        cloth_count = len(clothes) if isinstance(clothes, list) else 0
    except Exception:
        cloth_count = 0

    def menu_card(title, subtitle, icon, color, route):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=COLORS["text_on_color"], size=26),
                        width=48, height=48,
                        bgcolor=color,
                        border_radius=RADIUS["md"],
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=4),
                    ft.Text(title,
                            size=FONT["title_sm"],
                            weight=ft.FontWeight.W_700,
                            color=COLORS["text_primary"]),
                    ft.Text(subtitle,
                            size=FONT["caption"],
                            color=COLORS["text_tertiary"]),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=SPACE["lg"],
            bgcolor=COLORS["card_bg"],
            border_radius=RADIUS["lg"],
            on_click=lambda e: go(route),
            ink=True,
            ink_color=color,
            shadow=ft.BoxShadow(
                blur_radius=18,
                color=COLORS["shadow_light"],
                offset=ft.Offset(0, 4),
            ),
            expand=True,
        )

    def open_menu(_):
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text("메뉴", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.TextButton(
                        "내 옷장",
                        on_click=lambda e: (page.close(dlg), go("/list")),
                    ),
                    ft.TextButton(
                        "온도별 추천",
                        on_click=lambda e: (page.close(dlg), go("/temperature")),
                    ),
                    ft.TextButton(
                        "코디해보기",
                        on_click=lambda e: (page.close(dlg), go("/coordinate")),
                    ),
                    ft.Divider(),
                    ft.TextButton(
                        "로그아웃",
                        on_click=lambda e: (page.close(dlg), logout_fn()),
                        style=ft.ButtonStyle(color=COLORS["pink"]),
                    ),
                ],
                tight=True,
            ),
        )
        page.open(dlg)

    count_badge = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECKROOM_ROUNDED, color=COLORS["primary"], size=16),
                ft.Text(f"등록된 옷 {cloth_count}벌",
                        size=FONT["body_sm"],
                        color=COLORS["primary"],
                        weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        bgcolor=COLORS["primary_soft"],
        border_radius=RADIUS["full"],
    )

    return ft.Column(
        [
            # 상단바
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.MENU_ROUNDED,
                            icon_color=COLORS["text_primary"],
                            icon_size=22,
                            on_click=open_menu,
                        ),
                        ft.Text("옷 추천 앱",
                                size=FONT["title"],
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["text_primary"]),
                        ft.IconButton(
                            content=ft.Container(
                                content=ft.Icon(ft.Icons.PERSON_ROUNDED,
                                                color=COLORS["text_secondary"], size=20),
                                width=40, height=40,
                                bgcolor=COLORS["bg"],
                                border_radius=20,
                                alignment=ft.alignment.center,
                            ),
                            on_click=lambda e: go("/profile"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["md"], vertical=SPACE["sm"]),
                bgcolor=COLORS["card_bg"],
            ),
            # 인사말
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"안녕하세요, {nickname}님 👋",
                                size=FONT["heading"],
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["text_primary"]),
                        ft.Container(height=2),
                        ft.Text("오늘은 어떤 옷을 입어볼까요?",
                                size=FONT["body"],
                                color=COLORS["text_secondary"]),
                        ft.Container(height=10),
                        ft.Row([count_badge], alignment=ft.MainAxisAlignment.START),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.only(
                    left=SPACE["xl"], right=SPACE["xl"],
                    top=SPACE["xl"], bottom=SPACE["lg"],
                ),
            ),
            # 메뉴 그리드 (2x3)
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                menu_card("옷 등록", "사진 또는 직접",
                                          ft.Icons.ADD_ROUNDED, COLORS["primary"], "/register"),
                                menu_card("코디해보기", "옷 조합 추천",
                                          ft.Icons.AUTO_AWESOME_ROUNDED, COLORS["pink"], "/coordinate"),
                            ],
                            spacing=SPACE["md"],
                        ),
                        ft.Row(
                            [
                                menu_card("맞춤 코디", "내 스타일 추천",
                                          ft.Icons.FAVORITE_ROUNDED, COLORS["purple"], "/custom"),
                                menu_card("온도별 추천", "날씨 기반",
                                          ft.Icons.THERMOSTAT_ROUNDED, COLORS["green"], "/temperature"),
                            ],
                            spacing=SPACE["md"],
                        ),
                        ft.Row(
                            [
                                menu_card("내 옷장", "등록한 옷 보기",
                                          ft.Icons.CHECKROOM_ROUNDED, COLORS["indigo"], "/list"),
                                menu_card("오늘의 코디", "추천 코디",
                                          ft.Icons.STYLE_ROUNDED, COLORS["gray"], "/today"),
                            ],
                            spacing=SPACE["md"],
                        ),
                    ],
                    spacing=SPACE["md"],
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["lg"]),
            ),
        ],
        spacing=0,
        expand=True,
    )
