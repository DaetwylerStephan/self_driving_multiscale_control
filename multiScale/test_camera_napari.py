
import concurrency_tools as ct
import numpy as np
import cv2
import msvcrt

from pyvcam.camera import Camera
from napari_in_subprocess import display

import src.camera.Photometrics_camera as Photometricscamera

from constants import NI_board_parameters
import src.ni_board.vni as ni

if __name__ == '__main__': #needed for threading of napari in subprocess

    #init
    camera = Photometricscamera.Photo_Camera('PMUSBCam00')
    testdisplay = display()
    out = np.ndarray(shape=(2048, 2048), dtype='uint16')

    ao = ni.Analog_Out(
        num_channels=NI_board_parameters.ao_nchannels,
        rate=NI_board_parameters.rate,
        daq_type=NI_board_parameters.ao_type,
        line=NI_board_parameters.line_selection,
        verbose=True)

    #laser power
    ao_laser488_power = ni.Analog_Out(
        daq_type=NI_board_parameters.ao_type_constant,
        line=NI_board_parameters.power_488_line,
        minVol=NI_board_parameters.minVol_constant,
        maxVol=NI_board_parameters.maxVol_constant,
        verbose=True)
    ao_laser488_power.setconstantvoltage(3)

    # generate array
    basic_unit = np.zeros(
        (ao.s2p(312/1000 + 0.02), NI_board_parameters.ao_nchannels),
        np.dtype(np.float64))
    basic_unit[:, 3] = 4 #488 nm laser
    basic_unit[ao.s2p(0):ao.s2p(0.002), 0] = 4.  # high-res camera


    camera.set_up_preview(exposure=20)

    while True:

        # write voltages
        write_voltages_thread = ct.ResultThread(target=ao._write_voltages, args=(basic_unit,),
                                                ).start()


        camera.run_preview(out)

        # play voltages
        ao.play_voltages(block=True)

        testdisplay.show_image(out)

        #frame['pixel_data'] = cv2.resize(frame['pixel_data'], dim, interpolation=cv2.INTER_AREA)
        #cv2.imshow('Live Mode', frame['pixel_data'])


        if msvcrt.kbhit():
            break