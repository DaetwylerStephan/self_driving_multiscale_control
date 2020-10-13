from MCSControl_PythonWrapper import *
import time

#init error_msg
error_msg = ct.c_char_p()

#initialize system and channelindex
systemIndex = ct.c_ulong()
channelIndex = 0
st = ct.c_ulong(1)

#check dll version
version = ct.c_ulong()
SA_GetDLLVersion(version)
print('DLL-version: {}'.format(version.value))

#find systems available
outBuffer = ct.create_string_buffer(1)
ioBufferSize = ct.c_ulong(1)
results = SA_FindSystems('', outBuffer, ioBufferSize);
outBuffer = ct.create_string_buffer(ioBufferSize.value)
ioBufferSize = ct.c_ulong(ioBufferSize.value+1)
results = SA_FindSystems('', outBuffer, ioBufferSize);
print('outBuffer: {}'.format(outBuffer[:].decode("utf-8")))
print('ioBuffer: {}'.format(ioBufferSize.value))
SA_GetStatusInfo(results, error_msg)
print('SA_GetStatusInfo: {}'.format(error_msg.value[:].decode('utf-8')))

#connect to system
results = SA_OpenSystem(systemIndex, outBuffer,'sync,reset')
print('systemIndex: {}'.format(systemIndex.value))


#result = SA_StepMove_S(systemIndex,2,100,4095,440);
SA_GetStatusInfo(results, error_msg)
print('SA_GetStatusInfo: {}'.format(error_msg.value[:].decode('utf-8')))

Alle_mein_Entchen_Freq = [262,294,330,349,392,392,440,440,440,440,392,440,440,440,440,392,349,349,349,349,330,330,294,294,294,294,262]
Alle_mein_Entchen_Time = [500,500,500,500,1000,1000,500,500,500,500,1500,500,500,500,500,1500,500,500,500,500,1000,1000,500,500,500,500,1000]
Alle_mein_Entchen_Time = [int(x/2) for x in Alle_mein_Entchen_Time]
print(Alle_mein_Entchen_Time)

for index,freq in enumerate(Alle_mein_Entchen_Freq):
	print('Frequenz: {}, Laenge: {}'.format(freq, Alle_mein_Entchen_Time[index]))
	#SA_StepMove_S(systemIndex,0,Alle_mein_Entchen_Time[index],4095, freq)
	SA_StepMove_S(systemIndex,1,Alle_mein_Entchen_Time[index],4095, freq)
	#SA_StepMove_S(systemIndex,2,Alle_mein_Entchen_Time[index],4095, 2*freq)
	while True:
		SA_GetStatus_S(systemIndex,channelIndex, st)
		if st.value == SA_STOPPED_STATUS:
			time.sleep(1.0)
			break

#close connection
results= SA_CloseSystem(systemIndex)
results = SA_GetStatusInfo(results, error_msg)
print('SA_GetStatusInfo: {}'.format(error_msg.value[:].decode('utf-8')))


	
