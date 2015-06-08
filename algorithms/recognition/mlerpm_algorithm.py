from algorithms.recognition.features import (FeatureDetector,
                                             BRISKDetectorType, ORBDetectorType)
from algorithms.features.detectors import (BRISKDetector, ORBDetector,
                                           BRISKDetectorSettings, ORBDetectorSettings)
from algorithms.features.matchers import (createMatcher,
                                          BruteForceMatcherType, FlannBasedMatcherType,
                                          LowesMatchingScheme)
import logger
import numpy
import math


class MLERPMSettings:
    """
    Metric Learned Extended Robust Point Matching (MLERPM) Settings class
    """
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()
    matcher_type = BruteForceMatcherType


class MLERPMAlgorithm:
    settings = MLERPMSettings()

    def __init__(self):
        self._data = None
        self._source = None
        self._additional_data = dict()
        self._additional_data['Itmax'] = 100
        self._additional_data['C'] = 1
        self._additional_data['l1'] = 1

    def recognize(self, data, source):
        self._feature_extraction(data)
        self._feature_extraction(source)
        self._data = data
        self._source = source
        self._additional_data['matches'] = self._keypoint_selection(data, source)

    def _feature_extraction(self, imgobj):
        detector = FeatureDetector()
        if self.settings.detector_type is BRISKDetectorType:
            brisk_detector = BRISKDetector(self.settings.brisk_settings.thresh,
                                           self.settings.brisk_settings.octaves,
                                           self.settings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            orb_detector = ORBDetector(self.settings.orb_settings.features,
                                       self.settings.orb_settings.scaleFactor,
                                       self.settings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        try:
            obj = detector.detectAndComputeImage(imgobj['data'])
        except Exception as err:
            logger.logger.debug(err.message)
            return False
        imgobj['keypoints'] = obj['keypoints']
        imgobj['descriptors'] = obj['descriptors']
        if imgobj['descriptors'] is None:
            imgobj['descriptors'] = []

    def _keypoint_selection(self, dataobj, souobj):
        matcher = createMatcher(self.settings.matcher_type)
        matches = matcher.knnMatch(dataobj['descriptors'], souobj['descriptors'], k=2)
        opt = []
        for match in matches:
            if len(match) >= 2:
                if LowesMatchingScheme(match[0], match[1]):
                    opt.append(match[0])
        return opt

    def recalc_m(self):
        m = self._additional_data.get("m", None)
        if m is None:
            m = numpy.zeros((len(self._data['keypoints']), len(self._source['keypoints'])))
        for i in range(len(self._data['keypoints'])):
            for j in range(len(self._source['keypoints'])):
                a = pow(self.norm2(self.f_func(self._data['keypoints'][i].pt) - self._source['keypoints'][j].pt), 2)
                b = self.normM(self._data['descriptors'][i], self._source['descriptors'][j])
                m[i][j] = math.exp(-1 * (a + self._additional_data.get('l1', 0) * b) / (2 * self._additional_data['C']))
        print m

    def transpose(self, v):
        transposed = []
        for i in range(len(v)):
            transposed.append([row[i] for row in v])
        return transposed

    def norm2(self, x):
        x_sum = 0
        for xi in x:
            x_sum += pow(abs(xi), 2)
        return pow(x_sum, 0.5)

    def normM(self, t1, t2):
        dt = t1 - t2
        return self.transpose(dt) * self._additional_data['M'] * dt

    def f_func(self, g):
        pass

    def diag(self):
        pass

    def _mlrp_matching(self):
        for i in range(0, self._additional_data['Itmax'], 1):
            pass


def main():
    algo = MLERPMAlgorithm()
    algo.recalc_m()


if __name__ == '__main__':
    main()