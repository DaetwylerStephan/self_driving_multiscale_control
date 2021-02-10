
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class AdvancedSettings_Tab(tk.Frame):
    """
    A tab for advanced settings such as rotational stage calibration etc

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # intro-text
        intro_text = tk.Text(self, height=2, width= 600, wrap="none", bg="grey")
        intro_text.insert('1.0', 'In this tab, you have some advanced settings available \n')
        intro_text.grid(row=0, column=0, columnspan=5000, sticky=(tk.E + tk.W))

        #slit settings
        self.slit_currentsetting = tk.DoubleVar()
        self.slit_lowres = tk. DoubleVar()
        self.slit_highres = tk. DoubleVar()

        #set the different label frames
        slit_settings = tk.LabelFrame(self, text="Slit Settings")

        # overall positioning of label frames
        slit_settings.grid(row=2, column=0, sticky = tk.W + tk.E+tk.S+tk.N)

        ### ----------------------------slit settings -----------------------------------------------------------------
        # slit labels (positioned)
        slit_opening_label = ttk.Label(slit_settings, text="Slit opening:").grid(row=2, column=0)
        slit_opening_label2 = ttk.Label(slit_settings, text="current:").grid(row=3, column=0)
        slit_lowres_label = ttk.Label(slit_settings, text="Low Res:").grid(row=4, column=0)
        slit_highres_label = ttk.Label(slit_settings, text="High Res:").grid(row=4, column=3)

        self.slit_opening_entry = tk.Entry(slit_settings, textvariable=self.slit_currentsetting, width=6)
        self.slit_lowres_entry = tk.Entry(slit_settings, textvariable=self.slit_lowres, width=6)
        self.slit_highres_entry = tk.Entry(slit_settings, textvariable=self.slit_highres, width=6)

        slit_scale = tk.Scale(slit_settings, variable=self.slit_currentsetting, from_=0, to=4000, orient="horizontal")

        # set defaults
        self.slit_lowres.set(4000)
        self.slit_highres.set(150)

        # slit layout
        slit_scale.grid(row=2, column=1, rowspan=2, columnspan=4, sticky=tk.W + tk.E)
        self.slit_opening_entry.grid(row=3, column=5, sticky=tk.W + tk.E + tk.S)
        self.slit_lowres_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E + tk.S)
        self.slit_highres_entry.grid(row=4, column=4, columnspan=2, sticky=tk.W + tk.E + tk.S)

    def print_values(self):
        print("test")
