from biomio.algorithms.recognition.keypoints import KODSettings
from biomio.algorithms.recognition.face.clusters_keypoints import ClustersMatchingDetector
from biomio.algorithms.recognition.face.intersect_keypoints import IntersectMatchingDetector


def getClustersMatchingDetectorWithoutTemplate():
    detector = ClustersMatchingDetector()
    detector.setUseTemplate(False)
    return detector


def getClustersMatchingDetectorWithL0Template():
    detector = ClustersMatchingDetector()
    detector.setUseTemplate(True)
    detector.setTemplateLayer(0)
    return detector


def getClustersMatchingDetectorWithL1Template():
    detector = ClustersMatchingDetector()
    detector.setUseTemplate(True)
    detector.setTemplateLayer(1)
    return detector


def getIntersectMatchingDetector():
    detector = IntersectMatchingDetector()
    return detector