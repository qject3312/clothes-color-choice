import os
import shutil
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from api_client import add_clothing_to_backend, recommend_from_photo_backend
from PIL import Image, ImageTk
from app_paths import IMAGE_DIR, make_relative_to_app, resolve_existing_path

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
        style.enable_canvas_drag(canvas, bind_children=scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        form_card = tk.Frame(scrollable_frame, bg=style.CARD, highlightbackground=style.CARD_BORDER, highlightthickness=1, bd=0)
        form_card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(
            form_card,
            text="사진을 불러오면 옷 종류와 대표 색상을 자동으로 추측합니다.",
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
                file_path = resolve_existing_path(file_path)
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
                image_dir = str(IMAGE_DIR)
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
            elif isinstance(result, dict) and "error" in result:
                messagebox.showerror(
                    "저장 실패",
                    "서버 저장에 실패해서 옷장에 추가하지 않았습니다.\n앱을 다시 실행했을 때 사라지는 문제를 막기 위해 저장 성공한 옷만 추가합니다."
                )
                return
            else:
                self.app.clothes.append(item)

            if isinstance(result, dict) and "error" in result:
                messagebox.showwarning(
                    "백엔드 저장 실패",
                    "서버 저장에 실패했습니다."
                )
            else:
                messagebox.showinfo(
                    "저장 완료",
                    f"{item.category} / {item.detail} 옷이 저장되었습니다."
                )

            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
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
            font=(style.FONT, 11),
            height=5
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
            font=(style.FONT, 11),
            height=6
        )
        detail_box.pack(fill="x", padx=18, pady=3)

        feature_section = tk.Frame(form_card, bg=style.CARD)
        feature_section.pack(fill="x", padx=18, pady=(8, 4))

        def select_feature(key, value):
            # 특징 버튼을 누를 때 버튼 영역을 다시 그리면 Tkinter가 캔버스 스크롤을
            # 맨 위로 되돌리는 경우가 있어, 현재 위치를 저장했다가 그대로 복원합니다.
            scroll_pos = canvas.yview()[0]

            if selected_features[key] == value:
                selected_features[key] = ""
            else:
                selected_features[key] = value

            render_feature_buttons()
            canvas.update_idletasks()
            canvas.yview_moveto(scroll_pos)

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
            """파일명 + 이미지 형태를 함께 사용하는 강화된 규칙 기반 추측 함수입니다.
            별도 AI 모델을 설치하지 않아도 맥/윈도우에서 그대로 실행되도록 PIL만 사용합니다.
            """
            filename = os.path.basename(file_path).lower()
            name_text = filename.replace("_", " ").replace("-", " ").replace(".", " ")

            # 1) 파일명 단서가 있으면 가장 우선합니다. 한국어/영어/쇼핑몰식 표현을 넓게 반영했습니다.
            filename_rules = [
                ("상의", "기모 맨투맨", ["기모맨투맨", "기모 맨투맨", "fleece sweatshirt", "brushed sweatshirt"]),
                ("상의", "후드티", ["후드티", "후드", "hoodie", "hooded", "hood"]),
                ("상의", "맨투맨", ["맨투맨", "스웨트셔츠", "sweatshirt", "sweat shirt", "mtm"]),
                ("상의", "반팔", ["반팔", "반소매", "티셔츠", "티", "tshirt", "t shirt", "t-shirt", "tee", "short sleeve", "shortsleeve", "short sleeved"]),
                ("상의", "긴팔", ["긴팔", "긴소매", "long sleeve", "longsleeve", "long sleeved"]),
                ("상의", "셔츠", ["셔츠", "남방", "와이셔츠", "shirt", "button down", "buttonup", "button up"]),
                ("상의", "니트", ["니트", "스웨터", "knit", "sweater", "pullover"]),
                ("상의", "블라우스", ["블라우스", "blouse"]),
                ("상의", "민소매", ["민소매", "나시", "sleeveless", "tank", "tanktop", "tank top"]),
                ("하의", "청바지", ["청바지", "데님", "jean", "jeans", "denim"]),
                ("하의", "슬랙스", ["슬랙스", "slacks", "trouser", "trousers", "dress pants"]),
                ("하의", "반바지", ["반바지", "쇼츠", "shorts", "half pants"]),
                ("하의", "조거팬츠", ["조거", "jogger", "joggers"]),
                ("하의", "면바지", ["면바지", "치노", "chino", "chinos", "cotton pants"]),
                ("하의", "치마", ["치마", "스커트", "skirt"]),
                ("하의", "두꺼운 바지", ["두꺼운바지", "두꺼운 바지", "winter pants", "기모바지"]),
                ("하의", "얇은 바지", ["얇은바지", "얇은 바지", "summer pants"]),
                ("아우터", "패딩", ["패딩", "숏패딩", "롱패딩", "덕다운", "구스다운", "다운", "padding", "puffer", "padded", "down jacket", "parka"]),
                ("아우터", "후리스", ["후리스", "플리스", "fleece"]),
                ("아우터", "두꺼운 코트", ["두꺼운코트", "두꺼운 코트", "heavy coat", "winter coat"]),
                ("아우터", "코트", ["코트", "coat", "trench"]),
                ("아우터", "얇은 가디건", ["얇은가디건", "얇은 가디건", "light cardigan"]),
                ("아우터", "가디건", ["가디건", "cardigan"]),
                ("아우터", "얇은 자켓", ["얇은자켓", "얇은 자켓", "light jacket"]),
                ("아우터", "자켓", ["자켓", "재킷", "jacket", "blazer"]),
                ("아우터", "점퍼", ["점퍼", "jumper", "windbreaker", "윈드브레이커"]),
                ("아우터", "집업", ["집업", "zipup", "zip up", "zip-up"]),
                ("신발", "운동화", ["운동화", "러닝화", "running shoes", "running"]),
                ("신발", "스니커즈", ["스니커즈", "sneaker", "sneakers"]),
                ("신발", "구두", ["구두", "dress shoes"]),
                ("신발", "로퍼", ["로퍼", "loafer", "loafers"]),
                ("신발", "부츠", ["부츠", "boots", "boot"]),
                ("신발", "샌들", ["샌들", "sandal", "sandals"]),
                ("신발", "슬리퍼", ["슬리퍼", "slide", "slides", "slipper"]),
                ("악세서리", "선글라스", ["선글라스", "sunglasses", "sun glasses"]),
                ("악세서리", "모자", ["모자", "볼캡", "비니", "cap", "hat", "beanie"]),
                ("악세서리", "가방", ["가방", "백팩", "토트백", "크로스백", "숄더백", "에코백", "힙색", "파우치", "지갑", "bag", "backpack", "tote", "cross bag", "shoulder bag", "pouch", "wallet"]),
                ("악세서리", "시계", ["시계", "watch"]),
                ("악세서리", "목걸이", ["목걸이", "체인", "펜던트", "목걸", "necklace", "chain", "pendant", "choker"]),
                ("악세서리", "팔찌", ["팔찌", "뱅글", "bracelet", "bangle"]),
                ("악세서리", "반지", ["반지", "ring"]),
                ("악세서리", "벨트", ["벨트", "belt"]),
                ("악세서리", "머플러", ["머플러", "목도리", "scarf", "muffler"]),
                ("악세서리", "양말", ["양말", "sock", "socks"]),
            ]

            for category, detail, keywords in filename_rules:
                if any(keyword in name_text for keyword in keywords):
                    return category, detail, "파일명", "높음"

            try:
                return infer_clothing_by_image_shape(file_path)
            except Exception as e:
                print("이미지 기반 종류 추측 실패:", e)
                return None, None, "실패", "낮음"

        def infer_clothing_by_image_shape(file_path):
            """사진 속 물체의 마스크/비율/상하 폭/색상 분포를 이용해 종류를 추측합니다.
            완전한 AI 분류기는 아니지만 기존 단순 비율 방식보다 반팔·긴팔·하의·아우터·신발을 더 잘 나누도록 보강했습니다.
            """
            import colorsys
            import math

            file_path = resolve_existing_path(file_path)
            img = Image.open(file_path).convert("RGB")
            img.thumbnail((260, 260))
            w, h = img.size
            pixels = img.load()

            # 모서리/가장자리 색을 배경색으로 보고, 배경과 다른 픽셀을 옷 후보로 잡습니다.
            edge_samples = []
            step = max(1, min(w, h) // 20)
            for x in range(0, w, step):
                edge_samples.append(pixels[x, 0])
                edge_samples.append(pixels[x, h - 1])
            for y in range(0, h, step):
                edge_samples.append(pixels[0, y])
                edge_samples.append(pixels[w - 1, y])

            bg = tuple(int(sorted([c[i] for c in edge_samples])[len(edge_samples) // 2]) for i in range(3))

            mask = []
            xs = []
            ys = []
            for y in range(h):
                row = []
                for x in range(w):
                    r, g, b = pixels[x, y]
                    hv, s_val, v_val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    dist_bg = math.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)

                    # 흰/회색 배경과 그림자는 제외하되, 검정 옷은 살립니다.
                    too_close_to_bg = dist_bg < 28 and not (v_val < 0.35 and dist_bg > 12)
                    plain_white_bg = v_val > 0.94 and s_val < 0.08
                    soft_gray_bg = s_val < 0.05 and 0.80 < v_val < 0.98 and dist_bg < 45
                    very_small_shadow = v_val < 0.04
                    is_object = not (too_close_to_bg or plain_white_bg or soft_gray_bg or very_small_shadow)

                    # 배경과 비슷한 색이어도 채도 있거나 충분히 어두우면 옷 후보로 추가
                    if not is_object and (s_val > 0.18 or (0.08 < v_val < 0.70 and dist_bg > 18)):
                        is_object = True

                    row.append(is_object)
                    if is_object:
                        xs.append(x)
                        ys.append(y)
                mask.append(row)

            if len(xs) < max(150, w * h * 0.015):
                return None, None, "이미지", "낮음"

            # 가장 큰 연결 덩어리만 사용해 배경 물체/로고/그림자를 줄입니다.
            visited = [[False] * w for _ in range(h)]
            best = []
            for sy in range(h):
                for sx in range(w):
                    if not mask[sy][sx] or visited[sy][sx]:
                        continue
                    stack = [(sx, sy)]
                    visited[sy][sx] = True
                    comp = []
                    while stack:
                        cx, cy = stack.pop()
                        comp.append((cx, cy))
                        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                            if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not visited[ny][nx]:
                                visited[ny][nx] = True
                                stack.append((nx, ny))
                    if len(comp) > len(best):
                        best = comp

            if len(best) < max(120, len(xs) * 0.35):
                best = list(zip(xs, ys))

            xs = [p[0] for p in best]
            ys = [p[1] for p in best]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            box_w = max_x - min_x + 1
            box_h = max_y - min_y + 1
            ratio = box_w / max(1, box_h)
            coverage = len(best) / max(1, w * h)
            center_y = (min_y + max_y) / 2 / h

            def width_at(frac1, frac2):
                y1 = min_y + box_h * frac1
                y2 = min_y + box_h * frac2
                line_xs = [x for x, y in best if y1 <= y <= y2]
                if not line_xs:
                    return 0
                return max(line_xs) - min(line_xs) + 1

            upper_w = width_at(0.10, 0.32)
            mid_w = width_at(0.38, 0.62)
            lower_w = width_at(0.70, 0.95)
            upper_mid = upper_w / max(1, mid_w)
            lower_mid = lower_w / max(1, mid_w)
            object_density = len(best) / max(1, box_w * box_h)

            def height_at(frac1, frac2):
                x1 = min_x + box_w * frac1
                x2 = min_x + box_w * frac2
                line_ys = [y for x, y in best if x1 <= x <= x2]
                if not line_ys:
                    return 0
                return max(line_ys) - min(line_ys) + 1

            left_h = height_at(0.05, 0.25)
            center_h = height_at(0.38, 0.62)
            right_h = height_at(0.75, 0.95)
            side_center_h = max(left_h, right_h) / max(1, center_h)

            # 색상 힌트: 파란 계열 하의는 청바지 가능성이 큼
            blue_score = 0
            dark_score = 0
            sample_step = max(1, len(best) // 900)
            for x, y in best[::sample_step]:
                r, g, b = pixels[x, y]
                if b > r + 18 and b > g + 5:
                    blue_score += 1
                if max(r, g, b) < 85:
                    dark_score += 1

            # 매우 얇거나 작은 물체는 옷보다 악세서리일 가능성이 큽니다.
            # 목걸이/팔찌/벨트처럼 배경 안에 선 형태로 보이는 물체를 상의/하의로 오인하지 않게 먼저 걸러냅니다.
            sparse_object = object_density < 0.26 and coverage < 0.12
            thin_wide_object = ratio > 2.25 and box_h < h * 0.34 and coverage < 0.18
            thin_tall_object = ratio < 0.45 and box_w < w * 0.32 and coverage < 0.14
            ring_like_object = 0.55 <= ratio <= 1.65 and sparse_object and box_w < w * 0.72 and box_h < h * 0.72

            if thin_wide_object:
                if box_h < h * 0.16:
                    return "악세서리", "벨트", "이미지 형태", "낮음"
                return "악세서리", "머플러", "이미지 형태", "낮음"
            if ring_like_object:
                # 동그란 고리/체인 형태는 목걸이·팔찌·반지로 추정합니다.
                if box_w < w * 0.28 and box_h < h * 0.28:
                    return "악세서리", "반지", "이미지 형태", "낮음"
                if box_w < w * 0.50 and box_h < h * 0.45:
                    return "악세서리", "팔찌", "이미지 형태", "낮음"
                return "악세서리", "목걸이", "이미지 형태", "낮음"
            if thin_tall_object:
                return "악세서리", "목걸이", "이미지 형태", "낮음"

            # 신발/슬리퍼: 가로로 길고 세로가 낮은 물체
            if ratio > 1.85 and box_h < h * 0.45 and coverage < 0.34:
                if dark_score > 120:
                    return "신발", "구두", "이미지 형태", "낮음"
                return "신발", "운동화", "이미지 형태", "중간"

            # 패딩/코트/자켓: 팔이 양옆으로 퍼지거나 몸통 면적이 큰 아우터를 가방/상의로 오인하지 않게 먼저 확인합니다.
            bulky_outer = (
                box_h > h * 0.58
                and box_w > w * 0.45
                and coverage > 0.22
                and 0.55 <= ratio <= 1.65
                and (side_center_h > 0.55 or upper_mid > 1.12)
            )
            puffer_like = (
                bulky_outer
                and object_density > 0.50
                and lower_mid >= 0.80
                and upper_mid >= 0.82
                and box_h > h * 0.64
            )
            if puffer_like:
                return "아우터", "패딩", "이미지 형태", "중간"
            if bulky_outer and box_h > h * 0.70:
                return "아우터", "코트", "이미지 형태", "낮음"
            if bulky_outer and upper_mid > 1.08:
                return "아우터", "자켓", "이미지 형태", "낮음"

            # 가방/악세서리: 백팩/토트백처럼 중앙에 세로로 서 있는 물체를 하의로 오인하지 않도록
            # 하의 판정 전에 먼저 확인합니다.
            # - 가방은 대체로 세로가 약간 더 길고, 중간/아래 폭이 몸통처럼 일정합니다.
            # - 바지는 아래로 갈수록 다리 분리 때문에 폭이 줄거나 빈 공간이 많아지는 경우가 많습니다.
            # - 검정 백팩처럼 화면을 크게 차지하는 경우도 있어 coverage 조건을 너무 낮게 잡지 않습니다.
            bag_like_tall = (
                0.45 <= ratio <= 1.05
                and box_h > h * 0.48
                and box_w > w * 0.28
                and lower_mid >= 0.74
                and upper_mid <= 1.18
                and 0.28 <= center_y <= 0.72
            )
            bag_like_compact = (
                0.65 <= ratio <= 1.45
                and box_h < h * 0.70
                and coverage < 0.30
            )
            very_dark_bag = (
                0.48 <= ratio <= 1.10
                and dark_score > 220
                and lower_mid >= 0.70
                and coverage < 0.48
            )
            if bag_like_tall or bag_like_compact or very_dark_bag:
                return "악세서리", "가방", "이미지 형태", "중간"

            # 하의: 세로로 길고 아래쪽 폭이 유지되며, 위쪽보다 아래쪽까지 길게 내려옴
            if box_h > box_w * 1.25 and max_y > h * 0.72:
                if ratio < 0.58 and lower_mid > 0.70:
                    return "하의", "치마", "이미지 형태", "낮음"
                if blue_score > 90:
                    return "하의", "청바지", "이미지 색상+형태", "중간"
                if lower_mid < 0.72:
                    return "하의", "조거팬츠", "이미지 형태", "낮음"
                return "하의", "슬랙스", "이미지 형태", "중간"

            # 아우터: 면적이 크고 세로/가로가 모두 크며 위아래 폭이 비교적 유지됨
            if coverage > 0.30 and box_h > h * 0.62 and box_w > w * 0.50:
                if object_density > 0.55 and lower_mid >= 0.82:
                    return "아우터", "패딩", "이미지 형태", "낮음"
                if box_h > h * 0.76 and ratio < 1.15:
                    return "아우터", "코트", "이미지 형태", "낮음"
                if ratio > 1.20 and upper_mid > 1.10:
                    return "아우터", "자켓", "이미지 형태", "낮음"
                return "아우터", "집업", "이미지 형태", "낮음"

            # 상의: 상단 소매 폭과 몸통 폭의 차이로 반팔/긴팔/맨투맨을 나눔
            if 0.62 <= ratio <= 1.75:
                if upper_mid >= 1.55 and box_w > w * 0.66:
                    return "상의", "긴팔", "이미지 형태", "중간"
                if coverage > 0.27 and upper_mid > 1.18:
                    return "상의", "맨투맨", "이미지 형태", "낮음"
                if ratio > 1.18 and upper_mid > 1.05:
                    return "상의", "반팔", "이미지 형태", "중간"
                if box_h > h * 0.58 and ratio < 1.05:
                    return "상의", "셔츠", "이미지 형태", "낮음"
                return "상의", "반팔", "이미지 형태", "중간"

            # 넓게 펼친 옷은 긴팔/아우터 가능성이 큼
            if ratio > 1.75:
                return "상의", "긴팔", "이미지 형태", "중간"

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

        def close_open_comboboxes(event=None):
            # ttk.Combobox의 드롭다운을 연 상태에서 화면을 스크롤하면
            # 일부 Windows/macOS Tk 환경에서 드롭다운 목록만 화면에 남아 따라 내려오는 문제가 있습니다.
            # 스크롤/클릭이 시작되는 즉시 Escape와 포커스 이동을 보내 팝업을 강제로 닫습니다.
            for box in (category_box, detail_box):
                try:
                    box.event_generate("<Escape>")
                except Exception:
                    pass
            try:
                self.app.root.event_generate("<Escape>")
                self.app.root.focus_set()
            except Exception:
                pass

        def close_comboboxes_then_scroll(event=None):
            close_open_comboboxes(event)
            try:
                delta = event.delta if hasattr(event, "delta") and event.delta else (120 if getattr(event, "num", None) == 4 else -120)
                canvas.yview_scroll(int(-1 * (delta / 120)), "units")
                return "break"
            except Exception:
                return None

        category_box.bind("<<ComboboxSelected>>", update_detail_options)
        category_box.bind("<MouseWheel>", close_comboboxes_then_scroll)
        detail_box.bind("<MouseWheel>", close_comboboxes_then_scroll)
        canvas.bind("<MouseWheel>", close_comboboxes_then_scroll, add="+")
        scrollable_frame.bind("<MouseWheel>", close_comboboxes_then_scroll, add="+")
        self.app.root.bind_all("<MouseWheel>", close_comboboxes_then_scroll, add="+")
        self.app.root.bind_all("<Button-4>", close_comboboxes_then_scroll, add="+")
        self.app.root.bind_all("<Button-5>", close_comboboxes_then_scroll, add="+")
        canvas.bind("<Button-1>", close_open_comboboxes, add="+")
        scrollable_frame.bind("<Button-1>", close_open_comboboxes, add="+")
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
            text="사진 저장",
            font=(style.FONT, 11, "bold"),
            bg=style.PRIMARY,
            fg="white",
            height=2,
            bd=0,
            command=save_photo_clothing
        ).pack(fill="x", padx=18, pady=(10, 14))