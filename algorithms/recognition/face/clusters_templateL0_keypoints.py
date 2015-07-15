import multiprocessing as mp
import sys

import numpy

from algorithms.features.matchers import Matcher, BruteForceMatcherType
from algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from algorithms.recognition.keypoints import verifying
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
import logger

PROCESS_COUNT = 8 # mp.cpu_count()


def parallel_update_hash_templateL0(etalon, data, index):
    matcher = Matcher(BruteForceMatcherType)
    et_cluster = etalon[index]
    dt_cluster = data[index]
    if et_cluster is None or len(et_cluster) == 0:
        return index, et_cluster
    elif dt_cluster is None or len(dt_cluster) == 0:
        return index, et_cluster
    else:
        matches1 = matcher.knnMatch(et_cluster, dt_cluster, k=3)
        matches2 = matcher.knnMatch(dt_cluster, et_cluster, k=3)

        good = []

        for v in matches1:
            if len(v) >= 1:
                for m in v:
                    # m = v[0]
                    for c in matches2:
                        if len(c) >= 1:
                            for n in c:
                                # n = c[0]
                                    if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                        good.append(et_cluster[m.queryIdx])
                                        good.append(dt_cluster[m.trainIdx])
        return index, listToNumpy_ndarray(good)


def parallel_verify_template_L0(etalon, data, index):
    matcher = Matcher(BruteForceMatcherType)
    et_cluster = etalon[index]
    dt_cluster = data[index]
    ms = []
    val = 0
    if ((et_cluster is None or dt_cluster is None) or
            (len(et_cluster) <= 0 or len(dt_cluster) <= 0)):
        logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(etalon[index]))
                                + " Invalid.")
            # self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) + " Invalid.\n"
    else:
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
            #  else:
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
        val = (len(ms) / (1.0 * len(etalon[index]))) * 100
        logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(etalon[index]))
                                + " Positive: " + str(len(ms)) + " Probability: " + str(val))
            # self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) \
            #              + " Positive: " + str(len(ms)) + " Probability: " + str(val) + "\n"
    return val, len(ms)


