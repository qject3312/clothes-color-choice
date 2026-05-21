import tkinter as tk

from ui.main_ui import MainUI
from ui.register_ui import RegisterUI
from ui.clothes_ui import ClothesUI
from ui.today_recommend_ui import TodayRecommendUI
from ui.temperature_ui import TemperatureUI


class ClothingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("옷 추천 앱")
        self.root.geometry("430x780")
        self.root.configure(bg="#f4f6fb")
        self.root.resizable(True, True)

        self.clothes = []

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
            ]
        }

        self.current_hue = 220
        self.selected_rgb = (90, 130, 255)
        self.selected_hex = "#5a82ff"

        self.main_frame = tk.Frame(self.root, bg="#f4f6fb")
        self.main_frame.pack(fill="both", expand=True)

        self.main_ui = MainUI(self)
        self.register_ui = RegisterUI(self)
        self.clothes_ui = ClothesUI(self)
        self.today_recommend_ui = TodayRecommendUI(self)
        self.temperature_ui = TemperatureUI(self)

        self.show_home()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_top_bar(self, title=""):
        top_bar = tk.Frame(self.main_frame, bg="white", height=65, bd=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        menu_btn = tk.Button(
            top_bar,
            text="☰",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#333333",
            bd=0,
            activebackground="white",
            command=self.open_menu
        )
        menu_btn.place(x=15, y=12)

        title_label = tk.Label(
            top_bar,
            text=title,
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#222222"
        )
        title_label.place(relx=0.5, y=20, anchor="center")

        profile_btn = tk.Button(
            top_bar,
            text="👤",
            font=("Arial", 16),
            bg="#e9edf5",
            fg="#333333",
            bd=0,
            width=2,
            height=1,
            activebackground="#dfe6f3",
            command=self.show_profile
        )
        profile_btn.place(x=375, y=14)

    def open_menu(self):
        menu_win = tk.Toplevel(self.root)
        menu_win.title("메뉴")
        menu_win.geometry("260x360")
        menu_win.configure(bg="white")
        menu_win.resizable(True, True)

        tk.Label(
            menu_win,
            text="메뉴",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#222222"
        ).pack(pady=18)

        tk.Button(
            menu_win,
            text="갖고있는 옷 확인",
            font=("Arial", 12),
            bg="#f1f3f7",
            fg="#222222",
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_clothes_list()]
        ).pack(pady=8)

        tk.Button(
            menu_win,
            text="온도 기반 추천",
            font=("Arial", 12),
            bg="#f1f3f7",
            fg="#222222",
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_temperature_ui()]
        ).pack(pady=8)

        tk.Button(
            menu_win,
            text="오늘의 추천 코디",
            font=("Arial", 12),
            bg="#f1f3f7",
            fg="#222222",
            width=20,
            height=2,
            bd=0,
            command=lambda: [menu_win.destroy(), self.show_today_recommend_ui()]
        ).pack(pady=8)

        tk.Button(
            menu_win,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=15,
            bd=0,
            command=menu_win.destroy
        ).pack(pady=18)

    def show_profile(self):
        profile_win = tk.Toplevel(self.root)
        profile_win.title("사용자 정보")
        profile_win.geometry("300x250")
        profile_win.configure(bg="white")
        profile_win.resizable(True, True)

        tk.Label(
            profile_win,
            text="사용자 정보",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#222222"
        ).pack(pady=18)

        canvas = tk.Canvas(profile_win, width=70, height=70, bg="white", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 65, 65, fill="#dbe4ff", outline="")
        canvas.create_text(35, 35, text="👤", font=("Arial", 24))

        tk.Label(
            profile_win,
            text="이름: 사용자\n스타일: 캐주얼\n관심: 옷 추천 / 색 조합",
            font=("Arial", 12),
            bg="white",
            fg="#333333",
            justify="center"
        ).pack(pady=15)

        tk.Button(
            profile_win,
            text="닫기",
            font=("Arial", 11),
            bg="#e9edf5",
            width=12,
            bd=0,
            command=profile_win.destroy
        ).pack(pady=10)

    def show_home(self):
        self.main_ui.show()

    def show_register_options(self):
        self.register_ui.show_register_options()

    def show_clothes_list(self):
        self.clothes_ui.show()

    def show_today_recommend_ui(self):
        self.today_recommend_ui.show()

    def show_temperature_ui(self):
        self.temperature_ui.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingApp(root)
    root.mainloop()