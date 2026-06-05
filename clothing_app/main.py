import os
import tkinter as tk
from backend_runner import start_backend_if_needed
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

try:
    from api_client import get_clothes_from_backend, update_user_backend
except Exception:
    def get_clothes_from_backend(user_id="guest"):
        return []
    def update_user_backend(user):
        return {"error": "api_client import failed"}

from model.clothing import Clothing
from ui.login_ui import LoginUI
from ui.main_ui import MainUI
from ui.register_ui import RegisterUI
from ui.clothes_ui import ClothesUI
from ui.recommend_ui import RecommendUI
from ui.today_recommend_ui import TodayRecommendUI
from ui.temperature_ui import TemperatureUI
from ui.personal_recommend_ui import PersonalRecommendUI
from ui.outfit_ui import OutfitUI
from ui.coordination_ui import CoordinationUI
from ui import style


class ClothingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("핏픽 - 맞춤 옷 추천")
        self.root.geometry("430x760")
        style.apply_theme(self.root)
        self.root.resizable(True, True)

        # 백엔드를 사용자가 따로 켜지 않아도 앱 시작 시 자동 실행합니다.
        self.backend_ready = start_backend_if_needed()

        self.users = {}
        self.current_user = None

        self.clothes = []
        self.saved_outfits = []

        self.detail_options = {
            "상의": [
                "반팔", "긴팔", "셔츠", "니트", "맨투맨",
                "후드티", "블라우스", "민소매", "기모 맨투맨"
            ],
            "하의": [
                "청바지", "슬랙스", "반바지", "조거팬츠",
                "면바지", "치마", "두꺼운 바지", "얇은 바지"
            ],
            "아우터": [
                "패딩", "후리스", "코트", "두꺼운 코트",
                "가디건", "자켓", "점퍼", "집업", "얇은 자켓", "얇은 가디건"
            ],
            "신발": [
                "운동화", "스니커즈", "구두", "로퍼",
                "부츠", "샌들", "슬리퍼"
            ],
            "악세서리": [
                "모자", "가방", "시계", "목걸이",
                "팔찌", "반지", "벨트", "머플러"
            ]
        }

        self.current_hue = 220
        self.selected_rgb = (90, 130, 255)
        self.selected_hex = "#5a82ff"

        self.main_frame = tk.Frame(self.root, bg=style.BG)
        self.main_frame.pack(fill="both", expand=True)

        self.login_ui = LoginUI(self)
        self.main_ui = MainUI(self)
        self.register_ui = RegisterUI(self)
        self.clothes_ui = ClothesUI(self)
        self.recommend_ui = RecommendUI(self)
        self.today_recommend_ui = TodayRecommendUI(self)
        self.temperature_ui = TemperatureUI(self)
        self.personal_recommend_ui = PersonalRecommendUI(self)
        self.outfit_ui = OutfitUI(self)
        self.coordination_ui = CoordinationUI(self)

        self.show_login()


    def get_current_user_id(self):
        if self.current_user is None:
            return "guest"
        return self.current_user.get("user_id", "guest")

    def load_current_user_clothes(self):
        self.clothes = []
        user_id = self.get_current_user_id()

        try:
            saved_clothes = get_clothes_from_backend(user_id)

            if isinstance(saved_clothes, dict) and "error" in saved_clothes:
                print("저장된 옷 불러오기 실패:", saved_clothes["error"])
                return

            for c in saved_clothes:
                self.clothes.append(
                    Clothing(
                        category=c.get("category", ""),
                        detail=c.get("detail", ""),
                        feature=c.get("feature", ""),
                        rgb=(0, 0, 0),
                        hex_code=c.get("color_hex", "#cccccc"),
                        color_name=c.get("color_name", "미분석"),
                        image_path=c.get("image_path", ""),
                        clothing_id=c.get("id")
                    )
                )
        except Exception as e:
            print("저장된 옷 불러오기 실패:", e)

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_top_bar(self, title=""):
        top_bar = tk.Frame(self.main_frame, bg=style.CARD, height=58, bd=0, highlightthickness=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        menu_btn = tk.Button(
            top_bar,
            text="☰",
            font=(style.FONT, 16, "bold"),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            bd=0,
            activebackground=style.CARD,
            command=self.open_menu
        )
        menu_btn.place(x=14, y=8)

        title_label = tk.Label(
            top_bar,
            text=title,
            font=(style.FONT, 16, "bold"),
            bg=style.CARD,
            fg=style.TEXT
        )
        title_label.place(relx=0.5, y=18, anchor="center")

        profile_btn = tk.Button(
            top_bar,
            text="👤",
            font=(style.FONT, 14),
            bg=style.SECONDARY,
            fg=style.MUTED_TEXT,
            bd=0,
            width=2,
            height=1,
            activebackground="#dfe6f3",
            command=self.show_profile
        )
        profile_btn.place(relx=1.0, x=-50, y=11)

    def open_menu(self):
        menu_win = tk.Toplevel(self.root)
        menu_win.title("메뉴")
        menu_win.geometry("260x500")
        menu_win.configure(bg=style.CARD)
        menu_win.resizable(True, True)

        tk.Label(
            menu_win,
            text="메뉴",
            font=(style.FONT, 16, "bold"),
            bg=style.CARD,
            fg=style.TEXT
        ).pack(pady=18)

        tk.Button(
            menu_win,
            text="갖고있는 옷 확인",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_clothes_list()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="사용자 맞춤 코디",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_personal_recommend_ui()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="코디해보기",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_coordination_ui()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="나의 코디 확인",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_outfit_ui()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="온도 기반 추천",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_temperature_ui()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="오늘의 추천 코디",
            font=(style.FONT, 12),
            bg=style.MUTED,
            fg=style.TEXT,
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_today_recommend_ui()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="로그아웃",
            font=(style.FONT, 12),
            bg="#fee2e2",
            fg="#c0392b",
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.logout()]
        ).pack(pady=7)

        tk.Button(
            menu_win,
            text="홈으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            width=15,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_home()]
        ).pack(pady=16)

    def show_profile(self):
        profile_win = tk.Toplevel(self.root)
        profile_win.title("사용자 정보")
        profile_win.geometry("360x640")
        profile_win.configure(bg=style.CARD)
        profile_win.resizable(True, True)

        user = self.current_user

        if user is None:
            user = {
                "user_id": "없음",
                "name": "비로그인",
                "gender": "미입력",
                "height": "미입력",
                "weight": "미입력",
                "body_type": "미입력",
                "skin_tone": "미입력",
                "personal_color": "미입력",
                "styles": ["미선택"]
            }

        styles = user.get("styles", ["미선택"])

        if isinstance(styles, str):
            styles = [styles]

        tk.Label(
            profile_win,
            text="사용자 정보",
            font=(style.FONT, 18, "bold"),
            bg=style.CARD,
            fg=style.TEXT
        ).pack(pady=(18, 10))

        icon_canvas = tk.Canvas(
            profile_win,
            width=70,
            height=70,
            bg=style.CARD,
            highlightthickness=0
        )
        icon_canvas.pack()
        icon_canvas.create_oval(5, 5, 65, 65, fill="#dbe4ff", outline="")
        icon_canvas.create_text(35, 35, text="👤", font=(style.FONT, 24))

        info_card = tk.Frame(profile_win, bg=style.CARD)
        info_card.pack(fill="x", padx=24, pady=18)

        def info_line(label, value):
            row = tk.Frame(info_card, bg=style.CARD)
            row.pack(fill="x", pady=5)

            tk.Label(
                row,
                text=f"{label}:",
                font=(style.FONT, 11, "bold"),
                bg=style.CARD,
                fg=style.TEXT,
                width=10,
                anchor="w"
            ).pack(side="left")

            tk.Label(
                row,
                text=str(value),
                font=(style.FONT, 11),
                bg=style.CARD,
                fg=style.MUTED_TEXT,
                anchor="w",
                wraplength=210,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

        info_line("아이디", user.get("user_id", "미입력"))
        info_line("이름", user.get("name", "미입력"))
        info_line("성별", user.get("gender", "미입력"))
        info_line("키", user.get("height", "미입력"))
        info_line("몸무게", user.get("weight", "미입력"))
        info_line("체형", user.get("body_type", "미입력"))
        info_line("피부톤", user.get("skin_tone", "미입력"))
        info_line("퍼스널컬러", user.get("personal_color", "미입력"))
        info_line("추구 패션", ", ".join(styles))

        button_area = tk.Frame(profile_win, bg=style.CARD)
        button_area.pack(fill="x", padx=24, pady=(10, 18))

        def open_edit_profile():
            profile_win.destroy()
            self.show_edit_profile()

        def logout_from_profile():
            profile_win.destroy()
            self.logout()

        tk.Button(
            button_area,
            text="정보 수정",
            font=(style.FONT, 11, "bold"),
            bg=style.PRIMARY,
            fg="white",
            height=2,
            bd=0,
            command=open_edit_profile
        ).pack(fill="x", pady=5)

        tk.Button(
            button_area,
            text="로그아웃",
            font=(style.FONT, 11, "bold"),
            bg=style.DANGER,
            fg="white",
            height=2,
            bd=0,
            command=logout_from_profile
        ).pack(fill="x", pady=5)

        tk.Button(
            button_area,
            text="닫기",
            font=(style.FONT, 11),
            bg=style.SECONDARY,
            fg=style.TEXT,
            height=2,
            bd=0,
            command=profile_win.destroy
        ).pack(fill="x", pady=5)

    def show_edit_profile(self):
        if self.current_user is None:
            messagebox.showwarning("수정 불가", "로그인된 사용자가 없습니다.")
            return

        edit_win = tk.Toplevel(self.root)
        edit_win.title("사용자 정보 수정")
        edit_win.geometry("380x700")
        edit_win.configure(bg=style.CARD)
        edit_win.resizable(True, True)

        user = self.current_user

        tk.Label(
            edit_win,
            text="사용자 정보 수정",
            font=(style.FONT, 18, "bold"),
            bg=style.CARD,
            fg=style.TEXT
        ).pack(pady=(18, 8))

        outer = tk.Frame(edit_win, bg=style.CARD)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=style.CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.CARD)

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

        def label(text):
            tk.Label(
                body,
                text=text,
                font=(style.FONT, 11, "bold"),
                bg=style.CARD,
                fg=style.TEXT
            ).pack(anchor="w", padx=22, pady=(12, 4))

        def make_entry(default_value):
            entry = tk.Entry(
                body,
                font=(style.FONT, 11),
                bd=0,
                relief="flat",
                highlightthickness=1,
                highlightbackground=style.CARD_BORDER,
                highlightcolor=style.PRIMARY
            )
            entry.pack(fill="x", padx=22, ipady=6)
            entry.insert(0, "" if default_value == "미입력" else str(default_value))
            return entry

        label("아이디")
        tk.Label(
            body,
            text=user.get("user_id", "미입력"),
            font=(style.FONT, 11),
            bg=style.CARD,
            fg=style.SUBTEXT
        ).pack(anchor="w", padx=22, pady=(0, 4))

        label("이름")
        name_entry = make_entry(user.get("name", ""))

        label("성별")
        gender_var = tk.StringVar(value=user.get("gender", "미입력"))
        gender_box = ttk.Combobox(
            body,
            textvariable=gender_var,
            state="readonly",
            values=["미입력", "남성", "여성", "기타"],
            font=(style.FONT, 11)
        )
        gender_box.pack(fill="x", padx=22, ipady=4)

        label("키(cm)")
        height_entry = make_entry(user.get("height", ""))

        label("몸무게(kg)")
        weight_entry = make_entry(user.get("weight", ""))

        label("체형")
        body_type_var = tk.StringVar(value=user.get("body_type", "미입력"))
        body_type_box = ttk.Combobox(
            body,
            textvariable=body_type_var,
            state="readonly",
            values=["미입력", "마른 체형", "보통 체형", "근육형", "통통한 체형"],
            font=(style.FONT, 11)
        )
        body_type_box.pack(fill="x", padx=22, ipady=4)

        label("피부톤")
        skin_tone_var = tk.StringVar(value=user.get("skin_tone", "미입력"))
        skin_tone_box = ttk.Combobox(
            body,
            textvariable=skin_tone_var,
            state="readonly",
            values=[
                "미입력",
                "밝은 피부톤",
                "중간 피부톤",
                "어두운 피부톤",
                "붉은기 있는 피부톤"
            ],
            font=(style.FONT, 11)
        )
        skin_tone_box.pack(fill="x", padx=22, ipady=4)

        label("퍼스널 컬러")
        personal_color_var = tk.StringVar(value=user.get("personal_color", "미입력"))
        personal_color_box = ttk.Combobox(
            body,
            textvariable=personal_color_var,
            state="readonly",
            values=[
                "미입력",
                "봄 웜",
                "여름 쿨",
                "가을 웜",
                "겨울 쿨"
            ],
            font=(style.FONT, 11)
        )
        personal_color_box.pack(fill="x", padx=22, ipady=4)

        tk.Label(
            body,
            text="추구하는 패션",
            font=(style.FONT, 13, "bold"),
            bg=style.CARD,
            fg=style.TEXT
        ).pack(anchor="w", padx=22, pady=(18, 8))

        style_options = [
            "캐주얼",
            "힙",
            "댄디",
            "미니멀",
            "스트릿",
            "스포티",
            "빈티지",
            "러블리",
            "포멀",
            "아메카지"
        ]

        current_styles = user.get("styles", [])

        if isinstance(current_styles, str):
            current_styles = [current_styles]

        selected_styles = set(current_styles)

        if "미선택" in selected_styles:
            selected_styles.remove("미선택")

        style_frame = tk.Frame(body, bg=style.CARD)
        style_frame.pack(fill="x", padx=18, pady=(0, 12))

        style_buttons = {}

        def refresh_style_buttons():
            for style, btn in style_buttons.items():
                if style in selected_styles:
                    btn.config(bg=style.PRIMARY, fg="white", text=f"{style}\n선택됨")
                else:
                    btn.config(bg="#eef1f7", fg="#222222", text=style)

        def toggle_style(style):
            if style in selected_styles:
                selected_styles.remove(style)
            else:
                selected_styles.add(style)

            refresh_style_buttons()

        for idx, style in enumerate(style_options):
            row = idx // 2
            col = idx % 2

            btn = tk.Button(
                style_frame,
                text=style,
                font=(style.FONT, 10, "bold"),
                bg="#eef1f7",
                fg=style.TEXT,
                width=14,
                height=3,
                bd=0,
                command=lambda s=style: toggle_style(s)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            style_buttons[style] = btn

        style_frame.grid_columnconfigure(0, weight=1)
        style_frame.grid_columnconfigure(1, weight=1)

        refresh_style_buttons()

        button_area = tk.Frame(body, bg=style.CARD)
        button_area.pack(fill="x", padx=22, pady=(10, 22))

        def save_profile():
            name = name_entry.get().strip()
            height = height_entry.get().strip()
            weight = weight_entry.get().strip()

            if not name:
                name = user.get("user_id", "사용자")

            user["name"] = name
            user["gender"] = gender_var.get()
            user["height"] = height if height else "미입력"
            user["weight"] = weight if weight else "미입력"
            user["body_type"] = body_type_var.get()
            user["skin_tone"] = skin_tone_var.get()
            user["personal_color"] = personal_color_var.get()
            user["styles"] = list(selected_styles) if selected_styles else ["미선택"]

            user_id = user.get("user_id")

            if user_id:
                update_result = update_user_backend(user)
                if isinstance(update_result, dict) and "error" not in update_result and "detail" not in update_result:
                    user = update_result
                elif isinstance(update_result, dict) and "detail" in update_result:
                    messagebox.showwarning("저장 실패", str(update_result["detail"]))
                else:
                    messagebox.showwarning("저장 실패", "서버에 사용자 정보 저장을 실패했습니다.")

            self.current_user = user

            messagebox.showinfo("수정 완료", "사용자 정보가 수정되었습니다.")
            edit_win.destroy()
            self.show_profile()

        tk.Button(
            button_area,
            text="수정 저장",
            font=(style.FONT, 12, "bold"),
            bg="#47c95a",
            fg="white",
            height=2,
            bd=0,
            command=save_profile
        ).pack(fill="x", pady=5)

        tk.Button(
            button_area,
            text="취소",
            font=(style.FONT, 11),
            bg=style.MUTED,
            fg=style.TEXT,
            height=2,
            bd=0,
            command=edit_win.destroy
        ).pack(fill="x", pady=5)

    def logout(self):
        self.current_user = None
        self.clothes = []
        self.show_login()

    def show_login(self):
        self.login_ui.show_login()

    def show_home(self):
        self.main_ui.show()

    def show_register_options(self):
        self.register_ui.show_register_options()

    def show_clothes_list(self):
        self.clothes_ui.show()

    def show_today_recommend_ui(self):
        # 기존 단순 추천 대신 점수 기반 TOP3 추천 화면으로 연결합니다.
        self.recommend_ui.show()

    def show_temperature_ui(self):
        self.temperature_ui.show()

    def show_personal_recommend_ui(self):
        # 사용자 프로필/체형/퍼스널컬러/스타일을 반영한 추천 화면으로 연결합니다.
        self.recommend_ui.show()

    def show_outfit_ui(self):
        self.outfit_ui.show()

    def show_coordination_ui(self):
        self.coordination_ui.show()

    def show_recommendation_board(self, item, result):
        self.clear_screen()
        self.create_top_bar("추천 코디")

        body = tk.Frame(self.main_frame, bg=style.BG)
        body.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            body,
            text="추천 코디",
            font=(style.FONT, 20, "bold"),
            bg=style.BG,
            fg=style.TEXT
        ).pack(pady=(10, 15))

        if getattr(item, "image_path", "") and os.path.exists(item.image_path):
            try:
                img = Image.open(item.image_path).convert("RGB")
                img.thumbnail((180, 180))
                tk_img = ImageTk.PhotoImage(img)

                img_label = tk.Label(body, image=tk_img, bg=style.BG)
                img_label.image = tk_img
                img_label.pack(pady=10)
            except Exception as e:
                print("추천 화면 이미지 표시 실패:", e)

        tk.Label(
            body,
            text=f"{item.category} / {item.detail}",
            font=(style.FONT, 14, "bold"),
            bg=style.BG,
            fg=style.TEXT
        ).pack(pady=5)

        tk.Canvas(
            body,
            width=250,
            height=50,
            bg=getattr(item, "hex", "#cccccc"),
            highlightthickness=1
        ).pack(pady=10)

        tk.Label(
            body,
            text=f"기준 색상: {item.color_name} / {getattr(item, 'hex', '')}",
            font=(style.FONT, 11),
            bg=style.BG,
            fg=style.MUTED_TEXT
        ).pack(pady=5)

        tk.Label(
            body,
            text=f"추천 하의 색상: {', '.join(result.get('recommended_bottom_colors', []))}",
            bg=style.BG,
            font=(style.FONT, 11),
            fg=style.MUTED_TEXT,
            wraplength=340
        ).pack(pady=5)

        tk.Label(
            body,
            text=f"추천 신발 색상: {', '.join(result.get('recommended_shoes_colors', []))}",
            bg=style.BG,
            font=(style.FONT, 11),
            fg=style.MUTED_TEXT,
            wraplength=340
        ).pack(pady=5)

        tk.Label(
            body,
            text=f"이유:\n{result.get('reason', '추천 이유가 없습니다.')}",
            bg=style.BG,
            font=(style.FONT, 10),
            fg=style.MUTED_TEXT,
            wraplength=340,
            justify="left"
        ).pack(pady=15)

        tk.Button(
            body,
            text="홈으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            width=12,
            bd=0,
            command=self.show_home
        ).pack(pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingApp(root)
    root.mainloop()