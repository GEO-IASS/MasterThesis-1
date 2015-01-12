# -*- coding: utf-8 -*-
"""
Created on 30/11-2014

@author: christian
"""

##########################################
# Libraries
##########################################
import numpy as np                  # required for calculate i.e mean with np.mean
from pexpect import searcher_re
from scipy.maxentropy.maxentropy import conditionalmodel
import cv2                          # required for use OpenCV
import matplotlib.pyplot as plt     # required for plotting
import pylab                        # required for arrange doing the wx list
import random                       # required to choose random initial weights and shuffle data

##########################################
# Classes
##########################################

class ProcessImage(object):

    #The constructor will run each time an object is assigned to this class.
    def __init__(self, img):
        self.img = img
        self.thresholdValue = 128

        self.minHue = 22
        self.maxHue = 255
        self.minSaturation = 0
        self.maxSaturation = 255
        self.minValue = 147
        self.maxValue = 255

        self.lower_hsv = np.array([self.minHue, self.minSaturation, self.minValue], dtype=np.uint8)
        self.upper_hsv = np.array([self.maxHue, self.maxSaturation, self.maxValue], dtype=np.uint8)

        # Functions that I want to be called each time we instansiate the class. I.e each time we get a new image
        self.imgGray = self.getGrayImage()
        self.imgThreshold = self.getThresholdImage(self.thresholdValue)  # Let the background be black and the seeds be gray.
        self.imgHSV = self.getHSV(self.lower_hsv, self.upper_hsv)
        self.imgSeedAndTrout = self.addImg(self.imgThreshold, self.imgHSV)
        self.imgMorph = self.getClosing(self.imgHSV, 2, 2)

        # contours
        self.contours = self.getContours(self.imgMorph)
        self.centers = self.getCentroid(self.contours, 120)

        self.imgWithContours = self.img.copy()
        self.drawCentroid(self.imgWithContours, self.centers, 10, (0, 0, 255))

        self.rects = self.getMinAreaRect(self.contours)
        # self.box = cv2.cv.BoxPoints(self.rects)
        # self.box = np.int0(self.box)


    def showImg(self, nameOfWindow, image, scale):
        imgCopy = image.copy()
        image_show = self.scaleImg(imgCopy, scale)
        cv2.imshow(nameOfWindow, image_show)
        cv2.imwrite("/home/christian/workspace_python/MasterThesis/SeedDetection/writefiles/" + str(nameOfWindow) + ".jpg", image_show)

    def scaleImg(self, image, scale):
        img_scale = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        return img_scale

    def addImg(self, image1, image2):
        addedImage = cv2.add(image1, image2)
        return addedImage

    def getGrayImage(self):
        #Do the grayscale converting
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        return img_gray

    def getThresholdImage(self, maxValue):
        # Do the thresholding of the image.
        # Somehow we need to return the "ret" together with the image, to be able to show the image...
        ret, img_threshold = cv2.threshold(self.imgGray, self.thresholdValue, maxValue, cv2.THRESH_BINARY)
        return img_threshold

    def getEdge(self):
        img_edges = cv2.Canny(self.imgGray, self.minCannyValue, self.maxCannyValue)
        return img_edges

    def getHSV(self, lower_hsv, upper_hsv):
        img_hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        img_seg = cv2.inRange(img_hsv, lower_hsv, upper_hsv)
        return img_seg

    def getContours(string, binary_img):
        #Copy the image, to avoid manipulating with original
        contour_img = binary_img.copy()

        #Find the contours of the thresholded image
        contours, hierarchy = cv2.findContours(contour_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #Return the contours. We dont want to use the hierarchy yet
        # However the hierarchy is usefull the detect contours inside a contour or dont detect it.
        # That is what hierarchy keeps track of. (Children and parents)
        return contours

    def getCentroid(self, contours, areaThreshold):
        # List of centers
        centers = []

        #Run through all the contours
        for contour in contours:

            #Get the area of each contour
            contour_area = cv2.contourArea(contour, False)

            if contour_area < areaThreshold:
                continue

            #Calculate the moments for each contour in contours
            m = cv2.moments(contour)

            #If somehow one of the moments is zero, then we brake and reenter the loop (continue)
            #to avoid dividing with zero
            if (int(m['m01']) == 0 or int(m['m00'] == 0)):
                continue

            #Calculate the centroid x,y, coordinate out from standard formula.
            center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))

            #Append each calculated center into the centers list.
            centers.append(center)
        return centers

    def getMinAreaRect(self, contours):
        list_of_rects = []
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            list_of_rects.append(rect)
        return list_of_rects

    def drawCentroid(self, image, centers, size, RGB_list):
        # Color the central coordinates for red bricks with a filled circle
        for center in centers:
            cv2.circle(image, center, size, RGB_list, -1)

    def getErode(self, img_binary, iterations_erode):
        kernel = np.ones((3, 3), np.uint8)
        img_erode = cv2.erode(img_binary, kernel, iterations=iterations_erode)
        return img_erode

    def getDilate(self, img_binary, iterations_dilate):
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_binary, kernel, iterations=iterations_dilate)
        return img_dilate

    def getOpening(self, img_binary, iterations_erode, iterations_dilate):
        kernel = np.ones((3, 3), np.uint8)
        img_erode = cv2.erode(img_binary, kernel, iterations=iterations_erode)
        img_morph = cv2.dilate(img_erode, kernel, iterations=iterations_dilate)
        return img_morph

    def getClosing(self, img_binary, iterations_erode, iterations_dilate):
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_binary, kernel, iterations=iterations_dilate)
        img_morph = cv2.erode(img_dilate, kernel, iterations=iterations_erode)
        return img_morph

    def nothing(self, x):
        pass

    def addTrackbar(self, name, nameOfWindow, startValue, maxValue):
        cv2.namedWindow(nameOfWindow)
        cv2.createTrackbar(name, nameOfWindow, startValue, maxValue, self.nothing)

    def trackbarListener(self, name, nameOfWindow):
        value = cv2.getTrackbarPos(name, nameOfWindow)
        return value


