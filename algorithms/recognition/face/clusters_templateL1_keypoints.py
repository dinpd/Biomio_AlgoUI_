from algorithms.features.matchers import Matcher, BruteForceMatcherType
from algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from algorithms.recognition.keypoints import verifying
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
import logger
import numpy


class ClustersTemplateL1MatchingDetector(ClustersMatchingDetector):
    def __init__(self):
        ClustersMatchingDetector.__init__(self)

    def update_hash(self, data):
        del data['keypoints']
        del data['descriptors']
        self._hash.append(data)
        self.update_hash_templateL1(data)

    def update_hash_templateL1(self, data):
        """

        max_weight = se*sum(i=1,k-1: 1+2*i) + k*(n-k)*se,
        where
            n - count of images,
            k - count of identical matches, k <= n,
            se - single estimate, I used se=1

        :param data:
        :return:
        """
        if len(self._hash) == 1:
            self._etalon = map(lambda cluster:
                               [] if cluster is None else [(desc, 1) for desc in cluster],
                               data['clusters'])
        else:
            matcher = Matcher(BruteForceMatcherType)
            for index, et_cluster in enumerate(self._etalon):
                dt_cluster = data['clusters'][index]
                if dt_cluster is None or len(dt_cluster) == 0:
                    continue
                for obj in self._hash:
                    if data['path'] == obj['path']:
                        continue
                    ob_cluster = obj['clusters'][index]
                    if ob_cluster is None or len(ob_cluster) == 0:
                        continue
                    matches1 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster),
                                                listToNumpy_ndarray(ob_cluster), k=5)
                    for v in matches1:
                        if len(v) >= 1:
                            best = v[0]
                            if best.distance != 0:
                                dist = - 1
                                for m in v:
                                    for d, c in et_cluster:
                                        if numpy.array_equal(d, ob_cluster[m.trainIdx]):
                                            if dist < c / (1.0 * m.distance):
                                                dist = c / (1.0 * m.distance)
                                                best = m
                                            break
                            ob_is = False
                            dt_is = False
                            new_cluster = []
                            for d, c in et_cluster:
                                if numpy.array_equal(d, ob_cluster[best.trainIdx]):
                                    c += 1
                                    ob_is = True
                                if numpy.array_equal(d, dt_cluster[best.queryIdx]):
                                    c += 1
                                    dt_is = True
                                new_cluster.append((d, c))
                            if not ob_is:
                                new_cluster.append((ob_cluster[best.trainIdx], 1))
                            if not dt_is:
                                new_cluster.append((dt_cluster[best.queryIdx], 1))
                            et_cluster = new_cluster
                    self._etalon[index] = et_cluster

    def importSources(self, source):
        self._etalon = []
        logger.logger.debug("Database loading started...")
        self.importSources_L1Template(source.get('data', dict()))
        self._prob = source.get('threshold', 100)
        logger.logger.debug("Database loading finished.")

    def importSources_L1Template(self, source):
        for j in range(0, len(source.keys())):
            self._etalon.append([])
        for c_num, cluster in source.iteritems():
            etalon_cluster = []
            for k in range(0, len(cluster.keys())):
                etalon_cluster.append([])
            for d_num, desc_dict in cluster.iteritems():
                etalon_cluster[int(d_num)] = (listToNumpy_ndarray(desc_dict['descriptor']),
                                              int(desc_dict['count']))
            self._etalon[int(c_num)] = etalon_cluster

    def exportSources(self):
        data = self.exportSources_L1Template()
        source = dict()
        if len(data.keys()) > 0:
            source = dict()
            source['data'] = data
            source['threshold'] = self._prob
        return source

    def exportSources_L1Template(self):
        sources = dict()
        for index in range(0, len(self._etalon)):
            et_weight_cluster = self._etalon[index]
            cluster = dict()
            i = 0
            for d, c in et_weight_cluster:
                obj = dict()
                # desc_dict = dict()
                # for indx in range(0, len(d)):
                # desc_dict[str(indx)] = str(d[indx])
                obj['descriptor'] = numpy_ndarrayToList(d)
                obj['count'] = c
                cluster[str(i)] = obj
                i += 1
            sources[str(index)] = cluster
        return sources

    @verifying
    def verify(self, data):
        return self.verify_template_L1(data)

    def verify_template_L1(self, data):
        matcher = Matcher(BruteForceMatcherType)
        res = []
        prob = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        for index in range(0, len(self._etalon)):
            et_weight_cluster = self._etalon[index]
            et_cluster = []
            cluster_weight = 0
            for d, c in et_weight_cluster:
                if c > 0:
                    et_cluster.append(d)
                    cluster_weight += c
            dt_cluster = data['clusters'][index]
            ms = []
            if et_cluster is None or dt_cluster is None:
                continue
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster, numpy.uint8),
                                            listToNumpy_ndarray(dt_cluster, numpy.uint8), k=2)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, numpy.uint8),
                                            listToNumpy_ndarray(et_cluster, numpy.uint8), k=2)
                # for v in matches:
                # if len(v) >= 1:
                # if len(v) >= 2:
                # m = v[0]
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
                                            ms.append(et_cluster[m.queryIdx])
                c_val = 0
                for item in ms:
                    for d, c in et_weight_cluster:
                        if numpy.array_equal(d, item):
                            c_val += c
                res.append(c_val / cluster_weight)
                val = (c_val / (1.0 * cluster_weight)) * 100
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight)
                                        + " Positive: " + str(c_val) + " Probability: " + str(val))
                self._log += "Cluster #" + str(index + 1) + ": " + str(cluster_weight) \
                             + " Positive: " + str(c_val) + " Probability: " + str(val) + "\n"
                prob += val
            else:
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight)
                                        + " Invalid.")
                self._log += "Cluster #" + str(index + 1) + ": " + str(cluster_weight) + " Invalid.\n"
        logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        return prob / (1.0 * len(res))
