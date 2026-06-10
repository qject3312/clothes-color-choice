import os
import sys
# macOS 기본 Tk 경고 제거 및 렌더링 안정화
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
import tkinter as tk
from tkinter import ttk

# Modern app palette
BG = "#f5f7fb"
CARD = "#ffffff"
CARD_BORDER = "#e5eaf3"
TEXT = "#172033"
SUBTEXT = "#667085"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
SECONDARY = "#eef4ff"
SUCCESS = "#16a34a"
DANGER = "#ef4444"
WARNING = "#f59e0b"
MUTED = "#eef2f7"
MUTED_TEXT = "#475467"
DARK = "#27364f"
SHADOW = "#d8dfeb"

FONT = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"  # Korean-friendly font



_ORIGINAL_TK_BUTTON = tk.Button


class MacColorButton(tk.Label):
    """macOS Tk의 기본 Button은 bg/fg 색을 무시하는 경우가 많아서,
    색상이 필요한 버튼은 Label 기반 버튼으로 대체합니다.
    기존 tk.Button과 비슷하게 command, bg, fg, activebackground를 지원합니다.
    """
    def __init__(self, master=None, **kwargs):
        self.command = kwargs.pop("command", None)
        self.activebackground = kwargs.pop("activebackground", kwargs.get("bg", "#eeeeee"))
        self.activeforeground = kwargs.pop("activeforeground", kwargs.get("fg", TEXT))
        self.normal_bg = kwargs.get("bg", kwargs.get("background", "#eeeeee"))
        self.normal_fg = kwargs.get("fg", kwargs.get("foreground", TEXT))
        self.state = kwargs.pop("state", "normal")
        kwargs.pop("relief", None)
        kwargs.pop("bd", None)
        kwargs.pop("borderwidth", None)
        kwargs.setdefault("anchor", "center")
        kwargs.setdefault("cursor", "hand2")
        # Label은 Button보다 세로 패딩이 작게 느껴져서 기본값 보정
        kwargs.setdefault("padx", 10)
        kwargs.setdefault("pady", 6)
        super().__init__(master, **kwargs)
        self.configure(bg=self.normal_bg, fg=self.normal_fg, highlightthickness=0, bd=0)
        self.bind("<Button-1>", self._click, add="+")
        self.bind("<Return>", self._click, add="+")
        self.bind("<Enter>", self._enter, add="+")
        self.bind("<Leave>", self._leave, add="+")

    def _click(self, event=None):
        if self.state != "disabled" and callable(self.command):
            return self.command()

    def _enter(self, event=None):
        if self.state != "disabled":
            try:
                super().configure(bg=self.activebackground, fg=self.activeforeground)
            except tk.TclError:
                pass

    def _leave(self, event=None):
        try:
            super().configure(bg=self.normal_bg, fg=self.normal_fg)
        except tk.TclError:
            pass

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "command" in kwargs:
            self.command = kwargs.pop("command")
        if "state" in kwargs:
            self.state = kwargs.pop("state")
        if "activebackground" in kwargs:
            self.activebackground = kwargs.pop("activebackground")
        if "activeforeground" in kwargs:
            self.activeforeground = kwargs.pop("activeforeground")
        if "bg" in kwargs or "background" in kwargs:
            self.normal_bg = kwargs.get("bg", kwargs.get("background", self.normal_bg))
        if "fg" in kwargs or "foreground" in kwargs:
            self.normal_fg = kwargs.get("fg", kwargs.get("foreground", self.normal_fg))
        kwargs.pop("relief", None)
        kwargs.pop("bd", None)
        kwargs.pop("borderwidth", None)
        return super().configure(**kwargs)

    config = configure


def install_mac_color_buttons():
    """macOS에서 버튼 색상이 전부 회색으로 보이는 문제를 방지합니다."""
    if sys.platform == "darwin" and tk.Button is not MacColorButton:
        tk.Button = MacColorButton

def clear_children(widget):
    for child in widget.winfo_children():
        child.destroy()


def apply_theme(root):
    """Apply one consistent modern style to the whole Tkinter app."""
    install_mac_color_buttons()
    root.configure(bg=BG)
    root.option_add("*Font", f"{{{FONT}}} 10")
    root.option_add("*Button.Cursor", "hand2")
    root.option_add("*Entry.Relief", "flat")
    root.option_add("*Entry.Background", "#fbfcff")
    root.option_add("*Entry.Foreground", TEXT)
    root.option_add("*Entry.InsertBackground", PRIMARY)

    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass

    s.configure(
        "TCombobox",
        fieldbackground="#fbfcff",
        background="#fbfcff",
        foreground=TEXT,
        arrowcolor=PRIMARY,
        bordercolor=CARD_BORDER,
        lightcolor=CARD_BORDER,
        darkcolor=CARD_BORDER,
        padding=(10, 7),
        relief="flat",
    )
    s.map(
        "TCombobox",
        fieldbackground=[("readonly", "#fbfcff")],
        selectbackground=[("readonly", "#eaf1ff")],
        selectforeground=[("readonly", TEXT)],
    )


