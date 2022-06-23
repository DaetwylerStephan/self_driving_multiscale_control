import numpy as np
from tifffile import imread, imwrite

class images_InMemory_class:
    def __init__(self):
        """
        This class is containing the images for calculations of drift correction, template matching and other smart microscopy
        """
        self.currentTP_lowResMaxProjection = []
        self.currentTP_highResMaxprojection = []
        self.previousTP_lowResMaxProjection = []
        self.previousTP_highResMaxProjection = []
        self.driftcorrection_transmissionImageList = []

    def addNewImage(self, whichlist, PosNumber, image):
        """
        add an Image newly to a list.
        :param whichlist: which list to add image - options: "current_lowRes_Proj", "previous_lowresProj",
                          "current_highRes_Proj", "previous_highRes_Proj", "transmission_ImageList"
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
        if whichlist == "transmission_ImageList":
            self.driftcorrection_transmissionImageList.append((PosNumber, image))


    def replaceImage(self, whichlist, PosNumber, image):
        """
        replace an Image with index PosNumber in the list "whichlist" with image.
        :param whichlist: which list to add image - options: "current_lowRes_Proj", "previous_lowresProj",
                          "current_highRes_Proj", "previous_highRes_Proj", "transmission_ImageList"
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
                temporaryimage = np.copy(imagelist[iter][1]) #copy so that it is not overwritten
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
            self.addNewImage(strcurrentlist, PosNumber, image)


if __name__ == '__main__':
    #load some images to assign and replace images.
    image_deposit = images_InMemory_class()
    img_lowrestrans_name = "D://test/drift_correctionTest/transmission/lowres_transmission.tif"
    img_lowrestrans = imread(img_lowrestrans_name)
    image_deposit.replaceImage("current_lowRes_Proj", 0, img_lowrestrans)
    print("next2")
    image_deposit.replaceImage("current_lowRes_Proj", 0, img_lowrestrans)
    print("next3")

    image_deposit.replaceImage("current_lowRes_Proj", 0, img_lowrestrans)


