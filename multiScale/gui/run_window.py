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
        super().__init__(parent, **kwargs)


        self.acquisition_progress = tk.DoubleVar()
        self.numberOfTimepoints = tk.IntVar()
        self.excitation_lowres = tk.IntVar()
        self.numberOfTimepoints = 50


        #set the different label frames
        preview_settings = tk.LabelFrame(self, text="Preview")
        stack_aquisition_settings = tk.LabelFrame(self, text="Stack acquisition")
        timelapse_acquisition_settings = tk.LabelFrame(self, text="Time-lapse acquisition")

        # overall positioning of label frames
        preview_settings.grid(row=0, column=1, sticky = tk.W + tk.E)
        stack_aquisition_settings.grid(row=1, column=1, sticky = tk.W + tk.E)
        timelapse_acquisition_settings.grid(row=2, column=1, sticky=tk.W + tk.E)

        ### ----------------------------preview buttons ---------------------------------------------------------------
        #preview settings-----------------------------------------------------------------------------------
        self.bt_changeTo488 = tk.Button(preview_settings, text="488 nm", command= lambda : self.preview_filter_select(self.bt_changeTo488), bg="#00f7ff")
        self.bt_changeTo552 = tk.Button(preview_settings, text="552 nm", command= lambda : self.preview_filter_select(self.bt_changeTo552), bg="#a9ff00")
        self.bt_changeTo594 = tk.Button(preview_settings, text="594 nm", command=lambda : self.preview_filter_select(self.bt_changeTo594), bg="#ffd200")
        self.bt_changeTo640 = tk.Button(preview_settings, text="640 nm", command=lambda : self.preview_filter_select(self.bt_changeTo640), bg="#ff2100")
        self.bt_changeTo_block = tk.Button(preview_settings, text="no filter", command=lambda : self.preview_filter_select(self.bt_changeTo_block))
        self.bt_changeTo_trans = tk.Button(preview_settings, text="block", command=lambda : self.preview_filter_select(self.bt_changeTo_trans))
        self.bt_preview_lowres = tk.Button(preview_settings, text="Low Res Preview", command= lambda : self.preview_change(self.bt_preview_lowres))
        self.bt_preview_highres = tk.Button(preview_settings, text="High Res Preview", command=lambda : self.preview_change(self.bt_preview_highres))

        #preview layout
        self.bt_changeTo488.grid(row=3, column=2)
        self.bt_changeTo552.grid(row=3, column=3)
        self.bt_changeTo594.grid(row=3, column=4)
        self.bt_changeTo640.grid(row=3, column=5)
        self.bt_changeTo_block.grid(row=3, column=6)
        self.bt_changeTo_trans.grid(row=3, column=7)
        self.bt_preview_lowres.grid(row=4, column=2, columnspan=2, sticky = (tk.W + tk.E))
        self.bt_preview_highres.grid(row=4, column=4, columnspan=2, sticky=(tk.W + tk.E))

        ### ----------------------------stack acquisition buttons ------------------------------------------------------
        #stack aquisition labels (positioned)
        laseron_label = ttk.Label(stack_aquisition_settings, text="Laser On:").grid(row=2, column=0)
        numberOfPlanes_label= ttk.Label(stack_aquisition_settings, text="Number of planes:").grid(row = 3, column = 0)
        plane_spacing_label= ttk.Label(stack_aquisition_settings, text="Spacing of planes:").grid(row = 4, column = 0)

        #stack aquisition settings
        self.numberOfPlanes = tk.IntVar()
        self.Entry_numberOfPlanes = tk.Entry(stack_aquisition_settings, textvariable = self.numberOfPlanes)
        self.Entry_numberOfPlanes.insert(0,"20")

        self.plane_spacing = tk.DoubleVar()
        self.Entry_plane_spacing = tk.Entry(stack_aquisition_settings, textvariable=self.plane_spacing)
        self.Entry_plane_spacing.insert(0, "1")

        self.bt_run_lowresstack = tk.Button(stack_aquisition_settings, text="Acquire Low Res Stack(s)")
        self.bt_run_highresstack = tk.Button(stack_aquisition_settings, text="Acquire High Res Stack(s)")

        self.bt_laserOn488 = tk.Checkbutton(stack_aquisition_settings, text ='488')
        self.bt_laserOn552 = tk.Checkbutton(stack_aquisition_settings, text ='552')
        self.bt_laserOn594 = tk.Checkbutton(stack_aquisition_settings, text ='594')
        self.bt_laserOn640 = tk.Checkbutton(stack_aquisition_settings, text ='640')

        #stack aquisition layout (labels positioned above)
        self.bt_laserOn488.grid(row =2, column=1)
        self.bt_laserOn552.grid(row=2, column=2)
        self.bt_laserOn594.grid(row=2, column=3)
        self.bt_laserOn640.grid(row=2, column=4)
        self.Entry_numberOfPlanes.grid(row =3, column=1, columnspan=3, sticky = tk.W + tk.E)
        self.Entry_plane_spacing.grid(row =4, column=1, columnspan=3, sticky = tk.W + tk.E)
        self.bt_run_lowresstack.grid(row = 5, column =0, columnspan=3, sticky = tk.W + tk.E)
        self.bt_run_highresstack.grid(row=5, column=3, columnspan=3, sticky=tk.W + tk.E)

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



#-------button press functions---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------

    def preview_change(self, button):
        if (button.cget('relief') == "sunken"):
            button.config(relief="raised")
        else:
            button.config(relief="sunken")

    def preview_filter_select(self, button):
        self.bt_changeTo488.config(relief="raised")
        self.bt_changeTo552.config(relief="raised")
        self.bt_changeTo594.config(relief="raised")
        self.bt_changeTo640.config(relief="raised")
        self.bt_changeTo_block.config(relief="raised")
        self.bt_changeTo_trans.config(relief="raised")
        button.config(relief="sunken")

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
