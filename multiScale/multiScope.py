import queue
import time
import os
import atexit
import threading
import numpy as np

import auxiliary_code.concurrency_tools as ct
import auxiliary_code.napari_in_subprocess as napari

import src.camera.Photometrics_camera as Photometricscamera
import src.ni_board.vni as ni
import src.stages.rotation_stage_cmd as RotStage
import src.stages.translation_stage_cmd as TransStage
import src.filter_wheel.ludlcontrol as FilterWheel
import src.slit.slit_cmd as SlitControl

from constants import FilterWheel_parameters
from constants import Stage_parameters
from constants import NI_board_parameters
from constants import Camera_parameters
from constants import ASLM_parameters
from tifffile import imread, imwrite

class multiScopeModel:
    def __init__(
        self
        ):
        """
        We use bytes_per_buffer to specify the shared_memory_sizes for the
        child processes.
        """
        self.unfinished_tasks = queue.Queue()

        self.data_buffers = [
            ct.SharedNDArray(shape=(2960, 5056), dtype='uint16')
            for i in range(2)]
        self.data_buffer_queue = queue.Queue()
        for i in range(len(self.data_buffers)):
            self.data_buffer_queue.put(i)
        print("Displaying", self.data_buffers[0].shape,
              self.data_buffers[0].dtype, 'images.')
        self.num_frames = 0
        self.initial_time = time.perf_counter()

        #parameters
        self.exposure_time_HR = 200
        self.exposure_time_LR = 200
        self.continue_preview_lowres = False
        self.continue_preview_highres = False
        self.stack_nbplanes_lowres =200
        self.stack_nbplanes_highres = 200
        self.lowres_planespacing = 10000000
        self.highres_planespacing = 10000000
        # self.stack_buffer_lowres = ct.SharedNDArray(shape=(self.stack_nbplanes_lowres, Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        # self.stack_buffer_lowres.fill(0)
        # self.stack_buffer_highres = ct.SharedNDArray(shape=(self.stack_nbplanes_highres, Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel), dtype='uint16')
        # self.stack_buffer_highres.fill(0)
        self.filepath = 'D:/acquisitions/testimage.tif'
        self.current_laser = NI_board_parameters.laser488
        self.channelIndicator = "00"
        self.slitopening_lowres = 1500
        self.slitopening_highres= 4558

        self.current_lowresROI_width = Camera_parameters.LR_width_pixel
        self.current_lowresROI_height = Camera_parameters.LR_height_pixel
        self.current_highresROI_width = Camera_parameters.HR_width_pixel
        self.current_highresROI_height = Camera_parameters.HR_height_pixel

        self.ASLM_acquisition_time = 0.3
        self.ASLM_from_Volt = 0 #first voltage applied at remote mirror
        self.ASLM_to_Volt = 1 #voltage applied at remote mirror at the end of sawtooth
        self.ASLM_currentVolt = 0 #current voltage applied to remote mirror
        self.ASLM_staticLowResVolt = 0 #default ASLM low res voltage
        self.ASLM_staticHighResVolt = 0 #default ASLM high res voltage
        self.ASLM_alignmentOn = 0 #param=1 if ASLM alignment mode is on, otherwise zero
        self.ASLM_Sawtooth = 0 #alignment mode - run sawtooth
        self.ASLM_ConstantVoltage = 0 #alignment mode - run constant voltage
        self.delay_cameratrigger = 0.001  # the time given for the stage to move to the new position

        #preview buffers
        self.low_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.high_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel), dtype='uint16')
        self.low_res_buffer.fill(0) #fill to initialize
        self.high_res_buffer.fill(0) #fill to initialize

        #textlabels for GUI
        self.currentFPS = str(0)

        self.high_res_buffers = [
            ct.SharedNDArray(shape=(Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel), dtype='uint16')
            for i in range(2)]
        for i in range(2):
            self.high_res_buffers[i].fill(0) # fill them
        print("Displaying 2: ", self.high_res_buffers[0].shape,
              self.high_res_buffers[0].dtype, 'images.')

        self.high_res_buffers_queue = queue.Queue()
        for i in range(len(self.high_res_buffers)):
            self.high_res_buffers_queue.put(i)

        #start initializing all hardware component here by calling the initialization from a ResultThread
        lowres_camera_init = ct.ResultThread(target=self._init_lowres_camera).start() #~3.6s
        highres_camera_init = ct.ResultThread(target=self._init_highres_camera).start() #~3.6s
        self._init_display() #~1.3s


        #initialize stages and stages in ResultThreads
        trans_stage_init = ct.ResultThread(target=self._init_XYZ_stage).start() #~0.4s
        rot_stage_init = ct.ResultThread(target=self._init_rotation_stage).start()
        filterwheel_init = ct.ResultThread(target=self._init_filterwheel).start()  # ~5.3s
        slit_init = ct.ResultThread(target=self._init_slit).start()  #


        self._init_ao()  # ~0.2s

        #wait for all started initialization threads before continuing (by calling thread join)
        lowres_camera_init.get_result()
        highres_camera_init.get_result()
        filterwheel_init.get_result()
        trans_stage_init.get_result()
        rot_stage_init.get_result()
        slit_init.get_result()

        print('Finished initializing multiScope')

    def _init_lowres_camera(self):
        """
        Initialize low resolution camera
        """
        print("Initializing low resolution camera ..")
        #place the Photometrics class as object into an Object in Subprocess
        self.lowres_camera = ct.ObjectInSubprocess(Photometricscamera.Photo_Camera, 'PMPCIECam00')
        #self.lowres_camera.take_snapshot(20)
        print("done with camera.")

    def _init_highres_camera(self):
        """
        Initialize low resolution camera
        """
        print("Initializing high resolution camera..")
        #place the Photometrics class as object into an Object in Subprocess
        self.highres_camera = ct.ObjectInSubprocess(Photometricscamera.Photo_Camera, 'PMUSBCam00')
        #self.lowres_camera.take_snapshot(20)
        print("done with camera.")

    def _init_display(self):
        print("Initializing display...")
        self.display = ct.ObjectInSubprocess(napari._NapariDisplay, custom_loop= napari._napari_child_loop, close_method_name='close')

        print("done with display.")

    def _init_ao(self):
        """
        Initialize National Instruments card 6378 as device 1, Dev1
        """
        print("Initializing ao card...", end=' ')

        self.ao = ni.Analog_Out(
            num_channels=NI_board_parameters.ao_nchannels,
            rate=NI_board_parameters.rate,
            daq_type=NI_board_parameters.ao_type,
            line=NI_board_parameters.line_selection,
            verbose=True)

        self.ao_laser488_power = ni.Analog_Out(
            daq_type=NI_board_parameters.ao_type_constant,
            line=NI_board_parameters.power_488_line,
            minVol=NI_board_parameters.minVol_constant,
            maxVol=NI_board_parameters.maxVol_constant,
            verbose=True)
        self.ao_laser552_power = ni.Analog_Out(
            daq_type=NI_board_parameters.ao_type_constant,
            line=NI_board_parameters.power_552_line,
            minVol=NI_board_parameters.minVol_constant,
            maxVol=NI_board_parameters.maxVol_constant,
            verbose=True)
        self.ao_laser594_power = ni.Analog_Out(
            daq_type=NI_board_parameters.ao_type_constant,
            line=NI_board_parameters.power_594_line,
            minVol=NI_board_parameters.minVol_constant,
            maxVol=NI_board_parameters.maxVol_constant,
            verbose=True)
        self.ao_laser640_power = ni.Analog_Out(
            daq_type=NI_board_parameters.ao_type_constant,
            line=NI_board_parameters.power_640_line,
            minVol=NI_board_parameters.minVol_constant,
            maxVol=NI_board_parameters.maxVol_constant,
            verbose=True)
        self.flipMirrorPosition_power = ni.Analog_Out(
            daq_type=NI_board_parameters.ao_type_constant,
            line=NI_board_parameters.flip_mirror_line,
            minVol=NI_board_parameters.minVol_constant,
            maxVol=NI_board_parameters.maxVol_constant,
            verbose=True)
        print("done with ao.")
        atexit.register(self.ao.close)

    def _init_filterwheel(self):
        """
        Initialize filterwheel
        """
        ComPort = FilterWheel_parameters.comport
        self.filters = FilterWheel_parameters.avail_filters

        print("Initializing filter wheel...", end=' ')
        self.filterwheel = FilterWheel.LudlFilterwheel(ComPort, self.filters)
        self.filterwheel.set_filter('515-30-25', wait_until_done=False)
        self.filterwheel.set_filter('572/20-25', wait_until_done=False)
        self.filterwheel.set_filter('615/20-25', wait_until_done=False)
        self.filterwheel.set_filter('676/37-25', wait_until_done=False)
        print("done with filterwheel.")

    def _init_shared_Memory(self):
        #init shared memory
        self.stack_buffer_lowres = ct.SharedNDArray((200, Camera_parameters.LR_height_pixel,
                                                           Camera_parameters.LR_width_pixel),
                                                          dtype='uint16')
        self.stack_buffer_lowres.fill(0)

        self.stack_buffer_highres = ct.SharedNDArray((200, Camera_parameters.HR_height_pixel,
                                                     Camera_parameters.HR_width_pixel),
                                                    dtype='uint16')
        self.stack_buffer_highres.fill(0)


    def _init_XYZ_stage(self):
        """
        Initialize translation stage
        """
        print("Initializing XYZ stage usb:sn:MCS2-00001795...")
        stage_id = Stage_parameters.stage_id_XYZ
        self.XYZ_stage = TransStage.SLC_translationstage(stage_id)
        self.XYZ_stage.findReference()
        print("done with XYZ stage.")
        atexit.register(self.XYZ_stage.close)

    def _init_rotation_stage(self):
        """
        Initialize rotation stage
        """
        print("Initializing rotation stage...")
        stage_id = Stage_parameters.stage_id_rot
        self.rotationstage = RotStage.SR2812_rotationstage(stage_id)
        #self.rotationstage.ManualMove()
        print("done with XY stage.")
        atexit.register(self.rotationstage.close)

    def _init_slit(self):
        """
        Initialize motorized slit
        """
        self.adjustableslit = SlitControl.slit_ximc_control()
        self.adjustableslit.slit_info()
        self.adjustableslit.slit_status()
        self.adjustableslit.slit_set_microstep_mode_256()
        self.adjustableslit.home_stage()
        print("slit homed")
        self.adjustableslit.slit_set_speed(1000)


    def close(self):
        """
        Close all opened channels, camera etc
                """
        self.finish_all_tasks()
        self.lowres_camera.close()
        self.highres_camera.close()
        self.ao.close()
        self.rotationstage.close()
        self.XYZ_stage.close()
        self.adjustableslit.slit_closing()
        self.display.close()  # more work needed here
        print('Closed multiScope')

    def finish_all_tasks(self):
        collected_tasks = []
        while True:
            try:
                th = self.unfinished_tasks.get_nowait()
            except queue.Empty:
                break
            th.join()
            collected_tasks.append(th)
        return collected_tasks

    def set_laserpower(self, powersettings):
        self.ao_laser488_power.setconstantvoltage(powersettings[0])
        self.ao_laser552_power.setconstantvoltage(powersettings[1])
        self.ao_laser594_power.setconstantvoltage(powersettings[2])
        self.ao_laser640_power.setconstantvoltage(powersettings[3])

    def move_to_position(self, positionlist):
        print(str(positionlist[0:3]))
        positionlistInt = np.array(positionlist, dtype=np.int64)
        self.XYZ_stage.moveToPosition(positionlistInt[0:3])
        self.rotationstage.moveToAngle(positionlist[3])

    def move_adjustableslit(self, slitopening, wait=0):
        """
        :param slitopening: move to this slitopening;
        :param if wait==1 - wait for slit move to finish before continuing
        """
        self.adjustableslit.slit_move(int(slitopening),0)
        if wait==1:
            self.adjustableslit.slit_wait_for_stop(100)



    def changeLRtoHR(self):
        """
        change from low resolution to high resolution acquisition settings
        """
        self.flipMirrorPosition_power.setconstantvoltage(3)
        self.move_adjustableslit(self.slitopening_highres, 1)


    def changeHRtoLR(self):
        """
        change from high resolution to low resolution acquisition settings
        """
        self.flipMirrorPosition_power.setconstantvoltage(0)
        self.move_adjustableslit(self.slitopening_lowres, 1)


    def preview_lowres(self):
        """
        starts a custody thread to run a low resolution preview.
        """
        def preview_lowres_task(custody):
            self.num_frames = 0
            self.initial_time = time.perf_counter()

            #define array for laser
            basic_unit = np.zeros((self.ao.s2p(0.3), NI_board_parameters.ao_nchannels), np.dtype(np.float64))

            def laser_preview():
                old_laserline = 0
                while self.continue_preview_lowres:
                    basic_unit[:, old_laserline] = 0
                    old_laserline = self.current_laser
                    basic_unit[:, self.current_laser] = 4.  # set TTL signal of the right laser to 4

                    if self.ASLM_alignmentOn == 1:
                        if self.ASLM_Sawtooth:
                            basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_minVolt
                            basic_unit[0: self.ao.s2p(0.2), NI_board_parameters.voicecoil] = np.linspace(self.ASLM_minVolt, self.ASLM_maxVolt, self.ao.s2p(0.2))
                            basic_unit[(self.ao.s2p(0.2)):self.ao.s2p(0.3), NI_board_parameters.voicecoil] = np.linspace(self.ASLM_maxVolt, self.ASLM_minVolt, self.ao.s2p(0.1))
                        else:
                            basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_currentVolt #set voltage of remote mirror
                    else:
                        basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_staticLowResVolt #set voltage of remote mirror

                    self.ao.play_voltages(basic_unit, block=True)

            ct.ResultThread(target=laser_preview).start()

            while self.continue_preview_lowres:
                self.lowres_camera.set_up_preview(self.exposure_time_LR)

                custody.switch_from(None, to=self.lowres_camera)
                self.lowres_camera.run_preview(out=self.low_res_buffer)
                custody.switch_from(self.lowres_camera, to=self.display)
                self.display.show_image_lowres(self.low_res_buffer)
                custody.switch_from(self.display, to=None)
                self.num_frames += 1
                #calculate fps to display
                if self.num_frames == 100:
                    time_elapsed = time.perf_counter() - self.initial_time
                    print("%0.2f average FPS" % (self.num_frames / time_elapsed))
                    self.num_frames = 0
                    self.initial_time = time.perf_counter()

            self.lowres_camera.end_preview()


        self.continue_preview_lowres = True
        th = ct.CustodyThread(target=preview_lowres_task, first_resource=None)
        th.start()
        return th

    ###this is the code to run a high resolution preview with a static light-sheet
    def preview_highres_static(self):
        def preview_highres_task(custody):

            self.num_frames = 0
            self.initial_time = time.perf_counter()



            def laser_preview_highres():
                #old_laserline = 0
                while self.continue_preview_highres:
                    # define array for laser
                    min_time = max(self.exposure_time_HR / 1000, 0.3)
                    basic_unit = np.zeros((self.ao.s2p(min_time), NI_board_parameters.ao_nchannels),
                                          np.dtype(np.float64))

                    #basic_unit[:,old_laserline] = 0
                    #old_laserline = self.current_laser
                    basic_unit[:, self.current_laser] = 4.  # set TTL signal of the right laser to 4
                    basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_staticHighResVolt #set voltage of remote mirror
                    self.ao.play_voltages(basic_unit, block=True)

            #run laser as sub-thread that is terminated when the preview button is pressed (self.continue_preview_highres is false).
            ct.ResultThread(target=laser_preview_highres).start()

            while self.continue_preview_highres:
                self.highres_camera.set_up_preview(self.exposure_time_HR, 1)
                self.num_frames += 1
                custody.switch_from(None, to=self.highres_camera)
                self.highres_camera.run_preview(out=self.high_res_buffer)

                custody.switch_from(self.highres_camera, to=self.display)
                self.display.show_image_highres(self.high_res_buffer)
                custody.switch_from(self.display, to=None)

                if self.num_frames == 100:
                    time_elapsed = time.perf_counter() - self.initial_time
                    avg_FPS = (self.num_frames / time_elapsed)
                    print("%0.2f average FPS" % avg_FPS)
                    self.currentFPS = str(avg_FPS)
                    self.num_frames = 0
                    self.initial_time = time.perf_counter()

            self.highres_camera.end_preview()

        self.continue_preview_highres = True
        th = ct.CustodyThread(target=preview_highres_task, first_resource=self.highres_camera)
        th.start()
        return th

    def calculate_ASLMparameters(self, desired_exposuretime):
        """
        calculate the parameters for an ASLM acquisition
        :param desired_exposuretime: the exposure time that is desired for the whole acquisition
        :return: set the important parameters for ASLM acquisitions
        """
        self.ASLM_lineExposure = int(np.ceil(desired_exposuretime / (1 + self.currentROI_y/ASLM_parameters.simultaneous_lines)))
        self.ASLM_line_delay = int(np.ceil((desired_exposuretime - self.ASLM_lineExposure)/(self.currentROI_y *ASLM_parameters.line_delay)))
        self.ASLM_acquisition_time = self.ASLM_line_delay * self.currentROI_y * ASLM_parameters.line_delay + self.ASLM_lineExposure

        print("ASLM parameters are: {} exposure time, and {} line delay factor, {} total acquisition time".format(self.ASLM_lineExposure, self.ASLM_line_delay, self.ASLM_acquisition_time))

    def preview_highres_ASLM(self):
        def preview_highresASLM_task(custody):

            self.num_frames = 0
            self.initial_time = time.perf_counter()

            while self.continue_preview_highres:

                #calculate ALSM parameters
                self.calculate_ASLMparameters(self.exposure_time_HR)
                self.highres_camera.prepare_ASLM_acquisition(self.ASLM_lineExposure, self.ASLM_line_delay)

                #generate array
                totallength = self.ao.s2p(0.001 + self.ASLM_acquisition_time/1000 + 0.02)
                basic_unit = np.zeros((totallength, NI_board_parameters.ao_nchannels), np.dtype(np.float64))

                basic_unit[self.ao.s2p(0.001):totallength, self.current_laser] = 4
                basic_unit[self.ao.s2p(0.001) : self.ao.s2p(0.002),0] = 4.  # high-res camera

                if self.ASLM_alignmentOn == 1:
                    #during alignment, set constant voltage
                    basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_currentVolt  # high-res camera
                else:
                    sawtooth_array = np.zeros(totallength, np.dtype(np.float64))
                    sawtooth_array[:] = self.ASLM_from_Volt
                    goinguppoints = self.ao.s2p(0.001 + self.ASLM_acquisition_time/1000)
                    goingdownpoints = self.ao.s2p(0.001 + self.ASLM_acquisition_time/1000 + 0.02) - goinguppoints
                    sawtooth_array[0:goinguppoints] = np.linspace(self.ASLM_from_Volt, self.ASLM_to_Volt, goinguppoints)
                    sawtooth_array[goinguppoints:] = np.linspace(self.ASLM_to_Volt, self.ASLM_from_Volt, goingdownpoints)

                    basic_unit[:, NI_board_parameters.voicecoil] = self.smooth_sawtooth(sawtooth_array, window_len = self.ao.s2p(0.01))

                print("array generated")

                custody.switch_from(None, to=self.highres_camera)

                # write voltages, indicate "False" so that the voltages are not set back to zero at the end (for the remote mirror)
                write_voltages_thread = ct.ResultThread(target=self.ao._write_voltages, args=(basic_unit,False),
                                                        ).start()

                #start camera thread to poll for new images
                def start_camera_streamASLMpreview():
                    self.highres_camera.run_preview_ASLM(out=self.high_res_buffer)

                camera_stream_thread_ASLMpreview = ct.ResultThread(target=start_camera_streamASLMpreview).start()

                #play voltages
                self.ao.play_voltages(block=True, force_final_zeros=False)

                print("voltages played")
                camera_stream_thread_ASLMpreview.get_result()
                print("camera thread returned")
                self.num_frames += 1



                #calculate fps to display
                #if (self.num_frames % 2 ==0): #Napari can only display 20fps
                if 1==1:
                    custody.switch_from(self.highres_camera, to=self.display)
                    self.display.show_image_highres(self.high_res_buffer)
                    custody.switch_from(self.display, to=None)
                else:
                    custody.switch_from(self.highres_camera, to=None)

                if self.num_frames == 100:
                    time_elapsed = time.perf_counter() - self.initial_time
                    print("%0.2f average FPS" % (self.num_frames / time_elapsed))
                    self.num_frames = 0
                    self.initial_time = time.perf_counter()

            #end preview by setting voltages back to zero
            end_unit = np.zeros((100, NI_board_parameters.ao_nchannels), np.dtype(np.float64))
            self.ao.play_voltages(voltages=end_unit, block=True, force_final_zeros=False)

            self.highres_camera.end_preview()

        #parameters for preview
        self.continue_preview_highres = True

        #start preview custody thread
        th = ct.CustodyThread(target=preview_highresASLM_task, first_resource=self.highres_camera)
        th.start()
        return th

    def stack_acquisition_master(self, current_folder, current_startposition, whichlaser, resolutionmode):
        """
        Master to start stack acquisitions of different channels and resolution modes. Decides which stack acquisition method to call
        :param current_folder: folder to save the acquired data
        :param current_startposition: start position for the stack streaming
        :param whichlaser: which channels to image
        :return:
        """
        if whichlaser[0]==1:
            print("acquire 488 laser")
            # filepath
            current_filepath = os.path.join(current_folder, "1_CH00_000000.tif")
            if resolutionmode == "low":
                self.acquire_stack_lowres(current_startposition, NI_board_parameters.laser488, current_filepath)
            if resolutionmode == "highASLM":
                print("acquire highALSM")
            if resolutionmode == "highSPIM":
                print("acquire highSPIM")
                self.acquire_stack_highres(current_startposition, NI_board_parameters.laser488, current_filepath)


        if whichlaser[1]==1:
            print("acquire 552 laser")
            current_filepath = os.path.join(current_folder, "1_CH01_000000.tif")
            if resolutionmode == "low":
                self.acquire_stack_lowres(current_startposition, NI_board_parameters.laser552,
                                            current_filepath)
            if resolutionmode == "highASLM":
                print("acquire highALSM")
            if resolutionmode == "highSPIM":
                print("acquire highSPIM")
                self.acquire_stack_highres(current_startposition, NI_board_parameters.laser552, current_filepath)


        if whichlaser[2]==1:
            print("acquire 594 laser")
            current_filepath = os.path.join(current_folder, "1_CH02_000000.tif")
            if resolutionmode == "low":
                self.acquire_stack_lowres(current_startposition, NI_board_parameters.laser594,
                                            current_filepath)
            if resolutionmode == "highASLM":
                print("acquire highALSM")
            if resolutionmode == "highSPIM":
                print("acquire highSPIM")
                self.acquire_stack_highres(current_startposition, NI_board_parameters.laser594, current_filepath)

        if whichlaser[3]==1:
            print("acquire 640 laser")
            current_filepath = os.path.join(current_folder, "1_CH03_000000.tif")
            if resolutionmode == "low":
                self.acquire_stack_lowres(current_startposition, NI_board_parameters.laser640,
                                            current_filepath)
            if resolutionmode == "highASLM":
                print("acquire highALSM")
            if resolutionmode == "highSPIM":
                print("acquire highSPIM")
                self.acquire_stack_highres(current_startposition, NI_board_parameters.laser640, current_filepath)


    def prepare_acquisition(self, current_startposition, laser):
        """
        prepare acquisition by moving filter wheel and stage system to right position
        """
        def movestage():
            self.move_to_position(current_startposition)
        thread_stagemove = ct.ResultThread(target=movestage).start()

        if laser == NI_board_parameters.laser488:
            self.filterwheel.set_filter('515-30-25', wait_until_done=False)
        if laser == NI_board_parameters.laser552:
            self.filterwheel.set_filter('572/20-25', wait_until_done=False)
        if laser == NI_board_parameters.laser594:
            self.filterwheel.set_filter('615/20-25', wait_until_done=False)
        if laser == NI_board_parameters.laser640:
            self.filterwheel.set_filter('676/37-25', wait_until_done=False)

        thread_stagemove.get_result()

    def acquire_stack_lowres(self, current_startposition, current_laserline, filepath):
        def acquire_task(custody):

            custody.switch_from(None, to=self.lowres_camera)

            #prepare acquisition by moving filter wheel etc
            self.prepare_acquisition(current_startposition, current_laserline)


            # the camera needs time to read out the pixels - this is the camera readout time, and it adds to the
            # exposure time, depending on the number of rows that are imaged
            nb_rows = 2960
            # nb_rows = 2480
            readout_time = nb_rows * Camera_parameters.lowres_line_digitization_time

            #prepare voltage array
            # calculate minimal unit duration and set up array
            minimal_trigger_timeinterval = self.exposure_time_LR / 1000 + readout_time / 1000 + self.delay_cameratrigger
            basic_unit = np.zeros((self.ao.s2p(minimal_trigger_timeinterval), NI_board_parameters.ao_nchannels), np.dtype(np.float64))

            #set voltages in array - camera, stage, remote mirror, laser
            basic_unit[self.ao.s2p(self.delay_cameratrigger):self.ao.s2p(self.delay_cameratrigger + 0.002), 1] = 4.  # camera - ao5
            basic_unit[0:self.ao.s2p(0.002), 2] = 4.  # stage
            basic_unit[self.ao.s2p(self.delay_cameratrigger):self.ao.s2p(self.exposure_time_LR / 1000), current_laserline] = 4. #laser
            basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_staticLowResVolt #remote mirror

            control_array = np.tile(basic_unit, (self.stack_nbplanes_lowres + 1, 1))  # add +1 as you want to return to origin position

            #write voltages
            write_voltages_thread = ct.ResultThread(target=self.ao._write_voltages, args=(control_array,),
                                            ).start()

            #data allocation correct
            low_res_buffer = ct.SharedNDArray(
                 shape=(self.stack_nbplanes_lowres, self.current_lowresROI_height, self.current_lowresROI_width),
                 dtype='uint16')
            #low_res_buffer.fill(0)

            #set up stage
            self.XYZ_stage.streamStackAcquisition_externalTrigger_setup(self.stack_nbplanes_lowres, self.lowres_planespacing)

            # prepare camera for stack acquisition
            self.lowres_camera.prepare_stack_acquisition(self.exposure_time_LR)

            # start thread on stage to wait for trigger
            def start_stage_stream():
                self.XYZ_stage.streamStackAcquisition_externalTrigger_waitEnd()
            stream_thread = ct.ResultThread(target=start_stage_stream).start()  # ~3.6s

            def start_camera_stream():
                self.lowres_camera.run_stack_acquisition_buffer(self.stack_nbplanes_lowres, low_res_buffer)
            camera_stream_thread = ct.ResultThread(target=start_camera_stream).start()

            # play voltages
            # you need to use "block true" as otherwise the program finishes without playing the voltages really
            self.ao.play_voltages(block=True)
            stream_thread.get_result()
            camera_stream_thread.get_result()

            custody.switch_from(self.lowres_camera, to=self.display)

            def saveimage():
                # save image
                try:
                    imwrite(filepath, low_res_buffer) #can a thread change self.filepath ? Can someone change stack_buffer?
                except:
                    print("couldn't save image")
            savethread = ct.ResultThread(target=saveimage).start()

            self.display.show_stack(low_res_buffer)

            custody.switch_from(self.display, to=None)
            savethread.get_result()

        acquire_thread = ct.CustodyThread(
            target=acquire_task, first_resource=self.lowres_camera).start()
        acquire_thread.get_result()

    def acquire_stack_highres(self, current_startposition, current_laserline, filepath):
        def acquire_taskHighResSPIM(custody):

            custody.switch_from(None, to=self.highres_camera)

            # prepare acquisition by moving filter wheel etc
            self.prepare_acquisition(current_startposition, current_laserline)

            # the camera needs time to read out the pixels - this is the camera readout time, and it adds to the
            # exposure time, depending on the number of rows that are imaged
            nb_rows = 2480
            readout_time = nb_rows * Camera_parameters.highres_line_digitization_time

            # prepare voltage array
            # calculate minimal unit duration and set up array
            minimal_trigger_timeinterval = self.exposure_time_HR / 1000 + readout_time / 1000 + self.delay_cameratrigger
            basic_unit = np.zeros((self.ao.s2p(minimal_trigger_timeinterval), NI_board_parameters.ao_nchannels), np.dtype(np.float64))

            #set voltages in array - camera, stage, remote mirror, laser
            basic_unit[self.ao.s2p(self.delay_cameratrigger):self.ao.s2p(self.delay_cameratrigger + 0.002), 0] = 4.  # highrescamera - ao0
            basic_unit[0:self.ao.s2p(0.002), 2] = 4.  # stage
            basic_unit[:, NI_board_parameters.voicecoil] = self.ASLM_staticHighResVolt #remote mirror
            basic_unit[self.ao.s2p(self.delay_cameratrigger):self.ao.s2p(self.exposure_time_HR / 1000), current_laserline] = 4. #laser

            control_array = np.tile(basic_unit,
                                    (self.stack_nbplanes_highres + 1, 1))  # add +1 as you want to return to origin position

            # write voltages
            write_voltages_thread = ct.ResultThread(target=self.ao._write_voltages, args=(control_array,),
                                                    ).start()

            # data allocation correct
            highres_buffer = ct.SharedNDArray(
                shape=(self.stack_nbplanes_highres, self.current_highresROI_height, self.current_highresROI_width), dtype='uint16')

            # set up stage
            self.XYZ_stage.streamStackAcquisition_externalTrigger_setup(self.stack_nbplanes_highres, self.highres_planespacing)

            # prepare high res camera for stack acquisition
            self.highres_camera.prepare_stack_acquisition(self.exposure_time_HR)

            # start thread on stage to wait for trigger
            def start_stage_streamHighResSPIM():
                self.XYZ_stage.streamStackAcquisition_externalTrigger_waitEnd()
            stream_thread = ct.ResultThread(target=start_stage_streamHighResSPIM).start()  # ~3.6s

            #start thread so that camera waits for trigger
            def start_camera_streamHighResSPIM():
                self.highres_camera.run_stack_acquisition_buffer(self.stack_nbplanes_highres, highres_buffer)
            camera_stream_thread = ct.ResultThread(target=start_camera_streamHighResSPIM).start()

            # play voltages
            # you need to use "block true" as otherwise the program finishes without playing the voltages really
            self.ao.play_voltages(block=True)
            stream_thread.get_result()
            camera_stream_thread.get_result()

            custody.switch_from(self.highres_camera, to=self.display)

            def saveimage_highresSPIM():
                # save image
                try:
                    imwrite(filepath, highres_buffer)
                except:
                    print("couldn't save image")
            savethread = ct.ResultThread(target=saveimage_highresSPIM).start()

            self.display.show_stack(highres_buffer)

            custody.switch_from(self.display, to=None)
            savethread.get_result()

        #start thread and wait for its completion
        acquire_threadHighResSPIM = ct.CustodyThread(
            target=acquire_taskHighResSPIM, first_resource=self.highres_camera).start()
        acquire_threadHighResSPIM.get_result()

    def smooth_sawtooth(self, array, window_len = 101):

        if (window_len % 2) == 0:
            window_len = window_len + 1
        startwindow = int((window_len - 1) / 2)

        startarray = np.ones(startwindow) * array[0]
        endarray = np.ones(startwindow) * array[-1]

        s = np.r_[startarray, array, endarray] #make array bigger on both sides

        w = np.ones(window_len, 'd') #define a flat window - all values have equal weight

        returnarray = np.convolve(w / w.sum(), s, mode='valid') #convolve with window to smooth

        return returnarray

if __name__ == '__main__':
    # first code to run in the multiscope

    # Create scope object:
    scope = multiScopeModel()


    # snap_threads = []
    # for i in range(150):
    #     th = scope.snap()
    #     snap_threads.append(th)
    # print(len(snap_threads), "'snap' threads launched.")
    # for th in snap_threads:
    #     th.get_result()

    # th = scope.preview_lowres()
    # print("All 'snap' threads finished execution.")
    # input('Hit enter to close napari...')
    # scope.continue_preview_lowres = False
    # th.get_result()
    #
    # scope.preview_highres()
    # print("All 'snap' threads finished execution.")
    # input('Hit enter to close napari...')
    # scope.continue_preview_highres = False

    #close
    scope.close()
