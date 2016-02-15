from biomio.algorithms.features.matchers import Matcher
from biomio.algorithms.clustering import FOREL, KMeans
from biomio.algorithms.recognition.keypoints import KeypointsObjectDetector
from biomio.algorithms.cvtools.visualization import (drawClusters, drawLine, showClusters, drawSelfGraph, drawKeypoints)
from biomio.algorithms.cvtools.system import saveNumpyImage
from biomio.algorithms.features.matchers import SelfGraph
from biomio.algorithms.features import matcherForDetector, BRISKDetectorType, ORBDetectorType
from biomio.algorithms.cascades.detectors import OptimalROIDetectorSAoS
from biomio.algorithms.cascades.scripts_detectors import CascadesDetectionInterface
from biomio.algorithms.cascades.tools import loadScript
from biomio.algorithms.logger import logger


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._cascadeROI = OptimalROIDetectorSAoS()
        self._eyeROI = CascadesDetectionInterface(loadScript("main_haarcascade_eyes_union.json", True))
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

    def _detect(self, data, detector):
        # ROI detection
        rect = self._eyeROI.detect(data['roi'])[1]
        if len(rect) <= 0 or len(rect[0]) <= 0:
            logger.info("Eye ROI wasn't found.")
            self._last_error = "Eye ROI wasn't found."
            return False
        # ROI cutting
        rect = rect[0]
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[1] - lefteye[1]) / 2)
        centernose = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        centermouth = (centernose[0], centernose[1] + rect[3])
        leftmouth = (lefteye[0], centermouth[1])
        rightmouth = (righteye[0], centermouth[1])
        # out = drawLine(data['roi'], (lefteye[0], lefteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centereye[0], centereye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (righteye[0], righteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centermouth[0], centermouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (leftmouth[0], leftmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (rightmouth[0], rightmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        centers = [lefteye, righteye, centereye, centernose, leftmouth, rightmouth]
        # self.filter_keypoints(data)

        clusters = KMeans(data['keypoints'], 0, centers)
        # clusters = FOREL(obj['keypoints'], 40)
        # showClusters(clusters, out)
        data['true_clusters'] = clusters
        descriptors = []
        centers = []
        weights = []
        keydescriptors = []
        for cluster in clusters:
            desc = detector.compute(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
            centers.append(cluster['center'])
            pairs = []
            sum = 0
            for index, item in enumerate(cluster['items']):
                # pairs.append((desc['descriptors'][index], item.response))
                sum += item.response
            weights.append((pairs, sum))
            cluster_keypoints = []
            for index, item in enumerate(cluster['items']):
                cluster_keypoints.append((item, desc['descriptors'][index]))
            keydescriptors.append(cluster_keypoints)
        data['clusters'] = descriptors
        data['centers'] = centers
        data['weights'] = weights
        data['key_desc'] = keydescriptors
        logger.debug("!!!Keypoints!!!")
        logger.debug(len(data['keypoints']))

        # logger.logger.debug(os.path.join("D:\Projects\Biomio\Test1", "roi", data['name'] + ".jpg"))
        # saveNumpyImage(os.path.join("D:/Projects/Biomio/Test1/roi", data['name'] + ".jpg"), data['roi'])
        # data['keypoints_image'] = drawKeypoints(data, 'roi')
        # for idx, cluster in enumerate(data['true_clusters']):
        #     self_graph = SelfGraph(cluster['items'], 3, data['clusters'][idx])
        #     data['keypoints_image'] = drawSelfGraph(data, self_graph, key='keypoints_image')
        # import cv2
        # cv2.imshow("Window", data['keypoints_image'])
        # cv2.waitKey()
        return True

    def filter_keypoints(self, data):
        clusters = FOREL(data['keypoints'], 20)
        keypoints = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            if p > 0.02:
                keypoints += [item for item in cluster['items']]
        data['keypoints'] = keypoints
