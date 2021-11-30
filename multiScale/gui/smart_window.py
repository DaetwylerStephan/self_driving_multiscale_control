
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class SmartMicroscopySettings_Tab(tk.Frame):
    """
    A tab for advanced settings such as rotational stage calibration etc

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # intro-text
        intro_text = tk.Label(self, text='In this tab, you have some settings available for automated microscopy \n', height=2,
                              width=115,
                              fg="black", bg="grey")
        intro_text.grid(row=0, column=0, columnspan=5000, sticky=(tk.E))