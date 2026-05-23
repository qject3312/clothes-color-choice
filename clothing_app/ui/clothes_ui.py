import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class ClothesUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []
        self.selected_category = "상의"
        self.selected_detail = "전체"

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("등록된 옷 확인")
        self.image_refs = []

        self.selected_category = "상의"
        self.selected_detail = "전체"

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        category_frame = tk.Frame(outer, bg="#f4f6fb")
        category_frame.pack(fill="x", pady=(0, 10))

        detail_frame = tk.Frame(outer, bg="#f4f6fb")
        detail_frame.pack(fill="x", pady=(0, 10))

        result_area = tk.Frame(outer, bg="#f4f6fb")
        result_area.pack(fill="both", expand=True)

        category_buttons = []
        detail_buttons = []

        def clear_buttons(buttons):
            for btn in buttons:
                btn.destroy()
            buttons.clear()

        def set_category(category):
            self.selected_category = category
            self.selected_detail = "전체"
            render_category_buttons()
            render_detail_buttons()
            render_clothes()

        def set_detail(detail):
            self.selected_detail = detail
            render_detail_buttons()
            render_clothes()

        def render_category_buttons():
            clear_buttons(category_buttons)

            for category in ["상의", "하의", "아우터", "신발", "악세서리"]:
                is_selected = category == self.selected_category

                btn = tk.Button(
                    category_frame,
                    text=category,
                    font=("Arial", 11, "bold"),
                    bg="#2f80ff" if is_selected else "#e1e6f0",
                    fg="white" if is_selected else "#222222",
                    bd=0,
                    width=9,
                    height=2,
                    command=lambda c=category: set_category(c)
                )
                btn.pack(side="left", padx=4)
                category_buttons.append(btn)

        def render_detail_buttons():
            clear_buttons(detail_buttons)

            detail_canvas = tk.Canvas(
                detail_frame,
                bg="#f4f6fb",
                height=48,
                highlightthickness=0
            )
            detail_canvas.pack(fill="x", expand=True)

            inner = tk.Frame(detail_canvas, bg="#f4f6fb")
            detail_canvas.create_window((0, 0), window=inner, anchor="nw")

            scrollbar = tk.Scrollbar(
                detail_frame,
                orient="horizontal",
                command=detail_canvas.xview
            )
            scrollbar.pack(fill="x")

            detail_canvas.configure(xscrollcommand=scrollbar.set)

            def update_scroll_region(event):
                detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))

            inner.bind("<Configure>", update_scroll_region)

            detail_buttons.append(detail_canvas)
            detail_buttons.append(scrollbar)

            options = ["전체"] + self.app.detail_options.get(self.selected_category, [])

            for detail in options:
                is_selected = detail == self.selected_detail

                btn = tk.Button(
                    inner,
                    text=detail,
                    font=("Arial", 10, "bold"),
                    bg="#47c95a" if is_selected else "white",
                    fg="white" if is_selected else "#222222",
                    bd=0,
                    padx=12,
                    pady=8,
                    command=lambda d=detail: set_detail(d)
                )
                btn.pack(side="left", padx=4, pady=5)
                detail_buttons.append(btn)

        def render_clothes():
            for widget in result_area.winfo_children():
                widget.destroy()

            canvas = tk.Canvas(result_area, bg="#f4f6fb", highlightthickness=0)
            scrollbar = tk.Scrollbar(result_area, orient="vertical", command=canvas.yview)
            body = tk.Frame(canvas, bg="#f4f6fb")

            body.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=body, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            filtered = []

            for cloth in self.app.clothes:
                if cloth.category != self.selected_category:
                    continue

                if self.selected_detail != "전체" and cloth.detail != self.selected_detail:
                    continue

                filtered.append(cloth)

            title_text = self.selected_category

            if self.selected_detail != "전체":
                title_text += f" / {self.selected_detail}"

            tk.Label(
                body,
                text=title_text,
                font=("Arial", 16, "bold"),
                bg="#f4f6fb",
                fg="#222222"
            ).pack(anchor="w", padx=4, pady=(8, 10))

            if not filtered:
                if self.selected_detail == "전체":
                    empty_text = f"등록된 {self.selected_category}가 없습니다."
                else:
                    empty_text = f"등록된 {self.selected_detail} 옷이 없습니다."

                tk.Label(
                    body,
                    text=empty_text,
                    font=("Arial", 13),
                    bg="#f4f6fb",
                    fg="#666666"
                ).pack(pady=40)

                tk.Button(
                    body,
                    text="홈으로",
                    font=("Arial", 11),
                    bg="#d9dee8",
                    width=12,
                    bd=0,
                    command=self.app.show_home
                ).pack(pady=18)
                return

            for cloth in filtered:
                self.create_cloth_card(body, cloth, render_clothes)

            tk.Button(
                body,
                text="홈으로",
                font=("Arial", 11),
                bg="#d9dee8",
                width=12,
                bd=0,
                command=self.app.show_home
            ).pack(pady=18)

        render_category_buttons()
        render_detail_buttons()
        render_clothes()

    def delete_cloth(self, cloth, refresh_callback):
        answer = messagebox.askyesno(
            "삭제 확인",
            f"{cloth.category} / {cloth.detail} 옷을 삭제할까요?"
        )

        if not answer:
            return

        if cloth in self.app.clothes:
            self.app.clothes.remove(cloth)

        messagebox.showinfo("삭제 완료", "등록된 옷을 삭제했습니다.")
        refresh_callback()

    def create_cloth_card(self, parent, cloth, refresh_callback):
        card = tk.Frame(parent, bg="white", bd=0)
        card.pack(fill="x", pady=7)

        top_area = tk.Frame(card, bg="white")
        top_area.pack(fill="x", padx=12, pady=(10, 5))

        if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
            try:
                img = Image.open(cloth.image_path).convert("RGB")
                img.thumbnail((90, 90))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                img_label = tk.Label(top_area, image=tk_img, bg="white")
                img_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print("옷 이미지 표시 실패:", e)

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
            wraplength=210,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

        delete_btn = tk.Button(
            top_area,
            text="삭제",
            font=("Arial", 10, "bold"),
            bg="#ff7675",
            fg="white",
            bd=0,
            width=6,
            height=2,
            command=lambda: self.delete_cloth(cloth, refresh_callback)
        )
        delete_btn.pack(side="right", padx=(8, 0))

        color_area = tk.Frame(card, bg="white")
        color_area.pack(fill="x", padx=12, pady=(5, 10))

        colors = getattr(cloth, "colors", None)

        if not colors:
            colors = [
                {
                    "rgb": getattr(cloth, "rgb", (0, 0, 0)),
                    "hex": getattr(cloth, "hex", "#cccccc"),
                    "name": getattr(cloth, "color_name", "미분석")
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