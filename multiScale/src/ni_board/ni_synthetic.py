
import numpy as np
import matplotlib.pyplot as plt

"""
TODO: One way or another, make it harder to forget the daq.close()
method, which can cause crazy voltages to persist. _del_? _enter_ and
_exit_? Try to do it better than we are.
Requires nicaiu.dll to be in the same directory, or located in the
os.environ['PATH'] search path.
If you get an error, google for NIDAQmx.h to decypher it.
"""


#todo- rewrite this so that you can specify in constants
#digital/analog, channel number, minVol, maxVol, name of channel, constant voltage or play

#todo - include a tool to make a single voltage output and not only the play voltage functionality

class Analog_Out:
    def __init__(
        self,
        num_channels='all',
        rate=1e4,
        verbose=True,
        daq_type='6733',
        line='Dev1/ao0',
        clock_name=None,
        minVol=0,
        maxVol=10,
        ):
        """Play analog voltages via a National Instruments analog-out DAQ board.
        """

        self.daq_type = daq_type

        if self.daq_type == 'synthetic':
            self.max_channels = 32
            self.max_rate = 1e6 #This is for 8 channels, otherwise 350 kS/s
            self.channel_type = 'analog'
            self.has_clock = True
        elif self.daq_type == 'synthetic_digital':
            # WARNING: See note about 6733_digital lines. Also note that there
            # are 8 digital lines on `port1`, but these are not "buffered". We
            # have not yet included any functionality for these lines.
            self.max_channels = 2
            self.max_rate = 10e6
            self.channel_type = 'digital'
            self.has_clock = False
        elif self.daq_type == 'synthetic_constant':
            self.max_channels = 32
            self.max_rate = 1e6  # This is for 8 channels, otherwise 350 kS/s
            self.channel_type = 'constant'
            self.has_clock = True

        if num_channels == 'all':
            num_channels = self.max_channels
        assert 1 <= num_channels <= self.max_channels
        self.num_channels = num_channels
        if clock_name is not None:
            assert isinstance(clock_name, str)
            clock_name = bytes(clock_name, 'ascii')
        self.verbose = verbose


        if self.channel_type == 'analog':
            if self.verbose: print("Create %s-out board..." % self.channel_type)

        elif self.channel_type == 'digital':
            if self.verbose: print("Create %s-out board..." % self.channel_type)

        elif self.channel_type == 'constant':
            if self.verbose: print("Create %s-out board..." % self.channel_type)
            return None

        if self.verbose: print(" Board open.")
        dtype = {'digital': np.uint8, 'analog': np.float64}[self.channel_type]
        self.voltages = np.zeros((2, self.num_channels), dtype=dtype)
        # Play initial voltages with the internal clock
        if self.has_clock:
            self.clock_name = None
        else:
            self.clock_name = clock_name
        self.set_rate(rate)
        self._write_voltages(self.voltages)
        if self.has_clock:
            self.play_voltages(force_final_zeros=False, block=True)
        else:
            self.play_voltages(force_final_zeros=False, block=False)
        if clock_name is not None and self.has_clock: # Switch to external clock
            self.clock_name = clock_name
            self.set_rate(rate)
        return None

    def set_rate(self, rate):
        self._ensure_task_is_stopped()
        assert 0 < rate <= self.max_rate
        self.rate = float(rate)
        return None

    def set_verbose(self,verbosevalue=False):
        self.verbose=verbosevalue

    def play_voltages(
        self,
        voltages=None,
        force_final_zeros=True,
        block=True,
        ):
        """
        If voltage is None, play the previously set voltage.
        If 'force_final_zeros', the last entry of each channel of
        'voltages' is set to zero.
        If 'block', this function will not return until the voltages are
        finished playing. Not performant, but easier to reason about.
        NB: by default, play_voltages() blocks until the voltages finish
        playing. This makes it harder to accidentally code yourself into
        ugly race conditions, but it obviously makes it hard to do
        anything else while the board is playing voltages. Since
        we're just issuing a DLL call, it's easy for play_voltages() to
        return as soon as the voltage task has started playing. This is
        probably what you want! But easier to write bugs with.
        Regardless, if a previous voltage task is still playing, we have
        to wait for it to finish before we can start the next one.
        """
        self._ensure_task_is_stopped()
        if voltages is not None:
            self._write_voltages(voltages, force_final_zeros)
        if self.verbose: print("Playing voltages...")
        self._task_running = True
        if block:
            self._ensure_task_is_stopped()
        return None

    def close(self):
        if self.verbose: print("Setting voltages to zero")
        if self.verbose: print(" %s board is closed." % self.daq_type)
        return None


    def setconstantvoltage(self, voltage):
        # Writes a floating-point sample to a task that contains a single analog output channel.
        if self.verbose: print("Set constant voltage to: " + str(voltage))

    def s2p(self, seconds):
        '''Convert a duration in seconds to a number of AO "pixels."
        Frequently I know how many seconds I want to play a voltage for,
        and I do simple math to convert this to how many "pixels" of
        voltage I should use on the analog out card to get this many
        seconds. Frequently I get this math wrong. That's why I wrote
        this function.
        '''
        num_pixels = int(round(self.rate * seconds))
        return num_pixels

    def p2s(self, num_pixels):
        '''Convert a  number of AO "pixels to a duration in seconds."
        Frequently I know how many "pixels" of voltage I'm playing on
        the analog out card, and I do simple math to convert this to how
        many seconds I'm playing that voltage for. Frequently I get this
        math wrong. That's why I wrote this function.
        '''
        seconds = num_pixels / self.rate
        return seconds

    def s2s(self, seconds):
        '''Calculate nearest duration the AO card can exactly deliver.
        This function rounds a time (in seconds) to the nearest time
        that the AO card can exactly deliver via an integer number of
        "pixels". For example, maybe you'd like to play a 10 millisecond
        pulse of voltage, but the AO rate is set to 300; how many
        "pixels" should we expect the AO card play for?
        '''
        seconds = self.p2s(self.s2p(seconds))
        return seconds

    def _ensure_task_is_stopped(self):
        return None

    def _write_voltages(self, voltages, force_final_zeros=True):
        assert len(voltages.shape) == 2
        assert voltages.dtype == self.voltages.dtype
        assert voltages.shape[0] >= 2
        assert voltages.shape[1] == self.num_channels
        if force_final_zeros:
            if self.verbose:
                print("***Coercing voltages to end in zero!***")
            voltages[-1, :] = 0
        old_voltages_shape = self.voltages.shape
        self.voltages = voltages
        if self.voltages.shape[0] != old_voltages_shape[0]:
            self.set_rate(self.rate)

        print("writing voltages")
        return None

    def plot_voltages(self, volts, names):
        # Reverse lookup table; channel numbers to names:
        for c in range(volts.shape[1]):
            plt.plot(volts[:, c], label=names[c])
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        xlocs, xlabels = plt.xticks()
        plt.xticks(xlocs, [self.p2s(l) for l in xlocs])
        plt.ylabel('Volts')
        plt.xlabel('Seconds')
        plt.tight_layout()
        plt.show()

    def get_voltage_array(self,
                          exposure_time=0.05,
                          remote_low_vol = -2,
                          remote_high_vol = 2,
                          stage_triggertime=0.002,
                          delay_camera_trigger=0.002,  # how long does stage needs to move
                          camera_triggertime=0.002,
                          laser_line=3 #3 or higher
                          ):
        '''
        channels: stage trigger, remote mirror, TTL laser (4), camera trigger
        :returns Array with voltages for 0: stage, 1: camera trigger, 2: remote mirror
        '''

        assert laser_line>2, print("Choose parameter 3-7 for laser line")

        returnpoint = self.s2p(stage_triggertime + delay_camera_trigger)
        endpoint = self.s2p(stage_triggertime + delay_camera_trigger + camera_triggertime + exposure_time)

        # np.linspace(remote_low_vol, remote_low_vol, num = ao.s2p(exposure_time + 0.004)-ao.s2p(0.000))
        basic_unit = np.zeros((endpoint, 7), np.dtype(np.float64))

        # stage trigger
        basic_unit[0:self.s2p(stage_triggertime), 0] = 4

        # camera trigger
        basic_unit[self.s2p(stage_triggertime + delay_camera_trigger): self.s2p(
            stage_triggertime + delay_camera_trigger + camera_triggertime), 1] = 4

        #remote mirror
        basic_unit[0: returnpoint, 2] = np.linspace(remote_high_vol, remote_low_vol, num=returnpoint - self.s2p(0.000))
        basic_unit[returnpoint: endpoint, 2] = np.linspace(remote_low_vol, remote_high_vol, num=endpoint - returnpoint)

        basic_unit[self.s2p(stage_triggertime + delay_camera_trigger + camera_triggertime): self.s2p(
            stage_triggertime + delay_camera_trigger + camera_triggertime + exposure_time), laser_line] = 4  # laser trigger
        print(self.s2p(exposure_time + 0.004) - self.s2p(0.000))

        return basic_unit


