# /**********************************************************************
# * Copyright (c) 2017 SmarAct GmbH
# *
# * This is a Python programming example for the Modular Control System 
# * API.
# *
# * THIS  SOFTWARE, DOCUMENTS, FILES AND INFORMATION ARE PROVIDED 'AS IS'
# * WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING,
# * BUT  NOT  LIMITED  TO,  THE  IMPLIED  WARRANTIES  OF MERCHANTABILITY,
# * FITNESS FOR A PURPOSE, OR THE WARRANTY OF NON-INFRINGEMENT.
# * THE  ENTIRE  RISK  ARISING OUT OF USE OR PERFORMANCE OF THIS SOFTWARE
# * REMAINS WITH YOU.
# * IN  NO  EVENT  SHALL  THE  SMARACT  GMBH  BE  LIABLE  FOR ANY DIRECT,
# * INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL OR OTHER DAMAGES ARISING
# * OUT OF THE USE OR INABILITY TO USE THIS SOFTWARE.
# **********************************************************************/

# Import MCSControl_PythonWrapper.py 
from src.stages.MCSControl.MCSControl_PythonWrapper import *

#check dll version (not really necessary)
version = ct.c_ulong()
SA_GetDLLVersion(version)
print('DLL-version: {}'.format(version.value))

#/* All MCS commands return a status/error code which helps analyzing 
#   problems */

def ExitIfError(status):
    #init error_msg variable
    error_msg = ct.c_char_p()
    if(status != SA_OK):
        SA_GetStatusInfo(status, error_msg)
        print('MCS error: {}'.format(error_msg.value[:].decode('utf-8')))
    return

def main():

    #find all available MCS systems
    outBuffer = ct.create_string_buffer(4096)
    ioBufferSize = ct.c_ulong(4096)
    ExitIfError( SA_FindSystems('', outBuffer, ioBufferSize) ) #will report a 'MCS error: query-buffer size' if outBuffer, ioBufferSize is to small
    print('MCS address: {}'.format(outBuffer[:18].decode("utf-8"))) #connect to first system of list

    # initialize some variables
    sensorEnabled = ct.c_ulong(0) #initialize sensorEnbaled variable
    mcsHandle = ct.c_ulong() #initialize MCS control handle

    # /* When opening a controller you must select one of the two communication
    #    modes:
    # sync: only commands from the set of synchronous commands can 
    #     be used in the program. In sync. communication mode commands like
    #     GetPosition, GetStatus etc. return the requested value directly. 
    #     this is easier to program, especially for beginners.
    # async: only asynchronous commands can be used. In this mode Get... 
    #     commands send a request message to the MCS controller but do not 
    #     wait for the reply. The replied message must be catched with special
    #     commands ReceiveNextPacket, ReceiveNextPacketIfChannel or 
    #     LookAtNextPacket, which are only available in async. communication
    #     mode. Please read the MCS Programmer's Guide for more information. */

    #/* Open the first MCS with USB interface in synchronous communication mode */
    ExitIfError( SA_OpenSystem(mcsHandle,bytes('usb:id:3948963323',"utf-8"), bytes('sync,reset',"utf-8")) )

    # /* Now the MCS is initialized and can be used.
    #    In this demo program all we do is reading the sensor power-mode. */

    ExitIfError( SA_GetSensorEnabled_S(mcsHandle,sensorEnabled) )
    if (sensorEnabled.value == SA_SENSOR_DISABLED): 
        print("Sensors are disabled: {}\n".format(sensorEnabled.value))
        return
    elif (sensorEnabled.value == SA_SENSOR_ENABLED): 
        print("Sensors are enabled: {}\n".format(sensorEnabled.value)) 
        return
    elif (sensorEnabled.value == SA_SENSOR_POWERSAVE): 
        print("Sensors are in power-save mode: {}\n".format(sensorEnabled.value)) 
        return
    else:
        print("Error: unknown sensor power status: {}\n".format(sensorEnabled.value))
        return

   # /* At the end of the program you should release all opened systems. */

    ExitIfError( SA_CloseSystem(mcsHandle) )
  
    return

if __name__ == "__main__":
    main()

# # Example output in terminal: 
# DLL-version: 33554456
# MCS address: usb:id:1778011641
# Sensors are enabled: 1