# Python program to illustrate
# multiscaling in template matching
import cv2
import numpy as np
import imutils




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
        template_resized = imutils.resize(template, width=int(templateHighres.shape[1] * scaling_factor))
        (tH, tW) = template_resized.shape[:2]

        #initiate template matching
        found = None

        # Perform match operations with normalized correlation
        res = cv2.matchTemplate(searchimage, template_resized, cv2.TM_CCOEFF_NORMED)

        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)
        print(maxVal)

        # Specify a threshold
        threshold = 0.53035
        # Store the coordinates of matched area in a numpy array
        loc = np.where(res >= threshold)

        if showimage==True:
            # Draw a rectangle around the matched region.
            for pt in zip(*loc[::-1]):
                img_rgb = cv2.rectangle(img_gray, pt, (pt[0] + tW, pt[1] + tH), (0, 255, 255), 2)

            # Show the final image with the matched area.
            img_rgb = cv2.resize(img_rgb, (1011, 592))
            cv2.imshow('Detected', img_rgb)
            cv2.waitKey(0)

        cv2.imwrite('D://test/test_templatematching/template_result.tif', img_gray)


if __name__ == '__main__':

    # Create class object:
    template_matchClass = automated_templateMatching()

    # Load the template image
    template = cv2.imread('D://test/test_templatematching/template.tif')
    templateHighres = cv2.imread('D://test/test_templatematching/template2.tif')

    # Load the search image
    img_gray = cv2.imread('D://test/test_templatematching/searchImage2.tif')

    scaling_factor = 11.11 / 55.55 * 6.5 / 4.25

    template_matchClass.simple_templateMatching(img_gray, templateHighres, scaling_factor, showimage=True)









# for scale in np.linspace(0.5, 1.0, 20)[::-1]:
#     # resize the image according to the scale, and keep track
#     # of the ratio of the resizing
#     resized = imutils.resize(img_gray, width=int(img_gray.shape[1] * scale))
#     r = img_gray.shape[1] / float(resized.shape[1])
#     # if the resized image is smaller than the template, then break
#     # from the loop
#     if resized.shape[0] < tH or resized.shape[1] < tW:
#         break
#     # detect edges in the resized, grayscale image and apply template
#     # matching to find the template in the image
#     edged = cv2.Canny(resized, 50, 200)
#     result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
#     (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
#     # if we have found a new maximum correlation value, then update
#     # the found variable if found is None or maxVal > found[0]:
#     found = (maxVal, maxLoc, r)
#
# # unpack the found variable and compute the (x, y) coordinates
# # of the bounding box based on the resized ratio
# (_, maxLoc, r) = found
# (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
# (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
#
# print(maxLoc)
# print(startX, startY, endX, endY)
#
#
# # draw a bounding box around the detected result and display the image
# cv2.rectangle(img_gray, (startX, startY), (endX, endY), (0, 0, 255), 2)
# img = cv2.resize(img_gray,(1011,592))
# cv2.imshow("Image", img)


