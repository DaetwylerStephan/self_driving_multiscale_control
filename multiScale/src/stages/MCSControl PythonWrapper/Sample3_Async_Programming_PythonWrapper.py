# /**********************************************************************
# * Copyright (c) 2017 SmarAct GmbH
# *
# * This is a Python programming example for the Modular Control System 
# * API.
# * It demonstrates programming with asynchronous functions.
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

# error message printer
def PrintMcsError(st):
    print("MCS error {}\n".format(st))

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

    mcsHandle = ct.c_ulong()
    numOfChannels = ct.c_ulong(0)
    channelA = 0
    channelB = 1
    stop = 0
    chanAStopped = 0
    chanBStopped = 0
    packet = SA_packet()

    #// ----------------------------------------------------------------------------------
    #find all available MCS systems
    outBuffer = ct.create_string_buffer(17) 
    ioBufferSize = ct.c_ulong(18)
    ExitIfError( SA_FindSystems('', outBuffer, ioBufferSize) ) #will report a 'MCS error: query-buffer size' if outBuffer, ioBufferSize is to small
    print('MCS address: {}'.format(outBuffer[:18].decode("utf-8"))) #connect to first system of list

    #// open the first MCS with USB interface in synchronous communication mode
    ExitIfError( SA_OpenSystem(mcsHandle, outBuffer, bytes('async,reset',"utf-8")) )
    
    ExitIfError( SA_GetNumberOfChannels(mcsHandle,numOfChannels) )
    print("Number of Channels: {}\n".format(numOfChannels.value))

    # /* If buffered output is enabled the commands are collected in a 
    #    buffer on the PC side. SA_FlushOutput_A sends the buffer 
    #    content to the MCS. Buffering is useful to prepare some commands
    #    (e.g. movements) and send them to the MCS simultaneously. */

    ExitIfError( SA_SetBufferedOutput_A(mcsHandle,SA_BUFFERED_OUTPUT) )

    # /* This stores movement commands for two positioners in the output
    #    buffer on the PC.
    #    FlushOutput sends them to the MCS so both positioners will start 
    #    moving (almost) simultaneously. */

    ExitIfError( SA_StepMove_A(mcsHandle,channelA,200,4000,800) )
    ExitIfError( SA_StepMove_A(mcsHandle,channelB,250,4000,1000) )
    ExitIfError( SA_FlushOutput_A(mcsHandle) )

    #/* now poll the status of the two channels until both have 'stopped' status */

    while True:
        if stop == 1:
            break
    
        # /* To receive data from the MCS store the Get... commands in the
        #    buffer and flush it. */
        ExitIfError( SA_GetStatus_A(mcsHandle,channelA) )
        ExitIfError( SA_GetStatus_A(mcsHandle,channelB) )
        ExitIfError( SA_FlushOutput_A(mcsHandle) )

        # /* Receive packets from the MCS. The code should be prepared to handle
        #    unexpected packets like error packets beside the expected ones 
        #    (here: status packets). Also note that ReceiveNextPacket could 
        #    timeout before a packet is received, which is indicated by a 
        #    SA_NO_PACKET_TYPE packet. */

        ExitIfError( SA_ReceiveNextPacket_A(mcsHandle,1000,packet) )

        if packet.SA_PACKET_TYPE == SA_NO_PACKET_TYPE:         #/* SA_ReceiveNextPacket_A timed out */
            break
        elif packet.SA_PACKET_TYPE == SA_ERROR_PACKET_TYPE:     # /* the MCS has sent an error message */
            PrintMcsError(packet.data1)
            stop = 1
            break
        if packet.SA_PACKET_TYPE == SA_STATUS_PACKET_TYPE:     #/* received a channel status packet */
            print('Packet received from:')
            if (packet.SA_INDEX == channelA):
                print('Channel A')
                if (not chanAStopped) and (packet.data1 == SA_STOPPED_STATUS):
                
                    chanAStopped = 1
                    print("\n!!! Channel A has stopped !!!\n")
                
            
            elif (packet.SA_INDEX == channelB):
                print('Channel B')
                if (not chanBStopped) and (packet.data1 == SA_STOPPED_STATUS):
                
                    chanBStopped = 1
                    print("\n!!! Channel B has stopped !!!\n")
                
            
            stop = (chanAStopped and chanBStopped)
            #break
        
    

    ExitIfError( SA_CloseSystem(mcsHandle) )

    return

if __name__ == "__main__":
    main()