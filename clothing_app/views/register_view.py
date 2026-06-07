"""옷 등록 화면 - 버그 수정 버전.
수정사항:
1. Row 안의 btn_primary expand 충돌 → 직접 ElevatedButton으로 교체
2. state.get("user_id") → state["user"]["user_id"] 경로 수정
3. 사진 저장 경로 uid 처리 수정
"""
import os
import shutil
import time
import flet as ft
from pathlib import Path
from views.theme import C, R, S, F, DETAIL_OPTIONS
from views.components import (card, top_bar, section, field, dropdown, resolve_image)

try:
    from api_client import add_clothing_to_backend
except Exception:
    def add_clothing_to_backend(item, uid="guest"): return {"error": "off"}

try:
    from logic.color_logic import rgb_to_hex, rgb_to_name
except Exception:
    def rgb_to_hex(r, g, b): return f"#{r:02x}{g:02x}{b:02x}"
    def rgb_to_name(r, g, b): return "기타"

try:
    from logic.recommend_logic import extract_dominant_colors
except Exception:
    def extract_dominant_colors(path, color_count=3): return []

try:
    from app_paths import IMAGE_DIR, resolve_existing_path
except Exception:
    IMAGE_DIR = Path("app_data/images")
    def resolve_existing_path(p): return str(p)

from model.clothing import Clothing


def _get_uid(app_state):
    """app_state에서 user_id 안전하게 추출."""
    u = app_state.get("user") or app_state.get("current_user")
    if u and isinstance(u, dict):
        return u.get("user_id", "guest")
    return "guest"


def _action_btn(text, on_click, icon=None, color=None):
    """Row 안에서도 안전하게 쓸 수 있는 버튼 (expand 없음)."""
    color = color or C["primary"]
    row = []
    if icon:
        row.append(ft.Icon(icon, color="white", size=18))
    row.append(ft.Text(text, color="white", weight=ft.FontWeight.BOLD, size=F["md"]))
    return ft.ElevatedButton(
        content=ft.Row(row, alignment=ft.MainAxisAlignment.CENTER, spacing=6, tight=True),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=color,
            shape=ft.RoundedRectangleBorder(radius=R["md"]),
            padding=ft.padding.symmetric(vertical=14, horizontal=16),
            elevation=2,
        ),
        expand=True,
    )


def _full_btn(text, on_click, icon=None, color=None):
    """전체 너비 버튼."""
    color = color or C["primary"]
    row = []
    if icon:
        row.append(ft.Icon(icon, color="white", size=18))
    row.append(ft.Text(text, color="white", weight=ft.FontWeight.BOLD, size=F["md"]))
    return ft.ElevatedButton(
        content=ft.Row(row, alignment=ft.MainAxisAlignment.CENTER, spacing=6, tight=True),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=color,
            shape=ft.RoundedRectangleBorder(radius=R["md"]),
            padding=ft.padding.symmetric(vertical=15),
            elevation=2,
        ),
        width=9999,
    )


