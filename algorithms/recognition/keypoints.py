from algorithms.features.detectors import (BRISKDetector, ORBDetector,
                                           BRISKDetectorSettings, ORBDetectorSettings)
from algorithms.features.classifiers import (getROIImage,
                                             RectsIntersect, RectsFiltering)
from algorithms.recognition.features import (FeatureDetector,
                                             BRISKDetectorType, ORBDetectorType)
from algorithms.cvtools.visualization import showClusters, drawLine
from algorithms.features.matchers import FlannMatcher
from algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList
# from algorithms.hashing.nearpy_hash import NearPyHash
from algorithms.clustering.forel import FOREL
from algorithms.clustering.kmeans import KMeans
import logger
import numpy
import os


LSHashType = 0
NearPyHashType = 1


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    neighbours_distance = 1.0
    max_hash_length = 600
    detector_type = BRISKDetectorType
    brisk_settings = BRISKDetectorSettings()
    orb_settings = ORBDetectorSettings()


def identifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Identifying...")
        res = None
        if self.data_detect(self, data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Identifying finished.")
        return res
    return wrapped


def verifying(fn):
    def wrapped(self, data):
        logger.logger.debug("Verifying...")
        self._log = ""
        res = False
        if self.data_detect(data):
            if data is not None:
                res = fn(self, data)
        logger.logger.debug("Verifying finished.")
        return res
    return wrapped


class KeypointsObjectDetector:
    kodsettings = KODSettings()

    def __init__(self):
        self._hash = None
        self._cascadeROI = None
        self._detector = None
        self._eyeROI = None
        self._use_etalon = False
        self._log = ""

    def log(self):
        return self._log

    def setUseTemplate(self, use):
        self._use_etalon = use

    def addSource(self, data):
        if self.data_detect(data):
            self.update_hash(data)

    def addSources(self, data_list):
        for data in data_list:
            self.addSource(data)

    def importSources(self, data):
        pass

    def exportSources(self):
        pass

    @identifying
    def identify(self, data):
        pass

    @verifying
    def verify(self, data):
        logger.logger.debug("Detector doesn't support image verification.")
        pass

    def detect(self, data):
        pass

    def data_detect(self, data):
        # ROI detection
        rect = self._cascadeROI.detectAndJoin(data['data'], False, RectsFiltering)
        # ROI cutting
        data['roi'] = getROIImage(data['data'], rect)
        # showNumpyImage(data['roi'])
        # Keypoints detection
        detector = FeatureDetector()
        if self.kodsettings.detector_type is BRISKDetectorType:
            brisk_detector = BRISKDetector(self.kodsettings.brisk_settings.thresh,
                                           self.kodsettings.brisk_settings.octaves,
                                           self.kodsettings.brisk_settings.patternScale)
            detector.set_detector(brisk_detector)
        else:
            orb_detector = ORBDetector(self.kodsettings.orb_settings.features,
                                       self.kodsettings.orb_settings.scaleFactor,
                                       self.kodsettings.orb_settings.nlevels)
            detector.set_detector(orb_detector)
        obj = detector.detectAndComputeImage(data['roi'])
        data['keypoints'] = obj['keypoints']
        data['descriptors'] = obj['descriptors']
        if data['descriptors'] is None:
            data['descriptors'] = []
        return self._detect(data, detector)

    def _detect(self, data, detector):
        pass

    def update_hash(self, data):
        pass


class FeaturesMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._data_keys = dict()
        if self.kodsettings.detector_type is BRISKDetectorType:
            size = 64
        else:
            size = 32
        self._hash = NearPyHash(size)
        self._hash.addRandomBinaryProjectionsEngine(10)

    def update_hash(self, data):
        # for keypoint in data['keypoints']:
        for keypoint in data['descriptors']:
            self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])
            value = self._data_keys.get(os.path.split(data['path'])[0], 0)
            value += 1
            self._data_keys[os.path.split(data['path'])[0]] = value

    @identifying
    def identify(self, data):
        imgs = dict()
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

    def _detect(self, data, detector):
        key_arrays = keypointsToArrays(data['keypoints'])
        data['keypoints'] = key_arrays
        return True


class SpiralKeypointsVectorDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = NearPyHash(self.kodsettings.max_hash_length)
        self._hash.addRandomBinaryProjectionsEngine(10)

    def update_hash(self, data):
        self._hash.add_dataset(data['descriptors'], os.path.split(data['path'])[0])

    @identifying
    def identify(self, data):
        imgs = dict()
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

    def _detect(self, data, detector):
        height, width = data['roi'].shape[0], data['roi'].shape[1]
        order_keys = obj.keypoints()  # spiralSort(obj, width, height)
        order_keys = minimizeSort(obj)
        obj.keypoints(keypointsToArrays(order_keys))
        key_arr = joinVectors(obj.keypoints())
        while len(key_arr) < self.kodsettings.max_hash_length:
            key_arr.append(0)
        data['keypoints'] = listToNumpy_ndarray(key_arr)
        return True


class ObjectsMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self.etalon = []
        self._hash = []

    def update_hash(self, data):
        del data['data']
        del data['roi']
        del data['keypoints']
        self._hash.append(data)
        ##############################################
        if len(self.etalon) == 0:
            self.etalon = data['descriptors']
        else:
            matcher = FlannMatcher()
            matches1 = matcher.knnMatch(self.etalon, data['descriptors'], k=1)
            matches2 = matcher.knnMatch(data['descriptors'], self.etalon, k=1)

            good = []
            # for v in matches:
            #         if len(v) >= 1:
                    # if len(v) >= 2:
                    #     m = v[0]
                    # n = v[1]
                    # good.append(self.etalon[m.queryIdx])
                    #     if m.distance < self.kodsettings.neighbours_distance:
                    #         good.append(self.etalon[m.queryIdx])
                    # good.append(data['descriptors'][m.queryIdx])
                    # good.append(self.etalon[m.trainIdx])
                    #
                    # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    #     good.append(self.etalon[m.queryIdx])
                    # else:
                    #     good.append(self.etalon[m.queryIdx])
                    #     good.append(data['descriptors'][m.trainIdx])
                    # good.append(data['descriptors'][m.queryIdx])
                    # good.append(self.etalon[m.trainIdx])

            for v in matches1:
                if len(v) >= 1:
                    m = v[0]
                    for c in matches2:
                        if len(c) >= 1:
                            n = c[0]
                            if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                good.append(self.etalon[m.queryIdx])
                                good.append(data['descriptors'][n.queryIdx])
            self.etalon = listToNumpy_ndarray(good)

    @identifying
    def identify(self, data):
        imgs = dict()
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

    @verifying
    def verify(self, data):
        matcher = FlannMatcher()
        matches = matcher.knnMatch(self.etalon, data['descriptors'], k=1)
        # matches2 = matcher.knnMatch(data['descriptors'], self.etalon, k=1)
        ms = []
        for v in matches:
            if len(v) >= 1:
            # if len(v) >= 2:
                m = v[0]
                # n = v[1]
                # logger.logger.debug(str(m.distance) + " " + str(m.queryIdx) + " " + str(m.trainIdx) + " | "
                # + str(n.distance) + " " + str(n.queryIdx) + " " + str(n.trainIdx))
                if m.distance < self.kodsettings.neighbours_distance:
                # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    ms.append(m)
                # else:
                #     ms.append(m)
                #     ms.append(n)
            # for v in matches1:
            # if len(v) >= 1:
            #         m = v[0]
            #         for c in matches2:
            #             if len(c) >= 1:
            #                 n = c[0]
            #                 if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
            #                     ms.append(m)

        logger.logger.debug("Image: " + data['path'])
        logger.logger.debug("Template size: " + str(len(self.etalon)) + " descriptors.")
        logger.logger.debug("Positive matched descriptors: " + str(len(ms)))
        logger.logger.debug("Probability: " + str((len(ms) / (1.0 * len(self.etalon))) * 100))
        return True

    @staticmethod
    def merge_results(results):
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

    @staticmethod
    def print_dict(d):
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


class ClustersMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = []
        self._etalon = []

    def update_hash(self, data):
        del data['data']
        # del data['roi']
        del data['keypoints']
        del data['descriptors']
        self._hash.append(data)
        ##############################################
        if len(self._etalon) == 0:
            self._etalon = data['clusters']
        else:
            matcher = FlannMatcher()
            for index in range(0, len(self._etalon)):
                et_cluster = self._etalon[index]
                dt_cluster = data['clusters'][index]
                matches1 = matcher.knnMatch(et_cluster, dt_cluster, k=2)
                matches2 = matcher.knnMatch(dt_cluster, et_cluster, k=2)

                good = []
                # for v in matches:
                #     if len(v) >= 1:
                    # if len(v) >= 2:
                    #     m = v[0]
                    #     n = v[1]
                    #     good.append(self.etalon[m.queryIdx])
                    #     if m.distance < self.kodsettings.neighbours_distance:
                    #         good.append(self.etalon[m.queryIdx])
                    #     good.append(data['descriptors'][m.queryIdx])
                    #     good.append(self.etalon[m.trainIdx])
                    #
                    #     if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    #         good.append(self.etalon[m.queryIdx])
                    #     else:
                    #         good.append(self.etalon[m.queryIdx])
                    #         good.append(data['descriptors'][m.trainIdx])
                    #         good.append(data['descriptors'][m.queryIdx])
                    #         good.append(self.etalon[m.trainIdx])

                for v in matches1:
                    if len(v) >= 1:
                        for m in v:
                        # m = v[0]
                            for c in matches2:
                                if len(c) >= 1:
                                    for n in c:
                                        # n = c[0]
                                        if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                            good.append(self._etalon[index][m.queryIdx])
                                            good.append(data['clusters'][index][n.queryIdx])
                self._etalon[index] = listToNumpy_ndarray(good)
            local_clusters = []
            for cl_set in self._etalon:
                cl = dict()
                cl['center'] = (0, 0)
                cl['items'] = cl_set
                local_clusters.append(cl)
            showClusters(local_clusters, data['roi'])

    def importSources(self, source):
        self._etalon = []
        etalon = source['etalon']
        logger.logger.debug("Database loading started...")
        for j in range(0, len(etalon.keys())):
            self._etalon.append([])
        for c_num, cluster in etalon.iteritems():
            etalon_cluster = []
            for k in range(0, len(cluster.keys())):
                etalon_cluster.append([])
            for d_num, descriptor in cluster.iteritems():
                desc = []
                for i in range(0, len(descriptor.keys())):
                    desc.append([])
                for e_num, element in descriptor.iteritems():
                    desc[int(e_num)] = numpy.uint8(element)
                etalon_cluster[int(d_num)] = listToNumpy_ndarray(desc)
            self._etalon[int(c_num) - 1] = listToNumpy_ndarray(etalon_cluster)
        logger.logger.debug("Database loading finished.")

    def exportSources(self):
        sources = dict()
        etalon = dict()
        i = 0
        for cluster in self._etalon:
            i += 1
            elements = dict()
            for index in range(0, len(cluster)):
                descriptor = cluster[index]
                desc_dict = dict()
                for indx in range(0, len(descriptor)):
                    desc_dict[str(indx)] = str(descriptor[indx])
                elements[str(index)] = desc_dict
            etalon[str(i)] = elements
        sources["etalon"] = etalon
        return sources

    def detect(self, data):
        if self.data_detect(data):
            data['clustering'] = drawClusters(data['true_clusters'], data['roi'])

    def importSettings(self, settings):
        info = dict()
        detector = settings.get('Detector Settings', dict())
        if settings.get('Detector Type') == 'BRISK':
            self.kodsettings.detector_type = BRISKDetectorType
            self.kodsettings.brisk_settings.thresh = detector['Thresh']
            self.kodsettings.brisk_settings.octaves = detector['Octaves']
            self.kodsettings.brisk_settings.patternScale = detector['Pattern Scale']
            info['Detector Settings'] = settings
        elif settings.get('Detector Type') == 'ORB':
            self.kodsettings.detector_type = ORBDetectorType
            self.kodsettings.orb_settings.features = detector['Number of features']
            self.kodsettings.orb_settings.scaleFactor = detector['Scale Factor']
            self.kodsettings.orb_settings.nlevels = detector['Number of levels']

    def exportSettings(self):
        info = dict()
        info['Database Size'] = str(len(self._hash)) + " images"
        settings = dict()
        if self.kodsettings.detector_type == BRISKDetectorType:
            info['Detector Type'] = 'BRISK'
            settings['Thresh'] = self.kodsettings.brisk_settings.thresh
            settings['Octaves'] = self.kodsettings.brisk_settings.octaves
            settings['Pattern Scale'] = self.kodsettings.brisk_settings.patternScale
        elif self.kodsettings.detector_type == ORBDetectorType:
            info['Detector Type'] = 'ORB'
            settings['Number of features'] = self.kodsettings.orb_settings.features
            settings['Scale Factor'] = self.kodsettings.orb_settings.scaleFactor
            settings['Number of levels'] = self.kodsettings.orb_settings.nlevels
        info['Detector Settings'] = settings
        face_cascade = dict()
        face_cascade['Cascades'] = self._cascadeROI.cascades()
        face_settings = dict()
        face_settings['Scale Factor'] = self._cascadeROI.classifierSettings.scaleFactor
        face_settings['Minimum Neighbors'] = self._cascadeROI.classifierSettings.minNeighbors
        face_settings['Minimum Size'] = self._cascadeROI.classifierSettings.minSize
        face_cascade['Settings'] = face_settings
        info['Face Cascade Detector'] = face_cascade
        info['Database Source'] = "Extended Yale Face Database B. Person Yale12"
        return info

    @verifying
    def verify(self, data):
        if self._use_etalon:
            return self.verify_etalon(data)
        else:
            return self.verify_database(data)

    def verify_database(self, data):
        matcher = FlannMatcher()
        gres = []
        self._log += "Test: " + data['path'] + "\n"
        for d in self._hash:
            res = []
            logger.logger.debug("Source: " + d['path'])
            self._log += "Source: " + d['path'] + "\n"
            for i in range(0, len(d['clusters'])):
                test = data['clusters'][i]
                source = d['clusters'][i]
                matches = matcher.knnMatch(test, source, k=1)

                ms = []
                for v in matches:
                    if len(v) >= 1:
                        # if len(v) >= 2:
                        m = v[0]
                        # n = v[1]
                        if m.distance < self.kodsettings.neighbours_distance:
                            ms.append(m)
                prob = len(ms) / (1.0 * len(matches))
                res.append(prob * 100)
                logger.logger.debug("Part #" + str(i + 1) + ": " + str(prob * 100) + "%")
                self._log += "Part #" + str(i + 1) + ": " + str(prob * 100) + "%" + "\n"
            suma = 0
            for val in res:
                suma += val
            logger.logger.debug("Total for image: " + str(suma / len(res)))
            self._log += "Total for image: " + str(suma / len(res)) + "\n"
            gres.append(suma / len(res))
        s = 0
        for val in gres:
            s += val
        logger.logger.debug("Total: " + str(s / len(gres)))
        self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        return True

    def verify_etalon(self, data):
        matcher = FlannMatcher()
        res = []
        self._log += "Test: " + data['path'] + "\n"
        for index in range(0, len(self._etalon)):
            et_cluster = self._etalon[index]
            dt_cluster = data['clusters'][index]
            matches1 = matcher.knnMatch(et_cluster, dt_cluster, k=2)
            matches2 = matcher.knnMatch(dt_cluster, et_cluster, k=2)
            ms = []
            # for v in matches:
            #     if len(v) >= 1:
                # if len(v) >= 2:
                #     m = v[0]
                    # n = v[1]
                    # logger.logger.debug(str(m.distance) + " " + str(m.queryIdx) + " " + str(m.trainIdx) + " | "
                    #                     + str(n.distance) + " " + str(n.queryIdx) + " " + str(n.trainIdx))
                    # if m.distance < self.kodsettings.neighbours_distance:
                    # if m.distance < self.kodsettings.neighbours_distance * n.distance:
                    #     ms.append(m)
                    # else:
                    #     ms.append(m)
                    #     ms.append(n)
            for v in matches1:
                if len(v) >= 1:
                    for m in v:
                    # m = v[0]
                        for c in matches2:
                            if len(c) >= 1:
                                for n in c:
                                    # n = c[0]
                                    if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                                        ms.append(m)
            res.append(ms)

        prob = 0
        logger.logger.debug("Image: " + data['path'])
        logger.logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        for index in range(0, len(self._etalon)):
            val = (len(res[index]) / (1.0 * len(self._etalon[index]))) * 100
            logger.logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                + " Positive: " + str(len(res[index])) + " Probability: " + str(val))
            self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))\
                         + " Positive: " + str(len(res[index])) + " Probability: " + str(val) + "\n"
            prob += val
        logger.logger.debug("Probability: " + str((prob / (1.0 * len(self._etalon)))))
        self._log += "Probability: " + str((prob / (1.0 * len(self._etalon)))) + "\n"
        return True

    def _detect(self, data, detector):
        # ROI detection
        rect = self._eyeROI.detectAndJoin(data['roi'], False)
        if len(rect) <= 0:
            return False
        # ROI cutting
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[0] - lefteye[0]) / 2)
        center = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        out = drawLine(data['roi'], (lefteye[0], lefteye[1], centereye[0], centereye[1]), (255, 0, 0))
        out = drawLine(out, (centereye[0], centereye[1], righteye[0], righteye[1]), (255, 0, 0))
        out = drawLine(out, (lefteye[0], lefteye[1], center[0], center[1]), (255, 0, 0))
        out = drawLine(out, (righteye[0], righteye[1], center[0], center[1]), (255, 0, 0))
            # drawImage(out)
        centers = [lefteye, righteye, centereye, center]
        self.filter_keypoints(data)

        clusters = KMeans(data['keypoints'], 0, centers)
        # clusters = FOREL(obj['keypoints'], 40)
        showClusters(clusters, out)
        data['true_clusters'] = clusters
        descriptors = []
        for cluster in clusters:
            desc = detector.computeImage(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
        data['clusters'] = descriptors
        return True

    def filter_keypoints(self, data):
        logger.logger.debug(len(data['keypoints']))
        clusters = FOREL(data['keypoints'], 20)
        logger.logger.debug(len(data['keypoints']))
        keypoints = []
        # cls = []
        for cluster in clusters:
            # logger.logger.debug(cluster['items'])
            logger.logger.debug(len(cluster['items']))
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            logger.logger.debug(p)
            # logger.logger.debug(cluster['center'])
            img = dict()
            img['data'] = data['roi']
            img['keypoints'] = cluster['items']
            if p > 0.02:
                # cls.append(cluster)
                for item in cluster['items']:
                    keypoints.append(item)
        data['keypoints'] = keypoints
