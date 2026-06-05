import tkinter as tk
from tkinter import messagebox
from ui import style

from logic.recommend_logic import recommend_outfits, format_item


class RecommendUI:
    def __init__(self, app):
        self.app = app
        self.recommendations = []
        self.selected_temp = tk.StringVar(value="22")

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("맞춤 코디 추천")

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.BG)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._render_header(body)

        if not getattr(self.app, "clothes", None):
            self._render_empty(body)
            return

        self._render_input_area(body)
        self._render_recommendations(body)

    def _render_header(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=(16, 10))

        tk.Label(
            card,
            text="오늘의 맞춤 코디 TOP 3",
            font=(style.FONT, 18, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=18, pady=(16, 4))

        tk.Label(
            card,
            text="등록된 옷을 조합한 뒤 색상, 온도, 체형, 퍼스널 컬러, 선호 스타일을 점수화해 추천합니다.",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.SUBTEXT,
            wraplength=520,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 16))

    def _render_empty(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=20)

        tk.Label(
            card,
            text="먼저 옷을 등록해 주세요.",
            font=(style.FONT, 15, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(pady=(30, 12))

        tk.Label(
            card,
            text="상의와 하의가 최소 1개씩 있어야 코디 추천을 만들 수 있습니다.",
            font=(style.FONT, 11),
            bg=style.CARD,
            fg=style.SUBTEXT
        ).pack(pady=(0, 20))

        tk.Button(
            card,
            text="옷 등록하러 가기",
            font=(style.FONT, 12, "bold"),
            bg=style.PRIMARY,
            fg="white",
            width=16,
            height=2,
            bd=0,
            command=self.app.show_register_options
        ).pack(pady=(0, 30))

    def _render_input_area(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=10)

        tk.Label(
            card,
            text="추천 조건",
            font=(style.FONT, 14, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = tk.Frame(card, bg=style.CARD)
        row.pack(fill="x", padx=18, pady=(0, 14))

        tk.Label(
            row,
            text="현재 기온(℃)",
            font=(style.FONT, 11, "bold"),
            bg=style.CARD,
            fg="#333333"
        ).pack(side="left")

        temp_entry = tk.Entry(
            row,
            textvariable=self.selected_temp,
            font=(style.FONT, 11),
            width=8,
            relief="solid",
            bd=1
        )
        temp_entry.pack(side="left", padx=(10, 8))

        tk.Button(
            row,
            text="다시 추천",
            font=(style.FONT, 10, "bold"),
            bg=style.PRIMARY,
            fg="white",
            bd=0,
            padx=12,
            pady=6,
            command=lambda: self.show()
        ).pack(side="left", padx=4)

        tk.Button(
            row,
            text="홈으로",
            font=(style.FONT, 10),
            bg=style.MUTED,
            fg="#222222",
            bd=0,
            padx=12,
            pady=6,
            command=self.app.show_home
        ).pack(side="right", padx=4)

    def _get_current_user(self):
        # 프로젝트마다 로그인 사용자 저장 이름이 다를 수 있어서 여러 후보를 확인
        for name in ["current_user", "user", "login_user", "logged_in_user"]:
            if hasattr(self.app, name):
                value = getattr(self.app, name)
                if value:
                    return value
        return {}

    def _render_recommendations(self, parent):
        try:
            temp = float(self.selected_temp.get())
        except Exception:
            messagebox.showwarning("입력 오류", "기온은 숫자로 입력해 주세요.")
            temp = 22
            self.selected_temp.set("22")

        user = self._get_current_user()
        clothes = getattr(self.app, "clothes", [])

        self.recommendations = recommend_outfits(user, clothes, temp=temp, top_n=3)

        if not self.recommendations:
            self._render_not_enough(parent)
            return

        for idx, result in enumerate(self.recommendations, start=1):
            self._render_result_card(parent, idx, result)

    def _render_not_enough(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=14)

        tk.Label(
            card,
            text="추천 조합을 만들기 위한 옷이 부족합니다.",
            font=(style.FONT, 14, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            card,
            text="상의와 하의를 각각 1개 이상 등록하면 점수 기반 코디 추천을 받을 수 있습니다.",
            font=(style.FONT, 11),
            bg=style.CARD,
            fg=style.SUBTEXT,
            wraplength=520,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def _render_result_card(self, parent, rank, result):
        score = result["score"]
        outfit = result["outfit"]
        details = result["details"]

        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=10)

        title_row = tk.Frame(card, bg=style.CARD)
        title_row.pack(fill="x", padx=18, pady=(16, 8))

        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"

        tk.Label(
            title_row,
            text=f"{medal} 추천 코디 {rank}위",
            font=(style.FONT, 15, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(side="left")

        tk.Label(
            title_row,
            text=f"{score}점",
            font=(style.FONT, 15, "bold"),
            bg=style.CARD,
            fg="#2f80ff"
        ).pack(side="right")

        items_frame = tk.Frame(card, bg="#f8f9fd")
        items_frame.pack(fill="x", padx=18, pady=(0, 10))

        self._item_line(items_frame, "상의", format_item(outfit.get("top")))
        self._item_line(items_frame, "하의", format_item(outfit.get("bottom")))
        if outfit.get("outer") is not None:
            self._item_line(items_frame, "아우터", format_item(outfit.get("outer")))
        if outfit.get("shoe") is not None:
            self._item_line(items_frame, "신발", format_item(outfit.get("shoe")))

        tk.Label(
            card,
            text="추천 이유",
            font=(style.FONT, 12, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=18, pady=(4, 4))

        for reason in result.get("summary", [])[:4]:
            tk.Label(
                card,
                text=f"✓ {reason}",
                font=(style.FONT, 10),
                bg=style.CARD,
                fg="#555555",
                wraplength=520,
                justify="left"
            ).pack(anchor="w", padx=22, pady=1)

        btn_row = tk.Frame(card, bg=style.CARD)
        btn_row.pack(fill="x", padx=18, pady=(12, 16))

        tk.Button(
            btn_row,
            text="추천 근거 보기",
            font=(style.FONT, 10, "bold"),
            bg=style.SECONDARY,
            fg="#2f80ff",
            bd=0,
            padx=12,
            pady=7,
            command=lambda r=result: self._show_detail_popup(r)
        ).pack(side="left")

        # 앱에 저장 함수가 있으면 연결, 없으면 안내만 표시
        tk.Button(
            btn_row,
            text="코디 저장",
            font=(style.FONT, 10, "bold"),
            bg=style.SUCCESS,
            fg="white",
            bd=0,
            padx=12,
            pady=7,
            command=lambda r=result: self._save_outfit(r)
        ).pack(side="right")

    def _item_line(self, parent, label, value):
        row = tk.Frame(parent, bg="#f8f9fd")
        row.pack(fill="x", padx=12, pady=4)

        tk.Label(
            row,
            text=f"{label}",
            font=(style.FONT, 10, "bold"),
            bg="#f8f9fd",
            fg="#333333",
            width=8,
            anchor="w"
        ).pack(side="left")

        tk.Label(
            row,
            text=value,
            font=(style.FONT, 10),
            bg="#f8f9fd",
            fg=style.MUTED_TEXT,
            anchor="w",
            wraplength=430,
            justify="left"
        ).pack(side="left", fill="x", expand=True)

    def _show_detail_popup(self, result):
        win = tk.Toplevel(self.app.root if hasattr(self.app, "root") else None)
        win.title("추천 근거")
        win.geometry("420x520")
        win.configure(bg=style.BG)

        tk.Label(
            win,
            text=f"총점 {result['score']}점",
            font=(style.FONT, 18, "bold"),
            bg=style.BG,
            fg="#2f80ff"
        ).pack(pady=(18, 8))

        for name, data in result["details"].items():
            card = tk.Frame(win, bg=style.CARD)
            card.pack(fill="x", padx=14, pady=6)

            tk.Label(
                card,
                text=f"{name}: {int(round(data['score']))}/{data['max']}",
                font=(style.FONT, 12, "bold"),
                bg=style.CARD,
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(10, 4))

            for reason in data.get("reasons", [])[:2]:
                tk.Label(
                    card,
                    text=f"- {reason}",
                    font=(style.FONT, 9),
                    bg=style.CARD,
                    fg="#555555",
                    wraplength=360,
                    justify="left"
                ).pack(anchor="w", padx=16, pady=1)

            tk.Frame(card, height=6, bg=style.CARD).pack()

        tk.Button(
            win,
            text="닫기",
            font=(style.FONT, 10, "bold"),
            bg=style.MUTED,
            fg="#222222",
            bd=0,
            padx=16,
            pady=8,
            command=win.destroy
        ).pack(pady=12)

    def _save_outfit(self, result):
        # 프로젝트에 저장 메서드가 있으면 사용
        for method_name in ["save_outfit", "save_recommended_outfit", "add_saved_outfit"]:
            if hasattr(self.app, method_name):
                try:
                    getattr(self.app, method_name)(result)
                    messagebox.showinfo("저장 완료", "추천 코디를 저장했습니다.")
                    return
                except Exception as e:
                    messagebox.showerror("저장 실패", f"코디 저장 중 오류가 발생했습니다.\n{e}")
                    return

        messagebox.showinfo(
            "안내",
            "현재 프로젝트에는 코디 저장 DB 함수가 아직 연결되어 있지 않습니다.\n"
            "추천 결과 화면은 정상 동작하며, 저장 기능은 backend에 saved_outfits 테이블을 추가하면 연결할 수 있습니다."
        )
