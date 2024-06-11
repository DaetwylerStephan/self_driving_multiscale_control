
'''
Synthetic rotation_stage.py
========================================
Script containing all functions to initialize and operate a synthetic rotation stage
'''

import time


class Synthetic_rotationstage:

    def __init__(self, locator):
        '''
        Initialize rotation stage parameters, and print out some parameters for debugging
        Input: locator address of the rotation stage, e.g. usb:id:3948963323
        Output: an initialized and connected stage.
        '''
        # initialize rotation stage
        self.angle = 0

    def ExitIfError(self, status):
        '''
        MCS controller error message parser.
        Input: status report of the stage
        Output: print an error message if applicable
        '''
        #init error_msg variable
        return

    def moveToAngle(self, angle):
        self.angle = angle
        print("move to angle: " + str(angle))

    def getAngle(self):
       print("angle: " + str(self.angle))

    def close(self):
        # /* At the end of the program you should release all opened systems. */
        print('stage closed')

if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'usb:id:3948963323'

    rotationstage = Synthetic_rotationstage(stage_id)
    rotationstage.moveToAngle(50)
    rotationstage.close()
