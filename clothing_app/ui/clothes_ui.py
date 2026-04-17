import tkinter as tk


class ClothesUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("등록된 옷 확인")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True, padx=15, pady=15)

        if not self.app.clothes:
            tk.Label(
                body,
                text="등록된 옷이 없습니다.",
                font=("Arial", 14),
                bg="#f4f6fb",
                fg="#666666"
            ).pack(pady=40)
        else:
            for cloth in self.app.clothes:
                card = tk.Frame(body, bg="white", bd=0)
                card.pack(fill="x", pady=8)

                top_line = tk.Frame(card, bg="white")
                top_line.pack(fill="x", padx=12, pady=(10, 5))

                tk.Label(
                    top_line,
                    text=f"{cloth.category} / {cloth.detail}",
                    font=("Arial", 13, "bold"),
                    bg="white",
                    fg="#222222"
                ).pack(side="left")

                color_box = tk.Canvas(top_line, width=24, height=24, bg="white", highlightthickness=0)
                color_box.pack(side="right")
                color_box.create_rectangle(2, 2, 22, 22, fill=cloth.hex, outline="#bbbbbb")

                tk.Label(
                    card,
                    text=f"특징: {cloth.feature}",
                    font=("Arial", 11),
                    bg="white",
                    fg="#444444",
                    anchor="w"
                ).pack(fill="x", padx=12, pady=2)

                tk.Label(
                    card,
                    text=f"색상명: {cloth.color_name} / RGB{cloth.rgb}",
                    font=("Arial", 11),
                    bg="white",
                    fg="#444444",
                    anchor="w"
                ).pack(fill="x", padx=12, pady=(0, 10))

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).pack(pady=15)