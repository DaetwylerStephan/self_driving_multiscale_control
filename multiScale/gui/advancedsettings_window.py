
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class AdvancedSettings_Tab(tk.Frame):
    """
    A tab for advanced settings such as rotational stage calibration etc

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        #intro-text
        intro_text = tk.Text(self, height = 2, wrap = "none", bg="grey")
        intro_text.insert('1.0', 'In this tab, you have some advanced settings available \n')
        intro_text.grid(row=0, column=0, columnspan=3, sticky=(tk.E + tk.W))



        # Layout form


        self.columnconfigure(1, weight=1)

    def print_values(self):
        print("test")
