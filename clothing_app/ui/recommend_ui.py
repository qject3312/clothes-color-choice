import tkinter as tk


class RecommendUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("추천 결과")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True, padx=16, pady=16)

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

        tk.Label(
            body,
            text="등록된 옷 목록",
            font=("Arial", 16, "bold"),
            bg="#f4f6fb",
            fg="#222222"
        ).pack(pady=10)

        for item in self.app.clothes:
            card = tk.Frame(body, bg="white")
            card.pack(fill="x", pady=6)

            tk.Label(
                card,
                text=f"{item.category} / {item.detail} / {item.color_name}",
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(10, 4))

            tk.Label(
                card,
                text=f"특징: {item.feature}",
                font=("Arial", 11),
                bg="white",
                fg="#444444"
            ).pack(anchor="w", padx=12, pady=(0, 10))

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).pack(pady=12)