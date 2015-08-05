from algorithms.features.matchers import Matcher
from algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from algorithms.recognition.keypoints import verifying
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
from algorithms.features import matcherForDetector, dtypeForDetector
import itertools
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

        def _values(d, key=None):
            l = sorted(d, key=key)
            for e in l:
                yield d[e]

        self._hash = [
            {
                'clusters': [
                    [
                        listToNumpy_ndarray(descriptor) for descriptor in _values(cluster)
                    ] for cluster in _values(item, key=int)
                ]
            } for item in _values(source)
        ]

    def exportSources(self):
        data = self.exportSources_Database()
        if len(data.keys()) > 0:
            return {
                'data': data,
                'threshold': self._prob
            }
        else:
            return {}

    def exportSources_Database(self):
        return {
            str(i): {
                str(index): {
                    indx: numpy_ndarrayToList(c) for (indx, c) in enumerate(cluster)
                } for (index, cluster) in enumerate(data['clusters']) if cluster is not None
            } for (i, data) in enumerate(self._hash)
        }

    def _probability(self, matcher, source, test):
        dtype = dtypeForDetector(self.kodsettings.detector_type)
        matches = matcher.knnMatch(listToNumpy_ndarray(test, dtype),
                                   listToNumpy_ndarray(source, dtype), k=1)
        ms = sum(
            itertools.imap(
                lambda v: len(v) >= 1 and v[0].distance < self.kodsettings.neighbours_distance, matches
            )
        )
        return ms / (1.0 * len(matches))

    @verifying
    def verify(self, data):
        # matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))
        # gres = []
        # self._log += "Test: " + data['path'] + "\n"
        # for d in self._hash:
        #     res = []
        #     for i in range(0, len(d['clusters'])):
        #         test = data['clusters'][i]
        #         source = d['clusters'][i]
        #         if (test is None) or (source is None) or (len(test) == 0) or (len(source) == 0):
        #             logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
        #             self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
        #         else:
        #             matches = matcher.knnMatch(listToNumpy_ndarray(test, numpy.uint8),
        #                                        listToNumpy_ndarray(source, numpy.uint8), k=1)
        #             ms = sum(itertools.imap(
        #                 lambda v: len(v) >= 1 and v[0].distance < self.kodsettings.neighbours_distance,
        #                 matches)
        #             )
        #             prob = ms / (1.0 * len(matches))
        #             res.append(prob * 100)
        #             logger.sys_logger.debug("Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): "
        #                                     + str(prob * 100) + "%")
        #             self._log += "Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): " + str(prob * 100) \
        #                          + "%" + "\n"
        #     suma = sum(res)
        #     logger.sys_logger.debug("Total for image: " + str(suma / len(res)))
        #     self._log += "Total for image: " + str(suma / len(res)) + "\n"
        #     gres.append(suma / len(res))
        # s = sum(gres)
        # logger.logger.debug("Total: " + str(s / len(gres)))
        # self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        # return s / len(gres)
        matcher = Matcher(matcherForDetector(self.kodsettings.detector_type))
        tprob = 0
        self._log += "Test: " + data['path'] + "\n"
        for d in self._hash:
            prob = [0, 0]
            for i, source in enumerate(d['clusters']):
                test = data['clusters'][i]
                if (test is None) or (source is None) or (len(test) == 0) or (len(source) == 0):
                    logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
                    self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
                else:
                    _prob = 100 * self._probability(matcher, source, test)
                    prob[0] += _prob
                    prob[1] += 1
            tprob += (prob[0]/prob[1])
        logger.logger.debug("Total: " + str(tprob/len(self._hash)))
        # self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        return tprob/len(self._hash)
