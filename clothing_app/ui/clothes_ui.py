import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from app_paths import resolve_existing_path
from api_client import delete_clothing_backend, update_clothing_backend
from ui import style


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

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        category_frame = tk.Frame(outer, bg=style.BG)
        category_frame.pack(fill="x", pady=(0, 10))

        detail_frame = tk.Frame(outer, bg=style.BG)
        detail_frame.pack(fill="x", pady=(0, 10))

        result_area = tk.Frame(outer, bg=style.BG)
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

            # 카테고리 버튼도 세부 분류 버튼처럼 가로 스크롤/드래그가 가능하게 구성합니다.
            # 창 폭이 좁을 때 오른쪽의 악세서리 버튼이 잘리는 문제를 방지합니다.
            category_canvas = tk.Canvas(
                category_frame,
                bg=style.BG,
                height=58,
                highlightthickness=0
            )
            category_canvas.pack(fill="x", expand=True)

            inner = tk.Frame(category_canvas, bg=style.BG)
            category_canvas.create_window((0, 0), window=inner, anchor="nw")

            scrollbar = tk.Scrollbar(
                category_frame,
                orient="horizontal",
                command=category_canvas.xview
            )
            scrollbar.pack(fill="x")

            category_canvas.configure(xscrollcommand=scrollbar.set)
            style.enable_canvas_drag(category_canvas, orient="horizontal", bind_children=inner)

            def update_scroll_region(event=None):
                category_canvas.configure(scrollregion=category_canvas.bbox("all"))

            inner.bind("<Configure>", update_scroll_region)

            category_buttons.append(category_canvas)
            category_buttons.append(scrollbar)

            for category in ["상의", "하의", "아우터", "신발", "악세서리"]:
                is_selected = category == self.selected_category

                btn = tk.Button(
                    inner,
                    text=category,
                    font=(style.FONT, 11, "bold"),
                    bg=style.PRIMARY if is_selected else "#e1e6f0",
                    fg="white" if is_selected else "#222222",
                    bd=0,
                    width=9,
                    height=2,
                    command=lambda c=category: set_category(c)
                )
                btn.pack(side="left", padx=4, pady=5)
                category_buttons.append(btn)

        def render_detail_buttons():
            clear_buttons(detail_buttons)

            detail_canvas = tk.Canvas(
                detail_frame,
                bg=style.BG,
                height=48,
                highlightthickness=0
            )
            detail_canvas.pack(fill="x", expand=True)

            inner = tk.Frame(detail_canvas, bg=style.BG)
            detail_canvas.create_window((0, 0), window=inner, anchor="nw")

            scrollbar = tk.Scrollbar(
                detail_frame,
                orient="horizontal",
                command=detail_canvas.xview
            )
            scrollbar.pack(fill="x")

            detail_canvas.configure(xscrollcommand=scrollbar.set)
            style.enable_canvas_drag(detail_canvas, orient="horizontal")

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
                    font=(style.FONT, 10, "bold"),
                    bg=style.SUCCESS if is_selected else "white",
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

            canvas = tk.Canvas(result_area, bg=style.BG, highlightthickness=0)
            scrollbar = tk.Scrollbar(result_area, orient="vertical", command=canvas.yview)
            body = tk.Frame(canvas, bg=style.BG)

            body.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")

            def resize_body(event):
                # 카드가 실제 화면 폭보다 넓어지지 않게 맞춰서 오른쪽 버튼이 잘리지 않도록 합니다.
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", resize_body)
            canvas.configure(yscrollcommand=scrollbar.set)
            style.enable_canvas_drag(canvas, bind_children=body)

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
                font=(style.FONT, 16, "bold"),
                bg=style.BG,
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
                    font=(style.FONT, 13),
                    bg=style.BG,
                    fg=style.SUBTEXT
                ).pack(pady=40)

                tk.Button(
                    body,
                    text="홈으로",
                    font=(style.FONT, 11),
                    bg=style.MUTED,
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
                font=(style.FONT, 11),
                bg=style.MUTED,
                width=12,
                bd=0,
                command=self.app.show_home
            ).pack(pady=18)

        render_category_buttons()
        render_detail_buttons()
        render_clothes()


    def edit_cloth(self, cloth, refresh_callback):
        edit_win = tk.Toplevel(self.app.root)
        edit_win.title("옷 정보 수정")
        edit_win.geometry("360x430")
        edit_win.configure(bg=style.CARD)
        edit_win.resizable(True, True)

        tk.Label(edit_win, text="옷 정보 수정", font=(style.FONT, 16, "bold"), bg=style.CARD, fg=style.TEXT).pack(pady=(18, 10))

        # 옷 정보 수정창도 스크롤/드래그가 가능하게 구성합니다.
        # 창을 작게 열거나 macOS에서 콤보박스 높이가 달라져도 아래 입력칸/버튼이 잘리지 않습니다.
        outer = tk.Frame(edit_win, bg=style.CARD)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=style.CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.CARD)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")

        def resize_body(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_body)
        canvas.configure(yscrollcommand=scrollbar.set)
        style.enable_canvas_drag(canvas, bind_children=body)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def label(text):
            tk.Label(body, text=text, font=(style.FONT, 10, "bold"), bg=style.CARD, fg=style.TEXT).pack(anchor="w", padx=22, pady=(10, 4))

        label("종류")
        category_var = tk.StringVar(value=cloth.category)
        category_box = ttk.Combobox(body, textvariable=category_var, state="readonly", values=["상의", "하의", "아우터", "신발", "악세서리"], font=(style.FONT, 11))
        category_box.pack(fill="x", padx=22, ipady=4)

        label("세부 종류")
        detail_var = tk.StringVar(value=cloth.detail)
        detail_box = ttk.Combobox(body, textvariable=detail_var, state="readonly", font=(style.FONT, 11))
        detail_box.pack(fill="x", padx=22, ipady=4)

        def update_details(event=None):
            opts = self.app.detail_options.get(category_var.get(), [])
            detail_box["values"] = opts
            if detail_var.get() not in opts and opts:
                detail_var.set(opts[0])

        category_box.bind("<<ComboboxSelected>>", update_details)
        update_details()

        label("색상 이름")
        color_entry = tk.Entry(body, font=(style.FONT, 11), bd=0, highlightthickness=1, highlightbackground=style.CARD_BORDER, highlightcolor=style.PRIMARY)
        color_entry.pack(fill="x", padx=22, ipady=6)
        color_entry.insert(0, getattr(cloth, "color_name", ""))

        label("색상 코드")
        hex_entry = tk.Entry(body, font=(style.FONT, 11), bd=0, highlightthickness=1, highlightbackground=style.CARD_BORDER, highlightcolor=style.PRIMARY)
        hex_entry.pack(fill="x", padx=22, ipady=6)
        hex_entry.insert(0, getattr(cloth, "hex", "#cccccc"))

        label("특징/메모")
        feature_entry = tk.Entry(body, font=(style.FONT, 11), bd=0, highlightthickness=1, highlightbackground=style.CARD_BORDER, highlightcolor=style.PRIMARY)
        feature_entry.pack(fill="x", padx=22, ipady=6)
        feature_entry.insert(0, getattr(cloth, "feature", ""))

        def save_edit():
            cloth.category = category_var.get()
            cloth.detail = detail_var.get()
            cloth.color_name = color_entry.get().strip() or "미분석"
            cloth.hex = hex_entry.get().strip() or "#cccccc"
            cloth.feature = feature_entry.get().strip() or "특징 없음"
            if getattr(cloth, "colors", None):
                cloth.colors[0]["name"] = cloth.color_name
                cloth.colors[0]["hex"] = cloth.hex
            if getattr(cloth, "id", None) is not None:
                result = update_clothing_backend(cloth.id, cloth, self.app.get_current_user_id())
                if isinstance(result, dict) and ("error" in result or "detail" in result):
                    messagebox.showwarning("서버 수정 실패", "화면에는 반영했지만 서버 저장은 실패했습니다.")
            messagebox.showinfo("수정 완료", "옷 정보가 수정되었습니다.")
            edit_win.destroy()
            refresh_callback()

        style.button(body, "수정 저장", save_edit, bg=style.PRIMARY, padx=22, pady=(18, 5))
        style.ghost_button(body, "취소", edit_win.destroy, padx=22, pady=(5, 18))

    def delete_cloth(self, cloth, refresh_callback):
        answer = messagebox.askyesno(
            "삭제 확인",
            f"{cloth.category} / {cloth.detail} 옷을 삭제할까요?"
        )

        if not answer:
            return

        if getattr(cloth, "id", None) is not None:
            result = delete_clothing_backend(cloth.id, self.app.get_current_user_id())
            if isinstance(result, dict) and ("error" in result or "detail" in result):
                messagebox.showwarning("서버 삭제 실패", "서버에서 삭제하지 못했습니다. 백엔드 서버를 확인해 주세요.")
                return

        if cloth in self.app.clothes:
            self.app.clothes.remove(cloth)

        messagebox.showinfo("삭제 완료", "등록된 옷을 삭제했습니다.")
        refresh_callback()

    def create_cloth_card(self, parent, cloth, refresh_callback):
        card = tk.Frame(parent, bg=style.CARD, bd=0)
        card.pack(fill="x", pady=7)

        top_area = tk.Frame(card, bg=style.CARD)
        top_area.pack(fill="x", padx=12, pady=(10, 5))

        if getattr(cloth, "image_path", "") and os.path.exists(resolve_existing_path(cloth.image_path)):
            try:
                img = Image.open(resolve_existing_path(cloth.image_path)).convert("RGB")
                img.thumbnail((90, 90))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                img_label = tk.Label(top_area, image=tk_img, bg=style.CARD)
                img_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print("옷 이미지 표시 실패:", e)

        button_area = tk.Frame(top_area, bg=style.CARD)
        button_area.pack(side="right", padx=(8, 0), anchor="n")

        edit_btn = tk.Button(
            button_area,
            text="수정",
            font=(style.FONT, 9, "bold"),
            bg=style.PRIMARY,
            fg="white",
            bd=0,
            width=5,
            height=2,
            command=lambda: self.edit_cloth(cloth, refresh_callback)
        )
        edit_btn.pack(side="right", padx=(4, 0))

        delete_btn = tk.Button(
            button_area,
            text="삭제",
            font=(style.FONT, 9, "bold"),
            bg=style.DANGER,
            fg="white",
            bd=0,
            width=5,
            height=2,
            command=lambda: self.delete_cloth(cloth, refresh_callback)
        )
        delete_btn.pack(side="right", padx=(4, 0))

        text_area = tk.Frame(top_area, bg=style.CARD)
        text_area.pack(side="left", fill="both", expand=True)

        tk.Label(
            text_area,
            text=f"{cloth.category} / {cloth.detail}",
            font=(style.FONT, 12, "bold"),
            bg=style.CARD,
            fg="#222222",
            wraplength=170,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            text_area,
            text=f"특징: {cloth.feature}",
            font=(style.FONT, 9),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            anchor="w",
            wraplength=165,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

        color_area = tk.Frame(card, bg=style.CARD)
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
            row = tk.Frame(color_area, bg=style.CARD)
            row.pack(fill="x", pady=2)

            box = tk.Canvas(row, width=22, height=22, bg=style.CARD, highlightthickness=0)
            box.pack(side="left", padx=(0, 6))
            box.create_rectangle(2, 2, 20, 20, fill=color["hex"], outline="#999999")

            tk.Label(
                row,
                text=f"{idx}. {color['name']} / RGB{color['rgb']} / {color['hex']}",
                font=(style.FONT, 9),
                bg=style.CARD,
                fg=style.MUTED_TEXT,
                wraplength=360,
                justify="left"
            ).pack(side="left", fill="x", expand=True)
