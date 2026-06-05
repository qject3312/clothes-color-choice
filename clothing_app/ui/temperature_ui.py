import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from app_paths import resolve_existing_path
from ui import style


class TemperatureUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []
        self.selected_items = {
            "top": None,
            "bottom": None,
            "outer": None,
            "shoes": None,
            "accessory": None
        }

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("온도별 옷 추천")
        self.image_refs = []

        self.selected_items = {
            "top": None,
            "bottom": None,
            "outer": None,
            "shoes": None,
            "accessory": None
        }

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.BG)

        body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")

        def resize_body(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_body)
        canvas.configure(yscrollcommand=scrollbar.set)
        style.enable_canvas_drag(canvas, bind_children=body)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(
            body,
            text="현재 온도를 입력하세요",
            font=(style.FONT, 18, "bold"),
            bg=style.BG,
            fg="#222222"
        ).pack(pady=(20, 8))

        temp_var = tk.StringVar()

        temp_entry = tk.Entry(
            body,
            textvariable=temp_var,
            font=(style.FONT, 14),
            justify="center",
            bd=1,
            relief="solid"
        )
        temp_entry.pack(fill="x", padx=30, ipady=8, pady=8)

        tk.Label(
            body,
            text="예: 5, 12, 20, 30",
            font=(style.FONT, 10),
            bg=style.BG,
            fg="#777777"
        ).pack(pady=(0, 10))

        preview_area = tk.Frame(body, bg=style.BG)
        preview_area.pack(fill="x", padx=16, pady=8)

        result_area = tk.Frame(body, bg=style.BG)
        result_area.pack(fill="both", expand=True, padx=16, pady=8)

        def get_temp_info(temp):
            if temp <= 5:
                return {
                    "reason": "5℃ 이하의 추운 날씨라 보온성이 높은 옷 위주로 추천합니다.",
                    "rules": {
                        "상의": ["기모 맨투맨", "니트", "후드티", "긴팔", "맨투맨"],
                        "하의": ["두꺼운 바지", "청바지", "슬랙스", "면바지"],
                        "아우터": ["패딩", "두꺼운 코트", "코트"],
                        "신발": ["운동화", "스니커즈", "구두", "로퍼", "부츠"]
                    }
                }

            if temp <= 11:
                return {
                    "reason": "6~11℃는 쌀쌀한 날씨라 니트, 맨투맨, 코트, 후리스 같은 옷을 추천합니다.",
                    "rules": {
                        "상의": ["니트", "맨투맨", "후드티", "긴팔", "셔츠"],
                        "하의": ["청바지", "슬랙스", "면바지", "두꺼운 바지"],
                        "아우터": ["코트", "후리스", "자켓", "점퍼", "집업"],
                        "신발": ["운동화", "스니커즈", "구두", "로퍼", "부츠"]
                    }
                }

            if temp <= 16:
                return {
                    "reason": "12~16℃는 선선한 날씨라 긴팔과 가벼운 아우터 조합이 좋습니다.",
                    "rules": {
                        "상의": ["긴팔", "셔츠", "맨투맨", "니트", "후드티"],
                        "하의": ["청바지", "슬랙스", "면바지", "조거팬츠"],
                        "아우터": ["가디건", "자켓", "얇은 자켓", "집업"],
                        "신발": ["운동화", "스니커즈", "구두", "로퍼"]
                    }
                }

            if temp <= 22:
                return {
                    "reason": "17~22℃는 온화하지만 아침저녁으로 쌀쌀할 수 있어 긴팔이나 얇은 겉옷을 추천합니다.",
                    "rules": {
                        "상의": ["긴팔", "셔츠", "블라우스", "맨투맨", "니트"],
                        "하의": ["청바지", "슬랙스", "면바지", "얇은 바지", "치마"],
                        "아우터": ["얇은 가디건", "얇은 자켓", "가디건", "자켓"],
                        "신발": ["운동화", "스니커즈", "구두", "로퍼"]
                    }
                }

            if temp <= 27:
                return {
                    "reason": "23~27℃는 따뜻한 날씨라 반팔, 얇은 셔츠, 가벼운 하의를 추천합니다.",
                    "rules": {
                        "상의": ["반팔", "셔츠", "블라우스", "민소매"],
                        "하의": ["얇은 바지", "청바지", "반바지", "치마"],
                        "아우터": ["얇은 가디건", "얇은 자켓"],
                        "신발": ["운동화", "스니커즈", "로퍼", "샌들"]
                    }
                }

            return {
                "reason": "28℃ 이상은 더운 날씨라 통풍이 잘 되는 옷과 가벼운 신발을 추천합니다.",
                "rules": {
                    "상의": ["반팔", "민소매"],
                    "하의": ["반바지", "치마", "얇은 바지"],
                    "아우터": [],
                    "신발": ["운동화", "스니커즈", "샌들", "슬리퍼"]
                }
            }

        def match_cloth(cloth, allowed_details):
            if not allowed_details:
                return False

            detail = getattr(cloth, "detail", "")
            feature = getattr(cloth, "feature", "")

            if detail in allowed_details:
                return True

            for word in allowed_details:
                if word in feature:
                    return True

            return False

        def get_filtered_clothes(category, allowed_details):
            clothes = [
                cloth for cloth in self.app.clothes
                if getattr(cloth, "category", "") == category
            ]

            if category == "악세서리":
                return clothes

            return [
                cloth for cloth in clothes
                if match_cloth(cloth, allowed_details)
            ]

        def refresh_preview():
            for widget in preview_area.winfo_children():
                widget.destroy()

            card = tk.Frame(preview_area, bg=style.CARD)
            card.pack(fill="x", pady=5)

            tk.Label(
                card,
                text="선택한 코디",
                font=(style.FONT, 14, "bold"),
                bg=style.CARD,
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(12, 8))

            self.draw_selected_item(card, "상의", self.selected_items.get("top"))
            self.draw_selected_item(card, "하의", self.selected_items.get("bottom"))
            self.draw_selected_item(card, "아우터", self.selected_items.get("outer"))
            self.draw_selected_item(card, "신발", self.selected_items.get("shoes"))
            self.draw_selected_item(card, "악세서리", self.selected_items.get("accessory"))

        def auto_select_first(filtered_map):
            self.selected_items["top"] = filtered_map["상의"][0] if filtered_map["상의"] else None
            self.selected_items["bottom"] = filtered_map["하의"][0] if filtered_map["하의"] else None
            self.selected_items["outer"] = filtered_map["아우터"][0] if filtered_map["아우터"] else None
            self.selected_items["shoes"] = filtered_map["신발"][0] if filtered_map["신발"] else None
            self.selected_items["accessory"] = filtered_map["악세서리"][0] if filtered_map["악세서리"] else None

        def save_selected_outfit(temp, reason):
            top = self.selected_items.get("top")
            bottom = self.selected_items.get("bottom")
            outer_item = self.selected_items.get("outer")
            shoes = self.selected_items.get("shoes")
            accessory = self.selected_items.get("accessory")

            if top is None or bottom is None:
                messagebox.showwarning(
                    "저장 불가",
                    "코디를 저장하려면 상의와 하의를 반드시 선택해야 합니다."
                )
                return

            user_id = "guest"
            if self.app.current_user:
                user_id = self.app.current_user.get("user_id", "guest")

            reason_parts = [
                f"{temp:g}℃ 날씨에 맞춰 추천된 옷 중 사용자가 선택한 코디입니다.",
                reason,
                f"{top.detail} 상의와 {bottom.detail} 하의를 중심으로 구성했습니다."
            ]

            if outer_item:
                reason_parts.append(f"아우터로 {outer_item.detail}를 선택했습니다.")

            if shoes:
                reason_parts.append(f"신발은 {shoes.detail}로 전체 분위기를 맞췄습니다.")

            if accessory:
                reason_parts.append(f"악세서리로 {accessory.detail}를 더했습니다.")

            outfit = {
                "top": top,
                "bottom": bottom,
                "outer": outer_item,
                "shoes": shoes,
                "accessory": accessory,
                "reason": " ".join(reason_parts),
                "source_label": "온도별 옷 추천",
                "source": "temperature",
                "temperature": temp,
                "user_id": user_id
            }

            if hasattr(self.app, "save_outfit"):
                self.app.save_outfit(outfit)
            else:
                if not hasattr(self.app, "saved_outfits"):
                    self.app.saved_outfits = []
                self.app.saved_outfits.append(outfit)
            messagebox.showinfo("저장 완료", "선택한 날씨 코디가 나의 코디에 저장되었습니다.")

        def recommend_by_temperature():
            for widget in result_area.winfo_children():
                widget.destroy()

            try:
                temp = float(temp_var.get())
            except ValueError:
                tk.Label(
                    result_area,
                    text="온도를 숫자로 입력해 주세요.",
                    font=(style.FONT, 12),
                    bg=style.BG,
                    fg="#c0392b"
                ).pack(pady=20)
                return

            temp_info = get_temp_info(temp)
            rules = temp_info["rules"]
            reason = temp_info["reason"]

            filtered_map = {
                "상의": get_filtered_clothes("상의", rules.get("상의", [])),
                "하의": get_filtered_clothes("하의", rules.get("하의", [])),
                "아우터": get_filtered_clothes("아우터", rules.get("아우터", [])),
                "신발": get_filtered_clothes("신발", rules.get("신발", [])),
                "악세서리": get_filtered_clothes("악세서리", [])
            }

            auto_select_first(filtered_map)
            refresh_preview()

            reason_card = tk.Frame(result_area, bg=style.CARD)
            reason_card.pack(fill="x", pady=(5, 10))

            tk.Label(
                reason_card,
                text=f"{temp:g}℃ 추천 기준",
                font=(style.FONT, 13, "bold"),
                bg=style.CARD,
                fg="#222222"
            ).pack(anchor="w", padx=12, pady=(10, 4))

            tk.Label(
                reason_card,
                text=reason + "\n악세서리는 온도와 상관없이 전체 목록에서 선택할 수 있습니다.",
                font=(style.FONT, 10),
                bg=style.CARD,
                fg=style.MUTED_TEXT,
                wraplength=340,
                justify="left"
            ).pack(anchor="w", padx=12, pady=(0, 12))

            choice_area = tk.Frame(result_area, bg=style.BG)
            choice_area.pack(fill="both", expand=True)

            def draw_all_choices():
                for widget in choice_area.winfo_children():
                    widget.destroy()

                configs = [
                    ("top", "추천 상의", "상의"),
                    ("bottom", "추천 하의", "하의"),
                    ("outer", "추천 아우터", "아우터"),
                    ("shoes", "추천 신발", "신발"),
                    ("accessory", "악세서리", "악세서리")
                ]

                for key, title, category in configs:
                    section = tk.Frame(choice_area, bg=style.BG)
                    section.pack(fill="x", pady=8)

                    tk.Label(
                        section,
                        text=title,
                        font=(style.FONT, 15, "bold"),
                        bg=style.BG,
                        fg="#222222"
                    ).pack(anchor="w", pady=(0, 5))

                    clothes = filtered_map.get(category, [])

                    if not clothes:
                        tk.Label(
                            section,
                            text=f"조건에 맞는 {category}가 없습니다.",
                            font=(style.FONT, 10),
                            bg=style.BG,
                            fg="#777777"
                        ).pack(anchor="w", padx=4, pady=5)
                        continue

                    for cloth in clothes:
                        is_selected = self.selected_items.get(key) == cloth

                        def choose_item(selected_key=key, selected_cloth=cloth):
                            if self.selected_items.get(selected_key) == selected_cloth:
                                self.selected_items[selected_key] = None
                            else:
                                self.selected_items[selected_key] = selected_cloth

                            refresh_preview()
                            draw_all_choices()

                        self.draw_choice_card(section, key, cloth, is_selected, choose_item)

            draw_all_choices()

            action_row = tk.Frame(result_area, bg=style.BG)
            action_row.pack(pady=(12, 20))

            tk.Button(
                action_row,
                text="선택 코디 저장",
                font=(style.FONT, 11, "bold"),
                bg=style.SUCCESS,
                fg="white",
                width=15,
                height=2,
                bd=0,
                command=lambda: save_selected_outfit(temp, reason)
            ).grid(row=0, column=0, padx=5)

            tk.Button(
                action_row,
                text="나의 코디 확인",
                font=(style.FONT, 11, "bold"),
                bg=style.PRIMARY,
                fg="white",
                width=15,
                height=2,
                bd=0,
                command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_outfit_ui()]
            ).grid(row=0, column=1, padx=5)

            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        tk.Button(
            body,
            text="추천받기",
            font=(style.FONT, 12, "bold"),
            bg=style.SUCCESS,
            fg="white",
            width=14,
            height=2,
            bd=0,
            command=recommend_by_temperature
        ).pack(pady=8)

        tk.Button(
            body,
            text="홈으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            width=12,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
        ).pack(pady=(5, 15))

    def draw_selected_item(self, parent, title, cloth):
        row = tk.Frame(parent, bg=style.CARD)
        row.pack(fill="x", padx=12, pady=4)

        tk.Label(
            row,
            text=f"{title}:",
            font=(style.FONT, 10, "bold"),
            bg=style.CARD,
            fg="#222222",
            width=8,
            anchor="w"
        ).pack(side="left")

        if cloth is None:
            tk.Label(
                row,
                text="선택 안 함",
                font=(style.FONT, 10),
                bg=style.CARD,
                fg="#777777"
            ).pack(side="left")
            return

        if getattr(cloth, "image_path", "") and os.path.exists(resolve_existing_path(cloth.image_path)):
            try:
                img = Image.open(resolve_existing_path(cloth.image_path)).convert("RGB")
                img.thumbnail((45, 45))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                tk.Label(
                    row,
                    image=tk_img,
                    bg=style.CARD
                ).pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(
            row,
            text=f"{cloth.detail} / {cloth.color_name}",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            wraplength=220,
            justify="left"
        ).pack(side="left", fill="x", expand=True)

    def draw_choice_card(self, parent, key, cloth, is_selected, choose_callback):
        card = tk.Frame(
            parent,
            bg="#dff7e5" if is_selected else "white"
        )
        card.pack(fill="x", pady=5)

        content = tk.Frame(card, bg=card["bg"])
        content.pack(fill="x", padx=10, pady=8)

        if getattr(cloth, "image_path", "") and os.path.exists(resolve_existing_path(cloth.image_path)):
            try:
                img = Image.open(resolve_existing_path(cloth.image_path)).convert("RGB")
                img.thumbnail((65, 65))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                tk.Label(
                    content,
                    image=tk_img,
                    bg=card["bg"]
                ).pack(side="left", padx=(0, 10))
            except Exception:
                pass

        info = tk.Frame(content, bg=card["bg"])
        info.pack(side="left", fill="both", expand=True)

        tk.Label(
            info,
            text=f"{cloth.category} / {cloth.detail}",
            font=(style.FONT, 11, "bold"),
            bg=card["bg"],
            fg="#222222"
        ).pack(anchor="w")

        tk.Label(
            info,
            text=f"색상: {cloth.color_name}",
            font=(style.FONT, 9),
            bg=card["bg"],
            fg=style.MUTED_TEXT
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            info,
            text=f"특징: {cloth.feature}",
            font=(style.FONT, 9),
            bg=card["bg"],
            fg="#555555",
            wraplength=210,
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

        tk.Button(
            content,
            text="선택됨" if is_selected else "선택",
            font=(style.FONT, 9, "bold"),
            bg=style.SUCCESS if is_selected else "#2f80ff",
            fg="white",
            bd=0,
            width=7,
            command=choose_callback
        ).pack(side="right", padx=(8, 0))
