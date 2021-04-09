# Imports from the python standard library:
import time
import os
from datetime import datetime
import atexit
import queue

# Third party imports, installable via pip:
import numpy as np
from scipy.ndimage import zoom, rotate
from tifffile import imread, imwrite
# import matplotlib
# We only import matplotlib if/when we call Snoutscope._plot_voltages()

# Our stuff, from github.com/AndrewGYork/tools. Don't pip install.
# One .py file per module, copy files to your local directory.
try: # to allow snoutscope import for 'Pre' and 'Post' processors
    import pco # Install PCO's SDK to get relevant DLLs
    import ni # Install NI-DAQmx to get relevant DLLs
    import sutter
    import physik_instrumente as p_i
    import thorlabs
    import concurrency_tools as ct
    from napari_in_subprocess import display
except Exception as e:
    import traceback
    error = traceback.format_exc()
    print('Module import for Snoutscope failed with error:\n', error)

### TODO list: ###
# - Add a software autofocus option, it may not work for everyone, but will work
# for most
# - Expand Postprocessor() methods e.g: .auto_cropper()
# - Fix the spiral tile preview and find some way off allowing users to pick
# + move to a field of choice

# Snoutscope configuration (edit as needed):
M1 = 200 / 2; Mscan = 70 / 70; M2 = 5 / 357; M3 = 200 / 5
MRR = M1 * Mscan * M2; Mtot = MRR * M3;
camera_px_um = 6.5; sample_px_um = camera_px_um / Mtot
tilt = np.deg2rad(30)

