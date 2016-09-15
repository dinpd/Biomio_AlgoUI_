from algos import ImageTestDataSeparator, ImageCollector, GeneralEstimationPreparing, \
    EstimationPreparing, RAWSTRUCT_SOURCE
from outputs import EuclideanDistanceOutput, DistanceTableOutput, TSNEEmbeddingsOutput
from server.biomio.algorithms.flows.base import IAlgorithm, LinearAlgorithmFlow
from analysers import EuclideanDistanceAnalyser, DistanceTableAnalyser
from openfacetests import OpenFaceTestAlgorithm
from estimates import EuclideanEstimation
from flows import SeparateProcessingFlow


class SingleImageTest(IAlgorithm):
    def __init__(self, data_struct):
        self._data_struct = data_struct
        self._flow = None
        self._construct()

    def _construct(self):
        prepare_image_flow = SeparateProcessingFlow()
        prepare_image_flow.setSeparationStage(ImageTestDataSeparator())
        prepare_image_flow.setProcessingStage(OpenFaceTestAlgorithm())

        bridge_flow = LinearAlgorithmFlow()
        bridge_flow.addStage('flows:image_collector', ImageCollector())
        bridge_flow.addStage('flows:estimation_preparation', GeneralEstimationPreparing())

        estimation_analysis = LinearAlgorithmFlow()
        estimation_analysis.addStage('flows:analyser', EuclideanDistanceAnalyser())
        estimation_analysis.addStage('flows:output', EuclideanDistanceOutput())
        estimation_analysis.addStage('flows:table_analyser', DistanceTableAnalyser())
        estimation_analysis.addStage('flows:table_output', DistanceTableOutput())
        estimation_analysis.addStage('flows:image_output', TSNEEmbeddingsOutput())

        local_estimate_flow = SeparateProcessingFlow()
        local_estimate_flow.setSeparationStage(EstimationPreparing())
        local_estimate_flow.setProcessingStage(EuclideanEstimation())
        local_estimate_flow.setJoiningStage(estimation_analysis)

        estimate_flow = SeparateProcessingFlow()
        estimate_flow.setSeparationStage(bridge_flow)
        estimate_flow.setProcessingStage(local_estimate_flow)

        self._flow = SeparateProcessingFlow()
        self._flow.setSeparationStage(ImageTestDataSeparator())
        self._flow.setProcessingStage(prepare_image_flow)
        self._flow.setJoiningStage(estimate_flow)

    def apply(self, data):
        if data is None:
            return data
        data.attribute('type', 'test')
        init_struct = {
            'type': RAWSTRUCT_SOURCE,
            'train': self._data_struct,
            'test': data
        }
        if self._flow:
            return self._flow.apply(init_struct)
        return None
