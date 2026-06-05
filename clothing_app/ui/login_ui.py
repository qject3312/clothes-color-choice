import tkinter as tk
from tkinter import ttk, messagebox
from api_client import login_user_backend, signup_user_backend
from ui import style


class LoginUI:
    def __init__(self, app):
        self.app = app
        self.selected_styles = []

        self.style_options = [
            ("캐주얼", "#74b9ff"),
            ("힙", "#a29bfe"),
            ("댄디", "#55efc4"),
            ("미니멀", "#dfe6e9"),
            ("스트릿", "#fd79a8"),
            ("스포티", "#00cec9"),
            ("빈티지", "#fab1a0"),
            ("러블리", "#ffeaa7"),
            ("포멀", "#636e72"),
            ("아메카지", "#b2bec3"),
        ]

    def show_login(self):
        self.app.clear_screen()

        body = tk.Frame(self.app.main_frame, bg=style.BG)
        body.pack(fill="both", expand=True)

        card = tk.Frame(body, bg=style.CARD)
        card.place(relx=0.5, rely=0.47, anchor="center", width=350, height=440)

        tk.Label(
            card,
            text="옷 추천 앱",
            font=(style.FONT, 24, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(pady=(35, 8))

        tk.Label(
            card,
            text="로그인 후 서비스를 이용하세요",
            font=(style.FONT, 11),
            bg=style.CARD,
            fg=style.SUBTEXT
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="아이디",
            font=(style.FONT, 11, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=35, pady=(0, 5))

        user_id_entry = tk.Entry(
            card,
            font=(style.FONT, 12),
            bd=1,
            relief="solid"
        )
        user_id_entry.pack(fill="x", padx=35, ipady=7)

        tk.Label(
            card,
            text="비밀번호",
            font=(style.FONT, 11, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=35, pady=(15, 5))

        password_entry = tk.Entry(
            card,
            font=(style.FONT, 12),
            bd=1,
            relief="solid",
            show="*"
        )
        password_entry.pack(fill="x", padx=35, ipady=7)

        def login():
            user_id = user_id_entry.get().strip()
            password = password_entry.get().strip()

            if not user_id or not password:
                messagebox.showwarning("입력 필요", "아이디와 비밀번호를 입력해 주세요.")
                return

            result = login_user_backend(user_id, password)

            if isinstance(result, dict) and "detail" in result:
                messagebox.showerror("로그인 실패", str(result["detail"]))
                return

            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("로그인 실패", "백엔드 서버가 켜져 있는지 확인해 주세요.")
                return

            self.app.current_user = result
            self.app.load_current_user_clothes()
            messagebox.showinfo("로그인 성공", f"{result.get('name', user_id)}님 환영합니다.")
            self.app.show_home()

        tk.Button(
            card,
            text="로그인",
            font=(style.FONT, 12, "bold"),
            bg=style.PRIMARY,
            fg="white",
            bd=0,
            height=2,
            command=login
        ).pack(fill="x", padx=35, pady=(25, 10))

        tk.Button(
            card,
            text="회원가입",
            font=(style.FONT, 12, "bold"),
            bg=style.SUCCESS,
            fg="white",
            bd=0,
            height=2,
            command=self.show_signup
        ).pack(fill="x", padx=35, pady=5)

        tk.Button(
            card,
            text="게스트로 시작",
            font=(style.FONT, 10),
            bg=style.MUTED,
            fg="#222222",
            bd=0,
            height=2,
            command=self.guest_login
        ).pack(fill="x", padx=35, pady=(5, 0))

    def guest_login(self):
        self.app.current_user = {
            "user_id": "guest",
            "password": "",
            "name": "게스트",
            "gender": "미입력",
            "height": "미입력",
            "weight": "미입력",
            "body_type": "미입력",
            "skin_tone": "미입력",
            "personal_color": "미입력",
            "styles": ["미선택"]
        }
        self.app.load_current_user_clothes()
        self.app.show_home()

    def show_signup(self):
        self.app.clear_screen()
        self.selected_styles = []

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.BG)

        body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        style.enable_canvas_drag(canvas, bind_children=body)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title_card = tk.Frame(body, bg=style.BG)
        title_card.pack(fill="x", padx=18, pady=(18, 8))

        tk.Label(
            title_card,
            text="회원가입",
            font=(style.FONT, 23, "bold"),
            bg=style.BG,
            fg="#222222"
        ).pack(anchor="w")

        tk.Label(
            title_card,
            text="원하는 정보만 입력해도 가입할 수 있습니다.",
            font=(style.FONT, 10),
            bg=style.BG,
            fg=style.SUBTEXT
        ).pack(anchor="w", pady=(4, 0))

        form = tk.Frame(body, bg=style.CARD)
        form.pack(fill="x", padx=18, pady=10)

        def label(text):
            tk.Label(
                form,
                text=text,
                font=(style.FONT, 11, "bold"),
                bg=style.CARD,
                fg="#222222"
            ).pack(anchor="w", padx=16, pady=(12, 4))

        def entry():
            e = tk.Entry(
                form,
                font=(style.FONT, 11),
                bd=0,
                relief="flat",
                highlightthickness=1,
                highlightbackground=style.CARD_BORDER,
                highlightcolor=style.PRIMARY
            )
            e.pack(fill="x", padx=16, ipady=6)
            return e

        label("아이디")
        user_id_entry = entry()

        label("비밀번호")
        password_entry = tk.Entry(
            form,
            font=(style.FONT, 11),
            bd=1,
            relief="solid",
            show="*"
        )
        password_entry.pack(fill="x", padx=16, ipady=6)

        label("이름")
        name_entry = entry()

        label("성별")
        gender_var = tk.StringVar(value="미입력")
        gender_box = ttk.Combobox(
            form,
            textvariable=gender_var,
            state="readonly",
            values=["미입력", "남성", "여성", "기타"],
            font=(style.FONT, 11)
        )
        gender_box.pack(fill="x", padx=16, ipady=4)

        label("키(cm)")
        height_entry = entry()

        label("몸무게(kg)")
        weight_entry = entry()

        label("체형")
        body_type_var = tk.StringVar(value="미입력")
        body_type_box = ttk.Combobox(
            form,
            textvariable=body_type_var,
            state="readonly",
            values=["미입력", "마른 체형", "보통 체형", "근육형", "통통한 체형"],
            font=(style.FONT, 11)
        )
        body_type_box.pack(fill="x", padx=16, ipady=4)

        label("피부톤")
        skin_tone_var = tk.StringVar(value="미입력")
        skin_tone_box = ttk.Combobox(
            form,
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
        skin_tone_box.pack(fill="x", padx=16, ipady=4)

        label("퍼스널 컬러")
        personal_color_var = tk.StringVar(value="미입력")
        personal_color_box = ttk.Combobox(
            form,
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
        personal_color_box.pack(fill="x", padx=16, ipady=4, pady=(0, 15))

        style_section = tk.Frame(body, bg=style.CARD)
        style_section.pack(fill="x", padx=18, pady=10)

        tk.Label(
            style_section,
            text="추구하는 패션 선택",
            font=(style.FONT, 14, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=16, pady=(16, 4))

        tk.Label(
            style_section,
            text="사진 대신 임시 네모칸으로 구성했습니다. 여러 개 선택할 수 있습니다.",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.SUBTEXT,
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 12))

        grid_frame = tk.Frame(style_section, bg=style.CARD)
        grid_frame.pack(fill="x", padx=12, pady=(0, 16))

        style_buttons = {}

        def toggle_style(style_name):
            if style_name in self.selected_styles:
                self.selected_styles.remove(style_name)
            else:
                self.selected_styles.append(style_name)

            refresh_style_buttons()

        def refresh_style_buttons():
            for style_name, btn in style_buttons.items():
                if style_name in self.selected_styles:
                    btn.config(
                        relief="solid",
                        bd=3,
                        text=f"{style_name}\n선택됨"
                    )
                else:
                    btn.config(
                        relief="flat",
                        bd=0,
                        text=style_name
                    )

        for index, (style_name, color) in enumerate(self.style_options):
            row = index // 2
            col = index % 2

            btn = tk.Button(
                grid_frame,
                text=style_name,
                font=(style.FONT, 13, "bold"),
                bg=color,
                fg="#222222",
                width=14,
                height=5,
                bd=0,
                command=lambda s=style_name: toggle_style(s)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            style_buttons[style_name] = btn

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        button_area = tk.Frame(body, bg=style.BG)
        button_area.pack(fill="x", padx=18, pady=(8, 25))

        def make_user(skip_optional=False):
            user_id = user_id_entry.get().strip()
            password = password_entry.get().strip()
            name = name_entry.get().strip()

            if not user_id or not password:
                messagebox.showwarning("필수 입력", "아이디와 비밀번호는 입력해 주세요.")
                return None

            if not name:
                name = user_id

            if skip_optional:
                return {
                    "user_id": user_id,
                    "password": password,
                    "name": name,
                    "gender": "미입력",
                    "height": "미입력",
                    "weight": "미입력",
                    "body_type": "미입력",
                    "skin_tone": "미입력",
                    "personal_color": "미입력",
                    "styles": ["미선택"]
                }

            height = height_entry.get().strip()
            weight = weight_entry.get().strip()

            user = {
                "user_id": user_id,
                "password": password,
                "name": name,
                "gender": gender_var.get(),
                "height": height if height else "미입력",
                "weight": weight if weight else "미입력",
                "body_type": body_type_var.get(),
                "skin_tone": skin_tone_var.get(),
                "personal_color": personal_color_var.get(),
                "styles": self.selected_styles if self.selected_styles else ["미선택"]
            }

            return user

        def signup():
            user = make_user(skip_optional=False)

            if user is None:
                return

            result = signup_user_backend(user)

            if isinstance(result, dict) and "detail" in result:
                messagebox.showerror("가입 실패", str(result["detail"]))
                return

            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("가입 실패", "백엔드 서버가 켜져 있는지 확인해 주세요.")
                return

            self.app.current_user = result
            self.app.load_current_user_clothes()

            messagebox.showinfo("가입 완료", "회원가입이 완료되었습니다.")
            self.app.show_home()

        def skip_and_signup():
            user = make_user(skip_optional=True)

            if user is None:
                return

            result = signup_user_backend(user)

            if isinstance(result, dict) and "detail" in result:
                messagebox.showerror("가입 실패", str(result["detail"]))
                return

            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("가입 실패", "백엔드 서버가 켜져 있는지 확인해 주세요.")
                return

            self.app.current_user = result
            self.app.load_current_user_clothes()

            messagebox.showinfo("가입 완료", "선택 정보를 건너뛰고 가입했습니다.")
            self.app.show_home()

        tk.Button(
            button_area,
            text="회원가입 완료",
            font=(style.FONT, 12, "bold"),
            bg=style.PRIMARY,
            fg="white",
            bd=0,
            height=2,
            command=signup
        ).pack(fill="x", pady=5)

        tk.Button(
            button_area,
            text="선택 정보 건너뛰기",
            font=(style.FONT, 12, "bold"),
            bg="#5f6c86",
            fg="white",
            bd=0,
            height=2,
            command=skip_and_signup
        ).pack(fill="x", pady=5)

        tk.Button(
            button_area,
            text="로그인 화면으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            fg="#222222",
            bd=0,
            height=2,
            command=self.show_login
        ).pack(fill="x", pady=5)
