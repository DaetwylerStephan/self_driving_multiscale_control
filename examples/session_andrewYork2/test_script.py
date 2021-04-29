import numpy as np
import concurrency_tools as ct
import napari_in_subprocess as napari
import time

#not dominated by size of what is shown - seems limited to 20 fps

if __name__ == '__main__':
    display = napari.display()
    initialtime = time.perf_counter()
    list_images = []
    for i in range(0,100):
        out = ct.SharedNDArray(shape=(5, 2048, 2060), dtype='uint16')
        out[:] = np.random.randint(0, 2 ** 16, size=out.shape, dtype='uint16')
        list_images.append(out)

    endtime = time.perf_counter()-initialtime
    print(endtime)

    t0 = time.perf_counter()
    for image in list_images:
        display.show_image(image)
    tend = time.perf_counter()-t0

    print(tend)

    input("Press Enter to Close")
