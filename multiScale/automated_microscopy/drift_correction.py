import numpy as np
import tkinter as tk
from tkinter import ttk
from tifffile import imread, imwrite
import os

import sys
sys.path.append('C://Users/Colfax-202008/PycharmProjects/ContextDriven_MicroscopeControl/multiScale')
from auxiliary_code.constants import Image_parameters

from pystackreg import StackReg
import pystackreg

from matplotlib import pyplot as plt
from skimage import transform, io, exposure

class drift_correction:
    def __init__(self, lowres_tree, highres_tree, filepath="path.txt"):
        #init it
        self.lowres_tree = lowres_tree
        self.highres_tree = highres_tree
        self.logfile = filepath

    def update_stagePosition(self):
        '''
        update stage position
        :return:
        '''

    def init_imageBuffer(self, lowres_x, lowres_y, highres_x, highres_y):
        '''
        init image buffer
        :return:
        '''

        for line in self.highres_tree.get_children():
            xpos = int(
                float(self.highres_tree.item(line)['values'][1]) * 1000000000)
            ypos = int(
                float(self.highres_tree.item(line)['values'][2]) * 1000000000)
            zpos = int(
                float(self.highres_tree.item(line)['values'][3]) * 1000000000)
            angle = int(
                float(self.highres_tree.item(line)['values'][4]) * 1000000)
            currentposition = [zpos, xpos, ypos, angle]
            print(currentposition)


    def calculate_drift_lowRes(self):
        '''
        calculate drift based on low resolution images.
        :return:
        '''

    def calculate_drift_highRes(self, xyview, xzview, yzview, previousimage, z_step, treeviewitem):
        '''
        calculate drift based on high resolution images from previous timepoint, and update tree
        :param xyview:
        :param xzview:
        :param yzview:
        :param previousimage: file path to previous time point image
        :return:
        '''

        #load timepoint
        isExist = os.path.exists(previousimage)
        if not isExist:
            print("Wanted to make drift correction to reference image that does not exist")
            return #return if file does not exist - e.g. for first timepoint

        ref = imread(previousimage)

        ref_xy = ref[0:xyview.shape[0], 0:xyview.shape[1]]
        ref_yz = ref[0:xyview.shape[0], xyview.shape[1]:]
        ref_xz = ref[xyview.shape[0]:, 0:xyview.shape[1]]

        assert ref_xy.shape == xyview.shape
        assert ref_yz.shape == yzview.shape
        assert ref_xz.shape == xzview.shape

        correctX1, correctY1 = self.register_image(ref_xy, xyview, 'translation')
        correctZ1, correctY2 = self.register_image(ref_yz, yzview, 'translation')
        correctX2, correctZ2 = self.register_image(ref_xz, xzview, 'translation')

        print(correctX1, correctX2, correctY1, correctY2, correctZ1, correctZ2)

        correctX_mm = (1/1000.) * Image_parameters.xy_pixelsize_highres_um * (correctX1 + correctX2)/2.
        correctY_mm = (1/1000.) * Image_parameters.xy_pixelsize_highres_um * (correctY1 + correctY2)/2.
        correctZ_mm = (1/1000.) * z_step * (correctZ1 + correctZ2)/2.

        correctionarray = [0, correctX_mm, correctY_mm, correctZ_mm, 0, 0]
        print(correctX_mm,correctY_mm, correctZ_mm)

        # print(self.highres_tree.item(treeviewitem)['values'])
        x = np.array([np.float(self.highres_tree.item(treeviewitem)['values'][0]),
                      np.float(self.highres_tree.item(treeviewitem)['values'][1]),
                      np.float(self.highres_tree.item(treeviewitem)['values'][2]),
                      np.float(self.highres_tree.item(treeviewitem)['values'][3]),
                      np.float(self.highres_tree.item(treeviewitem)['values'][4]),
                      np.float(self.highres_tree.item(treeviewitem)['values'][5])])
        y = np.array(correctionarray).astype(np.float)
        print("x:" + str(x))
        print("y:" + str(y))
        newposition = x + y
        print(newposition)

        self.highres_tree.item(treeviewitem, values=(float(newposition[0]), newposition[1], newposition[2], newposition[3], newposition[4], int(newposition[5])))
        tree_values1 = self.highres_tree.item(treeviewitem)['values']
        print(tree_values1)
        # zpos = int(float(self.highres_tree.item(treeviewitem)['values'][3]) * 1000000000)
        # print(zpos)
        # return correctX_mm, correctY_mm, correctZ_mm



    def calculate_drift_lowRes_complete(self, previousimage):
        '''
        checks if drift correction is complete for all regions.
                :return:
        '''

        # load timepoint
        isExist = os.path.exists(previousimage)
        if not isExist:
            print("Wanted to make drift correction to reference image that does not exist")
            return  # return if file does not exist - e.g. for first timepoint

        ref = imread(previousimage)

    def plot_registration(self, ref, mov):
        '''
        plot images
        :param ref: image 1
        :param mov: image 2
        :return: plots them and their overlay
        '''

        f, ax = plt.subplots(3, 1, figsize=(18, 40))

        before_reg = self.composite_images([ref, mov])

        ax[0].imshow(ref, cmap='gray')
        ax[0].set_title('reference image')
        ax[0].axis('off')

        ax[1].imshow(mov, cmap='gray')
        ax[1].set_title('shifted image')
        ax[1].axis('off')

        ax[2].imshow(before_reg)
        ax[2].set_title('overlay')
        ax[2].axis('off');
        plt.show(block='False')

    def register_image(self, ref, mov, mode):
        if mode=='rigid':
            sr = StackReg(StackReg.RIGID_BODY)
        else:
            sr = StackReg(StackReg.TRANSLATION)
        reg = sr.register_transform(ref,mov)
        xshift = sr.get_matrix()[0,2]
        yshift = sr.get_matrix()[1,2]
        #print(xshift, yshift)
        #self.plot_registration(ref,reg)
        return xshift, yshift

    def overlay_images(self, imgs, equalize=False, aggregator=np.mean):

        if equalize:
            imgs = [exposure.equalize_hist(img) for img in imgs]

        imgs = np.stack(imgs, axis=0)

        return aggregator(imgs, axis=0)

    def composite_images(self, imgs, equalize=False, aggregator=np.mean):

        if equalize:
            imgs = [exposure.equalize_hist(img) for img in imgs]

        imgs = [img / img.max() for img in imgs]

        if len(imgs) < 3:
            imgs += [np.zeros(shape=imgs[0].shape)] * (3 - len(imgs))

        imgs = np.dstack(imgs)

        return imgs





