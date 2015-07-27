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

                            if v[0].distance == 0:
                                best = v[0]
                            else:
                                best = max(v, key=(lambda m:
                                                   next((c / (1.0 * m.distance) for (d, c) in et_cluster
                                                         if numpy.array_equal(d, ob_cluster[m.trainIdx])), -1
                                                        )
                                                   )
                                           )

                            # et_cluster_ob = [(d, c + 1) for (d, c) in et_cluster
                            #                  if numpy.array_equal(d, ob_cluster[best.trainIdx])]
                            #
                            # if len(et_cluster_ob) == 0:
                            #     et_cluster_ob.append((ob_cluster[best.trainIdx], 1))
                            #
                            # et_cluster_dt = [(d, c + 1) for (d, c) in et_cluster
                            #                  if numpy.array_equal(d, dt_cluster[best.queryIdx])]
                            #
                            # if len(et_cluster_dt) == 0:
                            #     et_cluster_dt.append((dt_cluster[best.queryIdx], 1))
                            #
                            # et_cluster_res = et_cluster_ob + et_cluster_dt
                            # logger.logger.debug("new")
                            # logger.logger.debug(et_cluster_ob)
                            # logger.logger.debug(et_cluster_dt)

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
                            # logger.logger.debug("old")
                            # logger.logger.debug(new_cluster)
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

        def _values(d, key=None):
            l = sorted(d, key=key)
            for e in l:
                yield d[e]

        self._etalon = [
            [
                (listToNumpy_ndarray(desc_dict['descriptor']), int(desc_dict['count']))
                for desc_dict in _values(cluster, key=int)
            ] for cluster in _values(source, key=int)
        ]

    def exportSources(self):
        data = self.exportSources_L1Template()
        source = dict()
        if len(data.keys()) > 0:
            source = dict()
            source['data'] = data
            source['threshold'] = self._prob
        return source

    def exportSources_L1Template(self):
        return {
            str(index): {
                str(i): {
                    'descriptor': numpy_ndarrayToList(d),
                    'count': c
                } for (i, (d, c)) in enumerate(et_weight_cluster)
            } for (index, et_weight_cluster) in enumerate(self._etalon)
        }

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
