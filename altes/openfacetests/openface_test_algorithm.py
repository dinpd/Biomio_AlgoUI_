from server.biomio.algorithms.openface import DLibFaceDetectionAlgorithm, OpenFaceDataRepresentation, \
    INNER_EYES_AND_BOTTOM_LIP, DLIB_PREDICTOR_V2
from server.biomio.protocol.probes.plugins.openface_verify_plugin.defs import OPENFACE_PATH
from server.biomio.algorithms.flows import FirstSuccessFlow, CascadesFaceDetectionAlgorithm, RotationDetectionAlgorithm
from server.biomio.algorithms.flows.base import IAlgorithm
import os


MODEL_DIR = os.path.join(OPENFACE_PATH, "models")
DLIB_MODEL_DIR = os.path.join(MODEL_DIR, "dlib")
OPENFACE_MODEL_DIR = os.path.join(MODEL_DIR, "openface")
DLIB_MODEL_NAME = "shape_predictor_68_face_landmarks.dat"
OPENFACE_MODEL_NAME_NN4 = 'nn4.small2.v1.t7'
OPENFACE_MODEL_NAME_AMF = '94.9-accuracy-model-float.t7'
OPENFACE_MODEL_NAME = OPENFACE_MODEL_NAME_AMF
IMAGE_DIMENSION = 96


class OpenFaceTestAlgorithm(IAlgorithm):
    """
    Input:
        {
            'img': altes.structs.ImageContainer
        }
    Output:
        {
            'img': altes.structs.ImageContainer
        }
    """
    def __init__(self):
        def check_image(data):
            return data is not None and data.get('img', None) is not None

        alignment_stage = FirstSuccessFlow(check_image)
        alignment_stage.addStage('flows::dlib_fdetect', DLibFaceDetectionAlgorithm({
            'dlibFacePredictor': os.path.join(DLIB_MODEL_DIR, DLIB_MODEL_NAME),
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
            'networkModel': os.path.join(OPENFACE_MODEL_DIR, OPENFACE_MODEL_NAME),
            'imgDim': IMAGE_DIMENSION,
            'error_handler': None
        })
        self._data_rep.setFaceRotationStage(RotationDetectionAlgorithm())
        self._data_rep.setFaceAlignmentStage(alignment_stage)

    def apply(self, data):
        if data is not None:
            img_obj = data['img']
            if img_obj.attribute('rep') is None:
                res = self._data_rep.apply({'path': img_obj.path()})
                print(res)
                img_obj.attribute('rep', res['rep'])
            return {'img': img_obj}
        return None
