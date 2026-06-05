import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ui import style


class CoordinationUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []

        self.selected_items = {
            "top": None,
            "bottom": None,
            "outer": None,
            "shoes": None,
            "accessory": None
        }

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("코디해보기")
        self.image_refs = []

        self.selected_items = {
            "top": None,
            "bottom": None,
            "outer": None,
            "shoes": None,
            "accessory": None
        }

        outer_frame = tk.Frame(self.app.main_frame, bg=style.BG)
        outer_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer_frame, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.BG)

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
            text="직접 코디 만들기",
            font=(style.FONT, 20, "bold"),
            bg=style.BG,
            fg="#222222"
        ).pack(pady=(20, 8))

        tk.Label(
            body,
            text="상의와 하의는 필수이고, 아우터/신발/악세서리는 선택입니다.",
            font=(style.FONT, 10),
            bg=style.BG,
            fg=style.SUBTEXT,
            wraplength=350,
            justify="center"
        ).pack(pady=(0, 10))

        preview_area = tk.Frame(body, bg=style.BG)
        preview_area.pack(fill="x", padx=16, pady=8)

        select_area = tk.Frame(body, bg=style.BG)
        select_area.pack(fill="both", expand=True, padx=16, pady=8)

        category_map = [
            ("top", "상의", "상의"),
            ("bottom", "하의", "하의"),
            ("outer", "아우터", "아우터"),
            ("shoes", "신발", "신발"),
            ("accessory", "악세서리", "악세서리"),
        ]

        def get_clothes(category):
            return [
                cloth for cloth in self.app.clothes
                if getattr(cloth, "category", "") == category
            ]

        def refresh_preview():
            for widget in preview_area.winfo_children():
                widget.destroy()

            card = tk.Frame(preview_area, bg=style.CARD)
            card.pack(fill="x", pady=5)

            tk.Label(
                card,
                text="현재 선택한 코디",
                font=(style.FONT, 14, "bold"),
                bg=style.CARD,
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(12, 8))

            for key, title, _ in category_map:
                cloth = self.selected_items.get(key)
                self.draw_selected_item(card, title, cloth)

        def choose_item(key, cloth):
            if self.selected_items.get(key) == cloth:
                self.selected_items[key] = None
            else:
                self.selected_items[key] = cloth

            refresh_preview()
            refresh_select_area()

        def refresh_select_area():
            for widget in select_area.winfo_children():
                widget.destroy()

            for key, title, category in category_map:
                section = tk.Frame(select_area, bg=style.BG)
                section.pack(fill="x", pady=8)

                tk.Label(
                    section,
                    text=title,
                    font=(style.FONT, 15, "bold"),
                    bg=style.BG,
                    fg="#222222"
                ).pack(anchor="w", pady=(0, 5))

                clothes = get_clothes(category)

                if not clothes:
                    tk.Label(
                        section,
                        text=f"등록된 {title}가 없습니다.",
                        font=(style.FONT, 10),
                        bg=style.BG,
                        fg="#777777"
                    ).pack(anchor="w", padx=4, pady=5)
                    continue

                for cloth in clothes:
                    is_selected = self.selected_items.get(key) == cloth
                    self.draw_choice_card(section, key, cloth, is_selected, choose_item)

        def save_outfit():
            top = self.selected_items.get("top")
            bottom = self.selected_items.get("bottom")
            outer_item = self.selected_items.get("outer")
            shoes = self.selected_items.get("shoes")
            accessory = self.selected_items.get("accessory")

            if top is None or bottom is None:
                messagebox.showwarning(
                    "저장 불가",
                    "코디를 저장하려면 상의와 하의를 반드시 선택해야 합니다."
                )
                return

            user_id = "guest"

            if self.app.current_user:
                user_id = self.app.current_user.get("user_id", "guest")

            reason_parts = [
                f"{top.detail} 상의와 {bottom.detail} 하의를 조합해 기본 코디를 구성했습니다."
            ]

            if outer_item:
                reason_parts.append(f"아우터로 {outer_item.detail}를 더해 완성도를 높였습니다.")

            if shoes:
                reason_parts.append(f"신발은 {shoes.detail}을 선택해 전체 분위기를 맞췄습니다.")

            if accessory:
                reason_parts.append(f"악세서리로 {accessory.detail}를 더해 포인트를 주었습니다.")

            outfit = {
                "top": top,
                "bottom": bottom,
                "outer": outer_item,
                "shoes": shoes,
                "accessory": accessory,
                "reason": " ".join(reason_parts),
                "user_id": user_id
            }

            if not hasattr(self.app, "saved_outfits"):
                self.app.saved_outfits = []

            self.app.saved_outfits.append(outfit)

            messagebox.showinfo("저장 완료", "직접 만든 코디가 나의 코디에 저장되었습니다.")

        refresh_preview()
        refresh_select_area()

        action_row = tk.Frame(body, bg=style.BG)
        action_row.pack(pady=(12, 20))

        tk.Button(
            action_row,
            text="이 코디 저장하기",
            font=(style.FONT, 11, "bold"),
            bg=style.SUCCESS,
            fg="white",
            width=15,
            height=2,
            bd=0,
            command=save_outfit
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            action_row,
            text="나의 코디 확인",
            font=(style.FONT, 11, "bold"),
            bg=style.PRIMARY,
            fg="white",
            width=15,
            height=2,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_outfit_ui()]
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            body,
            text="홈으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            width=12,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
        ).pack(pady=(0, 15))

    def draw_selected_item(self, parent, title, cloth):
        row = tk.Frame(parent, bg=style.CARD)
        row.pack(fill="x", padx=12, pady=4)

        tk.Label(
            row,
            text=f"{title}:",
            font=(style.FONT, 10, "bold"),
            bg=style.CARD,
            fg="#222222",
            width=8,
            anchor="w"
        ).pack(side="left")

        if cloth is None:
            tk.Label(
                row,
                text="선택 안 함",
                font=(style.FONT, 10),
                bg=style.CARD,
                fg="#777777"
            ).pack(side="left")
            return

        if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
            try:
                img = Image.open(cloth.image_path).convert("RGB")
                img.thumbnail((45, 45))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                tk.Label(
                    row,
                    image=tk_img,
                    bg=style.CARD
                ).pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(
            row,
            text=f"{cloth.detail} / {cloth.color_name}",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            wraplength=220,
            justify="left"
        ).pack(side="left", fill="x", expand=True)

    def draw_choice_card(self, parent, key, cloth, is_selected, choose_callback):
        card = tk.Frame(
            parent,
            bg="#dff7e5" if is_selected else "white"
        )
        card.pack(fill="x", pady=5)

        content = tk.Frame(card, bg=card["bg"])
        content.pack(fill="x", padx=10, pady=8)

        if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
            try:
                img = Image.open(cloth.image_path).convert("RGB")
                img.thumbnail((65, 65))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                tk.Label(
                    content,
                    image=tk_img,
                    bg=card["bg"]
                ).pack(side="left", padx=(0, 10))
            except Exception:
                pass

        info = tk.Frame(content, bg=card["bg"])
        info.pack(side="left", fill="both", expand=True)

        tk.Label(
            info,
            text=f"{cloth.category} / {cloth.detail}",
            font=(style.FONT, 11, "bold"),
            bg=card["bg"],
            fg="#222222"
        ).pack(anchor="w")

        tk.Label(
            info,
            text=f"색상: {cloth.color_name}",
            font=(style.FONT, 9),
            bg=card["bg"],
            fg=style.MUTED_TEXT
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            info,
            text=f"특징: {cloth.feature}",
            font=(style.FONT, 9),
            bg=card["bg"],
            fg="#555555",
            wraplength=210,
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

        tk.Button(
            content,
            text="선택됨" if is_selected else "선택",
            font=(style.FONT, 9, "bold"),
            bg=style.SUCCESS if is_selected else "#2f80ff",
            fg="white",
            bd=0,
            width=7,
            command=lambda: choose_callback(key, cloth)
        ).pack(side="right", padx=(8, 0))
