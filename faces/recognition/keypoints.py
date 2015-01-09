from faces.biom.faces import CascadeROIDetector
from rectmerge import mergeRectangles
from features.tools import (getROIImage, keypointsToArrays, spiralSort, joinVectors, listToNumpy_ndarray,
                            drawImage, drawKeypoints, minimizeSort)
from features.detectors import (BRISKDetector, ORBDetector, FeatureDetector,
                                BRISKDetectorSettings, ORBDetectorSettings)
from lshash import LSHash
from features.hashing.nearpy_hash import NearPyHash
import logger
import os


LSHashType = 0
NearPyHashType = 1

SimpleKeypoints = 0
SpiralKeypointsVector = 1

BRISKDetectorType = 0
ORBDetectorType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    cascade_list = []
    neighbours_distance = 2.0
    max_hash_length = 600
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self, hash_t=LSHashType, data_t=SimpleKeypoints):
        self._hash_type = hash_t
        self._data_type = data_t
        self._data_keys = dict()
        self._hash = None
        self._data_init = False

    def init_hash(self):
        if self.kodsettings.detector_type is BRISKDetectorType:
            size = 64
        else:
            size = 32
        if self._hash_type is LSHashType:
            self._hash = LSHash(128, size)
        else:
            if self._data_type is SimpleKeypoints:
                self._hash = NearPyHash(size)
            else:
                self._hash = NearPyHash(self.kodsettings.max_hash_length)
            self._hash.addRandomBinaryProjectionsEngine(10)
        self._data_init = True

    def hash_initialized(self):
        return self._data_init

    def addSource(self, data):
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        for data in data_list:
            self.addSource(data)

    def identify(self, data):
        if self.data_detect(data) and len(self._data_keys) > 0:
            if self._data_type is SimpleKeypoints:
                return self.matching(data)
            else:
                return self.vect_matching(data)
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
        if self.kodsettings.detector_type is BRISKDetectorType:
            logger.logger.debug('%d, %d, %f', self.kodsettings.brisk_settings.thresh,
                                self.kodsettings.brisk_settings.octaves, self.kodsettings.brisk_settings.patternScale)
            brisk_detector = BRISKDetector(self.kodsettings.brisk_settings.thresh,
                                           self.kodsettings.brisk_settings.octaves,
                                           self.kodsettings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            logger.logger.debug('%d, %f, %d', self.kodsettings.orb_settings.features,
                                self.kodsettings.orb_settings.scaleFactor, self.kodsettings.orb_settings.nlevels)
            orb_detector = ORBDetector(self.kodsettings.orb_settings.features,
                                       self.kodsettings.orb_settings.scaleFactor,
                                       self.kodsettings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        obj = detector.detectAndComputeImage(data['roi'])
        data['descriptors'] = obj.descriptors()
        if data['descriptors'] is None:
            data['descriptors'] = []
        if self._data_type is SimpleKeypoints:
            key_arrays = keypointsToArrays(obj.keypoints())
            data['keypoints'] = key_arrays
        else:
            height, width = data['roi'].shape[0], data['roi'].shape[1]
            order_keys = obj.keypoints() #spiralSort(obj, width, height)
            # order_keys = minimizeSort(obj)
            obj.keypoints(keypointsToArrays(order_keys))
            key_arr = joinVectors(obj.keypoints())
            while len(key_arr) < self.kodsettings.max_hash_length:
                key_arr.append(0)
            data['keypoints'] = listToNumpy_ndarray(key_arr)
        return True

    def update_hash(self, data):
        if self._hash_type is LSHashType:
            for keypoint in data['keypoints']:
                self._hash.index(keypoint)
        else:
            if self._data_type is SimpleKeypoints:
                # for keypoint in data['keypoints']:
                for keypoint in data['descriptors']:
                    self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])
                    value = self._data_keys.get(os.path.split(data['path'])[0], 0)
                    value += 1
                    self._data_keys[os.path.split(data['path'])[0]] = value
            else:
                self._hash.add_dataset(data['descriptors'], os.path.split(data['path'])[0])

    def matching(self, data):
        imgs = dict()
        if data is not None:
            for keypoint in data['descriptors']:
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
            logger.logger.debug(self._data_keys[max_key])
            logger.logger.debug(imgs[max_key] / (self._data_keys[max_key] * 1.0))
            return max_key
        return None

    def vect_matching(self, data):
        imgs = dict()
        if data is not None:
            neig = self._hash.neighbours(data['keypoints'])
            logger.logger.debug(neig)
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
            return max_key
        return None