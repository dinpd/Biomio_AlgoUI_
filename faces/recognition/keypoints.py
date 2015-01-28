from faces.biom.faces import CascadeROIDetector
from rectmerge import mergeRectangles
from features.tools import (getROIImage, keypointsToArrays, spiralSort, joinVectors, listToNumpy_ndarray,
                            drawImage, drawKeypoints, minimizeSort)
from features.detectors import (BRISKDetector, ORBDetector, FeatureDetector,
                                BRISKDetectorSettings, ORBDetectorSettings, FlannMatcher)
from lshash import LSHash
from features.hashing.nearpy_hash import NearPyHash
import logger
import os


LSHashType = 0
NearPyHashType = 1

FeaturesMatching = 0
SpiralKeypointsVector = 1
ObjectsFlannMatching = 2

BRISKDetectorType = 0
ORBDetectorType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    cascade_list = []
    neighbours_distance = 1.0
    max_hash_length = 600
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self, hash_t=LSHashType, data_t=FeaturesMatching):
        self._hash_type = hash_t
        self._data_type = data_t
        self._data_keys = dict()
        self._hash = None
        self.etalon = []
        self._data_init = False
        self._cascadeROI = None

    def init_hash(self):
        self._cascadeROI = CascadeROIDetector()
        for cascade in self.kodsettings.cascade_list:
            self._cascadeROI.add_cascade(cascade)
        if self.kodsettings.detector_type is BRISKDetectorType:
            size = 64
        else:
            size = 32
        if self._hash_type is LSHashType:
            self._hash = LSHash(128, size)
        else:
            if self._data_type is FeaturesMatching:
                self._hash = NearPyHash(size)
                self._hash.addRandomBinaryProjectionsEngine(10)
            elif self._data_type is SpiralKeypointsVector:
                self._hash = NearPyHash(self.kodsettings.max_hash_length)
                self._hash.addRandomBinaryProjectionsEngine(10)
            elif self._data_type is ObjectsFlannMatching:
                self._hash = []
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
        logger.logger.debug("Identifying...")
        res = None
        if self.data_detect(data):
            if self._data_type is FeaturesMatching:
                if len(self._data_keys) > 0:
                    res = self.matching(data)
            elif self._data_type is SpiralKeypointsVector:
                res = self.vect_matching(data)
            elif self._data_type is ObjectsFlannMatching:
                res = self.flann_matching(data)
        logger.logger.debug("Identifying finished.")
        return res

    def verify(self, data):
        logger.logger.debug("Verifying...")
        res = None
        if self.data_detect(data):
            if self._data_type is FeaturesMatching:
                logger.logger.debug("Data Type doesn't support image verification.")
            elif self._data_type is SpiralKeypointsVector:
                logger.logger.debug("Data Type doesn't support image verification.")
            elif self._data_type is ObjectsFlannMatching:
                res = self.flann_verify(data)
        logger.logger.debug("Verifying finished.")
        return res

    def data_detect(self, data):
        # ROI detection
        rects = self._cascadeROI.detect(data['data'])
        if len(rects) is 0:
            logger.logger.debug("ROI is not found for " + data['path'])
            return False
        rect = mergeRectangles(rects)
        # ROI cutting
        data['roi'] = getROIImage(data['data'], rect)
        # Keypoints detection
        detector = FeatureDetector()
        if self.kodsettings.detector_type is BRISKDetectorType:
            # logger.logger.debug('%d, %d, %f', self.kodsettings.brisk_settings.thresh,
            #                     self.kodsettings.brisk_settings.octaves, self.kodsettings.brisk_settings.patternScale)
            brisk_detector = BRISKDetector(self.kodsettings.brisk_settings.thresh,
                                           self.kodsettings.brisk_settings.octaves,
                                           self.kodsettings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            # logger.logger.debug('%d, %f, %d', self.kodsettings.orb_settings.features,
            #                     self.kodsettings.orb_settings.scaleFactor, self.kodsettings.orb_settings.nlevels)
            orb_detector = ORBDetector(self.kodsettings.orb_settings.features,
                                       self.kodsettings.orb_settings.scaleFactor,
                                       self.kodsettings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        obj = detector.detectAndComputeImage(data['roi'])
        data['keypoints'] = obj.keypoints()
        data['descriptors'] = obj.descriptors()
        if data['descriptors'] is None:
            data['descriptors'] = []
        if self._data_type is FeaturesMatching:
            key_arrays = keypointsToArrays(obj.keypoints())
            data['keypoints'] = key_arrays
        elif self._data_type is SpiralKeypointsVector:
            height, width = data['roi'].shape[0], data['roi'].shape[1]
            order_keys = obj.keypoints()  #spiralSort(obj, width, height)
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
            if self._data_type is FeaturesMatching:
                # for keypoint in data['keypoints']:
                for keypoint in data['descriptors']:
                    self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])
                    value = self._data_keys.get(os.path.split(data['path'])[0], 0)
                    value += 1
                    self._data_keys[os.path.split(data['path'])[0]] = value
            elif self._data_type is SpiralKeypointsVector:
                self._hash.add_dataset(data['descriptors'], os.path.split(data['path'])[0])
            elif self._data_type is ObjectsFlannMatching:
                del data['data']
                del data['roi']
                del data['keypoints']
                self._hash.append(data)
                ###############################################

                if len(self.etalon) == 0:
                    self.etalon = data['descriptors']
                else:
                    matcher = FlannMatcher()
                    matches = matcher.knnMatch(self.etalon, data['descriptors'], k=1)

                    good = []
                    for v in matches:
                        if len(v) >= 1:
                        # if len(v) >= 2:
                            m = v[0]
                            # n = v[1]
                            good.append(self.etalon[m.queryIdx])
                        #     if m.distance < self.kodsettings.neighbours_distance:
                        #         good.append(self.etalon[m.queryIdx])
                                # good.append(data['descriptors'][m.queryIdx])
                                # good.append(self.etalon[m.trainIdx])

                            # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                            #     good.append(self.etalon[m.queryIdx])
                            # else:
                            #     good.append(self.etalon[m.queryIdx])
                            #     good.append(data['descriptors'][m.trainIdx])
                                # good.append(data['descriptors'][m.queryIdx])
                                # good.append(self.etalon[m.trainIdx])

                    self.etalon = listToNumpy_ndarray(good)


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
            logger.logger.debug(len(data['descriptors']))
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

    def flann_matching(self, data):
        imgs = dict()
        if data is not None:
            matcher = FlannMatcher()
            for d in self._hash:
                matches = matcher.knnMatch(d['descriptors'],
                                           data['descriptors'],
                                           k=2)
                good = []
                count = len(matches)
                for v in matches:
                    if len(v) is 2:
                        m = v[0]
                        n = v[1]
                        if m.distance < self.kodsettings.neighbours_distance * n.distance:
                            good.append([m])
                    else:
                        count -= 1
                key = d['path']
                value = imgs.get(key, dict())
                value['id'] = os.path.split(d['path'])[1]
                value['all'] = count
                value['positive'] = len(good)
                value['negative'] = count - len(good)
                value['prob'] = len(good) / (1.0 * count)
                imgs[key] = value
            res = self.merge_results(imgs)
            result = self.print_dict(res)
            return result
        return None

    def merge_results(self, results):
        mres = dict()
        res = dict()
        for key in results.keys():
            value = results.get(key, dict())
            str_key = os.path.split(key)[0]
            avg = mres.get(str_key, dict({'id': str_key, 'all': 0, 'positive': 0,
                                          'negative': 0, 'prob': 0, 'count': 0}))
            avg['all'] += value['all']
            avg['positive'] += value['positive']
            avg['negative'] += value['negative']
            avg['prob'] += value['prob']
            avg['count'] += 1
            mres[str_key] = avg
        for k in mres.keys():
            value = mres.get(k, dict())
            dic = dict()
            dic['id'] = value['id']
            dic['all'] = value['all']  # / value['count']
            dic['positive'] = value['positive']  # / value['count']
            dic['negative'] = value['negative']  # / value['count']
            dic['prob'] = value['prob'] / value['count']
            res[k] = dic
        return res

    def print_dict(self, d):
        logs = "Keys\tAll Matches\tPositive Matches\tNegative Matches\tProbability\n"
        amatches = 0
        gmatches = 0
        nmatches = 0
        prob = 0
        count = 0
        max_val = 0
        max_key = ''
        max_low = 0
        low_key = ''
        for key in d.keys():
            value = d.get(key, dict())
            logs += (value['id'] + "\t" + str(value['all']) + "\t" + str(value['positive']) + "\t"
                     + str(value['negative']) + "\t" + str(value['prob'] * 100) + "\n")
            amatches += value['all']
            gmatches += value['positive']
            nmatches += value['negative']
            prob += value['prob'] * 100
            count += 1
            if max_val < value['prob']:
                max_key = key
                max_val = value['prob']
            if max_low < value['prob'] and max_key != key:
                low_key = key
                max_low = value['prob']
        v = d.get(max_key, dict())
        logs += ("Max:\t" + v['id'] + "\t" + str(v['all']) + "\t" + str(v['positive']) + "\t"
                 + str(v['negative']) + "\t" + str(v['prob'] * 100) + "\n")
        v1 = d.get(low_key, dict())
        logs += ("Next:\t" + v1['id'] + "\t" + str(v1['all']) + "\t" + str(v1['positive']) + "\t"
                 + str(v1['negative']) + "\t" + str(v1['prob'] * 100) + "\n")
        logs += ("Total:\t\t" + str(amatches) + "\t" + str(gmatches) + "\t" + str(nmatches)
                 + "\t" + str(prob) + "\n")
        if count > 0:
            logs += ("Average:\t\t" + str(amatches / (1.0 * count)) + "\t" + str(gmatches / (1.0 * count))
                     + "\t" + str(nmatches / (1.0 * count)) + "\t" + str(prob / (1.0 * count)) + "\n")
        logger.logger.debug(logs)
        return max_key

    def flann_verify(self, data):
        imgs = dict()
        if data is not None:
            matcher = FlannMatcher()
            # etalon = []
            # for d in self._hash:
            #     if len(etalon) == 0:
            #         etalon = d['descriptors']
            #     else:
            #         matches = matcher.knnMatch(d['descriptors'], etalon, k=2)
            #
            #         good = []
            #         for v in matches:
            #             # if len(v) >= 1:
            #             #     m = v[0]
            #             #     if m.distance < self.kodsettings.neighbours_distance:
            #             #         good.append(d['descriptors'][m.queryIdx])
            #             if len(v) >= 2:
            #                 m = v[0]
            #                 n = v[1]
            #
            #                 if m.distance < self.kodsettings.neighbours_distance * n.distance:
            #                     good.append(d['descriptors'][m.queryIdx])
            #                     good.append(etalon[m.trainIdx])
            #
            #         etalon = listToNumpy_ndarray(good)

            matches = matcher.knnMatch(self.etalon, data['descriptors'], k=1)
            ms = []
            for v in matches:
                if len(v) >= 1:
                # if len(v) >= 2:
                    m = v[0]
                    # n = v[1]
                    # logger.logger.debug(str(m.distance) + " " + str(m.queryIdx) + " " + str(m.trainIdx) + " | "
                    #                     + str(n.distance) + " " + str(n.queryIdx) + " " + str(n.trainIdx))
                    if m.distance < self.kodsettings.neighbours_distance:
                    # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                        ms.append(m)
                    # else:
                    #     ms.append(m)
                    #     ms.append(n)
            logger.logger.debug("Image: " + data['path'])
            logger.logger.debug("Template size: " + str(len(self.etalon)) + " descriptors.")
            logger.logger.debug("Positive matched descriptors: " + str(len(ms)))
            logger.logger.debug("Probability: " + str((len(ms) / (1.0 * len(self.etalon))) * 100))
            return True
        return None