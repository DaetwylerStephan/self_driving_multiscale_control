'''
synthetic_translation_stage.py
========================================
Script containing all functions to initialize and operate a synthetic translation stage
'''

import sys
from threading import Event, Thread
import numpy as np




class Synthetic_translationstage:

    def __init__(self):
        '''
        Initialize translation stage parameters, and print out some parameters for debugging
        Input: locator address of the translation stage, e.g. usb:sn:MCS2-00001795
        Output: an initialized and connected stage.
        '''
        self.no_of_channels = 0
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0

        # initialize stream events
        self.stream_done = Event()
        self.stream_abort = Event()

        print("Synthetic translation stage initialized")

    def findReference(self):
        # Set find reference options.
        # The reference options specify the behavior of the find reference sequence.
        # The reference flags can be ORed to build the reference options.
        # By default (options = 0) the positioner returns to the position of the reference mark.
        # Note: In contrast to previous controller systems this is not mandatory.
        # The MCS2 controller is able to find the reference position "on-the-fly".
        # See the MCS2 Programmer Guide for a description of the different modes.

        self.position_x = 0
        self.position_y = 0
        self.position_z = 0


    def close(self):
        print("Synthetic translation stage closed.")


    def moveToPosition(self, position_list):

        print("move to: " + str( position_list[0]))
        print("move to: " + str( position_list[1]))
        print("move to: " + str( position_list[2]))

    def streamStackAcquisition_externalTrigger_setup(self, no_of_frames, increment, slow_velocity, slow_acceleration):
        """

        :param no_of_frames: how many frames the stream will be
        :param increment: how many um the stream will go up
        :param slow_velocity: the factor for velocity of 10 mm/s
        :param slow_acceleration: the factor for acceleration 100 mm/s2
        :return: a waiting stream to receive voltage inputs
        """
        self.stream_done.clear()
        self.stream_abort.clear()

        #check velocity not too high
        if slow_velocity >= 1:
            slow_velocity =1
        if slow_acceleration >= 1:
            slow_acceleration =1

        #get starting position for stream
        startPosition = self.position_z
        print(startPosition)

        #generate array with relative positions to starting value based on the chosen increment
        stream_buffer = []
        for frame_idx in range(no_of_frames):
            frame = [int(0), int(startPosition + frame_idx * increment)]
            stream_buffer.append(frame)

        stream_buffer.append([int(0), startPosition])


        #iterate through stream_buffer
        pass

    def streamStackAcquisition_externalTrigger_waitEnd(self):
        # Wait for the "stream done" event.
        pass

if __name__ == '__main__':
    ##test here code of this class

    translationstage = Synthetic_translationstage()
    translationstage.findReference()
    #3000000 = 3 um
    #translationstage.streamPosition(100, 3000000)
    position_list = [1000000000, 2000000000, 8000000000]
    translationstage.moveToPosition(position_list)

    import time
    time.sleep(5)
    translationstage.streamStackAcquisition_externalTrigger_setup(1000, 5000000,0.5,0.5)
    time.sleep(3)

    position_list = [3000000000, -2000000000, -8000000000]
    translationstage.moveToPosition(position_list)

    import time

    time.sleep(5)
    translationstage.streamStackAcquisition_externalTrigger_setup(1000, 5000000,0.5,0.5)
    time.sleep(3)

    position_list = [0, 0, 0]
    translationstage.moveToPosition(position_list)
    #translationstage.stream_csvFile()
    #translationstage.streamStackAcquisition(1000, 5000000)
    #translationstage.stream_csvFile()

    translationstage.close()