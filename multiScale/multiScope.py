import queue
import time
import os
import atexit
import threading



import auxiliary_code.proxy_objects as proxy_objects
from auxiliary_code.proxied_napari import display
import src.camera.Photometrics_camera as Photometricscamera
import src.ni_board.ni as ni
import src.stages.rotation_stage_cmd as RotStage
import src.stages.translation_stage_cmd as TransStage
import src.filter_wheel.ludlcontrol as FilterWheel
from constants import FilterWheel_parameters
from constants import Stage_parameters
from constants import NI_board_parameters
from constants import SharedMemory_allocation

class multiScopeModel:
    def __init__(
        self
        ):
        """
        We use bytes_per_buffer to specify the shared_memory_sizes for the
        child processes.
        """
        self._init_shared_memory(
            SharedMemory_allocation.bytes_per_data_buffer, SharedMemory_allocation.num_data_buffers, SharedMemory_allocation.bytes_per_preview_buffer)
        self.unfinished_tasks = queue.Queue()

        #start initializing all hardware component here by calling the initialization from a thread
        lowres_camera_init = threading.Thread(target=self._init_lowres_camera) #~3.6s
        lowres_camera_init.start()

        #initialize stages in threads
        #trans_stage_init = threading.Thread(target=self._init_XYZ_stage) #~0.4s
        #trans_stage_init.start()
        #rot_stage_init = threading.Thread(target=self._init_rotation_stage)
        #rot_stage_init.start()


        #self.display = display(proxy_manager=self.pm)
        #self._init_ao()  # ~0.2s
        self._init_filterwheel()  # ~0.2s

        #wait for all started initialization threads before continuing (by calling thread join)
        lowres_camera_init.join()
        #trans_stage_init.join()
        #rot_stage_init.join()

        print('Finished initializing multiScope')


    def _init_shared_memory(
        self,
        bytes_per_data_buffer,
        num_data_buffers,
        bytes_per_preview_buffer,
        ):
        """
        Each buffer is acquired in deterministic time with a single play
        of the ao card.
        """
        num_preview_buffers = 3 # 3 for preprocess, display and filesave
        assert bytes_per_data_buffer > 0 and num_data_buffers > 0
        assert bytes_per_preview_buffer > 0
        print("Allocating shared memory...", end=' ')
        self.pm = proxy_objects.ProxyManager(shared_memory_sizes=(
            (bytes_per_data_buffer,   ) * num_data_buffers +
            (bytes_per_preview_buffer,) * num_preview_buffers))
        print("done allocating memory.")
        self.data_buffer_queue = queue.Queue(maxsize=num_data_buffers)
        for i in range(num_data_buffers):
            self.data_buffer_queue.put(i)
        self.preview_buffer_queue = queue.Queue(maxsize=num_preview_buffers)
        for i in range(num_preview_buffers):
            self.preview_buffer_queue.put(i + num_data_buffers) # pointer math!

    def _init_lowres_camera(self):
        """
        Initialize low resolution camera
        """
        print("Initializing camera..")
        #place the Photometrics class as object into a proxy object
        self.lowres_camera = self.pm.proxy_object(Photometricscamera.Photo_Camera)
        self.lowres_camera.take_snapshot(20)
        print("done with camera.")

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



if __name__ == '__main__':
    # first code to run in the multiscope

    # Create scope object:
    scope = multiScope()

    #close
    scope.close()
