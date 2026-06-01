import flet as ft
from logic.recommend_logic import get_temperature_recommendation
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, section_title


def build_temperature_view(page, go, clothes_store):
    """온도 입력 → 의상 추천."""

    temp_state = {"value": 20}
    result_container = ft.Container()

    # 온도 표시
    temp_display = ft.Text(
        f"{temp_state['value']}°",
        size=FONT["display"] + 18,
        weight=ft.FontWeight.BOLD,
        color=COLORS["primary"],
    )
    temp_label = ft.Text(
        "선선함",
        size=FONT["title_sm"],
        weight=ft.FontWeight.W_600,
        color=COLORS["text_secondary"],
    )

    def render_result():
        rec = get_temperature_recommendation(temp_state["value"])

        def make_chip(text, color):
            return ft.Container(
                content=ft.Text(
                    text,
                    size=FONT["body_sm"],
                    color=color,
                    weight=ft.FontWeight.W_500,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                bgcolor=COLORS["primary_soft"] if color == COLORS["primary"] else COLORS["green_soft"],
                border_radius=RADIUS["full"],
            )

        sections = []

        if rec["top"]:
            sections.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.CHECKROOM_ROUNDED,
                                        color=COLORS["primary"], size=18),
                                ft.Text("상의", size=FONT["body"],
                                        weight=ft.FontWeight.W_700,
                                        color=COLORS["text_primary"]),
                            ],
                            spacing=6,
                            tight=True,
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            [make_chip(t, COLORS["primary"]) for t in rec["top"]],
                            wrap=True, spacing=6, run_spacing=6,
                        ),
                    ],
                    spacing=4,
                )
            )

        if rec["bottom"]:
            sections.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.STYLE_ROUNDED,
                                        color=COLORS["green"], size=18),
                                ft.Text("하의", size=FONT["body"],
                                        weight=ft.FontWeight.W_700,
                                        color=COLORS["text_primary"]),
                            ],
                            spacing=6,
                            tight=True,
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            [make_chip(b, COLORS["green"]) for b in rec["bottom"]],
                            wrap=True, spacing=6, run_spacing=6,
                        ),
                    ],
                    spacing=4,
                )
            )

        if rec["outer"]:
            sections.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.AC_UNIT_ROUNDED,
                                        color=COLORS["indigo"], size=18),
                                ft.Text("아우터", size=FONT["body"],
                                        weight=ft.FontWeight.W_700,
                                        color=COLORS["text_primary"]),
                            ],
                            spacing=6,
                            tight=True,
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            [make_chip(o, COLORS["primary"]) for o in rec["outer"]],
                            wrap=True, spacing=6, run_spacing=6,
                        ),
                    ],
                    spacing=4,
                )
            )

        return ft.Column(
            [
                card(
                    ft.Column(
                        [
                            section_title("추천 의상"),
                            ft.Container(height=4),
                            *sections,
                        ],
                        spacing=SPACE["md"],
                    )
                ),
                card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
                                            color=COLORS["orange"], size=18),
                                    ft.Text("코디 팁",
                                            size=FONT["title_sm"],
                                            weight=ft.FontWeight.W_700,
                                            color=COLORS["text_primary"]),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            ft.Container(height=4),
                            ft.Text(rec["reason"],
                                    size=FONT["body_sm"],
                                    color=COLORS["text_secondary"]),
                            ft.Container(height=8),
                            ft.Text(
                                f"피해야 할 옷: {rec['avoid']}",
                                size=FONT["caption"],
                                color=COLORS["pink"],
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=2,
                    )
                ),
            ],
            spacing=SPACE["md"],
        )

    def on_slider(e):
        temp_state["value"] = int(e.control.value)
        temp_display.value = f"{temp_state['value']}°"
        rec = get_temperature_recommendation(temp_state["value"])
        temp_label.value = rec["label"]
        result_container.content = render_result()
        page.update()

    # 빠른 선택 버튼
    def quick_btn(label, temp):
        def on_click(_):
            temp_state["value"] = temp
            slider.value = temp
            temp_display.value = f"{temp}°"
            rec = get_temperature_recommendation(temp)
            temp_label.value = rec["label"]
            result_container.content = render_result()
            page.update()
        return ft.Container(
            content=ft.Text(
                label,
                size=FONT["body_sm"],
                weight=ft.FontWeight.W_600,
                color=COLORS["text_primary"],
            ),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            bgcolor=COLORS["bg"],
            border_radius=RADIUS["full"],
            border=ft.border.all(1, COLORS["border"]),
            on_click=on_click,
            ink=True,
        )

    slider = ft.Slider(
        min=-10, max=35, value=20, divisions=45,
        active_color=COLORS["primary"],
        on_change=on_slider,
    )

    result_container.content = render_result()

    return ft.Column(
        [
            top_bar("온도별 추천", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        card(
                            ft.Column(
                                [
                                    section_title("기온 입력"),
                                    ft.Container(height=4),
                                    ft.Row(
                                        [
                                            ft.Column(
                                                [temp_display, temp_label],
                                                spacing=0,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                expand=True,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    ft.Container(height=8),
                                    slider,
                                    ft.Row(
                                        [
                                            quick_btn("❄ 영하", -5),
                                            quick_btn("🍂 쌀쌀", 12),
                                            quick_btn("🌤 선선", 20),
                                            quick_btn("☀ 더움", 30),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
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
