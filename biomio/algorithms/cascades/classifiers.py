from biomio.algorithms.cascades import intersectRectangles, filterRectangles, mergeRectangles, APP_ROOT
from biomio.algorithms.cvtools import grayscale, rotate90
from biomio.algorithms.logger import logger
import cv2
import os


RectsUnion = 0
RectsIntersect = 1
RectsFiltering = 2


class CascadeClassifierSettings:
    scaleFactor = 1.1
    minNeighbors = 3
    minSize = (30, 30)
    maxSize = (1000, 1000)
    flags = cv2.cv.CV_HAAR_SCALE_IMAGE

    def exportSettings(self):
        settings = dict()
        settings['Scale Factor'] = self.scaleFactor
        settings['Minimum Neighbors'] = self.minNeighbors
        settings['Minimum Size'] = self.minSize
        settings['Maximum Size'] = self.maxSize
        return settings

    def importSettings(self, settings):
        self.scaleFactor = settings['Scale Factor']
        self.minNeighbors = settings['Minimum Neighbors']
        self.minSize = (settings['Minimum Size'][0], settings['Minimum Size'][1])
        self.maxSize = (settings['Maximum Size'][0], settings['Maximum Size'][1])

    def dump(self):
        logger.debug('Cascade Classifier Settings')
        logger.debug('Scale Factor: %f' % self.scaleFactor)
        logger.debug('Minimum Neighbors: %d' % self.minNeighbors)
        logger.debug('Minimum Size: %s' % str(self.minSize))
        logger.debug('Maximum Size: %s' % str(self.maxSize))


class CascadeROIDetector:
    def __init__(self):
        self.classifierSettings = CascadeClassifierSettings()
        self.__cascades = []
        self._cascades_list = []
        self._relative_cl = []

    def add_cascade(self, path):
        self._relative_cl.append(path)
        abs_path = os.path.join(APP_ROOT, "../../", path)
        logger.debug("####### %s" % abs_path)
        if os.path.exists(abs_path):
            self.__cascades.append(cv2.CascadeClassifier(abs_path))
            self._cascades_list.append(abs_path)
        else:
            logger.debug("Such file does not exist.")

    def cascades(self):
        cascades = []
        for cascade in self._cascades_list:
            cascades.append(cascade)
        return cascades

    def exportSettings(self):
        face_cascade = dict()
        face_cascade['ROI Cascades'] = [cascade for cascade in self._relative_cl]
        face_cascade['Settings'] = self.classifierSettings.exportSettings()
        return face_cascade

    def importSettings(self, settings):
        for cascade in settings['ROI Cascades']:
            self.add_cascade(cascade)
        self.classifierSettings.importSettings(settings['Settings'])

    def detect(self, img, as_list=False):
        rects = list()
        gray = grayscale(img)
        if len(self.__cascades) == 0:
            logger.debug("Detection impossible. Any cascade not found.")
            return rects
        for cascade in self.__cascades:
            lrects = cascade.detectMultiScale(
                gray,
                scaleFactor=self.classifierSettings.scaleFactor,
                minNeighbors=self.classifierSettings.minNeighbors,
                minSize=self.classifierSettings.minSize,
                maxSize=self.classifierSettings.maxSize,
                flags=self.classifierSettings.flags)
            logger.debug(lrects)
            if as_list:
                rects += [r for r in lrects]
            else:
                rects.append(lrects)
        logger.debug(rects)
        if len(rects) == 0:
            return []
        return rects

    def detectAndJoinWithRotation(self, image, as_list=False, algorithm=RectsUnion):
        rect = [0, 0, 0, 0]
        img = image
        c_rect = self.detectAndJoin(image, as_list, algorithm)
        if len(c_rect) > 0:
            if rect[2] < c_rect[2] and rect[3] < c_rect[3]:
                rect = c_rect
                img = image
        # 90
        img2 = rotate90(image)
        # 180
        img3 = rotate90(img2)
        # 270
        img4 = rotate90(img3)
        c_rect = self.detectAndJoin(img4, as_list, algorithm)
        if len(c_rect) > 0:
            if rect[2] < c_rect[2] and rect[3] < c_rect[3]:
                rect = c_rect
                img = img4
        if rect[2] == 0 or rect[3] == 0:
            rect = []
        return img, rect

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
