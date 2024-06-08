

import numpy as np

class Synthentic_cam_object:
    def __init__(self, camera_name):
        self.camera_name = camera_name
        if self.camera_name == "lowres_synthetic":
            self.shape_roi = (2960,5056)
        else:
            self.shape_roi = (2048, 2048)
        self.gain = 1
        self.exp_mode = 'Edge Trigger'
        self.exp_out_mode = "Any Row"
        self.speed_table_index = 0
        self.median_value = 200
        self.readout_time = 20
        self.prog_scan_mode = 0
        self.prog_scan_mode = 1  # Scan mode options: {'Auto': 0, 'Line Delay': 1, 'Scan Width': 2}
        self.prog_scan_dir = 0  # Scan direction options: {'Down': 0, 'Up': 1, 'Down/Up Alternate': 2}
        self.prog_scan_line_delay = 11.2  # 11.2 us x factor, e.g. a factor = 6 equals 67.2 us

        # The   Line   Output   Mode   is   used   for   synchronization   purposes   when
        # uses   Programmable Scan mode. Line Output Mode creates a rising edge for each
        # row that the rolling shutter read out mechanism of the sensor advances
        self.exp_out_mode = 4

    def close(self):
        "close synthetic camera object"
        pass

    def finish(self):
        "finish acquisitoin synthetic camera object"
        pass

    def open(self):
        "open synthetic camera object"
        pass

    def reset_rois(self):
        "reset_rois"
        if self.camera_name == "lowres_synthetic":
            self.shape_roi = (2960, 5056)
        else:
            self.shape_roi = (2048, 2048)

    def set_roi(self, s1, p1, w, h):
        "set roi"
        self.shape_roi = (h, w)

    def start_live(self, exp_time, buffer_frame_count=70):
        "start acquisition"
        self.median_value = 100 + (exp_time) * 150
        pass

    def poll_frame(self, timeout_ms=10000):
        "generate random frame"
        return np.random.normal(self.median_value, 50, size=self.shape_roi).astype(np.uint16), 60, 1

    def shape(self):
        "return shape"
        return self.shape_roi


class Synthetic_Photo_Camera:

    def __init__(self, camera_name):
        print("Synthetic camera start")
        self.cam = Synthentic_cam_object(camera_name)
        print('start camera: ' + camera_name)
        self.cam.open()
        print("camera open")
        return None

    def close(self):
        self.cam.close()
        print("camera closed")

    def getinfo(self):
        print("Synthetic camera trigger table")

    def get_imageroi(self):
        return self.cam.shape()

    def set_imageroi(self, s1, p1, w, h):
        """
        s2 = s1 + w - 1
        p2 = p1 + h - 1
        :param s1:
        :param p1:
        :param w:
        :param h:
        :return:
        """
        self.cam.reset_rois()
        self.cam.set_roi(s1, p1, w, h)

    def prepare_stack_acquisition(self, exposure_time=20):
        """Changes the settings of the low res camera to start stack acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")


    def init_camerabuffer(self, nbplanes, width, height):
        self.camerabuffer = np.zeros([nbplanes, width, height], dtype="uint16")

    def init_camerabuffer2(self, buffer):
        self.camerabuffer = buffer

    def get_camerabuffer(self):
        print(self.camerabuffer.shape)
        return self.camerabuffer

    def init_previewbuffer(self, width, height):
        self.previewbuffer = np.zeros([width, height], dtype="uint16")

    def get_previewbuffer(self):
        return self.previewbuffer

    def prepare_stack_acquisition_highres(self, exposure_time=20):
        """Changes the settings of the highres camera to start stack acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 1
        self.cam.readout_port = 0
        self.cam.gain = 1
        self.cam.prog_scan_mode = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")


    def return_camera_readouttime(self):
        return self.cam.readout_time

    def prepare_ASLM_acquisition(self, exposure_time, scandelay):
        """Changes the settings of the camera to ASLM acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.speed_table_index = 1 # 1 for 100 MHz
        self.cam.readout_port = 0
        self.cam.gain = 1
        self.cam.prog_scan_mode = 1 # Scan mode options: {'Auto': 0, 'Line Delay': 1, 'Scan Width': 2}
        self.cam.prog_scan_dir = 0 # Scan direction options: {'Down': 0, 'Up': 1, 'Down/Up Alternate': 2}
        self.cam.prog_scan_line_delay = scandelay  # 11.2 us x factor, e.g. a factor = 6 equals 67.2 us

        #The   Line   Output   Mode   is   used   for   synchronization   purposes   when
        # uses   Programmable Scan mode. Line Output Mode creates a rising edge for each
        # row that the rolling shutter read out mechanism of the sensor advances
        self.cam.exp_out_mode = 4

        self.cam.start_live(exp_time=exposure_time)

    def prepare_stack_acquisition_seq(self, exposure_time=20):
        """Changes the settings of the low res camera to start stack acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time,  buffer_frame_count=70)
        print("camera ready")

    def run_stack_acquisition_buffer_fast(self, nb_planes, buffer, flipimage=False):
        """
        Run a stack acquisition.
        :param nb_planes: how many planes to acquire
        :param buffer: the buffer to save the acquired planes to
        :param flipimage - if TRUE flip image
        """
        framesReceived = 0
        while framesReceived < nb_planes:
            try:
                frame, fps, frame_count = self.cam.poll_frame(timeout_ms=10000)

                if flipimage==True:
                    buffer[framesReceived, :, :] = np.flipud(np.copy(frame))
                else:
                    buffer[framesReceived, :, :] = np.copy(frame)


                frame = None
                del frame

                framesReceived += 1

            except Exception as e:
                print(str(e))
                break

        self.cam.finish()
        return

    def run_stack_acquisition_buffer_pull(self):
        """Run a stack acquisition."""
        try:
            #fps, frame_count = self.cam.poll_frame2(out=buffer)
            frame, fps, frame_count = self.cam.poll_frame()
            return frame
        except Exception as e:
            print(str(e))
        return


    def set_up_lowres_preview(self, exposure=20):
        self.cam.exp_mode = "Internal Trigger"
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0
        self.cam.start_live(exp_time=exposure)

    def set_up_highrespreview(self, exposure=20):
        self.cam.exp_mode = "Internal Trigger"
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 1
        self.cam.gain = 1
        self.cam.prog_scan_mode = 0

        self.cam.start_live(exp_time=exposure)

    def run_preview(self, out, flipimage=False):
        frame, fps, frame_count = self.cam.poll_frame()
        if flipimage==False:
            out[:] = np.copy(frame)
        else:
            out[:] = np.flipud(np.copy(frame))


    def acquire_preview_tobuffer(self):
        frame, fps, frame_count = self.cam.poll_frame()
        self.previewbuffer = np.copy(frame)

    def run_preview_ASLM(self, out):
        framesReceived = 0
        print("in run_preview_ASLM: framesReceived started")
        while framesReceived < 1:
            try:
                frame, fps, frame_count = self.cam.poll_frame()
                out[:] = np.flipud(np.copy(frame))
                framesReceived += 1
                print("{}:{}".format(framesReceived, fps))
            except Exception as e:
                print(str(e))
                break

    def end_stackacquisition(self):
        self.cam.finish()

    def end_preview(self):
        self.cam.finish()


if __name__ == '__main__':
    camera = Synthetic_Photo_Camera('PMUSBCam00')
    camera.cam.poll_frame()
    camera.getinfo()
    camera.close()