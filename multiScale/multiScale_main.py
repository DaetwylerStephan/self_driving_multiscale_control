import tkinter as tk
from tkinter import ttk

import time
from threading import Thread
import numpy as np
import datetime as dt
import os
import glob


from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel
import auxiliary_code.concurrency_tools as ct
from constants import Camera_parameters
from constants import NI_board_parameters
from constants import FileSave_parameters
from constants import ASLM_parameters


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
        self.continuetimelapse = 1 #enable functionality to stop timelapse

        #######connect buttons / variables from GUI with functions here-----------------------------------
        self.view.runtab.bt_preview_lowres.bind("<ButtonRelease>", self.run_lowrespreview)
        self.view.runtab.bt_preview_highres.bind("<ButtonRelease>", self.run_highrespreview)
        self.view.runtab.bt_preview_stop.bind("<Button>", self.run_stop_preview)
        self.view.runtab.bt_changeTo488.bind("<Button>", lambda event: self.changefilter(event, '488'))
        self.view.runtab.bt_changeTo552.bind("<Button>", lambda event: self.changefilter(event, '552'))
        self.view.runtab.bt_changeTo594.bind("<Button>", lambda event: self.changefilter(event, '594'))
        self.view.runtab.bt_changeTo640.bind("<Button>", lambda event: self.changefilter(event, '640'))
        self.view.runtab.bt_changeTo_block.bind("<Button>", lambda event: self.changefilter(event, 'None'))
        self.view.runtab.bt_changeTo_trans.bind("<Button>", lambda event: self.changefilter(event, 'LED'))
        self.view.runtab.stack_aq_bt_run_stack.bind("<Button>", self.acquire_stack)
        #self.view.runtab.stack_aq_numberOfPlanes.trace_add("write", self.updateNbPlanes)
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
        self.view.stagessettingstab.stage_moveto_angle.trace_add("write", self.movestage)
        #buttons advanced settings tab
        self.view.advancedSettingstab.slit_currentsetting.trace_add("write", self.slit_opening_move)
        self.view.advancedSettingstab.slit_lowres.trace_add("write", self.slit_opening_setPositions)
        self.view.advancedSettingstab.slit_highres.trace_add("write", self.slit_opening_setPositions)
        self.view.advancedSettingstab.ASLM_volt_current.trace_add("write", self.update_remoteMirrorVoltage)
        self.view.advancedSettingstab.ASLM_alignmentmodeOn.trace_add("write", self.update_ASLM_alignmentsettings)
        self.view.advancedSettingstab.ASLM_SawToothOn.trace_add("write", self.update_ASLM_alignmentsettings)
        self.view.advancedSettingstab.ASLM_constantVoltageOn.trace_add("write", self.update_ASLM_alignmentsettings)
        self.view.advancedSettingstab.ASLM_volt_min.trace_add("write", self.update_remoteMirrorVoltage)
        self.view.advancedSettingstab.ASLM_volt_max.trace_add("write", self.update_remoteMirrorVoltage)

        #buttons stage tab
        self.view.stagessettingstab.keyboard_input_on_bt.bind("<Button>", self.enable_keyboard_movement)
        self.view.stagessettingstab.keyboard_input_off_bt.bind("<Button>", self.disable_keyboard_movement)

        #define some parameters

        #self.stack_buffer_lowres = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes_lowres.get(),Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.current_laser = "488"

    def run(self):
        """
        Run the Tkinter Gui in the main loop
        :return:
        """
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)
        #self.automatically_update_stackbuffer()
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

            #change mirror position/slit position
            self.model.changeHRtoLR()

            # set parameter that you run a preview
            self.model.continue_preview_lowres = True
            #self.model.laserOn = self.current_laser

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

            # change mirror position/slit position
            self.model.changeLRtoHR()

            # set parameter that you run a preview
            self.model.continue_preview_highres = True
            #self.model.laserOn = self.current_laser

            #set button layout - sunken relief
            def set_buttonHR():
                time.sleep(0.002)
                self.view.runtab.bt_preview_highres.config(relief="sunken")
            ct.ResultThread(target=set_buttonHR).start()

            #run preview with given parameters
            self.model.exposure_time_HR = self.view.runtab.cam_highresExposure.get() # set exposure time

            #ASLM or static light-sheet mode
            if self.view.runtab.cam_highresMode.get()=='SPIM Mode':
                self.model.preview_highres_static()
                print("running high res static preview")
            else:
                self.model.preview_highres_ASLM(self.view.runtab.cam_highresExposure.get())
                print("running high res ASLM preview")

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

    def movestage(self, var,indx, mode):
        """
        moves the stage to a certain position
        """
        #get positions from GUI and constract position array "moveToPosition"
        lateralPosition = self.view.stagessettingstab.stage_moveto_lateral.get() * 1000000000
        updownPosition =self.view.stagessettingstab.stage_moveto_updown.get() * 1000000000
        axialPosition =self.view.stagessettingstab.stage_moveto_axial.get() * 1000000000
        anglePosition =self.view.stagessettingstab.stage_moveto_angle.get() * 1000000
        moveToPosition = [axialPosition, lateralPosition, updownPosition, anglePosition]

        #move
        self.model.move_to_position(moveToPosition)

    def slit_opening_move(self, var,indx, mode):
        """
        changes the slit opening
        """
        currentslitopening = self.view.advancedSettingstab.slit_currentsetting.get()
        self.model.move_adjustableslit(currentslitopening)

    def slit_opening_setPositions(self, var,indx, mode):
        """
        set the low resolution and high-resolution slit openings
        """
        self.model.slitopening_lowres = self.view.advancedSettingstab.slit_lowres.get()
        self.model.slitopening_highres = self.view.advancedSettingstab.slit_highres.get()

    def changefilter(self, event, laser):
        """
        changes the filter to the specified one by the laser active
        """
        print("change filter to laser: " + laser)
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
        """
        update the laser power
        """
        #get laser power from GUI and construct laser power setting array
        voltage488 = self.view.runtab.laser488_percentage.get()*5/100.
        voltage552 = self.view.runtab.laser552_percentage.get()*5/100.
        voltage594 = self.view.runtab.laser594_percentage.get()*5/100.
        voltage640 = self.view.runtab.laser640_percentage.get()*5/100.
        power_settings = [voltage488, voltage552, voltage594, voltage640]

        #change laser power
        self.model.set_laserpower(power_settings)

    def update_remoteMirrorVoltage(self, var,indx, mode):
        """
        update the remote mirror voltage power, check for boundaries to not apply too high voltages
        """
        minVol = ASLM_parameters.remote_mirror_minVol
        maxVol = ASLM_parameters.remote_mirror_maxVol

        #get remote mirror voltage from GUI and update model parameter, also check for boundaries
        self.model.ASLM_currentVolt = min(maxVol, max(minVol, self.view.advancedSettingstab.ASLM_volt_current.get()))
        self.model.ASLM_minVolt = min(maxVol, max(minVol, self.view.advancedSettingstab.ASLM_volt_min.get()))
        self.model.ASLM_maxVolt = max(minVol, min(maxVol, self.view.advancedSettingstab.ASLM_volt_max.get()))

        print("update voltages")


    def update_ASLM_alignmentsettings(self, var,indx, mode):
        """
        update the ASLM alignment settings
        """
        #get remote mirror voltage from GUI and update model parameter
        self.model.ASLM_alignmentOn = self.view.advancedSettingstab.ASLM_volt_current.get()

        runmode = self.view.advancedSettingstab.ASLM_SawtoothORconstant.get()
        if runmode =='Sawtooth':
            self.model.ASLM_Sawtooth =1
            self.model.ASLM_ConstantVoltage = 0
        else:
            self.model.ASLM_Sawtooth = 0
            self.model.ASLM_ConstantVoltage = 1

    def updatefilename(self):
        """
        construct the filename used to save data, based on the information from the GUI
        """
        parentdir = FileSave_parameters.parentdir

        modelorganism = self.view.welcometab.welcome_modelorganism.get()
        date = dt.datetime.now().strftime("%Y%m%d")
        username = self.view.welcometab.welcome_username.get()

        foldername = date + "_" + modelorganism
        if username == "Stephan Daetwyler":
            foldername = date + "_Daetwyler_" + modelorganism
        if username == "Reto Fiolka":
            foldername = date + "_Fiolka_" + modelorganism
        if username == "Bo-Jui Chang":
            foldername = date + "_Chang_" + modelorganism
        if username == "Dagan Segal":
            foldername = date + "_Segal_" + modelorganism

        self.parentfolder = os.path.join(parentdir, foldername)



    def acquire_stack(self, event):
        """
        acquire a stack acquisition
        """
        self.view.runtab.stack_aq_bt_run_stack.config(relief="sunken")
        self.view.update()
        self.updatefilename()

        #stop all potential previews
        self.model.continue_preview_lowres = False
        self.model.continue_preview_highres = False

        #set model parameters
        self.model.stack_nbplanes_lowres = self.view.runtab.stack_aq_numberOfPlanes_lowres.get()
        self.model.stack_nbplanes_highres = self.view.runtab.stack_aq_numberOfPlanes_highres.get()
        self.model.exposure_time_LR = self.view.runtab.cam_lowresExposure.get()
        self.model.exposure_time_HR = self.view.runtab.cam_highresExposure.get()

        #save acquistition parameters and construct file name to save (only if not time-lapse)
        stackfilepath = self.parentfolder
        if self.continuetimelapse != 0:
            #generate file path
            nbfiles_folder = len(glob.glob('Experiment*'))
            newfolderind = nbfiles_folder + 1
            experiment_name = "Experiment" + f'{newfolderind:04}'

            #write acquisition parameters
            filepath_write_acquisitionParameters = os.path.join(self.parentfolder, experiment_name)
            try:
                print("filepath : " + filepath_write_acquisitionParameters)
                os.makedirs(filepath_write_acquisitionParameters)
            except OSError as error:
                print("File writing error")
            self.write_to_textfile(os.path.join(filepath_write_acquisitionParameters, 'Experiment_settings.txt'))

            #set timepoint = 0 to be consistent with time-lapse acquisitions
            stackfilepath = os.path.join(self.parentfolder, experiment_name, "t00000")
            print(stackfilepath)


        #init shared memory
        self.model.stack_buffer_lowres = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes_lowres.get(),
                                                           Camera_parameters.LR_height_pixel,
                                                           Camera_parameters.LR_width_pixel),
                                                          dtype='uint16')
        self.model.stack_buffer_highres = ct.SharedNDArray((self.view.runtab.stack_aq_numberOfPlanes_highes.get(),
                                                           Camera_parameters.HR_height_pixel,
                                                           Camera_parameters.HR_width_pixel),
                                                          dtype='uint16')
        #self.model.stack_buffer_lowres.fill(0)

        print("acquiring low res stack")
        print("number of planes: " + str(self.view.runtab.stack_aq_numberOfPlanes_highres.get()) + ", plane spacing: " + str(
            self.view.runtab.stack_aq_plane_spacing.get()))

        ########-------------------------------------------------------------------------------------------------------
        #start low resolution stack acquisition
        if self.view.runtab.stack_aq_lowResCameraOn.get():
            positioniter = -1
            for line in self.view.stagessettingstab.stage_savedPos_tree.get_children():
                #get current position from list
                xpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(line)['values'][1]) * 1000000000)
                ypos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(line)['values'][2])* 1000000000)
                zpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(line)['values'][3])* 1000000000)
                angle = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(line)['values'][4]) * 1000000)
                current_startposition = [zpos, xpos, ypos, angle]
                print(current_startposition)
                positioniter = positioniter + 1

                # filepath
                current_folder = os.path.join(stackfilepath, "low_stack" + f'{positioniter:03}')
                try:
                    print("filepath : " + current_folder)
                    os.makedirs(current_folder)
                except OSError as error:
                    print("File writing error")

                #start stackstreaming
                which_channels = [self.view.runtab.stack_aq_488on.get(), self.view.runtab.stack_aq_552on.get(), self.view.runtab.stack_aq_594on.get(), self.view.runtab.stack_aq_640on.get()]
                self.model.stack_acquisition_master(current_folder, current_startposition, which_channels, "low")

        ########-------------------------------------------------------------------------------------------------------
        # start high resolution stack acquisition
        #high resolution list
        if self.view.runtab.stack_aq_highResCameraOn.get():
            for line in self.view.stagessettingstab.stage_highres_savedPos_tree.get_children():
                #get current position from list
                xpos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][1]) * 1000000000)
                ypos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][2])* 1000000000)
                zpos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][3])* 1000000000)
                angle = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][4]) * 1000000)
                currentposition = [zpos, xpos, ypos, angle]
                print(currentposition)

                #define highresolution stack path by corner positions.
                xpos_label = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][1])*1000)
                ypos_label = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(line)['values'][1])*1000)

                # filepath
                current_folder = os.path.join(stackfilepath, "high_stack_" + str(xpos_label)+ "_" + str(ypos_label))
                try:
                    print("filepath : " + current_folder)
                    os.makedirs(current_folder)
                except OSError as error:
                    print("File writing error")

                # start stackstreaming
                which_channels = [self.view.runtab.stack_aq_488on.get(), self.view.runtab.stack_aq_552on.get(),
                                      self.view.runtab.stack_aq_594on.get(), self.view.runtab.stack_aq_640on.get()]

                if self.view.runtab.cam_highresMode.get()=="SPIM Mode":
                    self.model.high_res_stack_acquisition_master(current_folder, current_startposition, which_channels, "highSPIM")
                else:
                    self.model.high_res_stack_acquisition_master(current_folder, current_startposition, which_channels, "highASLM")

        self.view.runtab.stack_aq_bt_run_stack.config(relief="raised")




    def acquire_timelapse(self, event):
        """
        start a time-lapse acquisition thread, called from GUI (otherwise it freezes)
        """

        #update GUI
        self.view.runtab.updateTimesTimelapse()
        self.view.update_idletasks()
        self.view.update()
        self.view.runtab.timelapse_aq_progressbar.config(maximum=self.view.runtab.timelapse_aq_nbTimepoints-1)
        # set button layout - sunken relief
        def set_buttonTL():
            time.sleep(0.002)
            self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="sunken")
        ct.ResultThread(target=set_buttonTL).start()

        # stop all potential previews
        self.model.continue_preview_lowres = False
        self.model.continue_preview_highres = False

        self.continuetimelapse = 0
        print("acquiring timelapse")

        #(1) NOTE: You cannot use a While loop here as it makes the Tkinter mainloop freeze - put the time-lapse instead into a thread
        #(2) where you can run while loops etc.
        self.timelapse_thread = Thread(target=self.run_timelapse)
        self.timelapse_thread.start()
        #after that main loop continues


    def run_timelapse(self):
        """
        thread that controls time-lapse, started from function acquire_timelapse(self, event):
        """

        #todo implement here time-lapse functionalities
        varb = str(np.random.randint(0, 100))
        self.view.update()

        for timeiter in range(0, self.view.runtab.timelapse_aq_nbTimepoints):
            t0 = time.clock()
            self.view.runtab.timelapse_aq_progress.set(timeiter)
            self.view.runtab.timelapse_aq_progressindicator.config(text=str(timeiter+1) +" of " + str(self.view.runtab.timelapse_aq_nbTimepoints))


            print("hello " + varb)
            time.sleep(2)

            ## stop time-lapse acquisition if you stop it
            if self.continuetimelapse == 1:
                break  # Break while loop when stop = 1


            #calculate the time until next stack acquisition starts
            t1 = time.clock() - t0
            totaltime = self.view.runtab.timelapse_aq_timeinterval_min.get() * 60 + self.view.runtab.timelapse_aq_timeinterval_seconds.get()

            remaining_waittime = totaltime - t1



        self.view.runtab.timelapse_aq_bt_run_timelapse.config(relief="raised")
        self.view.update()


    def abort_timelapse(self,event):
        self.continuetimelapse = 1

#write experiment parameters to textfile
    def write_to_textfile(self, filePath):
        with open(filePath, 'w') as f:
            f.write('Experiment parameters of ' + self.parentfolder + "\n")
            f.write('---------------------------------------------\n')
            f.write('Plane spacing lowres: ' + str(self.view.runtab.stack_aq_plane_spacing_lowres.get()) + "\n")
            f.write('Plane spacing highres: ' + str(self.view.runtab.stack_aq_plane_spacing_highres.get()) + "\n")
            f.write('Nb of planes lowres: ' + str(self.view.runtab.stack_aq_numberOfPlanes_lowres.get()) + "\n")
            f.write('Nb of planes highres: ' + str(self.view.runtab.stack_aq_numberOfPlanes_highres.get()) + "\n")

            f.write('---------------------------------------------\n')
            f.write('low resultion stack positions\n')

            for iter_lowrespos in self.view.stagessettingstab.stage_savedPos_tree.get_children():
                #get current position from list
                xpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][1]))
                ypos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][2]))
                zpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][3]))
                angle = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][4]))
                current_startposition = [zpos, xpos, ypos, angle]
                f.write(str(current_startposition) + "\n")

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





