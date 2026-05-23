import os
import tkinter as tk
from PIL import Image, ImageTk


class OutfitUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("나의 코디 확인")
        self.image_refs = []

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg="#f4f6fb")

        body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")

        def resize_body(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_body)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(
            body,
            text="저장한 코디 목록",
            font=("Arial", 20, "bold"),
            bg="#f4f6fb",
            fg="#222222"
        ).pack(pady=(20, 10))

        if not getattr(self.app, "saved_outfits", []):
            tk.Label(
                body,
                text="아직 저장한 코디가 없습니다.\n사용자 맞춤 코디나 코디해보기에서 코디를 저장해 보세요.",
                font=("Arial", 12),
                bg="#f4f6fb",
                fg="#666666",
                justify="center",
                wraplength=330
            ).pack(pady=40)

            tk.Button(
                body,
                text="코디해보기",
                font=("Arial", 12, "bold"),
                bg="#2f80ff",
                fg="white",
                width=18,
                height=2,
                bd=0,
                command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_coordination_ui()]
            ).pack(pady=10)

            tk.Button(
                body,
                text="홈으로",
                font=("Arial", 11),
                bg="#d9dee8",
                width=12,
                bd=0,
                command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
            ).pack(pady=10)
            return

        for idx, outfit in enumerate(self.app.saved_outfits, start=1):
            self.draw_outfit_card(body, idx, outfit)

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
        ).pack(pady=20)

    def draw_outfit_card(self, parent, idx, outfit):
        card = tk.Frame(parent, bg="white")
        card.pack(fill="x", padx=16, pady=10)

        top = tk.Frame(card, bg="white")
        top.pack(fill="x", padx=12, pady=(12, 6))

        tk.Label(
            top,
            text=f"코디 {idx}",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#222222"
        ).pack(side="left")

        tk.Button(
            top,
            text="삭제",
            font=("Arial", 9, "bold"),
            bg="#ff7675",
            fg="white",
            bd=0,
            command=lambda: self.delete_outfit(outfit)
        ).pack(side="right")

        items_frame = tk.Frame(card, bg="white")
        items_frame.pack(fill="x", padx=12, pady=6)

        self.draw_item(items_frame, "상의", outfit.get("top"))
        self.draw_item(items_frame, "하의", outfit.get("bottom"))
        self.draw_item(items_frame, "아우터", outfit.get("outer"))
        self.draw_item(items_frame, "신발", outfit.get("shoes"))
        self.draw_item(items_frame, "악세서리", outfit.get("accessory"))

        tk.Label(
            card,
            text="추천/저장 이유",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=12, pady=(8, 3))

        tk.Label(
            card,
            text=outfit.get("reason", "저장 이유가 없습니다."),
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 12))

    def draw_item(self, parent, title, cloth):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=5)

        tk.Label(
            row,
            text=f"{title}:",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#222222",
            width=8,
            anchor="w"
        ).pack(side="left")

        if cloth is None:
            tk.Label(
                row,
                text="없음",
                font=("Arial", 10),
                bg="white",
                fg="#777777"
            ).pack(side="left")
            return

        if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
            try:
                img = Image.open(cloth.image_path).convert("RGB")
                img.thumbnail((55, 55))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                tk.Label(
                    row,
                    image=tk_img,
                    bg="white"
                ).pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(
            row,
            text=f"{cloth.detail} / {cloth.color_name}",
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            wraplength=210,
            justify="left"
        ).pack(side="left", fill="x", expand=True)

    def delete_outfit(self, outfit):
        if outfit in self.app.saved_outfits:
            self.app.saved_outfits.remove(outfit)

        self.show()