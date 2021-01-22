import tkinter as tk
from tkinter import ttk
import time

class Run_Tab(tk.Frame):
    """
    A run tab to select parameters such as
    - acquisition settings, e.g. nb of time points, which channels are imaged
    - Cycle laser (e.g. per stack or per plane)
    - which channel is displayed
    - preview button
    - number of planes
    - plane spacing
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.acquisition_progress = tk.DoubleVar()

        self.numberOfTimepoints = tk.IntVar()
        self.excitation_lowres = tk.IntVar()


        self.numberOfTimepoints = 50


        #set the different label frames
        preview_settings = tk.LabelFrame(self, text="Preview")
        lightsheet_settings = tk.LabelFrame(self, text="Low Resolution camera settings")

        #preview settings-----------------------------------------------------------------------------------
        self.bt_changeTo488 = tk.Button(preview_settings, text="488 nm", command=self.preview_changeTo488, bg="#00f7ff").grid(row=3, column=2)
        self.bt_changeTo552 = tk.Button(preview_settings, text="552 nm", command=self.preview_changeTo552, bg="#a9ff00").grid(row=3, column=3)
        bt_changeTo594 = tk.Button(preview_settings, text="594 nm", command=self.preview_changeTo594, bg="#ffd200").grid(row=3, column=4)
        bt_changeTo640 = tk.Button(preview_settings, text="640 nm", command=self.preview_changeTo640, bg="#ff2100").grid(row=3, column=5)
        bt_changeTo_block = tk.Button(preview_settings, text="no filter", command=self.preview_changeToBlock).grid(row=3, column=6)
        bt_changeTo_trans = tk.Button(preview_settings, text="block", command=self.preview_changeToTransmission).grid(row=3, column=7)
        self.bt_preview = tk.Button(preview_settings, text="Preview", command=self.preview)

        #layout preview
        self.bt_preview.grid(row=4, column=2, columnspan=2, sticky = (tk.W + tk.E))



        preview_settings.grid(row=0,column=1)


        ch_button = ttk.Button(self, text="Change", command=self.loop_function)
        ch_button.grid(row=0, column=3, sticky=tk.E)

        progressbar = ttk.Progressbar(self, variable=self.acquisition_progress, maximum=self.numberOfTimepoints)
        progressbar.grid(row=0, column=2, sticky=tk.E)


    def timelapse_started(self):
        """
        Set all the buttons to disable by using config - config can change the properties of a widget
        my_button.config(state=DISABLED)
        :return:
        """


    def loop_function(self):
        k = 0
        while k <= self.numberOfTimepoints:
            ### some work to be done
            self.acquisition_progress.set(k)
            k += 1
            time.sleep(0.02)
            self.update_idletasks()
        #self.after(100, loop_function())



#-------preview functions---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------

    def preview(self):
        if (self.bt_preview.cget('relief') == "sunken"):
            self.bt_preview.config(relief="raised")
        else:
            self.bt_preview.config(relief="sunken")
        pass

    def preview_changeTo488(self):
        self.changeFilter('515-30-25')
        self.switchLaser('488')

    def preview_changeTo552(self):
        self.changeFilter('572/20-25')
        self.switchLaser('552')

    def preview_changeTo594(self):
        self.changeFilter('615/20-25')
        self.switchLaser('594')

    def preview_changeTo640(self):
        self.changeFilter('676/37-25')
        self.switchLaser('640')

    def preview_changeToTransmission(self):
        self.changeFilter('transmission')

    def preview_changeToBlock(self):
        self.changeFilter('block')

    def changeFilter(self, filter):
        pass

    def switchLaser(self, laserline):
        pass

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
