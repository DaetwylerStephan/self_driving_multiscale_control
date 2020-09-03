# Imports from the python standard library:
import time
import atexit
import threading
import queue

# Third party imports, installable via pip:
import numpy as np
from tifffile import imwrite
# import matplotlib
# We only import matplotlib if/when we call Snoutscope.plot_voltages()

# Our stuff, from github.com/AndrewGYork/tools. Don't pip install.
# One .py file per module, copy files to your local directory.
import pco # Install PCO's SDK to get relevant DLLs
import ni # Install NI-DAQmx to get relevant DLLs
import asi_FW_1000
import proxy_objects
from proxied_napari import display

class Snoutscope:
    def __init__(self, bytes_per_buffer, num_buffers=1):
        """
        We use bytes_per_buffer to specify the shared_memory_sizes for the
        child processes.
        """
        # TODO: Think about an elegant solution for printing and threading
        self._init_shared_memory(bytes_per_buffer, num_buffers)
        self.unfinished_tasks = queue.Queue()
        slow_camera_init = threading.Thread(target=self._init_camera)
        slow_fw_init = threading.Thread(target=self._init_filter_wheel)
        slow_camera_init.start()
        slow_fw_init.start()
        self._init_display()
        self._init_ao()
        slow_camera_init.join()
        slow_fw_init.join()
        # Note: you still have to call .apply_settings() before you can .snap()

    def _init_shared_memory(self, bytes_per_buffer, num_buffers):
        """
        Each buffer is acquired in deterministic time with a single play
        of the ao card.
        """
        assert bytes_per_buffer > 0 and num_buffers > 0
        print("Allocating shared memory...", end=' ')
        self.pm = proxy_objects.ProxyManager(
            shared_memory_sizes=(bytes_per_buffer,) * num_buffers)
        print("done allocating memory.")
        self.data_buffer_queue = queue.Queue(
            maxsize=len(self.pm.shared_mp_arrays))
        for i in range(len(self.pm.shared_mp_arrays)):
            self.data_buffer_queue.put(i)

    def _init_ao(self):
        self.names_to_voltage_channels = {
            'camera':0,
            'galvo' :4,
            'LED_power':12, 
            '405_TTL':16,
            '405_power':17,
            '488_TTL':20,
            '488_power':21,
            '561_TTL':24,
            '561_power':25,
            '640_TTL':28,
            '640_power':29,}
        print("Initializing ao card...", end=' ')
        self.ao = ni.Analog_Out(num_channels=30,
                                rate=1e5,
                                daq_type='6739',
                                board_name='PXI1Slot2',
                                verbose=False)
        print("done with ao.")
        atexit.register(self.ao.close)

    def _init_camera(self):
        print("Initializing camera... (this sometimes hangs)")
        self.camera = self.pm.proxy_object(pco.Camera, verbose=False,
                                           close_method_name='close')
        print("done with camera.")

    def _init_filter_wheel(self):
        print("Initializing filter wheel...")
        self.filter_wheel = asi_FW_1000.FW_1000(which_port='COM8',
                                                which_wheels=(0,),
                                                verbose=True)
        print("done with filter wheel.")

    def _init_display(self):
        print("Initializing display...")
        self.display = display(proxy_manager=self.pm)
        print("done with display.")

    def apply_settings(
        self,
        roi=None,
        exposure_time_microseconds=None,
        volumes_per_buffer=None,
        slices_per_volume=None,
        channels_per_slice=None,
        power_per_channel=None,
        filter_wheel_position=None
        ):
        ''' Apply any settings to the scope that need to be configured before
            acquring an image. Think filter wheel position, stage position,
            camera settings, light intensity, calculate daq voltages, etc.'''
        # TODO: switch from setting exposure_time to setting illumination time
        # TODO: input sanitization
        args = locals()
        args.pop('self')
        def settings_task(custody):
            custody.switch_from(None, to=self.camera)
            # We own the camera, safe to change settings
            self._settings_are_sane = False # In case the thread crashes
            if filter_wheel_position is not None:
                self.filter_wheel.move(filter_wheel_position, block=False)
            if (roi is not None or
                exposure_time_microseconds is not None):
                self.camera.apply_settings(
                    trigger='external_trigger',
                    region_of_interest=roi,
                    exposure_time_microseconds=exposure_time_microseconds)
                self.camera._set_timestamp_mode("binary+ASCII")
                self.camera.arm(16)
            # Attributes must be set previously or currently:
            for k, v in args.items(): 
                if v is not None:
                    setattr(self, k, v) # A lot like self.x = x
                assert hasattr(self, k), (
                    'Attribute %s must be set by apply_settings()'%k)
            self._calculate_voltages()
            if filter_wheel_position is not None:
                self.filter_wheel._finish_moving()
            self._settings_are_sane = True
            custody.switch_from(self.camera, to=None)
        settings_thread = proxy_objects.launch_custody_thread(
            target=settings_task, first_resource=self.camera)
        self.unfinished_tasks.put(settings_thread)
        return settings_thread

    def _calculate_voltages(self):
        # We'll use this a lot, so a short nickname is nice:
        n2c = self.names_to_voltage_channels
        # Input sanitization
        illumination_sources = ('LED', '405', '488', '561', '640')
        for ch in self.channels_per_slice:
            assert ch in illumination_sources
        assert len(self.channels_per_slice) > 0
        for ch in illumination_sources:
            if ch in self.power_per_channel: # Ensure sane limits
                assert 0 <= self.power_per_channel[ch] <= 4.5
            else: # ...or else a sane default: small but nonzero.
                self.power_per_channel[ch] = 0.1
        assert self.slices_per_volume == int(self.slices_per_volume)
        assert self.slices_per_volume > 0
        assert self.volumes_per_buffer == int(self.volumes_per_buffer)
        assert self.volumes_per_buffer > 0

        # Timing information
        exposure_pix = self.ao.s2p(1e-6*self.camera.exposure_time_microseconds)
        rolling_pix = self.ao.s2p(1e-6*self.camera.rolling_time_microseconds)
        print('\nRolling time:', self.camera.rolling_time_microseconds, 'us')

        jitter_pix = max(self.ao.s2p(29e-6), 1) # Maybe as low as 27 us?
        period_pix = max(exposure_pix, rolling_pix) + jitter_pix
        print("Repetition time: %0.2f us"%(1e6*self.ao.p2s(period_pix)))

        # Calculate galvo voltages from volume settings:
        galvo_voltages = np.linspace(0, 2, self.slices_per_volume)

        # Calculate voltages
        voltages = []
        for vo in range(self.volumes_per_buffer):
            # TODO: either bidirectional volumes, or smoother galvo flyback
            for sl in range(self.slices_per_volume):
                for ch in self.channels_per_slice:
                    v = np.zeros((period_pix, self.ao.num_channels), 'float64')
                    # Camera trigger:
                    v[:rolling_pix, n2c['camera']] = 5 # falling edge->light on!
                    # Galvo step:
                    v[:, n2c['galvo']] = galvo_voltages[sl] # galvo
                    # Illumination TTL trigger:
                    if ch != 'LED': # i.e. the laser channels
                        v[rolling_pix:period_pix - jitter_pix,
                          n2c[ch + '_TTL']] = 3
                    # Illumination power modulation:
                    v[rolling_pix:period_pix - jitter_pix,
                      n2c[ch + '_power']] = self.power_per_channel[ch]
                    voltages.append(v)
        self.voltages = np.concatenate(voltages, axis=0)

    def plot_voltages(self):
        import matplotlib.pyplot as plt
        # Reverse lookup table; channel numbers to names:
        c2n = {v:k for k, v in self.names_to_voltage_channels.items()}
        for c in range(self.voltages.shape[1]):
            plt.plot(self.voltages[:, c], label=c2n.get(c, f'ao-{c}'))
        plt.legend(loc='upper right')
        xlocs, xlabels = plt.xticks()
        plt.xticks(xlocs, [self.ao.p2s(l) for l in xlocs])
        plt.ylabel('Volts')
        plt.xlabel('Seconds')
        plt.show()

    def snap(self, display=True, filename=None, delay_seconds=None):
        def snap_task(custody):
            custody.switch_from(None, to=self.camera)
            if delay_seconds is not None:
                time.sleep(delay_seconds) # simple but not precise
            assert hasattr(self, '_settings_are_sane'), (
                'Please call .apply_settings() before using .snap()')
            assert self._settings_are_sane, (
                'Did .apply_settings() fail? Please call it again.')
            exposures_per_buffer = (len(self.channels_per_slice) *
                                    self.slices_per_volume *
                                    self.volumes_per_buffer)
            data_buffer = self._get_data_buffer(
                (exposures_per_buffer, self.camera.height, self.camera.width),
                'uint16')
            # It would be nice if record_to_memory() wasn't blocking,
            # but we'll use a thread for now.
            camera_thread = threading.Thread(
                target=self.camera.record_to_memory,
                args=(exposures_per_buffer,),
                kwargs={'out': data_buffer,
                        'first_trigger_timeout_seconds': 4},)
            camera_thread.start()
            # There's a race here. The PCO camera starts with N empty
            # single-frame buffers (typically 16), which are filled by
            # the triggers sent by ao.play_voltages(). The camera_thread
            # empties them, hopefully fast enough that we never run out.
            # So far, the camera_thread seems to both start on time, and
            # keep up reliably once it starts, but this could be
            # fragile.
            self.ao.play_voltages(self.voltages, block=False)
            ## TODO: consider finished playing all voltages before moving on...
            camera_thread.join()
            # Acquisition is 3D, but display and filesaving are 5D:
            data_buffer = data_buffer.reshape(self.volumes_per_buffer,
                                              self.slices_per_volume,
                                              len(self.channels_per_slice),
                                              data_buffer.shape[-2],
                                              data_buffer.shape[-1])
            if display:
                custody.switch_from(self.camera, to=self.display)
                self.display.show_image(data_buffer)
                custody.switch_from(self.display, to=None)
            else:
                custody.switch_from(self.camera, to=None)
            # TODO: if file saving turns out to disrupt other activities
            # in the main process, make a FileSaving proxy object.
            if filename is not None:
                print("Saving file", filename, end=' ')
                imwrite(filename, data_buffer, imagej=True)
                print("done.")
            self._release_data_buffer(data_buffer)
            print('Finished snap task')
        snap_thread = proxy_objects.launch_custody_thread(
            target=snap_task, first_resource=self.camera)
        self.unfinished_tasks.put(snap_thread)
        return snap_thread

    def _get_data_buffer(self, shape, dtype):
        which_mp_array = self.data_buffer_queue.get()
        try:
            buffer = self.pm.shared_numpy_array(which_mp_array, shape, dtype)
        except ValueError as e:
            print("Your Snoutscope buffers are too small to hold a", shape,
                  "array of type", dtype)
            print("Either ask for a smaller array, or make a new Snoutscope",
                  " object with more 'bytes_per_buffer'.")
            raise e
        return buffer

    def _release_data_buffer(self, shared_numpy_array):
        assert isinstance(shared_numpy_array, proxy_objects._SharedNumpyArray)
        which_mp_array = shared_numpy_array.buffer
        self.data_buffer_queue.put(which_mp_array)

    def finish_all_tasks(self):
        collected_tasks = []
        while True:
            try:
                th = self.unfinished_tasks.get_nowait()
            except queue.Empty:
                break
            th.join()
            collected_tasks.append(th)
        return collected_tasks