# Test function

def testFunction():
    a = 2
    b = 2
    c = a + b
    return a, b, c

def main():

    # Loading the image
    input_image = cv2.imread("/home/christian/workspace_python/MasterThesis/SeedDetection/seeds/seeds2.jpg", cv2.CV_LOAD_IMAGE_COLOR)

    #input_image = cv2.imread("/home/christian/workspace_python/MasterThesis/SeedDetection/seeds/roi_seed.png", cv2.CV_LOAD_IMAGE_COLOR)
    # The next step is to interface a camera into the code.
    # And then each frame from the camera will be treated as a input_image

    # Do the image processing on that given image and create the object "image"
    imgObj = ProcessImage(input_image)

    # Show the image. 1 = normal size. 0.5 = half size. About 1 and bigger takes a lot of CPU power!!! So dont go there.
    image_ratio = 0.3
    #imgObj.showImg("Input image and fitted to display on screen", imgObj.img, image_ratio)

    # Threshold the image
    imgObj.showImg("Thresholded image and fitted to display on screen", imgObj.imgThreshold, image_ratio)

    # Segment the image with HSV
    imgObj.showImg("HSV segmented image and fitted to display on screen", imgObj.imgHSV, image_ratio)

    # Do a little morph on the HSV to get nicer trouts
    imgObj.showImg("HSV segmented image morphed and fitted to display on screen", imgObj.imgMorph, image_ratio)

    # Add the two images, grayscale and HSV
    #imgObj.showImg("Added images and fitted to display on screen", imgObj.imgSeedAndTrout, image_ratio)

    # Add the two images, grayscale and HSV
    imgObj.showImg("Show contours in image and let it be fitted to display on screen", imgObj.imgWithContours, image_ratio)

    # Get the list of data from the minRectArea OpenCV function
    rect = imgObj.rects

    print "The contour size is: ", len(rect)
    print rect

    print "Result of test function is: ", testFunction()

    test = testFunction()
    print test[2]

    cv2.waitKey(0)
    cv2.destroyAllWindows()


    # while(1):
    #     k = cv2.waitKey(30) & 0xff
    #     if k == 27:
    #         print("User closed the program...")
    #         break
    # # Wait until the user hit any key
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



    # # This is the HSV segmentation
    # image.addTrackbar("Hue min", "HSV segmentation", image.minHue, 255)
    # image.addTrackbar("Hue max", "HSV segmentation", image.maxHue, 255)
    # image.addTrackbar("Saturation min", "HSV segmentation", image.minSaturation, 255)
    # image.addTrackbar("Saturation max", "HSV segmentation", image.maxSaturation, 255)
    # image.addTrackbar("Value min", "HSV segmentation", image.minValue, 255)
    # image.addTrackbar("Value max", "HSV segmentation", image.maxValue, 255)

    # Wait here, while user hits ESC.
    # while 1:
    #
    #     image_ratio = 0.2
    #     morph_iterations = 2
    #
    #     # Show the image
    #     image.showImg("Input image and fitted to display on screen", image.img, image_ratio)
    #
    #     # # This is the normal thresholding --- Test show that this was not useful in segmentating the eeeds vs. trout
    #     threshold_img = image.getThresholdImage(128)
    #     image.showImg("Threshold image", threshold_img, image_ratio)
    #     image.thresholdValue = image.trackbarListener("Threshold", "Threshold image")
    #
    #     # # This is the Canny edge detection  --- Test show that this was not very useful
    #     # image.showImg("Edge detection image", image.getEdge(), image_ratio)
    #     # image.minCannyValue = image.trackbarListener("Min value", "Edge detection image")
    #     # image.maxCannyValue = image.trackbarListener("Max value", "Edge detection image")
    #
    #     # # This is the HSV segmentation --- Test show that this was ?????????
    #     hsv_img = image.getHSV(image.lower_hsv, image.upper_hsv)
    #     # image.showImg("HSV segmentation", hsv_img, image_ratio)
    #     # image.lower_hsv[0] = image.trackbarListener("Hue min", "HSV segmentation")
    #     # image.upper_hsv[0] = image.trackbarListener("Hue max", "HSV segmentation")
    #     # image.lower_hsv[1] = image.trackbarListener("Saturation min", "HSV segmentation")
    #     # image.upper_hsv[1] = image.trackbarListener("Saturation max", "HSV segmentation")
    #     # image.lower_hsv[2] = image.trackbarListener("Value min", "HSV segmentation")
    #     # image.upper_hsv[2] = image.trackbarListener("Value max", "HSV segmentation")
    #
    #     image_dilate = image.getDilate(hsv_img, morph_iterations)
    #     # image.showImg("Dilate", image_dilate, image_ratio)
    #     image_erode = image.getErode(image_dilate, morph_iterations)
    #     # image.showImg("Closing", image_erode, image_ratio)
    #
    #     # Here add the grayscale and hsv image together. Note: use cv2.add otherwise pixelvale like 250 + 10 = 260 % 255 = 4, and not 255.
    #     seedAndTrout_img = cv2.add(threshold_img, hsv_img)
    #     image.showImg("Seed image", threshold_img, image_ratio)
    #     image.showImg("Trout image", hsv_img, image_ratio)
    #     image.showImg("Seed and trout image", seedAndTrout_img, image_ratio)
    #
    #     contours = image.getContours(threshold_img)
    #     centers = image.getCentroid(contours)
    #     image.drawCentroid(img, centers, (0, 255, 0))
    #
    #
    #
    #
    #
    #
    #
    #     k = cv2.waitKey(30) & 0xff
    #     if k == 27:
    #         print("User closed the program...")
    #         break

    # Close down all open windows...

    # Wait for a user input to close down the script

    # cv2.destroyAllWindows()

if __name__ == '__main__':
    main()