import queue
import time
import os
import atexit
import threading

import auxiliary_code.concurrency_tools as ct
import auxiliary_code.napari_in_subprocess as napari

import src.camera.Photometrics_camera as Photometricscamera
import src.ni_board.ni as ni
import src.stages.rotation_stage_cmd as RotStage
import src.stages.translation_stage_cmd as TransStage
import src.filter_wheel.ludlcontrol as FilterWheel
from constants import FilterWheel_parameters
from constants import Stage_parameters
from constants import NI_board_parameters
from constants import SharedMemory_allocation
from constants import Camera_parameters

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
            ct.SharedNDArray(shape=(1, 2048, 2048), dtype='uint16')
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
        self.continue_preview = True

        #preview buffers
        self.low_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel), dtype='uint16')
        self.high_res_buffer = ct.SharedNDArray(shape=(Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel), dtype='uint16')
        self.low_res_buffer.fill(0) #fill to initialize
        self.high_res_buffer.fill(0) #fill to initialize

        #start initializing all hardware component here by calling the initialization from a ResultThread
        lowres_camera_init = ct.ResultThread(target=self._init_lowres_camera).start() #~3.6s
        #highres_camera_init = ct.ResultThread(target=self._init_highres_camera).start() #~3.6s
        self._init_display() #~1.3s


        #initialize stages and stages in ResultThreads
        #trans_stage_init = ct.ResultThread(target=self._init_XYZ_stage).start() #~0.4s
        #rot_stage_init = ct.ResultThread(target=self._init_rotation_stage).start()
        #filterwheel_init = ct.ResultThread(target=self._init_filterwheel).start()  # ~5.3s


        #self._init_ao()  # ~0.2s


        #wait for all started initialization threads before continuing (by calling thread join)
        lowres_camera_init.get_result()
        #highres_camera_init.get_result()
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
        self.display = ct.ObjectInSubprocess(napari._NapariDisplay, custom_loop= napari._napari_child_loop, close_method_name='close')

        print("done with display.")

    def _init_ao(self):
        """
        Initialize National Instruments card 6378 as device 1, Dev1
        """
        self.names_to_voltage_channels = NI_board_parameters.names_to_voltage_channels
        print("Initializing ao card...", end=' ')
        self.ao = ni.Analog_Out(num_channels=30,
                                rate=1e5,
                                daq_type='6738',
                                board_name='Dev1',
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
        custody.switch_from(None, to=self.highres_camera)
        which_buffer = self.data_buffer_queue.get()
        data_buffer = self.data_buffers[which_buffer]
        self.highres_camera.record(out=data_buffer)
        custody.switch_from(self.highres_camera, to=self.display)
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
        th = ct.CustodyThread(first_resource=self.highres_camera, target=self.snap_task)
        return th.start()

    def preview_lowres(self):

        def preview_lowres_task(custody):
            self.lowres_camera.set_up_preview(self.exposure_time)
            self.num_frames = 0
            self.initial_time = time.perf_counter()

            while self.continue_preview:

                custody.switch_from(None, to=self.lowres_camera)
                self.lowres_camera.run_preview(out=self.low_res_buffer)
                custody.switch_from(self.lowres_camera, to=self.display)
                self.display.show_image(self.low_res_buffer)
                custody.switch_from(self.display, to=None)
                self.num_frames += 1

                #calculate fps to display
                if self.num_frames == 100:
                    time_elapsed = time.perf_counter() - self.initial_time
                    print("%0.2f average FPS" % (self.num_frames / time_elapsed))
                    self.num_frames = 0
                    self.initial_time = time.perf_counter()

            self.lowres_camera.end_preview()

        self.continue_preview = True
        th = ct.CustodyThread(target=preview_lowres_task, first_resource=None)
        th.start()

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
    scope.preview_lowres()
    print("All 'snap' threads finished execution.")
    input('Hit enter to close napari...')
    scope.continue_preview = False

    #close
    scope.close()