class Snoutscope:
    def __init__(self, max_allocated_bytes): # Limit for machine
        # TODO: Check available system memory?
        self.unfinished_tasks = queue.Queue()
        slow_fw_init = ct.ResultThread(
            target=self._init_filter_wheel).start() #~5.3s
        slow_camera_init = ct.ResultThread(
            target=self._init_camera).start() #~3.6s
        slow_snoutfocus_init = ct.ResultThread(
            target=self._init_snoutfocus).start()#1s
        slow_focus_init = ct.ResultThread(
            target=self._init_focus_piezo).start() #~0.6s
        slow_stage_init = ct.ResultThread(
            target=self._init_XY_stage).start() #~0.4s
        self._init_display() #~1.3s
        self._init_preprocessor() #~0.8s
        self._init_ao() #~0.2s
        slow_stage_init.get_result()
        slow_focus_init.get_result()
        slow_snoutfocus_init.get_result()
        slow_camera_init.get_result()
        slow_fw_init.get_result()
        self.max_allocated_bytes = max_allocated_bytes
        self.max_bytes_per_buffer = (2**31) # Legal tiff
        self.max_data_buffers = 4 # Camera, preprocessor, display, filesave
        self.max_preview_buffers = 4 # Camera, preprocessor, display, filesave
        self.preview_line_px_width = 10 # line thickness for previews
        self.num_active_data_buffers = 0
        self.num_active_preview_buffers = 0
        print('Finished initializing Snoutscope')
        # Note: you still must call .apply_settings() before you can .acquire()

    def check_memory(
        self,
        channels_per_slice,
        roi,
        scan_step_size_px,
        slices_per_volume,
        volumes_per_buffer,
        max_data_buffers,
        max_preview_buffers,
        preview_line_px_width,
        ):
        # Data:
        ud_px = roi['bottom'] - roi['top'] + 1
        lr_px = roi['right'] - roi['left'] + 1
        img = (volumes_per_buffer * slices_per_volume * len(channels_per_slice))
        bytes_per_data_buffer = 2 * img * ud_px * lr_px
        assert bytes_per_data_buffer < self.max_bytes_per_buffer
        # Preview:
        p_shape = Preprocessor.three_traditional_projections_shape(
            slices_per_volume,
            ud_px,
            lr_px,
            scan_step_size_px,
            preview_line_px_width)
        bytes_per_preview_buffer = (2 * volumes_per_buffer *
                                    len(channels_per_slice) *
                                    int(np.prod(p_shape)))
        assert bytes_per_preview_buffer < self.max_bytes_per_buffer
        # Total:
        total_bytes = (bytes_per_data_buffer * max_data_buffers +
                       bytes_per_preview_buffer * max_preview_buffers)
        assert total_bytes < self.max_allocated_bytes
        return None

    def apply_settings(
        self,
        channels_per_slice=None, # Tuple of strings
        power_per_channel=None,  # Tuple of floats
        filter_wheel_position=None, # Int
        illumination_time_microseconds=None, # Float
        timestamp_mode=None, # String, see pco.py ._set_timestamp_mode()
        roi=None, # Dict, see pco.py ._set_roi()
        scan_step_size_px=None, # Int (or Float but be careful!)
        slices_per_volume=None,  # Int
        volumes_per_buffer=None, # Int
        focus_piezo_position_um=None, # Float or (Float, "relative")
        XY_stage_position_mm=None, # (Float, Float, optional: "relative")
        max_bytes_per_buffer=None, # Int
        max_data_buffers=None, # Int
        max_preview_buffers=None, # Int
        preview_line_px_width=None, # Int
        ):
        ''' Apply any settings to the scope that need to be configured before
            acquring an image. Think filter wheel position, stage position,
            camera settings, light intensity, calculate daq voltages, etc.'''
        args = locals()
        args.pop('self')
        def settings_task(custody):
            custody.switch_from(None, to=self.camera)
            # We own the camera, safe to change settings
            self._settings_are_sane = False # In case the thread crashes
            # Attributes must be set previously or currently:
            for k, v in args.items(): 
                if v is not None:
                    setattr(self, k, v) # A lot like self.x = x
                assert hasattr(self, k), (
                    'Attribute %s must be set by apply_settings()'%k)
            self.check_memory(self.channels_per_slice,
                              self.roi,
                              self.scan_step_size_px,
                              self.slices_per_volume,
                              self.volumes_per_buffer,
                              self.max_data_buffers,
                              self.max_preview_buffers,
                              self.preview_line_px_width)
            # Send hardware commands, slowest to fastest:
            if XY_stage_position_mm is not None:
                x, y = XY_stage_position_mm[0:2]
                if len(XY_stage_position_mm) > 2: # Relative motion?
                    assert XY_stage_position_mm[2] == "relative"
                    x0, y0 = self.XY_stage.get_position()
                    x, y = x0+x, y0+y
                self.XY_stage.move(x, y, blocking=False)
            if filter_wheel_position is not None:
                self.filter_wheel.move(filter_wheel_position,
                                       speed=6,
                                       block=False)
            if focus_piezo_position_um is not None:
                try: # Absolute position?
                    z = float(focus_piezo_position_um)
                except TypeError: # Relative position?
                    assert focus_piezo_position_um[1] == "relative"
                    z = (float(focus_piezo_position_um[0]) +
                         self.focus_piezo.get_real_position())
                self.focus_piezo.move(z) # nonblocking
            if (roi is not None or
                illumination_time_microseconds is not None or
                timestamp_mode is not None):
                self.camera.disarm()
                if roi is not None: self.camera._set_roi(roi)
                if (roi, illumination_time_microseconds) != (None, None):
                    self.camera._set_exposure_time(
                        self.illumination_time_microseconds +
                        self.camera.rolling_time_microseconds)
                if timestamp_mode is not None:
                    self.camera._set_timestamp_mode(timestamp_mode)
                self.camera.arm(16)
            self._calculate_voltages()
            # Finalize hardware commands, fastest to slowest:
            if focus_piezo_position_um is not None:
                self.focus_piezo._finish_moving()
                self.focus_piezo_position_um = ( # update attribute
                    self.focus_piezo.get_real_position())
            if filter_wheel_position is not None:
                self.filter_wheel._finish_moving()
            if XY_stage_position_mm is not None:
                self.XY_stage.finish_moving()
                self.XY_stage_position_mm = self.XY_stage.get_position()
            self._settings_are_sane = True
            custody.switch_from(self.camera, to=None)
        settings_thread = ct.CustodyThread(
            target=settings_task, first_resource=self.camera).start()
        self.unfinished_tasks.put(settings_thread)
        return settings_thread

    def acquire(self, display=True, filename=None, delay_seconds=None):
        if delay_seconds is not None and delay_seconds > 3:
            self.snoutfocus(delay_seconds=delay_seconds) # Might as well!
            delay_seconds = None
        def acquire_task(custody):
            def prepare_to_save_task(filename, delay_seconds):
                cwd = os.getcwd()
                folder, name = os.path.split(filename)
                data_directory = cwd + '\\' + folder + '\data'
                if not os.path.exists(data_directory):
                    os.makedirs(data_directory)
                data_path = data_directory + '\\' + name
                self._save_metadata(filename, delay_seconds, data_path)
                if display:
                    preview_directory = (cwd + '\\' + folder + '\preview')
                    if not os.path.exists(preview_directory):
                        os.makedirs(preview_directory)
                    preview_path = preview_directory + '\\' + name
                else:
                    preview_path = None
                return data_path, preview_path
            custody.switch_from(None, to=self.camera)
            if delay_seconds is not None:
                time.sleep(delay_seconds) # simple but not precise
            assert hasattr(self, '_settings_are_sane'), (
                'Please call .apply_settings() before using .acquire()')
            assert self._settings_are_sane, (
                'Did .apply_settings() fail? Please call it again, ' +
                'with all arguments specified.')
            if filename is not None:
                prepare_to_save_thread = ct.ResultThread(
                    target=prepare_to_save_task,
                    args=(filename, delay_seconds)).start()
            exposures_per_buffer = (len(self.channels_per_slice) *
                                    self.slices_per_volume *
                                    self.volumes_per_buffer)
            # Can we aviod writing the same voltages twice?
            write_voltages_thread = ct.ResultThread(
                target=self.ao._write_voltages, args=(self.voltages,)).start()
            data_buffer = self._get_data_buffer(
                (exposures_per_buffer, self.camera.height, self.camera.width),
                'uint16')
            write_voltages_thread.get_result()
            # camera.record_to_memory() blocks, so we use a thread:
            camera_thread = ct.ResultThread(
                target=self.camera.record_to_memory,
                args=(exposures_per_buffer,),
                kwargs={'out': data_buffer,
                        'first_trigger_timeout_seconds': 1},).start()
            # There's a race here. The PCO camera starts with N empty
            # single-frame buffers (typically 16), which are filled by
            # the triggers sent by ao.play_voltages(). The camera_thread
            # empties them, hopefully fast enough that we never run out.
            # So far, the camera_thread seems to both start on time, and
            # keep up reliably once it starts, but this could be
            # fragile.
            self.ao.play_voltages(block=False)
            ## TODO: consider finished playing all voltages before moving on...
            camera_thread.get_result()
            # Acquisition is 3D, but display and filesaving are 5D:
            data_buffer = data_buffer.reshape(self.volumes_per_buffer,
                                              self.slices_per_volume,
                                              len(self.channels_per_slice),
                                              data_buffer.shape[-2],
                                              data_buffer.shape[-1])
            if filename is not None:
                data_path, preview_path = prepare_to_save_thread.get_result()
            if display:
                # We have custody of the camera so attribute access is safe:
                scan_step_size_px = self.scan_step_size_px
                preview_line_px_width = self.preview_line_px_width
                skip_rows = 0
                if self.timestamp_mode != "off":
                    skip_rows = 8 # Ignore rows so timestamps don't dominate
                preview_me = data_buffer[:, :, :, skip_rows:, :]
                prev_shape = (
                    (self.volumes_per_buffer,
                     len(self.channels_per_slice),) +
                    Preprocessor.three_traditional_projections_shape(
                        self.slices_per_volume,
                        preview_me.shape[-2],
                        preview_me.shape[-1],
                        scan_step_size_px,
                        preview_line_px_width))
                custody.switch_from(self.camera, to=self.preprocessor)
                preview_buffer = self._get_preview_buffer(prev_shape, 'uint16')
                for vo in range(preview_me.shape[0]):
                    for ch in range(preview_me.shape[2]):
                        self.preprocessor.three_traditional_projections(
                            data_buffer[vo, :, ch, skip_rows:, :],
                            scan_step_size_px,
                            preview_line_px_width,
                            out=preview_buffer[vo, ch, :, :])
                custody.switch_from(self.preprocessor, to=self.display)
                self.display.show_image(preview_buffer)
                custody.switch_from(self.display, to=None)
                if filename is not None:
                    print("Saving file:", preview_path)
                    imwrite(preview_path, preview_buffer, imagej=True)
                self._release_preview_buffer(preview_buffer)
                del preview_buffer
            else:
                custody.switch_from(self.camera, to=None)
            # TODO: consider puting FileSaving in a SubProcess
            if filename is not None:
                print("Saving file:", data_path)
                imwrite(data_path, data_buffer, imagej=True)
            self._release_data_buffer(data_buffer)
        acquire_thread = ct.CustodyThread(
            target=acquire_task, first_resource=self.camera).start()
        self.unfinished_tasks.put(acquire_thread)
        return acquire_thread

    def _save_metadata(self, filename, delay_seconds, path):
        to_save = {
            'Date':datetime.strftime(datetime.now(),'%Y-%m-%d'),
            'Time':datetime.strftime(datetime.now(),'%H:%M:%S'),
            'filename':filename,
            'delay_seconds':delay_seconds,
            'channels_per_slice':self.channels_per_slice,
            'power_per_channel':self.power_per_channel,
            'filter_wheel_position':self.filter_wheel_position,
            'illumination_time_us':self.illumination_time_microseconds,
            'timestamp_mode':self.timestamp_mode,
            'roi':self.roi,
            'scan_step_size_px':self.scan_step_size_px,
            'scan_step_size_um':calculate_scan_step_size_um(
                self.scan_step_size_px),
            'slices_per_volume':self.slices_per_volume,
            'scan_range_um':calculate_scan_range_um(
                self.scan_step_size_px, self.slices_per_volume),
            'volumes_per_buffer':self.volumes_per_buffer,
            'focus_piezo_position_um':self.focus_piezo_position_um,
            'XY_stage_position_mm':self.XY_stage_position_mm,
            'preview_line_px_width':self.preview_line_px_width,
            'MRR':MRR,
            'Mtot':Mtot,
            'tilt':tilt,
            'sample_px_um':sample_px_um,
            'voxel_aspect_ratio':calculate_voxel_aspect_ratio(
                self.scan_step_size_px),
            }
        with open(os.path.splitext(path)[0] + '_metadata.txt', 'w') as file:
            for k, v in to_save.items():
                file.write(k + ': ' + str(v) + '\n')

    def snoutfocus(self, filename=None, delay_seconds=None):
        def snoutfocus_task(custody):
            custody.switch_from(None, to=self.camera) # safe to change settings
            if delay_seconds is not None:
                start_time = time.perf_counter()
                if delay_seconds > 3: # 3 seconds is def. enough time to focus
                    time.sleep(delay_seconds - 3)
            assert self._settings_are_sane, (
                'Did .apply_settings() fail? Please call it again, ' +
                'with all arguments specified.')
            self._settings_are_sane = False # In case the thread crashes
            # Record the settings we'll have to reset:
            old_filter_wheel_position = self.filter_wheel_position
            old_roi = self.camera.roi
            old_exp_us = self.camera.exposure_time_microseconds
            timestamp_mode = self.camera.timestamp_mode
            # Get microscope settings ready to take our measurement:
            self.filter_wheel.move(1, speed=6, block=False) # Empty slot
            self.snoutfocus_controller.set_voltage(
                0, block=False) # Slow, but filter wheel is slower
            self.camera.disarm()
            self.camera._set_roi({'left': 901, 'top': 901, # reduce for speed
                                  'right': 1160, 'bottom': 1148})
            self.camera._set_exposure_time(100) # Microseconds
            self.camera.arm(16)
            # Calculate voltages for the analog-out card:
            exp_pix = self.ao.s2p(1e-6*self.camera.exposure_time_microseconds)
            roll_pix = self.ao.s2p(1e-6*self.camera.rolling_time_microseconds)
            jitter_pix = max(self.ao.s2p(29e-6), 1) # Maybe as low as 27 us?
            piezo_settling_pix = self.ao.s2p(0.000) # Not yet measured
            period_pix = (max(exp_pix, roll_pix, piezo_settling_pix)
                          + jitter_pix)
            piezo_voltage_limit = 150 # 15 um for current piezo
            piezo_voltage_step = 2 # 200 nm steps
            n2c = self.names_to_voltage_channels # A temporary nickname
            voltages = []
            for piezo_voltage in np.arange(
                0, piezo_voltage_limit+piezo_voltage_step, piezo_voltage_step):
                v = np.zeros((period_pix, self.ao.num_channels), 'float64')
                v[:roll_pix, n2c['camera']] = 5
                v[:, n2c['snoutfocus_piezo']] = 10*(piezo_voltage /
                                                    piezo_voltage_limit) # 10 V
                voltages.append(v)
            exposures_per_buffer = len(voltages)
            voltages = np.concatenate(voltages, axis=0)
            # Allocate memory and finalize microscope settings:
            data_buffer = self._get_data_buffer(
                (exposures_per_buffer, self.camera.height, self.camera.width),
                'uint16') # TODO: effectively a min size for data buffers!
            self.snoutfocus_controller._finish_set_voltage()
            self.filter_wheel._finish_moving()
            # Take pictures while moving the snoutfocus piezo:
            camera_thread = ct.ResultThread(
                target=self.camera.record_to_memory,
                args=(exposures_per_buffer,),
                kwargs={'out': data_buffer,
                        'first_trigger_timeout_seconds': 1},).start()
            self.ao.play_voltages(voltages, block=False) # Ends at 0 V
            camera_thread.get_result()
            # Start cleaning up after ourselves:
            self.filter_wheel.move(old_filter_wheel_position,
                                   speed=6, block=False)
            # Inspect the images to find/set best snoutfocus piezo position:
            # Top rows might have timestamps
            if np.max(data_buffer[:,8:,:]) < 5 * np.min(data_buffer[:,8:,:]):
                print('WARNING: snoutfocus laser intensity is low:',
                      'is the laser/shutter powered up?')
            controller_voltage = piezo_voltage_step * np.unravel_index(
                np.argmax(data_buffer[:,8:,:]), data_buffer[:,8:,:].shape)[0]
            if (controller_voltage == 0 or
                controller_voltage == piezo_voltage_limit):
                print('WARNING: snoutfocus piezo is out of range!')
            self.snoutfocus_controller.set_voltage(
                controller_voltage, block=False)
            print('Snoutfocus piezo voltage =', controller_voltage)
            # Finish cleaning up after ourselves:
            self.camera.disarm()
            self.camera._set_roi(old_roi)
            self.camera._set_exposure_time(old_exp_us)
            self.camera.arm(16)
            self.snoutfocus_controller._finish_set_voltage()
            self.filter_wheel._finish_moving()
            self._settings_are_sane = True
            # We might want to hold camera custody for a fixed amount of time:
            if delay_seconds is not None:
                while time.perf_counter() - start_time < delay_seconds:
                    time.sleep(0.001)
            custody.switch_from(self.camera, to=None)
            if filename is not None:
                directory = (os.getcwd() + '\\' +
                             os.path.dirname(filename) + '\snoutfocus')
                if not os.path.exists(directory): os.makedirs(directory)
                path = directory + '\\' + os.path.basename(filename)
                print("Saving file:", path)
                imwrite(path, data_buffer[:, np.newaxis, :, :], imagej=True)
            self._release_data_buffer(data_buffer)
        snoutfocus_thread = ct.CustodyThread(
            target=snoutfocus_task, first_resource=self.camera).start()
        self.unfinished_tasks.put(snoutfocus_thread)
        return snoutfocus_thread

    def spiral_tiling_preview(
        self,
        num_spirals=1,
        dx_mm=0.1,
        dy_mm=0.1,
        ):
        ####################
        # WORK IN PROGRESS #
        ####################
        # TODO: xy, or yx? What's stage leftright vs. screen leftright?
        # If we get this straight, this code will suck less.
