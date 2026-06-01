import flet as ft
import os
from model.clothing import Clothing
from logic.color_logic import rgb_to_hex, rgb_to_name
from views.theme import COLORS, RADIUS, SPACE, FONT
from views.components import top_bar, card, primary_button, section_title


DETAIL_OPTIONS = {
    "상의": ["반팔", "긴팔", "셔츠", "니트", "맨투맨", "후드티", "블라우스", "민소매", "기모 맨투맨"],
    "하의": ["청바지", "슬랙스", "반바지", "조거팬츠", "면바지", "치마", "두꺼운 바지", "얇은 바지"],
    "아우터": ["패딩", "후리스", "코트", "두꺼운 코트", "가디건", "자켓", "점퍼", "집업", "얇은 자켓"],
}


def build_register_options_view(page, go, clothes_store):
    """옷 등록 방법 선택 화면."""

    file_picker = ft.FilePicker(
        on_result=lambda e: handle_file_pick(e, page, go, clothes_store)
    )
    page.overlay.append(file_picker)

    def pick_photo(_):
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "gif", "bmp"],
        )

    def option_card(title, desc, icon, color, on_click):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color="white", size=28),
                        width=56,
                        height=56,
                        bgcolor=color,
                        border_radius=RADIUS["md"],
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=FONT["title_sm"],
                                weight=ft.FontWeight.W_700,
                                color=COLORS["text_primary"],
                            ),
                            ft.Text(
                                desc,
                                size=FONT["body_sm"],
                                color=COLORS["text_secondary"],
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT_ROUNDED,
                        color=COLORS["text_tertiary"],
                    ),
                ],
                spacing=SPACE["md"],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=SPACE["lg"],
            bgcolor=COLORS["card_bg"],
            border_radius=RADIUS["lg"],
            on_click=on_click,
            ink=True,
            shadow=ft.BoxShadow(
                blur_radius=14,
                color=COLORS["shadow_light"],
                offset=ft.Offset(0, 3),
            ),
        )

    return ft.Column(
        [
            top_bar("옷 등록하기", lambda: go("/")),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(height=SPACE["md"]),
                        ft.Text(
                            "어떻게 등록할까요?",
                            size=FONT["title"],
                            weight=ft.FontWeight.W_700,
                            color=COLORS["text_primary"],
                        ),
                        ft.Text(
                            "방법을 선택해주세요",
                            size=FONT["body_sm"],
                            color=COLORS["text_secondary"],
                        ),
                        ft.Container(height=SPACE["lg"]),
                        option_card(
                            "사진으로 등록",
                            "갤러리에서 옷 사진 선택",
                            ft.Icons.PHOTO_CAMERA_ROUNDED,
                            COLORS["pink"],
                            pick_photo,
                        ),
                        option_card(
                            "직접 입력",
                            "종류, 색상 등 정보 입력",
                            ft.Icons.EDIT_NOTE_ROUNDED,
                            COLORS["primary"],
                            lambda e: go("/register_direct"),
                        ),
                    ],
                    spacing=SPACE["md"],
                ),
                padding=SPACE["lg"],
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )


def handle_file_pick(e, page, go, clothes_store):
    """사진 선택 후 처리."""
    if e.files:
        file_path = e.files[0].path
        file_name = os.path.basename(file_path)
        item = Clothing(
            category="사진등록",
            detail=file_name,
            feature="사진에서 불러온 옷",
            rgb=(0, 0, 0),
            hex_code="#cccccc",
            color_name="미분석",
            image_path=file_path,
        )
        clothes_store.append(item)
        page.open(
            ft.SnackBar(
                content=ft.Text(f"{file_name} 등록되었습니다"),
                bgcolor=COLORS["green"],
            )
        )
        go("/")


