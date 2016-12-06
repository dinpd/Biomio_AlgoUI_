from corealgorithms.flows import IAlgorithm, DLibFaceDetectionAlgorithm, OpenFaceDataRepresentation, \
    INNER_EYES_AND_BOTTOM_LIP, DLIB_PREDICTOR_V2, FirstSuccessFlow, CascadesFaceDetectionAlgorithm, \
    RotationDetectionAlgorithm
from corealgorithms import DLIB_MODEL_PATH, OPENFACE_AMF_MODEL_PATH, OPENFACE_NN4_MODEL_PATH


OPENFACE_MODEL_NAME = OPENFACE_AMF_MODEL_PATH
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
            img_obj = data['img']
            if img_obj.attribute('rep') is None:
                res = self._data_rep.apply({'path': img_obj.path()})
                print(res)
                img_obj.attribute('rep', res['rep'])
            return {'img': img_obj}
        return None