## TODO: - make sure stage is at max velocity and then return
        assert dx_mm and dy_mm < 1
        assert num_spirals < 4 # C'mon don't be silly, this is still a lot
        data_filename = "spiral_%02i_%02i.tif"
        preview_filename = "spiral_%02i_%02i_preview.tif"
        ix, iy = [0], [0] # Mutable, integer coords relative to starting tile
        acquire_tasks = []
        def move(x, y):
            ix[0], iy[0] = ix[0]+x, iy[0]+y
            self.apply_settings(
                XY_stage_position_mm=(dx_mm*x, dy_mm*y, "relative"))
            acquire_tasks.append(self.acquire(
                filename=data_filename%(ix[0]+num_spirals, iy[0]+num_spirals),
                display=True))
        def move_up():    move( 0,  1)
        def move_down():  move( 0, -1)
        def move_left():  move(-1,  0)
        def move_right(): move( 1,  0)
        move(0, 0) # get the central tile
        for which_spiral in range(num_spirals): # This took me a while...
            for i in range(1):
                move_up()
            for i in range(1 + 2*which_spiral):
                move_right()
            for i in range(2 + 2*which_spiral):
                move_down()
            for i in range(2 + 2*which_spiral):
                move_left()
            for i in range(2 + 2*which_spiral):
                move_up()
        self.apply_settings( # Return to original position
            XY_stage_position_mm=(-dx_mm*ix[0], -dy_mm*iy[0], "relative"))
        def display_preview_task(custody):
            # To preserve order we follow the same custody pattern as acquire():
            custody.switch_from(None, to=self.camera)
            custody.switch_from(self.camera, to=self.preprocessor)
            custody.switch_from(self.preprocessor, to=self.display)
            # You can't display until the preview files have saved to disk:
            for a in acquire_tasks: a.join()
            # Now you can start to reload the preview images:
            # TODO: re-try (with small delay) if file not found yet?
            first_tile = imread(preview_filename%(0, 0))
            ud_pix, lr_pix = first_tile.shape[-2:]
            preview_shape = list(first_tile.shape)
            preview_shape[-2] = ud_pix * (1 + 2*num_spirals)
            preview_shape[-1] = lr_pix * (1 + 2*num_spirals)
            # We're ready to hog some shared resources:
            # TODO: seriously consider adding spiral_preview_buffers to avoid
            # asking for memory that's not available
            preview_buffer = self._get_preview_buffer(preview_shape, 'uint16')
            preview_buffer[..., :ud_pix, :lr_pix] = first_tile
            for i in range(1 + 2*num_spirals):
                for j in range(1 + 2*num_spirals):
                    if (i, j) == (0, 0): continue # We already did this tile
                    preview_buffer[...,
                                   ud_pix*j:ud_pix*(j+1),
                                   lr_pix*i:lr_pix*(i+1)
                                   ] = imread(preview_filename%(i, j))
            self.display.show_image(preview_buffer)
            custody.switch_from(self.display, to=None)
            self._release_preview_buffer(preview_buffer)
        display_thread = proxy_objects.launch_custody_thread(
            target=display_preview_task, first_resource=self.camera)
        self.unfinished_tasks.put(display_thread)

    def finish_all_tasks(self):
        collected_tasks = []
        while True:
            try:
                th = self.unfinished_tasks.get_nowait()
            except queue.Empty:
                break
            th.get_result()
            collected_tasks.append(th)
        return collected_tasks

    def close(self, finish_all_tasks=True):
        if finish_all_tasks:
            self.finish_all_tasks()
        self.ao.close()
        self.filter_wheel.close()
        self.camera.close()
        self.snoutfocus_controller.close()
        self.focus_piezo.close()
        self.XY_stage.close()
        self.display.close()
        print('Closed Snoutscope')

    def _init_ao(self):
        self.names_to_voltage_channels = {
            'camera': 0,
            'galvo': 4,
            'snoutfocus_piezo': 6,
            'LED_power': 12, 
            '405_TTL': 16,
            '405_power': 17,
            '488_TTL': 20,
            '488_power': 21,
            '561_TTL': 24,
            '561_power': 25,
            '640_TTL': 28,
            '640_power': 29,}
        print("Initializing ao card...", end=' ')
        self.ao = ni.Analog_Out(num_channels=30,
                                rate=1e5,
                                daq_type='6739',
                                board_name='PXI1Slot2',
                                verbose=False)
        print("done with ao.")
        atexit.register(self.ao.close)

    def _init_filter_wheel(self):
        print("Initializing filter wheel...")
        self.filter_wheel = sutter.Lambda_10_3(which_port='COM3', verbose=False)
        print("done with filter wheel.")
        self.filter_wheel_position = 0
        atexit.register(self.filter_wheel.close)

    def _init_camera(self):
        print("Initializing camera... (this sometimes hangs)")
        self.camera = ct.ObjectInSubprocess(pco.Camera, verbose=False,
                                           close_method_name='close')
        self.camera.apply_settings(trigger='external_trigger')
        print("done with camera.")

    def _init_snoutfocus(self):
        print("Initializing snoutfocus piezo...")
        self.snoutfocus_controller = thorlabs.MDT694B_piezo_controller(
            which_port='COM7', verbose=False)
        print("done with snoutfocus piezo.")
        atexit.register(self.snoutfocus_controller.close)

    def _init_focus_piezo(self):
        print("Initializing focus piezo...")
        self.focus_piezo = p_i.E753_Z_Piezo(which_port='COM6', verbose=False)
        print("done with focus piezo.")
        atexit.register(self.focus_piezo.close)

    def _init_XY_stage(self):
        print("Initializing XY stage...")
        self.XY_stage = p_i.C867_XY_Stage(which_port='COM5', verbose=False)
        print("done with XY stage.")
        atexit.register(self.XY_stage.close)

    def _init_preprocessor(self):
        print("Initializing preprocessor...")
        self.preprocessor = ct.ObjectInSubprocess(Preprocessor)
        print("done with preprocessor.")

    def _init_display(self):
        print("Initializing display...")
        self.display = display()
        print("done with display.")

    def _calculate_voltages(self):
        # We'll use this a lot, so a short nickname is nice:
        n2c = self.names_to_voltage_channels
        # Input sanitization
        illumination_sources = ('LED', '405', '488', '561', '640',
                                '405_on_during_rolling')
        for channel in self.channels_per_slice:
            assert channel in illumination_sources
        assert len(self.channels_per_slice) > 0
        assert len(self.power_per_channel) == len(self.channels_per_slice)
        for power in self.power_per_channel:
            assert 0 <= power <= 100
        assert self.slices_per_volume == int(self.slices_per_volume)
        assert self.slices_per_volume > 0
        assert self.volumes_per_buffer == int(self.volumes_per_buffer)
        assert self.volumes_per_buffer > 0

        # Timing information
        exposure_pix = self.ao.s2p(1e-6*self.camera.exposure_time_microseconds)
        rolling_pix = self.ao.s2p(1e-6*self.camera.rolling_time_microseconds)

        jitter_pix = max(self.ao.s2p(29e-6), 1) # Maybe as low as 27 us?
        period_pix = max(exposure_pix, rolling_pix) + jitter_pix

        # Calculate scan_range_um and check limit:
        scan_range_um = calculate_scan_range_um(
            self.scan_step_size_px, self.slices_per_volume)
        assert 0 <= scan_range_um <= 200 # optical limit

        # Calculate galvo voltages from volume settings:
        galvo_volts_per_um = 4.5 / 110 # calibrated using graticule
        galvo_scan_volts = galvo_volts_per_um * scan_range_um
        galvo_voltages = np.linspace(-galvo_scan_volts/2,
                                     galvo_scan_volts/2,
                                     self.slices_per_volume)

        # Calculate voltages
        voltages = []
        for vo in range(self.volumes_per_buffer):
            # TODO: either bidirectional volumes, or smoother galvo flyback
            for sl in range(self.slices_per_volume):
                for ch, pw in zip(self.channels_per_slice,
                                  self.power_per_channel):
                    v = np.zeros((period_pix, self.ao.num_channels), 'float64')
                    # Camera trigger:
                    v[:rolling_pix, n2c['camera']] = 5 # falling edge->light on!
                    # Galvo step:
                    v[:, n2c['galvo']] = galvo_voltages[sl] # galvo
                    if channel in ('405_on_during_rolling',):
                        light_on_pix = 0
                    else:
                        light_on_pix = rolling_pix
                    # Illumination TTL trigger:
                    if ch != 'LED': # i.e. the laser channels
                        v[light_on_pix:period_pix - jitter_pix,
                          n2c[ch + '_TTL']] = 3
                    # Illumination power modulation:
                    v[light_on_pix:period_pix - jitter_pix,
                      n2c[ch + '_power']] = 4.5 * pw / 100
                    voltages.append(v)
        self.voltages = np.concatenate(voltages, axis=0)

    def _plot_voltages(self):
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

    def _get_data_buffer(self, shape, dtype):
        while self.num_active_data_buffers >= self.max_data_buffers:
            time.sleep(1e-3) # 1.7ms min
        data_buffer = ct.SharedNDArray(shape, dtype)
        self.num_active_data_buffers += 1
        return data_buffer

    def _release_data_buffer(self, shared_numpy_array):
        assert isinstance(shared_numpy_array, ct.SharedNDArray)
        self.num_active_data_buffers -= 1

    def _get_preview_buffer(self, shape, dtype):
        while self.num_active_preview_buffers >= self.max_preview_buffers:
            time.sleep(1e-3) # 1.7ms min
        preview_buffer = ct.SharedNDArray(shape, dtype)
        self.num_active_preview_buffers += 1
        return preview_buffer

    def _release_preview_buffer(self, shared_numpy_array):
        assert isinstance(shared_numpy_array, ct.SharedNDArray)
        self.num_active_preview_buffers -= 1

