from biomio.algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from biomio.algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
from biomio.algorithms.recognition.estimation import ClusterL0Estimation, SelfGraphEstimation, \
    SelfGraphNoClusterEstimation, CROSS_DISTANCE_MODE, FULL_DISTANCE_MODE, LOWES_DISTANCE_MODE, DEFAULT_MODE, \
    SelfGraphDistanceEstimation
from biomio.algorithms.recognition.keypoints import verifying
from biomio.algorithms.logger import logger
import sys


class ClustersTemplateL0MatchingDetector(ClustersMatchingDetector):
    def __init__(self):
        ClustersMatchingDetector.__init__(self)
        self._w_clusters = None
        self._etalon = {}

    def threshold(self):
        return self._coff * self._prob

    def update_hash(self, data):
        del data['keypoints']
        del data['descriptors']
        self._database.append(data)
        self.update_hash_templateL0(data)

    def update_hash_templateL0(self, data):
        # estimation = ClusterL0Estimation(self.kodsettings.detector_type, knn=3, max_distance=0.9,
        #                                  mode=DEFAULT_MODE)
        estimation = SelfGraphEstimation(self.kodsettings.detector_type, knn=3)
        # estimation = SelfGraphDistanceEstimation(self.kodsettings.detector_type, knn=3)
        # estimation = SelfGraphNoClusterEstimation(self.kodsettings.detector_type, knn=3)
        # self._etalon = estimation.estimate_training(data['clusters'], self._etalon)
        self._etalon = estimation.estimate_training(data, self._etalon)
        # self._etalon = estimation.estimate_training((data['clusters'], data['centers']), self._etalon)
        # self._etalon = estimation.estimate_training(data['descriptors'], self._etalon)

    def update_database(self):
        if len(self._database) > 0:
            minv = sys.maxint
            for obj in self._database:
                res = self.verify_template_L0(obj)
                if minv > res:
                    minv = res
            self._prob = minv

    def importSources(self, source):
        logger.debug("Database loading started...")
        self._etalon = SelfGraphEstimation.importDatabase(source.get('data', dict()))
        self._prob = source.get('threshold', 100)
        logger.info('Dynamic threshold: %f' % self._prob)
        logger.debug("Database loading finished.")

    @staticmethod
    def load_database(source):
        return {
            "template": SelfGraphEstimation.importDatabase(source.get('data', dict())),
            "threshold": source.get('threshold', 100)
        }

    def exportSources(self):
        data = SelfGraphEstimation.exportDatabase(self._etalon)
        if len(data.keys()) > 0:
            return {
                'data': data,
                'threshold': self._prob
            }
        else:
            return {}

    @verifying
    def verify(self, data):
        return self.verify_template_L0(data)

    def verify_template_L0(self, data):
        # estimation = ClusterL0Estimation(self.kodsettings.detector_type, knn=2, max_distance=0.9,
        #                                  mode=DEFAULT_MODE)
        estimation = SelfGraphEstimation(self.kodsettings.detector_type, knn=8)
        # estimation = SelfGraphDistanceEstimation(self.kodsettings.detector_type, knn=1)
        # estimation = SelfGraphNoClusterEstimation(self.kodsettings.detector_type, knn=3)
        logger.debug("Image: " + data['path'])
        # return estimation.estimate_verification(data['clusters'], self._etalon)
        return estimation.estimate_verification(data, self._etalon)
        # return estimation.estimate_verification((data['clusters'], data['centers']), self._etalon)
        # return estimation.estimate_verification(data['descriptors'], self._etalon)
