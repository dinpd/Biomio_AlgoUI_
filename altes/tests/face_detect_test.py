from algos import ImageTestDataSeparator, ImageCollector, GeneralEstimationPreparing, RepEmbeddingsAlgorithm, \
    RAWSTRUCT_SOURCE
from server.biomio.algorithms.flows.base import IAlgorithm, LinearAlgorithmFlow
from openfacetests import OpenFaceTestAlgorithm, OpenFaceVerificationEstimation
from estimates import EmbeddingsRepresentationEstimation
from outputs import OpenFaceDistanceOutput
from flows import SeparateProcessingFlow


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
