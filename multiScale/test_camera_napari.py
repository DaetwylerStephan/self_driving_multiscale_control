
import concurrency_tools as ct
import numpy as np

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

