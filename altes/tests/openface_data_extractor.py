from corealgorithms.flows import IAlgorithm, RotationDetectionAlgorithm, CascadesFaceDetectionAlgorithm, \
    FirstSuccessFlow, OpenFaceDataRepresentation, DLibFaceDetectionAlgorithm, \
    INNER_EYES_AND_BOTTOM_LIP, DLIB_PREDICTOR_V2
from corealgorithms import OPENFACE_NN4_MODEL_PATH, DLIB_MODEL_PATH
import os


IMAGE_DIMENSION = 96


class OpenfaceDataExtractor(IAlgorithm):
    def __init__(self):
        self._init()

    def _init(self):

        def check_image(data):
            return data is not None and data.get('img', None) is not None

        alignment_stage = FirstSuccessFlow(check_image)
        alignment_stage.addStage('flows::dlib_fdetect', DLibFaceDetectionAlgorithm({
            'dlibFacePredictor': DLIB_MODEL_PATH,
            'landmarkIndices': INNER_EYES_AND_BOTTOM_LIP,
            'predictorVersion': DLIB_PREDICTOR_V2,
            'imgDim': IMAGE_DIMENSION
        }))
        alignment_stage.addStage('flows::cascades_fdetect', CascadesFaceDetectionAlgorithm({
            'imgDim': IMAGE_DIMENSION
        }))
        self._data_rep = OpenFaceDataRepresentation({
            'networkModel': OPENFACE_NN4_MODEL_PATH,
            'imgDim': IMAGE_DIMENSION
        })
        # self._data_rep.setFaceRotationStage(RotationDetectionAlgorithm())
        self._data_rep.setFaceAlignmentStage(alignment_stage)

    def apply(self, data):
        if data is not None:
            for p_key, p_data in data['data'].iteritems():
                if os.path.exists(p_key):
                    print p_key
                    k = 1 / 0
                    data['data'].update({p_key: self._get(p_key)})
                else:
                    for s_key, s_data in p_data.iteritems():
                        if os.path.exists(s_key):
                            res = self._get(s_key)
                            if res is not None:
                                p_data.update({s_key: res})
                            else:
                                del p_data[s_key]
                        else:
                            del p_data[s_key]
        return data

    def _get(self, path):
        return self._data_rep.apply({'path': path}).get('rep', None)
