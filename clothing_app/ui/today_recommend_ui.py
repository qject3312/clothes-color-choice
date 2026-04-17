import tkinter as tk


class TodayRecommendUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("오늘의 추천 코디")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        tops = [c for c in self.app.clothes if c.category == "상의"]
        bottoms = [c for c in self.app.clothes if c.category == "하의"]
        outers = [c for c in self.app.clothes if c.category == "아우터"]

        if not self.app.clothes:
            tk.Label(
                body,
                text="먼저 옷을 등록해 주세요.",
                font=("Arial", 15, "bold"),
                bg="#f4f6fb",
                fg="#222222"
            ).pack(pady=40)

            tk.Button(
                body,
                text="옷 등록하러 가기",
                font=("Arial", 12, "bold"),
                bg="#2f80ff",
                fg="white",
                width=16,
                height=2,
                bd=0,
                command=self.app.show_register_options
            ).pack(pady=10)
            return

        card = tk.Frame(body, bg="white")
        card.pack(fill="x", pady=10)

        tk.Label(
            card,
            text="오늘의 추천 조합",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=16, pady=(16, 8))

        def draw_line(label, item):
            if item:
                text = f"{label}: {item.detail} / {item.color_name} / {item.feature}"
            else:
                text = f"{label}: 없음"

            tk.Label(
                card,
                text=text,
                font=("Arial", 11),
                bg="white",
                fg="#444444",
                anchor="w"
            ).pack(fill="x", padx=16, pady=6)

        draw_line("상의", tops[0] if tops else None)
        draw_line("하의", bottoms[0] if bottoms else None)
        draw_line("아우터", outers[0] if outers else None)

        tk.Label(
            card,
            text="추천 이유: 현재 등록된 옷 중에서 가장 먼저 사용할 수 있는 기본 조합입니다.",
            font=("Arial", 11),
            bg="white",
            fg="#555555",
            wraplength=360,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(10, 8))

        tk.Label(
            card,
            text="추천하지 않는 이유: 아직 날씨나 온도를 반영한 추천은 아닙니다.",
            font=("Arial", 11),
            bg="white",
            fg="#c0392b",
            wraplength=360,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).pack(pady=15)