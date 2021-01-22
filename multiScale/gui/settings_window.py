import tkinter as tk
from tkinter import ttk
import time

class Settings_Tab(tk.Frame):
    """
    A settings tab to select parameters such as
    - camera excitation time
    - laser power
    -
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.acquisition_progress = tk.DoubleVar()

        self.numberOfTimepoints = tk.IntVar()
        self.excitation_lowres = tk.IntVar()


        self.numberOfTimepoints = 50


        #set the different label frames
        low_res_camera_settings = tk.LabelFrame(self, text="Low Resolution camera settings")
        high_res_camera_settings = tk.LabelFrame(self, text="Low Resolution camera settings")
        slit_settings = tk.LabelFrame(self, text="Low Resolution camera settings")
        filterwheel_settings = tk.LabelFrame(self, text="Low Resolution camera settings")
        lightsheet_settings = tk.LabelFrame(self, text="Low Resolution camera settings")



        self.excitation_lowres = ttk.Label
        low_res_camera_settings.grid(row=1, column=0, sticky=(tk.W + tk.E))

