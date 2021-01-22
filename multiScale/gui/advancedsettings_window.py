
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class AdvancedSettings_Tab(tk.Frame):
    """
    A stages tab to select which positions will be imaged in a timelapse
    - table to display selected positions
    - activate keyboard for movement and add positions (a,s,w,d and r,t)
    - change speed of stages for selecting
    - a tool to make a mosaic of the selected positions

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.username = tk.StringVar()
        self.modelorganism_name = tk.StringVar()
        self.maker_name = tk.StringVar

        #intro-text
        intro_text = tk.Text(self, height = 2, wrap = "none", bg="grey")
        intro_text.insert('1.0', 'In this tab, you have some advanced settings available \n')


        #Set default values



        # Layout form
        intro_text.grid(row=0, column=0, columnspan=3, sticky=(tk.E + tk.W))

        self.columnconfigure(1, weight=1)


