from corealgorithms.flows import AlgorithmFlow
import scipy.spatial.distance as distance

DISTANCE_ESTIMATION_STAGE = 'flows:distance_estimation'


class ThresholdDistanceEstimation(AlgorithmFlow):
    def __init__(self, threshold=0.5):
        AlgorithmFlow.__init__(self)
        self._threshold = threshold

    def setDistanceEstimationStage(self, stage):
        self._stages[DISTANCE_ESTIMATION_STAGE] = stage

    def apply(self, data):
        if data is None:
            return data
        res = self._stages[DISTANCE_ESTIMATION_STAGE].apply(data)
        return {'result': res['result'] < self._threshold}
