from algorithms.features.detectors import (BRISKDetector, BaseDetector)
from algorithms.features.matchers import Matcher, BruteForceMatcherType
from algorithms.cvtools.effects import grayscaleAndEqualize, grayscale, gaussianBlurring
from algorithms.cvtools.visualization import showNumpyImage
from algorithms.cvtools.system import saveNumpyImage
from logger import logger
import numpy
import cv2


class BaseDecorator(BaseDetector):
    def __init__(self, detector):
        BaseDetector.__init__(self)
        self._detector = detector


class FeatureDetector(BaseDecorator):
    def __init__(self, detector):
        BaseDecorator.__init__(self, detector)

    def detect(self, image, mask=None):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        maskimg = None
        if mask is not None:
            maskimg = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        keypoints = self._detector.detect(gray, maskimg)
        fea_image['keypoints'] = keypoints
        return fea_image

    def detectAndCompute(self, image, mask=None):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image
        gray = grayscaleAndEqualize(image)
        maskimg = None
        if mask is not None:
            maskimg = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = self._detector.detectAndCompute(gray, maskimg)
        fea_image['keypoints'] = keypoints
        fea_image['descriptors'] = descriptors
        return fea_image

    def compute(self, image, keypoints):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image
        gray = grayscaleAndEqualize(image)
        keypoints, descriptors = self._detector.compute(gray, keypoints)
        fea_image['keypoints'] = keypoints
        fea_image['descriptors'] = descriptors
        return fea_image


class ExternalFeatureDetector(BaseDecorator):
    def __init__(self, detector):
        BaseDecorator.__init__(self, detector)

    def detect(self, image, mask=None):
        fea_image = dict()
        img = cv2.imread(image, cv2.CV_LOAD_IMAGE_COLOR)
        if img is None:
            print "Couldn't find the object image with the provided path."
            return fea_image
        fea_image['data'] = img
        gray = grayscaleAndEqualize(img)
        maskimg = None
        if mask is not None:
            maskimg = cv2.imread(mask, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        keypoints = self._detector.detect(gray, maskimg)
        fea_image['keypoints'] = keypoints
        return fea_image

    def detectAndCompute(self, image, mask=None):
        fea_image = dict()
        img = cv2.imread(image, cv2.CV_LOAD_IMAGE_COLOR)
        if img is None:
            print "Couldn't find the object image with the provided path."
            return fea_image
        fea_image['data'] = img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        maskimg = None
        if mask is not None:
            maskimg = cv2.imread(mask, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        keypoints, descriptors = self._detector.detectAndCompute(gray, maskimg)
        fea_image['keypoints'] = keypoints
        fea_image['descriptors'] = descriptors
        return fea_image


class ComplexDetector:
    def __init__(self):
        self._detector = BRISKDetector()
        self._extractor = BRISKDetector.extractor()
        # self._matcher = MatcherCreator('BruteForce-Hamming')
        self._matcher = Matcher(BruteForceMatcherType)

    def detect(self, filepath, maskpath=None):
        fea_image = ImageFeatures()

        rect = (100, 400, 1000, 1100)

        image = cvtools.loadImage(filepath)

        # roiImage = ComplexDetector.getROIImage(image, rect)
        roiImage = image

        convImage = numpy.asarray(roiImage[:,:])
        fea_image.image(convImage)

        grayImage = cvtools.grayscale(convImage)

        eqImage = cv2.equalizeHist(grayImage)
        fea_image.image(eqImage)

        gabor = gfilter.build_filters()
        gImage = gfilter.process(eqImage, gabor)
        # fea_image.image(gImage)
        i = 0
        for kern in gabor:
            fimg = gfilter.process_kernel(eqImage, kern)
            cvtools.saveImage(filepath + "_" + str(i) + ".png", fimg)
            i += 1

        mask = None
        if maskpath is not None:
            mask = cv2.imread(maskpath, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        keypoints = self._detector.detect(gImage, mask)
        fea_image.keypoints(keypoints)
        return fea_image