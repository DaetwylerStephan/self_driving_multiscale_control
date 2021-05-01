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

    def apply_preview_settings_Iris(self):
        """Changes the settings of the Iris camera to preview acquisitions."""
        self.cam.clear_mode = "Pre-Sequence"
        self.cam.exp_mode = "Timed"
        self.cam.readout_port = 0
        self.cam.speed_table_index = 0
        self.cam.gain = 1

    def run_stack_aquisition(self, nb_planes):
        """Changes the settings of the Iris camera to preview acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Rows"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live()

        framesReceived = 0

        while framesReceived < nb_planes:
            time.sleep(0.005)

            try:
                frame, fps, frame_count = self.cam.poll_frame()
                print('Count: {} FPS: {} First five pixels of frame: {}'.format(frame_count, round(fps, 2),
                                                                                frame['pixel_data'][0, 0:5]))
                framesReceived += 1
            except Exception as e:
                print(str(e))

        self.cam.finish()

    def prepare_stack_acquisition(self, exposure_time=20):
        """Changes the settings of the camera to stack acquisitions."""
        self.cam.exp_mode = 'Edge Trigger'
        self.cam.exp_out_mode = "Any Row"
        self.cam.speed_table_index = 0

        # Collect frames in live mode
        self.cam.start_live(exp_time=exposure_time)
        print("camera ready")

    def run_stack_acquisition_buffer(self, nb_planes, out):
        """Run a stack acquisition."""


        framesReceived = 0
        testvar =0

        print("******************cam ready***********************" + str(nb_planes))

        while framesReceived < nb_planes:
            time.sleep(0.004)

            try:
                fps, frame_count = self.cam.poll_frame2(out=out[framesReceived,:,:])
                #frame, fps, frame_count = self.cam.poll_frame()
                #print('Count: {} FPS: {} First five pixels of frame: {}'.format(frame_count, round(fps, 2),
                #                                                                frame['pixel_data'][0, 0:5]))
                #out[framesReceived, :, :] = frame['pixel_data'][:]

                framesReceived += 1
                print(framesReceived)
            except Exception as e:
                if testvar ==0:
                    testvar = 1
                    print(str(e))

        self.cam.finish()

    def apply_preview_settings_PrimeExpress(self):
        """Changes the settings of the Iris camera to preview acquisitions."""
        self.cam.exp_mode = "Timed"
        self.cam.readout_port = 0
        self.cam.speed_table_index = 0
        self.cam.gain = 1

    def set_up_preview(self, exposure=20):
        self.cam.start_live(exp_time=exposure)

    def run_preview(self, out):
        fps, frame_count = self.cam.poll_frame2(out)

    def end_preview(self):
        self.cam.finish()

    def preview_live(self):
        self.cam.start_live(exp_time=20)

        cnt = 0
        tot = 0
        t1 = time.time()
        start = time.time()
        width = 800
        height = int(self.cam.sensor_size[1] * width / self.cam.sensor_size[0])
        dim = (width, height)
        fps = 0

        while True:
            frame, fps, frame_count = self.cam.poll_frame()
            frame['pixel_data'] = cv2.resize(frame['pixel_data'], dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('Live Mode', frame['pixel_data'])

            low = np.amin(frame['pixel_data'])
            high = np.amax(frame['pixel_data'])
            average = np.average(frame['pixel_data'])

            if cnt == 10:
                t1 = time.time() - t1
                fps = 10 / t1
                t1 = time.time()
                cnt = 0
            if cv2.waitKey(10) == 27:
                break
            print('Min:{}\tMax:{}\tAverage:{:.0f}\tFrame Rate: {:.1f}\n'.format(low, high, average, fps))
            cnt += 1
            tot += 1

        self.cam.finish()


if __name__ == '__main__':
    camera = Photo_Camera('PMUSBCam00')
    # camera = Photo_Camera('PMPCIECam00')

    camera.take_snapshot(20)
    camera.getinfo()
    #camera.preview_live()
    camera.take_snapshot(20)
    camera.close()