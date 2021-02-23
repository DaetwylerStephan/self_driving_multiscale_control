import tkinter as tk
from tkinter import ttk

import time
from threading import Thread
import numpy as np

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
        self.continuetimelapse = 0 #enable functionality to stop timelapse

        #buttons run tab
        self.view.runtab.bt_preview_lowres.bind("<Button>", self.run_lowrespreview)
        self.view.runtab.bt_preview_highres.bind("<Button>", self.run_highrespreview)
        self.view.runtab.bt_changeTo488.bind("<Button>", lambda event: self.changefilter(event, '488', '488_filter'))
        self.view.runtab.bt_changeTo552.bind("<Button>", lambda event: self.changefilter(event, '552', '552_filter'))
        self.view.runtab.bt_changeTo594.bind("<Button>", lambda event: self.changefilter(event, '594', '594_filter'))
        self.view.runtab.bt_changeTo640.bind("<Button>", lambda event: self.changefilter(event, '640', '640_filter'))
        self.view.runtab.bt_changeTo_block.bind("<Button>", lambda event: self.changefilter(event, 'None', 'Block'))
        self.view.runtab.bt_changeTo_trans.bind("<Button>", lambda event: self.changefilter(event, 'LED', 'No_filter'))
        self.view.runtab.stack_aq_bt_run_stack.bind("<Button>", self.acquire_stack)
        self.view.runtab.timelapse_aq_bt_run_timelapse.bind("<Button>", self.acquire_timelapse)
        self.view.runtab.timelapse_aq_bt_abort_timelapse.bind("<Button>", self.abort_timelapse)

        #buttons stage tab
        self.view.stagessettingstab.keyboard_input_on_bt.bind("<Button>", self.enable_keyboard_movement)
        self.view.stagessettingstab.keyboard_input_off_bt.bind("<Button>", self.disable_keyboard_movement)

    def run(self):
        """
        Run the Tkinter Gui in the main loop
        :return:
        """
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)
        self.root.mainloop()

    def close(self):
        self.model.close()

    ##here follow the call to the functions of the model (microscope) that were bound above:

    def run_lowrespreview(self, event):
        self.view.runtab.preview_change(self.view.runtab.bt_preview_lowres)
        print("running preview")
        self.model.lowres_camera.take_snapshot(20)

    def run_highrespreview(self, event):
        self.view.runtab.preview_change(self.view.runtab.bt_preview_highres)
        print("running preview")
        self.model.lowres_camera.take_snapshot(20)

    def changefilter(self, event, laser, filter):
        print("filter " + filter)
        self.model.filterwheel.set_filter('515-30-25', wait_until_done=False)
        print("laser " + laser)

    def acquire_stack(self, event):
        self.view.runtab.stack_aq_bt_run_stack.config(relief="sunken")
        self.view.update()

        print("acquiring low res stack")
        print("number of planes: " + str(self.view.runtab.stack_aq_numberOfPlanes.get()) + ", plane spacing: " + str(self.view.runtab.stack_aq_plane_spacing.get()))
        self.view.runtab.stack_aq_bt_run_stack.config(relief="raised")

    def acquire_timelapse(self, event):

        self.view.runtab.updateTimesTimelapse()
        self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="sunken")
        self.view.update_idletasks()
        self.view.update()

        self.view.runtab.timelapse_aq_progressbar.config(maximum=self.view.runtab.timelapse_aq_nbTimepoints-1)
        self.continuetimelapse = 0
        print("acquiring timelapse")

        #(1) NOTE: You cannot use a While loop here as it makes the Tkinter mainloop freeze - but the time lapse instead into a thread
        #(2) where you can run while loops etc.
        self.timelapse_thread = Thread(target=self.run_timelapse)
        self.timelapse_thread.start()
        #after that main loop continues


    def run_timelapse(self):
        varb = str(np.random.randint(0, 100))
        self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="sunken")
        self.view.update()

        for timeiter in range(0, self.view.runtab.timelapse_aq_nbTimepoints):
            self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="sunken") #keep the button pressed while executing the timelapse
            self.view.runtab.timelapse_aq_progress.set(timeiter)
            self.view.runtab.timelapse_aq_progressindicator.config(text=str(timeiter+1) +" of " + str(self.view.runtab.timelapse_aq_nbTimepoints))


            print("hello " + varb)
            time.sleep(2)
            if self.continuetimelapse == 1:
                break  # Break while loop when stop = 1

        self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="raised")
        self.view.update()


    def abort_timelapse(self,event):
        self.continuetimelapse = 1


#enable keyboard movements ---------------------------------------------------------------------------------------------
    def enable_keyboard_movement(self, event):
        self.root.bind("<Key>", self.key_pressed)
        self.root.update()

    def disable_keyboard_movement(self, event):
        self.root.unbind("<Key>")
        self.root.update()

    def key_pressed(self, event):
        print(event.keysym)
        if event.char == "w" or event.keysym =="Up":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_updown, 1)
            self.view.stagessettingstab.stage_last_key.set("w")

        if event.char == "s" or event.keysym =="Down":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_updown, -1)
            self.view.stagessettingstab.stage_last_key.set("s")

        if event.char =="a" or event.keysym =="Left":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_lateral, -1)
            self.view.stagessettingstab.stage_last_key.set("a")

        if event.char == "d" or event.keysym =="Right":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_lateral, 1)
            self.view.stagessettingstab.stage_last_key.set("d")

        if event.char == "q":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_axial, 1)
            self.view.stagessettingstab.stage_last_key.set("q")

        if event.char == "e":
            self.view.stagessettingstab.change_currentposition(self.view.stagessettingstab.stage_moveto_axial, -1)
            self.view.stagessettingstab.stage_last_key.set("e")


if __name__ == '__main__':
    c = MultiScale_Microscope_Controller()
    c.run()
    c.close()





