


import concurrency_tools as ct
import numpy as np

from pyvcam.camera import Camera


import src.camera.Photometrics_camera as Photometricscamera

camera = Photometricscamera.Photo_Camera('PMPCIECam00')

out = np.ndarray(shape=(2, 2960, 5056), dtype='uint16')


camera.prepare_stack_acquisition()
camera.run_stack_acquisition_buffer(2, out)
