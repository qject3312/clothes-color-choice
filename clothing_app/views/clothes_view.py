"""내 옷장 화면. 이미지를 resolve_existing_path로 처리해 반드시 표시."""
import flet as ft
from views.theme import C, R, S, F, DETAIL_OPTIONS
from views.components import (card, top_bar, btn_primary, section,
                               dropdown, field, cloth_image, empty_state)

try:
    from api_client import delete_clothing_backend, update_clothing_backend
except Exception:
    def delete_clothing_backend(cid, uid): return {}
    def update_clothing_backend(cid, item, uid): return {}


def _get(item, key, default=""):
    return (item.get(key) if isinstance(item, dict) else getattr(item, key, default)) or default


def build_clothes(page, go, app_state):
    """등록된 옷 목록 + 카테고리/세부 필터 + 이미지 표시 + 수정/삭제."""

    selected = {"category": "상의", "detail": "전체"}

    def get_filtered():
        result = []
        for c in app_state.get("clothes", []):
            if _get(c, "category") != selected["category"]:
                continue
            if selected["detail"] != "전체" and _get(c, "detail") != selected["detail"]:
                continue
            result.append(c)
        return result

    # 상단 필터 영역
    cat_row    = ft.Row(spacing=4, wrap=True)
    detail_row = ft.Row(spacing=4, wrap=True, run_spacing=4)
    list_col   = ft.Column(spacing=S["sm"], scroll=ft.ScrollMode.AUTO)

    def refresh_all():
        # 카테고리 버튼
        cat_row.controls = [
            ft.Container(
                content=ft.Text(cat, size=F["sm"], weight=ft.FontWeight.W_700,
                                color="white" if cat == selected["category"] else C["text"]),
                bgcolor=C["primary"] if cat == selected["category"] else C["muted"],
                border_radius=R["full"],
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                on_click=lambda e, c=cat: set_cat(c), ink=True,
            )
            for cat in list(DETAIL_OPTIONS.keys())
        ]
        # 세부 버튼
        details = ["전체"] + DETAIL_OPTIONS.get(selected["category"], [])
        detail_row.controls = [
            ft.Container(
                content=ft.Text(d, size=F["xs"], weight=ft.FontWeight.W_600,
                                color="white" if d == selected["detail"] else C["text"]),
                bgcolor=C["success"] if d == selected["detail"] else C["card"],
                border_radius=R["full"],
                border=ft.border.all(1, C["border"]),
                padding=ft.padding.symmetric(horizontal=12, vertical=7),
                on_click=lambda e, d=d: set_detail(d), ink=True,
            )
            for d in details
        ]
        # 목록
        filtered = get_filtered()
        list_col.controls.clear()
        if not filtered:
            list_col.controls.append(
                ft.Container(
                    content=ft.Text(f"등록된 {selected['category']}가 없습니다.",
                                    size=F["body"], color=C["subtext"]),
                    padding=ft.padding.symmetric(vertical=40),
                    alignment=ft.alignment.center,
                )
            )
        else:
            for c in filtered:
                list_col.controls.append(make_cloth_card(c))
        page.update()

    def set_cat(cat):
        selected["category"] = cat
        selected["detail"] = "전체"
        refresh_all()

    def set_detail(d):
        selected["detail"] = d
        refresh_all()

    def make_cloth_card(cloth):
        image_path = _get(cloth, "image_path")
        img_widget = cloth_image(image_path, size=72, radius=10)

        def on_delete(_):
            def confirm(e):
                page.close(dlg)
                cloth_id = _get(cloth, "id", None) or (cloth.get("id") if isinstance(cloth, dict) else getattr(cloth, "id", None))
                if cloth_id is not None:
                    delete_clothing_backend(cloth_id, app_state.get("user_id", "guest"))
                clothes = app_state.get("clothes", [])
                if cloth in clothes:
                    clothes.remove(cloth)
                page.open(ft.SnackBar(ft.Text("삭제되었습니다."), bgcolor=C["subtext"]))
                refresh_all()
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("삭제하시겠어요?", weight=ft.FontWeight.BOLD),
                content=ft.Text(f"{_get(cloth,'category')} / {_get(cloth,'detail')}"),
                actions=[
                    ft.TextButton("취소", on_click=lambda e: page.close(dlg)),
                    ft.TextButton("삭제", on_click=confirm,
                                  style=ft.ButtonStyle(color=C["danger"])),
                ],
            )
            page.open(dlg)

        def on_edit(_):
            page.session.set("edit_cloth", cloth)
            go("/clothes_edit")

        # 색상 칩들
        colors = (cloth.get("colors") if isinstance(cloth, dict) else getattr(cloth, "colors", None)) or []
        if not colors:
            hex_c = _get(cloth, "hex") or _get(cloth, "color_hex", "#cccccc")
            name_c = _get(cloth, "color_name", "미분석")
            colors = [{"hex": hex_c, "name": name_c}]

        color_chips = ft.Row([
            ft.Row([
                ft.Container(width=14, height=14, bgcolor=c.get("hex","#ccc"),
                             border_radius=7, border=ft.border.all(1, C["border"])),
                ft.Text(f"{c.get('name','')} {c.get('hex','')}",
                        size=F["xs"], color=C["subtext"]),
            ], spacing=4, tight=True)
            for c in colors
        ], wrap=True, spacing=8, run_spacing=4)

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    img_widget,
                    ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(_get(cloth,"category"), size=F["xs"],
                                                weight=ft.FontWeight.W_700, color=C["primary"]),
                                bgcolor=C["primary_soft"], border_radius=R["full"],
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.Text(_get(cloth,"detail"), size=F["md"],
                                    weight=ft.FontWeight.W_700, color=C["text"]),
                        ], spacing=6),
                        ft.Text(_get(cloth,"feature"), size=F["sm"], color=C["subtext"],
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        color_chips,
                    ], spacing=4, expand=True),
                    ft.Column([
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=C["primary"],
                                      icon_size=20, on_click=on_edit),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=C["danger"],
                                      icon_size=20, on_click=on_delete),
                    ], spacing=0),
                ], spacing=S["md"], vertical_alignment=ft.CrossAxisAlignment.START),
            ]),
            bgcolor=C["card"], border_radius=R["lg"],
            border=ft.border.all(1, C["border"]),
            padding=S["md"],
            shadow=ft.BoxShadow(blur_radius=10, color=C["shadow"], offset=ft.Offset(0, 2)),
        )

    refresh_all()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=C["text"],
                              on_click=lambda e: go("/")),
                ft.Text("등록된 옷 확인", size=F["lg"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.IconButton(ft.Icons.ADD_ROUNDED, icon_color=C["primary"],
                              on_click=lambda e: go("/register")),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=C["card"],
            padding=ft.padding.symmetric(horizontal=S["sm"], vertical=S["sm"]),
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(content=cat_row, padding=ft.padding.only(bottom=4)),
                ft.Container(content=detail_row, padding=ft.padding.only(bottom=4)),
                list_col,
            ], spacing=S["sm"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=12, vertical=12),
            expand=True,
        ),
    ], spacing=0, expand=True)


