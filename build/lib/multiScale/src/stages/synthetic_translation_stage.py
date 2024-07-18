'''
synthetic_translation_stage.py
========================================
Script containing all functions to initialize and operate a synthetic translation stage
'''

import sys
from threading import Event, Thread
import numpy as np




class Synthetic_translationstage:
    """
    Class to operate a synthetic translation stage system with 3 axes (XYZ).
    """

    def __init__(self):
        """
        Initialize the synthetic translation stage system (x,y,z positions) and stream events.
        """

        self.position_x = 0
        self.position_y = 0
        self.position_z = 0

        # initialize stream events
        self.stream_done = Event()
        self.stream_abort = Event()

        print("Synthetic translation stage initialized")

    def findReference(self):
        """
        Reference synthetic translation stage and set values to zero.
        """

        self.position_x = 0
        self.position_y = 0
        self.position_z = 0


    def close(self):
        """
        Close synthetic translation stage.
        """
        print("Synthetic translation stage closed.")


    def moveToPosition(self, position_list):
        """
        Move synthetic translation stage to new position.

        :param position_list: list of positions
        """
        self.position_x = position_list[0]
        self.position_y = position_list[1]
        self.position_z = position_list[2]

        print("move to: " + str( position_list[0]))
        print("move to: " + str( position_list[1]))
        print("move to: " + str( position_list[2]))

    def streamStackAcquisition_externalTrigger_setup(self, no_of_frames, increment, slow_velocity, slow_acceleration):
        """
        Set up synthetic translation stage into a waiting mode where it can be triggered to move stage by increment upon
        receiving triggers. Total number of triggers expected is no_of_frames.

        :param no_of_frames: How many external triggers are expected (number of images to acquire in stack acquisition).
        :param increment: How big one step is.
        :param slow_velocity: How fast the stage moves (slow_velocity * 10 mm/s).
        :param slow_acceleration: How fast the stage is accelerated (slow_acceleration * 100 mm/s2).
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
        """
        Wait for stream to finish.
        """
        # Wait for the "stream done" event.
        print("Stream finished.")
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
    time.sleep(2)
    translationstage.streamStackAcquisition_externalTrigger_setup(1000, 5000000,0.5,0.5)
    translationstage.streamStackAcquisition_externalTrigger_waitEnd()
    time.sleep(3)

    position_list = [3000000000, -2000000000, -8000000000]
    translationstage.moveToPosition(position_list)

    import time

    time.sleep(2)
    translationstage.streamStackAcquisition_externalTrigger_setup(1000, 5000000,0.5,0.5)
    translationstage.streamStackAcquisition_externalTrigger_waitEnd()
    time.sleep(3)

    position_list = [0, 0, 0]
    translationstage.moveToPosition(position_list)
    #translationstage.stream_csvFile()
    #translationstage.streamStackAcquisition(1000, 5000000)
    #translationstage.stream_csvFile()

    translationstage.close()