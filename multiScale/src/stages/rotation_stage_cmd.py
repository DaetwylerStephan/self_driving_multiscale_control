


# Import MCSControl_PythonWrapper.py
from MCSControl.MCSControl_PythonWrapper import *

class SR2812_rotationstage:

    def __init__(self, locator):
        # check dll version (not really necessary)
        version = ct.c_ulong()
        SA_GetDLLVersion(version)
        print('DLL-version: {}'.format(version.value))

        # initialize some variables
        self.sensorEnabled = ct.c_ulong(0)  # initialize sensorEnbaled variable
        self.mcsHandle = ct.c_ulong()  # initialize MCS control handle

        # /* Open the first MCS with USB interface in synchronous communication mode */
        self.ExitIfError(SA_OpenSystem(self.mcsHandle, bytes(locator, "utf-8"), bytes('sync,reset', "utf-8")))

        self.ExitIfError( SA_GetSensorEnabled_S(self.mcsHandle,self.sensorEnabled) )

        if (self.sensorEnabled.value == SA_SENSOR_DISABLED):
            print("Sensors are disabled: {}\n".format(self.sensorEnabled.value))
            return
        elif (self.sensorEnabled.value == SA_SENSOR_ENABLED):
            print("Sensors are enabled: {}\n".format(self.sensorEnabled.value))
            return
        elif (self.sensorEnabled.value == SA_SENSOR_POWERSAVE):
            print("Sensors are in power-save mode: {}\n".format(self.sensorEnabled.value))
            return
        else:
            print("Error: unknown sensor power status: {}\n".format(self.sensorEnabled.value))
            return


    def ExitIfError(self, status):
        #init error_msg variable
        error_msg = ct.c_char_p()
        if(status != SA_OK):
            SA_GetStatusInfo(status, error_msg)
            print('MCS error: {}'.format(error_msg.value[:].decode('utf-8')))
        return

    def closestage(self):
        # /* At the end of the program you should release all opened systems. */
        self.ExitIfError(SA_CloseSystem(self.mcsHandle))
        print('stage closed')

if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'usb:id:3948963323'

    rotationstage = SR2812_rotationstage(stage_id)
    rotationstage.closestage()