if __name__ == '__main__':
    import time # to test performance
    # Set variables: tzcyx acquisition for now
    crop_pix_lr = 0
    crop_pix_ud = 0 # max 1019
    ch_per_slice = ["LED","405","LED"]
    pwr_per_ch = {"LED" : 2,}
    fw_pos = 3
    slices_per_vol = 5
    vol_per_buffer = 2 # hard coded as 1 vol for galvo
    num_buffers = 1
    # interbuffer time limited to ~2-4ms by ao play
    num_snap = 1 # interbuffer time is ~10-20ms with this setup
    exp_time_us = 50000

    # Calculate bytes_per_buffer for precise memory allocation:
    roi = pco.legalize_roi({'left': 1 + crop_pix_lr,
                            'right': 2060 - crop_pix_lr,
                            'top': 1 + crop_pix_ud,
                            'bottom': 2048 - crop_pix_ud},
                           camera_type='edge 4.2', verbose=False)
    w_px = roi['right'] - roi['left'] + 1
    h_px = roi['bottom'] - roi['top'] + 1
    images_per_buffer = vol_per_buffer * slices_per_vol * len(ch_per_slice)
    bytes_per_buffer = images_per_buffer * h_px * w_px * 2

    # Create scope object:
    scope = Snoutscope(bytes_per_buffer, num_buffers)
    scope.apply_settings( # Mandatory call
        roi=roi,
        exposure_time_microseconds=exp_time_us,
        volumes_per_buffer=vol_per_buffer,
        slices_per_volume=slices_per_vol,
        channels_per_slice=ch_per_slice,
        power_per_channel=pwr_per_ch,
        filter_wheel_position=fw_pos
        ).join()

    # Optionally, show voltages. Useful for debugging.
    scope.plot_voltages()

    # Start frames-per-second timer: acquire, display and save
    start = time.perf_counter()
    for i in range(num_snap):
        scope.snap(
            display=True,
            filename='test_images\%06i.tif'%i # comment out to aviod
            )

    # End timing when camera is released from snap and calculate fps
    # i.e. do not include display and file save etc. in fps timing
    def get_time(start, custody):
        custody.switch_from(None, to=scope.camera)
        end = time.perf_counter()
        custody.switch_from(scope.camera, to=None)
        num_images = images_per_buffer * num_snap
        print('frames=', num_images)
        print('time=', end-start)
        print('fps=', num_images/(end-start)) # up to 7700 (1 snap, >100k slices)
    t = proxy_objects.launch_custody_thread(
        target=get_time, first_resource=scope.camera, args=(start,))
    t.join()
    
    scope.finish_all_tasks()

    # predicted fps
    tot_ao_time = num_snap * scope.ao.p2s(scope.ao.voltages.shape[0])
    tot_buffer_time = num_snap * 0.01 # ~8-15 ms with this setup?
    max_fps = 7700
    predicted_fps = max_fps * (tot_ao_time / (tot_ao_time + tot_buffer_time))
    print('predicted fps ~', predicted_fps)
