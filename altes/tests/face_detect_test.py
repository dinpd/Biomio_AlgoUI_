from openfacetests import OpenFaceTestAlgorithm
from corealgorithms.flows import IAlgorithm


class FaceDetectionTest(IAlgorithm):
    def __init__(self, data_struct=None):
        self._flow = None
        self._construct()

    def _construct(self):
        self._flow = OpenFaceTestAlgorithm()

    def apply(self, data):
        if data is None:
            return data
        data_dict = {'img': data}
        if self._flow:
            return self._flow.apply(data_dict)
        return None
