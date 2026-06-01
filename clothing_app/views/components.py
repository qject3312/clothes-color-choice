"""모든 화면에서 공통으로 쓰는 UI 컴포넌트."""
import flet as ft
from views.theme import COLORS, RADIUS, SPACE, FONT


def top_bar(title, on_back, right_action=None):
    """상단바. 뒤로가기 + 제목 + 우측 액션."""
    right = right_action if right_action else ft.Container(width=40)
    return ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    ft.Icons.ARROW_BACK_ROUNDED,
                    icon_color=COLORS["text_primary"],
                    on_click=lambda e: on_back(),
                ),
                ft.Text(
                    title,
                    size=FONT["title"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_primary"],
                ),
                right,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=SPACE["md"], vertical=SPACE["sm"]),
        bgcolor=COLORS["card_bg"],
    )


def card(child, padding_=None):
    """하얀 카드. 그림자 + 둥근 모서리."""
    if padding_ is None:
        padding_ = SPACE["lg"]
    return ft.Container(
        content=child,
        bgcolor=COLORS["card_bg"],
        padding=padding_,
        border_radius=RADIUS["lg"],
        shadow=ft.BoxShadow(
            blur_radius=14,
            color=COLORS["shadow_light"],
            offset=ft.Offset(0, 3),
        ),
    )


def primary_button(text, on_click, icon=None, color=None):
    """주요 액션 버튼."""
    if color is None:
        color = COLORS["primary"]

    children = []
    if icon:
        children.append(ft.Icon(icon, color="white", size=18))
    children.append(
        ft.Text(text, size=FONT["title_sm"], weight=ft.FontWeight.BOLD, color="white")
    )

    return ft.ElevatedButton(
        content=ft.Row(
            children,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=color,
            shape=ft.RoundedRectangleBorder(radius=RADIUS["md"]),
            padding=ft.padding.symmetric(vertical=16),
            elevation=2,
        ),
        width=10000,
    )


def empty_state(icon, title, subtitle, action_text=None, on_action=None, color=None):
    """빈 상태 화면. 아이콘 + 제목 + 부제목 + 액션."""
    if color is None:
        color = COLORS["primary"]
    children = [
        ft.Container(
            content=ft.Icon(icon, size=56, color=COLORS["text_tertiary"]),
            width=120,
            height=120,
            bgcolor=COLORS["bg"],
            border_radius=60,
            alignment=ft.alignment.center,
        ),
        ft.Container(height=SPACE["md"]),
        ft.Text(
            title,
            size=FONT["title_sm"],
            weight=ft.FontWeight.W_700,
            color=COLORS["text_primary"],
        ),
        ft.Text(
            subtitle,
            size=FONT["body_sm"],
            color=COLORS["text_secondary"],
            text_align=ft.TextAlign.CENTER,
        ),
    ]
    if action_text and on_action:
        children.append(ft.Container(height=SPACE["lg"]))
        children.append(
            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ADD_ROUNDED, color="white", size=18),
                        ft.Text(action_text, color="white", weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                    tight=True,
                ),
                on_click=on_action,
                style=ft.ButtonStyle(
                    bgcolor=color,
                    shape=ft.RoundedRectangleBorder(radius=RADIUS["md"]),
                    padding=ft.padding.symmetric(horizontal=24, vertical=14),
                ),
            )
        )

    return ft.Container(
        content=ft.Column(
            children,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def color_chip(color_hex, color_name, size=40):
    """색상 + 이름 표시."""
    return ft.Row(
        [
            ft.Container(
                width=size,
                height=size,
                bgcolor=color_hex,
                border_radius=RADIUS["md"],
                border=ft.border.all(1, COLORS["border"]),
            ),
            ft.Text(
                color_name,
                size=FONT["body_sm"],
                color=COLORS["text_secondary"],
                weight=ft.FontWeight.W_500,
            ),
        ],
        spacing=8,
        tight=True,
    )


def section_title(text):
    """섹션 제목."""
    return ft.Text(
        text,
        size=FONT["title_sm"],
        weight=ft.FontWeight.W_700,
        color=COLORS["text_primary"],
    )
