from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import time
import cv2
import numpy as np


class Photo_Camera:
    def __init__(self, camera_name):
        pvc.init_pvcam()
        print("pvcam initialized")

        camera_names = Camera.get_available_camera_names()
        print('Available cameras: ' + str(camera_names))

        self.cam = Camera.select_camera(camera_name)
        print('start camera: ' + camera_name)
        print("camera detected")
        self.cam.open()
        print("camera open")
        return None

    def close(self):
        self.cam.close()
        pvc.uninit_pvcam()
        print("camera closed")

    def getinfo(self):
        print(self.cam.trigger_table)

    def getimagesize(self):
        self.cam.roi

    def take_snapshot(self, exposure):
        frame = self.cam.get_frame(exp_time=exposure).reshape(self.cam.sensor_size[::-1])
        plt.imshow(frame, cmap="gray")
        plt.show()

    def record(self, out, exposure=20):
        import numpy as np
        out[:] = self.cam.get_frame(exp_time=exposure).reshape(self.cam.sensor_size[::-1])


    def prepare_stack_acquisition(self, exposure_time=20):
        """Changes the settings of the camera to stack acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")

    def return_camera_readouttime(self):
        return self.cam.readout_time

    def run_stack_acquisition_buffer(self, nb_planes, buffer):
        """Run a stack acquisition."""
        framesReceived = 0
        while framesReceived < nb_planes:
            # time.sleep(0.001)

            try:
                fps, frame_count = self.cam.poll_frame2(out=buffer[framesReceived, :, :])
                framesReceived += 1
                print("{}:{}".format(framesReceived, fps))
            except Exception as e:
                print(str(e))
                break

        self.cam.finish()


    def set_up_preview(self, exposure=20):
        self.cam.exp_mode = "Internal Trigger"
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0
        self.cam.start_live(exp_time=exposure)

    def run_preview(self, out):
        fps, frame_count = self.cam.poll_frame2(out)

    def end_preview(self):
        self.cam.finish()


if __name__ == '__main__':
    camera = Photo_Camera('PMUSBCam00')
    # camera = Photo_Camera('PMPCIECam00')

    camera.take_snapshot(20)
    camera.getinfo()
    #camera.preview_live()
    camera.take_snapshot(20)
    camera.close()