if __name__ == '__main__':

    #define trees as in GUI
    root = tk.Tk()
    stage_highres_savedPos_tree = ttk.Treeview(root, columns=("Position", "X", "Y", "Z", "Phi", "Label"),
                                               show="headings", height=9)
    stage_highres_savedPos_tree.heading("Position", text="Position")
    stage_highres_savedPos_tree.heading("X", text="X")
    stage_highres_savedPos_tree.heading("Y", text="Y")
    stage_highres_savedPos_tree.heading("Z", text="Z")
    stage_highres_savedPos_tree.heading("Phi", text="Angle")
    stage_highres_savedPos_tree.heading("Label", text="Label")

    stage_highres_savedPos_tree.column("Position", minwidth=0, width=55, stretch="NO", anchor="center")
    stage_highres_savedPos_tree.column("X", minwidth=0, width=100, stretch="NO", anchor="center")
    stage_highres_savedPos_tree.column("Y", minwidth=0, width=100, stretch="NO", anchor="center")
    stage_highres_savedPos_tree.column("Z", minwidth=0, width=100, stretch="NO", anchor="center")
    stage_highres_savedPos_tree.column("Phi", minwidth=0, width=100, stretch="NO", anchor="center")
    stage_highres_savedPos_tree.column("Label", minwidth=0, width=100, stretch="NO", anchor="center")

    tuples = [(1, 0, 0, 0, 0, 0)]
    index = iid = 1
    for row in tuples:
        stage_highres_savedPos_tree.insert("", index=1, iid=1, values=row)
        index = iid = index + 1

    #init class
    c = drift_correction(stage_highres_savedPos_tree, stage_highres_savedPos_tree)

    #load sample images
    #img0name = "D://test/drift_correctionTest/CH488/t00000.tif"
    #img1name = "D://test/drift_correctionTest/CH488/t00001.tif"
    img0name ="D://multiScope_Data//20220421_Daetwyler_Xenograft//Experiment0007//projections//high_stack_001//CH488///t00000.tif"
    img1name ="D://multiScope_Data//20220421_Daetwyler_Xenograft//Experiment0007//projections//high_stack_001//CH488///t00001.tif"

    img0 = imread(img0name)
    img1 = imread(img1name)
    # img0_cropXY = img0[0:1024, 0:2048]
    # img1_cropXY = img1[0:1024, 0:2048]
    # img0_cropXZ = img0[1024:, 0:2048]
    # img1_cropXZ = img1[1024:, 0:2048]
    # img0_cropYZ = img0[0:1024, 2048:]
    # img1_cropZY = img1[0:1024, 2048:]

    img0_cropXY = img0[0:2048, 0:2048]
    img1_cropXY = img1[0:2048, 0:2048]
    img0_cropXZ = img0[2048:, 0:2048]
    img1_cropXZ = img1[2048:, 0:2048]
    img0_cropYZ = img0[0:2048, 2048:]
    img1_cropZY = img1[0:2048, 2048:]

    # c.plot_registration(img0_cropXY, img1_cropXY)
    # c.plot_registration(img0_cropXZ, img1_cropXZ)
    # c.plot_registration(img0_cropYZ, img1_cropZY)

    #c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, "D://test/drift_correctionTest/CH488/t00000.tif", 0.3, 1)
    c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, img0name, 0.3, 1)

    #c.register_image(img0_crop,img1_crop,"translation")

