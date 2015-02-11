from algorithms.features.classifiers import CascadeClassifierSettings, CascadeROIDetector
from algorithms.recognition.keypoints import (KeypointsObjectDetector, FeaturesMatchingDetector,
                                              SpiralKeypointsVectorDetector, ObjectsMatchingDetector,
                                              ClustersMatchingDetector)
from logger import logger


HAAR_CASCADES_DIR = "algorithms/data/haarcascades"

FaceCascadeClassifier = "FaceCascadeClassifier"
EyesCascadeClassifier = "EyesCascadeClassifier"

FeaturesMatching = 0
SpiralKeypointsVector = 1
ObjectsFlannMatching = 2
ClustersObjectMatching = 3


class DetectorCreator:
    def __init__(self, type=FeaturesMatching):
        self._type = type
        self._classifiers = dict()
        pass

    def addClassifier(self, classifier_type=FaceCascadeClassifier, settings=CascadeClassifierSettings()):
        classifier = self._classifiers.get(classifier_type, None)
        if classifier is None:
            classifier = CascadeROIDetector()
            self._classifiers[classifier_type] = classifier
        classifier.classifierSettings = settings

    def addCascade(self, classifier_type, cascade_name):
        classifier = self._classifiers.get(classifier_type, None)
        if classifier is None:
            logger.debug("The classifier was not exists. Add such classifier first, please!")
        else:
            classifier.add_cascade(cascade_name)

    def detector(self):
        detector = KeypointsObjectDetector()
        if self._type == FeaturesMatching:
            detector = FeaturesMatchingDetector()
        elif self._type == SpiralKeypointsVector:
            detector = SpiralKeypointsVectorDetector()
        elif self._type == ObjectsFlannMatching:
            detector = ObjectsMatchingDetector()
        elif self._type == ClustersObjectMatching:
            detector = ClustersMatchingDetector()
        detector.setUseTemplate(True)
        detector._cascadeROI = self._classifiers[FaceCascadeClassifier]
        detector._eyeROI = self._classifiers[EyesCascadeClassifier]
        return detector
