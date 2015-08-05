from algorithms.cascades.classifiers import (getROIImage, RectsFiltering)
from algorithms.features.features import (FeatureDetector)
from algorithms.features import (constructDetector, constructSettings,
                                 BRISKDetectorType)
from algorithms.cascades.roi import optimalROIDetection
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
    settings = None
    probability = 25.0

    def exportSettings(self):
        return {
            'Neighbours Distance': self.neighbours_distance,
            'Probability': self.probability,
            'Detector Type': self.detector_type,
            'Detector Settings': self.settings.exportSettings()
        }

    def importSettings(self, settings):
        self.neighbours_distance = settings['Neighbours Distance']
        self.probability = settings['Probability']
        self.detector_type = settings.get('Detector Type')
        self.settings = constructSettings(self.detector_type)
        self.settings.importSettings(settings.get('Detector Settings', dict()))

    def dump(self):
        logger.logger.debug('Keypoints Objects Detectors Settings')
        logger.logger.debug('Neighbours Distance: %f' % self.neighbours_distance)
        logger.logger.debug('Probability: %f' % self.probability)
        logger.logger.debug('Detector Type: %s' % self.detector_type)
        self.settings.dump()


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
        if self._sources_preparing:
            self._prepare_sources([data])
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
        self._use_roi = True
        self._sources_preparing = True
        self._log = ""

    def threshold(self):
        return self.kodsettings.probability

    def log(self):
        return self._log

    def setUseROIDetection(self, use):
        self._use_roi = use

    def addSource(self, data):
        logger.logger.debug(data['path'])
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        if self._sources_preparing:
            self._prepare_sources(data_list)
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
        detector = FeatureDetector(constructDetector(self.kodsettings.detector_type, self.kodsettings.settings))
        try:
            obj = detector.detectAndCompute(data['roi'])
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

    def _prepare_sources(self, data_list):
        self._use_roi = False
        optimalROIDetection(data_list)

    def update_hash(self, data):
        logger.logger.debug("The hash does not need to be updated!")

    def update_database(self):
        logger.logger.debug("The database does not need to be updated!")