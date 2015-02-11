from logger import logger

from aiplugins import IAlgorithmPlugin
import algorithms.faces.biom.faces as fs
from algorithms.cvtools.visualization import drawRectangle
from algorithms.features.classifiers import CascadeROIDetector
from algorithms.faces.biom.utils import files_list
from algorithms.recognition.detcreator import (DetectorCreator,
                                               ClustersObjectMatching,
                                               FaceCascadeClassifier, EyesCascadeClassifier)
from algorithms.imgobj import loadImageObject

import os


VerificationAlgorithm = "KeypointsVerificationAlgorithm"


class FaceRecognitionPlugin(IAlgorithmPlugin):
    def __init__(self):
        super(FaceRecognitionPlugin, self).__init__()
        self.init_detector()

    def set_image_manager(self, manager):
        self._imanager = manager

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
        if name == VerificationAlgorithm:
            setting['database'] = "default"
            setting['max_neigh'] = self.checkMaxNeigh
            setting['data'] = None
        return setting

    @staticmethod
    def checkMaxNeigh(value):
        res = False
        if type(value) == type(float):
            if 0 < value < 1000.0:
                res = True
        return res

    def apply(self, name, settings=dict()):
        if name == VerificationAlgorithm:
            return self.verification_algorithm(settings)
        return None

    def init_detector(self):
        creator = DetectorCreator(type=ClustersObjectMatching)
        creator.addClassifier(FaceCascadeClassifier)
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt_tree.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt2.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_default.xml")
        creator.addClassifier(EyesCascadeClassifier)
        creator.addCascade(EyesCascadeClassifier, "algorithms/data/haarcascades/haarcascade_mcs_eyepair_big.xml")
        self._keysrecg_detector = creator.detector()

    def verification_algorithm(self, settings):
        database = self._imanager.database(settings['database'])
        self._keysrecg_detector.importSources(database['data'])
        self._keysrecg_detector.kodsettings.neighbours_distance = settings['max_neigh']
        self._keysrecg_detector.kodsettings.detector_type = database['settings']
        self._keysrecg_detector.kodsettings.brisk_settings = database['settings']
        self._keysrecg_detector.kodsettings.orb_settings = database['settings']
        self._keysrecg_detector.verify(settings['data'])