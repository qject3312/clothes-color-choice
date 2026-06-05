import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

from app_paths import resolve_existing_path
from ui import style


def _get(item, name, default=""):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _color(item):
    return str(_get(item, "color_name", _get(item, "color", "")) or "").strip()


def _category(item):
    return str(_get(item, "category", "") or "").strip()


def _detail(item):
    return str(_get(item, "detail", "") or "").strip()


def _feature(item):
    return str(_get(item, "feature", "") or "").strip()


def _serialize(item):
    if item is None:
        return None
    if isinstance(item, dict):
        return dict(item)
    return {
        "id": _get(item, "id", None),
        "category": _category(item),
        "detail": _detail(item),
        "feature": _feature(item),
        "color_name": _color(item),
        "hex": _get(item, "hex", _get(item, "hex_code", "")),
        "rgb": _get(item, "rgb", ""),
        "image_path": _get(item, "image_path", ""),
    }


class BaseItemRecommendUI:
    """선택한 옷 하나를 기준으로 상의/하의/아우터의 색상과 종류를 추천하는 화면."""

    COLOR_RULES = {
        "흰색": {"top": ["네이비", "검정", "베이지", "하늘색"], "bottom": ["중청", "연청", "검정", "네이비", "베이지"], "outer": ["네이비", "베이지", "회색", "카키"], "mood": "깔끔하고 대부분의 옷과 잘 어울리는 기본 색입니다."},
        "검정": {"top": ["흰색", "회색", "베이지", "하늘색"], "bottom": ["중청", "회색", "카키", "베이지"], "outer": ["회색", "베이지", "카키", "데님"], "mood": "차분하고 안정적이라 밝은 색을 섞으면 답답함이 줄어듭니다."},
        "파랑": {"top": ["흰색", "아이보리", "회색", "네이비"], "bottom": ["흰색", "베이지", "회색", "검정"], "outer": ["아이보리", "베이지", "네이비", "회색"], "mood": "청량한 느낌이 강해서 흰색, 회색, 베이지와 조합하면 깔끔합니다."},
        "네이비": {"top": ["흰색", "하늘색", "회색", "아이보리"], "bottom": ["흰색", "베이지", "회색", "중청"], "outer": ["베이지", "회색", "아이보리"], "mood": "단정한 느낌이 강해서 학교, 출근, 데일리에 모두 무난합니다."},
        "베이지": {"top": ["흰색", "검정", "네이비", "브라운"], "bottom": ["중청", "흰색", "브라운", "카키"], "outer": ["브라운", "네이비", "카키", "아이보리"], "mood": "부드러운 색이라 브라운 계열이나 네이비와 잘 맞습니다."},
        "회색": {"top": ["흰색", "검정", "네이비", "파랑"], "bottom": ["검정", "중청", "네이비", "흰색"], "outer": ["검정", "네이비", "베이지"], "mood": "튀지 않고 차분해서 무채색 또는 네이비와 안정적으로 어울립니다."},
        "노랑": {"top": ["흰색", "아이보리", "네이비", "회색"], "bottom": ["중청", "연청", "흰색", "베이지", "검정"], "outer": ["아이보리", "네이비", "데님"], "mood": "밝은 포인트 색이라 나머지는 기본색으로 눌러주면 좋습니다."},
        "브라운": {"top": ["흰색", "아이보리", "베이지", "네이비"], "bottom": ["중청", "아이보리", "베이지", "카키"], "outer": ["베이지", "아이보리", "카키"], "mood": "따뜻한 느낌이 강해서 아이보리, 베이지 계열과 자연스럽습니다."},
        "보라": {"top": ["흰색", "회색", "아이보리", "검정"], "bottom": ["검정", "중청", "흰색", "회색"], "outer": ["회색", "검정", "아이보리"], "mood": "보라색은 포인트가 강하므로 나머지는 차분한 색이 좋습니다."},
    }

    ALIAS = {
        "청": "파랑", "청바지": "파랑", "데님": "파랑", "중청": "파랑", "연청": "파랑", "진청": "네이비",
        "하양": "흰색", "화이트": "흰색", "아이보리": "흰색", "크림": "흰색",
        "검정색": "검정", "검은색": "검정", "블랙": "검정",
        "남색": "네이비", "곤색": "네이비",
        "그레이": "회색", "연회색": "회색", "차콜": "회색",
        "카멜": "브라운", "갈색": "브라운",
        "노란색": "노랑", "옐로우": "노랑",
        "퍼플": "보라", "보라색": "보라",
    }

    COLOR_SWATCH = {
        "흰색": "#f7f7f7", "아이보리": "#f3ead7", "검정": "#222222", "회색": "#9ca3af", "네이비": "#1e3a8a",
        "베이지": "#d6b98c", "브라운": "#8b5a2b", "카키": "#7c8450", "파랑": "#2563eb", "하늘색": "#93c5fd",
        "중청": "#3b82f6", "연청": "#bfdbfe", "노랑": "#facc15", "데님": "#315f9d", "보라": "#8b5cf6",
    }

    TYPE_RULES = {
        "상의": {
            "데일리": ["기본 반팔", "긴팔 티셔츠", "맨투맨"],
            "출근": ["셔츠", "니트", "깔끔한 긴팔"],
            "데이트": ["니트", "셔츠", "가디건"],
            "학교": ["맨투맨", "후드", "기본 반팔"],
            "운동": ["기능성 반팔", "후드", "트레이닝 상의"],
            "기본": ["기본 반팔", "셔츠", "니트"],
        },
        "하의": {
            "데일리": ["청바지", "와이드 팬츠", "면바지"],
            "출근": ["슬랙스", "일자핏 팬츠", "면바지"],
            "데이트": ["슬랙스", "청바지", "와이드 팬츠"],
            "학교": ["청바지", "조거팬츠", "와이드 팬츠"],
            "운동": ["트레이닝 팬츠", "조거팬츠", "반바지"],
            "기본": ["청바지", "슬랙스", "와이드 팬츠"],
        },
        "아우터": {
            "데일리": ["가디건", "자켓", "후드집업"],
            "출근": ["블레이저", "코트", "가디건"],
            "데이트": ["가디건", "자켓", "코트"],
            "학교": ["후드집업", "자켓", "가디건"],
            "운동": ["바람막이", "후드집업", "트레이닝 자켓"],
            "기본": ["가디건", "자켓", "코트"],
        },
    }

    def __init__(self, app):
        self.app = app
        self.selected_key = tk.StringVar(value="")
        self.selected_category = tk.StringVar(value="상의")
        self.item_map = {}
        self.result = None
        self.image_refs = []
        self._selector_card = None
        self._result_area = None
        self._combo = None

    def show(self):
        self.app.clear_screen()
        self.image_refs = []
        self.result = None
        self.app.create_top_bar("색상 기반 코디 추천")

        outer = tk.Frame(self.app.main_frame, bg=style.BG)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=style.BG)
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width), add="+")
        canvas.configure(yscrollcommand=scrollbar.set)
        style.enable_canvas_drag(canvas, bind_children=body)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._header(body)
        clothes = self._base_clothes()
        if not clothes:
            self._empty(body)
            return
        self._selector(body)
        self._result_area = tk.Frame(body, bg=style.BG)
        self._result_area.pack(fill="x")

    def _base_clothes(self):
        return [c for c in (getattr(self.app, "clothes", []) or []) if self._simple_category(c) in ["상의", "하의", "아우터"]]

    def _simple_category(self, item):
        text = f"{_category(item)} {_detail(item)}"
        if "상의" in text or any(k in text for k in ["반팔", "긴팔", "셔츠", "니트", "맨투맨", "후드", "블라우스"]):
            return "상의"
        if "하의" in text or any(k in text for k in ["바지", "청바지", "슬랙스", "반바지", "치마", "조거"]):
            return "하의"
        if "아우터" in text or any(k in text for k in ["자켓", "재킷", "코트", "패딩", "가디건", "후리스", "집업", "점퍼"]):
            return "아우터"
        return _category(item)

    def _header(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=(16, 10))
        tk.Label(card, text="옷 하나를 기준으로 색상 조합 추천", font=(style.FONT, 16, "bold"), bg=style.CARD, fg=style.TEXT).pack(anchor="w", padx=18, pady=(16, 6))
        tk.Label(card, text="등록한 상의, 하의, 아우터 중 하나를 고르면 나머지 옷의 색상과 종류를 함께 추천합니다.", font=(style.FONT, 10), bg=style.CARD, fg=style.SUBTEXT, wraplength=360, justify="left").pack(anchor="w", padx=18, pady=(0, 16))

    def _empty(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=14)
        tk.Label(card, text="추천에 사용할 상의, 하의, 아우터를 먼저 등록해 주세요.", font=(style.FONT, 13, "bold"), bg=style.CARD, fg=style.TEXT, wraplength=340, justify="left").pack(pady=(24, 8), padx=18)
        tk.Button(card, text="옷 등록하러 가기", font=(style.FONT, 11, "bold"), bg=style.PRIMARY, fg="white", bd=0, padx=16, pady=8, command=self.app.show_register_options).pack(pady=(0, 24))

    def _selector(self, parent):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=10)
        self._selector_card = card
        tk.Label(card, text="기준이 될 옷 선택", font=(style.FONT, 14, "bold"), bg=style.CARD, fg=style.TEXT).pack(anchor="w", padx=18, pady=(14, 8))

        tab_row = tk.Frame(card, bg=style.CARD)
        tab_row.pack(fill="x", padx=18, pady=(0, 10))
        for cat in ["상의", "하의", "아우터"]:
            self._cat_button(tab_row, cat).pack(side="left", padx=(0, 6))

        self._combo_frame = tk.Frame(card, bg=style.CARD)
        self._combo_frame.pack(fill="x", padx=18, pady=(0, 12))
        self._refresh_combo()

        row = tk.Frame(card, bg=style.CARD)
        row.pack(fill="x", padx=18, pady=(0, 14))
        tk.Button(row, text="색상 추천받기", font=(style.FONT, 11, "bold"), bg=style.PRIMARY, fg="white", bd=0, padx=16, pady=8, command=self._recommend).pack(side="left")
        tk.Button(row, text="홈으로", font=(style.FONT, 10), bg=style.MUTED, fg=style.TEXT, bd=0, padx=14, pady=8, command=self.app.show_home).pack(side="right")

    def _cat_button(self, parent, cat):
        selected = self.selected_category.get() == cat
        return tk.Button(parent, text=cat, font=(style.FONT, 10, "bold"), bg=style.PRIMARY if selected else style.MUTED, fg="white" if selected else style.TEXT, bd=0, padx=14, pady=7, command=lambda c=cat: self._change_category(c))

    def _change_category(self, cat):
        self.selected_category.set(cat)
        self.selected_key.set("")
        self.show()

    def _refresh_combo(self):
        for w in self._combo_frame.winfo_children():
            w.destroy()
        target = self.selected_category.get()
        clothes = [c for c in self._base_clothes() if self._simple_category(c) == target]
        self.item_map = {}
        labels = []
        for idx, item in enumerate(clothes):
            feat = _feature(item)
            if feat.strip() in ["", "없음", "특징 없음", "None"]:
                feat = ""
            label = f"{idx + 1}. {_color(item)} {_detail(item)}" + (f" ({feat[:12]})" if feat else "")
            self.item_map[label] = item
            labels.append(label)
        if not labels:
            tk.Label(self._combo_frame, text=f"등록된 {target}가 없습니다.", font=(style.FONT, 10), bg=style.CARD, fg=style.SUBTEXT).pack(anchor="w")
            return
        self.selected_key.set(labels[0])
        self._combo = ttk.Combobox(self._combo_frame, textvariable=self.selected_key, values=labels, state="readonly", font=(style.FONT, 10))
        self._combo.pack(fill="x")

    def _normalize_color(self, color, detail=""):
        text = f"{color} {detail}"
        for key, value in self.ALIAS.items():
            if key in text:
                return value
        return color if color in self.COLOR_RULES else "흰색"

    def _recommend(self):
        for w in self._result_area.winfo_children():
            w.destroy()
        item = self.item_map.get(self.selected_key.get())
        if not item:
            messagebox.showwarning("선택 필요", "기준이 될 옷을 선택해 주세요.")
            return
        cat = self._simple_category(item)
        base_color = self._normalize_color(_color(item), _detail(item))
        rules = self.COLOR_RULES.get(base_color, self.COLOR_RULES["흰색"])
        targets = [("상의", "top"), ("하의", "bottom"), ("아우터", "outer")]
        targets = [(name, key) for name, key in targets if name != cat]
        recs = {}
        type_recs = {}
        for name, key in targets:
            recs[name] = rules.get(key, ["흰색", "검정", "베이지"])[0:4]
            type_recs[name] = self._recommend_types(name, item)
        self.result = {
            "base_item": item,
            "base_color": base_color,
            "recommendations": recs,
            "type_recommendations": type_recs,
            "mood": rules.get("mood", "기본 색상 중심으로 안정적인 조합을 추천했습니다."),
            "profile_note": self._profile_note(),
        }
        self._draw_result(self._result_area, self.result)

    def _preferred_style_key(self):
        user = getattr(self.app, "current_user", None) or {}
        raw = user.get("styles", "") or user.get("style", "") or ""
        text = raw if isinstance(raw, str) else ",".join(raw)
        for key in ["데일리", "출근", "데이트", "학교", "운동"]:
            if key in text:
                return key
        return "기본"

    def _recommend_types(self, target_category, base_item):
        user = getattr(self.app, "current_user", None) or {}
        style_key = self._preferred_style_key()
        types = list(self.TYPE_RULES.get(target_category, {}).get(style_key, self.TYPE_RULES.get(target_category, {}).get("기본", [])))
        body_type = user.get("body_type", "미입력")
        base_detail = _detail(base_item)

        if target_category == "하의":
            if body_type == "마른 체형":
                types = ["와이드 팬츠", "청바지", "조거팬츠"]
            elif body_type == "통통한 체형":
                types = ["일자핏 팬츠", "슬랙스", "와이드 팬츠"]
            elif body_type == "근육형":
                types = ["일자핏 팬츠", "청바지", "조거팬츠"]
        elif target_category == "상의":
            if body_type == "마른 체형":
                types = ["오버핏 맨투맨", "니트", "후드"]
            elif body_type == "통통한 체형":
                types = ["정핏 셔츠", "깔끔한 긴팔", "니트"]
            elif body_type == "근육형":
                types = ["정핏 반팔", "셔츠", "맨투맨"]
        elif target_category == "아우터":
            if body_type == "통통한 체형":
                types = ["롱코트", "블레이저", "깔끔한 자켓"]
            elif "반팔" in base_detail:
                types = ["가디건", "얇은 자켓", "후드집업"]

        # 중복 제거 후 3개만 표시
        clean = []
        for t in types:
            if t not in clean:
                clean.append(t)
        return clean[:3]

    def _profile_note(self):
        user = getattr(self.app, "current_user", None) or {}
        bits = []
        if user.get("body_type") and user.get("body_type") != "미입력":
            bits.append(user.get("body_type"))
        style_key = self._preferred_style_key()
        if style_key != "기본":
            bits.append(f"{style_key} 스타일")
        if user.get("personal_color") and user.get("personal_color") != "미입력":
            bits.append(user.get("personal_color"))
        return " · ".join(bits) if bits else "기본 프로필 기준"

    def _draw_result(self, parent, result):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=12)
        top = tk.Frame(card, bg=style.CARD)
        top.pack(fill="x", padx=18, pady=(16, 10))
        tk.Label(top, text="추천 결과", font=(style.FONT, 16, "bold"), bg=style.CARD, fg=style.TEXT).pack(side="left")
        tk.Button(top, text="저장", font=(style.FONT, 10, "bold"), bg=style.SUCCESS, fg="white", bd=0, padx=14, pady=7, command=self._save).pack(side="right")

        base = tk.Frame(card, bg="#f4f7fb")
        base.pack(fill="x", padx=18, pady=(0, 12))
        self._draw_item_preview(base, "기준 옷", result["base_item"])

        tk.Label(card, text=f"{result['base_color']} 계열: {result['mood']}", font=(style.FONT, 10), bg=style.CARD, fg=style.SUBTEXT, wraplength=360, justify="left").pack(anchor="w", padx=18, pady=(0, 4))
        tk.Label(card, text=f"반영 정보: {result.get('profile_note', '기본 프로필 기준')}", font=(style.FONT, 9, "bold"), bg=style.CARD, fg=style.PRIMARY, wraplength=360, justify="left").pack(anchor="w", padx=18, pady=(0, 12))

        for name, colors in result["recommendations"].items():
            box = tk.Frame(card, bg="#f8f9fd", highlightbackground="#e5eaf3", highlightthickness=1)
            box.pack(fill="x", padx=18, pady=7)
            tk.Label(box, text=name, font=(style.FONT, 12, "bold"), bg="#f8f9fd", fg=style.TEXT).pack(anchor="w", padx=12, pady=(10, 4))

            tk.Label(box, text="추천 종류", font=(style.FONT, 9, "bold"), bg="#f8f9fd", fg=style.SUBTEXT).pack(anchor="w", padx=12, pady=(2, 3))
            type_row = tk.Frame(box, bg="#f8f9fd")
            type_row.pack(anchor="w", padx=12, pady=(0, 8))
            for t in result.get("type_recommendations", {}).get(name, [])[:3]:
                tk.Label(type_row, text=t, font=(style.FONT, 9, "bold"), bg="#eef4ff", fg=style.PRIMARY, padx=9, pady=4).pack(side="left", padx=(0, 6))

            tk.Label(box, text="추천 색상", font=(style.FONT, 9, "bold"), bg="#f8f9fd", fg=style.SUBTEXT).pack(anchor="w", padx=12, pady=(0, 3))
            chip_row = tk.Frame(box, bg="#f8f9fd")
            chip_row.pack(anchor="w", padx=12, pady=(0, 10))
            for c in colors[:4]:
                bg = self.COLOR_SWATCH.get(c, "#eef2f7")
                fg = "white" if c in ["검정", "네이비", "브라운", "파랑", "보라", "데님"] else style.TEXT
                tk.Label(chip_row, text=c, font=(style.FONT, 9, "bold"), bg=bg, fg=fg, padx=9, pady=4).pack(side="left", padx=(0, 6))

        tk.Label(card, text="내 옷장 매칭", font=(style.FONT, 12, "bold"), bg=style.CARD, fg=style.TEXT).pack(anchor="w", padx=18, pady=(14, 4))
        tk.Label(card, text=self._matching_owned_text(result), font=(style.FONT, 10), bg=style.CARD, fg=style.SUBTEXT, wraplength=360, justify="left").pack(anchor="w", padx=18, pady=(0, 16))

    def _draw_item_preview(self, parent, title, item):
        row = tk.Frame(parent, bg="#f4f7fb")
        row.pack(fill="x", padx=12, pady=10)
        tk.Label(row, text=f"{title}", font=(style.FONT, 10, "bold"), bg="#f4f7fb", fg=style.TEXT, width=8, anchor="w").pack(side="left")
        image_path = resolve_existing_path(_get(item, "image_path", ""))
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path).convert("RGB")
                img.thumbnail((48, 48))
                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)
                tk.Label(row, image=tk_img, bg="#f4f7fb").pack(side="left", padx=(0, 8))
            except Exception:
                pass
        txt = f"{self._simple_category(item)} / {_color(item)} {_detail(item)}"
        tk.Label(row, text=txt, font=(style.FONT, 10), bg="#f4f7fb", fg=style.SUBTEXT, wraplength=260, justify="left").pack(side="left", fill="x", expand=True)

    def _matching_owned_text(self, result):
        clothes = self._base_clothes()
        lines = []
        for name, colors in result["recommendations"].items():
            matches = []
            for item in clothes:
                if self._simple_category(item) == name and any(c in (_color(item) + _detail(item)) for c in colors):
                    matches.append(f"{_color(item)} {_detail(item)}")
            if matches:
                lines.append(f"{name}: " + ", ".join(matches[:3]))
        return "\n".join(lines) if lines else "추천 색상과 정확히 맞는 등록 옷은 아직 없지만, 위 색상을 기준으로 새 코디를 구성할 수 있습니다."

    def _pseudo_item(self, category, colors, types=None):
        detail = "추천: " + ", ".join((types or [])[:2]) if types else "추천 종류"
        return {"category": category, "detail": detail, "feature": "색상/종류 추천 결과", "color_name": ", ".join(colors[:4]), "image_path": ""}

    def _save(self):
        if not self.result:
            messagebox.showwarning("저장 불가", "먼저 색상 추천을 받아 주세요.")
            return
        base = _serialize(self.result["base_item"])
        outfit = {"source": "base_color", "source_label": "색상 기반 코디 추천", "reason": f"{_color(self.result['base_item'])} {_detail(self.result['base_item'])}을 기준으로 상의/하의/아우터 색상과 종류를 추천해 저장했습니다."}
        base_cat = self._simple_category(self.result["base_item"])
        key_map = {"상의": "top", "하의": "bottom", "아우터": "outer"}
        outfit[key_map[base_cat]] = base
        for kor, key in key_map.items():
            if key not in outfit and kor in self.result["recommendations"]:
                outfit[key] = self._pseudo_item(kor, self.result["recommendations"][kor], self.result.get("type_recommendations", {}).get(kor, []))
        try:
            self.app.save_outfit(outfit)
            messagebox.showinfo("저장 완료", "색상 기반 추천 코디를 나의 코디에 저장했습니다.")
        except Exception as e:
            messagebox.showerror("저장 실패", f"코디 저장 중 오류가 발생했습니다.\n{e}")
