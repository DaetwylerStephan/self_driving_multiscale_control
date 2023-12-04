
import concurrency_tools as ct
import numpy as np
import time

from pyvcam.camera import Camera
from napari_in_subprocess import display

import src.camera.Photometrics_camera as Photometricscamera
import src.ni_board.vni as ni


if __name__ == '__main__': #needed for threading of napari in subprocess

    #settings
    exposuretime = 20
    out = np.ndarray(shape=(2048, 2048), dtype='uint16')
    out.fill(0)
    frames_unit = 10

    #camera init
    camera = Photometricscamera.Photo_Camera('PMUSBCam00')
    camera.prepare_stack_acquisition(exposuretime)
    #display init
    testdisplay = display()

    #ni board for trigger - init

    ao = ni.Analog_Out(
        num_channels=3,
        rate=2e4,
        daq_type='6738',
        line="Dev1/ao5, Dev1/ao8, Dev1/ao12",
        verbose=True)

    basic_unit = np.zeros((ao.s2p(exposuretime/1000 + 0.01), 3), np.dtype(np.float64))
    basic_unit[0:ao.s2p(0.002), 0] = 4
    control_array = np.tile(basic_unit, (frames_unit, 1))


    runit=0
    while runit==0:
        ao._write_voltages(control_array)
        ao.play_voltages(block=False)
        framesReceived = 0

        while framesReceived < frames_unit:
            time.sleep(0.004)

            try:
                fps, frame_count = camera.cam.poll_frame2(out=out)

                framesReceived += 1
                if framesReceived%2==0:
                    testdisplay.show_image(out)


                print(framesReceived)
            except Exception as e:
                print(str(e))
                runit =1
                break


    camera.finish()

