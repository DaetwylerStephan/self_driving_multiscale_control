import src.ni_board.vni as ni
import numpy as np

from constants import Stage_parameters
from constants import Camera_parameters

import src.stages.translation_stage_cmd as TransStage
import auxiliary_code.concurrency_tools as ct
import time
from pyvcam.camera import Camera
from napari_in_subprocess import display

import src.camera.Photometrics_camera as Photometricscamera
if __name__ == '__main__': #needed for threading of napari in subprocess
    # ni board for trigger - init

    # settings
    exposuretime = 20
    frames_unit = 100

    #initialize array
    ao = ni.Analog_Out(
        num_channels=4,
        rate=2e4,
        daq_type='6738',
        line="Dev1/ao0, Dev1/ao5, Dev1/ao8, Dev1/ao12",
        verbose=True)

    delay_cameratrigger = 0.001
    basic_unit = np.zeros((ao.s2p(exposuretime/1000 + delay_cameratrigger+0.001), 4), np.dtype(np.float64))
    basic_unit[ao.s2p(delay_cameratrigger):ao.s2p(delay_cameratrigger+0.002), 0] = 4. #camera - ao0
    basic_unit[0:ao.s2p(0.002), 1] = 4. #stage

    control_array = np.tile(basic_unit, (frames_unit+1, 1)) #add +1 as you want to return to origin position

    ####################------handled by init at beginning
    # camera init
    camera = Photometricscamera.Photo_Camera('PMPCIECam00')
    #init stages
    stage_id = Stage_parameters.stage_id_XYZ
    XYZ_stage = TransStage.SLC_translationstage(stage_id)
    XYZ_stage.findReference()
    print("done with XYZ stage.")
    # display init
    #testdisplay = display()
    ####################

    #init memory
    # low_res_buffer = ct.SharedNDArray(shape=(frames_unit, Camera_parameters.LR_height_pixel, Camera_parameters.LR_width_pixel),
    #                                        dtype='uint16')
    # low_res_buffer.fill(0)

    #position_list = [1000000000, 2000000000, 8000000000]
    #XYZ_stage.moveToPosition(position_list)

    #prepare stage for stack acquisition
    XYZ_stage.streamStackAcquisition_externalTrigger_setup(frames_unit, 3000000)

    #prepare camera for stack acquisition
    camera.prepare_stack_acquisition(exposuretime)


    #start thread on stage to wait for trigger
    def start_stage_stream():
        XYZ_stage.streamStackAcquisition_externalTrigger_waitEnd()
    stream_thread = ct.ResultThread(target=start_stage_stream).start()  # ~3.6s

    def start_camera_stream():
        runit = 0
        while runit == 0:
            framesReceived = 0
            while framesReceived < frames_unit:
                time.sleep(0.004)

                try:
                    #fps, frame_count = camera.cam.poll_frame2(out=low_res_buffer[framesReceived,:,:])
                    framesReceived += 1
                    print(framesReceived)
                except Exception as e:
                    print(str(e))
                    runit = 1
                    break

    #camera_stream_thread = ct.ResultThread(target=start_camera_stream).start()

    #init voltage - write them
    print("test")
    ao._write_voltages(control_array)


    #play voltages
    #you need to use "block true" as otherwise the program finishes without playing the voltages really
    ao.play_voltages(block=True)
    stream_thread.get_result()
    #camera_stream_thread.get_result()

    #testdisplay.show_image(low_res_buffer)
    input("press enter to finish")
    print("done playing")

