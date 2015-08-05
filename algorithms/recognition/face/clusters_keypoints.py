from algorithms.features.matchers import Matcher
from algorithms.clustering.forel import FOREL
from algorithms.clustering.kmeans import KMeans
from algorithms.cascades.classifiers import CascadeROIDetector
from algorithms.recognition.keypoints import (KeypointsObjectDetector,
                                              BRISKDetectorType)
from algorithms.cvtools.visualization import (drawClusters, drawLine, showClusters)
from algorithms.features import matcherForDetector, dtypeForDetector
import logger


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = []
        self._etalon = []
        self._prob = 100
        self._coff = 0.9

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
        info['Database Size'] = str(len(self._hash)) + " images"
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
            logger.logger.debug("Settings loading started...")
            self.kodsettings.importSettings(settings['KODSettings'])
            self.kodsettings.dump()
            if self._cascadeROI is None:
                self._cascadeROI = CascadeROIDetector()
            self._cascadeROI.importSettings(settings['Face Cascade Detector'])
            logger.logger.debug('Face Cascade Detector')
            self._cascadeROI.classifierSettings.dump()
            if self._eyeROI is None:
                self._eyeROI = CascadeROIDetector()
            self._eyeROI.importSettings(settings['Eye Cascade Detector'])
            logger.logger.debug('Eye Cascade Detector')
            self._eyeROI.classifierSettings.dump()
            logger.logger.debug("Settings loading finished.")
            return True
        return False

    def exportSettings(self):
        info = dict()
        info['KODSettings'] = self.kodsettings.exportSettings()
        info['Face Cascade Detector'] = self._cascadeROI.exportSettings()
        info['Eye Cascade Detector'] = self._eyeROI.exportSettings()
        return info

    def compare(self, f_imgobj, s_imgobj):
        if not self.data_detect(f_imgobj):
            logger.logger.debug("First image data isn't valid.")
            return False
        if not self.data_detect(s_imgobj):
            logger.logger.debug("Second image data isn't valid.")
            return False
        # matcher = FlannMatcher()
        # gres = []
        # for i in range(0, len(f_imgobj['clusters'])):
        # first = f_imgobj['clusters'][i]
        # second = s_imgobj['clusters'][i]
        #     res = []
        #     if (first is None) or (second is None):
        #         logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
        #         self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
        #     else:
        #         matches = matcher.knnMatch(first, second, k=1)
        #         ms = []
        #         for v in matches:
        #             if len(v) >= 1:
        #                 # if len(v) >= 2:
        #                 m = v[0]
        #                 # n = v[1]
        #                 if m.distance < self.kodsettings.neighbours_distance:
        #                     ms.append(m)
        #         prob = len(ms) / (1.0 * len(matches))
        #         res.append(prob * 100)
        #         logger.logger.debug("Cluster #" + str(i + 1) + " (Size: " + str(len(second)) + "): "
        #                             + str(prob * 100) + "%")
        #         self._log += "Cluster #" + str(i + 1) + " (Size: " + str(len(second)) + "): " + str(prob * 100) \
        #                      + "%" + "\n"
        #     suma = 0
        #     for val in res:
        #         suma += val
        #     logger.logger.debug("Total for image: " + str(suma / len(res)))
        #     self._log += "Total for image: " + str(suma / len(res)) + "\n"
        #     gres.append(suma / len(res))
        # s = 0
        # for val in gres:
        #     s += val
        # logger.logger.debug("Total: " + str(s / len(gres)))
        # self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        self._compare_descriptors(f_imgobj, s_imgobj)

    def _compare_descriptors(self, f_imgobj, s_imgobj):
        matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))
        matches = matcher.knnMatch(f_imgobj['descriptors'], s_imgobj['descriptors'], k=1)
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        stat = dict()
        for v in matches:
            if len(v) >= 1:
                # if len(v) >= 2:
                m = v[0]
                logger.logger.debug("Query Index: " + str(m.queryIdx) + " Train Index: " + str(m.trainIdx)
                                    + " Distance: " + str(m.distance))
                for i in range(0, 100, 1):
                    if m.distance <= i * 10:
                        val = stat.get(str(i * 10), 0)
                        val += 1
                        stat[str(i * 10)] = val
                        break
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        for k, z in stat.iteritems():
            logger.logger.debug(k + ": " + str(z))
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.logger.debug("First image descriptors number: " + str(len(f_imgobj['descriptors'])))
        logger.logger.debug("Second image descriptors number: " + str(len(s_imgobj['descriptors'])))
        ms = []
        for v in matches:
            if len(v) >= 1:
                # if len(v) >= 2:
                m = v[0]
                # n = v[1]
                if m.distance < self.kodsettings.neighbours_distance:
                    ms.append(m)
        prob = len(ms) / (1.0 * len(matches))
        logger.logger.debug("Positive matches: " + str(len(ms)) + " Probability: " + str(prob * 100))
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def _detect(self, data, detector):
        # ROI detection
        rect = self._eyeROI.detectAndJoin(data['roi'], False)
        if len(rect) <= 0:
            return False
        # ROI cutting
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[1] - lefteye[1]) / 2)
        centernose = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        centermouth = (centernose[0], centernose[1] + rect[3])
        leftmouth = (lefteye[0], centermouth[1])
        rightmouth = (righteye[0], centermouth[1])
        out = drawLine(data['roi'], (lefteye[0], lefteye[1], centernose[0], centernose[1]), (255, 0, 0))
        out = drawLine(out, (centereye[0], centereye[1], centernose[0], centernose[1]), (255, 0, 0))
        out = drawLine(out, (righteye[0], righteye[1], centernose[0], centernose[1]), (255, 0, 0))
        out = drawLine(out, (centermouth[0], centermouth[1], centernose[0], centernose[1]), (255, 0, 0))
        out = drawLine(out, (leftmouth[0], leftmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        out = drawLine(out, (rightmouth[0], rightmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        centers = [lefteye, righteye, centereye, centernose, leftmouth, rightmouth]
        # self.filter_keypoints(data)

        clusters = KMeans(data['keypoints'], 0, centers, 3)
        # clusters = FOREL(obj['keypoints'], 40)
        showClusters(clusters, out)
        data['true_clusters'] = clusters
        descriptors = []
        for cluster in clusters:
            desc = detector.compute(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
        data['clusters'] = descriptors
        return True

    def filter_keypoints(self, data):
        def point(item):
            return item.pt
        clusters = FOREL(data['keypoints'], 20, point)
        keypoints = []
        # cls = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            img = dict()
            img['data'] = data['roi']
            img['keypoints'] = cluster['items']
            if p > 0.02:
                # cls.append(cluster)
                for item in cluster['items']:
                    keypoints.append(item)
        data['keypoints'] = keypoints
