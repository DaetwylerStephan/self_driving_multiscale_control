

import numpy as np

class Synthentic_cam_object:
    """
    The API of a synthetic camera object that returns random pictures around a median value.
    """

    def __init__(self, camera_name):
        """
        Initialize synthetic camera object

        :param camera_name: Determines initial "Chip size" (lowres_synthetic: (2960, 5056); else (2048, 2048)).
        """

        self.camera_name = camera_name
        if self.camera_name == "lowres_synthetic":
            self.shape_roi = (2960,5056)
        else:
            self.shape_roi = (2048, 2048)
        self.median_value = 200

    def close(self):
        """
        Close the synthetic camera.
        """
        pass

    def finish(self):
        "Finish acquisition in synthetic camera object"
        pass

    def open(self):
        "Open synthetic camera object"
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
    """
    This is the main class to control a synthetic camera object.
    """

    def __init__(self, camera_name):
        """
        Initialize synthetic camera class.

        :param camera_name: name of the camera.
        """
        print("Synthetic camera start")
        self.cam = Synthentic_cam_object(camera_name)
        print('start camera: ' + camera_name)
        self.cam.open()
        print("camera open")
        return None

    def close(self):
        """
        Close the synthetic camera.
        """
        self.cam.close()
        print("camera closed")

    def get_imageroi(self):
        """
        Return the current region of interest / image shape of it.

        :return: shape of ROI of camera.
        """
        return self.cam.shape()

    def set_imageroi(self, s1, p1, w, h):
        """
        Configures and set a ROI on the synthetic camera.

        :param s1: starting point x (width)
        :param p1: starting point y (height)
        :param w: width of selected image ROI (how many columns)
        :param h: height of selected image ROI (how many rows)
        """
        self.cam.reset_rois()
        self.cam.set_roi(s1, p1, w, h)

    #############################
    # Preview functions
    #############################

    def set_up_lowres_preview(self, exposure=20):
        """
        Prepare a low-resolution preview of the synthetic camera.

        :param exposure_time: Exposure time for the current acquisition.
        """
        self.cam.start_live(exp_time=exposure)

    def set_up_highrespreview(self, exposure=20):
        """
        Prepare a high-resolution static (SPIM) preview of the synthetic camera.

        :param exposure_time: Exposure time for the current acquisition.
        """
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
        self.previewbuffer = np.copy(frame)
        return self.previewbuffer

    def run_preview_highres(self, out, flipimage=True):
        """
        Acquire and return a buffer image for the synthetic high-resolution preview (SPIM and ASLM). Update buffer out.

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
        Prepare the settings of the low-resolution camera to start low-resolution stack acquisitions.

        :param exposure_time: Exposure time for the current acquisition.
        """
        self.cam.start_live(exp_time=exposure_time,  buffer_frame_count=70)
        print("camera ready")


    def prepare_stack_acquisition_highres(self, exposure_time=20):
        """
        Prepare the settings of the high-resolution camera to start stack acquisitions using static light-sheet imaging (SPIM).

        :param exposure_time: Exposure time for the current acquisition.
        """
        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")

    def prepare_ASLM_acquisition(self, exposure_time, scandelay):
        """
        Prepare the settings of the high-resolution camera to start preview or stack acquisitions using axially-swept light-sheet microscopy.

        :param exposure_time: Exposure time for the current acquisition.
        :param scandelay: scan delay for ASLM.
        """

        self.cam.start_live(exp_time=exposure_time)


    def run_stack_acquisition_buffer_fast(self, nb_planes, buffer, flipimage=False):
        """
        Run a stack acquisition of low- or high-res imaging.

        :param nb_planes: how many planes to acquire
        :param buffer: the buffer to save the acquired planes to
        :param flipimage: True/False. if TRUE flip image
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



if __name__ == '__main__':
    camera = Synthetic_Photo_Camera('PMUSBCam00')
    camera.cam.poll_frame()
    camera.getinfo()
    camera.close()