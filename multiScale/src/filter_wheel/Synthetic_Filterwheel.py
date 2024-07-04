
import time


class Synthetic_Filterwheel:

    """
    Synthetic FilterWheel
    """

    def __init__(self, COMport, filterdict, baudrate=9600):
        print('Initializing Synthetic Filter Wheel')
        self.COMport = COMport
        self.baudrate = baudrate
        self.filterdict = filterdict

        ''' Delay in s for the wait until done function '''
        self.wait_until_done_delay = 0.5

        self.first_item_in_filterdict = list(self.filterdict.keys())[0]



    def close(self):
        '''
        Close the filter wheel
        '''
        pass

    def _check_if_filter_in_filterdict(self, filter):
        '''
        Checks if the filter designation (string) given as argument
        exists in the filterdict
        '''
        if filter in self.filterdict:
            return True
        else:
            raise ValueError('Filter designation not in the configuration')

    def set_filter(self, filter, wait_until_done=False):
        '''
        Moves and sets correct filter

        '''
        if self._check_if_filter_in_filterdict(filter) is True:
            print("set and move to filter position")
            if wait_until_done:
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
    filterwheel_test = Synthetic_Filterwheel(ComPort, filters)
    filterwheel_test.set_filter('515-30-25', wait_until_done=False)
    filterwheel_test.set_filter('572/20-25', wait_until_done=False)
    filterwheel_test.set_filter('615/20-25', wait_until_done=False)
    filterwheel_test.set_filter('676/37-25', wait_until_done=False)