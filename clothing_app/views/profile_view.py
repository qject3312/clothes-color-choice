import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, section_title


def build_profile_view(page, go, clothes_store):
    """프로필 화면."""

    tops_count = len([c for c in clothes_store if c.category == "상의"])
    bottoms_count = len([c for c in clothes_store if c.category == "하의"])
    outers_count = len([c for c in clothes_store if c.category == "아우터"])

    def stat_box(label, count, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        str(count),
                        size=FONT["heading"],
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                    ft.Text(
                        label,
                        size=FONT["caption"],
                        color=COLORS["text_secondary"],
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=SPACE["md"],
            expand=True,
        )

    return ft.Column(
        [
            top_bar("내 정보", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        # 프로필 헤더
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Icon(
                                            ft.Icons.PERSON_ROUNDED,
                                            color=COLORS["primary"],
                                            size=44,
                                        ),
                                        width=90, height=90,
                                        bgcolor=COLORS["primary_soft"],
                                        border_radius=45,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(height=SPACE["sm"]),
                                    ft.Text(
                                        "사용자",
                                        size=FONT["title"],
                                        weight=ft.FontWeight.BOLD,
                                        color=COLORS["text_primary"],
                                    ),
                                    ft.Text(
                                        "캐주얼 스타일",
                                        size=FONT["body_sm"],
                                        color=COLORS["text_secondary"],
                                    ),
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=SPACE["lg"],
                        ),
                        # 통계 카드
                        card(
                            ft.Column(
                                [
                                    section_title("내 옷장 통계"),
                                    ft.Container(height=4),
                                    ft.Row(
                                        [
                                            stat_box("상의", tops_count, COLORS["primary"]),
                                            ft.Container(
                                                width=1, height=40,
                                                bgcolor=COLORS["border"],
                                            ),
                                            stat_box("하의", bottoms_count, COLORS["green"]),
                                            ft.Container(
                                                width=1, height=40,
                                                bgcolor=COLORS["border"],
                                            ),
                                            stat_box("아우터", outers_count, COLORS["pink"]),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        # 정보 카드
                        card(
                            ft.Column(
                                [
                                    section_title("내 정보"),
                                    ft.Container(height=4),
                                    info_row("이름", "사용자"),
                                    info_row("선호 스타일", "캐주얼"),
                                    info_row("관심사", "옷 추천 / 색 조합"),
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
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


def info_row(label, value):
    return ft.Row(
        [
            ft.Text(
                label,
                size=FONT["body_sm"],
                color=COLORS["text_secondary"],
                width=80,
            ),
            ft.Text(
                value,
                size=FONT["body"],
                color=COLORS["text_primary"],
                weight=ft.FontWeight.W_500,
            ),
        ],
    )