# ─────────────────────────────────────────────
# 등록 방법 선택 화면
# ─────────────────────────────────────────────
def build_register_options(page, go):
    def opt_card(title, desc, icon, color, on_click):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color="white", size=26),
                    width=54, height=54, bgcolor=color,
                    border_radius=R["md"], alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(title, size=F["md"], weight=ft.FontWeight.W_700, color=C["text"]),
                    ft.Text(desc,  size=F["sm"], color=C["subtext"]),
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=C["hint"]),
            ], spacing=S["md"], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=C["card"], border_radius=R["lg"],
            border=ft.border.all(1, C["border"]),
            padding=S["lg"], on_click=on_click, ink=True,
            shadow=ft.BoxShadow(blur_radius=14, color=C["shadow"], offset=ft.Offset(0, 3)),
        )

    return ft.Column([
        top_bar(page, "옷 등록하기", on_back=lambda: go("/")),
        ft.Container(
            content=ft.Column([
                ft.Container(height=S["md"]),
                ft.Text("어떻게 등록할까요?",
                        size=F["lg"], weight=ft.FontWeight.W_700, color=C["text"]),
                ft.Text("방법을 선택해주세요", size=F["sm"], color=C["subtext"]),
                ft.Container(height=S["lg"]),
                opt_card("사진으로 등록", "갤러리에서 옷 사진을 선택합니다.",
                         ft.Icons.PHOTO_CAMERA_ROUNDED, C["pink"],
                         lambda e: go("/register_photo")),
                opt_card("직접 입력", "종류, 색상 등 정보를 직접 입력합니다.",
                         ft.Icons.EDIT_NOTE_ROUNDED, C["primary"],
                         lambda e: go("/register_direct")),
            ], spacing=S["md"]),
            padding=S["lg"], expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 사진 등록 화면
# ─────────────────────────────────────────────
def build_register_photo(page, go, app_state):
    photo_state = {
        "file_path": "",
        "colors":    [],
        "max_colors": 3,
    }

    # ─── 위젯 ───
    image_display = ft.Container(
        width=260, height=260,
        bgcolor=C["muted"], border_radius=R["md"],
        border=ft.border.all(1, C["border"]),
        content=ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                        color=C["hint"], size=48),
        alignment=ft.alignment.center,
    )
    color_chips_row = ft.Row(wrap=True, spacing=6, run_spacing=6)
    auto_guess_text = ft.Text(
        "사진을 선택하면 옷 종류를 자동으로 추측합니다.",
        size=F["xs"], color=C["subtext"],
    )
    category_dd = dropdown("종류", "상의", list(DETAIL_OPTIONS.keys()))
    detail_dd   = dropdown("세부 종류", DETAIL_OPTIONS["상의"][0], DETAIL_OPTIONS["상의"])
    memo_tf     = field("메모", hint="예: 데일리용, 학교 갈 때")

    # 특징 선택
    feature_options = {
        "상의":    {"fit":["오버핏","정핏","슬림핏"],
                    "thickness":["얇음","보통","두꺼움"],
                    "mood":["캐주얼","댄디","미니멀","스트릿","포멀"],
                    "season":["봄가을","여름","겨울"]},
        "하의":    {"fit":["와이드","일자핏","슬림핏","스키니","조거핏"],
                    "thickness":["얇음","보통","두꺼움"],
                    "mood":["캐주얼","댄디","스트릿","포멀"],
                    "season":["봄가을","여름","겨울"]},
        "아우터":  {"fit":["오버핏","정핏","크롭","롱기장"],
                    "thickness":["얇음","보통","두꺼움"],
                    "mood":["캐주얼","댄디","미니멀","스트릿","포멀"],
                    "season":["봄가을","겨울"]},
        "신발":    {"fit":["낮은 굽","높은 굽","발볼 넓음","발볼 보통"],
                    "thickness":["가벼움","보통","두꺼움"],
                    "mood":["캐주얼","댄디","스트릿","스포티","포멀"],
                    "season":["봄가을","여름","겨울"]},
        "악세서리":{"fit":["작은 사이즈","보통 사이즈","큰 사이즈"],
                    "thickness":["얇음","보통","두꺼움"],
                    "mood":["캐주얼","댄디","미니멀","스트릿","포멀","러블리"],
                    "season":["사계절","봄가을","여름","겨울"]},
    }
    selected_features = {"fit":"","thickness":"","mood":"","season":""}
    feature_btns_row  = ft.Column(spacing=S["sm"])

    def refresh_image():
        if not photo_state["file_path"]:
            return
        resolved = resolve_existing_path(photo_state["file_path"])
        if resolved and os.path.exists(resolved):
            image_display.content = ft.Image(
                src=resolved,
                width=260, height=260,
                fit=ft.ImageFit.CONTAIN,
                border_radius=ft.border_radius.all(R["md"]),
            )
            image_display.bgcolor = None
        page.update()

    def refresh_colors():
        color_chips_row.controls.clear()
        for idx, c in enumerate(photo_state["colors"]):
            def make_remove(i):
                def remove(_):
                    photo_state["colors"].pop(i)
                    refresh_colors(); page.update()
                return remove
            color_chips_row.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(width=16, height=16, bgcolor=c["hex"],
                                 border_radius=8,
                                 border=ft.border.all(1, C["border"])),
                    ft.Text(f"{c['name']}  {c['hex']}",
                            size=F["xs"], color=C["text"]),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=14,
                                  icon_color=C["danger"],
                                  on_click=make_remove(idx),
                                  style=ft.ButtonStyle(padding=0)),
                ], spacing=4, tight=True),
                bgcolor=C["muted"], border_radius=R["full"],
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            ))
        page.update()

    def refresh_feature_buttons():
        feature_btns_row.controls.clear()
        cat  = category_dd.value or "상의"
        opts = feature_options.get(cat, {})
        key_labels = {"fit":"핏","thickness":"두께","mood":"무드","season":"계절감"}
        for key, values in opts.items():
            row = ft.Row(wrap=True, spacing=6, run_spacing=6)
            for v in values:
                sel = selected_features[key] == v
                def make_handler(k, val):
                    def handler(_):
                        selected_features[k] = "" if selected_features[k] == val else val
                        refresh_feature_buttons(); page.update()
                    return handler
                row.controls.append(ft.Container(
                    content=ft.Text(v, size=F["xs"],
                                    color="white" if sel else C["text"],
                                    weight=ft.FontWeight.W_600),
                    bgcolor=C["primary"] if sel else C["muted"],
                    border_radius=R["full"],
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    on_click=make_handler(key, v), ink=True,
                ))
            feature_btns_row.controls.append(ft.Column([
                ft.Text(key_labels.get(key, key),
                        size=F["xs"], color=C["subtext"]),
                row,
            ], spacing=4))

    refresh_feature_buttons()

    def update_details(e=None):
        cat  = category_dd.value or "상의"
        opts = DETAIL_OPTIONS.get(cat, [])
        detail_dd.options = [ft.dropdown.Option(o) for o in opts]
        detail_dd.value   = opts[0] if opts else ""
        refresh_feature_buttons()
        page.update()

    category_dd.on_change = update_details

    file_picker = ft.FilePicker(on_result=lambda e: on_file_pick(e))
    page.overlay.append(file_picker)

    def on_file_pick(e):
        if not e.files:
            return
        fp = e.files[0].path
        resolved = resolve_existing_path(fp)
        photo_state["file_path"] = resolved or fp
        photo_state["colors"]    = []

        # 색상 자동 추출
        try:
            extracted = extract_dominant_colors(
                photo_state["file_path"], color_count=photo_state["max_colors"])
            for name, hex_code in extracted:
                hc  = hex_code.lstrip("#")
                rgb = tuple(int(hc[i:i+2], 16) for i in (0, 2, 4))
                photo_state["colors"].append(
                    {"rgb": rgb, "hex": hex_code, "name": name})
        except Exception as ex:
            print("색상 추출 오류:", ex)

        refresh_image()
        refresh_colors()

        # 카테고리 자동 추측
        try:
            from api_client import recommend_from_photo_backend
            if photo_state["colors"]:
                mc     = photo_state["colors"][0]
                result = recommend_from_photo_backend(mc["name"], "상의", "하의")
                if isinstance(result, dict) and not result.get("error"):
                    guessed = result.get("category", "")
                    if guessed in DETAIL_OPTIONS:
                        category_dd.value        = guessed
                        auto_guess_text.value    = f"자동 추측: {guessed}"
                        update_details()
        except Exception:
            pass
        page.update()

    def on_save(_):
        if not photo_state["file_path"]:
            page.open(ft.SnackBar(
                ft.Text("먼저 사진을 선택해 주세요."), bgcolor=C["danger"]))
            return
        if not photo_state["colors"]:
            page.open(ft.SnackBar(
                ft.Text("색상이 추출되지 않았습니다."), bgcolor=C["danger"]))
            return

        main_color        = photo_state["colors"][0]
        saved_image_path  = photo_state["file_path"]

        # 이미지 복사
        try:
            image_dir = str(IMAGE_DIR)
            os.makedirs(image_dir, exist_ok=True)
            ext      = os.path.splitext(photo_state["file_path"])[1] or ".jpg"
            uid      = _get_uid(app_state)
            filename = f"{uid}_{int(time.time()*1000)}{ext}"
            saved_image_path = os.path.join(image_dir, filename)
            shutil.copy2(photo_state["file_path"], saved_image_path)
        except Exception as ex:
            print("이미지 복사 실패:", ex)

        # feature 텍스트 조합
        parts = [f"{k}: {v}" for k, v in selected_features.items() if v]
        memo  = (memo_tf.value or "").strip()
        if memo:
            parts.append(f"메모: {memo}")
        feature_text = ", ".join(parts) or "특징 없음"

        item = Clothing(
            category   = category_dd.value,
            detail     = detail_dd.value,
            feature    = feature_text,
            rgb        = main_color["rgb"],
            hex_code   = main_color["hex"],
            color_name = main_color["name"],
            image_path = saved_image_path,
            colors     = photo_state["colors"],
        )
        uid    = _get_uid(app_state)
        result = add_clothing_to_backend(item, uid)
        if isinstance(result, dict) and "id" in result:
            item.id = result["id"]
        app_state.setdefault("clothes", []).append(item)
        page.open(ft.SnackBar(
            ft.Text(f"{item.category} / {item.detail} 저장 완료!"),
            bgcolor=C["success"]))
        go("/clothes")

    # ─── UI 조립 ───
    return ft.Column([
        top_bar(page, "사진으로 옷 등록", on_back=lambda: go("/register")),
        ft.Container(
            content=ft.Column([
                # 사진 선택 카드
                card(ft.Column([
                    section("사진 선택"),
                    ft.Text("사진을 선택하면 대표 색상 3개가 자동 추출됩니다.",
                            size=F["xs"], color=C["subtext"]),
                    ft.Container(height=6),
                    # 이미지 미리보기
                    ft.Row([image_display],
                           alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),
                    # 버튼 행 — expand=True로 각각 반반
                    ft.Row([
                        _action_btn(
                            "사진 선택",
                            lambda e: file_picker.pick_files(
                                allowed_extensions=["png","jpg","jpeg","bmp"]),
                            ft.Icons.PHOTO_LIBRARY_ROUNDED,
                        ),
                        ft.Container(width=S["sm"]),
                        ft.ElevatedButton(
                            content=ft.Text("색상 초기화",
                                            color=C["subtext"],
                                            weight=ft.FontWeight.W_600,
                                            size=F["body"]),
                            on_click=lambda e: [
                                photo_state["colors"].clear(),
                                refresh_colors(),
                                page.update(),
                            ],
                            style=ft.ButtonStyle(
                                bgcolor=C["muted"],
                                shape=ft.RoundedRectangleBorder(radius=R["md"]),
                                padding=ft.padding.symmetric(vertical=14),
                                elevation=0,
                            ),
                            expand=True,
                        ),
                    ]),
                    ft.Container(height=4),
                    auto_guess_text,
                ], spacing=S["sm"])),
                # 추출된 색상 카드
                card(ft.Column([
                    section("추출된 색상"),
                    ft.Text(f"최대 {photo_state['max_colors']}개까지 저장됩니다.",
                            size=F["xs"], color=C["subtext"]),
                    ft.Container(height=4),
                    color_chips_row,
                ], spacing=S["sm"])),
                # 옷 정보 카드
                card(ft.Column([
                    section("옷 정보"),
                    ft.Container(height=4),
                    category_dd,
                    detail_dd,
                ], spacing=S["sm"])),
                # 특징 선택 카드
                card(ft.Column([
                    section("특징 선택"),
                    feature_btns_row,
                    memo_tf,
                ], spacing=S["sm"])),
                # 저장 버튼
                _full_btn("저장하기", on_save,
                          ft.Icons.CHECK_ROUNDED, C["success"]),
                ft.Container(height=S["lg"]),  # 하단 여백
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)


# ─────────────────────────────────────────────
# 직접 입력 등록 화면
# ─────────────────────────────────────────────
def build_register_direct(page, go, app_state):
    sel = {"r": 90, "g": 130, "b": 255}

    category_dd = dropdown("종류", "상의", list(DETAIL_OPTIONS.keys()))
    detail_dd   = dropdown("세부 종류", DETAIL_OPTIONS["상의"][0], DETAIL_OPTIONS["상의"])
    feature_tf  = field("특징", hint="예: 오버핏, 얇음, 캐주얼")

    preview = ft.Container(
        width=70, height=70,
        bgcolor=rgb_to_hex(**sel),
        border_radius=R["md"],
        border=ft.border.all(1, C["border"]),
    )
    color_name_text = ft.Text(
        rgb_to_name(**sel),
        size=F["md"], weight=ft.FontWeight.W_700, color=C["text"],
    )
    color_hex_text = ft.Text(
        rgb_to_hex(**sel),
        size=F["sm"], color=C["hint"],
    )

    def update_color():
        hx = rgb_to_hex(**sel)
        nm = rgb_to_name(**sel)
        preview.bgcolor     = hx
        color_name_text.value = nm
        color_hex_text.value  = hx
        page.update()

    def make_slider(ch, accent):
        vt = ft.Text(str(sel[ch]), size=F["sm"], color=C["subtext"],
                     weight=ft.FontWeight.W_600, width=30,
                     text_align=ft.TextAlign.RIGHT)
        def on_ch(e):
            sel[ch] = int(e.control.value)
            vt.value = str(sel[ch])
            update_color()
        return ft.Row([
            ft.Container(
                content=ft.Text(ch.upper(), color="white",
                                weight=ft.FontWeight.BOLD, size=F["xs"]),
                width=26, height=26, bgcolor=accent,
                border_radius=R["sm"], alignment=ft.alignment.center,
            ),
            ft.Slider(min=0, max=255, value=sel[ch], divisions=255,
                      expand=True, active_color=accent, on_change=on_ch),
            vt,
        ], spacing=S["sm"])

    def update_details(e=None):
        opts = DETAIL_OPTIONS.get(category_dd.value, [])
        detail_dd.options = [ft.dropdown.Option(o) for o in opts]
        detail_dd.value   = opts[0] if opts else ""
        page.update()
    category_dd.on_change = update_details

    def on_save(_):
        r, g, b = sel["r"], sel["g"], sel["b"]
        item = Clothing(
            category   = category_dd.value,
            detail     = detail_dd.value,
            feature    = (feature_tf.value or "").strip() or "특징 없음",
            rgb        = (r, g, b),
            hex_code   = rgb_to_hex(r, g, b),
            color_name = rgb_to_name(r, g, b),
            image_path = "",
        )
        uid    = _get_uid(app_state)
        result = add_clothing_to_backend(item, uid)
        if isinstance(result, dict) and "id" in result:
            item.id = result["id"]
        app_state.setdefault("clothes", []).append(item)
        page.open(ft.SnackBar(
            ft.Text(f"{item.category} / {item.detail} 저장 완료!"),
            bgcolor=C["success"]))
        go("/clothes")

    return ft.Column([
        top_bar(page, "직접 등록하기", on_back=lambda: go("/register")),
        ft.Container(
            content=ft.Column([
                card(ft.Column([
                    section("기본 정보"),
                    ft.Container(height=4),
                    category_dd,
                    detail_dd,
                    feature_tf,
                ], spacing=S["sm"])),
                card(ft.Column([
                    section("색상 선택"),
                    ft.Container(height=4),
                    ft.Row([
                        preview,
                        ft.Column([
                            ft.Text("선택한 색", size=F["xs"], color=C["hint"]),
                            color_name_text,
                            color_hex_text,
                        ], spacing=2),
                    ], spacing=S["md"]),
                    ft.Container(height=4),
                    make_slider("r", "#ef4444"),
                    make_slider("g", "#22c55e"),
                    make_slider("b", "#3b82f6"),
                ], spacing=S["md"])),
                _full_btn("저장하기", on_save,
                          ft.Icons.CHECK_ROUNDED, C["success"]),
                ft.Container(height=S["lg"]),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)
