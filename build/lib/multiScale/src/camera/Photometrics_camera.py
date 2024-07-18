from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import time
import cv2
import numpy as np
import gc

class Photo_Camera:
    """
    This is the main class to control the Photometrics camera and call functions from the pyvcam / PyVCAM-master Python wrapper.

    Note:
    For the Photometrics camera to work, please go first to the PyVCAM-master folder and run:
    python setup.py install
    """

    def __init__(self, camera_name):
        """
        Initialize Photometrics camera class.

        :param camera_name: name of the camera. If you don't know it, PVCamTest displays it when running it.
        """
        pvc.init_pvcam()
        print("pvcam initialized")

        camera_names = Camera.get_available_camera_names()
        print('Available cameras: ' + str(camera_names))

        self.cam = Camera.select_camera(camera_name)
        print('start camera: ' + camera_name)
        print("camera detected")
        self.cam.open()
        print("camera open")

        self.cam.gain = 1

        return None

    def close(self):
        """
        Close the camera and un-initializes the PVCAM library.
        """
        self.cam.close()
        pvc.uninit_pvcam()
        print("camera closed")

    def get_imageroi(self):
        """
        Return the current region of interest / image shape of it.

        :return: shape of ROI of camera.
        """
        return self.cam.shape()

    def set_imageroi(self, s1, p1, w, h):
        """
        Configures and set a ROI on the camera.
        s2 = s1 + w - 1
        p2 = p1 + h - 1

        :param s1: starting point x (width)
        :param p1: starting point y (height)
        :param w: width of selected image ROI (how many columns)
        :param h: height of selected image ROI (how many rows)
        """
        self.cam.reset_rois()
        self.cam.set_roi(s1, p1, w, h)

    #############################
    #Preview functions
    #############################

    def set_up_lowres_preview(self, exposure=20):
        """
        Changes the settings of the low-resolution camera to start a preview.

        :param exposure_time: Exposure time for the current acquisition.
        """

        self.cam.exp_mode = "Internal Trigger"
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0
        self.cam.start_live(exp_time=exposure)

    def set_up_highrespreview(self, exposure=20):
        """
        Changes the settings of the high-resolution camera to start a high-resolution static (SPIM) preview.

        :param exposure_time: Exposure time for the current acquisition.
        """
        self.cam.exp_mode = "Internal Trigger"
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 1
        self.cam.gain = 1
        self.cam.prog_scan_mode = 0

        self.cam.start_live(exp_time=exposure)

    def init_previewbuffer(self, dimension1, dimension2):
        """
        Initialize a buffer to write images from the low-resolution preview function to.

        :param dimension1: dimension 1 of preview buffer (self.current_lowresROI_height)
        :param dimension2: dimension 2 of preview buffer (self.current_lowresROI_width)
        """
        self.previewbuffer = np.zeros([dimension1, dimension2], dtype="uint16")

    def run_preview_lowres(self):
        """
        Acquire and return a buffer image for the low-resolution preview.

        :return: acquired image
        """

        frame, fps, frame_count = self.cam.poll_frame()
        self.previewbuffer = np.copy(frame['pixel_data'][:])
        return self.previewbuffer


    def run_preview_highres(self, out, flipimage=True):
        """
        Acquire and return a buffer image for the high-resolution preview (SPIM and ASLM). Update buffer out

        :param out: buffer to update with acquired image
        :param flipimage: do you want to change the orientation of the image to display.
        """
        framesReceived = 0
        while framesReceived < 1:
            try:
                frame, fps, frame_count = self.cam.poll_frame()
                if flipimage == False:
                    out[:] = np.copy(frame['pixel_data'][:])
                else:
                    out[:] = np.flipud(np.copy(frame['pixel_data'][:]))
                framesReceived += 1
            except Exception as e:
                print(str(e))
                break

    def end_preview(self):
        """
        Finish preview imaging.
        """
        self.cam.finish()


    #############################
    #stack acquisition functions
    #############################

    def prepare_stack_acquisition_lowres(self, exposure_time=20):
        """
        Changes the settings of the low-resolution camera to start stack acquisitions.

        :param exposure_time: Exposure time for the current acquisition.
        """

        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time, buffer_frame_count=70)
        print("camera ready")

    def prepare_stack_acquisition_highres(self, exposure_time=20):
        """
        Changes the settings of the high-resolution camera to start stack acquisitions using static light-sheet imaging (SPIM).

        :param exposure_time: Exposure time for the current acquisition.
        """
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 1
        self.cam.readout_port = 0
        self.cam.gain = 1
        self.cam.prog_scan_mode = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")

    def prepare_ASLM_acquisition(self, exposure_time, scandelay):
        """
        Changes the settings of the high-resolution camera to start preview or stack acquisitions using axially-swept light-sheet microscopy.

        :param exposure_time: Exposure time for the current acquisition.
        :param scandelay: scan delay for ASLM.
        """

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

    def run_stack_acquisition_buffer_fast(self, nb_planes, buffer, flipimage=False):
        """
        Run a stack acquisition of low- or high-res imaging.

        :param nb_planes: how many planes to acquire
        :param buffer: the buffer to save the acquired planes to
        :param flipimage: (optional) True/False. If TRUE flip image
        """
        framesReceived = 0
        while framesReceived < nb_planes:
            try:
                frame, fps, frame_count = self.cam.poll_frame(timeout_ms=10000)

                if flipimage==True:
                    buffer[framesReceived, :, :] = np.flipud(np.copy(frame['pixel_data'][:]))
                else:
                    buffer[framesReceived, :, :] = np.copy(frame['pixel_data'][:])

                frame = None
                del frame
                framesReceived += 1

            except Exception as e:
                print(str(e))
                break

        self.cam.finish()
        return


if __name__ == '__main__':
    camera = Photo_Camera('PMUSBCam00')
    # camera = Photo_Camera('PMPCIECam00')

    camera.close()