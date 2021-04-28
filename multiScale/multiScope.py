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
from constants import FilterWheel_parameters
from constants import Stage_parameters
from constants import NI_board_parameters
from constants import Camera_parameters
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
        self.exposure_time = 20
        self.continue_preview_lowres = False
        self.continue_preview_highres = False
        self.stack_nbplanes =0
        self.stack_buffer = ct.SharedNDArray(shape=(200, 2000, 2000), dtype='uint16')
        self.stack_buffer.fill(0)
        self.filepath = 'D:/acquisitions/testimage.tif'

        #preview buffers
        self.low_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.high_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel), dtype='uint16')
        self.low_res_buffer.fill(0) #fill to initialize
        self.high_res_buffer.fill(0) #fill to initialize

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
        #trans_stage_init = ct.ResultThread(target=self._init_XYZ_stage).start() #~0.4s
        #rot_stage_init = ct.ResultThread(target=self._init_rotation_stage).start()
        #filterwheel_init = ct.ResultThread(target=self._init_filterwheel).start()  # ~5.3s


        self._init_ao()  # ~0.2s


        #wait for all started initialization threads before continuing (by calling thread join)
        lowres_camera_init.get_result()
        highres_camera_init.get_result()
        # filterwheel_init.get_result()
        # trans_stage_init.get_result()
        # rot_stage_init.get_result()

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
        #self.display = ct.ObjectInSubprocess(napari._NapariDisplay, custom_loop= napari._napari_child_loop, close_method_name='close')

        print("done with display.")

    def _init_ao(self):
        """
        Initialize National Instruments card 6378 as device 1, Dev1
        """
        self.names_to_voltage_channels = NI_board_parameters.names_to_voltage_channels
        print("Initializing ao card...", end=' ')

        #"ao0/stage", "ao5/camera", "ao6/remote mirror", "ao8/laser", "ao11", "ao14", "ao18"
        line_selection = "Dev1/ao0, Dev1/ao5, Dev1/ao6, Dev1/ao8, Dev1/ao11, Dev1/ao14, Dev1/ao18"
        ao_type = '6738'
        ao_nchannels = 7
        rate = 2e4

        self.ao = ni.Analog_Out(
            num_channels=ao_nchannels,
            rate=rate,
            daq_type=ao_type,
            line=line_selection,
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
        self.rotationstage.ManualMove()
        print("done with XY stage.")
        atexit.register(self.rotationstage.close)

    def close(self):
        """
        Close all opened channels, camera etc
                """
        self.finish_all_tasks()
        self.lowres_camera.close()
        self.highres_camera.close()
        self.ao.close()
        #self.rotationstage.close()
        #self.XYZ_stage.close()
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

    def snap_task(self, custody):
        custody.switch_from(None, to=self.lowres_camera)
        which_buffer = self.data_buffer_queue.get()
        data_buffer = self.data_buffers[which_buffer]
        self.lowres_camera.record(out=data_buffer)
        custody.switch_from(self.lowres_camera, to=self.display)
        self.display.show_image(data_buffer)
        custody.switch_from(self.display, to=None)
        self.data_buffer_queue.put(which_buffer)
        self.num_frames += 1
        if self.num_frames == 100:
            time_elapsed = time.perf_counter() - self.initial_time
            print("%0.2f average FPS" % (self.num_frames / time_elapsed))
            self.num_frames = 0
            self.initial_time = time.perf_counter()

    def snap(self):
        th = ct.CustodyThread(first_resource=self.lowres_camera, target=self.snap_task)
        return th.start()

    def preview_lowres(self):
        def preview_lowres_task(custody):
            self.lowres_camera.set_up_preview(self.exposure_time)
            self.num_frames = 0
            self.initial_time = time.perf_counter()

            while self.continue_preview_lowres:
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

    def preview_highres(self):
        def preview_highres_task(custody):
            self.highres_camera.set_up_preview(self.exposure_time)
            self.num_frames = 0
            self.initial_time = time.perf_counter()

            while self.continue_preview_highres:
                custody.switch_from(None, to=self.highres_camera)
                which_buffer = self.high_res_buffers_queue.get()
                data_buffer = self.high_res_buffers[which_buffer]
                self.highres_camera.run_preview(out=data_buffer)
                custody.switch_from(self.highres_camera, to=self.display)
                self.display.show_image_highres(data_buffer)
                custody.switch_from(self.display, to=None)
                self.high_res_buffers_queue.put(which_buffer)
                self.num_frames += 1
                #calculate fps to display
                if self.num_frames == 100:
                    time_elapsed = time.perf_counter() - self.initial_time
                    print("%0.2f average FPS" % (self.num_frames / time_elapsed))
                    self.num_frames = 0
                    self.initial_time = time.perf_counter()

            self.highres_camera.end_preview()

        self.continue_preview_highres = True
        th = ct.CustodyThread(target=preview_highres_task, first_resource=self.highres_camera)
        th.start()
        return th

    def acquire_stack_lowres(self):

        # move stage to start position
        # choose right filter wheel position
        # set remote mirror to right position
        # set flip mirror to right position
        def acquire_task(custody):
            #prepare camera for stack acquisition
            self.lowres_camera.prepare_stack_acquisition()

            #prepare voltage array
            basic_unit = self.ao.get_voltage_array()
            control_array = np.tile(basic_unit, (self.stack_nbplanes, 1))

            print(print(control_array[1:10,:]))

            custody.switch_from(None, to=self.lowres_camera)


            #play voltage
            #voltagethread = ct.ResultThread(target = self.ao.play_voltages,
            #    args=(control_array,), kwargs={'force_final_zeros': True, 'block': False}).start()
            write_voltages_thread = ct.ResultThread(target=self.ao._write_voltages,
                                            args=(control_array,),
                                            ).start()

            # set up camera for acquisition
            # camera_thread = ct.ResultThread(target=self.lowres_camera.run_stack_aquisition_buffer,
            #     args=(self.stack_nbplanes, self.stack_buffer,)).start()

            camera_thread = ct.ResultThread(target=self.lowres_camera.run_stack_acquisition_buffer,
                                            kwargs={'nb_planes': self.stack_nbplanes, 'out': self.stack_buffer}).start()

            write_voltages_thread.get_result()
            print("Ready to play voltages")
            self.ao.play_voltages(block=False)

            custody.switch_from(self.lowres_camera, to=None)
            # save image
            try:
                imwrite(self.filepath, self.stack_buffer)
            except:
                print("couldn't save image")

            custody.switch_from(None, to=self.display)
            self.display.show_stack(self.stack_buffer)
            custody.switch_from(self.display, to=None)

        acquire_thread = ct.CustodyThread(
            target=acquire_task, first_resource=self.lowres_camera).start()





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
