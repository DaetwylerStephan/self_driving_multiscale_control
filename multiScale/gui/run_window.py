import tkinter as tk
from tkinter import ttk
import time

class Run_Tab(tk.Frame):
    """
    A run tab to select parameters such as
    - camera excitation time
    - acquisition settings, e.g. nb of time points
    - laser power
    -
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.acquisition_progress = tk.DoubleVar()

        self.numberOfTimepoints = tk.IntVar()
        self.numberOfTimepoints = 50

        ch_button = ttk.Button(self, text="Change", command=self.loop_function)
        ch_button.grid(row=0, column=2, sticky=tk.E)

        progressbar = ttk.Progressbar(self, variable=self.acquisition_progress, maximum=self.numberOfTimepoints)
        progressbar.grid(row=0, column=1, sticky=tk.E)

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