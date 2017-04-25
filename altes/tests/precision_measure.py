from corealgorithms.flows import IAlgorithm


class PrecisionMeasure(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is not None:
            TP = data.get('TP', None)
            FP = data.get('FP', None)
            if TP is None or FP is None:
                raise "{}::Input Data Error".format(self.__class__.__name__)
            T = (1.0 * (TP + FP))
            if T != 0:
                data.update({'result': TP / T})
            else:
                data.update({'result': None})
        return data
