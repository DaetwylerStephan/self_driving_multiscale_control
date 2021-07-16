


import concurrency_tools as ct
import numpy as np

from pyvcam.camera import Camera


import src.camera.Photometrics_camera as Photometricscamera

camera = Photometricscamera.Photo_Camera('PMUSBCam00')

out = np.ndarray(shape=(2, 2048, 2048), dtype='uint16')
out.fill(0)

camera.prepare_stack_acquisition(exposure_time=20)
camera.run_stack_acquisition_buffer(2, out)

print(out[0,1,1:10])


