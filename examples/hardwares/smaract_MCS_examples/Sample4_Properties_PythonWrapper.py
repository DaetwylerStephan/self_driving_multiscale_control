# /**********************************************************************
# * Copyright (c) 2017 SmarAct GmbH
# *
# * This sample Python program shows how to work with channel properties.
# * (please read the MCS Programmer's Guide chapter about channel
# * properties first)
# * Properties are key/value pairs in the MCS that affect the behavior
# * of the controller. To read or write the value of a property, the
# * property must be addressed with its key. Keys consist of a component
# * selector, a sub-component selector and the property name.
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
from MCSControl_PythonWrapper import *

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

    error = SA_OK
    mcsHandle = ct.c_ulong()
    value = ct.c_int()

    #/* open the first MCS with USB interface in syncronous communication mode */
    #// ----------------------------------------------------------------------------------
    #find all available MCS systems
    outBuffer = ct.create_string_buffer(17) 
    ioBufferSize = ct.c_ulong(18)
    ExitIfError( SA_FindSystems('', outBuffer, ioBufferSize) ) #will report a 'MCS error: query-buffer size' if outBuffer, ioBufferSize is to small
    print('MCS address: {}'.format(outBuffer[:18].decode("utf-8"))) #connect to first system of list

    #// open the first MCS with USB interface in synchronous communication mode
    ExitIfError( SA_OpenSystem(mcsHandle,outBuffer,bytes('sync,reset',"utf-8")) )

    # /* Read the value of the low-vibration operation mode property which
    #    is 1 if the low-vibration movement mode is active. 
    #    The utilitiy function SA_EPK (encode property key) converts the
    #    three components of a property key to an unsigned int which is
    #    passed to the property get and set functions. */

    ExitIfError( SA_GetChannelProperty_S(mcsHandle,0,
                    SA_EPK(SA_GENERAL,SA_LOW_VIBRATION,SA_OPERATION_MODE),value) )
    print("Low-Vibration operation mode property is {}\n".format(value.value))

    # /* This reads another property (the current value of the internal counter #0). 
    #    The sub-component here is an integer number which is the index of the
    #    counter. 
    #    Note: when reading a property in asynchronous mode the value is returned
    #    in a SA_CHANNEL_PROPERTY_PACKET */

    print("Setting counter #0 to 0\n")
    ExitIfError( SA_SetChannelProperty_S(mcsHandle,0,SA_EPK(SA_COUNTER,0,SA_VALUE),0) )

    ExitIfError( SA_GetChannelProperty_S(mcsHandle,0,SA_EPK(SA_COUNTER,0,SA_VALUE),value) )
    print("Counter #0 value is {}\n".format(value.value))

    #/* Reset counter #0 by setting its value to 0 */

    print("Resetting counter #0 to 42\n")
    ExitIfError( SA_SetChannelProperty_S(mcsHandle,0,SA_EPK(SA_COUNTER,0,SA_VALUE),42) )

    ExitIfError( SA_GetChannelProperty_S(mcsHandle,0,SA_EPK(SA_COUNTER,0,SA_VALUE),value) )
    print("Counter #0 value is {}\n".format(value.value))

    ExitIfError( SA_CloseSystem(mcsHandle) )

    return

if __name__ == "__main__":
  main()