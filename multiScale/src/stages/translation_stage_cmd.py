'''
translation_stage_cmd.py
========================================
Script containing all functions to initialize and operate the translation stages from Smaract
'''

import sys
from threading import Event, Thread

try:
    from .smaract import ctl as ctl
except ImportError:
    import smaract.ctl as ctl



class SLC_translationstage:

    def __init__(self, locator):
        '''
        Initialize translation stage parameters, and print out some parameters for debugging
        Input: locator address of the translation stage, e.g. usb:sn:MCS2-00001795
        Output: an initialized and connected stage.
        '''
        self.locator = locator
        self.d_handle = 0
        self.no_of_channels = 0

        # Read the version of the library
        # Note: this is the only function that does not require the library to be initialized.
        version = ctl.GetFullVersionString()
        print("SmarActCTL library version: '{}'.".format(version))
        self.assert_lib_compatibility()

        try:
            # Open the MCS2 device
            self.d_handle = ctl.Open(self.locator)
            print("MCS2 opened {}.".format(self.locator))

            serial = ctl.GetProperty_s(self.d_handle, 0, ctl.Property.DEVICE_SERIAL_NUMBER)
            print("Device Serial Number: {}".format(serial))

        except ctl.Error as e:
            # Passing an error code to "GetResultInfo" returns a human readable string
            # specifying the error.
            print("MCS2 {}: {}, error: {} (0x{:04X}) in line: {}."
              .format(e.func, ctl.GetResultInfo(e.code), ctl.ErrorCode(e.code).name, e.code,
                      (sys.exc_info()[-1].tb_lineno)))

        except Exception as ex:
            print("Unexpected error: {}, {} in line: {}".format(ex, type(ex), (sys.exc_info()[-1].tb_lineno)))
            raise

        self.no_of_channels = ctl.GetProperty_i32(self.d_handle, 0, ctl.Property.NUMBER_OF_CHANNELS)
        print("MCS2 number of channels: {}.".format(self.no_of_channels))



    def assert_lib_compatibility(self):
        """
        Checks that the major version numbers of the Python API and the
        loaded shared SmarAct library are the same to avoid errors due to
        incompatibilities.
        Raises a RuntimeError if the major version numbers are different.
        """
        vapi = ctl.api_version
        vlib = [int(i) for i in ctl.GetFullVersionString().split('.')]
        if vapi[0] != vlib[0]:
            raise RuntimeError("Incompatible SmarActCTL python api and library version.")

    def findReference(self):
        # Set find reference options.
        # The reference options specify the behavior of the find reference sequence.
        # The reference flags can be ORed to build the reference options.
        # By default (options = 0) the positioner returns to the position of the reference mark.
        # Note: In contrast to previous controller systems this is not mandatory.
        # The MCS2 controller is able to find the reference position "on-the-fly".
        # See the MCS2 Programmer Guide for a description of the different modes.

        for channel in range(self.no_of_channels):
            print("MCS2 find reference on channel: {}.".format(channel))

            ctl.SetProperty_i32(self.d_handle, channel, ctl.Property.REFERENCING_OPTIONS, 0)
            # Set velocity to 1mm/s
            ctl.SetProperty_i64(self.d_handle, channel, ctl.Property.MOVE_VELOCITY, 1000000000)
            # Set acceleration to 10mm/s2.
            ctl.SetProperty_i64(self.d_handle, channel, ctl.Property.MOVE_ACCELERATION, 10000000000)
            # Start referencing sequence
            ctl.Reference(self.d_handle, channel)
            # Note that the function call returns immediately, without waiting for the movement to complete.
            # The "ChannelState.REFERENCING" flag in the channel state can be monitored to determine
            # the end of the referencing sequence.
            self.waitForEvent_referencing()

        #Set all positions to 0 pm
        for channel in range(self.no_of_channels):
            state = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.CHANNEL_STATE)
            # The returned channel state holds a bit field of several state flags.
            # See the MCS2 Programmers Guide for the meaning of all state flags.
            # We pick the "sensorPresent" flag to check if there is a positioner connected
            # which has an integrated sensor.
            # Note that in contrast to previous controller systems the controller supports
            # hotplugging of the sensor module and the actuators.
            position = ctl.GetProperty_i64(self.d_handle, channel, ctl.Property.POSITION)
            base_unit = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.POS_BASE_UNIT)

            #print("MCS2 position of channel {}: {}".format(channel, position), end='')
            #print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")

            position = 0  # in pm | ndeg
            print("MCS2 set position of channel {} to {}".format(channel, position), end='')
            base_unit = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.POS_BASE_UNIT)
            print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")
            ctl.SetProperty_i64(self.d_handle, channel, ctl.Property.POSITION, position)


    def close(self):
        if self.d_handle != None:
            ctl.Close(self.d_handle)
            print("MCS2 close.")

    def waitForEvent_referencing(self):
        """ Wait for events generated by the connected device """
        # The wait for event function blocks until an event was received or the timeout elapsed.
        # In case of timeout, a "ctl.Error" exception is raised containing the "TIMEOUT" error.
        # If the "timeout" parameter is set to "ctl.INFINITE" the call blocks until an event is received.
        # This can be useful in case the WaitForEvent function runs in a separate thread.
        # For simplicity, this is not shown here thus we set a timeout of 3 seconds.
        timeout = 3000  # in ms
        try:
            event = ctl.WaitForEvent(self.d_handle, timeout)
            # The "type" field specifies the event.
            # The "idx" field holds the device index for this event, it will always be "0", thus might be ignored here.
            # The "i32" data field gives additional information about the event.
            if event.type == ctl.EventType.REFERENCE_FOUND:
                if (event.i32 == ctl.ErrorCode.NONE):
                    # Movement finished.
                    print("MCS2 reference found, channel: ", event.idx)
                else:
                    # The movement failed for some reason. E.g. an endstop was detected.
                    print("MCS2 reference found, channel: {}, error: 0x{:04X} ({}) ".format(event.idx, event.i32,
                                                                                              ctl.GetResultInfo(
                                                                                                  event.i32)))
            else:
                # The code should be prepared to handle unexpected events beside the expected ones.
                print("MCS2 received event: {}".format(ctl.GetEventInfo(event)))
                self.waitForEvent_referencing()

        except ctl.Error as e:
            if e.code == ctl.ErrorCode.TIMEOUT:
                print("MCS2 wait for event timed out after {} ms".format(timeout))
            else:
                print("MCS2 {}".format(ctl.GetResultInfo(e.code)))
            return


    def waitForEvent_stream(self):
        """Wait for events generated by the connected device"""
        while True:
            try:
                self.event = ctl.WaitForEvent(self.d_handle, ctl.INFINITE)
                # The "type" field specifies the event.
                # The "idx" field holds the channel where the event came from.
                # The "i32" data field gives additional information about the event, e.g. error code.
                # Passing the event to GetEventInfo" returns a human readable string
                # specifying the event.
                if self.event.type == ctl.EventType.STREAM_FINISHED:
                    print("Stream: MCS2 {}".format(ctl.GetEventInfo(self.event)))
                    if ctl.EventParameter.PARAM_RESULT(self.event.i32) == ctl.ErrorCode.NONE:
                        # All streaming frames were processed, stream finished.
                        self.stream_done.set()
                    elif ctl.EventParameter.PARAM_RESULT(self.event.i32) == ctl.ErrorCode.ABORTED:
                        # Stream was canceled by the user.
                        print("Stream: MCS2 stream aborted by user")
                        self.stream_done.set()
                        self.stream_abort.set()
                    else:
                        # Stream was canceled by device.
                        # Note: The event parameter now holds the error code as well as the channel index responsible for the failure
                        print("Stream: MCS2 stream aborted by device: {}".format(
                            ctl.ErrorCode(ctl.EventParameter.PARAM_RESULT(self.event.i32)).name))
                        self.stream_done.set()
                        self.stream_abort.set()
                elif self.event.type == ctl.EventType.STREAM_READY or self.event.type == ctl.EventType.STREAM_TRIGGERED:
                    # These events are mainly useful when the STREAM_TRIGGER_MODE_EXTERNAL_ONCE trigger mode is used.
                    # A STREAM_READY event is generated to indicate that the stream is ready to be triggered
                    # by the external trigger. In this armed state the device waits for the trigger to occur and then generates a
                    # STREAM_TRIGGERED event.
                    # This example uses the STREAM_TRIGGER_MODE_DIRECT trigger mode, thus we don't care about this events here.
                    pass
                else:
                    # The code should be prepared to handle unexpected events beside the expected ones.
                    print("Stream: MCS2 received event: {}".format(ctl.GetEventInfo(self.event)))

            except ctl.Error as e:
                if e.code == ctl.ErrorCode.CANCELED:
                    # we use "INFINITE" timeout, so the function call will return only when canceled by the "Cancel" function
                    print("Stream: MCS2 canceled wait for event")
                else:
                    print("Stream: MCS2 {}".format(ctl.GetResultInfo(e.code)))
                return


    def streamPosition(self, no_of_frames, increment):

        try:
            self.stream_done = Event()
            self.stream_abort = Event()

            # Spawn a thread to receive events from the controller.
            event_handle_thread = Thread(target=self.waitForEvent_stream)
            event_handle_thread.start()

            ctl.SetProperty_i32(self.d_handle, 0, ctl.Property.SENSOR_POWER_MODE, ctl.SensorPowerMode.ENABLED)
            ctl.SetProperty_i32(self.d_handle, 0, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)

            # Prepare for streaming, select desired trigger mode
            # (using STREAM_TRIGGER_MODE_DIRECT starts the stream as soon as enough frames were sent to the device)
            s_handle = ctl.OpenStream(self.d_handle, ctl.StreamTriggerMode.DIRECT)

            startPosition = ctl.GetProperty_i64(self.d_handle, 0, ctl.Property.POSITION)
            print(startPosition)

            stream_buffer = []
            for frame_idx in range(no_of_frames):
                frame = [int(0), int(startPosition + frame_idx*increment)]
                print(frame)
                stream_buffer.append(frame)

            for frame_idx in range(no_of_frames):
                # The "waitForEvent" thread received an "abort" event.
                if self.stream_abort.isSet():
                    break
                # Make list from stream data, each frame contains all
                # target positions for all channels that participate in the trajectory.
                # The frame data list must have the structure:
                # <chA>,<posA,<chB>,<posB>
                frame = stream_buffer[frame_idx]
                ctl.StreamFrame(self.d_handle, s_handle, frame)

            # All frames sent, close stream
            ctl.CloseStream(self.d_handle, s_handle)
            print("stream closed")
            # Wait for the "stream done" event.
            self.stream_done.wait()
            print("wait closed")
            # Cancel waiting for events.
            ctl.Cancel(self.d_handle)
            print("canceled")
            # Wait for the "waitForEvent" thread to terminate.
            event_handle_thread.join()

        except ctl.Error as e:
            # Passing an error code to "GetResultInfo" returns a human readable string
            # specifying the error.
            print("MCS2 {}: {}, error: {} (0x{:04X}) in line: {}."
                  .format(e.func, ctl.GetResultInfo(e.code), ctl.ErrorCode(e.code).name, e.code,
                          (sys.exc_info()[-1].tb_lineno)))

        except Exception as ex:
            print("Unexpected error: {}, {} in line: {}".format(ex, type(ex), (sys.exc_info()[-1].tb_lineno)))
        raise


if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'network:sn:MCS2-00000382'

    translationstage = SLC_translationstage(stage_id)
    translationstage.findReference()
    translationstage.streamPosition(100, 400000)
    translationstage.close()