from algorithms.cvtools.effects import grayscaleAndEqualize
from algorithms.cvtools.types import numpy_darrayToIplImage, iplImageToNumpy_darray
from algorithms.features.rectmerge import mergeRectangles
from logger import logger
import cv2
import os


RectanglesUnion = 0


def getROIImage(image, rectangle):
    """
    Cut rectangle ROI (Region of Image) on the image.

    :param image: numpy.ndarray image.
    :param rectangle: list[x, y, width, height]
    :return: numpy.ndarray ROI image.
    """
    im = numpy_darrayToIplImage(image)
    cv2.cv.SetImageROI(im, (rectangle[0], rectangle[1], rectangle[2], rectangle[3]))
    out = cv2.cv.CreateImage(cv2.cv.GetSize(im), im.depth, im.nChannels)
    cv2.cv.Copy(im, out)
    cv2.cv.ResetImageROI(out)
    return iplImageToNumpy_darray(out)


class CascadeClassifierSettings:
    scaleFactor = 1.1
    minNeighbors = 7
    minSize = (10, 10)
    flags = cv2.cv.CV_HAAR_SCALE_IMAGE


class CascadeROIDetector:
    classifierSettings = CascadeClassifierSettings()

    def __init__(self):
        self.__cascades = []

    def add_cascade(self, path):
        if os.path.exists(path):
            self.__cascades.append(cv2.CascadeClassifier(path))
            # logger.debug("Cascade is loaded.")
        else:
            logger.debug("Such file does not exist.")

    def detect(self, img):
        rects = list()
        gray = grayscaleAndEqualize(img)
        if len(self.__cascades) == 0:
            logger.debug("Detection impossible. Any cascade not found.")
            return rects
        for cascade in self.__cascades:
            lrects = cascade.detectMultiScale(
                gray,
                scaleFactor=self.classifierSettings.scaleFactor,
                minNeighbors=self.classifierSettings.minNeighbors,
                minSize=self.classifierSettings.minSize,
                flags=self.classifierSettings.flags)
            # if len(lrects) != 0:
                # lrects[:,2:] += lrects[:,:2]
            for r in lrects:
                rects.append(r)
        if len(rects) == 0:
            return []
        return rects

    def detectAndJoin(self, image, algorithm=RectanglesUnion):
        rects = self.detect(image)
        if len(rects) is 0:
            logger.debug("ROI is not found for image")
        return self.joinRectangles(rects, algorithm)

    @staticmethod
    def joinRectangles(rects, algorithm=RectanglesUnion):
        if len(rects) > 0:
            if algorithm == RectanglesUnion:
                return mergeRectangles(rects)
        return []