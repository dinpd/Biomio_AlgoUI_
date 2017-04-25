from corealgorithms.flows import IAlgorithm


class RecallMeasure(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is not None:
            TP = data.get('TP', None)
            FN = data.get('FN', None)
            if TP is None or FN is None:
                raise "{}::Input Data Error".format(self.__class__.__name__)
            T = (1.0 * (TP + FN))
            if T != 0:
                data.update({'result': TP / T})
            else:
                data.update({'result': None})
        return data
