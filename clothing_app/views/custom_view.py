import flet as ft
from logic.recommend_logic import get_color_style_info
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, section_title


# 미리 정의된 컬러 팔레트
COLOR_PALETTE = [
    ("검정", "#1a1a1a"),
    ("흰색", "#ffffff"),
    ("회색", "#888888"),
    ("네이비", "#1e3a8a"),
    ("베이지", "#e8d5b7"),
    ("카키", "#8a8866"),
    ("브라운", "#8b5a3c"),
    ("빨강", "#dc2626"),
    ("핑크", "#ec4899"),
    ("노랑", "#fbbf24"),
    ("파랑", "#3b82f6"),
    ("초록", "#22c55e"),
]


def build_custom_view(page, go, clothes_store):
    """맞춤 코디 - 색상 선택 → 어울리는 색 추천."""

    selected_color = {"name": "검정", "hex": "#1a1a1a"}
    result_container = ft.Container()

    def make_result_card():
        info = get_color_style_info(selected_color["name"])

        # 추천 색상 찾아서 hex 매칭
        recommend_widgets = []
        for c_name in info["recommended"]:
            hex_match = next((h for n, h in COLOR_PALETTE if n == c_name), "#cccccc")
            recommend_widgets.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=24, height=24,
                                bgcolor=hex_match,
                                border_radius=RADIUS["sm"],
                                border=ft.border.all(1, COLORS["border"]),
                            ),
                            ft.Text(
                                c_name,
                                size=FONT["body_sm"],
                                color=COLORS["text_primary"],
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    bgcolor=COLORS["green_soft"],
                    border_radius=RADIUS["full"],
                )
            )

        avoid_widgets = [
            ft.Container(
                content=ft.Text(
                    a,
                    size=FONT["body_sm"],
                    color=COLORS["pink"],
                    weight=ft.FontWeight.W_500,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                bgcolor=COLORS["pink_soft"],
                border_radius=RADIUS["full"],
            )
            for a in info["avoid"]
        ]

        return ft.Column(
            [
                # 선택한 색
                card(
                    ft.Column(
                        [
                            section_title("선택한 색"),
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    ft.Container(
                                        width=56, height=56,
                                        bgcolor=selected_color["hex"],
                                        border_radius=RADIUS["md"],
                                        border=ft.border.all(1, COLORS["border"]),
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                selected_color["name"],
                                                size=FONT["title_sm"],
                                                weight=ft.FontWeight.BOLD,
                                                color=COLORS["text_primary"],
                                            ),
                                            ft.Text(
                                                selected_color["hex"],
                                                size=FONT["body_sm"],
                                                color=COLORS["text_tertiary"],
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=SPACE["md"],
                            ),
                        ],
                        spacing=SPACE["sm"],
                    )
                ),
                # 잘 어울리는 색
                card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED,
                                            color=COLORS["green"], size=20),
                                    ft.Text("잘 어울리는 색",
                                            size=FONT["title_sm"],
                                            weight=ft.FontWeight.W_700,
                                            color=COLORS["text_primary"]),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            ft.Container(height=4),
                            ft.Row(recommend_widgets, wrap=True, spacing=6, run_spacing=6),
                            ft.Container(height=4),
                            ft.Text(
                                info["reason"],
                                size=FONT["body_sm"],
                                color=COLORS["text_secondary"],
                            ),
                        ],
                        spacing=SPACE["sm"],
                    )
                ),
                # 피해야 할 색
                card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED,
                                            color=COLORS["pink"], size=20),
                                    ft.Text("피하면 좋은 색",
                                            size=FONT["title_sm"],
                                            weight=ft.FontWeight.W_700,
                                            color=COLORS["text_primary"]),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            ft.Container(height=4),
                            ft.Row(avoid_widgets, wrap=True, spacing=6, run_spacing=6),
                            ft.Container(height=4),
                            ft.Text(
                                info["avoid_reason"],
                                size=FONT["body_sm"],
                                color=COLORS["text_secondary"],
                            ),
                        ],
                        spacing=SPACE["sm"],
                    )
                ),
            ],
            spacing=SPACE["md"],
        )

    def color_swatch(name, hex_color):
        is_selected = selected_color["name"] == name
        def on_tap(_):
            selected_color["name"] = name
            selected_color["hex"] = hex_color
            palette_container.content = render_palette()
            result_container.content = make_result_card()
            page.update()
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        width=48, height=48,
                        bgcolor=hex_color,
                        border_radius=RADIUS["md"],
                        border=ft.border.all(
                            3 if is_selected else 1,
                            COLORS["primary"] if is_selected else COLORS["border"],
                        ),
                    ),
                    ft.Text(
                        name,
                        size=FONT["caption"],
                        color=COLORS["text_secondary"],
                        weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=on_tap,
            ink=True,
            padding=4,
            border_radius=RADIUS["md"],
        )

    def render_palette():
        return ft.Row(
            [color_swatch(n, h) for n, h in COLOR_PALETTE],
            wrap=True,
            spacing=4,
            run_spacing=4,
        )

    palette_container = ft.Container(content=render_palette())
    result_container.content = make_result_card()

    return ft.Column(
        [
            top_bar("맞춤 코디", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        card(
                            ft.Column(
                                [
                                    section_title("색상 선택"),
                                    ft.Text(
                                        "원하는 색을 선택해보세요",
                                        size=FONT["body_sm"],
                                        color=COLORS["text_secondary"],
                                    ),
                                    ft.Container(height=4),
                                    palette_container,
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        result_container,
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
