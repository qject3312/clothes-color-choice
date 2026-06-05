"""
옷 추천 앱 - Flet 메인 진입점.
- 백엔드(FastAPI) 자동 실행
- 로그인/회원가입 흐름
- Windows/macOS 호환성 처리
"""
import sys
import platform
import flet as ft

# 백엔드 자동 시작
try:
    from backend_runner import start_backend_if_needed
    start_backend_if_needed()
except Exception as e:
    print(f"[WARN] 백엔드 자동 시작 실패: {e}")
    print("[INFO] 게스트 모드로 계속 진행할 수 있습니다.")

from views.theme import COLORS
from views.auth_view import build_login_view, build_signup_view
from views.home_view import build_home_view
from views.register_view import build_register_options_view, build_register_direct_view
from views.list_view import build_list_view
from views.coordinate_view import build_coordinate_view
from views.custom_view import build_custom_view
from views.temperature_view import build_temperature_view
from views.today_view import build_today_view
from views.profile_view import build_profile_view


# OS 정보
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def get_font_family():
    if IS_WINDOWS:
        return "Malgun Gothic, Segoe UI, sans-serif"
    elif IS_MAC:
        return "Apple SD Gothic Neo, -apple-system, sans-serif"
    else:
        return "Noto Sans CJK KR, sans-serif"


def main(page: ft.Page):
    # ===== 페이지 설정 =====
    page.title = "옷 추천 앱"
    page.window.width = 430
    page.window.height = 780
    page.window.min_width = 380
    page.window.min_height = 700
    page.window.resizable = False
    if IS_MAC:
        page.window.center()

    page.bgcolor = COLORS["bg"]
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=COLORS["primary"],
        use_material3=True,
        font_family=get_font_family(),
    )

    # ===== 전역 상태 =====
    state = {
        "current_user": None,  # 로그인 안 됨
    }

    def set_user(user_data):
        state["current_user"] = user_data

    def logout():
        state["current_user"] = None
        go("/login")

    # ===== 화면 컨테이너 =====
    container = ft.Container(expand=True)

    def go(route: str):
        user = state["current_user"]

        # 로그인 안 했으면 로그인/회원가입만 허용
        if user is None:
            if route == "/signup":
                container.content = build_signup_view(page, go)
            else:
                container.content = build_login_view(page, go, set_user)
        else:
            # 로그인 후 라우팅
            if route == "/" or route == "/home":
                container.content = build_home_view(page, go, user, logout)
            elif route == "/register":
                container.content = build_register_options_view(page, go, user)
            elif route == "/register_direct":
                container.content = build_register_direct_view(page, go, user)
            elif route == "/list":
                container.content = build_list_view(page, go, user)
            elif route == "/coordinate":
                container.content = build_coordinate_view(page, go, user)
            elif route == "/custom":
                container.content = build_custom_view(page, go, user)
            elif route == "/temperature":
                container.content = build_temperature_view(page, go, user)
            elif route == "/today":
                container.content = build_today_view(page, go, user)
            elif route == "/profile":
                container.content = build_profile_view(page, go, user, logout)
            else:
                container.content = build_home_view(page, go, user, logout)
        page.update()

    page.add(container)
    go("/")


if __name__ == "__main__":
    if IS_WINDOWS:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ft.app(target=main)
