import tkinter as tk
from tkinter import messagebox
from logic.recommend_logic import get_temperature_recommendation


class TemperatureUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("온도 기반 추천")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(body, bg="white")
        card.pack(fill="x", pady=10)

        tk.Label(
            card,
            text="현재 온도 입력",
            font=("Arial", 15, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=16, pady=(16, 8))

        tk.Label(
            card,
            text="예: 27",
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        ).pack(anchor="w", padx=16)

        temp_var = tk.StringVar()

        temp_entry = tk.Entry(card, textvariable=temp_var, font=("Arial", 13))
        temp_entry.pack(fill="x", padx=16, pady=12, ipady=6)

        result_frame = tk.Frame(body, bg="#f4f6fb")
        result_frame.pack(fill="both", expand=True)

        def clear_result():
            for widget in result_frame.winfo_children():
                widget.destroy()

        def show_result():
            clear_result()

            try:
                temp = float(temp_var.get())
            except ValueError:
                messagebox.showerror("입력 오류", "온도는 숫자로 입력해야 합니다.")
                return

            info = get_temperature_recommendation(temp)

            title_card = tk.Frame(result_frame, bg="white")
            title_card.pack(fill="x", pady=8)

            tk.Label(
                title_card,
                text=f"{temp}°C 추천 결과",
                font=("Arial", 16, "bold"),
                bg="white"
            ).pack(anchor="w", padx=16, pady=(16, 8))

            tk.Label(
                title_card,
                text=info["reason"],
                font=("Arial", 11),
                bg="white",
                fg="#444444",
                wraplength=360,
                justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 16))

            def add_section(title, values):
                section = tk.Frame(result_frame, bg="white")
                section.pack(fill="x", pady=8)

                tk.Label(
                    section,
                    text=title,
                    font=("Arial", 13, "bold"),
                    bg="white"
                ).pack(anchor="w", padx=16, pady=(16, 10))

                if values:
                    row = tk.Frame(section, bg="white")
                    row.pack(fill="x", padx=12, pady=(0, 12))
                    for v in values:
                        tk.Label(
                            row,
                            text=v,
                            font=("Arial", 10, "bold"),
                            bg="#eef3ff",
                            fg="#2f5fbf",
                            padx=10,
                            pady=6
                        ).pack(side="left", padx=4)
                else:
                    tk.Label(
                        section,
                        text="추천 겉옷 없음",
                        font=("Arial", 11),
                        bg="white",
                        fg="#666666"
                    ).pack(anchor="w", padx=16, pady=(0, 12))

            add_section("추천 상의", info["top"])
            add_section("추천 하의", info["bottom"])
            add_section("추천 아우터", info["outer"])

            avoid_card = tk.Frame(result_frame, bg="white")
            avoid_card.pack(fill="x", pady=8)

            tk.Label(
                avoid_card,
                text="피하면 좋은 옷",
                font=("Arial", 13, "bold"),
                bg="white"
            ).pack(anchor="w", padx=16, pady=(16, 8))

            tk.Label(
                avoid_card,
                text=info["avoid"],
                font=("Arial", 11),
                bg="white",
                fg="#c0392b",
                wraplength=360,
                justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 16))

        tk.Button(
            card,
            text="추천 보기",
            font=("Arial", 12, "bold"),
            bg="#2f80ff",
            fg="white",
            width=12,
            height=2,
            bd=0,
            command=show_result
        ).pack(pady=(0, 16))

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).pack(pady=12)