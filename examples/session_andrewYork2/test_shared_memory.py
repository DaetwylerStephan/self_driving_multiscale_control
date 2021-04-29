import numpy as np
import concurrency_tools as ct
import napari_in_subprocess as napari
import time


if __name__ == '__main__':

    s = int(40e6)

    for i in range(0,10):
        print("Shared")
        t0 = time.perf_counter()
        out = ct.SharedNDArray(shape=s, dtype='uint16')
        tend = time.perf_counter() - t0
        print(tend)

        t0 = time.perf_counter()
        out.fill(0)
        tend = time.perf_counter() - t0
        print(tend)

        t0 = time.perf_counter()
        out.fill(7)
        tend = time.perf_counter() - t0
        print(tend)

        print("normal")

        t0 = time.perf_counter()
        out2 = np.ndarray(shape=s, dtype='uint16')
        tend = time.perf_counter() - t0
        print(tend)

        t0 = time.perf_counter()
        out2.fill(0)
        tend = time.perf_counter() - t0
        print(tend)

        t0 = time.perf_counter()
        out2.fill(7)
        tend = time.perf_counter() - t0
        print(tend)
