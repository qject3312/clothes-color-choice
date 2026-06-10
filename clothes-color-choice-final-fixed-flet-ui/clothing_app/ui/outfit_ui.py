import os
import tkinter as tk
from PIL import Image, ImageTk
from app_paths import resolve_existing_path
from ui import style
from api_client import delete_saved_outfit_backend


class OutfitUI:
    def __init__(self, app):
        self.app = app
        self.image_refs = []

    def show(self):
        self.app.clear_screen()
        self.app.create_top_bar("나의 코디 확인")
        self.image_refs = []

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
            text="저장한 코디 목록",
            font=(style.FONT, 20, "bold"),
            bg=style.BG,
            fg="#222222"
        ).pack(pady=(20, 10))

        if not getattr(self.app, "saved_outfits", []):
            tk.Label(
                body,
                text="아직 저장한 코디가 없습니다.\n오늘의 맞춤 코디와 코디해보기에서 코디를 저장해 보세요.",
                font=(style.FONT, 12),
                bg=style.BG,
                fg=style.SUBTEXT,
                justify="center",
                wraplength=330
            ).pack(pady=40)

            tk.Button(
                body,
                text="코디해보기",
                font=(style.FONT, 12, "bold"),
                bg=style.PRIMARY,
                fg="white",
                width=18,
                height=2,
                bd=0,
                command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_coordination_ui()]
            ).pack(pady=10)

            tk.Button(
                body,
                text="홈으로",
                font=(style.FONT, 11),
                bg=style.MUTED,
                width=12,
                bd=0,
                command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
            ).pack(pady=10)
            return

        groups = [
            ("오늘의 맞춤 코디 추천", []),
            ("오늘의 추천 코디", []),
            ("코디해보기 직접 선택", []),
            ("색상 기반 코디 추천", []),
            ("기타 저장 코디", []),
        ]
        group_map = {name: items for name, items in groups}

        for outfit in self.app.saved_outfits:
            label = outfit.get("source_label") or outfit.get("source") or "기타 저장 코디"
            if label == "recommend":
                label = "오늘의 맞춤 코디 추천"
            elif label == "temperature":
                label = "기타 저장 코디"
            elif label == "today":
                label = "오늘의 추천 코디"
            elif label == "manual":
                label = "코디해보기 직접 선택"
            elif label == "base_color":
                label = "색상 기반 코디 추천"
            if label not in group_map:
                label = "기타 저장 코디"
            group_map[label].append(outfit)

        for section_name, outfits in groups:
            if not outfits:
                continue
            tk.Label(
                body,
                text=section_name,
                font=(style.FONT, 16, "bold"),
                bg=style.BG,
                fg="#222222"
            ).pack(anchor="w", padx=20, pady=(18, 4))
            for idx, outfit in enumerate(outfits, start=1):
                self.draw_outfit_card(body, idx, outfit, section_name)

        tk.Button(
            body,
            text="홈으로",
            font=(style.FONT, 11),
            bg=style.MUTED,
            width=12,
            bd=0,
            command=lambda: [canvas.unbind_all("<MouseWheel>"), self.app.show_home()]
        ).pack(pady=20)

    def draw_outfit_card(self, parent, idx, outfit, section_name=""):
        card = tk.Frame(parent, bg=style.CARD)
        card.pack(fill="x", padx=16, pady=10)

        top = tk.Frame(card, bg=style.CARD)
        top.pack(fill="x", padx=12, pady=(12, 6))

        tk.Label(
            top,
            text=f"코디 {idx}",
            font=(style.FONT, 14, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(side="left")

        tk.Button(
            top,
            text="삭제",
            font=(style.FONT, 9, "bold"),
            bg=style.DANGER,
            fg="white",
            bd=0,
            command=lambda: self.delete_outfit(outfit)
        ).pack(side="right")

        if section_name:
            tk.Label(
                top,
                text=section_name,
                font=(style.FONT, 9, "bold"),
                bg=style.SECONDARY,
                fg="#2f80ff",
                padx=8,
                pady=3
            ).pack(side="right", padx=(0, 8))

        items_frame = tk.Frame(card, bg=style.CARD)
        items_frame.pack(fill="x", padx=12, pady=6)

        self.draw_item(items_frame, "상의", outfit.get("top"))
        self.draw_item(items_frame, "하의", outfit.get("bottom"))
        self.draw_item(items_frame, "아우터", outfit.get("outer"))
        self.draw_item(items_frame, "신발", outfit.get("shoes") or outfit.get("shoe"))
        self.draw_item(items_frame, "악세서리", outfit.get("accessory"))

        tk.Label(
            card,
            text="추천/저장 이유",
            font=(style.FONT, 11, "bold"),
            bg=style.CARD,
            fg="#222222"
        ).pack(anchor="w", padx=12, pady=(8, 3))

        tk.Label(
            card,
            text=outfit.get("reason", "저장 이유가 없습니다."),
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 12))

    def draw_item(self, parent, title, cloth):
        row = tk.Frame(parent, bg=style.CARD)
        row.pack(fill="x", pady=5)

        tk.Label(
            row,
            text=f"{title}:",
            font=(style.FONT, 10, "bold"),
            bg=style.CARD,
            fg="#222222",
            width=8,
            anchor="w"
        ).pack(side="left")

        if cloth is None or cloth == []:
            tk.Label(
                row,
                text="없음",
                font=(style.FONT, 10),
                bg=style.CARD,
                fg="#777777"
            ).pack(side="left")
            return

        if isinstance(cloth, list):
            names = []
            for item in cloth:
                if isinstance(item, dict):
                    names.append(f"{item.get('detail', '')} / {item.get('color_name', '')}")
                else:
                    names.append(f"{getattr(item, 'detail', '')} / {getattr(item, 'color_name', '')}")
            tk.Label(
                row,
                text=", ".join(names),
                font=(style.FONT, 10),
                bg=style.CARD,
                fg=style.MUTED_TEXT,
                wraplength=250,
                justify="left"
            ).pack(side="left", fill="x", expand=True)
            return

        image_path = cloth.get("image_path", "") if isinstance(cloth, dict) else getattr(cloth, "image_path", "")
        if image_path and not os.path.exists(image_path):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            candidate = os.path.join(base, image_path)
            if os.path.exists(candidate):
                image_path = candidate
        image_path = resolve_existing_path(image_path)
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path).convert("RGB")
                img.thumbnail((55, 55))
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
            text=f"{cloth.get('detail', '') if isinstance(cloth, dict) else cloth.detail} / {cloth.get('color_name', '') if isinstance(cloth, dict) else cloth.color_name}",
            font=(style.FONT, 10),
            bg=style.CARD,
            fg=style.MUTED_TEXT,
            wraplength=210,
            justify="left"
        ).pack(side="left", fill="x", expand=True)

    def delete_outfit(self, outfit):
        outfit_id = outfit.get("id") if isinstance(outfit, dict) else None
        if outfit_id is not None:
            delete_saved_outfit_backend(outfit_id, self.app.get_current_user_id())
        if outfit in self.app.saved_outfits:
            self.app.saved_outfits.remove(outfit)

        self.show()
