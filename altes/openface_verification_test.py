from tests.openface_verify_time_test import OpenFaceVerificationTimeTest
from structs.tools import get_all_files
import time
import os
from corealgorithms.flows import IAlgorithm, DLibFaceDetectionAlgorithm, OpenFaceDataRepresentation, \
    INNER_EYES_AND_BOTTOM_LIP, DLIB_PREDICTOR_V2, FirstSuccessFlow, CascadesFaceDetectionAlgorithm, \
    RotationDetectionAlgorithm, OpenFaceSimpleDistanceEstimation
from corealgorithms import DLIB_MODEL_PATH, OPENFACE_AMF_MODEL_PATH, OPENFACE_NN4_MODEL_PATH

OPENFACE_MODEL_NAME = OPENFACE_AMF_MODEL_PATH
IMAGE_DIMENSION = 96


class OpenFaceRepAlgorithm(IAlgorithm):
    def __init__(self):
        def check_image(data):
            return data is not None and data.get('img', None) is not None

        alignment_stage = FirstSuccessFlow(check_image)
        alignment_stage.addStage('flows::dlib_fdetect', DLibFaceDetectionAlgorithm({
            'dlibFacePredictor': DLIB_MODEL_PATH,
            'landmarkIndices': INNER_EYES_AND_BOTTOM_LIP,
            'predictorVersion': DLIB_PREDICTOR_V2,
            'imgDim': IMAGE_DIMENSION,
            'error_handler': None
        }))
        alignment_stage.addStage('flows::cascades_fdetect', CascadesFaceDetectionAlgorithm({
            'imgDim': IMAGE_DIMENSION,
            'error_handler': None
        }))
        self._data_rep = OpenFaceDataRepresentation({
            'networkModel': OPENFACE_MODEL_NAME,
            'imgDim': IMAGE_DIMENSION,
            'error_handler': None
        })
        self._data_rep.setFaceRotationStage(RotationDetectionAlgorithm())
        self._data_rep.setFaceAlignmentStage(alignment_stage)

    def apply(self, data):
        if data is not None:
            if data.get('rep', None) is None:
                res = self._data_rep.apply({'path': data['path']})
                data.update(res)
            return data
        return None


def run_openface_verification_flow(train_data, test_data):
    file_list = get_all_files(train_data, True)
    start = time.time()
    database = []
    rep_algo = OpenFaceRepAlgorithm()
    for file_name in file_list:
        database.append(rep_algo.apply({'path': file_name}))
    end = time.time()
    print("Training Execution Time: {} s".format(end - start))
    test_file_list = get_all_files(test_data, True)
    startMain = time.time()
    for test_file in test_file_list:
        start = time.time()
        data = {'train': database, "test": rep_algo.apply({'path': test_file})}
        end = time.time()
        print("Testing Execution Time of file {}: {} s".format(test_file, end - start))
    endMain = time.time()
    print("Testing Execution Time: {} s".format(endMain - startMain))
    print("Average Testing Execution Time: {} s".format((endMain - startMain)/(1.0 * len(test_file_list))))
