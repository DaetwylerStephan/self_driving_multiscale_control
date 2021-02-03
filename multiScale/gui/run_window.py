import tkinter as tk
from tkinter import ttk
import time
import datetime as dt

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

        #params
        self.excitation_lowres = tk.IntVar()

        #stack acquisition parameters
        self.stack_aq_progress = tk.DoubleVar()
        self.stack_aq_488on = tk.IntVar()
        self.stack_aq_552on = tk.IntVar()
        self.stack_aq_594on = tk.IntVar()
        self.stack_aq_640on = tk.IntVar()
        self.stack_acq_laserCycleMode = tk.StringVar()
        self.stack_aq_numberOfPlanes = tk.IntVar()
        self.stack_aq_plane_spacing = tk.DoubleVar()

        #time-lapse setting parameters
        self.timelapse_aq_progress = tk.DoubleVar()
        self.timelapse_aq_nbTimepoints = tk.IntVar()
        self.timelapse_aq_timeinterval = tk.DoubleVar()
        self.timelapse_aq_nbTimepoints.set(50)


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
        numberOfPlanes_label= ttk.Label(stack_aquisition_settings, text="Number of planes:").grid(row = 6, column = 0)
        plane_spacing_label= ttk.Label(stack_aquisition_settings, text="Spacing of planes:").grid(row = 10, column = 0)
        laser_cyclemode_label= ttk.Label(stack_aquisition_settings, text="Laser Cycle Mode:").grid(row = 3, column = 0)

        #stack aquisition settings
        self.ckb_laserOn488 = tk.Checkbutton(stack_aquisition_settings, text ='488', variable=self.stack_aq_488on, onvalue=1, offvalue=0)
        self.ckb_laserOn552 = tk.Checkbutton(stack_aquisition_settings, text ='552', variable=self.stack_aq_552on, onvalue=1, offvalue=0)
        self.ckb_laserOn594 = tk.Checkbutton(stack_aquisition_settings, text ='594', variable=self.stack_aq_594on, onvalue=1, offvalue=0)
        self.ckb_laserOn640 = tk.Checkbutton(stack_aquisition_settings, text ='640', variable=self.stack_aq_640on, onvalue=1, offvalue=0)

        laserCycles = ('Change filter/stack', 'Change filter/plane')
        self.option_laserCycle = tk.OptionMenu(stack_aquisition_settings, self.stack_acq_laserCycleMode, *laserCycles)
        self.stack_acq_laserCycleMode.set(laserCycles[0])

        self.Entry_numberOfPlanes = tk.Entry(stack_aquisition_settings, textvariable=self.stack_aq_numberOfPlanes)
        self.Entry_numberOfPlanes.insert(0, "20")

        self.Entry_plane_spacing = tk.Entry(stack_aquisition_settings, textvariable=self.stack_aq_plane_spacing)
        self.Entry_plane_spacing.insert(0, "1")

        self.bt_run_lowresstack = tk.Button(stack_aquisition_settings, text="Acquire Low Res Stack(s)")
        self.bt_run_highresstack = tk.Button(stack_aquisition_settings, text="Acquire High Res Stack(s)")

        #stack aquisition layout (labels positioned above)
        self.ckb_laserOn488.grid(row =2, column=1)
        self.ckb_laserOn552.grid(row=2, column=2)
        self.ckb_laserOn594.grid(row=2, column=3)
        self.ckb_laserOn640.grid(row=2, column=4)
        self.option_laserCycle.grid(row=3,column =1, columnspan=3,sticky = tk.W + tk.E)

        self.Entry_numberOfPlanes.grid(row =6, column=1, columnspan=3, sticky = tk.W + tk.E)
        self.Entry_plane_spacing.grid(row =10, column=1, columnspan=3, sticky = tk.W + tk.E)
        self.bt_run_lowresstack.grid(row = 15, column =0, columnspan=3, sticky = tk.W + tk.E)
        self.bt_run_highresstack.grid(row=15, column=3, columnspan=3, sticky=tk.W + tk.E)

        ### ----------------------------time-lapse acquisition buttons ------------------------------------------------------
        # time-lapse aquisition labels (positioned)
        timeinterval_label = ttk.Label(timelapse_acquisition_settings, text="Time interval:").grid(row=2, column=0)
        timepointsnb_label = ttk.Label(timelapse_acquisition_settings, text="Number of timepoints:").grid(row=5, column=0)
        start_time = ttk.Label(timelapse_acquisition_settings, text="Start time:").grid(row=12, column=0)
        end_time = ttk.Label(timelapse_acquisition_settings, text="End time:").grid(row=14, column=0)
        self.timelapse_lb_starttime = tk.Label(timelapse_acquisition_settings, text=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timelapse_lb_endtime = tk.Label(timelapse_acquisition_settings, text=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # time-lapse aquisition settings
        self.Entry_Timeinterval = tk.Entry(timelapse_acquisition_settings, textvariable=self.timelapse_aq_timeinterval)
        self.timelapse_aq_timeinterval.trace("w", lambda name, index, mode, var = self.timelapse_aq_timeinterval: self.updateTimesTimelapse())
        self.Entry_Timeinterval.insert(0, "6")
        self.Entry_NbTimepoints = tk.Entry(timelapse_acquisition_settings, textvariable=self.timelapse_aq_nbTimepoints, validate="all", validatecommand=self.updateTimesTimelapse)
        self.timelapse_aq_nbTimepoints.trace("w", lambda name, index, mode,
                                                         var=self.timelapse_aq_nbTimepoints: self.updateTimesTimelapse())

        self.Entry_NbTimepoints.insert(0, "6")

        self.bt_run_timelapse = tk.Button(timelapse_acquisition_settings, text="Run Timelapse")
        self.bt_abort_timelapse = tk.Button(timelapse_acquisition_settings, text="Abort Timelapse")


        # time-lapse aquisition layout (labels positioned above)
        self.Entry_Timeinterval.grid(row=2, column=1,columnspan=3, sticky = tk.W + tk.E)
        self.Entry_NbTimepoints.grid(row=5, column=2, columnspan=3, sticky = tk.W + tk.E)
        self.bt_run_timelapse.grid(row=15, column=0, columnspan=2, sticky=tk.W + tk.E)
        self.bt_abort_timelapse.grid(row=15, column=3, columnspan=2, sticky=tk.W + tk.E)
        self.timelapse_lb_starttime.grid(row=12, column=2)
        self.timelapse_lb_endtime.grid(row=14, column=2)

        ch_button = ttk.Button(self, text="Change", command=self.loop_function)
        ch_button.grid(row=0, column=3, sticky=tk.E)

        progressbar = ttk.Progressbar(self, variable=self.timelapse_aq_progress, maximum=self.timelapse_aq_nbTimepoints.get())
        progressbar.grid(row=0, column=2, sticky=tk.E)


    def timelapse_started(self):
        """
        Set all the buttons to disable by using config - config can change the properties of a widget
        my_button.config(state=DISABLED)
        :return:
        """


    def loop_function(self):
        k = 0
        print(self.timelapse_aq_nbTimepoints.get())
        while k <= self.timelapse_aq_nbTimepoints.get():
            ### some work to be done
            self.timelapse_aq_progress.set(k)
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

    def preview_change(self, button):
        if (button.cget('relief') == "sunken"):
            button.config(relief="raised")
        else:
            button.config(relief="sunken")

    def updateTimesTimelapse(self):
        now = dt.datetime.now()
        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.timelapse_lb_starttime.config(text=nowtime)

        #calculate end time
        try:
            endtime = now + dt.timedelta(0, self.timelapse_aq_timeinterval.get() * self.timelapse_aq_nbTimepoints.get())
        except:
            endtime = now #catch exception if all entries are deleted

        end = endtime.strftime("%Y-%m-%d %H:%M:%S")
        self.timelapse_lb_endtime.config(text=end)

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
