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
from MCSControl_PythonWrapper import *
import time

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

# ### implement getchar() function for single character user input
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _GetchWindows()


def main():
    error = ct.c_ulong(SA_OK)
    mcsHandle = ct.c_ulong()
    numOfChannels = ct.c_ulong(0)
    channel = ct.c_ulong(0)
    sensorType = ct.c_ulong()
    linearSensorPresent = 0
    rotSensorPresent = 0
    key = ct.c_int(0)
    status = ct.c_ulong()
    position = ct.c_int()
    step_angle = 1000000
    lin_step = 100000
    steps = 200

    #// ----------------------------------------------------------------------------------
    #find all available MCS systems
    outBuffer = ct.create_string_buffer(17) 
    ioBufferSize = ct.c_ulong(18)
    ExitIfError( SA_FindSystems('', outBuffer, ioBufferSize) ) #will report a 'MCS error: query-buffer size' if outBuffer, ioBufferSize is to small
    print('MCS address: {}'.format(outBuffer[:18].decode("utf-8"))) #connect to first system of list

    #// open the first MCS with USB interface in synchronous communication mode
    ExitIfError( SA_OpenSystem(mcsHandle,outBuffer, bytes('sync,reset',"utf-8")) )
    
    ExitIfError( SA_GetNumberOfChannels(mcsHandle,numOfChannels) )
    print("Number of Channels: {}\n".format(numOfChannels.value))
    if not numOfChannels.value == 0:
        channelList = list(range(numOfChannels.value))
        print("Which channel you want to control: {}".format(channelList))
        channel = ct.c_ulong(int(getch().decode("utf-8"))) #set channel
    else:
        return
    #// ----------------------------------------------------------------------------------
    #// check availability of linear sensor. only if a sensor is present
    #// the position can be read with SA_GetPosition_S
    ExitIfError( SA_GetSensorType_S(mcsHandle, channel, sensorType) )
    if (sensorType.value == SA_S_SENSOR_TYPE) or (sensorType.value == SA_M_SENSOR_TYPE) or \
        (sensorType.value == SA_SC_SENSOR_TYPE) or (sensorType.value == SA_SP_SENSOR_TYPE):
        linearSensorPresent = 1
        print("Linear sensor present\n")
    elif (sensorType.value == SA_SR_SENSOR_TYPE):
        rotSensorPresent = 1
        print("Rotational sensor present\n")
    else:
        linearSensorPresent = 0
        print("No linear sensor present\n")

    #// ----------------------------------------------------------------------------------
    if(linearSensorPresent):
        print("\nENTER COMMAND AND RETURN\n"\
            "+  Move positioner up by {}um\n"\
            "-  Move positioner down by {}um\n"\
            "s  Change step size\n"\
            "q  Quit program\n".format(lin_step/1000,lin_step/1000))
    elif (rotSensorPresent):
            print("\nENTER COMMAND AND RETURN\n"\
            "+  Move positioner up by {}mgrad\n"\
            "-  Move positioner down by {}mgrad\n"\
            "s  Change step size\n"\
            "q  Quit program\n".format(step_angle/1000,step_angle/1000))
    else:
        print("\nENTER COMMAND AND RETURN\n"\
            "+  Move positioner up by {} steps\n"\
            "-  Move positioner down by {} steps\n"\
            "s  Change number of steps\n"\
            "q  Quit program\n".format(steps,steps))
    
    #// ----------------------------------------------------------------------------------
    while True:
        key = getch().decode("utf-8")
        if key == 'q':
            break
        if (key == 's'):
            if (linearSensorPresent):
                print("Enter step size (nm):\n")
                lin_step = int(input())
                print("\nENTER COMMAND AND RETURN\n"\
                "+  Move positioner up by {}um\n"\
                "-  Move positioner down by {}um\n"\
                "s  Change step size\n"\
                "q  Quit program\n".format(lin_step/1000,lin_step/1000))
            elif (rotSensorPresent):
                print("Enter step size (ugrad):\n")
                step_angle = int(input())
                print("\nENTER COMMAND AND RETURN\n"\
                "+  Move positioner up by {}mgrad\n"\
                "-  Move positioner down by {}mgrad\n"\
                "s  Change step size\n"\
                "q  Quit program\n".format(step_angle/1000,step_angle/1000))               
            else:
                print("Enter number of steps:\n")
                steps = int(input())
                print("\nENTER COMMAND AND RETURN\n"\
                "+  Move positioner up by {} steps\n"\
                "-  Move positioner down by {} steps\n"\
                "s  Change number of steps\n"\
                "q  Quit program\n".format(steps,steps))
        if (key == '-'):										
            if (linearSensorPresent):						
                ExitIfError( SA_GotoPositionRelative_S(mcsHandle, channel, -lin_step, 1000) )
            elif (rotSensorPresent):                       
                ExitIfError( SA_GotoAngleRelative_S(mcsHandle, channel, -step_angle, 0, 1000) )
            else:
                ExitIfError( SA_StepMove_S(mcsHandle, channel,-steps, 4095, 2000)	)						

        if (key == '+'):											
            if (linearSensorPresent):							
                ExitIfError( SA_GotoPositionRelative_S(mcsHandle, channel, lin_step, 1000) )
            elif (rotSensorPresent):                       
                ExitIfError( SA_GotoAngleRelative_S(mcsHandle, channel, step_angle, 0, 1000) )	
            else:
                ExitIfError( SA_StepMove_S(mcsHandle, channel, steps, 4095, 2000)	)						

        #// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #// wait until movement has finished
        #// in synchronous communication mode, the current status of each channel
        #// must be checked periodically ('polled') to know when a movement has
        #// finished:
        while True:
            ExitIfError( SA_GetStatus_S(mcsHandle, channel, status) )	
            time.sleep(0.05)
            #print(status.value)
            if (status.value == SA_TARGET_STATUS) or (status.value == SA_STOPPED_STATUS):
                break

        #// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if (linearSensorPresent):
            ExitIfError( SA_GetPosition_S(mcsHandle, channel, position) )
            print("Position: {} nm (Press \'s\' to change step size. Press \'q\' to exit.)".format(position.value))
        elif (rotSensorPresent):
            revolution = ct.c_ulong()
            ExitIfError( SA_GetAngle_S(mcsHandle, channel, position, revolution) )
            print("Position: {} ugrad (Press \'s\' to change step size. Press \'q\' to exit.)".format(position.value))
        #// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ExitIfError( SA_CloseSystem(mcsHandle) )
    
    return
    


if __name__ == "__main__":
    main()