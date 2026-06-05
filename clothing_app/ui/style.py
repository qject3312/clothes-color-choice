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

FONT = "Malgun Gothic"  # Windows Korean-friendly font


def clear_children(widget):
    for child in widget.winfo_children():
        child.destroy()


def apply_theme(root):
    """Apply one consistent modern style to the whole Tkinter app."""
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
