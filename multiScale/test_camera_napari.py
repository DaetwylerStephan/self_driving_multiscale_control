
import concurrency_tools as ct
import numpy as np
import cv2

from pyvcam.camera import Camera
from napari_in_subprocess import display

import src.camera.Photometrics_camera as Photometricscamera


if __name__ == '__main__': #needed for threading of napari in subprocess
    camera = Photometricscamera.Photo_Camera('PMUSBCam00')

    testdisplay = display()

    out = np.ndarray(shape=(2048, 2048), dtype='uint16')

    camera.set_up_preview(exposure=20)

    while True:
        camera.run_preview(out)
        testdisplay.show_image(out)

        #frame['pixel_data'] = cv2.resize(frame['pixel_data'], dim, interpolation=cv2.INTER_AREA)
        #cv2.imshow('Live Mode', frame['pixel_data'])

        cv2.imshow('Live Mode', out)

        if cv2.waitKey(10) == 27:
            break