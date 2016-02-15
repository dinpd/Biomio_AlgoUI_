from biomio.algorithms.features.features import (FeatureDetector)
from biomio.algorithms.recognition.kodsettings import KODSettings
from biomio.algorithms.features import (constructDetector)
from biomio.algorithms.logger import logger


def identifying(fn):
    def wrapped(self, data):
        logger.info("Identifying...")
        res = None
        if self.data_detect(self, data):
            if data is not None:
                res = fn(self, data)
        logger.info("Identifying finished.")
        return res
    return wrapped


def verifying(fn):
    def wrapped(self, data):
        logger.info("Verifying...")
        res = False
        if self._sources_preparing:
            self._prepare_sources([data])
        if self.data_detect(data):
            if data is not None:
                res = fn(self, data)
        logger.info("Verifying finished.")
        return res
    return wrapped


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self):
        self._database = None
        self._cascadeROI = None
        self._detector = None
        self._eyeROI = None
        self._use_roi = True
        self._sources_preparing = False
        self._last_error = ""

    def threshold(self):
        return self.kodsettings.probability

    def last_error(self):
        return self._last_error

    def setUseROIDetection(self, use):
        self._use_roi = use

    def addSource(self, data):
        self._last_error = ""
        logger.info("Training started...")
        logger.info(data['path'])
        if self.data_detect(data):
            self.update_hash(data)
            logger.info("Training finished.")
            return True
        logger.info("Training finished.")
        return False

    def addSources(self, data_list):
        if self._sources_preparing:
            data_list = self._prepare_sources(data_list)
        count = 0
        for data in data_list:
            res = self.addSource(data)
            if res:
                count += 1
        return count

    def importSources(self, data):
        logger.info("Detector cannot import sources.")

    def exportSources(self):
        logger.info("Detector cannot export sources.")

    def importSettings(self, settings):
        logger.info("Detector cannot import settings.")

    def exportSettings(self):
        logger.info("Detector cannot export settings.")

    @identifying
    def identify(self, data):
        logger.info("Detector doesn't support image identification.")

    @verifying
    def verify(self, data):
        logger.info("Detector doesn't support image verification.")

    def detect(self, data):
        logger.info("Detector doesn't support image detection.")

    def data_detect(self, data):
        # ROI detection
        if self._use_roi:
            self._cascadeROI.detect([data])
            data['roi'] = data['data']
        else:
            data['roi'] = data['data']
        # Keypoints detection
        detector = FeatureDetector(constructDetector(self.kodsettings.detector_type, self.kodsettings.settings))
        try:
            obj = detector.detectAndCompute(data['roi'])
        except Exception as err:
            logger.debug(err.message)
            self._last_error = err.message
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
        data_list = self._cascadeROI.detect(data_list)
        return data_list

    def update_hash(self, data):
        logger.info("The hash does not need to be updated!")

    def update_database(self):
        logger.info("The database does not need to be updated!")
