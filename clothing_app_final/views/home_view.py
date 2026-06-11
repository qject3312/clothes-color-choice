"""홈 화면 - 히어로 + 미니통계 + 6개 메뉴."""
import flet as ft
from collections import Counter
from views.theme import C, R, S, F


def _cat_counts(clothes):
    cnt = Counter()
    for c in clothes:
        cat = (c.get("category") if isinstance(c, dict) else getattr(c,"category","")) or "기타"
        cnt[cat] += 1
    return cnt


def _recent_text(clothes):
    if not clothes:
        return "아직 등록한 옷이 없습니다."
    item = clothes[-1]
    g = lambda k: (item.get(k) if isinstance(item,dict) else getattr(item,k,"")) or ""
    parts = [p for p in [g("color_name"), g("category"), g("detail")] if p]
    return " · ".join(parts) if parts else "최근 등록 있음"


def build_home(page, go, user, clothes, open_menu):
    name = (user.get("name") or user.get("user_id","게스트")) if user else "게스트"
    total = len(clothes)
    cat   = _cat_counts(clothes)

    def menu_card(title, desc, emoji, color, route):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(emoji, size=18, color=color, weight=ft.FontWeight.BOLD),
                        width=36, height=36, bgcolor=C["primary_soft"],
                        border_radius=R["sm"], alignment=ft.alignment.center,
                    ),
                    ft.Text(title, size=F["body"]+1, weight=ft.FontWeight.BOLD, color=C["text"]),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Text(desc, size=F["xs"]+1, color=C["subtext"], max_lines=2),
                ft.Row([
                    ft.Container(expand=True),
                    ft.Text("바로가기 ›", size=F["xs"]+1,
                            weight=ft.FontWeight.BOLD, color=color),
                ]),
            ], spacing=6, expand=True),
            padding=S["md"],
            bgcolor=C["card"],
            border_radius=R["md"],
            border=ft.border.all(1, C["border"]),
            on_click=lambda e: go(route),
            ink=True, ink_color=color,
            expand=True, height=116,
        )

    def mini_stat(label, val, sub):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=F["xs"], weight=ft.FontWeight.BOLD, color=C["subtext"]),
                ft.Text(str(val), size=F["xxl"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Text(sub, size=F["xs"], color=C["hint"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=ft.padding.symmetric(vertical=10, horizontal=6),
            bgcolor=C["card"], border_radius=R["md"],
            border=ft.border.all(1, C["border"]),
            expand=True,
        )

    return ft.Column([
        # 상단바
        ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.MENU_ROUNDED, icon_color=C["text"],
                              icon_size=22, on_click=lambda e: open_menu()),
                ft.Text("핏픽", size=F["lg"], weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.IconButton(
                    content=ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_ROUNDED, color=C["subtext"], size=20),
                        width=38, height=38, bgcolor=C["muted"],
                        border_radius=19, alignment=ft.alignment.center,
                    ),
                    on_click=lambda e: go("/profile"),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=C["card"],
            padding=ft.padding.symmetric(horizontal=S["sm"], vertical=S["sm"]),
        ),
        # 본문
        ft.Container(
            content=ft.Column([
                # 히어로
                ft.Container(
                    content=ft.Column([
                        ft.Text("FITPICK", size=F["xs"], weight=ft.FontWeight.BOLD, color="#bfdbfe"),
                        ft.Text(f"{name}님,\n오늘 뭐 입을까요?",
                                size=F["lg"], weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=6),
                        ft.Text("등록한 옷과 프로필을 기반으로 색상·날씨·체형·스타일을 고려해 추천합니다.",
                                size=F["xs"]+1, color="#dbeafe"),
                        ft.Container(height=10),
                        ft.Row([
                            *[ft.Container(
                                content=ft.Text(t, size=F["xs"], weight=ft.FontWeight.BOLD, color="#bfdbfe"),
                                bgcolor="#1e40af", border_radius=R["sm"],
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ) for t in [f"옷 {total}개",
                                        f"상의 {cat.get('상의',0)}",
                                        f"하의 {cat.get('하의',0)}",
                                        "자동 분석"]],
                        ], wrap=True, spacing=5, run_spacing=4),
                    ], spacing=2),
                    bgcolor="#1d4ed8", border_radius=R["md"],
                    padding=ft.padding.only(left=S["lg"], right=S["lg"], top=S["lg"], bottom=S["lg"]),
                ),
                # 미니 통계 4개
                ft.Row([
                    mini_stat("전체", total, "items"),
                    mini_stat("상의", cat.get("상의", 0), "tops"),
                    mini_stat("하의", cat.get("하의", 0), "bottoms"),
                    mini_stat("아우터", cat.get("아우터", 0), "outer"),
                ], spacing=6),
                # 최근 등록
                ft.Container(
                    content=ft.Row([
                        ft.Text("최근 등록", size=F["xs"], weight=ft.FontWeight.BOLD, color=C["subtext"]),
                        ft.Text(_recent_text(clothes), size=F["sm"],
                                weight=ft.FontWeight.W_600, color=C["text"],
                                expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=C["card"], border_radius=R["sm"],
                    border=ft.border.all(1, C["border"]),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                ),
                # 메뉴 그리드 3행 2열
                ft.Row([
                    menu_card("옷 등록", "사진으로 옷을 등록합니다.", "＋", C["primary"], "/register"),
                    menu_card("맞춤 추천", "TOP3 코디 점수를 확인합니다.", "★", C["purple"], "/recommend"),
                ], spacing=8),
                ft.Row([
                    menu_card("코디해보기", "상·하의 조합을 확인합니다.", "◈", C["pink"], "/coordination"),
                    menu_card("온도 추천", "기온에 맞는 옷을 추천합니다.", "℃", C["success"], "/temperature"),
                ], spacing=8),
                ft.Row([
                    menu_card("내 옷장", "저장된 옷 목록을 확인합니다.", "▦", C["indigo"], "/clothes"),
                    menu_card("저장 코디", "저장한 코디 기록을 확인합니다.", "♡", C["gray"], "/outfit"),
                ], spacing=8),
                ft.Row([
                    menu_card("색상 추천", "옷 하나를 기준으로 나머지 색상을 추천합니다.", "◎", "#0891b2", "/base_recommend"),
                ], spacing=8),
                ft.Text("사진 등록 → 색상 추출 → 코디 추천까지 한 번에",
                        size=F["xs"], color=C["hint"], text_align=ft.TextAlign.CENTER),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=12, vertical=12),
            expand=True,
        ),
    ], spacing=0, expand=True)
