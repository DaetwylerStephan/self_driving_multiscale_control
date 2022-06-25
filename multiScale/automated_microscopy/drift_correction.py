import numpy as np
from tifffile import imread, imwrite
import os
import cv2
import copy
import sys
sys.path.append('C://Users/Colfax-202008/PycharmProjects/ContextDriven_MicroscopeControl/multiScale')
from auxiliary_code.constants import Image_parameters
from image_deposit import images_InMemory_class
from template_matching import automated_templateMatching

from pystackreg import StackReg
import pystackreg

from matplotlib import pyplot as plt
from skimage import transform, io, exposure

class drift_correction:
    def __init__(self, lowres_PosList, highres_PosList, lowres_zspacing, highres_zspacing, highresShape_x, highresShape_y, imageRepoLists, filepath="path.txt"):
        """
        :param lowres_PosList: the list of position of the low resolution imaging
        :param highres_PosList: the list of position of the high resolution imaging
        :param lowres_zspacing: the plane spacing of the low resolution stacks
        :param highres_zspacing: the plane spacing of the high resolution stacks
        :param highres_x: image size in x of highres image
        :param highres_y: image size in y of highres image
        :param filepath: (optional) filepath to logging the drift correction
        """
        #init it
        self.lowres_positionList = lowres_PosList
        self.highres_positionList = highres_PosList
        self.logfile = filepath
        self.scalingfactor = 11.11 / 4.25 *1000 #scalingfactor for how much one mm is in pixel on low res view
        self.scalingfactorLowToHighres = 11.11 / 55.55 * 6.5 / 4.25 #scalingfactor for high/low res camera views
        self.lowres_zspacing = lowres_zspacing
        self.highres_zspacing = highres_zspacing
        self.highres_x = highresShape_x
        self.highres_y = highresShape_y
        self.ImageRepo = imageRepoLists

        self.templatematching = automated_templateMatching()

    def calculate_drift_highRes(self, xyview, xzview, yzview, previousimage, z_step, PosNumber):
        '''
        calculate drift based on high resolution images from previous timepoint, and update position list
        :param xyview:
        :param xzview:
        :param yzview:
        :param previousimage: file path to previous time point image
        :param z_step:
        :param PosNumber: the entry list of the position
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

        x = self.highres_positionList[PosNumber]
        y = np.array(correctionarray).astype(np.float)
        #print("y:" + str(y))
        newposition = x + y
        #print(newposition)
        print("position list: " + str(self.highres_positionList))
        self.highres_positionList[PosNumber] = newposition

        print("position list updated: " + str(self.highres_positionList[PosNumber]))


    def find_closestLowResTile(self, PosNumber, return_number=False):
        '''
        find corresponding low resolution stack to selected high-res region (PosNumber).
        :param PosNumber: position of the highres view in the highres position list.
        :param return_number: if True, return number e.g. 1, if False return string for filename "low_stack000"
        :return: the corresponding file name of the low resolution stack which is closest to the high res stack.
        '''

        highrespoint = np.array(self.highres_positionList[PosNumber][1:4])
        angle = int(float(self.highres_positionList[PosNumber][4]))

        positioniter = -1
        positionnumber = -1
        dist = -1
        for lowresline in range(len(self.lowres_positionList)):
            positioniter = positioniter + 1

            # get current position from list

            angleLow = int(float(self.lowres_positionList[lowresline][4]))
            lowrespoint = np.array(self.lowres_positionList[lowresline][1:4])
            if angle==angleLow:
                dist_current = np.linalg.norm(highrespoint - lowrespoint)
                if dist == -1:
                    dist = dist_current
                    pos_label_line = "low_stack" + f'{positioniter:03}'
                    positionnumber = positioniter
                if dist > dist_current:
                    dist = dist_current
                    pos_label_line = "low_stack" + f'{positioniter:03}'
                    positionnumber = positioniter

        if return_number == False:
            return pos_label_line
        else:
            return positionnumber

    def calculate_drift_lowRes_complete(self, PosNumber, mode='fluorescence', firsttimepoint=False):
        '''
        calculates drift correction based on low res view.
        :param previousimage: to which previous image are you correcting to?
        :param PosNumber: which entry of the highres list are you trying to correct?
        :param mode: what drift correction are you running? e.g. on transmission image or fluorescence image
        :param firsttimepoint: is this the first time point, e.g. do you need to establish correspondances?
        :return:
        '''

        lateralId = 0
        UpDownID = 1
        AxialID = 2

        #transmission is different as there is no 1-to-1 correspondance between lowres and highres view. Therefore, one needs to first establish
        #an image of the region to follow. This image is saved in the image list
        if mode=="transmission":
            print('Use transmission image for drift correction')

            # retrieve corresponding high res image
            image_transmission = self.ImageRepo.image_retrieval("current_transmissionImage", PosNumber)
            print(image_transmission.shape)

            #establish the position of the first tile.
            if image_transmission.shape[0] < 2:
                print('Establish first corresponding transmission image')
                #find corresponding low resolution tile to high resolution image and get coordinates.
                lowstacknumber = self.find_closestLowResTile(PosNumber, return_number=True)
                coordinates_lowres = np.asarray(self.lowres_positionList[lowstacknumber][1:5])
                coordinates_highres = np.asarray(self.highres_positionList[PosNumber][1:5])

                #caclulate coordinate differences and scale them from mm to pixel values.
                coordinate_difference = coordinates_lowres - coordinates_highres
                coordinate_difference[lateralId] = coordinate_difference[lateralId] * self.scalingfactor
                coordinate_difference[UpDownID] = coordinate_difference[UpDownID] * self.scalingfactor

                #get low resolution image
                img_lowrestrans = self.ImageRepo.image_retrieval("current_lowRes_Proj", lowstacknumber)
                print("img_lowrestrans.shape:" + str(img_lowrestrans.shape))
                #get central pixel for low resolution stack
                loc = (int(img_lowrestrans.shape[0]/2), int(img_lowrestrans.shape[1]/2))

                #highres size in lowres:
                pixel_w_highresInLowres = int(self.scalingfactorLowToHighres * self.highres_x)
                pixel_h_highresInLowres = int(self.scalingfactorLowToHighres * self.highres_y)

                #calculate displacement
                loc = (int(loc[0]+ coordinate_difference[lateralId]-pixel_w_highresInLowres/2), int(loc[1] + coordinate_difference[UpDownID]-pixel_h_highresInLowres/2))

                print("first location" + str(loc))
                #retrieve region in lowres view of highres view
                corresponding_lowres_view = img_lowrestrans[loc[0]:(loc[0]+pixel_w_highresInLowres), loc[1]:(loc[1]+pixel_h_highresInLowres)]
                print("corr" + str(corresponding_lowres_view.shape))

                #assign the image to the image list
                print("length0:" + str(len(self.ImageRepo.current_transmissionImageList)))

                self.ImageRepo.replaceImage("current_transmissionImage", PosNumber, copy.deepcopy(corresponding_lowres_view))
                print("length1:" + str(len(self.ImageRepo.current_transmissionImageList)))
                print("listcontent0: " + str(self.ImageRepo.current_transmissionImageList[0][0]))
                print("listcontent1: " + str(self.ImageRepo.current_transmissionImageList[0][1]))

                testim = self.ImageRepo.image_retrieval("current_transmissionImage", PosNumber)
                print("testim " +str(PosNumber) + ":" + str(testim.shape))
                #cv2.imwrite('D://test//drift_correctionTest/transmission/lowres_transmission_ROI.tif', corresponding_lowres_view)

                # Show the final image with the matched area.
                # visualization
                # img_rgb_sc = cv2.rectangle(img_lowrestrans, (loc[1], loc[0]), (loc[1] + pixel_w_highresInLowres, loc[0] + pixel_h_highresInLowres), (0, 255, 255), 2)
                # cv2.imwrite('D://test//drift_correctionTest/transmission/lowres_transmission_found.tif', img_rgb_sc)
            else:
                # if not first time, take previous image and find corresponding image in translation image with template matching
                print("perform matching on transmission image")

                #get corresponding low res stack
                stacknumber = self.find_closestLowResTile(PosNumber, return_number=True)
                lowresstackimage = self.ImageRepo.image_retrieval("current_lowRes_Proj", stacknumber)

                f, ax = plt.subplots(2, 1, figsize=(18, 40))
                ax[0].imshow(lowresstackimage, cmap='gray')
                ax[1].imshow(image_transmission, cmap='gray')
                plt.show(block='False')

                self.templatematching.scaling_templateMatching(lowresstackimage, image_transmission, 1)


        #
        elif mode=="fluorescence":
            print("Use fluorescence image for drift correction")
        else:
            print("Use fluorescence image for drift correction")



    def transmission_make_selectedfirstmax(self, lowstackname, PosNumber):
        '''
        calculates drift correction based on low res view.
        :param lowstackname: name to closest lowrestack
        :param PosNumber: which entry of the highres list are you trying to correct?
        '''
        coordinateshighresstack = self.highres_positionList[PosNumber]


    def register_image(self, ref, mov, mode):
        """
        register two images (ref, mov) to each other using the StackReg
        :param ref: reference image
        :param mov: moving image
        :param mode: rigid (if mode=='rigid'), else translation
        :return: lateral (xshift, yshift)
        """
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

    #set test positions
    stage_PositionList = [ (1,1.13718, -24.69498, -1.0845, 0.0,0), (2, 0.5, 0.6, 0.7, 0),(2, 0.5, 0.6, 0.7, 4), (2, 0.5, 0.4, 0.7, 0)]
    stage_highres_PositionList = [(1, 1.2441, -24.69498, -1.00431, 0.0, 1), (2, 1.2441, -25.25631, -0.89739, 0.0, 2)]

    #load test images
    img_lowres_t0000 = "D://test/drift_correctionTest/transmission_timeseries/lowres_transmission_t0000.tif"
    img_lowres_t0001 = "D://test/drift_correctionTest/transmission_timeseries/lowres_transmission100pixel_t0001.tif"
    img_lowres_t0002 = "D://test/drift_correctionTest/transmission_timeseries/lowres_transmission200pixel_t0002.tif"
    img_lowrestrans = imread(img_lowres_t0000)
    img_lowres_t_t0000 = imread(img_lowres_t0000)
    img_lowres_t_t0001 = imread(img_lowres_t0001)
    img_lowres_t_t0002 = imread(img_lowres_t0002)

    #initialize image repository class and drift correction class
    imagerepoclass = images_InMemory_class()
    c = drift_correction(stage_PositionList, stage_highres_PositionList, 0.0035, 0.0003, 2048, 2048, imagerepoclass)

    #first acquisition
    c.ImageRepo.replaceImage("current_lowRes_Proj", 0, img_lowres_t_t0000)
    returnvalue = c.ImageRepo.image_retrieval("current_lowRes_Proj", 0)
    print("testoutside:" + str(returnvalue.shape))
    c.calculate_drift_lowRes_complete(1, mode='transmission')

    #second acquisition
    c.ImageRepo.replaceImage("current_lowRes_Proj", 0, img_lowres_t_t0001)
    c.calculate_drift_lowRes_complete(1, mode='transmission')

    # #third acquisition
    c.ImageRepo.replaceImage("current_lowRes_Proj", 0, img_lowres_t_t0002)
    c.calculate_drift_lowRes_complete(1, mode='transmission')

    #load sample images
    # img0name = "D://test/drift_correctionTest/CH488/t00000.tif"
    # img1name = "D://test/drift_correctionTest/CH488/t00001.tif"
    # # img0name ="D://multiScope_Data//20220421_Daetwyler_Xenograft//Experiment0007//projections//high_stack_001//CH488///t00000.tif"
    # # img1name ="D://multiScope_Data//20220421_Daetwyler_Xenograft//Experiment0007//projections//high_stack_001//CH488///t00001.tif"
    # #
    # img0 = imread(img0name)
    # img1 = imread(img1name)
    # img0_cropXY = img0[0:1024, 0:2048]
    # img1_cropXY = img1[0:1024, 0:2048]
    # img0_cropXZ = img0[1024:, 0:2048]
    # img1_cropXZ = img1[1024:, 0:2048]
    # img0_cropYZ = img0[0:1024, 2048:]
    # img1_cropZY = img1[0:1024, 2048:]
    #
    # img0_cropXY = img0[0:2048, 0:2048]
    # img1_cropXY = img1[0:2048, 0:2048]
    # img0_cropXZ = img0[2048:, 0:2048]
    # img1_cropXZ = img1[2048:, 0:2048]
    # img0_cropYZ = img0[0:2048, 2048:]
    # img1_cropZY = img1[0:2048, 2048:]
    #
    # c.plot_registration(img0_cropXY, img1_cropXY)
    # c.plot_registration(img0_cropXZ, img1_cropXZ)
    # c.plot_registration(img0_cropYZ, img1_cropZY)

    #c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, "D://test/drift_correctionTest/CH488/t00000.tif", 0.3, 0)
    # c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, "D://test/drift_correctionTest/CH488/t00000.tif", 0.3, 0)
    # c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, "D://test/drift_correctionTest/CH488/t00000.tif", 0.3, 0)
    # c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, "D://test/drift_correctionTest/CH488/t00000.tif", 0.3, 0)
    # #c.calculate_drift_highRes(img1_cropXY, img1_cropXZ, img1_cropZY, img0name, 0.3, 1)



    # pos = c.find_closestLowResTile(0)
    # print(pos)
    #
    # img_lowrestrans_name = "D://test/drift_correctionTest/transmission/lowres_transmission.tif"
    # img_lowres = imread(img_lowrestrans_name)
    # print(img_lowres.shape)
    # imagerepoclass.replaceImage("current_lowRes_Proj", 0, img_lowres)
    #
    # c.calculate_drift_lowRes_complete("D://test/drift_correctionTest/CH488/t00000.tif", 0, mode='transmission', firsttimepoint=True)
    #c.register_image(img0_crop,img1_crop,"translation")

