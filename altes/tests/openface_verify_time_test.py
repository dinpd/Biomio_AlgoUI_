from openfacetests import OpenFaceTestAlgorithm, OpenFaceVerificationEstimation
from corealgorithms.flows import IAlgorithm, LinearAlgorithmFlow
from analysers.decorators import analyze_time
from algos import ImageTestDataSeparator
from flows import SeparateProcessingFlow


class OpenFaceVerificationTimeTest(IAlgorithm):
    def __init__(self):
        self._training_flow = None
        self._flow = None
        self._construct()

    def _construct(self):
        main_data_process = LinearAlgorithmFlow()
        main_data_process.addStage('flows:rep_extraction', OpenFaceTestAlgorithm())

        prepare_image_flow = SeparateProcessingFlow()
        prepare_image_flow.setProcessingStage(main_data_process)
        self._training_flow = prepare_image_flow

        self._flow = LinearAlgorithmFlow()
        self._flow.addStage('flows:estimate', OpenFaceVerificationEstimation())

    @analyze_time
    def _apply_training(self, data):
        return self._training_flow.apply(data['train'])

    @analyze_time
    def _apply_test(self, data):
        for test_data in data['test']:
            ver_data = {'train': data['train'], 'test': test_data}
            res = self._flow.apply(ver_data)

    def apply(self, data):
        print data
        if data is None:
            return data
        train_data = self._apply_training(data)
        data.update({'train': train_data})
        self._apply_test(data)
        return None
