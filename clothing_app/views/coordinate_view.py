"""코디해보기 - 상의/하의 선택해서 백엔드에 평가 요청."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, primary_button, empty_state, section_title

try:
    from api_client import get_clothes_from_backend, evaluate_outfit_backend
except Exception:
    def get_clothes_from_backend(user_id="guest"):
        return []
    def evaluate_outfit_backend(data):
        return {"error": "backend not available"}


def _get(item, *keys, default=""):
    """dict에서 여러 키 중 첫 번째 매칭 값 반환."""
    if not isinstance(item, dict):
        return default
    for k in keys:
        if k in item and item[k] is not None:
            return item[k]
    return default


def build_coordinate_view(page, go, current_user):
    user_id = current_user.get("user_id", "guest")

    try:
        clothes = get_clothes_from_backend(user_id)
        if not isinstance(clothes, list):
            clothes = []
    except Exception:
        clothes = []

    tops = [c for c in clothes if _get(c, "category") == "상의"]
    bottoms = [c for c in clothes if _get(c, "category") == "하의"]

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
                        bgcolor=_get(item, "color_hex", "hex", default="#cccccc"),
                        border_radius=RADIUS["sm"],
                        border=ft.border.all(1, COLORS["border"]),
                    ),
                    ft.Text(_get(item, "detail"),
                            size=FONT["body_sm"],
                            color="white" if is_selected else COLORS["text_primary"],
                            weight=ft.FontWeight.W_600),
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
            [cloth_chip(item, selected[key] is item,
                        lambda e, it=item: select(key, it))
             for item in items],
            wrap=True, spacing=8, run_spacing=8,
        )

    top_chips_container = ft.Container(content=render_chips(tops, "top"))
    bottom_chips_container = ft.Container(content=render_chips(bottoms, "bottom"))

    def get_hex(item):
        return _get(item, "color_hex", "hex", default="#cccccc")

    top_preview = ft.Container(
        width=80, height=80,
        bgcolor=get_hex(selected["top"]),
        border_radius=RADIUS["md"],
        border=ft.border.all(1, COLORS["border"]),
    )
    bottom_preview = ft.Container(
        width=80, height=80,
        bgcolor=get_hex(selected["bottom"]),
        border_radius=RADIUS["md"],
        border=ft.border.all(1, COLORS["border"]),
    )
    top_label = ft.Text(
        f"{_get(selected['top'], 'detail')} · {_get(selected['top'], 'color_name')}",
        size=FONT["body_sm"], color=COLORS["text_secondary"],
    )
    bottom_label = ft.Text(
        f"{_get(selected['bottom'], 'detail')} · {_get(selected['bottom'], 'color_name')}",
        size=FONT["body_sm"], color=COLORS["text_secondary"],
    )

    def update_preview():
        top_preview.bgcolor = get_hex(selected["top"])
        bottom_preview.bgcolor = get_hex(selected["bottom"])
        top_label.value = f"{_get(selected['top'], 'detail')} · {_get(selected['top'], 'color_name')}"
        bottom_label.value = f"{_get(selected['bottom'], 'detail')} · {_get(selected['bottom'], 'color_name')}"

    def select(key, item):
        selected[key] = item
        top_chips_container.content = render_chips(tops, "top")
        bottom_chips_container.content = render_chips(bottoms, "bottom")
        update_preview()
        page.update()

    def evaluate(_):
        # 백엔드에 평가 요청
        req_data = {
            "user_id": user_id,
            "top_color": _get(selected["top"], "color_name"),
            "bottom_color": _get(selected["bottom"], "color_name"),
        }
        result = evaluate_outfit_backend(req_data)

        # 응답 처리
        if isinstance(result, dict) and "error" not in result:
            is_good = result.get("is_good", True)
            reason = result.get("reason", result.get("message", "결과 처리 중..."))
        else:
            # 백엔드 실패 시 간단한 로컬 로직
            is_good = True
            reason = "백엔드 연결 실패로 간단한 평가만 표시됩니다."

        result_color = COLORS["green"] if is_good else COLORS["pink"]
        result_icon = ft.Icons.CHECK_CIRCLE_ROUNDED if is_good else ft.Icons.INFO_ROUNDED
        result_text = "좋은 조합이에요!" if is_good else "고민해볼 조합이에요"

        result_container.content = card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(result_icon, color=result_color, size=22),
                            ft.Text(result_text,
                                    size=FONT["title_sm"],
                                    weight=ft.FontWeight.W_700,
                                    color=result_color),
                        ],
                        spacing=6, tight=True,
                    ),
                    ft.Container(height=4),
                    ft.Text(reason, size=FONT["body_sm"], color=COLORS["text_secondary"]),
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
                        card(
                            ft.Column(
                                [
                                    section_title("선택한 코디"),
                                    ft.Container(height=4),
                                    ft.Row(
                                        [
                                            ft.Column([top_preview,
                                                       ft.Text("상의",
                                                               size=FONT["caption"],
                                                               color=COLORS["text_tertiary"])],
                                                      spacing=4,
                                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                            ft.Container(width=12),
                                            ft.Column([bottom_preview,
                                                       ft.Text("하의",
                                                               size=FONT["caption"],
                                                               color=COLORS["text_tertiary"])],
                                                      spacing=4,
                                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                            ft.Container(width=12),
                                            ft.Column([top_label, bottom_label],
                                                      spacing=4, expand=True),
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        card(ft.Column([section_title("상의"), top_chips_container],
                                       spacing=SPACE["sm"])),
                        card(ft.Column([section_title("하의"), bottom_chips_container],
                                       spacing=SPACE["sm"])),
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
