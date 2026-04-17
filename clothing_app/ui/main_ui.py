import tkinter as tk


class MainUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("옷 추천 앱")

        body = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg="#f4f6fb")
        center.place(relx=0.5, rely=0.45, anchor="center")

        tk.Button(
            center,
            text="옷 등록하기",
            font=("Arial", 18, "bold"),
            bg="#2f80ff",
            fg="white",
            width=16,
            height=2,
            bd=0,
            command=self.app.show_register_options
        ).pack(pady=15)

        tk.Button(
            center,
            text="옷 추천받기",
            font=("Arial", 18, "bold"),
            bg="#47c95a",
            fg="white",
            width=16,
            height=2,
            bd=0,
            command=self.app.show_today_recommend_ui
        ).pack(pady=15)