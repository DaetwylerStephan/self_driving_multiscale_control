
import tkinter as tk
from tkinter import ttk

class Welcome_Tab(tk.Frame):
    """
    A welcome tab to select experiment parameters such as
    - model organism
    - user
    - fluorescent marker
    - quit application
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.username = tk.StringVar()

        intro_text = tk.Text(self)

        name_label = ttk.Label(self, text="Username:")
        username_box = ttk.Combobox(self, textvariable=self.username, values=["Stephan Daetwyler", "Reto Fiolka", "Bo-Jui Chang"])

        # Layout form
        name_label.grid(row=1, column=0, sticky=tk.W)
        username_box.grid(row=1, column=1, sticky=(tk.W))

        self.columnconfigure(1, weight=1)

        #quit_button = tk.Button(self, text="Quit", command =self.quit)
        #quit_button.grid(tk.S + tk.E)
