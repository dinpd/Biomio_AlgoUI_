from algos import ImageTestDataSeparator, ImageCollector, GeneralEstimationPreparing, RepEmbeddingsAlgorithm, \
    RAWSTRUCT_SOURCE
from server.biomio.algorithms.flows.base import IAlgorithm, LinearAlgorithmFlow
from openfacetests import OpenFaceTestAlgorithm, OpenFaceVerificationEstimation
from estimates import EmbeddingsRepresentationEstimation
from outputs import OpenFaceDistanceOutput
from flows import SeparateProcessingFlow


class OpenFaceVerificationTest(IAlgorithm):
    def __init__(self, data_struct):
        self._data_struct = data_struct
        self._flow = None
        self._construct()

    def _construct(self):
        main_data_process = LinearAlgorithmFlow()
        main_data_process.addStage('flows:rep_extraction', OpenFaceTestAlgorithm())
        # main_data_process.addStage('flows:rep_embeddings', RepEmbeddingsAlgorithm())

        prepare_image_flow = SeparateProcessingFlow()
        prepare_image_flow.setSeparationStage(ImageTestDataSeparator())
        prepare_image_flow.setProcessingStage(main_data_process)

        bridge_flow = LinearAlgorithmFlow()
        bridge_flow.addStage('flows:image_collector', ImageCollector())
        bridge_flow.addStage('flows:estimation_preparation', GeneralEstimationPreparing())

        emb_estimation = EmbeddingsRepresentationEstimation()
        emb_estimation.setBasicEstimationStage(OpenFaceVerificationEstimation())

        local_estimate_flow = LinearAlgorithmFlow()
        # local_estimate_flow.addStage('flows:estimate', emb_estimation)
        local_estimate_flow.addStage('flows:estimate', OpenFaceVerificationEstimation())
        local_estimate_flow.addStage('flows:output', OpenFaceDistanceOutput())

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
