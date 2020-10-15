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

        # Read the version of the library
        # Note: this is the only function that does not require the library to be initialized.
        version = ctl.GetFullVersionString()
        print("SmarActCTL library version: '{}'.".format(version))
        self.assert_lib_compatibility()

        try:
            # Open the first MCS2 device from the list
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


    def closestage(self):
        if self.d_handle != None:
            ctl.Close(self.d_handle)
            print("MCS2 close.")

if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'usb:sn:MCS2-00001795'

    translationstage = SLC_translationstage(stage_id)
    translationstage.closestage()