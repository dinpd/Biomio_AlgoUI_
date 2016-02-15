from biomio.algorithms.features.detectors import BaseDetector
import biomio.algorithms.algorithms.images.self_quotient_image as sqi
import biomio.algorithms.algorithms.images.colour_tools as hsv
import biomio.algorithms.cvtools.effects as effects
from gabor_threads import process, build_filters
import cv2


FEATURES_GRAYSCALE = 0
FEATURES_EQUALIZE = 1
FEATURES_SQIMAGE = 2
FEATURES_GABORIMAGE = 3


def grayscale(fn):
    def wrapped(self, image):
        res = image
        if res is not None and self._mode == FEATURES_GRAYSCALE:
            res = effects.grayscale(res)
        return fn(self, res)
    return wrapped


def grayscale_and_equalize(fn):
    def wrapped(self, image):
        res = image
        if res is not None and self._mode == FEATURES_EQUALIZE:
            res = effects.grayscaleAndEqualize(res)
        return fn(self, res)
    return wrapped


def self_quotient_image(fn):
    def wrapped(self, image):
        res = image
        if res is not None and self._mode == FEATURES_SQIMAGE:
            res = effects.grayscale(sqi.self_quotient_image(hsv.hsv_values_extraction(res)))
        return fn(self, res)
    return wrapped


def gabor_image(fn):
    def wrapped(self, image):
        res = image
        if res is not None and self._mode == FEATURES_GABORIMAGE:
            gabor = build_filters()
            res = effects.grayscale(process(res, gabor))
        return fn(self, res)
    return wrapped


class BaseDecorator(BaseDetector):
    def __init__(self, detector):
        BaseDetector.__init__(self)
        self._detector = detector


class FeatureDetector(BaseDecorator):
    def __init__(self, detector, mode=FEATURES_EQUALIZE):
        BaseDecorator.__init__(self, detector)
        self._mode = mode

    def detect(self, image, mask=None):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image
        maskimg = None
        if mask is not None:
            maskimg = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        keypoints = self._detector.detect(self.transform_image(image), maskimg)
        fea_image['keypoints'] = keypoints
        return fea_image

    def detectAndCompute(self, image, mask=None):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image

        maskimg = None
        if mask is not None:
            maskimg = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = self._detector.detectAndCompute(self.transform_image(image), maskimg)
        fea_image['keypoints'] = keypoints
        fea_image['descriptors'] = descriptors
        return fea_image

    def compute(self, image, keypoints):
        fea_image = dict()
        if image is None:
            return fea_image
        fea_image['data'] = image
        keypoints, descriptors = self._detector.compute(self.transform_image(image), keypoints)
        fea_image['keypoints'] = keypoints
        fea_image['descriptors'] = descriptors
        return fea_image

    @grayscale
    @grayscale_and_equalize
    @self_quotient_image
    @gabor_image
    def transform_image(self, image):
        return image
