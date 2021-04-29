import numpy as np
import concurrency_tools as ct
import napari_in_subprocess as napari
import time
from tifffile import imread, imwrite
import threading

disklock = threading.Lock()
orderlist = []

def save_data(out, iter):
    disklock.acquire()
    orderlist.append(iter)
    t0 = time.perf_counter()
    #name = np.uniform(1,1000000)
    string = 'D:/acquisitions/testimage' + str(iter) + '.tif'
    imwrite(string, out)
    tend = time.perf_counter() - t0
    #print(str(iter) + ": " + str(tend))
    disklock.release()


if __name__ == '__main__':

    print("Shared")
    t0 = time.perf_counter()
    out = ct.SharedNDArray(shape=(1,200,200), dtype='uint16')
    tend = time.perf_counter() - t0
    print(tend)

    for i in range(10000):
        thread1 = ct.ResultThread(target=save_data, args=(out,i)).start()


    for i in range(len(orderlist)):
        assert orderlist[i]==i
    #thread1.get_result()