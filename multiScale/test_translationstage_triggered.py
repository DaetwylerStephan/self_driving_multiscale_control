import src.ni_board.vni as ni
import numpy as np
from constants import Stage_parameters
import src.stages.translation_stage_cmd as TransStage
import auxiliary_code.concurrency_tools as ct
import time

if __name__ == '__main__': #needed for threading of napari in subprocess
    # ni board for trigger - init

    # settings
    exposuretime = 20
    frames_unit = 1000

    #initialize array
    ao = ni.Analog_Out(
        num_channels=3,
        rate=2e4,
        daq_type='6738',
        line="Dev1/ao5, Dev1/ao8, Dev1/ao12",
        verbose=True)

    basic_unit = np.zeros((ao.s2p(0.02 + 0.001), 3), np.dtype(np.float64))
    basic_unit[0:ao.s2p(0.002), 0] = 4.
    control_array = np.tile(basic_unit, (frames_unit+1, 1)) #add +1 as you want to return to origin position


    #init stages
    stage_id = Stage_parameters.stage_id_XYZ
    XYZ_stage = TransStage.SLC_translationstage(stage_id)
    XYZ_stage.findReference()
    print("done with XYZ stage.")

    #position_list = [1000000000, 2000000000, 8000000000]
    #XYZ_stage.moveToPosition(position_list)
    XYZ_stage.streamStackAcquisition_externalTrigger_setup(frames_unit, 10000000)


    def start_stream():
        XYZ_stage.streamStackAcquisition_externalTrigger_waitEnd()
    stream_thread = ct.ResultThread(target=start_stream).start()  # ~3.6s

    print("test")
    #you need to use "block true" as otherwise the program finishes without playing the voltages really
    ao._write_voltages(control_array)
    ao.play_voltages(block=True)
    stream_thread.get_result()

    #time.sleep(5)
    print("done playing")

