__author__ = 'vitalius.parubochyi'

from keypoints import KODSettings
from clusters_keypoints import ClustersMatchingDetector
from intersect_keypoints import IntersectMatchingDetector


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