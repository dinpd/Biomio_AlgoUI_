from algorithms.features.detectors import (BRISKDetector, ORBDetector,
                                           BRISKDetectorSettings, ORBDetectorSettings)
from algorithms.features.classifiers import (getROIImage,
                                             RectsIntersect, RectsFiltering)
from algorithms.recognition.features import (FeatureDetector,
                                             BRISKDetectorType, ORBDetectorType)
from algorithms.cvtools.visualization import (showClusters, showNumpyImage, showMatches,
                                              drawLine, drawClusters, drawKeypoints)
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
from algorithms.recognition.tools import minDistance, meanDistance, medianDistance
import logger


LSHashType = 0
NearPyHashType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    neighbours_distance = 1.0
    # max_hash_length = 600
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()
    probability = 25.0

    def exportSettings(self):
        info = dict()
        info['Neighbours Distance'] = self.neighbours_distance
        info['Probability'] = self.probability
        settings = dict()
        if self.detector_type == BRISKDetectorType:
            info['Detector Type'] = 'BRISK'
            settings['Thresh'] = self.brisk_settings.thresh
            settings['Octaves'] = self.brisk_settings.octaves
            settings['Pattern Scale'] = self.brisk_settings.patternScale
        elif self.detector_type == ORBDetectorType:
            info['Detector Type'] = 'ORB'
            settings['Number of features'] = self.orb_settings.features
            settings['Scale Factor'] = self.orb_settings.scaleFactor
            settings['Number of levels'] = self.orb_settings.nlevels
        info['Detector Settings'] = settings
        return info

    def importSettings(self, settings):
        self.neighbours_distance = settings['Neighbours Distance']
        self.probability = settings['Probability']
        detector = settings.get('Detector Settings', dict())
        if settings.get('Detector Type') == 'BRISK':
            self.detector_type = BRISKDetectorType
            self.brisk_settings.thresh = detector['Thresh']
            self.brisk_settings.octaves = detector['Octaves']
            self.brisk_settings.patternScale = detector['Pattern Scale']
        elif settings.get('Detector Type') == 'ORB':
            self.detector_type = ORBDetectorType
            self.orb_settings.features = detector['Number of features']
            self.orb_settings.scaleFactor = detector['Scale Factor']
            self.orb_settings.nlevels = detector['Number of levels']

    def dump(self):
        logger.logger.debug('Keypoints Objects Detectors Settings')
        logger.logger.debug('Neighbours Distance: %f' % self.neighbours_distance)
        logger.logger.debug('Probability: %f' % self.probability)
        logger.logger.debug('Detector Type: %s' % self.detector_type)
        logger.logger.debug('BRISK Detector Settings')
        logger.logger.debug('   Thresh: %d' % self.brisk_settings.thresh)
        logger.logger.debug('   Octaves: %d' % self.brisk_settings.octaves)
        logger.logger.debug('   Pattern Scale: %f' % self.brisk_settings.patternScale)
        logger.logger.debug('ORB Detector Settings')
        logger.logger.debug('   Number of features: %d' % self.orb_settings.features)
        logger.logger.debug('   Scale Factor: %f' % self.orb_settings.scaleFactor)
        logger.logger.debug('   Number of levels: %d' % self.orb_settings.nlevels)


def identifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Identifying...")
        res = None
        if self.data_detect(self, data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Identifying finished.")
        return res

    return wrapped


def verifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Verifying...")
        self._log = ""
        res = False
        if self.data_detect(data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Verifying finished.")
        return res

    return wrapped


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self):
        self._hash = None
        self._cascadeROI = None
        self._detector = None
        self._eyeROI = None
        self._use_template = False
        self._template_layer = 0
        self._use_roi = True
        self._log = ""

    def log(self):
        return self._log

    def setUseTemplate(self, use):
        self._use_template = use

    def setTemplateLayer(self, layer):
        self._template_layer = layer

    def setUseROIDetection(self, use):
        self._use_roi = use

    def addSource(self, data):
        logger.logger.debug(data['path'])
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        for data in data_list:
            self.addSource(data)

    def importSources(self, data):
        logger.logger.debug("Detector cannot import sources.")

    def exportSources(self):
        logger.logger.debug("Detector cannot export sources.")

    def importSettings(self, settings):
        logger.logger.debug("Detector cannot import settings.")

    def exportSettings(self):
        logger.logger.debug("Detector cannot export settings.")

    @identifying
    def identify(self, data):
        logger.logger.debug("Detector doesn't support image identification.")

    @verifying
    def verify(self, data):
        logger.logger.debug("Detector doesn't support image verification.")

    def detect(self, data):
        logger.logger.debug("Detector doesn't support image detection.")

    def compare(self, f_imgobj, s_imgobj):
        logger.logger.debug("Detector doesn't support image comparison.")

    def data_detect(self, data):
        # ROI detection
        if self._use_roi:
            # rect = self._cascadeROI.detectAndJoin(data['data'], False, RectsFiltering)
            img, rect = self._cascadeROI.detectAndJoinWithRotation(data['data'], False, RectsFiltering)
            if len(rect) <= 0:
                return False
            print rect
            # ROI cutting
            data['data'] = img
            data['roi'] = getROIImage(data['data'], rect)
        else:
            data['roi'] = data['data']
        # Keypoints detection
        detector = FeatureDetector()
        if self.kodsettings.detector_type is BRISKDetectorType:
            brisk_detector = BRISKDetector(self.kodsettings.brisk_settings.thresh,
                                           self.kodsettings.brisk_settings.octaves,
                                           self.kodsettings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            orb_detector = ORBDetector(self.kodsettings.orb_settings.features,
                                       self.kodsettings.orb_settings.scaleFactor,
                                       self.kodsettings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        try:
            obj = detector.detectAndComputeImage(data['roi'])
        except Exception as err:
            logger.logger.debug(err.message)
            return False
        data['keypoints'] = obj['keypoints']
        data['descriptors'] = obj['descriptors']
        if data['descriptors'] is None:
            data['descriptors'] = []
        return self._detect(data, detector)

    def _detect(self, data, detector):
        return True

    def update_hash(self, data):
        logger.logger.debug("The hash does not need to be updated!")

    def update_database(self):
        logger.logger.debug("The database does not need to be updated!")