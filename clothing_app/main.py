import flet as ft

from views.theme import COLORS
from views.home_view import build_home_view
from views.register_view import build_register_options_view, build_register_direct_view
from views.list_view import build_list_view
from views.coordinate_view import build_coordinate_view
from views.custom_view import build_custom_view
from views.temperature_view import build_temperature_view
from views.my_outfits_view import build_my_outfits_view
from views.profile_view import build_profile_view


def main(page: ft.Page):
    page.title = "옷 추천 앱"
    page.window.width = 430
    page.window.height = 780
    page.window.resizable = False
    page.bgcolor = COLORS["bg"]
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=COLORS["primary"],
        use_material3=True,
    )

    # 전역 상태
    clothes_store = []
    outfits_store = []

    # 화면 컨테이너
    container = ft.Container(expand=True)

    def go(route: str):
        if route == "/":
            container.content = build_home_view(page, go, clothes_store)
        elif route == "/register":
            container.content = build_register_options_view(page, go, clothes_store)
        elif route == "/register_direct":
            container.content = build_register_direct_view(page, go, clothes_store)
        elif route == "/list":
            container.content = build_list_view(page, go, clothes_store)
        elif route == "/coordinate":
            container.content = build_coordinate_view(page, go, clothes_store)
        elif route == "/custom":
            container.content = build_custom_view(page, go, clothes_store)
        elif route == "/temperature":
            container.content = build_temperature_view(page, go, clothes_store)
        elif route == "/my_outfits":
            container.content = build_my_outfits_view(page, go, clothes_store, outfits_store)
        elif route == "/profile":
            container.content = build_profile_view(page, go, clothes_store)
        else:
            container.content = build_home_view(page, go, clothes_store)
        page.update()

    page.add(container)
    go("/")


if __name__ == "__main__":
    ft.app(target=main)
