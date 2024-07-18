
import serial as Serial
import io as Io
import time


class LudlFilterwheel:

    """
    Class to control a 6-position Ludl filterwheel

    Needs a dictionary which combines filter designations and position IDs in the form: \n
    filters = {'405-488-647-Tripleblock' : 0, '405-488-561-640-Quadrupleblock': 1, '464 482-35': 2, '508 520-35': 3, '515LP':4,}

    Adapted from Ludl filter wheel control by Fabian Voigt. Check out:
    https://github.com/mesoSPIM/mesoSPIM-control/blob/master/mesoSPIM/src/devices/filter_wheels/mesoSPIM_FilterWheel.py

    """

    def __init__(self, COMport, filterdict, baudrate=9600):
        """
        Initialize Ludl filter wheel.

        :param COMport: COMport to connect to filter wheel.
        :param filterdict: Filter dictionary of mounted filters and their position.
        :param baudrate: Baudrate for connection.
        """

        print('Initializing Ludl Filter Wheel')
        self.COMport = COMport
        self.baudrate = baudrate
        self.filterdict = filterdict
        self.double_wheel = False

        self.wait_until_done_delay = 0.5 #Delay in s for the wait until done function

        self.first_item_in_filterdict = list(self.filterdict.keys())[0]


    def close(self):
        '''
        Close the Ludl filter wheel.
        '''

    def _check_if_filter_in_filterdict(self, filter):
        '''
        Checks if the filter designation (string) given as argument exists in the filterdict.

        :param filter: String, name of filter, e.g. '515-30-25'
        '''

        if filter in self.filterdict:
            return True
        else:
            raise ValueError('Filter designation not in the configuration')

    def set_filter(self, filter, wait_until_done=False):
        '''
        Moves filter wheel using the pyserial command set. No checks are done whether the movement is completed or
        finished in time.

        :param filter: String, name of filter, e.g. '515-30-25'
        :param wait_until_done: flag whether to wait a defined amount of time before returning
        '''
        if self._check_if_filter_in_filterdict(filter) is True:

            self.ser = Serial.Serial(self.COMport,
                                     self.baudrate,
                                     parity=Serial.PARITY_NONE,
                                     timeout=0,
                                     xonxoff=False,
                                     stopbits=Serial.STOPBITS_TWO)
            self.sio = Io.TextIOWrapper(Io.BufferedRWPair(self.ser, self.ser))

            # Get the filter position from the filterdict:
            self.filternumber = self.filterdict[filter]
            # Rotat is the Ludl high-level command for moving a filter wheel
            self.ludlstring = 'Rotat S M ' + str(self.filternumber) + '\n'
            self.sio.write(str(self.ludlstring))
            self.sio.flush()
            self.ser.close()

            if wait_until_done:
                """
                Wait a certain number of seconds. This is a hack.
                """
                time.sleep(self.wait_until_done_delay)

        else:
            print(f'Filter {filter} not found in configuration.')


if __name__ == '__main__':
    ##test here code of this class
    ComPort = 'COM6'
    filters = {'515-30-25': 0,
               '572/20-25': 1,
               '615/20-25': 2,
               '676/37-25': 3,
               'transmission': 4,
               'block': 5,
               }
    filterwheel_test = LudlFilterwheel(ComPort, filters)
    filterwheel_test.set_filter('515-30-25', wait_until_done=False)
    filterwheel_test.set_filter('572/20-25', wait_until_done=False)
    filterwheel_test.set_filter('615/20-25', wait_until_done=False)
    filterwheel_test.set_filter('676/37-25', wait_until_done=False)