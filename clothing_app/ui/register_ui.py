import os
import shutil
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from api_client import add_clothing_to_backend, recommend_from_photo_backend
from PIL import Image, ImageTk

from model.clothing import Clothing
from logic.color_logic import rgb_to_hex, rgb_to_name
from logic.recommend_logic import extract_dominant_colors
from ui import style


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
        self.max_photo_colors = 3

    def show_register_options(self):
        self.app.clear_screen()
        self.app.create_top_bar("옷 등록하기")

        body = tk.Frame(self.app.main_frame, bg=style.BG)
        body.pack(fill="both", expand=True)

        center_frame = tk.Frame(body, bg=style.BG)
        center_frame.place(relx=0.5, rely=0.42, anchor="center")

        tk.Button(
            center_frame,
            text="사진으로 등록하기",
            font=(style.FONT, 16, "bold"),
            bg=style.PRIMARY,
            fg="white",
            width=18,
            height=2,
            bd=0,
            command=self.show_photo_register
        ).pack(pady=18)

        tk.Button(
            body,
            text="뒤로가기",
            font=(style.FONT, 11),
            bg=style.MUTED,
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

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(outer, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=style.BG)

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

        form_card = tk.Frame(scrollable_frame, bg=style.CARD, highlightbackground=style.CARD_BORDER, highlightthickness=1, bd=0)
        form_card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(
            form_card,
            text="사진을 불러오면 대표 색상 3개가 자동 추출됩니다.",
            font=(style.FONT, 12, "bold"),
            bg=style.CARD,
            fg=style.TEXT,
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(15, 6))

        tk.Label(
            form_card,
            text="자동 추출 결과를 사용하거나, 사진 위를 직접 클릭해 색을 보정할 수 있습니다.",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.SUBTEXT
        ).pack(anchor="w", padx=18, pady=(0, 8))

        image_canvas = tk.Canvas(
            form_card,
            width=260,
            height=260,
            bg="#f1f5f9",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        image_canvas.pack(pady=(4, 6))

        selected_color_frame = tk.Frame(form_card, bg=style.CARD)
        selected_color_frame.pack(fill="x", padx=18, pady=(4, 6))

        auto_guess_var = tk.StringVar(value="사진을 선택하면 옷 종류를 자동으로 추측합니다.")
        tk.Label(
            form_card,
            textvariable=auto_guess_var,
            font=(style.FONT, 9),
            bg=style.CARD,
            fg=style.SUBTEXT,
            wraplength=360,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 6))

        def refresh_selected_colors():
            for widget in selected_color_frame.winfo_children():
                widget.destroy()

            if not self.photo_selected_colors:
                tk.Label(
                    selected_color_frame,
                    text="선택된 색: 없음",
                    font=(style.FONT, 10),
                    bg=style.CARD,
                    fg="#444444"
                ).pack(anchor="w")
                return

            tk.Label(
                selected_color_frame,
                text=f"선택된 색 {len(self.photo_selected_colors)}개 / 최대 {self.max_photo_colors}개",
                font=(style.FONT, 10, "bold"),
                bg=style.CARD,
                fg=style.TEXT
            ).pack(anchor="w", pady=(0, 4))

            for idx, color in enumerate(self.photo_selected_colors, start=1):
                row = tk.Frame(selected_color_frame, bg=style.CARD)
                row.pack(fill="x", pady=1)

                box = tk.Canvas(row, width=22, height=22, bg=style.CARD, highlightthickness=0)
                box.pack(side="left", padx=(0, 8))
                box.create_rectangle(2, 2, 20, 20, fill=color["hex"], outline="#999999")

                tk.Label(
                    row,
                    text=f"{idx}. {color['name']} / RGB{color['rgb']} / {color['hex']}",
                    font=(style.FONT, 9),
                    bg=style.CARD,
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
                    font=(style.FONT, 13, "bold")
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

            # 대표 색상 자동 추출: 사용자가 직접 클릭하지 않아도 바로 저장 가능
            try:
                extracted = extract_dominant_colors(file_path, color_count=self.max_photo_colors)
                for name, hex_code in extracted:
                    hex_clean = hex_code.lstrip("#")
                    rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                    self.photo_selected_colors.append({
                        "rgb": rgb,
                        "hex": hex_code,
                        "name": name
                    })
            except Exception as e:
                print("대표 색상 자동 추출 실패:", e)

            draw_image_on_canvas()
            refresh_selected_colors()
            apply_auto_clothing_guess(file_path)

        def reset_colors():
            self.photo_selected_colors = []
            draw_image_on_canvas()
            refresh_selected_colors()

        def auto_extract_colors():
            if not self.photo_selected_file_path:
                messagebox.showwarning("사진 없음", "먼저 사진을 선택해 주세요.")
                return
            try:
                self.photo_selected_colors = []
                for name, hex_code in extract_dominant_colors(self.photo_selected_file_path, color_count=self.max_photo_colors):
                    hex_clean = hex_code.lstrip("#")
                    rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                    self.photo_selected_colors.append({"rgb": rgb, "hex": hex_code, "name": name})
                draw_image_on_canvas()
                refresh_selected_colors()
                messagebox.showinfo("자동 추출 완료", "사진에서 대표 색상을 다시 추출했습니다.")
            except Exception as e:
                messagebox.showerror("추출 실패", f"대표 색상을 추출하지 못했습니다.\n{e}")

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

            if len(self.photo_selected_colors) >= self.max_photo_colors:
                messagebox.showinfo("선택 제한", f"색은 최대 {self.max_photo_colors}개까지만 선택할 수 있습니다.")
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

            saved_image_path = self.photo_selected_file_path
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                image_dir = os.path.join(base_dir, "app_data", "images")
                os.makedirs(image_dir, exist_ok=True)
                ext = os.path.splitext(self.photo_selected_file_path)[1] or ".jpg"
                filename = f"{self.app.get_current_user_id()}_{int(time.time() * 1000)}{ext}"
                saved_image_path = os.path.join(image_dir, filename)
                shutil.copy2(self.photo_selected_file_path, saved_image_path)
            except Exception as e:
                print("이미지 복사 실패:", e)

            item = Clothing(
                category=category_var.get(),
                detail=detail_var.get(),
                feature=feature_text,
                rgb=main_color["rgb"],
                hex_code=main_color["hex"],
                color_name=main_color["name"],
                image_path=saved_image_path,
                colors=colors_for_save
            )

            result = add_clothing_to_backend(item, self.app.get_current_user_id())

            if isinstance(result, dict) and "id" in result:
                item.id = result["id"]

            self.app.clothes.append(item)

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

        image_button_row = tk.Frame(form_card, bg=style.CARD)
        image_button_row.pack(pady=(4, 10))

        tk.Button(
            image_button_row,
            text="사진 선택",
            font=(style.FONT, 10, "bold"),
            bg="#5f6c86",
            fg="white",
            width=9,
            height=1,
            bd=0,
            command=select_image
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            image_button_row,
            text="자동 추출",
            font=(style.FONT, 10, "bold"),
            bg="#8b5cf6",
            fg="white",
            width=9,
            height=1,
            bd=0,
            command=auto_extract_colors
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            image_button_row,
            text="색 초기화",
            font=(style.FONT, 10),
            bg=style.MUTED,
            fg=style.TEXT,
            width=9,
            height=1,
            bd=0,
            command=reset_colors
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            image_button_row,
            text="사진 저장",
            font=(style.FONT, 10, "bold"),
            bg=style.SUCCESS,
            fg="white",
            width=9,
            height=1,
            bd=0,
            command=save_photo_clothing
        ).grid(row=0, column=3, padx=3)

        tk.Label(
            form_card,
            text="종류",
            font=(style.FONT, 12, "bold"),
            bg=style.CARD
        ).pack(anchor="w", padx=18, pady=(8, 4))

        category_var = tk.StringVar(value="상의")
        category_box = ttk.Combobox(
            form_card,
            textvariable=category_var,
            state="readonly",
            values=["상의", "하의", "아우터", "신발", "악세서리"],
            font=(style.FONT, 11)
        )
        category_box.pack(fill="x", padx=18, pady=3)

        tk.Label(
            form_card,
            text="세부 종류",
            font=(style.FONT, 12, "bold"),
            bg=style.CARD
        ).pack(anchor="w", padx=18, pady=(8, 4))

        detail_var = tk.StringVar()
        detail_box = ttk.Combobox(
            form_card,
            textvariable=detail_var,
            state="readonly",
            font=(style.FONT, 11)
        )
        detail_box.pack(fill="x", padx=18, pady=3)

        feature_section = tk.Frame(form_card, bg=style.CARD)
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
                font=(style.FONT, 12, "bold"),
                bg=style.CARD,
                fg=style.TEXT
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
                block = tk.Frame(feature_section, bg=style.CARD)
                block.pack(fill="x", pady=(2, 5))

                tk.Label(
                    block,
                    text=option_titles[key],
                    font=(style.FONT, 10, "bold"),
                    bg=style.CARD,
                    fg=style.TEXT
                ).pack(anchor="w", pady=(0, 3))

                row = tk.Frame(block, bg=style.CARD)
                row.pack(fill="x")

                for value in options.get(key, []):
                    is_selected = selected_features[key] == value

                    btn = tk.Button(
                        row,
                        text=value,
                        font=(style.FONT, 8, "bold"),
                        bg=style.PRIMARY if is_selected else "#eef1f7",
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
                font=(style.FONT, 10, "bold"),
                bg=style.CARD,
                fg=style.TEXT
            ).pack(anchor="w", pady=(8, 3))

            memo_entry = tk.Entry(
                feature_section,
                textvariable=memo_var,
                font=(style.FONT, 11),
                bd=0,
                relief="flat",
                highlightthickness=1,
                highlightbackground=style.CARD_BORDER,
                highlightcolor=style.PRIMARY
            )
            memo_entry.pack(fill="x", ipady=5)

            def clear_memo_placeholder(event):
                if memo_var.get() == "예: 데일리용, 학교 갈 때, 중요한 날":
                    memo_var.set("")

            memo_entry.bind("<FocusIn>", clear_memo_placeholder)

        def infer_clothing_by_rule(file_path):
            """파일명 + 이미지 형태를 함께 사용하는 가벼운 규칙 기반 추측 함수입니다.
            AI 모델을 추가하지 않아 기존 기능과 설치 환경은 그대로 유지하면서,
            파일명이 애매한 사진도 대략적인 종류를 자동 입력할 수 있게 합니다.
            """
            filename = os.path.basename(file_path).lower()

            # 1) 파일명 단서가 있으면 가장 우선합니다. 사용자가 저장한 이름이 가장 정확한 경우가 많습니다.
            filename_rules = [
                ("상의", "반팔", ["반팔", "티셔츠", "tshirt", "t-shirt", "tee", "short sleeve", "short_sleeve"]),
                ("상의", "긴팔", ["긴팔", "long sleeve", "long_sleeve", "longsleeve"]),
                ("상의", "셔츠", ["셔츠", "shirt", "남방"]),
                ("상의", "니트", ["니트", "knit", "sweater"]),
                ("상의", "맨투맨", ["맨투맨", "sweatshirt"]),
                ("상의", "후드티", ["후드", "hoodie", "hood"]),
                ("상의", "블라우스", ["블라우스", "blouse"]),
                ("상의", "민소매", ["민소매", "나시", "sleeveless", "tank"]),
                ("하의", "청바지", ["청바지", "jean", "denim"]),
                ("하의", "슬랙스", ["슬랙스", "slacks", "trouser"]),
                ("하의", "반바지", ["반바지", "shorts"]),
                ("하의", "조거팬츠", ["조거", "jogger"]),
                ("하의", "면바지", ["면바지", "chino"]),
                ("하의", "치마", ["치마", "skirt"]),
                ("아우터", "패딩", ["패딩", "padding", "puffer"]),
                ("아우터", "후리스", ["후리스", "fleece"]),
                ("아우터", "코트", ["코트", "coat"]),
                ("아우터", "가디건", ["가디건", "cardigan"]),
                ("아우터", "자켓", ["자켓", "재킷", "jacket", "blazer"]),
                ("아우터", "집업", ["집업", "zipup", "zip-up"]),
                ("신발", "운동화", ["운동화", "sneaker", "running"]),
                ("신발", "구두", ["구두", "dress shoes"]),
                ("신발", "로퍼", ["로퍼", "loafer"]),
                ("신발", "부츠", ["부츠", "boots"]),
                ("신발", "샌들", ["샌들", "sandal"]),
                ("신발", "슬리퍼", ["슬리퍼", "slipper"]),
                ("악세서리", "모자", ["모자", "cap", "hat"]),
                ("악세서리", "가방", ["가방", "bag"]),
                ("악세서리", "시계", ["시계", "watch"]),
                ("악세서리", "목걸이", ["목걸이", "necklace"]),
                ("악세서리", "팔찌", ["팔찌", "bracelet"]),
                ("악세서리", "반지", ["반지", "ring"]),
                ("악세서리", "벨트", ["벨트", "belt"]),
                ("악세서리", "머플러", ["머플러", "scarf", "muffler"]),
            ]

            for category, detail, keywords in filename_rules:
                if any(keyword in filename for keyword in keywords):
                    return category, detail, "파일명", "높음"

            # 2) 파일명에 단서가 없으면 사진 속 옷 덩어리의 가로/세로 비율로 추측합니다.
            try:
                return infer_clothing_by_image_shape(file_path)
            except Exception as e:
                print("이미지 기반 종류 추측 실패:", e)
                return None, None, "실패", "낮음"

        def infer_clothing_by_image_shape(file_path):
            """무거운 AI 없이 사진의 중앙 물체 형태를 이용해 옷 종류를 추측합니다.
            정확한 판별이 아니라 자동 입력 보조용입니다.
            """
            import colorsys

            img = Image.open(file_path).convert("RGB")
            img.thumbnail((220, 220))
            w, h = img.size
            pixels = img.load()

            xs = []
            ys = []
            for y in range(h):
                for x in range(w):
                    r, g, b = pixels[x, y]
                    hv, s_val, v_val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

                    # 흰 배경, 완전 검정 그림자, 너무 연한 배경은 제외하고 옷으로 보이는 픽셀만 모읍니다.
                    is_plain_white = v_val > 0.93 and s_val < 0.10
                    is_deep_shadow = v_val < 0.06
                    is_soft_background = s_val < 0.06 and 0.78 < v_val < 0.96
                    if is_plain_white or is_deep_shadow or is_soft_background:
                        continue

                    # 채도 있는 옷 또는 적당히 어둡고 면적이 있는 무채색 옷 후보
                    if s_val > 0.16 or (0.12 < v_val < 0.78):
                        xs.append(x)
                        ys.append(y)

            if len(xs) < 120:
                return None, None, "이미지", "낮음"

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            box_w = max_x - min_x + 1
            box_h = max_y - min_y + 1
            ratio = box_w / max(1, box_h)
            coverage = len(xs) / max(1, w * h)

            # 하의는 보통 세로로 길고 아래쪽까지 이어집니다.
            if box_h > box_w * 1.35 and max_y > h * 0.70:
                # 파란 계열이 많으면 청바지로, 아니면 가장 무난한 슬랙스로 추측
                blue_count = 0
                for idx in range(0, len(xs), max(1, len(xs) // 800)):
                    r, g, b = pixels[xs[idx], ys[idx]]
                    if b > r + 18 and b > g + 6:
                        blue_count += 1
                if blue_count > 40:
                    return "하의", "청바지", "이미지 형태", "중간"
                return "하의", "슬랙스", "이미지 형태", "중간"

            # 좌우로 매우 넓고 세로가 짧으면 펼친 긴팔/아우터일 가능성이 있습니다.
            if ratio > 1.55 and box_w > w * 0.62:
                if coverage > 0.34:
                    return "아우터", "자켓", "이미지 형태", "낮음"
                return "상의", "긴팔", "이미지 형태", "중간"

            # 상의는 중앙에 몸통이 있고 가로/세로 비율이 비교적 균형적입니다.
            if 0.70 <= ratio <= 1.55:
                # 윗부분 면적이 두껍고 목 주변 덩어리가 크면 후드/맨투맨 계열로 약하게 추측
                top_pixels = sum(1 for x, y in zip(xs, ys) if y < min_y + box_h * 0.28)
                top_ratio = top_pixels / max(1, len(xs))
                if top_ratio > 0.36 and coverage > 0.28:
                    return "상의", "맨투맨", "이미지 형태", "낮음"
                return "상의", "반팔", "이미지 형태", "중간"

            # 애매하면 사진 등록에서 가장 자주 쓰는 상의/반팔로 두되, 사용자가 수정 가능하게 안내합니다.
            return "상의", "반팔", "기본 추측", "낮음"

        def apply_auto_clothing_guess(file_path):
            guessed_category, guessed_detail, source, confidence = infer_clothing_by_rule(file_path)

            if not guessed_category or not guessed_detail:
                auto_guess_var.set("자동 종류 추측: 단서를 충분히 찾지 못했습니다. 필요하면 아래에서 직접 선택해 주세요.")
                return

            category_box.set(guessed_category)
            update_detail_options(reset_features=False)

            values = list(detail_box["values"])
            if guessed_detail in values:
                detail_box.set(guessed_detail)

            auto_guess_var.set(
                f"자동 종류 추측: {guessed_category} / {guessed_detail} · 기준: {source}, 신뢰도: {confidence} · 틀리면 아래에서 바로 수정할 수 있습니다."
            )

        def update_detail_options(event=None, reset_features=True):
            selected = category_var.get()
            options = self.app.detail_options.get(selected, [])
            detail_box["values"] = options

            if options and detail_var.get() not in options:
                detail_box.set(options[0])

            if reset_features:
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
            font=(style.FONT, 11, "bold"),
            bg=style.PRIMARY,
            fg="white",
            height=2,
            bd=0,
            command=recommend_by_photo
        ).pack(fill="x", padx=18, pady=(10, 14))