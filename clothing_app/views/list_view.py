import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, empty_state


def build_list_view(page, go, clothes_store):
    """등록된 옷 목록 화면."""

    def cloth_card(item, idx):
        def confirm_delete(_):
            def do_delete(e):
                clothes_store.pop(idx)
                page.close(dlg)
                page.open(
                    ft.SnackBar(
                        content=ft.Text("삭제되었습니다"),
                        bgcolor=COLORS["text_secondary"],
                    )
                )
                go("/list")

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("삭제하시겠어요?", weight=ft.FontWeight.BOLD),
                content=ft.Text(f"{item.category} · {item.detail}"),
                actions=[
                    ft.TextButton("취소", on_click=lambda e: page.close(dlg)),
                    ft.TextButton(
                        "삭제",
                        on_click=do_delete,
                        style=ft.ButtonStyle(color=COLORS["pink"]),
                    ),
                ],
            )
            page.open(dlg)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=56, height=56,
                        bgcolor=item.hex,
                        border_radius=RADIUS["md"],
                        border=ft.border.all(1, COLORS["border"]),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            item.category,
                                            size=FONT["caption"],
                                            color=COLORS["primary"],
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor=COLORS["primary_soft"],
                                        border_radius=RADIUS["sm"],
                                    ),
                                    ft.Text(
                                        item.detail,
                                        size=FONT["title_sm"],
                                        weight=ft.FontWeight.W_700,
                                        color=COLORS["text_primary"],
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Text(
                                item.feature,
                                size=FONT["body_sm"],
                                color=COLORS["text_secondary"],
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{item.color_name} · {item.hex}",
                                size=FONT["caption"],
                                color=COLORS["text_tertiary"],
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_color=COLORS["text_tertiary"],
                        icon_size=20,
                        on_click=confirm_delete,
                    ),
                ],
                spacing=SPACE["md"],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLORS["card_bg"],
            padding=SPACE["md"],
            border_radius=RADIUS["lg"],
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=COLORS["shadow_light"],
                offset=ft.Offset(0, 2),
            ),
        )

    if clothes_store:
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{len(clothes_store)}",
                                        size=FONT["display"],
                                        weight=ft.FontWeight.BOLD,
                                        color=COLORS["primary"],
                                    ),
                                    ft.Text("등록된 옷",
                                            size=FONT["body_sm"],
                                            color=COLORS["text_secondary"]),
                                ],
                                spacing=0,
                            ),
                        ],
                    ),
                    padding=ft.padding.only(bottom=SPACE["md"], left=SPACE["xs"]),
                ),
                *[cloth_card(c, len(clothes_store)-1-i)
                  for i, c in enumerate(reversed(clothes_store))],
            ],
            spacing=SPACE["sm"],
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        content = empty_state(
            ft.Icons.CHECKROOM_OUTLINED,
            "등록된 옷이 없어요",
            "첫 번째 옷을 등록해볼까요?",
            "옷 등록하기",
            lambda e: go("/register"),
        )

    return ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=COLORS["text_primary"],
                            on_click=lambda e: go("/"),
                        ),
                        ft.Text(
                            "내 옷장",
                            size=FONT["title"],
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_primary"],
                        ),
                        ft.IconButton(
                            ft.Icons.ADD_ROUNDED,
                            icon_color=COLORS["primary"],
                            on_click=lambda e: go("/register"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=SPACE["md"], vertical=SPACE["sm"]),
                bgcolor=COLORS["card_bg"],
            ),
            ft.Container(
                content=content,
                padding=ft.padding.symmetric(horizontal=SPACE["lg"], vertical=SPACE["lg"]),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
