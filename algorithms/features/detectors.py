from algorithms.cvtools.types import listToNumpy_ndarray
from mahotas.features import surf
import logger
import numpy
import cv2


class BaseDetector:
    def __init__(self):
        print self.__class__
        self._detector = None
        self._extractor = None

    @staticmethod
    def defaultSettings():
        return dict()

    def detect(self, image, mask=None):
        return self._detector.detect(image, mask)

    def detectAndCompute(self, image, mask=None):
        if self._extractor is not None:
            keypoints = self._detector.detect(image, mask)
            return self._extractor.compute(image, keypoints)
        try:
            return self._detector.detectAndCompute(image, mask)
        except Exception as err:
            print err.message
            return None

    def compute(self, image, keypoints):
        if self._extractor is not None:
            return self._extractor.compute(image, keypoints)
        try:
            return self._detector.compute(image, keypoints)
        except Exception as err:
            print err.message
            return None


class BRISKDetectorSettings:
    thresh = 10
    octaves = 0
    patternScale = 1.0

    def exportSettings(self):
        return {
            'thresh': self.thresh,
            'octaves': self.octaves,
            'patternScale': self.patternScale
        }

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            self.thresh = settings['thresh']
            self.octaves = settings['octaves']
            self.patternScale = settings['patternScale']

    def dump(self):
        logger.logger.debug('BRISK Detector Settings:')
        logger.logger.debug('    Threshold: %f' % self.thresh)
        logger.logger.debug('    Octaves: %f' % self.octaves)
        logger.logger.debug('    Pattern Scale: %f' % self.patternScale)


class BRISKDetector(BaseDetector):
    def __init__(self, settings=BRISKDetectorSettings()):
        BaseDetector.__init__(self)
        self._detector = cv2.BRISK(thresh=settings.thresh,
                                   octaves=settings.octaves,
                                   patternScale=settings.patternScale)
        self._extractor = self._detector

    @staticmethod
    def defaultSettings():
        return {
            thresh: 10,
            octaves: 0,
            scale: 1.0
        }


class ORBDetectorSettings:
    features = 500
    scaleFactor = 1.1
    nlevels = 8

    def exportSettings(self):
        return {
            'features': self.features,
            'scaleFactor': self.scaleFactor,
            'nlevels': self.nlevels
        }

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            self.features = settings['features']
            self.scaleFactor = settings['scaleFactor']
            self.nlevels = settings['nlevels']

    def dump(self):
        logger.logger.debug('ORB Detector Settings:')
        logger.logger.debug('    Features: %d' % self.features)
        logger.logger.debug('    Scale Factor: %f' % self.scaleFactor)
        logger.logger.debug('    Levels: %d' % self.nlevels)


class ORBDetector(BaseDetector):
    def __init__(self, settings=ORBDetectorSettings()):
        BaseDetector.__init__(self)
        self._detector = cv2.ORB(nfeatures=settings.features,
                                 scaleFactor=settings.scaleFactor,
                                 nlevels=settings.nlevels)
        self._extractor = self._detector

    @staticmethod
    def defaultSettings():
        return {
            features: 500,
            scaleFactor: 1.1,
            nlevels: 8
        }


class SURFDetectorSettings:
    threshold = 300

    def exportSettings(self):
        return {
            'threshold': self.threshold
        }

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            self.threshold = settings['threshold']

    def dump(self):
        logger.logger.debug('SURF Detector Settings:')
        logger.logger.debug('    Threshold: %f' % self.threshold)


class SURFDetector(BaseDetector):
    def __init__(self, settings=SURFDetectorSettings()):
        BaseDetector.__init__(self)
        self._detector = cv2.SURF(hessianThreshold=settings.threshold)
        self._detector.extended = False
        self._extractor = self._detector


class mahotasSURFDetectorSettings:
    nr_octaves = 4
    nr_scales = 6
    initial_step_size = 1
    threshold = 0.1
    max_points = 1000
    is_integral = False

    def exportSettings(self):
        return {
            'octaves': self.nr_octaves,
            'scales': self.nr_scales,
            'init_step_size': self.initial_step_size,
            'threshold': self.threshold,
            'max_points': self.max_points,
            'is_integral': self.is_integral
        }

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            self.nr_octaves = settings['octaves']
            self.nr_scales = settings['scales']
            self.initial_step_size = settings['init_step_size']
            self.threshold = settings['threshold']
            self.max_points = settings['max_points']
            self.is_integral = settings['is_integral']

    def dump(self):
        logger.logger.debug('Mahotas SURF Detector Settings:')
        logger.logger.debug('    Octaves: %f' % self.nr_octaves)
        logger.logger.debug('    Scales: %f' % self.nr_scales)
        logger.logger.debug('    Initial Step Size: %f' % self.initial_step_size)
        logger.logger.debug('    Threshold: %f' % self.threshold)
        logger.logger.debug('    Max Points: %f' % self.max_points)
        logger.logger.debug('    Integral: %d' % self.is_integral)


class mahotasSURFDetector(BaseDetector):
    def __init__(self, settings=mahotasSURFDetectorSettings()):
        BaseDetector.__init__(self)
        self._settings = settings

    def detect(self, image, mask=None):
        keypoints = surf.interest_points(image, self._settings.nr_octaves, self._settings.nr_scales,
                                         self._settings.initial_step_size, self._settings.threshold,
                                         self._settings.max_points, self._settings.is_integral)
        return [mahotasSURFDetector.getKeyPoint(keypoint) for keypoint in keypoints]

    def detectAndCompute(self, image, mask=None):
        keypoints = surf.interest_points(image, self._settings.nr_octaves, self._settings.nr_scales,
                                         self._settings.initial_step_size, self._settings.threshold,
                                         self._settings.max_points, self._settings.is_integral)
        descriptors = surf.descriptors(image, keypoints, self._settings.is_integral, True)
        cvkeys = [mahotasSURFDetector.getKeyPoint(keypoint) for keypoint in keypoints]
        return cvkeys, listToNumpy_ndarray([mahotasSURFDetector.getDescriptor(d) for d in descriptors])

    def compute(self, image, keypoints):
        if keypoints is None or len(keypoints) == 0:
            return keypoints, []
        mkeys = [mahotasSURFDetector.getMahotasKeypoint(keypoint) for keypoint in keypoints]
        return keypoints, listToNumpy_ndarray([mahotasSURFDetector.getDescriptor(d) for d in
                                               surf.descriptors(image, mkeys, self._settings.is_integral, True)])

    @staticmethod
    def getKeyPoint(keypoint):
        return cv2.KeyPoint(keypoint[1], keypoint[0], keypoint[2], keypoint[4], keypoint[3])

    @staticmethod
    def getMahotasKeypoint(keypoint):
        return [keypoint.pt[1], keypoint.pt[0], keypoint.size, keypoint.response, keypoint.angle]

    @staticmethod
    def getDescriptor(descriptor):
        return listToNumpy_ndarray(descriptor, numpy.float32)
