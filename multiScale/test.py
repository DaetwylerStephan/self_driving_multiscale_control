
import src.ni_board.ni as ni
from constants import NI_board_parameters

# ### implement getchar() function for single character user input
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _GetchWindows()


class test_it:
    def __init__(self):
        self.names_to_voltage_channels = NI_board_parameters.names_to_voltage_channels
        print("Initializing ao card...", end=' ')
        self.ao = ni.Analog_Out(num_channels=30,
                        rate=1e5,
                        daq_type='6738',
                        board_name='Dev1',
                        verbose=True)
        print("done with ao.")

    def close(self):
        self.ao.close()

    def ManualMove(self):
        '''
        Use the _GetchWindows class to manually operate the voltage output from the command line.
        '''

        # // ----------------------------------------------------------------------------------
        while True:
            key = getch().decode("utf-8")
            if key == 'q':
                break
            if (key == 's'):

            if (key == '-'):

            if (key == '+'):

if __name__ == '__main__':
    # first code to run in the multiscope

     # Create scope object:
     test = test_it()