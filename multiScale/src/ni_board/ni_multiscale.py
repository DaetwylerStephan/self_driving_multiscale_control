import ctypes as C
import numpy as np
"""
TODO: One way or another, make it harder to forget the daq.close()
method, which can cause crazy voltages to persist. _del_? _enter_ and
_exit_? Try to do it better than we are.
Requires nicaiu.dll to be in the same directory, or located in the
os.environ['PATH'] search path.
If you get an error, google for NIDAQmx.h to decypher it.
"""
api = C.cdll.LoadLibrary("nicaiu")

class NIboard_management:
    def __init__(
            self,
            channellist,
    ):











# DLL api management----------------------------------------------------------------------------------------------------

#int32 DAQmxGetExtendedErrorInfo (char errorString[], uInt32 bufferSize);
#Returns dynamic, specific error information. This function is valid only for the last function that failed;
# additional NI-DAQmx calls may invalidate this information.
api.get_error_info = api.DAQmxGetExtendedErrorInfo
api.get_error_info.argtypes = [C.c_char_p, C.c_uint32]

def check_error(error_code):
    if error_code != 0:
        num_bytes = api.get_error_info(None, 0) #if passed in 0 in buffersize, the value returned is the number of bytes
        print("Error message from NI DAQ: (", num_bytes, "bytes )")
        error_buffer = (C.c_char * num_bytes)()
        api.get_error_info(error_buffer, num_bytes)
        print(error_buffer.value.decode('ascii'))
        raise UserWarning(
            "NI DAQ error code: %i; see above for details."%(error_code))
    return error_code

#int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
#Creates a task . If you use this function to create a task, you must use DAQmxClearTask to destroy it.
api.create_task = api.DAQmxCreateTask
api.create_task.argtypes = [C.c_char_p, C.POINTER(C.c_void_p)]
api.create_task.restype = check_error

#int32 DAQmxCreateAOVoltageChan (TaskHandle taskHandle, const char physicalChannel[], const char nameToAssignToChannel[],
# float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
# Creates channel(s) to generate voltage and adds the channel(s) to the task you specify with taskHandle.
api.create_ao_voltage_channel = api.DAQmxCreateAOVoltageChan
api.create_ao_voltage_channel.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_char_p,
    C.c_double,
    C.c_double,
    C.c_int32,
    C.c_char_p]
api.create_ao_voltage_channel.restype = check_error

#int32 DAQmxCreateDOChan (TaskHandle taskHandle, const char lines[], const char nameToAssignToLines[], int32 lineGrouping);
#Creates channel(s) to generate digital signals and adds the channel(s) to the task you specify with taskHandle. You can group
# digital lines into one digital channel or separate them into multiple digital channels. If you specify one or more entire ports
# in lines by using port physical channel names, you cannot separate the ports into multiple channels. To separate ports into multiple
# channels, use this function multiple times with a different port each time.
api.create_do_channel = api.DAQmxCreateDOChan
api.create_do_channel.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_char_p,
    C.c_int32]
api.create_do_channel.restype = check_error

#int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
#Sets the source of the Sample Clock, the rate of the Sample Clock, and the number of samples to acquire or generate.
api.clock_timing = api.DAQmxCfgSampClkTiming
api.clock_timing.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_double,
    C.c_int32,
    C.c_int32,
    C.c_uint64]
api.clock_timing.restype = check_error

#int32 DAQmxWriteAnalogF64 (TaskHandle taskHandle, int32 numSampsPerChan,
# bool32 autoStart, float64 timeout, bool32 dataLayout, float64 writeArray[],
# int32 *sampsPerChanWritten, bool32 *reserved);
#Writes multiple floating-point samples to a task that contains one or more analog output channels.
api.write_voltages = api.DAQmxWriteAnalogF64
api.write_voltages.argtypes = [
    C.c_void_p,
    C.c_int32,
    C.c_uint32, #NI calls this a 'bool32' haha awesome
    C.c_double,
    C.c_uint32,
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=2), #Numpy is awesome.
    C.POINTER(C.c_int32),
    C.POINTER(C.c_uint32)]
