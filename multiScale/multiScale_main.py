import tkinter as tk
from tkinter import ttk

import time
from threading import Thread
import numpy as np

from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel
import auxiliary_code.concurrency_tools as ct
from constants import Camera_parameters
from constants import NI_board_parameters


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
        self.view.runtab.bt_preview_highres.bind("<ButtonRelease>", self.run_highrespreview)
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
        self.view.runtab.timelapse_aq_bt_run_timelapse.bind("<Button>", self.run_stop_preview)#1
        self.view.runtab.timelapse_aq_progressindicator.bind("<Button>", self.run_stop_preview)#2
        self.view.runtab.laser488_percentage.trace_add("read", self.updateLaserPower)
        self.view.runtab.laser552_percentage.trace_add("read", self.updateLaserPower)
        self.view.runtab.laser594_percentage.trace_add("read", self.updateLaserPower)
        self.view.runtab.laser640_percentage.trace_add("read", self.updateLaserPower)
        self.view.stagessettingstab.stage_moveto_axial.trace_add("write", self.movestage)
        self.view.stagessettingstab.stage_moveto_lateral.trace_add("write", self.movestage)
        self.view.stagessettingstab.stage_moveto_updown.trace_add("write", self.movestage)


        #buttons stage tab
        self.view.stagessettingstab.keyboard_input_on_bt.bind("<Button>", self.enable_keyboard_movement)
        self.view.stagessettingstab.keyboard_input_off_bt.bind("<Button>", self.disable_keyboard_movement)

        #define some parameters
        self.current_stackbuffersize = self.view.runtab.stack_aq_numberOfPlanes.get()
        self.stack_buffer = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes.get(),Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.current_laser = "488"

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

    def wait_forInput(self):
        print("All 'snap' threads finished execution.")
        input('Hit enter to close napari...')
    ##here follow the call to the functions of the model (microscope) that were bound above:

    def run_lowrespreview(self, event):
        '''
        Runs the execution of a low resolution preview.
        Required:
        change mirror, set exposure time, start preview, set continue_preview_highres to True.
        '''
        if self.model.continue_preview_lowres == False:

            # set parameter that you run a preview
            self.model.continue_preview_lowres = True
            self.model.laserOn = self.current_laser

            #set button layout - sunken relief
            def set_button():
                time.sleep(0.002)
                self.view.runtab.preview_change(self.view.runtab.bt_preview_lowres)
            ct.ResultThread(target=set_button).start()

            #run preview with given parameters
            self.model.exposure_time_LR = self.view.runtab.cam_lowresExposure.get()
            self.model.preview_lowres()
            print("running lowres preview")

    def run_highrespreview(self, event):
        '''
        Runs the execution of a high resolution preview.
        Required:
        change mirror, set exposure time, start preview, set continue_preview_highres to True.
        '''
        if self.model.continue_preview_highres == False:
            # set parameter that you run a preview
            self.model.continue_preview_highres = True
            self.model.laserOn = self.current_laser
            #set button layout - sunken relief
            def set_buttonHR():
                time.sleep(0.002)
                self.view.runtab.bt_preview_highres.config(relief="sunken")

            ct.ResultThread(target=set_buttonHR).start()

            #run preview with given parameters
            self.model.exposure_time_HR = self.view.runtab.cam_highresExposure.get() # set exposure time
            self.model.preview_highres()
            print("running high res preview")


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

    def movestage(self, event, laser, filter):
        # self.model.stagessettingstab.stage_trans_stepsize.get()
        # self.model.stagessettingstab.stage_rot_stepsize.get()

        lateralPosition = self.view.stagessettingstab.stage_moveto_lateral.get() * 1000000000
        updownPosition =self.view.stagessettingstab.stage_moveto_updown.get() * 1000000000
        axialPosition =self.view.stagessettingstab.stage_moveto_axial.get() * 1000000000
        anglePosition =self.view.stagessettingstab.stage_moveto_angle.get() * 1000000000
        moveToPosition = [axialPosition, lateralPosition, updownPosition, anglePosition]

        self.model.move_to_position(moveToPosition)

    def changefilter(self, event, laser, filter):
        print("filter " + filter + ", laser: "+ laser)
        if laser == '488':
            self.model.filterwheel.set_filter('515-30-25', wait_until_done=False)
            self.model.current_laser = NI_board_parameters.laser488
        if laser == '552':
            self.model.filterwheel.set_filter('572/20-25', wait_until_done=False)
            self.model.current_laser = NI_board_parameters.laser552
        if laser == '594':
            self.model.filterwheel.set_filter('615/20-25', wait_until_done=False)
            self.model.current_laser = NI_board_parameters.laser594
        if laser == '640':
            self.model.filterwheel.set_filter('676/37-25', wait_until_done=False)
            self.model.current_laser = NI_board_parameters.laser640

    def updateLaserPower(self, var,indx, mode):
        voltage488 = self.view.runtab.laser488_percentage.get()*5/100.
        voltage552 = self.view.runtab.laser552_percentage.get()*5/100.
        voltage594 = self.view.runtab.laser594_percentage.get()*5/100.
        voltage640 = self.view.runtab.laser640_percentage.get()*5/100.
        power_settings = [voltage488, voltage552, voltage594, voltage640]
        self.model.set_laserpower(power_settings)



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

        def update_stackbuffer():
            try:
                    self.stack_buffer.fill(0)
                    self.current_stackbuffersize = self.stack_buffer_nb
            except:
                print("update error")

        self.stack_buffer_nb = self.view.runtab.stack_aq_numberOfPlanes.get()

        if self.stack_buffer_nb != self.current_stackbuffersize:
            ct.ResultThread(target=update_stackbuffer).start()

        #self.root.after(5000, self.automatically_update_stackbuffer)

    def acquire_stack(self, event):
        self.view.runtab.stack_aq_bt_run_stack.config(relief="sunken")
        self.view.update()

        #stop all potential previews
        self.model.continue_preview_lowres = False
        self.model.continue_preview_highres = False

        #set model parameters
        self.model.stack_nbplanes = self.view.runtab.stack_aq_numberOfPlanes.get()
        self.model.exposure_time_LR = self.view.runtab.cam_lowresExposure.get()
        self.model.exposure_time_HR = self.view.runtab.cam_highresExposure.get()

        self.view.runtab.stack_aq_lowResCameraOn.get()
        print(self.view.runtab.stack_aq_highResCameraOn.get())
        self.view.runtab.stack_acq_laserCycleMode.get()
        self.view.runtab.stack_aq_488on.get()
        self.view.runtab.stack_aq_552on.get()
        self.view.runtab.stack_aq_594on.get()
        self.view.runtab.stack_aq_640on.get()

        #which parameters to run

        self.model.stack_buffer_lowres = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes.get(),
                                              Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel),
                                             dtype='uint16')
        self.model.stack_buffer_lowres.fill(0)
        #self.model.filepath = self.view.welcometab.filepath_string.get()

        #self.model.acquire_stack_lowres()

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





