import numpy as np
import napari
from napari.qt import thread_worker
import time

with napari.gui_qt():
    viewer = napari.Viewer()

    # create the viewer with an image
    data = np.random.random((2048, 2060))
    layer = viewer.add_image(data)

    def update_layer(data):
        layer.data = data
        print(time.perf_counter())


    @thread_worker(connect={'yielded': update_layer})
    def create_data(*, update_period, num_updates):
        # number of times to update
        t0 = time.perf_counter()
        for k in range(num_updates):
            yield np.random.random((2048, 2060))
            time.sleep(update_period)
        t_end = time.perf_counter() - t0


    create_data(update_period=0.0, num_updates=100)

