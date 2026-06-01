import flet as ft
from logic.recommend_logic import explain_match
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, primary_button, empty_state, section_title


def build_coordinate_view(page, go, clothes_store):
    """코디해보기 - 상의 + 하의 선택해서 매치 평가."""

    tops = [c for c in clothes_store if c.category == "상의"]
    bottoms = [c for c in clothes_store if c.category == "하의"]

    if not tops or not bottoms:
        return ft.Column(
            [
                top_bar("코디해보기", lambda: go("/")),
                empty_state(
                    ft.Icons.AUTO_AWESOME_OUTLINED,
                    "옷이 부족해요",
                    "상의와 하의를 각각 1개 이상 등록해주세요",
                    "옷 등록하러 가기",
                    lambda e: go("/register"),
                    color=COLORS["pink"],
                ),
            ],
            spacing=0,
            expand=True,
        )

    selected = {"top": tops[0], "bottom": bottoms[0]}
    result_container = ft.Container()

    def cloth_chip(item, is_selected, on_click):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=28, height=28,
                        bgcolor=item.hex,
                        border_radius=RADIUS["sm"],
                        border=ft.border.all(1, COLORS["border"]),
                    ),
                    ft.Text(
                        item.detail,
                        size=FONT["body_sm"],
                        color="white" if is_selected else COLORS["text_primary"],
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                spacing=6,
                tight=True,
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            bgcolor=COLORS["primary"] if is_selected else COLORS["card_bg"],
            border_radius=RADIUS["full"],
            border=ft.border.all(1, COLORS["primary"] if is_selected else COLORS["border"]),
            on_click=on_click,
            ink=True,
        )

    def render_chips(items, key):
        return ft.Row(
            [
                cloth_chip(
                    item,
                    selected[key] is item,
                    lambda e, it=item: select(key, it),
                )
                for item in items
            ],
            wrap=True,
            spacing=8,
            run_spacing=8,
        )

    top_chips_container = ft.Container(content=render_chips(tops, "top"))
    bottom_chips_container = ft.Container(content=render_chips(bottoms, "bottom"))

    def select(key, item):
        selected[key] = item
        top_chips_container.content = render_chips(tops, "top")
        bottom_chips_container.content = render_chips(bottoms, "bottom")
        update_preview()
        page.update()

    # 미리보기
    top_preview = ft.Container(
        width=80, height=80,
        bgcolor=selected["top"].hex,
        border_radius=RADIUS["md"],
        border=ft.border.all(1, COLORS["border"]),
    )
    bottom_preview = ft.Container(
        width=80, height=80,
        bgcolor=selected["bottom"].hex,
        border_radius=RADIUS["md"],
        border=ft.border.all(1, COLORS["border"]),
    )
    top_label = ft.Text(
        f"{selected['top'].detail} · {selected['top'].color_name}",
        size=FONT["body_sm"],
        color=COLORS["text_secondary"],
    )
    bottom_label = ft.Text(
        f"{selected['bottom'].detail} · {selected['bottom'].color_name}",
        size=FONT["body_sm"],
        color=COLORS["text_secondary"],
    )

    def update_preview():
        top_preview.bgcolor = selected["top"].hex
        bottom_preview.bgcolor = selected["bottom"].hex
        top_label.value = f"{selected['top'].detail} · {selected['top'].color_name}"
        bottom_label.value = f"{selected['bottom'].detail} · {selected['bottom'].color_name}"

    def evaluate(_):
        is_good, reason = explain_match(
            selected["top"].color_name,
            selected["bottom"].color_name,
        )
        result_color = COLORS["green"] if is_good else COLORS["pink"]
        result_icon = ft.Icons.CHECK_CIRCLE_ROUNDED if is_good else ft.Icons.INFO_ROUNDED
        result_text = "좋은 조합이에요!" if is_good else "고민해볼 조합이에요"

        result_container.content = card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(result_icon, color=result_color, size=22),
                            ft.Text(
                                result_text,
                                size=FONT["title_sm"],
                                weight=ft.FontWeight.W_700,
                                color=result_color,
                            ),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    ft.Container(height=4),
                    ft.Text(
                        reason,
                        size=FONT["body_sm"],
                        color=COLORS["text_secondary"],
                    ),
                ],
                spacing=4,
            ),
        )
        page.update()

    return ft.Column(
        [
            top_bar("코디해보기", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        # 미리보기 카드
                        card(
                            ft.Column(
                                [
                                    section_title("선택한 코디"),
                                    ft.Container(height=4),
                                    ft.Row(
                                        [
                                            ft.Column(
                                                [
                                                    top_preview,
                                                    ft.Text("상의",
                                                            size=FONT["caption"],
                                                            color=COLORS["text_tertiary"]),
                                                ],
                                                spacing=4,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            ft.Container(width=12),
                                            ft.Column(
                                                [
                                                    bottom_preview,
                                                    ft.Text("하의",
                                                            size=FONT["caption"],
                                                            color=COLORS["text_tertiary"]),
                                                ],
                                                spacing=4,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            ft.Container(width=12),
                                            ft.Column(
                                                [
                                                    top_label,
                                                    bottom_label,
                                                ],
                                                spacing=4,
                                                expand=True,
                                            ),
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        # 상의 선택
                        card(
                            ft.Column(
                                [
                                    section_title("상의"),
                                    top_chips_container,
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        # 하의 선택
                        card(
                            ft.Column(
                                [
                                    section_title("하의"),
                                    bottom_chips_container,
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        primary_button("이 코디 평가하기", evaluate,
                                       ft.Icons.AUTO_AWESOME_ROUNDED,
                                       color=COLORS["pink"]),
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
