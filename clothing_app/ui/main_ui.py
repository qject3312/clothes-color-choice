import tkinter as tk
from collections import Counter
from ui import style


class MainUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("핏픽")

        body = tk.Frame(self.app.main_frame, bg=style.BG)
        body.pack(fill="both", expand=True)

        user_name = "게스트"
        if self.app.current_user:
            user_name = self.app.current_user.get("name") or self.app.current_user.get("user_id", "게스트")

        clothes = list(getattr(self.app, "clothes", []) or [])
        total_count = len(clothes)
        category_counts = self._category_counts(clothes)

        # 메인 히어로 영역
        hero_wrap = tk.Frame(body, bg=style.SHADOW)
        hero_wrap.pack(fill="x", padx=14, pady=(14, 8))

        hero = tk.Frame(hero_wrap, bg="#1d4ed8")
        hero.pack(fill="x", padx=(0, 2), pady=(0, 2))

        tk.Label(
            hero,
            text="FITPICK",
            font=(style.FONT, 8, "bold"),
            bg="#1d4ed8",
            fg="#bfdbfe",
        ).pack(anchor="w", padx=18, pady=(13, 0))

        tk.Label(
            hero,
            text=f"{user_name}님, 오늘 뭐 입을까요?",
            font=(style.FONT, 16, "bold"),
            bg="#1d4ed8",
            fg="white",
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 5))

        tk.Label(
            hero,
            text="등록한 옷과 프로필 정보를 바탕으로 색상, 날씨, 체형, 스타일을 고려해 코디를 추천합니다.",
            font=(style.FONT, 8),
            bg="#1d4ed8",
            fg="#dbeafe",
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 10))

        stat_row = tk.Frame(hero, bg="#1d4ed8")
        stat_row.pack(fill="x", padx=18, pady=(0, 13))
        self._stat_chip(stat_row, f"옷 {total_count}개")
        self._stat_chip(stat_row, f"상의 {category_counts.get('상의', 0)}")
        self._stat_chip(stat_row, f"하의 {category_counts.get('하의', 0)}")
        self._stat_chip(stat_row, "자동 분석")

        # 실제 앱 느낌을 위한 내 옷장 요약 카드
        summary = tk.Frame(body, bg=style.BG)
        summary.pack(fill="x", padx=14, pady=(0, 6))
        for c in range(4):
            summary.grid_columnconfigure(c, weight=1, uniform="summary")

        self._mini_stat(summary, 0, "전체", str(total_count), "items")
        self._mini_stat(summary, 1, "상의", str(category_counts.get("상의", 0)), "tops")
        self._mini_stat(summary, 2, "하의", str(category_counts.get("하의", 0)), "bottoms")
        self._mini_stat(summary, 3, "아우터", str(category_counts.get("아우터", 0)), "outer")

        recent_text = self._recent_text(clothes)
        if recent_text:
            recent = tk.Frame(body, bg="#ffffff", highlightbackground=style.CARD_BORDER, highlightthickness=1, bd=0)
            recent.pack(fill="x", padx=14, pady=(0, 8))
            tk.Label(recent, text="최근 등록", font=(style.FONT, 8, "bold"), bg="#ffffff", fg=style.SUBTEXT).pack(side="left", padx=(12, 6), pady=8)
            tk.Label(recent, text=recent_text, font=(style.FONT, 9, "bold"), bg="#ffffff", fg=style.TEXT).pack(side="left", pady=8)

        grid = tk.Frame(body, bg=style.BG)
        grid.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        for c in range(2):
            grid.grid_columnconfigure(c, weight=1, uniform="menu")
        for r in range(3):
            grid.grid_rowconfigure(r, weight=1, uniform="menu", minsize=106)

        def menu_card(row, col, title, desc, emoji, color, command):
            card = tk.Frame(
                grid,
                bg=style.CARD,
                highlightbackground=style.CARD_BORDER,
                highlightthickness=1,
                bd=0,
                height=106,
            )
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=5)
            card.grid_propagate(False)

            head = tk.Frame(card, bg=style.CARD)
            head.pack(fill="x", padx=12, pady=(10, 5))

            icon_bg = tk.Frame(
                head,
                bg="#f8fbff",
                width=34,
                height=34,
                highlightbackground="#eaf0fb",
                highlightthickness=1,
            )
            icon_bg.pack(side="left")
            icon_bg.pack_propagate(False)
            tk.Label(icon_bg, text=emoji, font=(style.FONT, 16), bg="#f8fbff", fg=color).pack(expand=True)

            tk.Label(
                head,
                text=title,
                font=(style.FONT, 11, "bold"),
                bg=style.CARD,
                fg=style.TEXT,
            ).pack(side="left", padx=(9, 0))

            tk.Label(
                card,
                text=desc,
                font=(style.FONT, 8),
                bg=style.CARD,
                fg=style.SUBTEXT,
                wraplength=165,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 3))

            cta = tk.Label(
                card,
                text="바로가기 →",
                font=(style.FONT, 8, "bold"),
                bg=style.CARD,
                fg=color,
            )
            cta.pack(anchor="e", padx=12, pady=(0, 7))

            def bind_all(widget):
                widget.bind("<Button-1>", lambda e: command())
                try:
                    widget.configure(cursor="hand2")
                except tk.TclError:
                    pass
                for child in widget.winfo_children():
                    bind_all(child)

            bind_all(card)

            def enter(_):
                card.configure(highlightbackground=color)
                cta.configure(text="이동하기 →")

            def leave(_):
                card.configure(highlightbackground=style.CARD_BORDER)
                cta.configure(text="바로가기 →")

            card.bind("<Enter>", enter)
            card.bind("<Leave>", leave)

        menu_card(0, 0, "옷 등록", "사진으로 옷을 등록하고 대표 색상을 저장합니다.", "＋", style.PRIMARY, self.app.show_register_options)
        menu_card(0, 1, "맞춤 추천", "TOP3 코디와 점수 근거를 확인합니다.", "★", "#7c3aed", self.app.show_today_recommend_ui)
        menu_card(1, 0, "코디해보기", "상의와 하의를 골라 조합을 확인합니다.", "◈", "#db2777", self.app.show_coordination_ui)
        menu_card(1, 1, "내 옷장", "저장된 옷 목록과 색상을 확인합니다.", "▦", "#475569", self.app.show_clothes_list)
        menu_card(2, 0, "저장 코디", "저장해 둔 코디 기록을 확인합니다.", "♡", "#334155", self.app.show_outfit_ui)

        tk.Label(
            body,
            text="사진 등록 → 색상 추출 → 코디 추천까지 한 번에",
            font=(style.FONT, 8),
            bg=style.BG,
            fg=style.SUBTEXT,
        ).pack(pady=(0, 6))

    def _item_value(self, item, name, default=""):
        if isinstance(item, dict):
            return item.get(name, default)
        return getattr(item, name, default)

    def _category_counts(self, clothes):
        counts = Counter()
        for item in clothes:
            category = self._item_value(item, "category", "미분류") or "미분류"
            counts[category] += 1
        return counts

    def _recent_text(self, clothes):
        if not clothes:
            return "아직 등록한 옷이 없습니다. 사진으로 첫 옷을 등록해 보세요."
        item = clothes[-1]
        color = self._item_value(item, "color_name", "") or self._item_value(item, "color", "")
        category = self._item_value(item, "category", "")
        detail = self._item_value(item, "detail", "")
        parts = [p for p in [color, category, detail] if p]
        return " · ".join(parts) if parts else "최근 등록한 옷이 있습니다."

    def _stat_chip(self, parent, text):
        chip = tk.Label(
            parent,
            text=text,
            font=(style.FONT, 8, "bold"),
            bg="#eff6ff",
            fg="#1d4ed8",
            padx=7,
            pady=4,
        )
        chip.pack(side="left", padx=(0, 5))

    def _mini_stat(self, parent, col, label, value, sub):
        card = tk.Frame(parent, bg=style.CARD, highlightbackground=style.CARD_BORDER, highlightthickness=1, bd=0)
        card.grid(row=0, column=col, sticky="ew", padx=3)
        tk.Label(card, text=label, font=(style.FONT, 7, "bold"), bg=style.CARD, fg=style.SUBTEXT).pack(pady=(6, 0))
        tk.Label(card, text=value, font=(style.FONT, 14, "bold"), bg=style.CARD, fg=style.TEXT).pack()
        tk.Label(card, text=sub, font=(style.FONT, 7), bg=style.CARD, fg="#98a2b3").pack(pady=(0, 6))
