"""공통 UI 컴포넌트."""
import flet as ft
from views.theme import C, R, S, F


def card(content, padding=S["lg"], bgcolor=None, shadow=True):
    return ft.Container(
        content=content,
        bgcolor=bgcolor or C["card"],
        padding=padding,
        border_radius=R["lg"],
        border=ft.border.all(1, C["border"]),
        shadow=ft.BoxShadow(blur_radius=16, color=C["shadow"], offset=ft.Offset(0, 4)) if shadow else None,
    )


def top_bar(page, title, on_back=None, on_menu=None, on_profile=None):
    left = ft.IconButton(
        ft.Icons.MENU_ROUNDED if on_menu else ft.Icons.ARROW_BACK_ROUNDED,
        icon_color=C["text"], icon_size=22,
        on_click=lambda e: (on_menu() if on_menu else on_back()),
    ) if (on_menu or on_back) else ft.Container(width=40)

    right = ft.IconButton(
        content=ft.Container(
            content=ft.Icon(ft.Icons.PERSON_ROUNDED, color=C["subtext"], size=20),
            width=38, height=38,
            bgcolor=C["muted"],
            border_radius=19,
            alignment=ft.alignment.center,
        ),
        on_click=lambda e: on_profile(),
    ) if on_profile else ft.Container(width=40)

    return ft.Container(
        content=ft.Row(
            [left,
             ft.Text(title, size=F["lg"], weight=ft.FontWeight.BOLD, color=C["text"]),
             right],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=C["card"],
        padding=ft.padding.symmetric(horizontal=S["sm"], vertical=S["sm"]),
    )


def btn_primary(text, on_click, icon=None, color=None, expand=True):
    color = color or C["primary"]
    row = []
    if icon:
        row.append(ft.Icon(icon, color="white", size=18))
    row.append(ft.Text(text, color="white", weight=ft.FontWeight.BOLD, size=F["md"]))
    b = ft.ElevatedButton(
        content=ft.Row(row, alignment=ft.MainAxisAlignment.CENTER, spacing=6, tight=True),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=color,
            shape=ft.RoundedRectangleBorder(radius=R["md"]),
            padding=ft.padding.symmetric(vertical=15),
            elevation=2,
        ),
    )
    if expand:
        b.width = 9999
    return b


def btn_secondary(text, on_click):
    return ft.ElevatedButton(
        content=ft.Text(text, color=C["subtext"], weight=ft.FontWeight.W_600, size=F["body"]),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=C["muted"],
            shape=ft.RoundedRectangleBorder(radius=R["md"]),
            padding=ft.padding.symmetric(vertical=13),
            elevation=0,
        ),
        width=9999,
    )


def field(label="", hint="", value="", password=False, icon=None, multiline=False):
    return ft.TextField(
        label=label, hint_text=hint, value=value,
        password=password, can_reveal_password=password,
        multiline=multiline,
        border_radius=R["md"], filled=True,
        bgcolor=C["card"], border_color=C["border"],
        focused_border_color=C["primary"],
        text_size=F["body"],
        prefix_icon=icon,
    )


def dropdown(label, value, options):
    return ft.Dropdown(
        label=label, value=value,
        options=[ft.dropdown.Option(o) for o in options],
        border_radius=R["md"], filled=True,
        bgcolor=C["card"], border_color=C["border"],
        focused_border_color=C["primary"],
        text_size=F["body"],
    )


def section(text, color=None):
    return ft.Text(text, size=F["md"], weight=ft.FontWeight.W_700, color=color or C["text"])


def badge(text, bg=None, fg=None):
    return ft.Container(
        content=ft.Text(text, size=F["xs"], weight=ft.FontWeight.W_700, color=fg or C["primary"]),
        bgcolor=bg or C["primary_soft"],
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=R["full"],
    )


def empty_state(icon, title, subtitle, btn_text=None, on_btn=None, color=None):
    color = color or C["primary"]
    kids = [
        ft.Container(
            content=ft.Icon(icon, size=52, color=C["hint"]),
            width=110, height=110,
            bgcolor=C["muted"], border_radius=55,
            alignment=ft.alignment.center,
        ),
        ft.Container(height=S["md"]),
        ft.Text(title, size=F["md"], weight=ft.FontWeight.W_700, color=C["text"]),
        ft.Text(subtitle, size=F["sm"], color=C["subtext"], text_align=ft.TextAlign.CENTER),
    ]
    if btn_text and on_btn:
        kids += [ft.Container(height=S["lg"]), btn_primary(btn_text, on_btn, ft.Icons.ADD_ROUNDED, color)]
    return ft.Container(
        content=ft.Column(kids, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          alignment=ft.MainAxisAlignment.CENTER, spacing=4),
        alignment=ft.alignment.center, expand=True,
    )


def cloth_color_dot(hex_code, size=22):
    """색상 미리보기 원."""
    return ft.Container(
        width=size, height=size,
        bgcolor=hex_code,
        border_radius=size // 2,
        border=ft.border.all(1, C["border"]),
    )


def resolve_image(image_path: str) -> str:
    """이미지 경로를 절대경로로 변환. 항상 이 함수를 통해서 경로를 사용."""
    if not image_path:
        return ""
    try:
        from app_paths import resolve_existing_path
        import os
        resolved = resolve_existing_path(image_path)
        return resolved if (resolved and os.path.exists(resolved)) else ""
    except Exception:
        return ""


def cloth_image(image_path: str, size=72, radius=10):
    """옷 이미지 위젯. 경로 없으면 색상 박스 대신 아이콘."""
    resolved = resolve_image(image_path)
    if resolved:
        return ft.Container(
            content=ft.Image(
                src=resolved,
                width=size, height=size,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(radius),
            ),
            width=size, height=size,
            border_radius=radius,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
    return ft.Container(
        width=size, height=size,
        bgcolor=C["muted"],
        border_radius=radius,
        border=ft.border.all(1, C["border"]),
        content=ft.Icon(ft.Icons.CHECKROOM_ROUNDED, color=C["hint"], size=size * 0.5),
        alignment=ft.alignment.center,
    )
