
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
        # intro-text
        intro_text = tk.Label(self, text='In this tab, you have some advanced settings available \n', height=2, width=115,
                              fg="black", bg="grey")
        intro_text.grid(row=0, column=0, columnspan=5000, sticky=(tk.E))

        #slit settings
        self.slit_currentsetting = tk.DoubleVar()
        self.slit_lowres = tk. DoubleVar()
        self.slit_highres = tk. DoubleVar()

        #ASLM settings
        self.ASLM_linedelay = tk.DoubleVar()
        self.ASLM_volt_min = tk.DoubleVar()
        self.ASLM_volt_max = tk.DoubleVar()
        self.ASLM_volt_current = tk.DoubleVar()
        self.ASLM_alignmentmodeOn = tk.IntVar()
        self.ASLM_SawToothOn = tk.IntVar()
        self.ASLM_constantVoltageOn = tk.IntVar()

        ### ----------------------------label frames-----------------------------------------------------------------

        #set the different label frames
        slit_settings = tk.LabelFrame(self, text="Slit Settings")
        ASLM_settings = tk.LabelFrame(self, text="Slit Settings")

        # overall positioning of label frames
        slit_settings.grid(row=2, column=0, sticky = tk.W + tk.E+tk.S+tk.N)
        ASLM_settings.grid(row=2, column=1, sticky = tk.W + tk.E+tk.S+tk.N)

        ### ----------------------------slit settings -----------------------------------------------------------------
        # slit labels (positioned)
        slit_opening_label = ttk.Label(slit_settings, text="Slit opening:").grid(row=2, column=0)
        slit_opening_label2 = ttk.Label(slit_settings, text="current:").grid(row=3, column=0)
        slit_lowres_label = ttk.Label(slit_settings, text="Low Res:").grid(row=4, column=0)
        slit_highres_label = ttk.Label(slit_settings, text="High Res:").grid(row=4, column=3)

        self.slit_opening_entry = tk.Entry(slit_settings, textvariable=self.slit_currentsetting, width=6)
        self.slit_lowres_entry = tk.Entry(slit_settings, textvariable=self.slit_lowres, width=6)
        self.slit_highres_entry = tk.Entry(slit_settings, textvariable=self.slit_highres, width=6)

        slit_scale = tk.Scale(slit_settings, variable=self.slit_currentsetting, from_=0, to=4558, orient="horizontal")

        # set defaults
        self.slit_lowres.set(4025)
        self.slit_highres.set(150)

        # slit settings layout
        slit_scale.grid(row=2, column=1, rowspan=2, columnspan=4, sticky=tk.W + tk.E)
        self.slit_opening_entry.grid(row=3, column=5, sticky=tk.W + tk.E + tk.S)
        self.slit_lowres_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E + tk.S)
        self.slit_highres_entry.grid(row=4, column=4, columnspan=2, sticky=tk.W + tk.E + tk.S)

        ### ----------------------------ASLM settings -----------------------------------------------------------------
        # ASLM labels (positioned)
        lineDelay_label = ttk.Label(ASLM_settings, text="Line Delay factor:").grid(row=2, column=0)
        voltageminimal_label = ttk.Label(ASLM_settings, text="ASLM remote mirror min voltage:").grid(row=4, column=0)
        voltagemaximal_label = ttk.Label(ASLM_settings, text="ASLM remote mirror max voltage:").grid(row=7, column=0)
        voltagecurrent_label = ttk.Label(ASLM_settings, text="Set ASLM remote mirror voltage:").grid(row=9, column=0)

        self.lineDelay_entry = tk.Entry(ASLM_settings, textvariable=self.ASLM_linedelay, width=6)
        self.voltageminimal_entry = tk.Entry(ASLM_settings, textvariable=self.ASLM_volt_min, width=6)
        self.voltagemaximal_entry = tk.Entry(ASLM_settings, textvariable=self.ASLM_volt_max, width=6)
        self.voltagecurrent_entry = tk.Entry(ASLM_settings, textvariable=self.ASLM_volt_current, width=6)

        # choice of scan mode
        self.ASLM_alignmentmodeOn_chkbt = tk.Checkbutton(ASLM_settings, text='Alignment mode on',
                                                         variable=self.ASLM_alignmentmodeOn, onvalue=1, offvalue=0)

        self.ASLM_sawtoothON_chkbt = tk.Checkbutton(ASLM_settings, text='Apply Saw Tooth ASLM',
                                                        variable=self.ASLM_SawToothOn, onvalue=1, offvalue=0)
        self.ASLM_constantRemoteOn_chkbt = tk.Checkbutton(ASLM_settings, text='Apply Constant ASLM voltage',
                                                         variable=self.ASLM_constantVoltageOn, onvalue=1, offvalue=0)


        # set defaults
        self.ASLM_linedelay.set(6)
        self.ASLM_volt_min.set(-1)
        self.ASLM_volt_max.set(1)
        self.ASLM_volt_current.set(0)


        #ASLM settings layout
        self.lineDelay_entry.grid(row=2, column=1, sticky=tk.W + tk.E + tk.S)
        self.voltageminimal_entry.grid(row=4, column=1, sticky=tk.W + tk.E + tk.S)
        self.voltagemaximal_entry.grid(row=7, column=1, sticky=tk.W + tk.E + tk.S)
        self.voltagecurrent_entry.grid(row=9, column=1, sticky=tk.W + tk.E + tk.S)
        self.ASLM_alignmentmodeOn_chkbt.grid(row=11, column=0, sticky=tk.W + tk.S)
        self.ASLM_sawtoothON_chkbt.grid(row=12, column=0, sticky=tk.W + tk.S)
        self.ASLM_constantRemoteOn_chkbt.grid(row=14, column=0, sticky=tk.W + tk.S)

    def print_values(self):
        print("test")
