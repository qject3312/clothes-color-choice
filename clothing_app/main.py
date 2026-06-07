"""
핏픽 - Flet 메인 진입점
- 백엔드(FastAPI) 자동 실행
- 전역 상태 관리 (user, clothes, saved_outfits)
- 라우터 (go 함수)
- 햄버거 메뉴
- Windows / macOS 호환
"""
import sys
import platform
import flet as ft

# ─── 백엔드 자동 시작 ───
try:
    from backend_runner import start_backend_if_needed
    start_backend_if_needed()
except Exception as e:
    print(f"[WARN] 백엔드 자동 시작 실패: {e}")

# ─── API 클라이언트 ───
try:
    from api_client import (
        get_clothes_from_backend,
        get_saved_outfits_backend,
        save_outfit_backend,
    )
except Exception:
    def get_clothes_from_backend(uid="guest"): return []
    def get_saved_outfits_backend(uid="guest"): return []
    def save_outfit_backend(o, uid="guest"): return {}

from model.clothing import Clothing
from app_paths import resolve_existing_path

# ─── 뷰 임포트 ───
from views.auth_view        import build_login, build_signup
from views.home_view        import build_home
from views.register_view    import build_register_options, build_register_photo, build_register_direct
from views.clothes_view     import build_clothes, build_clothes_edit
from views.recommend_view   import (build_recommend, build_coordination,
                                    build_temperature, build_today,
                                    build_personal_recommend, build_outfit)
from views.profile_view     import build_profile, build_edit_profile
from views.theme            import C

IS_WINDOWS = platform.system() == "Windows"
IS_MAC     = platform.system() == "Darwin"


def get_font():
    if IS_MAC:     return "Apple SD Gothic Neo"
    if IS_WINDOWS: return "Malgun Gothic"
    return "Noto Sans CJK KR"