# Snoutscope definitions:
def calculate_scan_step_size_um(scan_step_size_px):
    return scan_step_size_px * sample_px_um / np.cos(tilt)

def calculate_scan_range_um(scan_step_size_px, slices_per_volume):
    scan_step_size_um = calculate_scan_step_size_um(scan_step_size_px)
    return scan_step_size_um * (slices_per_volume - 1)

def calculate_voxel_aspect_ratio(scan_step_size_px):
    return scan_step_size_px * np.tan(tilt)

def calculate_cuboid_voxel_scan(voxel_aspect_ratio, scan_range_um):
    scan_step_size_px = max(int(round(voxel_aspect_ratio / np.tan(tilt))), 1)
    scan_step_size_um = calculate_scan_step_size_um(scan_step_size_px)
    slices_per_volume = 1 + int(round(scan_range_um / scan_step_size_um))
    return scan_step_size_px, slices_per_volume # watch out for fencepost!

class Preprocessor:
    @staticmethod
    def three_traditional_projections_shape(
        scan_steps,
        prop_pxls,
        width_pxls,
        scan_step_size_px,
        preview_line_px_width,
        ):
        # Calculate max pixel shift for shearing on the prop. and scan axes:       
        scan_step_size_um = calculate_scan_step_size_um(scan_step_size_px)
        prop_pxls_per_scan_step = scan_step_size_um / (
            sample_px_um * np.cos(tilt))
        prop_px_shift_max = int(np.rint(
            prop_pxls_per_scan_step * (scan_steps - 1)))
        scan_steps_per_prop_px = 1 / prop_pxls_per_scan_step
        scan_px_shift_max = int(np.rint(
            scan_steps_per_prop_px * (prop_pxls - 1)))

        # Make image with all projections and flip for traditional view:
        x_pxls = width_pxls
        y_pxls = int(round(
            (prop_pxls + prop_px_shift_max) * np.cos(tilt)))
        z_pxls = int(round(prop_pxls * np.sin(tilt)))
        ln_pxls = preview_line_px_width
        shape = (y_pxls + z_pxls + 2*ln_pxls, x_pxls + z_pxls + 2*ln_pxls)
        return shape
        
    def three_traditional_projections(
        self,
        data,
        scan_step_size_px,
        preview_line_px_width,
        out=None,
        ):
        # TODO: consider allowing -ve scan for bi-directional scanning
        # Light-sheet scan, propagation and width axes:
        scan_steps, prop_pxls, width_pxls = data.shape

        # Calculate max pixel shift for shearing on the prop. and scan axes:
        scan_step_size_um = calculate_scan_step_size_um(scan_step_size_px)
        prop_pxls_per_scan_step = scan_step_size_um / (
            sample_px_um * np.cos(tilt))
        prop_px_shift_max = int(np.rint(
            prop_pxls_per_scan_step * (scan_steps - 1)))
        scan_steps_per_prop_px = 1 / prop_pxls_per_scan_step
        scan_px_shift_max = int(np.rint(
            scan_steps_per_prop_px * (prop_pxls - 1)))

        # Make projections:
        O1_proj = np.zeros((prop_pxls + prop_px_shift_max, width_pxls),
                           'uint16')
        scan_proj = np.zeros((prop_pxls, width_pxls), 'uint16')
        width_proj = np.zeros((scan_steps, prop_pxls), 'uint16')

        for i in range(scan_steps):
            prop_px_shift = int(np.rint(i * prop_pxls_per_scan_step))
            target = O1_proj[prop_px_shift:prop_pxls + prop_px_shift, :]
            np.maximum(target, data[i, :, :], out=target) # O1 
            np.maximum(scan_proj, data[i, :, :], out=scan_proj) # scan 
            np.amax(data[i, :, :], axis=1, out=width_proj[i, :]) # width

        # Unshear the width projection:
        unsheared_width_proj = np.zeros(
            (scan_steps + scan_px_shift_max, prop_pxls), 'uint16')
        for i in range(prop_pxls):
            scan_px_shift = int(np.rint(i * scan_steps_per_prop_px))
            unsheared_width_proj[
                scan_px_shift:scan_steps + scan_px_shift, i] = width_proj[:, i]

        # Scale images according to pixel size (divide by X_px_um):
        X_px_um = sample_px_um # width axis
        Y_px_um = sample_px_um * np.cos(tilt) # prop. axis to scan axis
        Z_px_um = sample_px_um * np.sin(tilt) # prop. axis to O1 axis
        O1_img = zoom(O1_proj,(Y_px_um / X_px_um, 1))
        scan_img = zoom(scan_proj,(Z_px_um / X_px_um, 1))
        scan_scale = O1_img.shape[0] / unsheared_width_proj.shape[0]
        # = scan_step_size_um / X_px_um rounded to match O1_img.shape[0]
        width_img = zoom(unsheared_width_proj,(scan_scale, Z_px_um / X_px_um))

        # Make image with all projections and flip for traditional view:
        y_pxls, x_pxls = O1_img.shape
        ln_px = preview_line_px_width # to keep lines of code short!
        ln_min, ln_max = O1_img.min(), O1_img.max()

        if out is None:
            out = np.zeros((y_pxls + scan_img.shape[0]  + 2*ln_px,
                            x_pxls + width_img.shape[1] + 2*ln_px), 'uint16')
            return_value = out
        else:
            return_value = None
        assert out.shape == (y_pxls + scan_img.shape[0]  + 2*ln_px,
                             x_pxls + width_img.shape[1] + 2*ln_px)
        out[ln_px:y_pxls + ln_px, ln_px:x_pxls + ln_px] = O1_img
        out[y_pxls + 2*ln_px:, ln_px:x_pxls + ln_px] = np.flipud(scan_img)
        out[ln_px:y_pxls + ln_px, x_pxls + 2*ln_px:] = np.fliplr(width_img)
        out[y_pxls + 2*ln_px:, x_pxls + 2*ln_px:] = np.full(
            (scan_img.shape[0], width_img.shape[1]), 0)

        # Add line separations between projections:
        out[:ln_px,    :] = ln_max
        out[:ln_px, ::10] = ln_min
        out[y_pxls + ln_px:y_pxls + 2*ln_px,    :] = ln_max
        out[y_pxls + ln_px:y_pxls + 2*ln_px, ::10] = ln_min

        out[:,    :ln_px] = ln_max
        out[::10, :ln_px] = ln_min
        out[:,    x_pxls + ln_px:x_pxls + 2*ln_px] = ln_max
        out[::10, x_pxls + ln_px:x_pxls + 2*ln_px] = ln_min

        out[:] = np.flipud(out)
        return return_value