def _hover(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    def on_enter(_):
        try:
            widget.configure(bg=hover_bg)
            if hover_fg:
                widget.configure(fg=hover_fg)
        except tk.TclError:
            pass

    def on_leave(_):
        try:
            widget.configure(bg=normal_bg)
            if normal_fg:
                widget.configure(fg=normal_fg)
        except tk.TclError:
            pass

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def make_card(parent, padx=16, pady=10, bg=CARD, border=CARD_BORDER):
    # Tkinter has no true rounded corners, so use a clean bordered card with soft spacing.
    frame = tk.Frame(parent, bg=bg, highlightbackground=border, highlightcolor=border, highlightthickness=1, bd=0)
    frame.pack(fill="x", padx=padx, pady=pady)
    return frame


def title(parent, text, size=18, bg=CARD):
    return tk.Label(parent, text=text, font=(FONT, size, "bold"), bg=bg, fg=TEXT)


def subtitle(parent, text, bg=CARD, wraplength=360):
    return tk.Label(parent, text=text, font=(FONT, 10), bg=bg, fg=SUBTEXT, wraplength=wraplength, justify="left")


def button(parent, text, command, bg=PRIMARY, fg="white", hover_bg=None, height=2, font_size=11, bold=True, fill="x", padx=0, pady=6):
    hover_bg = hover_bg or _darker(bg)
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=(FONT, font_size, "bold" if bold else "normal"),
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        bd=0,
        relief="flat",
        cursor="hand2",
        height=height,
        padx=10,
        pady=3,
    )
    btn.pack(fill=fill, padx=padx, pady=pady)
    _hover(btn, bg, hover_bg, fg, fg)
    return btn


def ghost_button(parent, text, command, fill="x", padx=0, pady=6):
    return button(parent, text, command, bg=SECONDARY, fg=PRIMARY_DARK, hover_bg="#dbeafe", bold=True, fill=fill, padx=padx, pady=pady)


def danger_button(parent, text, command, fill="x", padx=0, pady=6):
    return button(parent, text, command, bg="#fee2e2", fg="#b42318", hover_bg="#fecaca", fill=fill, padx=padx, pady=pady)


def entry(parent, textvariable=None, show=None):
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        show=show,
        font=(FONT, 11),
        bg="#fbfcff",
        fg=TEXT,
        insertbackground=PRIMARY,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=CARD_BORDER,
        highlightcolor=PRIMARY,
    )
    return e


def pill(parent, text, selected=False, command=None):
    bg = PRIMARY if selected else "#f1f5f9"
    fg = "white" if selected else MUTED_TEXT
    hover = PRIMARY_DARK if selected else "#e2e8f0"
    b = tk.Button(parent, text=text, command=command, font=(FONT, 9, "bold"), bg=bg, fg=fg, activebackground=hover, activeforeground=fg, bd=0, relief="flat", padx=10, pady=5, cursor="hand2")
    _hover(b, bg, hover, fg, fg)
    return b


def _darker(hex_color):
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{int(r*0.88):02x}{int(g*0.88):02x}{int(b*0.88):02x}"
    except Exception:
        return hex_color



_ACTIVE_SCROLL_CANVAS = None
_ACTIVE_SCROLL_ORIENT = "vertical"
_SCROLL_BINDING_INSTALLED = False


def _scroll_units_from_event(event):
    """Windows/macOS/Linux 마우스 휠 값을 Tkinter 스크롤 단위로 변환."""
    delta = getattr(event, "delta", 0)
    if delta:
        # Windows: ±120 단위, macOS 트랙패드: 작은 값이 연속으로 들어오는 경우가 많음
        if abs(delta) >= 120:
            units = int(-delta / 120)
        else:
            units = -1 if delta > 0 else 1
        return units if units != 0 else (-1 if delta > 0 else 1)
    num = getattr(event, "num", None)
    if num == 4:
        return -3
    if num == 5:
        return 3
    return 0