def main(page: ft.Page):
    # ─── 페이지 설정 ───
    page.title = "핏픽 - 맞춤 옷 추천"
    page.bgcolor = C["bg"]
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=C["primary"],
        use_material3=True,
        font_family=get_font(),
    )
    page.window.width     = 430
    page.window.height    = 780
    page.window.min_width = 380
    page.window.min_height= 700
    page.window.resizable = True
    if IS_MAC:
        page.window.center()

    # ─── 전역 상태 ───
    # 단일 dict로 관리 - 모든 뷰에서 참조
    app_state = {
        "user":          None,   # 로그인된 사용자 dict
        "current_user":  None,   # user와 동일 (하위 호환)
        "clothes":       [],     # Clothing 객체 리스트
        "saved_outfits": [],     # 저장 코디 리스트
    }

    def get_uid():
        u = app_state["user"]
        return u.get("user_id", "guest") if u else "guest"

    def set_user(u):
        app_state["user"]         = u
        app_state["current_user"] = u

    def load_clothes():
        """백엔드에서 옷 목록 로드 - image_path는 반드시 resolve_existing_path 적용."""
        app_state["clothes"] = []
        try:
            raw = get_clothes_from_backend(get_uid())
            if not isinstance(raw, list):
                return
            for c in raw:
                # image_path 경로 정규화 (핵심!)
                raw_path = c.get("image_path", "")
                resolved = resolve_existing_path(raw_path) if raw_path else ""
                app_state["clothes"].append(
                    Clothing(
                        category   = c.get("category", ""),
                        detail     = c.get("detail", ""),
                        feature    = c.get("feature", ""),
                        rgb        = (0, 0, 0),
                        hex_code   = c.get("color_hex") or c.get("hex", "#cccccc"),
                        color_name = c.get("color_name", "미분석"),
                        image_path = resolved,
                        clothing_id= c.get("id"),
                        colors     = c.get("colors", []),
                    )
                )
        except Exception as e:
            print("[WARN] 옷 로드 실패:", e)

    def load_outfits():
        try:
            raw = get_saved_outfits_backend(get_uid())
            if isinstance(raw, list):
                app_state["saved_outfits"] = raw
        except Exception as e:
            print("[WARN] 코디 로드 실패:", e)

    def logout():
        set_user(None)
        app_state["clothes"]       = []
        app_state["saved_outfits"] = []
        go("/login")

    # ─── 햄버거 메뉴 ───
    def open_menu():
        R_MD_LOCAL = 12
        btn_style = ft.ButtonStyle(
            bgcolor=C["card"], color=C["text"],
            shape=ft.RoundedRectangleBorder(radius=R_MD_LOCAL),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            overlay_color=C["primary_soft"],
        )

        def nav(route):
            def _fn(e):
                page.close(dlg)
                go(route)
            return _fn

        def do_logout(e):
            page.close(dlg)
            logout()

        def do_home(e):
            page.close(dlg)
            go("/")

        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text("메뉴", weight=ft.FontWeight.BOLD,
                          size=18, color=C["text"]),
            content=ft.Column([
                ft.ElevatedButton("갖고있는 옷 확인",  width=240, on_click=nav("/clothes"),     style=btn_style),
                ft.ElevatedButton("사용자 맞춤 코디",  width=240, on_click=nav("/personal"),    style=btn_style),
                ft.ElevatedButton("코디해보기",        width=240, on_click=nav("/coordination"), style=btn_style),
                ft.ElevatedButton("나의 코디 확인",    width=240, on_click=nav("/outfit"),       style=btn_style),
                ft.ElevatedButton("오늘의 추천 코디",  width=240, on_click=nav("/today"),        style=btn_style),
                ft.ElevatedButton("홈으로",            width=240, on_click=do_home,              style=btn_style),
                ft.Divider(height=1, color=C["border"]),
                ft.ElevatedButton(
                    "로그아웃", width=240, on_click=do_logout,
                    style=ft.ButtonStyle(
                        bgcolor=C["danger_soft"], color=C["danger"],
                        shape=ft.RoundedRectangleBorder(radius=R_MD_LOCAL),
                        padding=ft.padding.symmetric(vertical=14, horizontal=10),
                    ),
                ),
            ], tight=True, spacing=6),
        )
        page.open(dlg)

    R_MD = 12  # 메뉴 버튼 모서리

    # ─── 화면 컨테이너 ───
    container = ft.Container(expand=True)

    def go(route: str):
        u = app_state["user"]

        # 비로그인 → 로그인/회원가입만
        if u is None:
            if route == "/signup":
                container.content = build_signup(page, go, set_user, lambda: (load_clothes(), load_outfits()))
            else:
                container.content = build_login(page, go, set_user, lambda: (load_clothes(), load_outfits()))
            page.update()
            return

        # 라우팅
        if route in ("/", "/home"):
            container.content = build_home(page, go, u, app_state["clothes"], open_menu)

        elif route == "/register":
            container.content = build_register_options(page, go)

        elif route == "/register_photo":
            container.content = build_register_photo(page, go, app_state)

        elif route == "/register_direct":
            container.content = build_register_direct(page, go, app_state)

        elif route == "/clothes":
            # 옷장 진입 시 최신 목록 다시 로드
            load_clothes()
            container.content = build_clothes(page, go, app_state)

        elif route == "/clothes_edit":
            container.content = build_clothes_edit(page, go, app_state)

        elif route == "/recommend":
            container.content = build_recommend(page, go, app_state)

        elif route == "/coordination":
            container.content = build_coordination(page, go, app_state)

        elif route == "/temperature":
            container.content = build_temperature(page, go, app_state)

        elif route == "/today":
            container.content = build_today(page, go, app_state)

        elif route == "/personal":
            container.content = build_personal_recommend(page, go, app_state)
        elif route == "/outfit":
            load_outfits()
            container.content = build_outfit(page, go, app_state)

        elif route == "/profile":
            container.content = build_profile(page, go, app_state, logout)

        elif route == "/edit_profile":
            container.content = build_edit_profile(page, go, app_state)

        else:
            container.content = build_home(page, go, u, app_state["clothes"], open_menu)

        page.update()

    page.add(container)
    go("/login")


if __name__ == "__main__":
    if IS_WINDOWS:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ft.app(target=main)