class Postprocessor:
    # This method can be used for software autofocus. It uses an earlier
    # 'preview' image to estimate the z location of the sample. Choose:
    # - 'max_intensity' to track the brightest z pixel
    # - 'max_gradient' as a proxy for the coverslip boundary z pixel
    def estimate_sample_z_axis_px(
        self,
        preview_image, # single volume, single channel
        roi,
        timestamp_mode,
        preview_line_px_width,
        method='max_gradient',
        ):
        assert method in ('max_intensity', 'max_gradient')
        w_px = roi['right'] - roi['left'] + 1
        h_px = roi['bottom'] - roi['top'] + 1
        if timestamp_mode != "off": h_px = h_px - 8 # skip timestamp rows
        z_px = int(round(h_px * np.sin(tilt))) # Preprocessor definition
        inspect_me = preview_image[:z_px, preview_line_px_width:w_px]
        intensity_line = np.average(inspect_me, axis=1)[::-1] # O1 -> coverslip
        if method == 'max_intensity':
            return np.argmax(intensity_line)
        max_intensity = np.max(intensity_line)
        intensity_gradient = np.zeros((len(intensity_line) - 1))
        for px in range(len(intensity_line) - 1):
            intensity_gradient[px] = intensity_line[px + 1] - intensity_line[px]
            if intensity_line[px + 1] == max_intensity:
                break
        return np.argmax(intensity_gradient)
    
    # The native view is the most 'principled' view of the data for analysis
    # If scan_step_size_px == type(int) then no interpolation is needed to view
    # the volume. The native view looks at the sample with the 'tilt' of Snouty.
    def native_view(self, data, scan_step_size_px):
        # Light-sheet scan, propagation and width axes:
        scan_steps, prop_pxls, width_pxls = data.shape
        scan_step_px_max = int(np.rint(scan_step_size_px * (scan_steps - 1)))
        native_volume = np.zeros(
            (scan_steps, prop_pxls + scan_step_px_max, width_pxls), 'uint16')
        for i in range(scan_steps):
            prop_px_shift = int(np.rint(i * scan_step_size_px))
            native_volume[
                i, prop_px_shift:prop_pxls + prop_px_shift, :] = data[i,:,:]
        return native_volume

    # Very slow but pleasing - returns the traditional volume!
    def traditional_view(self, native_volume, voxel_aspect_ratio):
        native_volume_cubic_voxels = zoom(
            native_volume, (voxel_aspect_ratio, 1, 1))
        traditional_volume = rotate(
            native_volume_cubic_voxels, np.rad2deg(tilt))
        return traditional_volume

