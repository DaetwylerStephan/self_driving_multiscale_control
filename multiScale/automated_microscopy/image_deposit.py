import numpy as np
from tifffile import imread, imwrite
from matplotlib import pyplot as plt
import copy

class images_InMemory_class:
    def __init__(self):
        """
        This class is containing the images for calculations of drift correction, template matching and other smart microscopy
        """
        self.currentTP_lowResMaxProjection = []
        self.currentTP_highResMaxprojection = []
        self.previousTP_lowResMaxProjection = []
        self.previousTP_highResMaxProjection = []
        self.current_transmissionImageList = []
        self.previous_transmissionImageList = []


    def addNewImage(self, whichlist, PosNumber, image):
        """
        add an Image newly to a list.
        :param whichlist: which list to add image - options: "current_lowRes_Proj", "previous_lowresProj",
                          "current_highRes_Proj", "previous_highRes_Proj", "current_transmissionImage",
                          "previous_transmissionImage"
        :param PosNumber: the corresponding position number
        :param image:  the image to add
        :return: updated list in class
        """
        if whichlist == "current_lowRes_Proj":
            self.currentTP_lowResMaxProjection.append((PosNumber, image))
        if whichlist == "previous_lowresProj":
            self.previousTP_lowResMaxProjection.append((PosNumber, image))
        if whichlist == "current_highRes_Proj":
            self.currentTP_highResMaxprojection.append((PosNumber, image))
        if whichlist == "previous_highRes_Proj":
            self.previousTP_highResMaxProjection.append((PosNumber, image))
        if whichlist == "current_transmissionImage":
            self.current_transmissionImageList.append((PosNumber, image))
        if whichlist == "previous_transmissionImage":
            self.previous_transmissionImageList.append((PosNumber, image))

    def replaceImage(self, whichlist, PosNumber, image):
        """
        replace an Image with index PosNumber in the list "whichlist" with image.
        :param whichlist: which list to add image - options: "current_lowRes_Proj", "previous_lowresProj",
                          "current_highRes_Proj", "previous_highRes_Proj",  "current_transmissionImage",
                          "previous_transmissionImage"
        :param PosNumber: the corresponding position number
        :param image:  the image to add
        :return: updated list in class
        """
        if whichlist == "current_lowRes_Proj":
            self._updatelist(self.currentTP_lowResMaxProjection,
                             self.previousTP_lowResMaxProjection,
                             PosNumber, image, "current_lowRes_Proj", "previous_lowresProj")
        if whichlist == "current_highRes_Proj":
            self._updatelist(self.currentTP_highResMaxprojection,
                             self.previousTP_highResMaxProjection,
                             PosNumber, image, "current_highRes_Proj", "previous_highRes_Proj")
        if whichlist == "current_transmissionImage":
            print("update transmission image" + str(image.shape))
            self._updatelist(self.current_transmissionImageList,
                             self.previous_transmissionImageList,
                             PosNumber, image, "current_transmissionImage", "previous_transmissionImage")
        # if whichlist == "previous_highRes_Proj":
        #     self.previousTP_highResMaxProjection.append((PosNumber, image))
        # if whichlist == "transmission_ImageList":
        #     self.driftcorrection_transmissionImageList.append((PosNumber, image))

    def _updatelist(self, imagelist, previousimagelist, PosNumber, image, strcurrentlist, strpreviouslist):
        """
        helper function for replace image.
        :param imagelist: list to change
        :param previousimagelist: list of previous timepoint to change
        :param PosNumber: entry number
        :param image: image to update
        :param strcurrentlist: string to current list
        :param strpreviouslist: string to previous list
        :return:
        """
        found_image = 0

        #find entry in current image list, and update image in it
        for iter in range(len(imagelist)):
            if imagelist[iter][0] == PosNumber:
                found_image = 1
                temporaryimage = copy.deepcopy(imagelist[iter][1]) #copy so that it is not overwritten
                imagelist[iter] = (PosNumber, np.copy(image))

                #update previous time point list
                found_previous_image =0
                for iter2 in range(len(previousimagelist)):
                    if previousimagelist[iter2][0]==PosNumber:
                        previousimagelist[iter2] = (PosNumber, temporaryimage)
                        found_previous_image=1
                if found_previous_image==0: #if not found, add new image
                    self.addNewImage(strpreviouslist, PosNumber, temporaryimage)
        if found_image == 0:
            #print("add new image" + str(image.shape) + ":" + strcurrentlist)
            self.addNewImage(strcurrentlist, PosNumber, image)

    def image_retrieval(self, whichlist, PosNumber):
        """
        get an image from a list
        :param whichlist: which list to retrieve image - options: "current_lowRes_Proj", "previous_lowresProj",
                          "current_highRes_Proj", "previous_highRes_Proj",  "current_transmissionImage",
                          "previous_transmissionImage"
        :param PosNumber: what is the Position Number (PosNumber) associated with the image
        :return: image, or if image is not found returns an array with value zero: np.array([0]) for easy checking
        """
        if whichlist == "current_lowRes_Proj":
            try:
                returnimage = self.currentTP_lowResMaxProjection[PosNumber][1]
            except:
                returnimage = np.array([0])
        if whichlist == "previous_lowresProj":
            try:
                returnimage = self.previousTP_lowResMaxProjection[PosNumber][1]
            except:
                returnimage = np.array([0])
        if whichlist == "current_highRes_Proj":
            try:
                returnimage = self.currentTP_highResMaxprojection[PosNumber][1]
            except:
                returnimage = np.array([0])
        if whichlist == "previous_highRes_Proj":
            try:
                returnimage = self.previousTP_highResMaxProjection[PosNumber][1]
            except:
                returnimage = np.array([0])
        if whichlist == "current_transmissionImage":
            try:
                print("get transmission image")
                #todo - you need to search for the position Number!!! for loop over the entries...
                returnimage = self.current_transmissionImageList[PosNumber][1]
            except:
                returnimage = np.array([0])
        if whichlist == "previous_transmissionImage":
            try:
                returnimage = self.previous_transmissionImageList[PosNumber][1]
            except:
                returnimage = np.array([0])
        return returnimage

