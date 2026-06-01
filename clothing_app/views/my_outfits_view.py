import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, empty_state, card, section_title


def build_my_outfits_view(page, go, clothes_store, outfits_store):
    """저장한 코디 조합 보기."""

    if not outfits_store:
        return ft.Column(
            [
                top_bar("나의 코디", lambda: go("/")),
                empty_state(
                    ft.Icons.STYLE_OUTLINED,
                    "저장한 코디가 없어요",
                    "코디해보기에서 마음에 드는 조합을 저장해보세요",
                    "코디해보기",
                    lambda e: go("/coordinate"),
                    color=COLORS["gray"],
                ),
            ],
            spacing=0,
            expand=True,
        )

    def outfit_card(outfit):
        cols = []
        if outfit.top:
            cols.append(
                ft.Column(
                    [
                        ft.Container(
                            width=60, height=60,
                            bgcolor=outfit.top.hex,
                            border_radius=RADIUS["md"],
                            border=ft.border.all(1, COLORS["border"]),
                        ),
                        ft.Text("상의", size=FONT["caption"], color=COLORS["text_tertiary"]),
                    ],
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        if outfit.bottom:
            cols.append(
                ft.Column(
                    [
                        ft.Container(
                            width=60, height=60,
                            bgcolor=outfit.bottom.hex,
                            border_radius=RADIUS["md"],
                            border=ft.border.all(1, COLORS["border"]),
                        ),
                        ft.Text("하의", size=FONT["caption"], color=COLORS["text_tertiary"]),
                    ],
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        return card(
            ft.Column(
                [
                    ft.Row(cols, spacing=SPACE["md"]),
                    ft.Container(height=4),
                    ft.Text(
                        outfit.note or "메모 없음",
                        size=FONT["body_sm"],
                        color=COLORS["text_secondary"],
                    ),
                ],
                spacing=SPACE["sm"],
            )
        )

    return ft.Column(
        [
            top_bar("나의 코디", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [outfit_card(o) for o in outfits_store],
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