if __name__ == '__main__':
    ### Set variables: tzcyx acquisition ###
    ## filter wheel options:        0:blocked,      1:open
    # 2:ET450/50M,  3:ET525/50M,    4:ET600/50M,    5:ET690/50M
    # 6:ZETquadM,   7:empty         8:empty         9:empty

    # Scan: input user friendly options -> return values for .apply_settings()
    aspect_ratio = 2
    scan_range_um = 50
    scan_step_size_px, slices_per_volume = calculate_cuboid_voxel_scan(
        aspect_ratio, scan_range_um)
    
    # Camera chip cropping:
    crop_px_lr = 500
    crop_px_ud = 900 # max 1019
    roi = pco.legalize_roi({'left': 1 + crop_px_lr,
                            'right': 2060 - crop_px_lr,
                            'top': 1 + crop_px_ud,
                            'bottom': 2048 - crop_px_ud},
                           camera_type='edge 4.2', verbose=False)    

    # Create scope object:
    scope = Snoutscope(100e9) # Max memory bytes for PC
    scope.apply_settings( # Mandatory call
        channels_per_slice=("LED", "488"), # ('LED','405','488','561','640')
        power_per_channel=(50, 10), # (5,0,20,30,100) # 0-100% match to channels
        filter_wheel_position=3, # pick 1 position - see above options
        illumination_time_microseconds=100,
        timestamp_mode="off", # pick: "off", "binary", "binary+ASCII", "ASCII"
        roi=roi,
        scan_step_size_px=scan_step_size_px,
        slices_per_volume=slices_per_volume,
        volumes_per_buffer=1,
        focus_piezo_position_um=(0,'relative'),
        XY_stage_position_mm=(0,0,'relative'),
        ).join()

    # Run snoufocus and acquire:
    scope.snoutfocus()
    for i in range(2):
        scope.acquire(
            display=True,
            filename='test_images\%06i.tif'%i, # comment out to avoid
            delay_seconds=0
            )
##    scope.spiral_tiling_preview(num_spirals=1, dx_mm=0.01, dy_mm=0.01)
    scope.close()