if __name__ == '__main__':

    #load some images to assign and replace images.
    image_deposit = images_InMemory_class()
    img_lowrestrans_name = "D://test/drift_correctionTest/transmission/lowres_transmission.tif"
    img_lowrestrans = imread(img_lowrestrans_name)
    img_crop_name = "D://test/drift_correctionTest/transmission/lowres_transmission_ROI.tif"
    img_crop = imread(img_crop_name)
    img_3 = "D://test/drift_correctionTest/transmission/lowres_transmission_found.tif"
    img_3 = imread(img_3)

    image_deposit.replaceImage("current_transmissionImage", 0, img_lowrestrans)
    image_deposit.replaceImage("current_transmissionImage", 1, img_3)
    image_deposit.replaceImage("current_transmissionImage", 2, img_lowrestrans)

    im1 = image_deposit.image_retrieval("current_transmissionImage", 1)
    im2 = image_deposit.image_retrieval("previous_transmissionImage", 1)

    f, ax = plt.subplots(2, 1, figsize=(18, 40))
    ax[0].imshow(img_lowrestrans, cmap='gray')
    ax[1].imshow(im1, cmap='gray')
    plt.show(block='False')

    image_deposit.replaceImage("current_transmissionImage", 0, img_crop)
    image_deposit.replaceImage("current_transmissionImage", 1, img_crop)
    image_deposit.replaceImage("current_transmissionImage", 2, img_crop)

    im3 = image_deposit.image_retrieval("current_transmissionImage", 1)
    im4 = image_deposit.image_retrieval("previous_transmissionImage", 1)
    print("next3")

    f, ax = plt.subplots(2, 1, figsize=(18, 40))
    ax[0].imshow(im3, cmap='gray')
    ax[1].imshow(im4, cmap='gray')
    plt.show(block='False')

    image_deposit.replaceImage("current_transmissionImage", 0, img_lowrestrans)
    image_deposit.replaceImage("current_transmissionImage", 1, img_3)
    image_deposit.replaceImage("current_transmissionImage", 2, img_lowrestrans)
    im1 = image_deposit.image_retrieval("current_transmissionImage", 1)
    im2 = image_deposit.image_retrieval("previous_transmissionImage", 1)

    f, ax = plt.subplots(2, 1, figsize=(18, 40))
    ax[0].imshow(im1, cmap='gray')
    ax[1].imshow(im2, cmap='gray')
    plt.show(block='False')


