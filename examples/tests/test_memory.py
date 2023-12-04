import auxiliary_code.concurrency_tools as ct
from constants import Camera_parameters
import queue
import time
import numpy as np


class testmicroscope:
    def __init__(
            self
    ):
        self.high_res_buffers = [
            ct.SharedNDArray(shape=(Camera_parameters.HR_height_pixel, Camera_parameters.HR_width_pixel),
                             dtype='uint16')
            for i in range(2)]

        self.low_res_buffers = [
            ct.SharedNDArray(shape=(Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel),
                             dtype='uint16')
            for i in range(2)]

        self.high_res_buffers_queue = queue.Queue()
        self.low_res_buffers_queue = queue.Queue()
        for i in range(2):
            self.high_res_buffers_queue.put(i)
            self.low_res_buffers_queue.put(i)

    def runmicroscope(self, i):
        ##navigate buffer queue - where to save current image.
        current_bufferiter = self.low_res_buffers_queue.get()  # get current buffer iter
        self.low_res_buffers_queue.put(current_bufferiter)  # add number to end of queue
        print("------------------------------------------------------------")
        print(current_bufferiter)
        print("------------------------------------------------------------")

        low_res_buffer = ct.SharedNDArray(
            shape=(i, 2000, 2000),
            dtype='uint16')
        low_res_buffer.fill(0)
        self.low_res_buffers[current_bufferiter] = low_res_buffer

        def calculate_projection():
            # calculate projections
            t0 = time.perf_counter()
            maxproj_xy = np.max(self.low_res_buffers[current_bufferiter], axis=0)


        projection_thread = ct.ResultThread(target=calculate_projection).start()
        time.sleep(5)

if __name__ == '__main__':
    # first code to run the test

    new_mic = testmicroscope()

    for x in range(100):
        new_mic.runmicroscope(x+200)
        print(x)


