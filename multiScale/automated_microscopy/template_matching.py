# Python program to illustrate
# multiscaling in template matching
import cv2
import numpy as np
import imutils
import copy



class automated_templateMatching:
    def __init__(self):
       pass

    def simple_templateMatching(self, searchimage, template, scaling_factor, showimage=False):
        '''


        :param template: highres image which we want to find in the low-res / big image
        :param searchimage: the big image, in which we want to find the template
        :param scaling_factor: scaling of the highres image (template) to match image dimensions of low res image
        :param showimage: show image when executing template matching
        :return:
        '''

        #convert image to unit32 file type for OpenCV template matching algorithm
        template.astype(np.uint32)
        searchimage.astype(np.uint32)

        # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        #resize highres image to fit dimensions of low res image - in our case
        template_resized = imutils.resize(template, width=int(template.shape[1] * scaling_factor))
        (tH, tW) = template_resized.shape[:2]

        #initiate template matching
        found = None

        # Perform match operations with normalized correlation
        res = cv2.matchTemplate(searchimage, template_resized, cv2.TM_CCOEFF_NORMED)

        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)
        print(maxLoc)
        print(maxVal)

        # Specify a threshold
        threshold = 0.53035
        # Store the coordinates of matched area in a numpy array
        loc = np.where(res >= threshold)

        if showimage==True:
            # Draw a rectangle around the matched region.
            for pt in zip(*loc[::-1]):
                img_rgb = cv2.rectangle(searchimage, pt, (pt[0] + tW, pt[1] + tH), (0, 255, 255), 2)

            # Show the final image with the matched area.
            img_rgb = cv2.resize(img_rgb, (1011, 592))
            cv2.imshow('Detected', img_rgb)
            cv2.waitKey(0)

            cv2.imwrite('D://test/test_templatematching/template_result3.tif', img_rgb)

    def scaling_templateMatching(self, searchimage_sc, template_sc, scaling_factor, showimage=False):
        '''


        :param template: highres image which we want to find in the low-res / big image
        :param searchimage: the big image, in which we want to find the template
        :param scaling_factor: scaling of the highres image (template) to match image dimensions of low res image
        :param showimage: show image when executing template matching
        :return:
        '''

        #convert image to unit32 file type for OpenCV template matching algorithm
        template_sc.astype(np.uint32)
        searchimage_sc.astype(np.uint32)

        # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        #resize highres image to fit dimensions of low res image - in our case
        template_resized = imutils.resize(template_sc, width=int(template_sc.shape[1] * scaling_factor))
        (tH, tW) = template_resized.shape[:2]

        #initiate template matching
        found = None

        #######
        maxvalue =0
        for scale in np.linspace(0.9, 1.1, 11):
            #resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(template_resized, width=int(template_resized.shape[1] * scale))
            r = resized.shape[1] / float(template_resized.shape[1])
            print(r)
            # if the resized image is smaller than the template, then break
            # from the loop
            if searchimage_sc.shape[0] < tH or searchimage_sc.shape[1] < tW:
                break

            # matching to find the template in the image
            #edged = cv2.Canny(resized, 50, 200)
            res = cv2.matchTemplate(searchimage_sc, resized, cv2.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)
            # if we have found a new maximum correlation value, then update
            # the found variable if found is None or maxVal > found[0]:
            if maxVal > maxvalue:
                found = (maxVal, maxLoc, r)
                maxvalue = maxVal
                print("-----new value:------")
                print(maxvalue)

        # Store the coordinates of matched area in a numpy array
        loc = found[1]
        print(loc)
        if showimage==True:
            # Draw a rectangle around the matched region.
            print(tH, tW)
            img_rgb_sc = cv2.rectangle(searchimage_sc, loc, (loc[0] + tW, loc[1] + tH), (0, 255, 255), 2)

            # Show the final image with the matched area.
            img_rgb_sc = cv2.resize(searchimage_sc, (1011, 592))
            cv2.imshow('Detected', img_rgb_sc)
            cv2.waitKey(0)



if __name__ == '__main__':

    # Create class object:
    template_matchClass = automated_templateMatching()

    # Load the template image
    template = cv2.imread('D://test/test_templatematching/template.tif')
    templateHighres = cv2.imread('D://test/test_templatematching/template3.tif')

    # Load the search image
    img_gray = cv2.imread('D://test/test_templatematching/searchImage3.tif')

    scaling_factor = 11.11 / 55.55 * 6.5 / 4.25

    template_matchClass.simple_templateMatching(copy.deepcopy(img_gray), copy.deepcopy(templateHighres), scaling_factor, showimage=True)
    print("-------------scaled version--------------")
    template_matchClass.scaling_templateMatching(copy.deepcopy(img_gray), copy.deepcopy(templateHighres), scaling_factor, showimage=True)

