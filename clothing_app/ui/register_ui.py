import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from api_client import add_clothing_to_backend, recommend_from_photo_backend
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
        center_frame.place(relx=0.5, rely=0.42, anchor="center")

        tk.Button(
            center_frame,
            text="사진으로 등록하기",
            font=("Arial", 16, "bold"),
            bg="#2f80ff",
            fg="white",
            width=18,
            height=2,
            bd=0,
            command=self.show_photo_register
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

        selected_features = {
            "fit": "",
            "thickness": "",
            "mood": "",
            "season": ""
        }

        memo_var = tk.StringVar(value="예: 데일리용, 학교 갈 때, 중요한 날")

        feature_options = {
            "상의": {
                "fit": ["오버핏", "정핏", "슬림핏"],
                "thickness": ["얇음", "보통", "두꺼움"],
                "mood": ["캐주얼", "댄디", "미니멀", "스트릿", "포멀"],
                "season": ["봄가을", "여름", "겨울"]
            },
            "하의": {
                "fit": ["와이드", "일자핏", "슬림핏", "스키니", "조거핏"],
                "thickness": ["얇음", "보통", "두꺼움"],
                "mood": ["캐주얼", "댄디", "스트릿", "포멀"],
                "season": ["봄가을", "여름", "겨울"]
            },
            "아우터": {
                "fit": ["오버핏", "정핏", "크롭", "롱기장"],
                "thickness": ["얇음", "보통", "두꺼움"],
                "mood": ["캐주얼", "댄디", "미니멀", "스트릿", "포멀"],
                "season": ["봄가을", "겨울"]
            },
            "신발": {
                "fit": ["낮은 굽", "높은 굽", "발볼 넓음", "발볼 보통"],
                "thickness": ["가벼움", "보통", "두꺼움"],
                "mood": ["캐주얼", "댄디", "스트릿", "스포티", "포멀"],
                "season": ["봄가을", "여름", "겨울"]
            },
            "악세서리": {
                "fit": ["작은 사이즈", "보통 사이즈", "큰 사이즈"],
                "thickness": ["얇음", "보통", "두꺼움"],
                "mood": ["캐주얼", "댄디", "미니멀", "스트릿", "포멀", "러블리"],
                "season": ["사계절", "봄가을", "여름", "겨울"]
            }
        }

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6fb")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def resize_body(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_body)
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
        ).pack(anchor="w", padx=18, pady=(15, 6))

        tk.Label(
            form_card,
            text="색은 최소 1개, 최대 5개까지 선택할 수 있습니다.",
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        ).pack(anchor="w", padx=18, pady=(0, 8))

        image_canvas = tk.Canvas(
            form_card,
            width=260,
            height=260,
            bg="#eef1f7",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        image_canvas.pack(pady=(4, 6))

        selected_color_frame = tk.Frame(form_card, bg="white")
        selected_color_frame.pack(fill="x", padx=18, pady=(4, 6))

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
            ).pack(anchor="w", pady=(0, 4))

            for idx, color in enumerate(self.photo_selected_colors, start=1):
                row = tk.Frame(selected_color_frame, bg="white")
                row.pack(fill="x", pady=1)

                box = tk.Canvas(row, width=22, height=22, bg="white", highlightthickness=0)
                box.pack(side="left", padx=(0, 8))
                box.create_rectangle(2, 2, 20, 20, fill=color["hex"], outline="#999999")

                tk.Label(
                    row,
                    text=f"{idx}. {color['name']} / RGB{color['rgb']} / {color['hex']}",
                    font=("Arial", 9),
                    bg="white",
                    fg="#444444"
                ).pack(side="left")

        def draw_image_on_canvas():
            image_canvas.delete("all")

            if self.photo_original_image is None:
                image_canvas.create_text(
                    130,
                    130,
                    text="사진을 선택하세요",
                    fill="#777777",
                    font=("Arial", 13, "bold")
                )
                return

            original_w, original_h = self.photo_original_image.size
            max_size = 250

            scale = min(max_size / original_w, max_size / original_h)
            display_w = int(original_w * scale)
            display_h = int(original_h * scale)

            self.photo_scale = scale
            self.photo_offset_x = (260 - display_w) // 2
            self.photo_offset_y = (260 - display_h) // 2

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

        def reset_colors():
            self.photo_selected_colors = []
            draw_image_on_canvas()
            refresh_selected_colors()

        def get_average_color(original_x, original_y):
            pixels = []

            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    px = original_x + dx
                    py = original_y + dy

                    if (
                        0 <= px < self.photo_original_image.size[0]
                        and 0 <= py < self.photo_original_image.size[1]
                    ):
                        pixels.append(self.photo_original_image.getpixel((px, py)))

            r = sum(p[0] for p in pixels) // len(pixels)
            g = sum(p[1] for p in pixels) // len(pixels)
            b = sum(p[2] for p in pixels) // len(pixels)

            return r, g, b

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

            r, g, b = get_average_color(original_x, original_y)
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

        image_canvas.bind("<Button-1>", pick_color_from_image)
        draw_image_on_canvas()
        refresh_selected_colors()

        def make_feature_text():
            parts = []

            if selected_features["fit"]:
                parts.append(f"핏: {selected_features['fit']}")

            if selected_features["thickness"]:
                parts.append(f"두께: {selected_features['thickness']}")

            if selected_features["mood"]:
                parts.append(f"무드: {selected_features['mood']}")

            if selected_features["season"]:
                parts.append(f"계절감: {selected_features['season']}")

            memo = memo_var.get().strip()

            if memo and memo != "예: 데일리용, 학교 갈 때, 중요한 날":
                parts.append(f"메모: {memo}")

            if not parts:
                return "특징 없음"

            return " / ".join(parts)

        def save_photo_clothing():
            if self.photo_original_image is None or not self.photo_selected_file_path:
                messagebox.showwarning("사진 없음", "등록할 사진을 먼저 선택해 주세요.")
                return

            if not self.photo_selected_colors:
                messagebox.showwarning("색상 없음", "사진에서 색을 최소 1개 이상 선택해 주세요.")
                return

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

            feature_text = make_feature_text()

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
            result = add_clothing_to_backend(item)

            if isinstance(result, dict) and "error" in result:
                messagebox.showwarning(
                    "백엔드 저장 실패",
                    "앱 화면에는 추가했지만 서버 저장은 실패했습니다.\n백엔드 서버가 켜져 있는지 확인해 주세요."
                )
            else:
                messagebox.showinfo(
                    "저장 완료",
                    f"{item.category} / {item.detail} 옷이 저장되었습니다."
                )

            canvas.unbind_all("<MouseWheel>")
            self.app.show_home()

        image_button_row = tk.Frame(form_card, bg="white")
        image_button_row.pack(pady=(4, 10))

        tk.Button(
            image_button_row,
            text="사진 선택",
            font=("Arial", 10, "bold"),
            bg="#5f6c86",
            fg="white",
            width=9,
            height=1,
            bd=0,
            command=select_image
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            image_button_row,
            text="색 초기화",
            font=("Arial", 10),
            bg="#d9dee8",
            fg="#222222",
            width=9,
            height=1,
            bd=0,
            command=reset_colors
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            image_button_row,
            text="사진 저장",
            font=("Arial", 10, "bold"),
            bg="#47c95a",
            fg="white",
            width=9,
            height=1,
            bd=0,
            command=save_photo_clothing
        ).grid(row=0, column=2, padx=3)

        tk.Label(
            form_card,
            text="종류",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", padx=18, pady=(8, 4))

        category_var = tk.StringVar(value="상의")
        category_box = ttk.Combobox(
            form_card,
            textvariable=category_var,
            state="readonly",
            values=["상의", "하의", "아우터", "신발", "악세서리"],
            font=("Arial", 11)
        )
        category_box.pack(fill="x", padx=18, pady=3)

        tk.Label(
            form_card,
            text="세부 종류",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", padx=18, pady=(8, 4))

        detail_var = tk.StringVar()
        detail_box = ttk.Combobox(
            form_card,
            textvariable=detail_var,
            state="readonly",
            font=("Arial", 11)
        )
        detail_box.pack(fill="x", padx=18, pady=3)

        feature_section = tk.Frame(form_card, bg="white")
        feature_section.pack(fill="x", padx=18, pady=(8, 4))

        def select_feature(key, value):
            if selected_features[key] == value:
                selected_features[key] = ""
            else:
                selected_features[key] = value

            render_feature_buttons()

        def render_feature_buttons():
            for widget in feature_section.winfo_children():
                widget.destroy()

            tk.Label(
                feature_section,
                text="특징 선택",
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", pady=(4, 6))

            current_category = category_var.get()
            options = feature_options.get(current_category, {})

            option_titles = {
                "fit": "핏",
                "thickness": "두께",
                "mood": "무드",
                "season": "계절감"
            }

            for key in ["fit", "thickness", "mood", "season"]:
                block = tk.Frame(feature_section, bg="white")
                block.pack(fill="x", pady=(2, 5))

                tk.Label(
                    block,
                    text=option_titles[key],
                    font=("Arial", 10, "bold"),
                    bg="white",
                    fg="#333333"
                ).pack(anchor="w", pady=(0, 3))

                row = tk.Frame(block, bg="white")
                row.pack(fill="x")

                for value in options.get(key, []):
                    is_selected = selected_features[key] == value

                    btn = tk.Button(
                        row,
                        text=value,
                        font=("Arial", 8, "bold"),
                        bg="#2f80ff" if is_selected else "#eef1f7",
                        fg="white" if is_selected else "#222222",
                        bd=0,
                        padx=6,
                        pady=4,
                        command=lambda k=key, v=value: select_feature(k, v)
                    )
                    btn.pack(side="left", padx=2, pady=2)

            tk.Label(
                feature_section,
                text="추가 메모",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#333333"
            ).pack(anchor="w", pady=(8, 3))

            memo_entry = tk.Entry(
                feature_section,
                textvariable=memo_var,
                font=("Arial", 11),
                bd=1,
                relief="solid"
            )
            memo_entry.pack(fill="x", ipady=5)

            def clear_memo_placeholder(event):
                if memo_var.get() == "예: 데일리용, 학교 갈 때, 중요한 날":
                    memo_var.set("")

            memo_entry.bind("<FocusIn>", clear_memo_placeholder)

        def update_detail_options(event=None):
            selected = category_var.get()
            options = self.app.detail_options.get(selected, [])
            detail_box["values"] = options

            if options:
                detail_box.set(options[0])

            selected_features["fit"] = ""
            selected_features["thickness"] = ""
            selected_features["mood"] = ""
            selected_features["season"] = ""

            render_feature_buttons()

        category_box.bind("<<ComboboxSelected>>", update_detail_options)
        update_detail_options()

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

            recommended = ", ".join(result.get("recommended_colors", []))
            avoid = ", ".join(result.get("avoid_colors", []))

            messagebox.showinfo(
                "사진 기반 추천 결과",
                f"선택한 색상: {result.get('base_color', main_color['name'])}\n\n"
                f"추천 대상: {result.get('target_category', '하의')}\n\n"
                f"추천 색상: {recommended}\n\n"
                f"피하면 좋은 색상: {avoid}\n\n"
                f"이유: {result.get('reason', '추천 이유가 없습니다.')}"
            )

        tk.Button(
            form_card,
            text="사진 색상으로 추천받기",
            font=("Arial", 11, "bold"),
            bg="#2f80ff",
            fg="white",
            height=2,
            bd=0,
            command=recommend_by_photo
        ).pack(fill="x", padx=18, pady=(10, 14))