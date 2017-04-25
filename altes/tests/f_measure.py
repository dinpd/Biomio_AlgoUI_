from precision_measure import PrecisionMeasure
from corealgorithms.flows import IAlgorithm
from recall_measure import RecallMeasure


class FMeasure(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is not None:
            TP = data.get('TP', None)
            FP = data.get('FP', None)
            FN = data.get('FN', None)
            if TP is None or FP is None or FN is None:
                raise "{}::Input Data Error".format(self.__class__.__name__)
            precision = PrecisionMeasure()
            P = precision.apply(data)['result']
            recall = RecallMeasure()
            R = recall.apply(data)['result']
            if P is not None and R is not None and (P != 0 or R != 0):
                data.update({'result': 2 * P * R / (P + R)})
            else:
                data.update({'result': None})
        return data
