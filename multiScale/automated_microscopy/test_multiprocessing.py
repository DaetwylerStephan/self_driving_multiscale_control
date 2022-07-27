import multiprocessing as mp
import concurrency_tools as ct
from numba import njit

import time
from tifffile import imread, imwrite
import numpy as np
import cv2
import copy
import matplotlib.pyplot as plt


def parallel_maxproj(stack, axis_direction, lock, outputarray, position):
    maxproj_current = np.max(stack, axis=axis_direction)
    lock.acquire()
    outputarray[position,:,:] = maxproj_current
    lock.release()

@njit
def maxproj(stack):
   maxproj_xy = np.max(stack)
   return maxproj_xy

@njit
def maxproj_axis1(stack):
    stack1 = np.swapaxes(stack, 0, 1)
    maxproj_side1 = np.max(stack1)
    return maxproj_side1

@njit
def maxproj_axis2(stack):
    stack2 = np.swapaxes(stack, 0, 2)
    maxproj_side2 = np.max(stack2)
    return maxproj_side2

if __name__ == '__main__':

    #set test positions
    print("start")
    filename = "D://multiScope_Data/20220606_Daetwyler_Xenograft/Experiment0009/t00000/low_stack000/1_CH488_000000.tif"
    imstack1 = imread(filename)
    print(imstack1.shape)
    (axial, width, height) = imstack1.shape
    print(imstack1.dtype)


    t0 = time.perf_counter()
    stack1 = np.swapaxes(imstack1, 0, 1)
    maxproj_numpy = np.max(stack1, axis=0)
    t1 = time.perf_counter() - t0


    print("max projection time" + str(t1) + " " +  str(maxproj_numpy.shape))

    t0 = time.perf_counter()


    # #maxproj_numba = maxproj_axis1(imstack1)
    # stack_cur = np.swapaxes(imstack1, 0, 1)
    # print(stack_cur.shape)
    # maximg = maxproj(stack_cur)
    # t1 = time.perf_counter() - t0

    stack1 = np.swapaxes(imstack1, 0, 1)
    print(imstack1.shape)
    maximg = maxproj(imstack1)
    #maximg =maxproj_axis1(imstack1)

    print("max projection time numba" + str(t1) + " " + str(maximg.shape))


    #
    # lock = mp.Lock()
    # outputarray = np.zeros((2, width, height))
    # t0 = time.perf_counter()
    #
    # p1 = mp.Process(target=parallel_maxproj, args=(imstack1[0:int(axial/2),:,:], 0, lock, outputarray, 0 ))
    # p2 = mp.Process(target=parallel_maxproj, args=(imstack1[int(axial/2):,:,:], 0, lock, outputarray, 1))
    #
    #
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()
    # print("multiprocessing done")
    # maxproj2 = np.max(outputarray, axis=0)
    # t1 = time.perf_counter() - t0
     # print("max projection time2" + str(t1))
     #
     #
     # plt.imshow(maxproj2)


