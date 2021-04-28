import numpy as np
import concurrency_tools as ct
import napari
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


if __name__ == '__main__':

    list_images = []

    for i in range(0, 100):
        #out = ct.SharedNDArray(shape=(1, 2048, 2060), dtype='uint16')
        #out[:] = np.random.randint(0, 2 ** 16, size=(1, 2048, 2060), dtype='uint16')
        out = np.random.randint(0, 2 ** 16, size=(1, 2048, 2060), dtype='uint16')
        list_images.append(out)

    with napari.gui_qt():
        viewer = napari.Viewer()
        layer = viewer.add_image(list_images[0], name="im")

        #input("press enter")
        t_0 = time.perf_counter()


        imagecounter =0
        while True:
            time.sleep(00.0005)
            layer.data = list_images[imagecounter]
            imagecounter =imagecounter +1
            if imagecounter ==100:
                t_end = time.perf_counter() - t_0
                print(t_end)
                imagecounter=0
                t_0 = time.perf_counter()


