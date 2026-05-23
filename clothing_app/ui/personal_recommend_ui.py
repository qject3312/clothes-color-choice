import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class PersonalRecommendUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("사용자 맞춤 코디")
        self.image_refs = []

        outer = tk.Frame(self.app.main_frame, bg="#f4f6fb")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#f4f6fb", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg="#f4f6fb")

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

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        user = self.app.current_user

        if user is None:
            user = {
                "name": "게스트",
                "styles": ["미선택"],
                "body_type": "미입력",
                "skin_tone": "미입력",
                "personal_color": "미입력",
                "height": "미입력",
                "weight": "미입력"
            }

        styles = user.get("styles", ["미선택"])
        if isinstance(styles, str):
            styles = [styles]

        tk.Label(
            body,
            text="사용자 맞춤 코디 추천",
            font=("Arial", 20, "bold"),
            bg="#f4f6fb",
            fg="#222222"
        ).pack(pady=(20, 8))

        user_card = tk.Frame(body, bg="white")
        user_card.pack(fill="x", padx=16, pady=10)

        tk.Label(
            user_card,
            text="반영된 사용자 정보",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=14, pady=(12, 5))

        user_info = (
            f"이름: {user.get('name', '미입력')}\n"
            f"추구 패션: {', '.join(styles)}\n"
            f"체형: {user.get('body_type', '미입력')}\n"
            f"피부톤: {user.get('skin_tone', '미입력')}\n"
            f"퍼스널 컬러: {user.get('personal_color', '미입력')}"
        )

        tk.Label(
            user_card,
            text=user_info,
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            justify="left",
            wraplength=350
        ).pack(anchor="w", padx=14, pady=(0, 12))

        result_area = tk.Frame(body, bg="#f4f6fb")
        result_area.pack(fill="both", expand=True, padx=16, pady=8)

        def calc_score(cloth):
            score = 50
            reasons = []

            feature = getattr(cloth, "feature", "") or ""
            color_name = getattr(cloth, "color_name", "") or ""
            personal_color = user.get("personal_color", "미입력")
            body_type = user.get("body_type", "미입력")

            for style in styles:
                if style != "미선택" and style in feature:
                    score += 20
                    reasons.append(f"선호하는 {style} 스타일과 맞습니다.")
                    break

            if personal_color == "봄 웜" and color_name in ["베이지", "아이보리", "노랑", "핑크", "하늘색"]:
                score += 15
                reasons.append("봄 웜톤에 어울리는 밝고 부드러운 색상입니다.")

            elif personal_color == "여름 쿨" and color_name in ["흰색", "회색", "네이비", "하늘색", "파랑"]:
                score += 15
                reasons.append("여름 쿨톤에 어울리는 차분하고 시원한 색상입니다.")

            elif personal_color == "가을 웜" and color_name in ["베이지", "브라운", "카키", "아이보리"]:
                score += 15
                reasons.append("가을 웜톤에 어울리는 따뜻한 계열의 색상입니다.")

            elif personal_color == "겨울 쿨" and color_name in ["검정", "흰색", "네이비", "파랑", "회색"]:
                score += 15
                reasons.append("겨울 쿨톤에 어울리는 선명하고 깔끔한 색상입니다.")

            if body_type == "마른 체형" and ("오버핏" in feature or "와이드" in feature):
                score += 10
                reasons.append("마른 체형에 자연스러운 실루엣을 줄 수 있는 핏입니다.")

            elif body_type == "보통 체형" and ("정핏" in feature or "보통" in feature):
                score += 10
                reasons.append("보통 체형에 무난하게 어울리는 기본 핏입니다.")

            elif body_type == "통통한 체형" and ("정핏" in feature or "일자핏" in feature or "롱기장" in feature):
                score += 10
                reasons.append("체형을 안정적으로 잡아주는 핏입니다.")

            if not reasons:
                reasons.append("등록된 옷 중 기본 조합에 무난하게 사용할 수 있습니다.")

            return score, reasons

        def pick_best(category):
            clothes = [
                cloth for cloth in self.app.clothes
                if getattr(cloth, "category", "") == category
            ]

            if not clothes:
                return None, 0, [f"등록된 {category}가 없습니다."]

            best_cloth = None
            best_score = -1
            best_reasons = []

            for cloth in clothes:
                score, reasons = calc_score(cloth)

                if score > best_score:
                    best_cloth = cloth
                    best_score = score
                    best_reasons = reasons

            return best_cloth, best_score, best_reasons

        def draw_cloth_card(title, cloth, score, reasons):
            card = tk.Frame(result_area, bg="white")
            card.pack(fill="x", pady=7)

            tk.Label(
                card,
                text=title,
                font=("Arial", 13, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(10, 5))

            content = tk.Frame(card, bg="white")
            content.pack(fill="x", padx=12, pady=(0, 10))

            if cloth is None:
                tk.Label(
                    content,
                    text="\n".join(reasons),
                    font=("Arial", 10),
                    bg="white",
                    fg="#777777",
                    justify="left",
                    wraplength=320
                ).pack(anchor="w")
                return

            if getattr(cloth, "image_path", "") and os.path.exists(cloth.image_path):
                try:
                    img = Image.open(cloth.image_path).convert("RGB")
                    img.thumbnail((95, 95))
                    tk_img = ImageTk.PhotoImage(img)
                    self.image_refs.append(tk_img)

                    tk.Label(
                        content,
                        image=tk_img,
                        bg="white"
                    ).pack(side="left", padx=(0, 10))
                except Exception as e:
                    print("맞춤 코디 이미지 표시 실패:", e)

            info = tk.Frame(content, bg="white")
            info.pack(side="left", fill="both", expand=True)

            tk.Label(
                info,
                text=f"{cloth.category} / {cloth.detail}",
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#222222"
            ).pack(anchor="w")

            tk.Label(
                info,
                text=f"색상: {cloth.color_name}",
                font=("Arial", 10),
                bg="white",
                fg="#444444"
            ).pack(anchor="w", pady=(3, 0))

            tk.Label(
                info,
                text=f"특징: {cloth.feature}",
                font=("Arial", 10),
                bg="white",
                fg="#444444",
                wraplength=220,
                justify="left"
            ).pack(anchor="w", pady=(3, 0))

            tk.Label(
                info,
                text=f"추천 점수: {score}점",
                font=("Arial", 9, "bold"),
                bg="white",
                fg="#2f80ff"
            ).pack(anchor="w", pady=(4, 0))

            tk.Label(
                info,
                text=f"이유: {' / '.join(reasons)}",
                font=("Arial", 9),
                bg="white",
                fg="#666666",
                wraplength=220,
                justify="left"
            ).pack(anchor="w", pady=(4, 0))

        top, top_score, top_reasons = pick_best("상의")
        bottom, bottom_score, bottom_reasons = pick_best("하의")
        outer_item, outer_score, outer_reasons = pick_best("아우터")

        reason_parts = []

        if styles and styles != ["미선택"]:
            reason_parts.append(
                f"사용자가 {', '.join(styles)} 스타일을 선호해서 해당 무드와 가까운 옷을 우선 추천했습니다."
            )

        if user.get("personal_color", "미입력") != "미입력":
            reason_parts.append(
                f"퍼스널 컬러 {user.get('personal_color')}에 어울리는 색상도 함께 고려했습니다."
            )

        if user.get("body_type", "미입력") != "미입력":
            reason_parts.append(
                f"체형 정보({user.get('body_type')})를 반영해 핏과 실루엣도 참고했습니다."
            )

        if top and bottom:
            reason_parts.append(
                f"{top.detail} 상의와 {bottom.detail} 하의를 조합해 하나의 코디로 구성했습니다."
            )

        if outer_item:
            reason_parts.append(
                f"아우터로 {outer_item.detail}를 더해 전체 코디 완성도를 높였습니다."
            )

        if not reason_parts:
            reason_parts.append(
                "사용자 정보가 부족해서 등록된 옷의 종류와 특징을 기준으로 기본 코디를 추천했습니다."
            )

        total_reason = " ".join(reason_parts)

        reason_card = tk.Frame(result_area, bg="white")
        reason_card.pack(fill="x", pady=(5, 10))

        tk.Label(
            reason_card,
            text="전체 코디 추천 이유",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#222222"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        tk.Label(
            reason_card,
            text=total_reason,
            font=("Arial", 10),
            bg="white",
            fg="#444444",
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 12))

        draw_cloth_card("추천 상의", top, top_score, top_reasons)
        draw_cloth_card("추천 하의", bottom, bottom_score, bottom_reasons)

        if outer_item is not None:
            draw_cloth_card("추천 아우터", outer_item, outer_score, outer_reasons)

        def save_outfit():
            if top is None or bottom is None:
                messagebox.showwarning(
                    "저장 불가",
                    "코디를 저장하려면 최소한 상의와 하의가 필요합니다."
                )
                return

            outfit = {
                "top": top,
                "bottom": bottom,
                "outer": outer_item,
                "reason": total_reason,
                "user_id": user.get("user_id", "guest")
            }

            if not hasattr(self.app, "saved_outfits"):
                self.app.saved_outfits = []

            self.app.saved_outfits.append(outfit)

            messagebox.showinfo("코디 등록 완료", "추천 코디가 나의 코디에 저장되었습니다.")

        action_row = tk.Frame(body, bg="#f4f6fb")
        action_row.pack(pady=(12, 20))

        tk.Button(
            action_row,
            text="이 코디 등록하기",
            font=("Arial", 11, "bold"),
            bg="#47c95a",
            fg="white",
            width=15,
            height=2,
            bd=0,
            command=save_outfit
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            action_row,
            text="나의 코디 확인",
            font=("Arial", 11, "bold"),
            bg="#2f80ff",
            fg="white",
            width=15,
            height=2,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_outfit_ui()]
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            body,
            text="홈으로",
            font=("Arial", 11),
            bg="#d9dee8",
            width=12,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
        ).pack(pady=(0, 15))

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))