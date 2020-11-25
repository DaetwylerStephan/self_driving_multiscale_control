'''
translation_stage_cmd.py
========================================
Script containing all functions to initialize and operate the translation stages from Smaract
'''

import sys
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

        for channel in range(self.no_of_channels):
            print(channel)
            state = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.CHANNEL_STATE)
            # The returned channel state holds a bit field of several state flags.
            # See the MCS2 Programmers Guide for the meaning of all state flags.
            # We pick the "sensorPresent" flag to check if there is a positioner connected
            # which has an integrated sensor.
            # Note that in contrast to previous controller systems the controller supports
            # hotplugging of the sensor module and the actuators.
            position = ctl.GetProperty_i64(self.d_handle, channel, ctl.Property.POSITION)
            base_unit = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.POS_BASE_UNIT)

            print("MCS2 position of channel {}: {}".format(channel, position), end='')
            print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")

            position = 100000000  # in pm | ndeg
            print("MCS2 set position of channel {} to {}".format(channel, position), end='')
            base_unit = ctl.GetProperty_i32(self.d_handle, channel, ctl.Property.POS_BASE_UNIT)
            print("pm.") if base_unit == ctl.BaseUnit.METER else print("ndeg.")
            ctl.SetProperty_i64(self.d_handle, channel, ctl.Property.POSITION, position)

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

    def closestage(self):
        if self.d_handle != None:
            ctl.Close(self.d_handle)
            print("MCS2 close.")

if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'usb:sn:MCS2-00001795'

    translationstage = SLC_translationstage(stage_id)
    translationstage.findReference()
    translationstage.closestage()