import tkinter as tk
from tkinter import ttk

import time
from threading import Thread
import numpy as np

from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel
import auxiliary_code.concurrency_tools as ct
from constants import Camera_parameters


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
        self.view.runtab.bt_preview_lowres.bind("<ButtonRelease>", self.run_lowrespreview)
        self.view.runtab.bt_preview_highres.bind("<Button>", self.run_highrespreview)
        self.view.runtab.bt_preview_stop.bind("<Button>", self.run_stop_preview)
        self.view.runtab.bt_changeTo488.bind("<Button>", lambda event: self.changefilter(event, '488', '488_filter'))
        self.view.runtab.bt_changeTo552.bind("<Button>", lambda event: self.changefilter(event, '552', '552_filter'))
        self.view.runtab.bt_changeTo594.bind("<Button>", lambda event: self.changefilter(event, '594', '594_filter'))
        self.view.runtab.bt_changeTo640.bind("<Button>", lambda event: self.changefilter(event, '640', '640_filter'))
        self.view.runtab.bt_changeTo_block.bind("<Button>", lambda event: self.changefilter(event, 'None', 'Block'))
        self.view.runtab.bt_changeTo_trans.bind("<Button>", lambda event: self.changefilter(event, 'LED', 'No_filter'))
        self.view.runtab.stack_aq_bt_run_stack.bind("<Button>", self.acquire_stack)
        self.view.runtab.stack_aq_numberOfPlanes.trace_add("write", self.updateNbPlanes)
        self.view.runtab.timelapse_aq_bt_run_timelapse.bind("<Button>", self.acquire_timelapse)
        self.view.runtab.timelapse_aq_bt_abort_timelapse.bind("<Button>", self.abort_timelapse)

        #buttons stage tab
        self.view.stagessettingstab.keyboard_input_on_bt.bind("<Button>", self.enable_keyboard_movement)
        self.view.stagessettingstab.keyboard_input_off_bt.bind("<Button>", self.disable_keyboard_movement)

        #define some parameters
        self.current_stackbuffersize = self.view.runtab.stack_aq_numberOfPlanes.get()
        self.stack_buffer = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes.get(),Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')


    def run(self):
        """
        Run the Tkinter Gui in the main loop
        :return:
        """
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)
        self.automatically_update_stackbuffer()
        self.root.mainloop()

    def close(self):
        self.model.close()

    ##here follow the call to the functions of the model (microscope) that were bound above:

    def run_lowrespreview(self, event):
        if self.model.continue_preview_lowres == False:
            self.model.continue_preview_lowres = True
            self.view.runtab.preview_change(self.view.runtab.bt_preview_lowres)
            print("running preview")
            self.view.after(10, self.view.runtab.preview_change(self.view.runtab.bt_preview_lowres))
            self.model.preview_lowres()

    def wait_forInput(self):
        print("All 'snap' threads finished execution.")
        input('Hit enter to close napari...')

    def run_highrespreview(self, event):
        self.view.runtab.preview_change(self.view.runtab.bt_preview_highres)
        print("running preview")
        #self.model.preview_lowres() // this gives an error!
        self.model.preview_highres()

    def run_stop_preview(self, event):
      '''
      Stops an executing preview and resets the profile of the preview buttons that were sunken after starting a preview
      '''
      if self.model.continue_preview_lowres == True:
        self.model.continue_preview_lowres =False
        self.view.runtab.preview_change(self.view.runtab.bt_preview_lowres)

      if self.model.continue_preview_highres == True:
        self.model.continue_preview_highres = False
        self.view.runtab.preview_change(self.view.runtab.bt_preview_highres)


    def changefilter(self, event, laser, filter):
        print("filter " + filter)
        self.model.filterwheel.set_filter('515-30-25', wait_until_done=False)
        print("laser " + laser)

    def updateNbPlanes(self, var,indx,mode):
        """
        generate a new SharedNDArray whenever the number of planes is updated.
        """
        print("number of planes: " + str(self.view.runtab.stack_aq_numberOfPlanes.get()))
        self.stack_buffer = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes.get(),Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.stack_buffer_nb = self.view.runtab.stack_aq_numberOfPlanes.get()
        #self.stack_buffer.fill(0) #too slow - need other solution

    def automatically_update_stackbuffer(self):
        print("update stack")
        try:
            self.stack_buffer_nb = self.view.runtab.stack_aq_numberOfPlanes.get()
            if self.stack_buffer_nb != self.current_stackbuffersize:
                self.stack_buffer.fill(0)
                self.current_stackbuffersize = self.stack_buffer_nb
        except:
            print("update error")
        self.root.after(5000, self.automatically_update_stackbuffer)

    def acquire_stack(self, event):
        self.view.runtab.stack_aq_bt_run_stack.config(relief="sunken")
        self.view.update()

        #stop all potential previews
        self.model.continue_preview_lowres = False
        self.model.continue_preview_highres = False

        #set model parameters
        self.model.stack_nbplanes = self.stack_buffer_nb
        self.model.stack_buffer = self.stack_buffer

        self.initial_time = time.perf_counter()
        data_buf = ct.SharedNDArray(shape=(200, 2000, 2000), dtype='uint16')
        time_elapsed = time.perf_counter() - self.initial_time
        print("time pre-alloc: " + str(time_elapsed))
        data_buf.fill(0)
        #data_buf[1, :, :] = 8
        time_elapsed = time.perf_counter() - self.initial_time
        print("time post-alloc: " + str(time_elapsed))

        self.initial_time = time.perf_counter()
        #data_buf.fill(1)
        data_buf[2,:,:]=8
        time_elapsed = time.perf_counter() - self.initial_time
        print("time re-alloc : " + str(time_elapsed))

        print("acquiring low res stack")
        print("number of planes: " + str(self.view.runtab.stack_aq_numberOfPlanes.get()) + ", plane spacing: " + str(self.view.runtab.stack_aq_plane_spacing.get()))
        self.view.runtab.stack_aq_bt_run_stack.config(relief="raised")

    def acquire_timelapse(self, event):

        self.view.runtab.updateTimesTimelapse()
        self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="sunken")
        self.view.update_idletasks()
        self.view.update()

        # stop all potential previews
        self.model.continue_preview_lowres = False
        self.model.continue_preview_highres = False

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