api.write_voltages.restype = check_error

#int32 DAQmxWriteAnalogScalarF64 (TaskHandle taskHandle, bool32 autoStart, float64 timeout, float64 value, bool32 *reserved);
#Writes a floating-point sample to a task that contains a single analog output channel.
api.write_scalarvoltages = api.DAQmxWriteAnalogScalarF64
api.write_scalarvoltages.argtypes = [
    C.c_void_p,
    C.c_uint32,
    C.c_double,
    C.c_double,
    C.POINTER(C.c_uint32)]
api.write_scalarvoltages.restype = check_error

#int32 DAQmxWriteDigitalLines (TaskHandle taskHandle, int32 numSampsPerChan, bool32 autoStart, float64 timeout,
# bool32 dataLayout, uInt8 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved);
#Writes multiple samples to each digital line in a task. When you create your write array, each sample per channel
# must contain the number of bytes returned by the DAQmx_Write_DigitalLines_BytesPerChan property.
api.write_digits = api.DAQmxWriteDigitalLines
api.write_digits.argtypes = [
    C.c_void_p,
    C.c_int32,
    C.c_uint32, #NI calls this a 'bool32' haha awesome
    C.c_double,
    C.c_uint32,
    np.ctypeslib.ndpointer(dtype=np.uint8, ndim=2), #Numpy is awesome.
    C.POINTER(C.c_int32),
    C.POINTER(C.c_uint32)]
api.write_digits.restype = check_error


#Transitions the task from the committed state to the running state, which begins measurement or generation. Using this
# function is required for some applications and optional for others. If you do not use this function, a measurement task starts
# automatically when a read operation begins. The autoStart parameter of the NI-DAQmx Write functions determines if a generation
# task starts automatically when you use an NI-DAQmx Write function. If you do not call DAQmxStartTask and DAQmxStopTask when you
# call NI-DAQmx Read functions or NI-DAQmx Write functions multiple times, such as in a loop, the task starts and stops repeatedly.
# Starting and stopping a task repeatedly reduces the performance of the application.
api.start_task = api.DAQmxStartTask
api.start_task.argtypes = [C.c_void_p]
api.start_task.restype = check_error

#int32 DAQmxWaitUntilTaskDone (TaskHandle taskHandle, float64 timeToWait);
#Waits for the measurement or generation to complete. Use this function to ensure that the specified operation is complete before you stop the task.
api.finish_task = api.DAQmxWaitUntilTaskDone
api.finish_task.argtypes = [C.c_void_p, C.c_double]
api.finish_task.restype = check_error

#int32 DAQmxStopTask (TaskHandle taskHandle);
#Stops the task and returns it to the state it was in before you called DAQmxStartTask or called an NI-DAQmx Write function with autoStart set to TRUE.
api.stop_task = api.DAQmxStopTask
api.stop_task.argtypes = [C.c_void_p]
api.stop_task.restype = check_error

#int32 DAQmxClearTask (TaskHandle taskHandle);
#Clears the task. Before clearing, this function aborts the task, if necessary, and releases any resources reserved by the task.
# You cannot use a task once you clear the task without recreating or reloading the task.
api.clear_task = api.DAQmxClearTask
api.clear_task.argtypes = [C.c_void_p]
api.clear_task.restype = check_error


if __name__ == '__main__':
##    6738 test block

NI_board_allocation = {
    ('laser488power', 'constant', 0, 5, "Dev1", 0),
    ('laser488onoff', 'digital', "Dev1", 1),
    ('laser552power', 'constant', 0, 5, "Dev1", 3),
    ('laser552onoff', 'digital', "Dev1", 3),
    ('laser594power', 'constant', 0, 5, "Dev1", 5),
    ('laser594onoff', 'digital', "Dev1", 5),
    ('laser640power', 'constant', 0, 5, "Dev1", 12),
    ('laser640onoff', 'digital', "Dev1"),
    ('voicecoil', 'analog', 0, 10, "Dev1", 18)
}

ao_board = NIboard_management(NI_board_allocation)