from biomio.algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
from biomio.algorithms.features import matcherForDetector, dtypeForDetector
from biomio.algorithms.interfaces import AlgorithmEstimation
from biomio.algorithms.features.matchers import Matcher
import itertools


class BaseTemplateEstimation(AlgorithmEstimation):
    def __init__(self, detector_type, knn):
        self._knn = knn
        self._matcher = Matcher(matcherForDetector(detector_type))
        self._dtype = dtypeForDetector(detector_type)

    @staticmethod
    def exportDatabase(data):
        return {
            str(index): {} if cluster is None else {
                i: numpy_ndarrayToList(descriptor) for i, descriptor in enumerate(cluster)
                } for index, cluster in enumerate(data)
            }

    @staticmethod
    def importDatabase(data):

        def _values(d, key=None):
            l = sorted(d, key=key)
            for e in l:
                yield d[e]

        return [listToNumpy_ndarray(
            [
                listToNumpy_ndarray(descriptor) for descriptor in _values(cluster)
            ]) for cluster in _values(data, key=int)
        ]

    def estimate_training(self, data, database):
        template = database
        if len(database) == 0:
            template = data
        else:
            for index, et_cluster in enumerate(database):
                dt_cluster = data[index]
                if et_cluster is None or len(et_cluster) == 0 or len(et_cluster) < self._knn:
                    template[index] = et_cluster
                elif dt_cluster is None or len(dt_cluster) == 0 or len(dt_cluster) < self._knn:
                    template[index] = et_cluster
                else:
                    matches1 = self._matcher.knnMatch(listToNumpy_ndarray(et_cluster, self._dtype),
                                                      listToNumpy_ndarray(dt_cluster, self._dtype), k=self._knn)
                    matches2 = self._matcher.knnMatch(listToNumpy_ndarray(dt_cluster, self._dtype),
                                                      listToNumpy_ndarray(et_cluster, self._dtype), k=self._knn)
                    good = list(itertools.chain.from_iterable(itertools.imap(
                        lambda(x, _): (et_cluster[x.queryIdx], dt_cluster[x.trainIdx]), itertools.ifilter(
                            lambda(m, n): m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx, itertools.product(
                                itertools.chain(*matches1), itertools.chain(*matches2)
                            )
                        )
                    )))
                    template[index] = listToNumpy_ndarray(good)
        return template

    def estimate_verification(self, data, database):
        raise NotImplementedError
