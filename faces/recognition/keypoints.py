from faces.biom.faces import CascadeROIDetector
from rectmerge import mergeRectangles
from features.tools import getROIImage, keypointsToArrays
from features.detectors import FeatureDetector
from lshash import LSHash
from features.hashing.nearpy_hash import NearPyHash
import logger
import os


LSHashType = 0
NearPyHashType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    cascade_list = []
    neighbours_distance = 2.0


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self, hash_t=LSHashType):
        self._hash_type = hash_t
        self._hash = None
        if hash_t is LSHashType:
            self._hash = LSHash(64, 4)
        else:
            self._hash = NearPyHash(4)
            self._hash.addRandomBinaryProjectionsEngine(10)

    def addSource(self, data):
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        for data in data_list:
            self.addSource(data)

    def identify(self, data):
        if self.data_detect(data):
            return self.matching(data)
        return None

    def data_detect(self, data):
        # ROI detection
        cascadeROI = CascadeROIDetector()
        for cascade in self.kodsettings.cascade_list:
            cascadeROI.add_cascade(cascade)
        rects = cascadeROI.detect(data['data'])
        if len(rects) is 0:
            logger.logger.debug("ROI is not found for " + data['path'])
            return False
        rect = mergeRectangles(rects)
        #ROI cutting
        data['roi'] = getROIImage(data['data'], rect)
        #Keypoints detection
        detector = FeatureDetector()
        obj = detector.detectImage(data['roi'])
        key_arrays = keypointsToArrays(obj.keypoints())
        data['keypoints'] = key_arrays
        return True

    def update_hash(self, data):
        if self._hash_type is LSHashType:
            for keypoint in data['keypoints']:
                self._hash.index(keypoint)
        else:
            for keypoint in data['keypoints']:
                self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])

    def matching(self, data):
        imgs = dict()
        if data is not None:
            for keypoint in data['keypoints']:
                neig = self._hash.neighbours(keypoint)
                for el in neig:
                    if el[2] < self.kodsettings.neighbours_distance:
                        value = imgs.get(el[1], 0)
                        value += 1
                        imgs[el[1]] = value
            keys = imgs.keys()
            vmax = 0
            max_key = ""
            for key in keys:
                if imgs[key] > vmax:
                    max_key = key
                    vmax = imgs[key]
            logger.logger.debug(imgs)
            logger.logger.debug(max_key)