class ClustersTemplateL0MatchingDetector(ClustersMatchingDetector):
    def __init__(self):
        ClustersMatchingDetector.__init__(self)

    def threshold(self):
        return self._coff * self._prob

    def update_hash(self, data):
        del data['keypoints']
        del data['descriptors']
        self._hash.append(data)
        self.update_hash_templateL0(data)

    def update_hash_templateL0(self, data):
        # self.update_hash_templateL0_parallel(data)
        self.update_hash_templateL0_noparallel(data)

    def update_hash_templateL0_parallel(self, data):
        if len(self._etalon) == 0:
            self._etalon = data['clusters']
        else:
            pool = mp.Pool(processes=PROCESS_COUNT)
            res = [pool.apply(parallel_update_hash_templateL0, args=(self._etalon, data['clusters'], x))
                   for x in range(len(self._etalon))]

            for i, cluster in res:
                self._etalon[i] = cluster

    def update_hash_templateL0_noparallel(self, data):
        if len(self._etalon) == 0:
            self._etalon = data['clusters']
        else:
            matcher = Matcher(BruteForceMatcherType)
            for index in range(0, len(self._etalon)):
                et_cluster = self._etalon[index]
                dt_cluster = data['clusters'][index]
                if et_cluster is None or len(et_cluster) == 0:
                    self._etalon[index] = et_cluster
                elif dt_cluster is None or len(dt_cluster) == 0:
                    self._etalon[index] = et_cluster
                else:
                    matches1 = matcher.knnMatch(et_cluster, dt_cluster, k=3)
                    matches2 = matcher.knnMatch(dt_cluster, et_cluster, k=3)

                    good = []
                    # for v in matches:
                    # if len(v) >= 1:
                    # if len(v) >= 2:
                    # m = v[0]
                    #     n = v[1]
                    #     good.append(self.etalon[m.queryIdx])
                    #     if m.distance < self.kodsettings.neighbours_distance:
                    #         good.append(self.etalon[m.queryIdx])
                    #     good.append(data['descriptors'][m.queryIdx])
                    #     good.append(self.etalon[m.trainIdx])
                    #
                    #     if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    #         good.append(self.etalon[m.queryIdx])
                    #     else:
                    #         good.append(self.etalon[m.queryIdx])
                    #         good.append(data['descriptors'][m.trainIdx])
                    #         good.append(data['descriptors'][m.queryIdx])
                    #         good.append(self.etalon[m.trainIdx])

                    for v in matches1:
                        if len(v) >= 1:
                            for m in v:
                                # m = v[0]
                                for c in matches2:
                                    if len(c) >= 1:
                                        for n in c:
                                            # n = c[0]
                                            if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                                good.append(et_cluster[m.queryIdx])
                                                good.append(dt_cluster[m.trainIdx])
                    self._etalon[index] = listToNumpy_ndarray(good)
                    # print "=========================="
                    # for etalon in self._etalon:
                    #     if etalon is not None:
                    #         print len(etalon)
                    #     else:
                    #         print 0
                    # print "=========================="

    def update_database(self):
        if len(self._hash) > 0:
            minv = sys.maxint
            for obj in self._hash:
                res = self.verify_template_L0(obj)
                if minv > res:
                    minv = res
            self._prob = minv

    def importSources(self, source):
        self._etalon = []
        logger.logger.debug("Database loading started...")
        self.importSources_L0Template(source.get('data', dict()))
        self._prob = source.get('threshold', 100)
        logger.logger.debug("Database loading finished.")

    def importSources_L0Template(self, source):
        for j in range(0, len(source.keys())):
            self._etalon.append([])
        for c_num, cluster in source.iteritems():
            etalon_cluster = []
            for d_num, descriptor in cluster.iteritems():
                etalon_cluster.append(listToNumpy_ndarray(descriptor))
            self._etalon[int(c_num)] = etalon_cluster

    def exportSources(self):
        data = self.exportSources_L0Template()
        source = dict()
        if len(data.keys()) > 0:
            source = dict()
            source['data'] = data
            source['threshold'] = self._prob
        return source

    def exportSources_L0Template(self):
        sources = dict()
        for index in range(0, len(self._etalon)):
            cluster = self._etalon[index]
            cluster_dict = dict()
            i_desc = 0
            if cluster is None:
                cluster = []
            for descriptor in cluster:
                cluster_dict[i_desc] = numpy_ndarrayToList(descriptor)
                i_desc += 1
            sources[str(index)] = cluster_dict
        return sources

    @verifying
    def verify(self, data):
        return self.verify_template_L0(data)

    def verify_template_L0(self, data):
        # return self.verify_template_L0_parallel(data)
        return self.verify_template_L0_noparallel(data)

    def verify_template_L0_parallel(self, data):
        res = []
        prob = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"

        pool = mp.Pool(processes=PROCESS_COUNT)
        res = [pool.apply(parallel_verify_template_L0, args=(self._etalon, data['clusters'], x))
               for x in range(len(self._etalon))]

        logger.logger.debug(res)
        for r, c in res:
            prob += r

        logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        return prob / (1.0 * len(res))

    def verify_template_L0_noparallel(self, data):
        matcher = Matcher(BruteForceMatcherType)
        res = []
        prob = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        summ = 0
        for index in range(0, len(self._etalon)):
            et_cluster = self._etalon[index]
            if et_cluster is not None:
                summ += len(et_cluster)
        for index in range(0, len(self._etalon)):
            et_cluster = self._etalon[index]
            dt_cluster = data['clusters'][index]
            ms = []
            if et_cluster is None:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(-1)
                                        + " Invalid. (Weight: 0)")
                continue
            if dt_cluster is None:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: 0 Probability: 0 (Weight: " +
                                        str(len(et_cluster) / (1.0 * summ)) + ")")
                continue
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster, numpy.uint8),
                                            listToNumpy_ndarray(dt_cluster, numpy.uint8), k=2)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, numpy.uint8),
                                            listToNumpy_ndarray(et_cluster, numpy.uint8), k=2)
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
                res.append(ms)
                val = (len(res[index]) / (1.0 * len(self._etalon[index]))) * 100
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: " + str(len(res[index])) + " Probability: " + str(val) +
                                        " (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")")
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) \
                             + " Positive: " + str(len(res[index])) + " Probability: " + str(val) + "\n"
                prob += (len(et_cluster) / (1.0 * summ)) * val
            else:
                res.append(ms)
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Invalid.")
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) + " Invalid.\n"
        # logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        # self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        # return prob / (1.0 * len(res))
        logger.sys_logger.debug("Probability: " + str(prob))
        self._log += "Probability: " + str(prob) + "\n"
        return prob