def build_register_direct_view(page, go, clothes_store):
    """직접 입력 등록 화면."""

    selected = {"r": 90, "g": 130, "b": 255}

    color_preview = ft.Container(
        width=70, height=70,
        bgcolor=rgb_to_hex(**selected),
        border_radius=RADIUS["md"],
        border=ft.border.all(1, COLORS["border"]),
    )
    color_name_label = ft.Text(
        rgb_to_name(**selected),
        size=FONT["title_sm"],
        weight=ft.FontWeight.W_700,
        color=COLORS["text_primary"],
    )
    color_hex_label = ft.Text(
        rgb_to_hex(**selected),
        size=FONT["body_sm"],
        color=COLORS["text_tertiary"],
    )

    def update_color():
        hex_code = rgb_to_hex(**selected)
        name = rgb_to_name(**selected)
        color_preview.bgcolor = hex_code
        color_name_label.value = name
        color_hex_label.value = hex_code
        page.update()

    def channel_slider(channel, accent):
        value_text = ft.Text(
            str(selected[channel]),
            size=FONT["body_sm"],
            color=COLORS["text_secondary"],
            weight=ft.FontWeight.W_600,
            width=32,
            text_align=ft.TextAlign.RIGHT,
        )
        def on_change(e):
            selected[channel] = int(e.control.value)
            value_text.value = str(selected[channel])
            update_color()
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(channel.upper(), color="white",
                                    weight=ft.FontWeight.BOLD, size=FONT["caption"]),
                    width=28, height=28,
                    bgcolor=accent, border_radius=RADIUS["sm"],
                    alignment=ft.alignment.center,
                ),
                ft.Slider(
                    min=0, max=255, value=selected[channel],
                    divisions=255, expand=True,
                    active_color=accent, on_change=on_change,
                ),
                value_text,
            ],
            spacing=SPACE["sm"],
        )

    category_dd = ft.Dropdown(
        label="종류", value="상의",
        options=[ft.dropdown.Option(c) for c in DETAIL_OPTIONS.keys()],
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        text_size=FONT["body"],
    )
    detail_dd = ft.Dropdown(
        label="세부 종류", value=DETAIL_OPTIONS["상의"][0],
        options=[ft.dropdown.Option(d) for d in DETAIL_OPTIONS["상의"]],
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        text_size=FONT["body"],
    )
    feature_tf = ft.TextField(
        label="특징", hint_text="예: 오버핏, 얇음, 캐주얼",
        border_radius=RADIUS["md"], filled=True,
        bgcolor=COLORS["card_bg"], border_color=COLORS["border"],
        text_size=FONT["body"],
    )

    def on_category_change(e):
        opts = DETAIL_OPTIONS[category_dd.value]
        detail_dd.options = [ft.dropdown.Option(d) for d in opts]
        detail_dd.value = opts[0]
        page.update()
    category_dd.on_change = on_category_change

    def on_save(_):
        feature = (feature_tf.value or "").strip() or "특징 없음"
        r, g, b = selected["r"], selected["g"], selected["b"]
        item = Clothing(
            category=category_dd.value,
            detail=detail_dd.value,
            feature=feature,
            rgb=(r, g, b),
            hex_code=rgb_to_hex(r, g, b),
            color_name=rgb_to_name(r, g, b),
        )
        clothes_store.append(item)
        page.open(
            ft.SnackBar(
                content=ft.Text(f"{item.category} · {item.detail} 저장됨"),
                bgcolor=COLORS["green"],
            )
        )
        go("/")

    return ft.Column(
        [
            top_bar("직접 등록하기", lambda: go("/register")),
            ft.Container(
                content=ft.Column(
                    [
                        card(
                            ft.Column(
                                [
                                    section_title("기본 정보"),
                                    ft.Container(height=4),
                                    category_dd,
                                    detail_dd,
                                    feature_tf,
                                ],
                                spacing=SPACE["sm"],
                            )
                        ),
                        card(
                            ft.Column(
                                [
                                    section_title("색상 선택"),
                                    ft.Container(height=4),
                                    ft.Row(
                                        [
                                            color_preview,
                                            ft.Column(
                                                [
                                                    ft.Text("선택한 색",
                                                            size=FONT["caption"],
                                                            color=COLORS["text_tertiary"]),
                                                    color_name_label,
                                                    color_hex_label,
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=SPACE["md"],
                                    ),
                                    ft.Container(height=4),
                                    channel_slider("r", "#ef4444"),
                                    channel_slider("g", "#22c55e"),
                                    channel_slider("b", "#3b82f6"),
                                ],
                                spacing=SPACE["md"],
                            )
                        ),
                        ft.Container(
                            content=primary_button("저장하기", on_save, ft.Icons.CHECK_ROUNDED),
                            padding=ft.padding.only(top=SPACE["sm"]),
                        ),
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
