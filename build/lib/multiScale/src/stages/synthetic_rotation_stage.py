
'''
Synthetic rotation_stage.py
========================================
Script containing all functions to initialize and operate a synthetic rotation stage
'''

import time


class Synthetic_rotationstage:
    """
    Class to make and operate a synthetic rotation stage.
    """

    def __init__(self, locator):
        """
        Initialize a synthetic rotation stage.

        :param locator: Stage ID/address of the synthetic rotation stage.
        """

        # initialize rotation stage
        self.angle = 0
        self.stageid = locator

    def moveToAngle(self, angle):
        """
        Move to specific angle with synthetic rotation stage.

        :param angle: Angle to move to.
        """

        self.angle = angle
        print("move to angle: " + str(angle))

    def getAngle(self):
        """
        Print current angle of rotation stage.
        """

        print("angle: " + str(self.angle))

    def close(self):
        """
        Close synthetic rotation stage.
        """

        # /* At the end of the program you should release all opened systems. */
        print('stage closed')

if __name__ == '__main__':
    ##test here code of this class

    stage_id = 'syntheticstagename'
    rotationstage = Synthetic_rotationstage(stage_id)
    rotationstage.moveToAngle(50)
    rotationstage.close()
