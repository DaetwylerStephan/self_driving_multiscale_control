import tkinter as tk
from tkinter import ttk

import time

from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel

class MultiScale_Microscope_Controller():
    """
    This is the controller in an MVC-scheme for mediating the interaction between the View (GUI) and the model (multiScope.py).
    Use: https://www.python-course.eu/tkinter_events_binds.php
    """
    def __init__(self):
        self.root = tk.Tk()

        # Create scope object as model
        self.model = multiScopeModel()

        #create the gui as view
        all_tabs_mainGUI = ttk.Notebook(self.root)
        self.view = MultiScope_MainGui(all_tabs_mainGUI, self.model)

        #define here which buttons run which function in the multiScope model

        #buttons run tab
        self.view.runtab.bt_preview_lowres.bind("<Button>", self.run_lowrespreview)
        self.view.runtab.bt_preview_highres.bind("<Button>", self.run_highrespreview)
        self.view.runtab.bt_changeTo488.bind("<Button>", lambda event: self.changefilter(event, '488', '488_filter'))
        self.view.runtab.bt_changeTo552.bind("<Button>", lambda event: self.changefilter(event, '552', '552_filter'))
        self.view.runtab.bt_changeTo594.bind("<Button>", lambda event: self.changefilter(event, '594', '594_filter'))
        self.view.runtab.bt_changeTo640.bind("<Button>", lambda event: self.changefilter(event, '640', '640_filter'))
        self.view.runtab.bt_changeTo_block.bind("<Button>", lambda event: self.changefilter(event, 'None', 'Block'))
        self.view.runtab.bt_changeTo_trans.bind("<Button>", lambda event: self.changefilter(event, 'LED', 'No_filter'))
        self.view.runtab.bt_run_lowresstack.bind("<Button>", self.acquire_lowresstack)
        self.view.runtab.bt_run_highresstack.bind("<Button>", self.acquire_highresstack)


    def run(self):
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def close(self):
        self.model.close()

    def run_lowrespreview(self, event):
        print("running preview")
        self.model.lowres_camera.take_snapshot(20)

    def run_highrespreview(self, event):
        print("running preview")
        self.model.lowres_camera.take_snapshot(20)

    def changefilter(self, event, laser, filter):
        print("filter " + filter)
        print("laser " + laser)

    def acquire_lowresstack(self, event):
        self.view.runtab.bt_run_lowresstack.config(relief="sunken")
        print("acquiring low res stack")
        print("number of planes: " + str(self.view.runtab.numberOfPlanes.get()) + ", plane spacing: " + str(self.view.runtab.plane_spacing.get()))
        self.view.runtab.bt_run_lowresstack.config(relief="raised")

    def acquire_highresstack(self, event):

        self.view.runtab.bt_run_highresstack.config(relief="sunken")
        self.view.update()

        time.sleep(2)
        print("acquiring high res stack")
        print("number of planes: " + str(self.view.runtab.numberOfPlanes.get()) + ", plane spacing: " + str(self.view.runtab.plane_spacing.get()))

        self.view.runtab.bt_run_highresstack.config(relief="raised")


if __name__ == '__main__':
    c = MultiScale_Microscope_Controller()
    c.run()
    c.close()





