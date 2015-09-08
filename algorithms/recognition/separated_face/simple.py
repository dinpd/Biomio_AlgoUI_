from algorithms.recognition.keypoints import KeypointsObjectDetector, verifying
from algorithms.features import matcherForDetector, constructDetector
from algorithms.cascades.roi_optimal import OptimalROIDetectorSAoS
from algorithms.features.features import FeatureDetector
from algorithms.features.matchers import Matcher
import logger


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)

    def update_hash(self, data):
        self._hash.append(data)

    def _detect_model(self):
        return {
            "eye": OptimalROIDetectorSAoS()
        }

    def data_detect(self, data):
        models = self._detect_model()
        if len(models.keys()) > 0:
            detector = FeatureDetector(constructDetector(self.kodsettings.detector_type,
                                                         self.kodsettings.settings))
            keypoints = dict()
            descriptors = dict()
            for key, value in models.iteritems():
                value.detect([data])
                data['roi'] = data['data']
                try:
                    obj = detector.detectAndCompute(data['roi'])
                    keypoints[key] = obj['keypoints']
                    if data['descriptors'] is None:
                        descriptors[key] = []
                    else:
                        descriptors[key] = obj['descriptors']
                except Exception as err:
                    logger.logger.debug(err.message)
            data['keypoints'] = keypoints
            data['descriptors'] = descriptors
            return self._detect(data, detector)
        else:
            logger.logger.debug("Model for detection is empty.")
            return False

    @verifying
    def verify(self, data):
        knn = 2
        matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))
        res = []
        ddescriptors = data['descriptors']
        for index, source in enumerate(self._hash):
            sdescriptors = source['descriptors']


        prob = 0
        prob1 = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        summ = sum(itertools.imap(lambda x: len(x) if x is not None else 0, self._etalon))
        for index in range(0, len(self._etalon)):
            et_cluster = self._etalon[index]
            dt_cluster = data['clusters'][index]
            et_weights = self._w_clusters[index]
            ms = []
            ms1 = 0
            if et_cluster is None or len(et_cluster) < knn:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(-1)
                                        + " Invalid. (Weight: 0)")
                continue
            if dt_cluster is None or len(dt_cluster) < knn:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: 0 Probability: 0 (Weight: " +
                                        str(len(et_cluster) / (1.0 * summ)) + ")")
                continue
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                dtype = dtypeForDetector(self.kodsettings.detector_type)
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster, dtype),
                                            listToNumpy_ndarray(dt_cluster, dtype), k=knn)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, dtype),
                                            listToNumpy_ndarray(et_cluster, dtype), k=knn)
                # logger.logger.debug("########")
                # for v in matches1:
                #     if len(v) >= 1:
                #         for m in v:
                #             logger.logger.debug(m.distance)
                # logger.logger.debug("########")
                # for c in matches2:
                #     if len(c) >= 1:
                #         for n in c:
                #             logger.logger.debug(n.distance)
                # logger.logger.debug("########")
                # for v in matches:
                # if len(v) >= 1:
                # if len(v) >= 2:
                #     m = v[0]
                # n = v[1]
                # logger.logger.debug(str(m.distance) + " " + str(m.queryIdx) + " " + str(m.trainIdx) + " | "
                #                     + str(n.distance) + " " + str(n.queryIdx) + " " + str(n.trainIdx))
                # if m.distance < self.kodsettings.neighbours_distance:
                # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                #     ms.append(m)
                # else:
                #     ms.append(m)
                #     ms.append(n)
                for v in matches1:
                    if len(v) >= 1:
                        for m in v:
                            # m = v[0]
                            for c in matches2:
                                if len(c) >= 1:
                                    for n in c:
                                        # n = c[0]
                                        if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                            ms.append(m)
                                            # logger.logger.debug("########")
                                            # logger.logger.debug(m.distance)
                                            # logger.logger.debug(n.distance)
                                            for desc, resp in et_weights[0]:
                                                if numpy.array_equal(et_cluster[m.queryIdx], desc):
                                                    ms1 += resp
                                                    break
                res.append(ms)
                val = (len(res[index]) / (1.0 * len(self._etalon[index]))) * 100
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: " + str(len(res[index])) + " Probability: " + str(val) +
                                        " (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")")
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) \
                             + " Positive: " + str(len(res[index])) + " Probability: " + str(val) + "\n"
                prob += (len(et_cluster) / (1.0 * summ)) * val

                vv = (ms1 / et_weights[1]) * val
                logger.sys_logger.debug("test Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: " + str(len(res[index])) + " Probability: " + str(vv) +
                                        " (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ", " +
                                        str(ms1 / et_weights[1]) + ")")
                # prob1 += (len(et_cluster) / (1.0 * summ)) * vv
                prob1 += vv / (1.0 * len(self._etalon))
            else:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Invalid.")
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) + " Invalid.\n"
        # logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        # self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        # return prob / (1.0 * len(res))
        logger.sys_logger.debug("Probability: " + str(prob))
        logger.sys_logger.debug("test Probability: " + str(prob1))
        self._log += "Probability: " + str(prob) + "\n"
        return prob