if __name__ == '__main__':
##    6738 test block
    rate = 2e4
    do_type = 'synthetic_digital'
    do_name = 'Dev1'
    do_nchannels = 2
    do_clock = '/Dev1/ao/SampleClock'
    do = Analog_Out(
        num_channels=do_nchannels,
        rate=rate,
        daq_type=do_type,
        line= 'Dev1/port0/line0',
        clock_name=do_clock,
        verbose=True)

    ao_type = 'synthetic'
    ao_nchannels = 7
    line_selection = "Dev1/ao0, Dev1/ao5, Dev1/ao6, Dev1/ao8, Dev1/ao11, Dev1/ao14, , Dev1/ao18"
    ao = Analog_Out(
        num_channels=ao_nchannels,
        rate=rate,
        daq_type=ao_type,
        line= line_selection,
        verbose=True)
    digits = np.zeros((do.s2p(10), do_nchannels), np.dtype(np.uint8))
    volts = np.zeros((ao.s2p(10), ao_nchannels), np.dtype(np.float64))
    digits[do.s2p(.25):do.s2p(.75), :] = 1
    volts[ao.s2p(.25):ao.s2p(1), :] = 5
    volts[ao.s2p(2.5):ao.s2p(4), :] = 5
    volts[ao.s2p(8):ao.s2p(10), :] = 5


    basic_unit = ao.get_voltage_array()

    nb_frames = 5
    control_array = np.tile(basic_unit, (nb_frames, 1))
    print(control_array)
    ao.plot_voltages(control_array, ("ao0/stage", "ao5/camera", "ao6/remote mirror", "ao8/laser", "ao11", "ao14", "ao18"))

    #volts[ao.s2p(0.001):ao.s2p]
    #do.play_voltages(digits, force_final_zeros=True, block=False)
    #ao.play_voltages(volts, force_final_zeros=True, block=True)

    ao.play_voltages(control_array, force_final_zeros=True, block=True)

    ao_constant = Analog_Out(
        daq_type='synthetic_constant',
        line="Dev1/ao22",
        minVol=0,
        maxVol=5,
        verbose=True)

    ao_constant.setconstantvoltage(2)

    import time
    #time.sleep(4)
    print("closing")
    do.close()
    ao.close()
    ao_constant.close()
