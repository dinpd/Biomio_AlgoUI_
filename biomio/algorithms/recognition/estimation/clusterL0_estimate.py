from biomio.algorithms.features.matchers import LowesMatchingScheme
from biomio.algorithms.cvtools.types import listToNumpy_ndarray
from base_template_estimate import BaseTemplateEstimation
from biomio.algorithms.logger import logger
import itertools
import math

DEFAULT_MODE = 0
CROSS_DISTANCE_MODE = 1
FULL_DISTANCE_MODE = 2
LOWES_DISTANCE_MODE = 3


class ClusterL0Estimation(BaseTemplateEstimation):
    def __init__(self, detector_type, knn, max_distance=None, mode=DEFAULT_MODE):
        BaseTemplateEstimation.__init__(self, detector_type, knn)
        self._max_distance = 0.5 if max_distance is None else max_distance
        self._mode = mode

    def estimate_verification(self, data, database):
        prob = 0
        logger.debug("Template size: ")
        summ = sum(itertools.imap(lambda x: len(x) if x is not None else 0, database))
        for index, et_cluster in enumerate(database):
            dt_cluster = data[index]
            if et_cluster is None or len(et_cluster) < self._knn:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
                continue
            if dt_cluster is None or len(dt_cluster) < self._knn:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(database[index]))
                             + " Positive: 0 Probability: 0 (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")")
                continue
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                matches1 = self._matcher.knnMatch(listToNumpy_ndarray(et_cluster, self._dtype),
                                                  listToNumpy_ndarray(dt_cluster, self._dtype), k=self._knn)
                matches2 = self._matcher.knnMatch(listToNumpy_ndarray(dt_cluster, self._dtype),
                                                  listToNumpy_ndarray(et_cluster, self._dtype), k=self._knn)
                ms = 0
                if (self._mode == DEFAULT_MODE or self._mode == CROSS_DISTANCE_MODE or
                    self._mode == FULL_DISTANCE_MODE):
                    ml = [
                        x for (x, _) in itertools.ifilter(
                            lambda(m, n): m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx, itertools.product(
                                itertools.chain(*matches1), itertools.chain(*matches2)
                            )
                        )
                    ]
                    ms = len(ml)
                    if self._mode == CROSS_DISTANCE_MODE:
                        ms = sum([1/math.exp(m.distance) for m in ml])
                        # ms = sum([1/(2**m.distance) for m in ml])
                        # ms = sum([1/((1 + m.distance)**m.distance) for m in ml])
                    elif self._mode == FULL_DISTANCE_MODE:
                        mu = [
                            x for (x, _) in itertools.ifilter(
                                lambda(m, n): m.queryIdx != n.trainIdx or m.trainIdx != n.queryIdx, itertools.product(
                                    itertools.chain(*matches1), itertools.chain(*matches2)
                                )
                            )
                        ]
                        ms = sum([2/math.exp(m.distance) for m in ml]) + sum([1/math.exp(m.distance) for m in mu])
                elif self._mode == LOWES_DISTANCE_MODE:
                    ml = [m[0] for m in matches2 if len(matches2) >= 2 and
                          LowesMatchingScheme(m[0], m[1], self._max_distance)]
                    ms = len(ml)
                val = (ms / (1.0 * len(et_cluster))) * 100
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(et_cluster)) + " Positive: "
                             + str(ms) + " Probability: " + str(val) + " (Weight: "
                             + str(len(et_cluster) / (1.0 * summ)) + ")")
                prob += (len(et_cluster) / (1.0 * summ)) * val
            else:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(et_cluster)) + " Invalid.")
        logger.debug("Probability: " + str(prob))
        return prob
