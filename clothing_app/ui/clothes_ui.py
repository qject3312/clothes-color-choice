import os
import tkinter as tk
from PIL import Image, ImageTk


class ClothesUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("등록된 옷 확인")
        self.image_refs = []

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

        if not self.app.clothes:
            tk.Label(
                body,
                text="등록된 옷이 없습니다.",
                font=("Arial", 14),
                bg="#f4f6fb",
                fg="#666666"
            ).pack(pady=40)
        else:
            grouped = {
                "상의": [],
                "하의": [],
                "아우터": []
            }

            for cloth in self.app.clothes:
                if cloth.category in grouped:
                    grouped[cloth.category].append(cloth)

            for category in ["상의", "하의", "아우터"]:
                tk.Label(
                    body,
                    text=category,
                    font=("Arial", 15, "bold"),
                    bg="#f4f6fb",
                    fg="#222222"
                ).pack(anchor="w", padx=4, pady=(12, 4))

                if not grouped[category]:
                    tk.Label(
                        body,
                        text=f"등록된 {category}가 없습니다.",
                        font=("Arial", 10),
                        bg="#f4f6fb",
                        fg="#777777"
                    ).pack(anchor="w", padx=8, pady=(0, 8))
                    continue

                for cloth in grouped[category]:
                    self.create_cloth_card(body, cloth)

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).pack(pady=18)

    def create_cloth_card(self, parent, cloth):
        card = tk.Frame(parent, bg="white", bd=0)
        card.pack(fill="x", pady=7)

        top_area = tk.Frame(card, bg="white")
        top_area.pack(fill="x", padx=12, pady=(10, 5))

        if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
            try:
                img = Image.open(cloth.image_path).convert("RGB")
                img.thumbnail((80, 80))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                img_label = tk.Label(top_area, image=tk_img, bg="white")
                img_label.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        text_area = tk.Frame(top_area, bg="white")
        text_area.pack(side="left", fill="both", expand=True)

        tk.Label(
            text_area,
            text=f"{cloth.category} / {cloth.detail}",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w")

        tk.Label(
            text_area,
            text=f"특징: {cloth.feature}",
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            anchor="w",
            wraplength=250,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

        color_area = tk.Frame(card, bg="white")
        color_area.pack(fill="x", padx=12, pady=(5, 10))

        colors = getattr(cloth, "colors", None)
        if not colors:
            colors = [
                {
                    "rgb": cloth.rgb,
                    "hex": cloth.hex,
                    "name": cloth.color_name
                }
            ]

        for idx, color in enumerate(colors, start=1):
            row = tk.Frame(color_area, bg="white")
            row.pack(fill="x", pady=2)

            box = tk.Canvas(row, width=22, height=22, bg="white", highlightthickness=0)
            box.pack(side="left", padx=(0, 6))
            box.create_rectangle(2, 2, 20, 20, fill=color["hex"], outline="#999999")

            tk.Label(
                row,
                text=f"{idx}. {color['name']} / RGB{color['rgb']} / {color['hex']}",
                font=("Arial", 10),
                bg="white",
                fg="#444444"
            ).pack(side="left")