"""내 옷장 - 백엔드에서 가져와서 목록으로 표시."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, empty_state

try:
    from api_client import get_clothes_from_backend, delete_clothing_backend
except Exception:
    def get_clothes_from_backend(user_id="guest"):
        return []
    def delete_clothing_backend(clothing_id, user_id="guest"):
        return {"error": "backend not available"}


def build_list_view(page, go, current_user):
    """등록된 옷 목록."""

    user_id = current_user.get("user_id", "guest")

    try:
        clothes = get_clothes_from_backend(user_id)
        if not isinstance(clothes, list):
            clothes = []
    except Exception:
        clothes = []

    def cloth_card(item):
        # 백엔드 응답 형식에 맞춰 키 처리
        cloth_id = item.get("id") if isinstance(item, dict) else getattr(item, "id", None)
        category = item.get("category") if isinstance(item, dict) else getattr(item, "category", "")
        detail = item.get("detail") if isinstance(item, dict) else getattr(item, "detail", "")
        feature = item.get("feature") if isinstance(item, dict) else getattr(item, "feature", "")
        color_hex = (item.get("color_hex") or item.get("hex") if isinstance(item, dict)
                     else getattr(item, "hex", "#cccccc"))
        color_name = (item.get("color_name") if isinstance(item, dict)
                      else getattr(item, "color_name", ""))

        def confirm_delete(_):
            def do_delete(e):
                if cloth_id is not None:
                    delete_clothing_backend(cloth_id, user_id)
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
                content=ft.Text(f"{category} · {detail}"),
                actions=[
                    ft.TextButton("취소", on_click=lambda e: page.close(dlg)),
                    ft.TextButton("삭제", on_click=do_delete,
                                  style=ft.ButtonStyle(color=COLORS["pink"])),
                ],
            )
            page.open(dlg)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=56, height=56,
                        bgcolor=color_hex,
                        border_radius=RADIUS["md"],
                        border=ft.border.all(1, COLORS["border"]),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(category,
                                                        size=FONT["caption"],
                                                        color=COLORS["primary"],
                                                        weight=ft.FontWeight.W_600),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor=COLORS["primary_soft"],
                                        border_radius=RADIUS["sm"],
                                    ),
                                    ft.Text(detail,
                                            size=FONT["title_sm"],
                                            weight=ft.FontWeight.W_700,
                                            color=COLORS["text_primary"]),
                                ],
                                spacing=6,
                            ),
                            ft.Text(feature,
                                    size=FONT["body_sm"],
                                    color=COLORS["text_secondary"],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"{color_name} · {color_hex}",
                                    size=FONT["caption"],
                                    color=COLORS["text_tertiary"]),
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

    if clothes:
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"{len(clothes)}",
                                            size=FONT["display"],
                                            weight=ft.FontWeight.BOLD,
                                            color=COLORS["primary"]),
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
                *[cloth_card(c) for c in reversed(clothes)],
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
                        ft.Text("내 옷장",
                                size=FONT["title"],
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["text_primary"]),
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