def enable_canvas_drag(canvas, orient="vertical", bind_children=None):
    """마우스 드래그와 휠로 긴 화면을 스크롤할 수 있게 합니다.

    기존에는 캔버스/스크롤바 위에 마우스가 있을 때만 휠이 먹는 경우가 있어,
    이 함수가 호출된 화면에서는 캔버스 안의 라벨, 버튼, 이미지, 카드 위에서도
    휠이 동일하게 작동하도록 전역 휠 처리와 자식 위젯 바인딩을 함께 적용합니다.
    """
    global _ACTIVE_SCROLL_CANVAS, _ACTIVE_SCROLL_ORIENT, _SCROLL_BINDING_INSTALLED

    state = {"x": 0, "y": 0, "dragged": False}
    root = canvas.winfo_toplevel()

    def activate(event=None):
        global _ACTIVE_SCROLL_CANVAS, _ACTIVE_SCROLL_ORIENT
        _ACTIVE_SCROLL_CANVAS = canvas
        _ACTIVE_SCROLL_ORIENT = orient

    def _xy(event):
        try:
            return canvas.canvasx(event.x_root - canvas.winfo_rootx()), canvas.canvasy(event.y_root - canvas.winfo_rooty())
        except Exception:
            return event.x, event.y

    def start(event):
        activate(event)
        state["x"], state["y"] = _xy(event)
        state["dragged"] = False
        try:
            canvas.configure(cursor="fleur")
        except tk.TclError:
            pass

    def drag(event):
        activate(event)
        x, y = _xy(event)
        dx = x - state["x"]
        dy = y - state["y"]
        state["x"], state["y"] = x, y
        if abs(dx) + abs(dy) > 2:
            state["dragged"] = True
        try:
            if orient == "horizontal":
                canvas.xview_scroll(int(-dx / 2) or (-1 if dx > 0 else 1), "units")
            else:
                canvas.yview_scroll(int(-dy / 2) or (-1 if dy > 0 else 1), "units")
        except tk.TclError:
            pass

    def end(event):
        try:
            canvas.configure(cursor="")
        except tk.TclError:
            pass

    def wheel(event):
        activate(event)
        units = _scroll_units_from_event(event)
        if units == 0:
            return "break"
        try:
            if orient == "horizontal":
                canvas.xview_scroll(units, "units")
            else:
                canvas.yview_scroll(units, "units")
        except tk.TclError:
            pass
        return "break"

    def global_wheel(event):
        active = _ACTIVE_SCROLL_CANVAS
        if active is None:
            return
        try:
            if not active.winfo_exists() or not active.winfo_viewable():
                return
            units = _scroll_units_from_event(event)
            if units == 0:
                return
            if _ACTIVE_SCROLL_ORIENT == "horizontal":
                active.xview_scroll(units, "units")
            else:
                active.yview_scroll(units, "units")
            return "break"
        except tk.TclError:
            return

    if not _SCROLL_BINDING_INSTALLED:
        root.bind_all("<MouseWheel>", global_wheel, add="+")
        root.bind_all("<Button-4>", global_wheel, add="+")
        root.bind_all("<Button-5>", global_wheel, add="+")
        _SCROLL_BINDING_INSTALLED = True

    def bind_one(widget):
        widget.bind("<Enter>", activate, add="+")
        widget.bind("<FocusIn>", activate, add="+")
        widget.bind("<MouseWheel>", wheel, add="+")
        widget.bind("<Button-4>", wheel, add="+")
        widget.bind("<Button-5>", wheel, add="+")

        # Entry/Combobox/Button 같은 입력 위젯에는 드래그 스크롤을 걸지 않습니다.
        # 그래야 숫자 입력칸의 글자를 드래그해도 화면이 아래로 튀지 않습니다.
        try:
            klass = widget.winfo_class()
        except tk.TclError:
            klass = ""
        interactive_classes = {
            "Entry", "TEntry", "Text", "Combobox", "TCombobox",
            "Button", "TButton", "Radiobutton", "TRadiobutton",
            "Checkbutton", "TCheckbutton", "Menubutton", "TMenubutton",
            "Listbox", "Spinbox", "TSpinbox"
        }
        if klass in interactive_classes:
            return

        widget.bind("<ButtonPress-1>", start, add="+")
        widget.bind("<B1-Motion>", drag, add="+")
        widget.bind("<ButtonRelease-1>", end, add="+")

    def bind_recursive(widget):
        try:
            bind_one(widget)
            for child in widget.winfo_children():
                bind_recursive(child)
        except tk.TclError:
            pass

    bind_one(canvas)
    activate()
    target = bind_children
    if target is not None:
        target.bind("<Configure>", lambda e: bind_recursive(target), add="+")
        bind_recursive(target)


# macOS에서는 tk.Button 색상이 회색으로 무시될 수 있으므로
# style 모듈이 import되는 즉시 색상 버튼 대체를 준비합니다.
# apply_theme()를 부르기 전에 만들어지는 버튼까지 같은 방식으로 보이게 하기 위한 안전장치입니다.
install_mac_color_buttons()
