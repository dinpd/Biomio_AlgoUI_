from logger import logger

from aiplugins import IAlgorithmPlugin
from algorithms.recognition.detcreator import (DetectorCreator,
                                               ClustersObjectMatching,
                                               FaceCascadeClassifier, EyesCascadeClassifier)
from algorithms.imgobj import loadImageObject

import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CASCADE_PATH = os.path.join(APP_ROOT, '../../algorithms/data/')

VerificationAlgorithm = {'name': 'Keypoints Verification Algorithm',
                         'pk': 0}


class FaceRecognitionPlugin(IAlgorithmPlugin):
    def __init__(self):
        super(FaceRecognitionPlugin, self).__init__()
        self.init_detector()

    def set_image_manager(self, manager):
        self._imanager = manager

    def set_resources_manager(self, manager):
        self._rmanager = manager

    def get_algorithms_actions(self, parent):
        pass

    def get_algorithms_list(self):
        return [VerificationAlgorithm]

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        pass

    def settings(self, name):
        setting = dict()
        if name == VerificationAlgorithm['pk']:
            setting = {'inputs': {
                'settings_parameters':
                    {
                        'image_required': True,
                        'number_of_images': 1
                    },
                'elements': [
                    {
                        'label': "Max Neighbours Distance",
                        'default_value': 50,
                        'settings_key': 'max_neigh'
                    }
                ],
                'general_label': 'Verification Settings'
            }}
        return setting

    @staticmethod
    def checkMaxNeigh(value):
        res = False
        if type(value) == type(float):
            if 0 < value < 1000.0:
                res = True
        return res

    def apply(self, name, settings=dict()):
        if name == VerificationAlgorithm['pk']:
            return self.verification_algorithm(settings)
        return None

    def init_detector(self):
        creator = DetectorCreator(type=ClustersObjectMatching)
        creator.addClassifier(FaceCascadeClassifier)
        creator.addCascade(FaceCascadeClassifier, os.path.join(CASCADE_PATH,
                                                               "haarcascades/haarcascade_frontalface_alt_tree.xml"))
        creator.addCascade(FaceCascadeClassifier, os.path.join(CASCADE_PATH,
                                                               "haarcascades/haarcascade_frontalface_alt2.xml"))
        creator.addCascade(FaceCascadeClassifier, os.path.join(CASCADE_PATH,
                                                               "haarcascades/haarcascade_frontalface_alt.xml"))
        creator.addCascade(FaceCascadeClassifier, os.path.join(CASCADE_PATH,
                                                               "haarcascades/haarcascade_frontalface_default.xml"))
        creator.addClassifier(EyesCascadeClassifier)
        creator.addCascade(EyesCascadeClassifier, os.path.join(CASCADE_PATH,
                                                               "haarcascades/haarcascade_mcs_eyepair_big.xml"))
        self._keysrecg_detector = creator.detector()

    def verification_algorithm(self, settings):
        database = self._rmanager.database(settings['database'])
        self._keysrecg_detector.importSources(database['data'])
        self._keysrecg_detector.importSettings(database['info'])
        self._keysrecg_detector.kodsettings.neighbours_distance = settings['max_neigh']
        result = dict()
        result['result'] = self._keysrecg_detector.verify(loadImageObject(settings['data']))
        result['log'] = self._keysrecg_detector.log()
        return result