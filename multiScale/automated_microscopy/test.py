from tifffile import imread, imwrite
import napari
import time
import numpy as np
import cv2
import copy


if __name__ == '__main__': #needed for threading of napari in subprocess
    print("start")
    t0 = time.perf_counter()
    filename= "D://multiScope_Data/20220606_Daetwyler_Xenograft/Experiment0009/t00000/low_stack000/1_CH488_000000.tif"
    imstack1 = imread(filename)
    print(imstack1.shape)
    print(imstack1.dtype)

    subarray = imstack1[60:62,1400:2000,1500:1900]
    t2 = time.perf_counter()
    for i in range(subarray.shape[0]):
        print(i)
        subarray[i] = np.flipud(subarray[i])
    t3 = time.perf_counter() - t2
    print("time stack flip" + str(t3))

    print(subarray.shape)
    maxproj_xy = np.max(subarray, axis=0)
    t1 = time.perf_counter() - t0
    print("time: " + str(t1))

    # cv2.imshow('maxproj', maxproj_xy)
    # cv2.waitKey(0)

    cv2.imwrite('D://test/test_zarr/maxProjtrad.tif', maxproj_xy)

    import zarr
    t0 = time.perf_counter()
    store = imread(filename, aszarr=True)
    z = zarr.open(store, mode='a')
    print(z[0].shape)
    subarray_zarr = copy.deepcopy(z[60:62, 1400:2000,1500:1900])
    maxproj_xy2 = np.max(subarray_zarr, axis=0)
    t1 = time.perf_counter() - t0
    print("time: " + str(t1))
    store.close()

    # cv2.imshow('maxproj2', maxproj_xy2)
    # cv2.waitKey(0)
    cv2.imwrite('D://test/test_zarr/maxProjzarr.tif', maxproj_xy2)


    #
    # print("The mean of the TIFF stack (whole stack!) is:")
    # # print(imstack1.mean())
    # #
    #with napari.gui_qt():
         # create the viewer with an image
         #viewer = napari.view_image(imstack1)
         #viewer = napari.view_image(z)

