from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import time
import cv2
import numpy as np


class Photo_Camera:
    def __init__(self):
        pvc.init_pvcam()
        print("pvcam initialized")
        self.cam = next(Camera.detect_camera())
        print("camera detected")
        self.cam.open()
        print("camera open")
        return None

    def close(self):
        self.cam.close()
        pvc.uninit_pvcam()
        print("camera closed")

    def take_snapshot(self, exposure):
        frame = self.cam.get_frame(exp_time=exposure).reshape(self.cam.sensor_size[::-1])
        plt.imshow(frame, cmap="gray")
        plt.show()

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
            frame = self.cam.get_live_frame().reshape(self.cam.sensor_size[::-1])
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('Live Mode', frame)

            low = np.amin(frame)
            high = np.amax(frame)
            average = np.average(frame)

            if cnt == 10:
                t1 = time.time() - t1
                fps = 10 / t1
                t1 = time.time()
                cnt = 0
            # esc-key
            if cv2.waitKey(10) == 27:
                break
            print('Min:{}\tMax:{}\tAverage:{:.0f}\tFrame Rate: {:.1f}\n'.format(low, high, average, fps))
            cnt += 1
            tot += 1

        self.cam.stop_live()
        print('Total frames: {}\nAverage fps: {}\n'.format(tot, (tot / (time.time() - start))))

if __name__ == '__main__':
    camera = Photometrics_Camera()
    camera.take_snapshot(20)
    camera.preview_live()
    camera.take_snapshot(20)
    camera.close()