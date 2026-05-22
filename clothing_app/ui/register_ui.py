import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from api_client import add_clothing_to_backend, recommend_from_photo_backend, recommend_by_cloth_backend
import colorsys


from PIL import Image, ImageTk

from model.clothing import Clothing
from logic.color_logic import rgb_to_hex, rgb_to_name

class RegisterUI:
    def __init__(self, app):
        self.app = app

        self.photo_original_image = None
        self.photo_display_image = None
        self.photo_tk_image = None
        self.photo_scale = 1
        self.photo_offset_x = 0
        self.photo_offset_y = 0
        self.photo_selected_colors = []
        self.photo_selected_file_path = ""

    def show_register_options(self):
        self.app.clear_screen()
        self.app.create_top_bar("옷 등록하기")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True)

        center_frame = tk.Frame(body, bg="#f4f6fb")
        center_frame.place(relx=0.5, rely=0.38, anchor="center")

        tk.Button(
            center_frame,
            text="사진으로 등록하기",
            font=("Arial", 16, "bold"),
            bg="#5f6c86",
            fg="white",
            width=18,
            height=2,
            bd=0,
            command=self.show_photo_register
        ).pack(pady=18)

        tk.Button(
            center_frame,
            text="직접 등록하기",
            font=("Arial", 16, "bold"),
            bg="#2f80ff",
            fg="white",
            width=18,
            height=2,
            bd=0,
            command=self.show_direct_register
        ).pack(pady=18)

        tk.Button(
            body,
            text="뒤로가기",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=self.app.show_home
        ).place(relx=0.5, rely=0.78, anchor="center")

    def show_photo_register(self):
        self.app.clear_screen()
        self.app.create_top_bar("사진으로 옷 등록")

        self.photo_original_image = None
        self.photo_display_image = None
        self.photo_tk_image = None
        self.photo_scale = 1
        self.photo_offset_x = 0
        self.photo_offset_y = 0
        self.photo_selected_colors = []
        self.photo_selected_file_path = ""

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6fb")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        form_card = tk.Frame(scrollable_frame, bg="white")
        form_card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(
            form_card,
            text="사진을 불러온 뒤, 사진 위를 클릭해서 색을 선택하세요.",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#222222",
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            form_card,
            text="색은 최소 1개, 최대 5개까지 선택할 수 있습니다.",
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        ).pack(anchor="w", padx=18, pady=(0, 10))

        image_canvas = tk.Canvas(
            form_card,
            width=340,
            height=340,
            bg="#eef1f7",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        image_canvas.pack(pady=8)

        selected_color_frame = tk.Frame(form_card, bg="white")
        selected_color_frame.pack(fill="x", padx=18, pady=8)

        selected_color_text = tk.Label(
            selected_color_frame,
            text="선택된 색: 없음",
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            justify="left",
            wraplength=340
        )
        selected_color_text.pack(anchor="w")

        tk.Label(form_card, text="종류", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=18, pady=(15, 5))

        category_var = tk.StringVar(value="상의")
        category_box = ttk.Combobox(
            form_card,
            textvariable=category_var,
            state="readonly",
            values=["상의", "하의", "아우터"],
            font=("Arial", 11)
        )
        category_box.pack(fill="x", padx=18, pady=4)

        tk.Label(form_card, text="세부 종류", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=18, pady=(12, 5))

        detail_var = tk.StringVar()
        detail_box = ttk.Combobox(
            form_card,
            textvariable=detail_var,
            state="readonly",
            font=("Arial", 11)
        )
        detail_box.pack(fill="x", padx=18, pady=4)

        def update_detail_options(event=None):
            selected = category_var.get()
            options = self.app.detail_options.get(selected, [])
            detail_box["values"] = options
            if options:
                detail_box.set(options[0])

        category_box.bind("<<ComboboxSelected>>", update_detail_options)
        update_detail_options()

        tk.Label(form_card, text="특징", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=18, pady=(12, 5))

        feature_entry = tk.Entry(form_card, font=("Arial", 11), bd=1, relief="solid")
        feature_entry.pack(fill="x", padx=18, pady=4, ipady=5)
        feature_entry.insert(0, "예: 오버핏, 얇음, 캐주얼")

        def clear_placeholder(event):
            if feature_entry.get() == "예: 오버핏, 얇음, 캐주얼":
                feature_entry.delete(0, tk.END)

        feature_entry.bind("<FocusIn>", clear_placeholder)

        def refresh_selected_colors():
            for widget in selected_color_frame.winfo_children():
                widget.destroy()

            if not self.photo_selected_colors:
                tk.Label(
                    selected_color_frame,
                    text="선택된 색: 없음",
                    font=("Arial", 10),
                    bg="white",
                    fg="#444444"
                ).pack(anchor="w")
                return

            tk.Label(
                selected_color_frame,
                text=f"선택된 색 {len(self.photo_selected_colors)}개",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", pady=(0, 5))

            for idx, color in enumerate(self.photo_selected_colors, start=1):
                row = tk.Frame(selected_color_frame, bg="white")
                row.pack(fill="x", pady=2)

                box = tk.Canvas(row, width=24, height=24, bg="white", highlightthickness=0)
                box.pack(side="left", padx=(0, 8))
                box.create_rectangle(2, 2, 22, 22, fill=color["hex"], outline="#999999")

                tk.Label(
                    row,
                    text=f"{idx}. {color['name']} / RGB{color['rgb']} / {color['hex']}",
                    font=("Arial", 10),
                    bg="white",
                    fg="#444444"
                ).pack(side="left")

        def draw_image_on_canvas():
            image_canvas.delete("all")

            if self.photo_original_image is None:
                image_canvas.create_text(
                    170,
                    170,
                    text="사진을 선택하세요",
                    fill="#777777",
                    font=("Arial", 13, "bold")
                )
                return

            original_w, original_h = self.photo_original_image.size
            max_size = 330

            scale = min(max_size / original_w, max_size / original_h)
            display_w = int(original_w * scale)
            display_h = int(original_h * scale)

            self.photo_scale = scale
            self.photo_offset_x = (340 - display_w) // 2
            self.photo_offset_y = (340 - display_h) // 2

            self.photo_display_image = self.photo_original_image.resize((display_w, display_h))
            self.photo_tk_image = ImageTk.PhotoImage(self.photo_display_image)

            image_canvas.create_image(
                self.photo_offset_x,
                self.photo_offset_y,
                anchor="nw",
                image=self.photo_tk_image
            )

            for color in self.photo_selected_colors:
                if "display_pos" in color:
                    x, y = color["display_pos"]
                    image_canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline="white", width=2)
                    image_canvas.create_oval(x - 7, y - 7, x + 7, y + 7, outline="black", width=1)

        def select_image():
            file_path = filedialog.askopenfilename(
                title="옷 사진 선택",
                filetypes=[
                    ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                    ("All Files", "*.*")
                ]
            )

            if not file_path:
                return

            try:
                self.photo_original_image = Image.open(file_path).convert("RGB")
            except Exception:
                messagebox.showerror("오류", "이미지를 불러올 수 없습니다.")
                return

            self.photo_selected_file_path = file_path
            self.photo_selected_colors = []
            draw_image_on_canvas()
            refresh_selected_colors()

        def pick_color_from_image(event):
            if self.photo_original_image is None:
                messagebox.showwarning("사진 없음", "먼저 사진을 선택해 주세요.")
                return

            if len(self.photo_selected_colors) >= 5:
                messagebox.showinfo("선택 제한", "색은 최대 5개까지만 선택할 수 있습니다.")
                return

            x = event.x
            y = event.y

            display_w = int(self.photo_original_image.size[0] * self.photo_scale)
            display_h = int(self.photo_original_image.size[1] * self.photo_scale)

            if not (
                self.photo_offset_x <= x <= self.photo_offset_x + display_w
                and self.photo_offset_y <= y <= self.photo_offset_y + display_h
            ):
                return

            original_x = int((x - self.photo_offset_x) / self.photo_scale)
            original_y = int((y - self.photo_offset_y) / self.photo_scale)

            original_x = max(0, min(self.photo_original_image.size[0] - 1, original_x))
            original_y = max(0, min(self.photo_original_image.size[1] - 1, original_y))

            r, g, b = self.photo_original_image.getpixel((original_x, original_y))
            hex_code = rgb_to_hex(r, g, b)
            color_name = rgb_to_name(r, g, b)

            self.photo_selected_colors.append(
                {
                    "rgb": (r, g, b),
                    "hex": hex_code,
                    "name": color_name,
                    "display_pos": (x, y)
                }
            )

            draw_image_on_canvas()
            refresh_selected_colors()

        def reset_colors():
            self.photo_selected_colors = []
            draw_image_on_canvas()
            refresh_selected_colors()

        def save_photo_clothing():
            if self.photo_original_image is None or not self.photo_selected_file_path:
                messagebox.showwarning("사진 없음", "등록할 사진을 먼저 선택해 주세요.")
                return

            if not self.photo_selected_colors:
                messagebox.showwarning("색상 없음", "사진에서 색을 최소 1개 이상 선택해 주세요.")
                return

            feature_text = feature_entry.get().strip()
            if feature_text == "" or feature_text == "예: 오버핏, 얇음, 캐주얼":
                feature_text = "특징 없음"

            main_color = self.photo_selected_colors[0]

            colors_for_save = []
            for color in self.photo_selected_colors:
                colors_for_save.append(
                    {
                        "rgb": color["rgb"],
                        "hex": color["hex"],
                        "name": color["name"]
                    }
                )

            item = Clothing(
                category=category_var.get(),
                detail=detail_var.get(),
                feature=feature_text,
                rgb=main_color["rgb"],
                hex_code=main_color["hex"],
                color_name=main_color["name"],
                image_path=self.photo_selected_file_path,
                colors=colors_for_save
            )

            self.app.clothes.append(item)
            add_clothing_to_backend(item)
            result = recommend_by_cloth_backend(
                item.category,
                item.color_name,
                item.detail
            )
            print("추천 result =", result)
            messagebox.showinfo(
                "추천 결과",
                f"{result['base_color']} {result['base_detail']}에 어울리는 조합입니다.\n\n"
                f"추천 하의 색상: {', '.join(result['recommended_bottom_colors'])}\n"
                f"추천 신발 색상: {', '.join(result['recommended_shoes_colors'])}\n\n"
                f"이유: {result['reason']}"
            )

            messagebox.showinfo(
                "저장 완료",
                f"{item.category} / {item.detail} 옷이 저장되었습니다.\n대표 색상: {item.color_name} {item.hex}"
            )

            canvas.unbind_all("<MouseWheel>")
            self.app.show_home()

        image_canvas.bind("<Button-1>", pick_color_from_image)
        draw_image_on_canvas()
        refresh_selected_colors()

        button_row1 = tk.Frame(form_card, bg="white")
        button_row1.pack(pady=(12, 6))


        def recommend_by_photo():
            if not self.photo_selected_colors:
                messagebox.showwarning("색상 없음", "사진에서 색을 먼저 선택해 주세요.")
                return

            main_color = self.photo_selected_colors[0]

            result = recommend_from_photo_backend(
                color_name=main_color["name"],
                category=category_var.get(),
                target_category="하의"
            )

            recommended = ", ".join(result["recommended_colors"])
            avoid = ", ".join(result["avoid_colors"])

            messagebox.showinfo(
                "사진 기반 추천 결과",
                f"선택한 색상: {result['base_color']}\n\n"
                f"추천 대상: {result['target_category']}\n\n"
                f"추천 색상: {recommended}\n\n"
                f"피하면 좋은 색상: {avoid}\n\n"
                f"이유: {result['reason']}"
            )
        tk.Button(
            button_row1,
            text="사진 선택",
            font=("Arial", 11, "bold"),
            bg="#5f6c86",
            fg="white",
            width=12,
            height=2,
            bd=0,
            command=select_image
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_row1,
            text="색 초기화",
            font=("Arial", 11),
            bg="#d9dee8",
            fg="#222222",
            width=12,
            height=2,
            bd=0,
            command=reset_colors
        ).grid(row=0, column=1, padx=5)

        button_row2 = tk.Frame(form_card, bg="white")
        button_row2.pack(pady=(8, 18))

        tk.Button(
            button_row2,
            text="저장하기",
            font=("Arial", 12, "bold"),
            bg="#47c95a",
            fg="white",
            width=12,
            height=2,
            bd=0,
            command=save_photo_clothing
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_row2,
            text="뒤로가기",
            font=("Arial", 12),
            bg="#d9dee8",
            fg="#222222",
            width=12,
            height=2,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.show_register_options()]
        ).grid(row=0, column=1, padx=5)
        tk.Button(
            form_card,
            text="사진 색상으로 추천받기",
            font=("Arial", 12, "bold"),
            bg="#2f80ff",
            fg="white",
            height=2,
            bd=0,
            command=recommend_by_photo
        ).pack(fill="x", padx=18, pady=8)

    def show_direct_register(self):
        self.app.clear_screen()
        self.app.create_top_bar("직접 등록하기")

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6fb")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        form_card = tk.Frame(scrollable_frame, bg="white", bd=0)
        form_card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(form_card, text="종류", font=("Arial", 13, "bold"), bg="white", fg="#222222").pack(anchor="w", padx=20, pady=(18, 6))

        category_var = tk.StringVar(value="상의")
        category_box = ttk.Combobox(
            form_card,
            textvariable=category_var,
            state="readonly",
            values=["상의", "하의", "아우터"],
            font=("Arial", 12)
        )
        category_box.pack(fill="x", padx=20, pady=5)

        tk.Label(form_card, text="세부 종류", font=("Arial", 13, "bold"), bg="white", fg="#222222").pack(anchor="w", padx=20, pady=(16, 6))

        detail_var = tk.StringVar()
        detail_box = ttk.Combobox(
            form_card,
            textvariable=detail_var,
            state="readonly",
            font=("Arial", 12)
        )
        detail_box.pack(fill="x", padx=20, pady=5)

        def update_detail_options(event=None):
            selected = category_var.get()
            options = self.app.detail_options.get(selected, [])
            detail_box["values"] = options
            if options:
                detail_box.set(options[0])

        category_box.bind("<<ComboboxSelected>>", update_detail_options)
        update_detail_options()

        tk.Label(form_card, text="특징", font=("Arial", 13, "bold"), bg="white", fg="#222222").pack(anchor="w", padx=20, pady=(16, 6))

        feature_entry = tk.Entry(form_card, font=("Arial", 12), bd=1, relief="solid")
        feature_entry.pack(fill="x", padx=20, pady=5, ipady=6)
        feature_entry.insert(0, "예: 오버핏, 얇음, 캐주얼")

        def clear_placeholder(event):
            if feature_entry.get() == "예: 오버핏, 얇음, 캐주얼":
                feature_entry.delete(0, tk.END)

        feature_entry.bind("<FocusIn>", clear_placeholder)

        tk.Label(
            form_card,
            text="색상 선택",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=20, pady=(16, 6))

        picker_info = tk.Label(
            form_card,
            text="위 막대에서 기본 색을 고르고, 아래 정사각형 안에서 드래그해 원하는 색을 선택하세요.",
            font=("Arial", 10),
            bg="white",
            fg="#666666",
            justify="left",
            wraplength=340
        )
        picker_info.pack(anchor="w", padx=20, pady=(0, 8))

        picker_frame = tk.Frame(form_card, bg="white")
        picker_frame.pack(pady=4)

        hue_width = 240
        hue_height = 20
        color_canvas_size = 180

        hue_canvas = tk.Canvas(
            picker_frame,
            width=hue_width,
            height=hue_height,
            highlightthickness=1,
            highlightbackground="#cccccc",
            bg="white"
        )
        hue_canvas.pack(pady=(0, 10))

        color_canvas = tk.Canvas(
            picker_frame,
            width=color_canvas_size,
            height=color_canvas_size,
            highlightthickness=1,
            highlightbackground="#cccccc",
            bg="white"
        )
        color_canvas.pack()

        selected_preview_row = tk.Frame(form_card, bg="white")
        selected_preview_row.pack(pady=12)

        color_preview = tk.Canvas(selected_preview_row, width=70, height=45, bg="white", highlightthickness=0)
        color_preview.pack(side="left", padx=(0, 10))
        preview_rect = color_preview.create_rectangle(8, 8, 62, 38, fill=self.app.selected_hex, outline="#bbbbbb")

        preview_text = tk.Label(
            selected_preview_row,
            text="",
            font=("Arial", 11),
            bg="white",
            fg="#444444",
            justify="left"
        )
        preview_text.pack(side="left")

        hue_indicator = None
        color_indicator = None
        hue_image = None
        color_image = None

        def make_hue_bar():
            nonlocal hue_image
            img = tk.PhotoImage(width=hue_width, height=hue_height)

            for x in range(hue_width):
                h = x / hue_width
                r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
                hex_color = rgb_to_hex(r * 255, g * 255, b * 255)
                img.put(hex_color, to=(x, 0, x + 1, hue_height))

            hue_canvas.delete("all")
            hue_canvas.create_image(0, 0, anchor="nw", image=img)
            hue_image = img

        def make_color_square():
            nonlocal color_image, color_indicator
            size = color_canvas_size
            img = tk.PhotoImage(width=size, height=size)

            for y in range(size):
                v = 1 - (y / (size - 1))
                row_colors = []
                for x in range(size):
                    s = x / (size - 1)
                    r, g, b = colorsys.hsv_to_rgb(self.app.current_hue / 360, s, v)
                    row_colors.append(rgb_to_hex(r * 255, g * 255, b * 255))
                img.put("{" + " ".join(row_colors) + "}", to=(0, y))

            color_canvas.delete("all")
            color_canvas.create_image(0, 0, anchor="nw", image=img)
            color_image = img
            color_indicator = color_canvas.create_oval(0, 0, 10, 10, outline="white", width=2)

        def update_preview(rgb):
            self.app.selected_rgb = tuple(map(int, rgb))
            self.app.selected_hex = rgb_to_hex(*self.app.selected_rgb)
            color_name = rgb_to_name(*self.app.selected_rgb)
            color_preview.itemconfig(preview_rect, fill=self.app.selected_hex)
            preview_text.config(text=f"{color_name}\nRGB{self.app.selected_rgb}\n{self.app.selected_hex}")

        def move_hue_indicator(x):
            nonlocal hue_indicator
            x = max(0, min(hue_width - 1, x))
            if hue_indicator is None:
                hue_indicator = hue_canvas.create_line(x, 0, x, hue_height, fill="white", width=3)
            else:
                hue_canvas.coords(hue_indicator, x, 0, x, hue_height)

        def move_color_indicator(x, y):
            x = max(0, min(color_canvas_size - 1, x))
            y = max(0, min(color_canvas_size - 1, y))
            color_canvas.coords(color_indicator, x - 5, y - 5, x + 5, y + 5)

        def on_hue_pick(event):
            self.app.current_hue = (max(0, min(hue_width - 1, event.x)) / (hue_width - 1)) * 360
            move_hue_indicator(event.x)
            make_color_square()

        def on_color_pick(event):
            x = max(0, min(color_canvas_size - 1, event.x))
            y = max(0, min(color_canvas_size - 1, event.y))

            s = x / (color_canvas_size - 1)
            v = 1 - (y / (color_canvas_size - 1))
            r, g, b = colorsys.hsv_to_rgb(self.app.current_hue / 360, s, v)
            rgb = (int(r * 255), int(g * 255), int(b * 255))

            move_color_indicator(x, y)
            update_preview(rgb)

        make_hue_bar()
        make_color_square()
        move_hue_indicator(140)
        move_color_indicator(90, 55)
        update_preview(self.app.selected_rgb)

        hue_canvas.bind("<Button-1>", on_hue_pick)
        hue_canvas.bind("<B1-Motion>", on_hue_pick)
        color_canvas.bind("<Button-1>", on_color_pick)
        color_canvas.bind("<B1-Motion>", on_color_pick)

        button_frame = tk.Frame(form_card, bg="white")
        button_frame.pack(pady=(18, 20))

        def save_clothing():
            feature_text = feature_entry.get().strip()
            if feature_text == "" or feature_text == "예: 오버핏, 얇음, 캐주얼":
                feature_text = "특징 없음"

            r, g, b = self.app.selected_rgb
            color_hex = self.app.selected_hex
            color_name = rgb_to_name(r, g, b)

            item = Clothing(
                category=category_var.get(),
                detail=detail_var.get(),
                feature=feature_text,
                rgb=(r, g, b),
                hex_code=color_hex,
                color_name=color_name
            )

            self.app.clothes.append(item)
            add_clothing_to_backend(item)

            result = recommend_by_cloth_backend(
                item.category,
                item.color_name,
                item.detail
            )

            messagebox.showinfo(
                "추천 결과",
                f"{result['base_color']} {result['base_detail']}에 어울리는 조합입니다.\n\n"
                f"추천 하의 색상: {', '.join(result['recommended_bottom_colors'])}\n"
                f"추천 신발 색상: {', '.join(result['recommended_shoes_colors'])}\n\n"
                f"이유: {result['reason']}"
            )

            messagebox.showinfo(
                "저장 완료",
                f"{item.category} / {item.detail} 옷이 저장되었습니다.\n선택 색상: {item.color_name} RGB{item.rgb}"
            )
            canvas.unbind_all("<MouseWheel>")
            self.app.show_home()

        tk.Button(
            button_frame,
            text="저장하기",
            font=("Arial", 12, "bold"),
            bg="#47c95a",
            fg="white",
            width=12,
            height=2,
            bd=0,
            command=save_clothing
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            button_frame,
            text="뒤로가기",
            font=("Arial", 12),
            bg="#d9dee8",
            fg="#222222",
            width=12,
            height=2,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.show_register_options()]
        ).grid(row=0, column=1, padx=8)