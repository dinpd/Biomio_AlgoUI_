from biomio.algorithms.features import matcherForDetector, dtypeForDetector
from biomio.algorithms.interfaces import AlgorithmEstimation, logger
from biomio.algorithms.cvtools.types import listToNumpy_ndarray
from biomio.algorithms.features.matchers import Matcher
import itertools


class ClusterDBEstimation(AlgorithmEstimation):
    def __init__(self, detector_type, max_distance):
        self._max_distance = max_distance
        self._matcher = Matcher(matcherForDetector(detector_type))
        self._dtype = dtypeForDetector(detector_type)

    def estimate_training(self, data, database):
        raise NotImplementedError

    def estimate_verification(self, data, database):
        tprob = 0
        for d in database:
            prob = [0, 0]
            for i, source in enumerate(d['clusters']):
                test = data['clusters'][i]
                if (test is None) or (source is None) or (len(test) == 0) or (len(source) == 0):
                    logger.debug("Cluster #%d: Invalid" % (i + 1))
                else:
                    _prob = 100 * self._probability(source, test)
                    prob[0] += _prob
                    prob[1] += 1
                    logger.debug("Cluster #%d (Size: %d): %f%%" % (i + 1, len(source), _prob))
            logger.debug("Total for image: %f%%" % (prob[0]/prob[1]))
            tprob += (prob[0] / prob[1])
        logger.debug("Total: %d%%" % (tprob / len(database)))
        return tprob / len(database)

    def _probability(self, source, test):
        matches = self._matcher.knnMatch(listToNumpy_ndarray(test, self._dtype),
                                         listToNumpy_ndarray(source, self._dtype), k=1)
        ms = sum(
            itertools.imap(
                lambda v: len(v) >= 1 and v[0].distance < self._max_distance, matches
            )
        )
        return ms / (1.0 * len(matches))
