from biomio.algorithms.recognition.keypoints import KeypointsObjectDetector
from biomio.algorithms.cvtools.visualization import (drawClusters, drawLine, showClusters, drawSelfGraph, drawKeypoints,
                                                     drawCircle)
from biomio.algorithms.features import matcherForDetector, BRISKDetectorType, ORBDetectorType
from biomio.algorithms.cascades.detectors import OptimalROIDetectorSAoS
from biomio.algorithms.cascades.scripts_detectors import CascadesDetectionInterface
from processing.feature_clusteringL0_process import FeatureClusteringL0Processing
from processing.feature_clusteringL1_process import FeatureClusteringL1Processing
from processing.clusters.static_cc_detector import StaticCCDetector
from biomio.algorithms.cascades.tools import loadScript
from biomio.algorithms.logger import logger


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._cascadeROI = OptimalROIDetectorSAoS()
        self._eyeROI = CascadesDetectionInterface(loadScript("main_haarcascade_eyes_union.json", True))
        # self._feature_processor = FeatureClusteringL0Processing(StaticCCDetector(self._eyeROI))
        self._feature_processor = FeatureClusteringL1Processing(StaticCCDetector(self._eyeROI))
        self._database = []
        self._etalon = []
        self._prob = 100
        self._coff = 0.9

    def get_template(self):
        return self._etalon

    def threshold(self):
        return self.kodsettings.probability

    def detect(self, data):
        if self.data_detect(data):
            data['clustering'] = drawClusters(data['true_clusters'], data['roi'])

    def importDBSettings(self, settings):
        detector = settings.get('Detector Settings', dict())
        if settings.get('Detector Type') == 'BRISK':
            self.kodsettings.detector_type = BRISKDetectorType
            self.kodsettings.brisk_settings.thresh = detector['Thresh']
            self.kodsettings.brisk_settings.octaves = detector['Octaves']
            self.kodsettings.brisk_settings.patternScale = detector['Pattern Scale']
        elif settings.get('Detector Type') == 'ORB':
            self.kodsettings.detector_type = ORBDetectorType
            self.kodsettings.orb_settings.features = detector['Number of features']
            self.kodsettings.orb_settings.scaleFactor = detector['Scale Factor']
            self.kodsettings.orb_settings.nlevels = detector['Number of levels']

    def exportDBSettings(self):
        info = dict()
        info['Database Size'] = str(len(self._database)) + " images"
        settings = dict()
        if self.kodsettings.detector_type == BRISKDetectorType:
            info['Detector Type'] = 'BRISK'
            settings['Thresh'] = self.kodsettings.brisk_settings.thresh
            settings['Octaves'] = self.kodsettings.brisk_settings.octaves
            settings['Pattern Scale'] = self.kodsettings.brisk_settings.patternScale
        elif self.kodsettings.detector_type == ORBDetectorType:
            info['Detector Type'] = 'ORB'
            settings['Number of features'] = self.kodsettings.orb_settings.features
            settings['Scale Factor'] = self.kodsettings.orb_settings.scaleFactor
            settings['Number of levels'] = self.kodsettings.orb_settings.nlevels
        info['Detector Settings'] = settings
        face_cascade = dict()
        face_cascade['Cascades'] = self._cascadeROI.cascades()
        face_settings = dict()
        face_settings['Scale Factor'] = self._cascadeROI.classifierSettings.scaleFactor
        face_settings['Minimum Neighbors'] = self._cascadeROI.classifierSettings.minNeighbors
        face_settings['Minimum Size'] = self._cascadeROI.classifierSettings.minSize
        face_cascade['Settings'] = face_settings
        info['Face Cascade Detector'] = face_cascade
        info['Database Source'] = "Extended Yale Face Database B. Person Yale12"
        return info

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            logger.info("Settings loading started...")
            self.kodsettings.importSettings(settings['KODSettings'])
            self.kodsettings.dump()
            if self._cascadeROI is None:
                self._cascadeROI = OptimalROIDetectorSAoS()
                # self._cascadeROI = CascadeROIDetector()
            # self._cascadeROI.importSettings(settings['Face Cascade Detector'])
            # logger.logger.debug('Face Cascade Detector')
            # self._cascadeROI.classifierSettings.dump()
            if self._eyeROI is None:
                self._eyeROI = CascadesDetectionInterface(loadScript("main_haarcascade_eyes_union.json", True))
                # self._eyeROI = CascadeROIDetector()
            # self._eyeROI.importSettings(settings['Eye Cascade Detector'])
            # logger.logger.debug('Eye Cascade Detector')
            # self._eyeROI.classifierSettings.dump()
            logger.debug("Settings loading finished.")
            return True
        return False

    def exportSettings(self):
        info = dict()
        info['KODSettings'] = self.kodsettings.exportSettings()
        info['Face Cascade Detector'] = self._cascadeROI.exportSettings()
        info['Eye Cascade Detector'] = self._eyeROI.exportSettings()
        return info
