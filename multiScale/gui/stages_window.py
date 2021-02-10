
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Stages_Tab(tk.Frame):
    """
    A stages tab to select which positions will be imaged in a timelapse
    - table to display selected positions
    - activate keyboard for movement and add positions (a,s,w,d and r,t)
    - change speed of stages for selecting
    - a tool to make a mosaic of the selected positions

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # intro-text
        intro_text = tk.Text(self, height=2, width=600, wrap="none", bg="grey")
        intro_text.insert('1.0', 'In this tab, select the positions to image \n')
        intro_text.grid(row=0, column=0, columnspan=5000, sticky=(tk.E + tk.W))

        # general stage settings
        self.stage_trans_stepsize = tk.DoubleVar()
        self.stage_rot_stepsize = tk.DoubleVar()

        # set the different label frames
        generalstage_settings = tk.LabelFrame(self, text="Stage Movement Settings")
        stagepositions = tk.LabelFrame(self, text="Stage Positions")

        # overall positioning of label frames
        generalstage_settings.grid(row=1, column=0, rowspan=3, sticky=tk.W + tk.E + tk.S + tk.N)
        stagepositions.grid(row=4, column=0, sticky=tk.W + tk.E + tk.S + tk.N)

        ### ----------------------------general stage settings -----------------------------------------------------------------
        # stage labels (positioned)
        stagestepsizelabel = ttk.Label(generalstage_settings, text="Trans. stage step size:").grid(row=0, column=0)
        rotstagestepsizelabel = ttk.Label(generalstage_settings, text="Rot. stage step size:").grid(row=0, column=6)
        mmstepsizelabel = ttk.Label(generalstage_settings, text="mm").grid(row=2, column=4)
        anglestepsizelabel = ttk.Label(generalstage_settings, text="degree").grid(row=2, column=8)

        transstage_scale = tk.Scale(generalstage_settings, variable=self.stage_trans_stepsize,from_=0, to=2, resolution = 0.001, orient="horizontal")
        rotstage_scale = tk.Scale(generalstage_settings, variable=self.stage_rot_stepsize,from_=0, to=360, resolution = 0.1,orient="horizontal")

        self.stage_trans_entry = tk.Entry(generalstage_settings, textvariable=self.stage_trans_stepsize, width=7)
        self.stage_rot_entry = tk.Entry(generalstage_settings, textvariable=self.stage_rot_stepsize, width=7)

        #default values
        self.stage_trans_stepsize.set(2.000)
        self.stage_rot_stepsize.set(2.000)

        #laser widgets layout
        self.stage_trans_entry.grid(row=3, column=4, sticky=tk.W + tk.E)
        self.stage_rot_entry.grid(row=3, column=8, sticky=tk.W + tk.E )
        transstage_scale.grid(row=2, column=0, rowspan =2, sticky=tk.W + tk.E)
        rotstage_scale.grid(row=2, column=6, rowspan =2, sticky=tk.W + tk.E)


