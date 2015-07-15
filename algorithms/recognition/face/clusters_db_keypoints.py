import numpy

from algorithms.features.matchers import Matcher, BruteForceMatcherType
from algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from algorithms.recognition.keypoints import verifying
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
import logger


class ClustersDBMatchingDetector(ClustersMatchingDetector):
    def __init__(self):
        ClustersMatchingDetector.__init__(self)

    def update_hash(self, data):
        del data['keypoints']
        del data['descriptors']
        self._hash.append(data)

    def importSources(self, source):
        self._etalon = []
        logger.logger.debug("Database loading started...")
        self.importSources_Database(source.get('data', dict()))
        self._prob = source.get('threshold', 100)
        logger.logger.debug("Database loading finished.")

    def importSources_Database(self, source):
        for j in range(0, len(source.keys())):
            self._hash.append(dict())
        for c_num, item in source.iteritems():
            item_data = []
            for k in range(0, len(item.keys())):
                item_data.append([])
            for d_num, cluster in item.iteritems():
                desc = []
                for i in range(0, len(cluster.keys())):
                    desc.append([])
                for e_num, descriptor in cluster.iteritems():
                    desc[int(e_num)] = listToNumpy_ndarray(descriptor)
                item_data[int(d_num)] = desc
            obj = dict()
            obj["clusters"] = item_data
            self._hash[int(c_num) - 1] = obj

    def exportSources(self):
        data = self.exportSources_Database()
        source = dict()
        if len(data.keys()) > 0:
            source = dict()
            source['data'] = data
            source['threshold'] = self._prob
        return source

    def exportSources_Database(self):
        etalon = dict()
        i = 0
        for data in self._hash:
            i += 1
            elements = dict()
            for index in range(0, len(data["clusters"])):
                cluster = data["clusters"][index]
                desc = dict()
                if cluster is not None:
                    for indx in range(0, len(cluster)):
                        desc[indx] = numpy_ndarrayToList(cluster[indx])
                elements[str(index)] = desc
            etalon[str(i)] = elements
        return etalon

    @verifying
    def verify(self, data):
        matcher = Matcher(BruteForceMatcherType)
        gres = []
        self._log += "Test: " + data['path'] + "\n"
        for d in self._hash:
            res = []
            for i in range(0, len(d['clusters'])):
                test = data['clusters'][i]
                source = d['clusters'][i]
                if (test is None) or (source is None) or (len(test) == 0) or (len(source) == 0):
                    logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
                    self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
                else:
                    matches = matcher.knnMatch(listToNumpy_ndarray(test, numpy.uint8),
                                               listToNumpy_ndarray(source, numpy.uint8), k=1)
                    ms = []
                    for v in matches:
                        if len(v) >= 1:
                            m = v[0]
                            if m.distance < self.kodsettings.neighbours_distance:
                                ms.append(m)
                    prob = len(ms) / (1.0 * len(matches))
                    res.append(prob * 100)
                    logger.sys_logger.debug("Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): "
                                            + str(prob * 100) + "%")
                    self._log += "Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): " + str(prob * 100) \
                                 + "%" + "\n"
            suma = sum(res)
            logger.sys_logger.debug("Total for image: " + str(suma / len(res)))
            self._log += "Total for image: " + str(suma / len(res)) + "\n"
            gres.append(suma / len(res))
        s = sum(gres)
        logger.logger.debug("Total: " + str(s / len(gres)))
        self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        return s / len(gres)
