from detectors import (BRISKDetector, BRISKDetectorSettings, ORBDetector, ORBDetectorSettings,
                       SURFDetector, SURFDetectorSettings, mahotasSURFDetector, mahotasSURFDetectorSettings)
from matchers import (BruteForceMatcherType, FlannBasedMatcherType)
import numpy


BRISKDetectorType = 'BRISK'
ORBDetectorType = 'ORB'
SURFDetectorType = 'SURF'
MahotasSURFDetectorType = "mahotasSURF"


def constructSettings(type=ORBDetectorType):
    settings = {BRISKDetectorType: BRISKDetectorSettings,
                ORBDetectorType: ORBDetectorSettings,
                SURFDetectorType: SURFDetectorSettings,
                MahotasSURFDetectorType: mahotasSURFDetectorSettings}
    if settings.keys().__contains__(type):
        return settings[type]()
    return None


def constructDetector(type=ORBDetectorType, settings=dict()):
    detectors = {BRISKDetectorType: BRISKDetector,
                 ORBDetectorType: ORBDetector,
                 SURFDetectorType: SURFDetector,
                 MahotasSURFDetectorType: mahotasSURFDetector}
    if detectors.keys().__contains__(type):
        return detectors[type](settings)
    return None


def matcherForDetector(detector_type=ORBDetectorType):
    matchers = {BRISKDetectorType: BruteForceMatcherType,
                ORBDetectorType: BruteForceMatcherType,
                SURFDetectorType: FlannBasedMatcherType,
                MahotasSURFDetectorType: FlannBasedMatcherType}
    if matchers.keys().__contains__(detector_type):
        return matchers[detector_type]
    return None


def dtypeForDetector(detector_type=ORBDetectorType):
    types = {BRISKDetectorType: numpy.uint8,
             ORBDetectorType: numpy.uint8,
             SURFDetectorType: numpy.float32,
             MahotasSURFDetectorType: numpy.float32}
    if types.keys().__contains__(detector_type):
        return types[detector_type]
    return None
