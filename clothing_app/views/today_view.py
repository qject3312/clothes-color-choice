"""오늘의 코디 (즐겨찾기 / 히스토리)."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, empty_state, section_title

try:
    from api_client import get_history_from_backend
except Exception:
    def get_history_from_backend(user_id="guest"):
        return []


def build_today_view(page, go, current_user):
    user_id = current_user.get("user_id", "guest")

    try:
        history = get_history_from_backend(user_id)
        if not isinstance(history, list):
            history = []
    except Exception:
        history = []

    if not history:
        return ft.Column(
            [
                top_bar("오늘의 코디", lambda: go("/")),
                empty_state(
                    ft.Icons.STYLE_OUTLINED,
                    "코디 히스토리가 없어요",
                    "코디해보기에서 다양한 조합을 시도해보세요",
                    "코디해보기",
                    lambda e: go("/coordinate"),
                    color=COLORS["gray"],
                ),
            ],
            spacing=0,
            expand=True,
        )

    def history_card(item):
        top_color = item.get("top_color", "#cccccc") if isinstance(item, dict) else "#cccccc"
        bottom_color = item.get("bottom_color", "#cccccc") if isinstance(item, dict) else "#cccccc"
        message = item.get("message", item.get("reason", "")) if isinstance(item, dict) else ""

        return card(ft.Column([
            ft.Row([
                ft.Container(width=50, height=50, bgcolor=top_color,
                             border_radius=RADIUS["md"],
                             border=ft.border.all(1, COLORS["border"])),
                ft.Container(width=50, height=50, bgcolor=bottom_color,
                             border_radius=RADIUS["md"],
                             border=ft.border.all(1, COLORS["border"])),
            ], spacing=SPACE["sm"]),
            ft.Container(height=4),
            ft.Text(message, size=FONT["body_sm"], color=COLORS["text_secondary"]),
        ], spacing=SPACE["sm"]))

    return ft.Column(
        [
            top_bar("오늘의 코디", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [history_card(h) for h in history[:10]],
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
