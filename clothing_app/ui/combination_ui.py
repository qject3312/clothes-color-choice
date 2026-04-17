import tkinter as tk

class CombinationUI:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_screen()
        tk.Label(self.app.main_frame, text="조합").pack()