def build_clothes_edit(page, go, app_state):
    """옷 정보 수정 화면."""
    cloth = page.session.get("edit_cloth")
    if not cloth:
        go("/clothes"); return ft.Container()

    cat_dd  = dropdown("종류", _get(cloth,"category","상의"), list(DETAIL_OPTIONS.keys()))
    det_dd  = dropdown("세부 종류", _get(cloth,"detail",""), DETAIL_OPTIONS.get(_get(cloth,"category","상의"), []))
    cname_tf= field("색상 이름", value=_get(cloth,"color_name",""))
    hex_tf  = field("색상 코드", value=_get(cloth,"hex") or _get(cloth,"color_hex","#cccccc"))
    feat_tf = field("특징/메모", value=_get(cloth,"feature",""), multiline=True)

    def update_details(e=None):
        opts = DETAIL_OPTIONS.get(cat_dd.value, [])
        det_dd.options = [ft.dropdown.Option(o) for o in opts]
        if _get(cloth,"detail") in opts:
            det_dd.value = _get(cloth,"detail")
        elif opts:
            det_dd.value = opts[0]
        page.update()
    cat_dd.on_change = update_details

    def on_save(_):
        if isinstance(cloth, dict):
            cloth["category"] = cat_dd.value
            cloth["detail"]   = det_dd.value
            cloth["color_name"] = cname_tf.value.strip() or "미분석"
            cloth["hex"]        = hex_tf.value.strip() or "#cccccc"
            cloth["color_hex"]  = cloth["hex"]
            cloth["feature"]    = feat_tf.value.strip() or "특징 없음"
            cid = cloth.get("id")
        else:
            cloth.category   = cat_dd.value
            cloth.detail     = det_dd.value
            cloth.color_name = cname_tf.value.strip() or "미분석"
            cloth.hex        = hex_tf.value.strip() or "#cccccc"
            cloth.feature    = feat_tf.value.strip() or "특징 없음"
            cid = getattr(cloth, "id", None)

        if cid is not None:
            result = update_clothing_backend(cid, cloth, app_state.get("user_id","guest"))
            if isinstance(result, dict) and ("error" in result or "detail" in result):
                page.open(ft.SnackBar(ft.Text("화면에 반영했지만 서버 저장 실패"), bgcolor=C["warning"]))
                return
        page.open(ft.SnackBar(ft.Text("수정 완료!"), bgcolor=C["success"]))
        go("/clothes")

    return ft.Column([
        top_bar(page, "옷 정보 수정", on_back=lambda: go("/clothes")),
        ft.Container(
            content=ft.Column([
                card(ft.Column([section("옷 정보"), ft.Container(height=4),
                                cat_dd, det_dd, cname_tf, hex_tf, feat_tf], spacing=S["sm"])),
                btn_primary("수정 저장", on_save, ft.Icons.CHECK_ROUNDED, C["success"]),
                btn_secondary("취소", lambda e: go("/clothes")),
            ], spacing=S["md"], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=S["lg"], vertical=S["lg"]),
            expand=True,
        ),
    ], spacing=0, expand=True)
