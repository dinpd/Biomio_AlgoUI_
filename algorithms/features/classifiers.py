from algorithms.cvtools.effects import grayscaleAndEqualize
from algorithms.cvtools.types import numpy_darrayToIplImage, iplImageToNumpy_darray
from algorithms.features.rectmerge import mergeRectangles
from algorithms.features.rectsect import intersectRectangles
from algorithms.features.rectfilter import filterRectangles
import logger
import cv2
import os


RectsUnion = 0
RectsIntersect = 1
RectsFiltering = 2


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
    minNeighbors = 2
    minSize = (30, 30)
    flags = cv2.cv.CV_HAAR_SCALE_IMAGE

    def exportSettings(self):
        face_settings = dict()
        face_settings['Scale Factor'] = self.scaleFactor
        face_settings['Minimum Neighbors'] = self.minNeighbors
        face_settings['Minimum Size'] = self.minSize
        return face_settings

    def importSettings(self, settings):
        self.scaleFactor = settings['Scale Factor']
        self.minNeighbors = settings['Minimum Neighbors']
        self.minSize = (settings['Minimum Size'][0], settings['Minimum Size'][1])

    def dump(self):
        logger.logger.debug('Cascade Classifier Settings')
        logger.logger.debug('Scale Factor: %f' % self.scaleFactor)
        logger.logger.debug('Minimum Neighbors: %d' % self.minNeighbors)
        logger.logger.debug('Minimum Size: %s' % str(self.minSize))


class CascadeROIDetector:
    classifierSettings = CascadeClassifierSettings()

    def __init__(self):
        self.__cascades = []
        self._cascades_list = []

    def add_cascade(self, path):
        if os.path.exists(path):
            self.__cascades.append(cv2.CascadeClassifier(path))
            self._cascades_list.append(path)
            # logger.debug("Cascade is loaded.")
        else:
            logger.debug("Such file does not exist.")

    def cascades(self):
        cascades = []
        for cascade in self._cascades_list:
            cascades.append(cascade)
        return cascades

    def exportSettings(self):
        face_cascade = dict()
        face_cascade['ROI Cascades'] = self.cascades()
        face_cascade['Settings'] = self.classifierSettings.exportSettings()
        return face_cascade

    def importSettings(self, settings):
        for cascade in settings['ROI Cascades']:
            self.add_cascade(cascade)
        self.classifierSettings.importSettings(settings['Settings'])

    def detect(self, img, as_list=False):
        rects = list()
        gray = grayscaleAndEqualize(img)
        if len(self.__cascades) == 0:
            logger.debug("Detection impossible. Any cascade not found.")
            return rects
        settings = CascadeClassifierSettings()
        for cascade in self.__cascades:
            lrects = cascade.detectMultiScale(
                gray,
                scaleFactor=self.classifierSettings.scaleFactor,
                minNeighbors=self.classifierSettings.minNeighbors,
                # minSize=settings.minSize,
                minSize=self.classifierSettings.minSize,
                flags=self.classifierSettings.flags)
            # if len(lrects) != 0:
                # lrects[:,2:] += lrects[:,:2]
            if as_list:
                for r in lrects:
                    rects.append(r)
            else:
                rects.append(lrects)
        if len(rects) == 0:
            return []
        return rects

    def detectAndJoin(self, image, as_list=False, algorithm=RectsUnion):
        rects = self.detect(image, as_list)
        if len(rects) == 0:
            logger.debug("ROI is not found for image")
        return self.joinRectangles(rects, algorithm)

    @staticmethod
    def joinRectangles(rects, algorithm=RectsUnion):
        if len(rects) > 0:
            if algorithm == RectsUnion:
                return mergeRectangles(CascadeROIDetector.toList(rects))
            elif algorithm == RectsIntersect:
                return intersectRectangles(CascadeROIDetector.toList(rects))
            elif algorithm == RectsFiltering:
                return filterRectangles(CascadeROIDetector.toList(rects))
        return []

    @staticmethod
    def toList(rects):
        rs = []
        for r in rects:
            for c in r:
                rs.append(c)
        return rs