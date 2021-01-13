import queue
import time
import os
import atexit
import threading
import auxiliary_code.proxy_objects as proxy_objects
from auxiliary_code.proxied_napari import display
import src.camera.Photometrics_camera as Photometricscamera



class _Camera:
    def record(self, out):
        import numpy as np
        out[:] = np.random.randint(
            0, 2**16, size=out.shape, dtype='uint16')


class multiScope:
    def __init__(
        self,
        bytes_per_data_buffer,
        num_data_buffers,
        bytes_per_preview_buffer,
        ):
        """
        We use bytes_per_buffer to specify the shared_memory_sizes for the
        child processes.
        """
        self._init_shared_memory(
            bytes_per_data_buffer, num_data_buffers, bytes_per_preview_buffer)
        self.unfinished_tasks = queue.Queue()

        #start initializing all hardware component here by calling the initialization from a thread
        lowres_camera_init = threading.Thread(target=self._init_lowres_camera) #~3.6s

        lowres_camera_init.start()
        #self._init_display() #~1.3s

        lowres_camera_init.join()

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
        print("Initializing camera..")
        self.camera = self.pm.proxy_object(Photometricscamera.Photo_Camera)
        #self.camera = self.pm.proxy_object(_Camera)

        self.camera.take_snapshot(20)
        #self.camera.apply_settings(trigger='external_trigger')
        print("done with camera.")

    def _init_display(self):
        print("Initializing display...")
        self.display = display(proxy_manager=self.pm)
        print("done with display.")


    def quit(self):
        self.camera.close()
        self.display.close() # more work needed here
        print('Quit Snoutscope')

    def close(self):
        self.finish_all_tasks()
        self.quit()
        print('Closed Snoutscope')

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

    # Acquisition:
    vol_per_buffer = 1
    num_data_buffers = 2  # increase for multiprocessing
    num_snap = 1  # interbuffer time limited by ao play

    images_per_buffer = 1
    bytes_per_data_buffer = images_per_buffer * 6000 * 4000 * 2


    bytes_per_preview_buffer = bytes_per_data_buffer *3

    # Create scope object:
    scope = multiScope(bytes_per_data_buffer, num_data_buffers, bytes_per_preview_buffer)
    scope.close()
