import tkinter as tk
from tkinter import messagebox

from logic.recommend_logic import get_temperature_recommendation


class TemperatureUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("온도 기반 추천")

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg="#f4f6fb")

        body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        def find_registered_items(category, recommended_details):
            result = []

            for cloth in self.app.clothes:
                if cloth.category != category:
                    continue

                if cloth.detail in recommended_details:
                    result.append(cloth)

            return result

        def add_recommend_section(title, category, recommended_details):
            section = tk.Frame(result_frame, bg="white")
            section.pack(fill="x", pady=8)

            tk.Label(
                section,
                text=title,
                font=("Arial", 13, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", padx=16, pady=(16, 8))

            registered_items = find_registered_items(category, recommended_details)

            tk.Label(
                section,
                text="추천되는 옷 종류: " + ", ".join(recommended_details) if recommended_details else "추천되는 옷 종류: 없음",
                font=("Arial", 10),
                bg="white",
                fg="#666666",
                wraplength=350,
                justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 8))

            if registered_items:
                tk.Label(
                    section,
                    text="내가 등록한 옷 중 추천 가능:",
                    font=("Arial", 10, "bold"),
                    bg="white",
                    fg="#2f5fbf"
                ).pack(anchor="w", padx=16, pady=(0, 6))

                for item in registered_items:
                    item_card = tk.Frame(section, bg="#f7f9ff")
                    item_card.pack(fill="x", padx=16, pady=4)

                    left = tk.Frame(item_card, bg="#f7f9ff")
                    left.pack(side="left", fill="both", expand=True, padx=10, pady=8)

                    tk.Label(
                        left,
                        text=f"{item.detail} / {item.color_name}",
                        font=("Arial", 11, "bold"),
                        bg="#f7f9ff",
                        fg="#222222"
                    ).pack(anchor="w")

                    tk.Label(
                        left,
                        text=f"특징: {item.feature}",
                        font=("Arial", 10),
                        bg="#f7f9ff",
                        fg="#444444",
                        wraplength=260,
                        justify="left"
                    ).pack(anchor="w", pady=(2, 0))

                    color_box = tk.Canvas(item_card, width=28, height=28, bg="#f7f9ff", highlightthickness=0)
                    color_box.pack(side="right", padx=10)
                    color_box.create_rectangle(4, 4, 24, 24, fill=item.hex, outline="#999999")
            else:
                tk.Label(
                    section,
                    text="아직 이 온도에 맞는 등록 옷이 없습니다. 위 추천 종류에 맞는 옷을 등록해 보세요.",
                    font=("Arial", 10),
                    bg="white",
                    fg="#c0392b",
                    wraplength=350,
                    justify="left"
                ).pack(anchor="w", padx=16, pady=(0, 14))

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
                bg="white",
                fg="#222222"
            ).pack(anchor="w", padx=16, pady=(16, 8))

            tk.Label(
                title_card,
                text=info["reason"],
                font=("Arial", 11),
                bg="white",
                fg="#444444",
                wraplength=350,
                justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 14))

            add_recommend_section("추천 상의", "상의", info["top"])
            add_recommend_section("추천 하의", "하의", info["bottom"])
            add_recommend_section("추천 아우터", "아우터", info["outer"])

            avoid_card = tk.Frame(result_frame, bg="white")
            avoid_card.pack(fill="x", pady=8)

            tk.Label(
                avoid_card,
                text="피하면 좋은 옷",
                font=("Arial", 13, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", padx=16, pady=(16, 8))

            tk.Label(
                avoid_card,
                text=info["avoid"],
                font=("Arial", 11),
                bg="white",
                fg="#c0392b",
                wraplength=350,
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
        ).pack(pady=15)