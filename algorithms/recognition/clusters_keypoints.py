__author__ = 'vitalius.parubochyi'

from algorithms.features.matchers import FlannMatcher
from algorithms.clustering.forel import FOREL
from algorithms.clustering.kmeans import KMeans
from algorithms.cvtools.system import saveNumpyImage
from algorithms.features.classifiers import CascadeROIDetector
from keypoints import (KeypointsObjectDetector,
                       drawClusters, drawKeypoints, drawLine,
                       listToNumpy_ndarray, numpy_ndarrayToList,
                       BRISKDetectorType, ORBDetectorType,
                       verifying)
import logger
import numpy
import sys


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
        if self._use_template:
            if self._template_layer == 0:
                self.update_hash_templateL0(data)
            elif self._template_layer == 1:
                self.update_hash_templateL1(data)
            else:
                logger.logger.debug("Detector doesn't has such template layer.")

    def update_hash_templateL0(self, data):
        if len(self._etalon) == 0:
            self._etalon = data['clusters']
        else:
            matcher = FlannMatcher()
            for index in range(0, len(self._etalon)):
                et_cluster = self._etalon[index]
                dt_cluster = data['clusters'][index]
                if et_cluster is None or len(et_cluster) == 0:
                    self._etalon[index] = et_cluster
                elif dt_cluster is None or len(dt_cluster) == 0:
                    self._etalon[index] = et_cluster
                else:
                    matches1 = matcher.knnMatch(et_cluster, dt_cluster, k=3)
                    matches2 = matcher.knnMatch(dt_cluster, et_cluster, k=3)

                    good = []
                    # for v in matches:
                    # if len(v) >= 1:
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
                                                good.append(et_cluster[m.queryIdx])
                                                good.append(dt_cluster[m.trainIdx])
                    self._etalon[index] = listToNumpy_ndarray(good)
        # print "=========================="
        # for etalon in self._etalon:
        #     if etalon is not None:
        #         print len(etalon)
        #     else:
        #         print 0
        # print "=========================="

    def update_hash_templateL1(self, data):
        """

        max_weight = se*suma(i=1,k-1: 1+2*i) + k*(n-k)*se,
        where
            n - count of images,
            k - count of identical matches, k <= n,
            se - single estimate, I used se=1

        :param data:
        :return:
        """
        logger.logger.debug("update_hash_templateL1")
        if len(self._hash) == 1:
            self._etalon = []
            for cluster in data['clusters']:
                weight_cluster = []
                for desc in cluster:
                    weight_cluster.append((desc, 1))
                self._etalon.append(weight_cluster)
        else:
            matcher = FlannMatcher()
            for index in range(0, len(self._etalon)):
                dt_cluster = data['clusters'][index]
                if dt_cluster is None or len(dt_cluster) == 0:
                    break
                et_cluster = self._etalon[index]
                # for dt in dt_cluster:
                #     dt_is = False
                #     weight_cluster = []
                #     for d, c in et_cluster:
                #         if numpy.array_equal(d, dt):
                ##             c += 1
                            # dt_is = True
                        # weight_cluster.append((d, c))
                    # if not dt_is:
                    #     weight_cluster.append((dt, 0))
                    # et_cluster = weight_cluster
                for obj in self._hash:
                    if data['path'] == obj['path']:
                        break
                    ob_cluster = obj['clusters'][index]
                    if ob_cluster is None or len(ob_cluster) == 0:
                        break
                    matches1 = matcher.knnMatch(listToNumpy_ndarray(ob_cluster),
                                                listToNumpy_ndarray(dt_cluster), k=5)
                    # matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster),
                    #                             listToNumpy_ndarray(ob_cluster), k=5)
                    good = []

                    for v in matches1:
                        if len(v) >= 1:
                            best = None
                            dist = -1
                            for m in v:
                                if m.distance == 0:
                                    best = m
                                    dist = 0
                                else:
                                    for d, c in et_cluster:
                                        # if numpy.array_equal(d, dt_cluster[m.trainIdx]):
                                        if dist < c / (1.0 * m.distance):
                                            dist = c / (1.0 * m.distance)
                                            best = m
                                        break
                            ob_is = False
                            dt_is = False
                            new_cluster = []
                            for d, c in et_cluster:
                                if numpy.array_equal(d, ob_cluster[best.queryIdx]):
                                    c += 1
                                    ob_is = True
                                if numpy.array_equal(d, dt_cluster[best.trainIdx]):
                                    c += 1
                                    dt_is = True
                                new_cluster.append((d, c))
                            if not ob_is:
                                new_cluster.append((ob_cluster[best.queryIdx], 1))
                            if not dt_is:
                                new_cluster.append((dt_cluster[best.trainIdx], 1))
                            et_cluster = new_cluster
                    # for v in matches1:
                    #     if len(v) >= 1:
                    #         for m in v:
                    #             # m = v[0]
                    #             for c in matches2:
                    #                 if len(c) >= 1:
                    #                     for n in c:
                    #                         # n = c[0]
                    #                         if m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx:
                    #                             ob_is = False
                    #                             dt_is = False
                    #                             new_cluster = []
                    #                             for d, c in et_cluster:
                    #                                 if numpy.array_equal(d, ob_cluster[m.queryIdx]):
                    #                                     c += 1
                    #                                     ob_is = True
                    #                                 if numpy.array_equal(d, dt_cluster[m.trainIdx]):
                    #                                     c += 1
                    #                                     dt_is = True
                    #                                 new_cluster.append((d, c))
                    #                             if not ob_is:
                    #                                 new_cluster.append((ob_cluster[m.queryIdx], 1))
                    #                             if not dt_is:
                    #                                 new_cluster.append((dt_cluster[m.trainIdx], 1))
                    #                             et_cluster = new_cluster
                    self._etalon[index] = et_cluster

    def importSources(self, source):
        self._etalon = []
        logger.logger.debug("Database loading started...")
        if self._use_template:
            if self._template_layer == 0:
                self.importSources_L0Template(source)
            elif self._template_layer == 1:
                self.importSources_L1Template(source)
            else:
                logger.logger.debug("Detector doesn't has such template layer.")
        else:
            self.importSources_Database(source)
        logger.logger.debug("Database loading finished.")

    def importSources_Database(self, source):
        etalon = source['etalon']
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

    def importSources_L0Template(self, source):
        for j in range(0, len(source.keys())):
            self._etalon.append([])
        for c_num, cluster in source.iteritems():
            etalon_cluster = []
            for d_num, descriptor in cluster.iteritems():
                etalon_cluster.append(listToNumpy_ndarray(descriptor))
            self._etalon[int(c_num)] = etalon_cluster

    def importSources_L1Template(self, source):
        for j in range(0, len(source.keys())):
            self._etalon.append([])
        for c_num, cluster in source.iteritems():
            etalon_cluster = []
            for k in range(0, len(cluster.keys())):
                etalon_cluster.append([])
            for d_num, desc_dict in cluster.iteritems():
                etalon_cluster[int(d_num)] = (listToNumpy_ndarray(desc_dict['descriptor']),
                                              int(desc_dict['count']))
            self._etalon[int(c_num)] = etalon_cluster

    def exportSources(self):
        if self._use_template:
            if self._template_layer == 0:
                return self.exportSources_L0Template()
            elif self._template_layer == 1:
                return self.exportSources_L1Template()
            else:
                logger.logger.debug("Detector doesn't has such template layer.")
        else:
            return self.exportSources_Database()
        return dict()

    def exportSources_Database(self):
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

    def exportSources_L0Template(self):
        sources = dict()
        for index in range(0, len(self._etalon)):
            cluster = self._etalon[index]
            cluster_dict = dict()
            i_desc = 0
            for descriptor in cluster:
                cluster_dict[i_desc] = numpy_ndarrayToList(descriptor)
                i_desc += 1
            sources[str(index)] = cluster_dict
        return sources

    def exportSources_L1Template(self):
        sources = dict()
        for index in range(0, len(self._etalon)):
            et_weight_cluster = self._etalon[index]
            cluster = dict()
            i = 0
            for d, c in et_weight_cluster:
                obj = dict()
                # desc_dict = dict()
                # for indx in range(0, len(d)):
                #     desc_dict[str(indx)] = str(d[indx])
                obj['descriptor'] = numpy_ndarrayToList(d)
                obj['count'] = c
                cluster[str(i)] = obj
                i += 1
            sources[str(index)] = cluster
        return sources

    def detect(self, data):
        if self.data_detect(data):
            data['clustering'] = drawClusters(data['true_clusters'], data['roi'])

    def importDBSettings(self, settings):
        detector = settings.get('Detector Settings', dict())
        if settings.get('Detector Type') == 'BRISK':
            self.kodsettings.detector_type = BRISKDetectorType
            self.kodsettings.brisk_settings.thresh = detector['Thresh']
            self.kodsettings.brisk_settings.octaves = detector['Octaves']
            self.kodsettings.brisk_settings.patternScale = detector['Pattern Scale']
        elif settings.get('Detector Type') == 'ORB':
            self.kodsettings.detector_type = ORBDetectorType
            self.kodsettings.orb_settings.features = detector['Number of features']
            self.kodsettings.orb_settings.scaleFactor = detector['Scale Factor']
            self.kodsettings.orb_settings.nlevels = detector['Number of levels']

    def exportDBSettings(self):
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

    def importSettings(self, settings):
        if len(settings.keys()) > 0:
            logger.logger.debug("Settings loading started...")
            self.kodsettings.importSettings(settings['KODSettings'])
            self.kodsettings.dump()
            if self._cascadeROI is None:
                self._cascadeROI = CascadeROIDetector()
            self._cascadeROI.importSettings(settings['Face Cascade Detector'])
            logger.logger.debug('Face Cascade Detector')
            self._cascadeROI.classifierSettings.dump()
            if self._eyeROI is None:
                self._eyeROI = CascadeROIDetector()
            self._eyeROI.importSettings(settings['Eye Cascade Detector'])
            logger.logger.debug('Eye Cascade Detector')
            self._eyeROI.classifierSettings.dump()
            logger.logger.debug("Settings loading finished.")
            return True
        return False

    def exportSettings(self):
        info = dict()
        info['KODSettings'] = self.kodsettings.exportSettings()
        info['Face Cascade Detector'] = self._cascadeROI.exportSettings()
        info['Eye Cascade Detector'] = self._eyeROI.exportSettings()
        return info

    @verifying
    def verify(self, data):
        if self._use_template:
            if self._template_layer == 0:
                return self.verify_template_L0(data)
            elif self._template_layer == 1:
                return self.verify_template_L1(data)
            else:
                logger.logger.debug("Detector doesn't has such template layer.")
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
                if (test is None) or (source is None):
                    logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
                    self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
                else:
                    matches = matcher.knnMatch(test, source, k=1)
                    # dataTest = dict()
                    # dataTest['data'] = data['roi']
                    # dataTest['keypoints'] = data['true_clusters'][i]['items']
                    # saveNumpyImage("D:/Test/imageData" + str(i) + ".png", drawKeypoints(dataTest))
                    # dTest = dict()
                    # dTest['data'] = d['roi']
                    # dTest['keypoints'] = d['true_clusters'][i]['items']
                    # saveNumpyImage("D:/Test/imageD" + str(i) + ".png", drawKeypoints(dTest))
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
                    logger.sys_logger.debug("Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): "
                                            + str(prob * 100) + "%")
                    self._log += "Cluster #" + str(i + 1) + " (Size: " + str(len(source)) + "): " + str(prob * 100) \
                                 + "%" + "\n"
            suma = 0
            for val in res:
                suma += val
            logger.sys_logger.debug("Total for image: " + str(suma / len(res)))
            self._log += "Total for image: " + str(suma / len(res)) + "\n"
            gres.append(suma / len(res))
        s = 0
        for val in gres:
            s += val
        logger.logger.debug("Total: " + str(s / len(gres)))
        self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        return s / len(gres)

    def verify_template_L0(self, data):
        matcher = FlannMatcher()
        res = []
        prob = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        for index in range(0, len(self._etalon)):
            et_cluster = self._etalon[index]
            dt_cluster = data['clusters'][index]
            ms = []
            if et_cluster is None or dt_cluster is None:
                break
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster, numpy.uint8),
                                            listToNumpy_ndarray(dt_cluster, numpy.uint8), k=2)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster, numpy.uint8),
                                            listToNumpy_ndarray(et_cluster, numpy.uint8), k=2)
                # for v in matches:
                # if len(v) >= 1:
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
                val = (len(res[index]) / (1.0 * len(self._etalon[index]))) * 100
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Positive: " + str(len(res[index])) + " Probability: " + str(val))
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) \
                             + " Positive: " + str(len(res[index])) + " Probability: " + str(val) + "\n"
                prob += val
            else:
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index]))
                                        + " Invalid.")
                self._log += "Cluster #" + str(index + 1) + ": " + str(len(self._etalon[index])) + " Invalid.\n"
        logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        return prob / (1.0 * len(res))

    def verify_template_L1(self, data):
        matcher = FlannMatcher()
        res = []
        prob = 0
        self._log += "Test: " + data['path'] + "\n"
        logger.sys_logger.debug("Image: " + data['path'])
        logger.sys_logger.debug("Template size: ")
        self._log += "Template size: " + "\n"
        for index in range(0, len(self._etalon)):
            et_weight_cluster = self._etalon[index]
            et_cluster = []
            cluster_weight = 0
            for d, c in et_weight_cluster:
                if c > 0:
                    et_cluster.append(d)
                    cluster_weight += c
            dt_cluster = data['clusters'][index]
            ms = []
            if et_cluster is None or dt_cluster is None:
                break
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                matches1 = matcher.knnMatch(listToNumpy_ndarray(et_cluster), listToNumpy_ndarray(dt_cluster), k=2)
                matches2 = matcher.knnMatch(listToNumpy_ndarray(dt_cluster), listToNumpy_ndarray(et_cluster), k=2)
                # for v in matches:
                # if len(v) >= 1:
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
                                            ms.append(et_cluster[m.queryIdx])
                c_val = 0
                for item in ms:
                    for d, c in et_weight_cluster:
                        if numpy.array_equal(d, item):
                            c_val += c
                res.append(c_val / cluster_weight)
                val = (c_val / (1.0 * cluster_weight)) * 100
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight)
                                        + " Positive: " + str(c_val) + " Probability: " + str(val))
                self._log += "Cluster #" + str(index + 1) + ": " + str(cluster_weight) \
                             + " Positive: " + str(c_val) + " Probability: " + str(val) + "\n"
                prob += val
            else:
                logger.sys_logger.debug("Cluster #" + str(index + 1) + ": " + str(cluster_weight)
                                        + " Invalid.")
                self._log += "Cluster #" + str(index + 1) + ": " + str(cluster_weight) + " Invalid.\n"
        logger.sys_logger.debug("Probability: " + str((prob / (1.0 * len(res)))))
        self._log += "Probability: " + str((prob / (1.0 * len(res)))) + "\n"
        return prob / (1.0 * len(res))

    def compare(self, f_imgobj, s_imgobj):
        if not self.data_detect(f_imgobj):
            logger.logger.debug("First image data isn't valid.")
            return False
        if not self.data_detect(s_imgobj):
            logger.logger.debug("Second image data isn't valid.")
            return False
        # matcher = FlannMatcher()
        # gres = []
        # for i in range(0, len(f_imgobj['clusters'])):
        # first = f_imgobj['clusters'][i]
        #     second = s_imgobj['clusters'][i]
        #     res = []
        #     if (first is None) or (second is None):
        #         logger.logger.debug("Cluster #" + str(i + 1) + ": Invalid")
        #         self._log += "Cluster #" + str(i + 1) + ": Invalid\n"
        #     else:
        #         matches = matcher.knnMatch(first, second, k=1)
        #         ms = []
        #         for v in matches:
        #             if len(v) >= 1:
        #                 # if len(v) >= 2:
        #                 m = v[0]
        #                 # n = v[1]
        #                 if m.distance < self.kodsettings.neighbours_distance:
        #                     ms.append(m)
        #         prob = len(ms) / (1.0 * len(matches))
        #         res.append(prob * 100)
        #         logger.logger.debug("Cluster #" + str(i + 1) + " (Size: " + str(len(second)) + "): "
        #                             + str(prob * 100) + "%")
        #         self._log += "Cluster #" + str(i + 1) + " (Size: " + str(len(second)) + "): " + str(prob * 100) \
        #                      + "%" + "\n"
        #     suma = 0
        #     for val in res:
        #         suma += val
        #     logger.logger.debug("Total for image: " + str(suma / len(res)))
        #     self._log += "Total for image: " + str(suma / len(res)) + "\n"
        #     gres.append(suma / len(res))
        # s = 0
        # for val in gres:
        #     s += val
        # logger.logger.debug("Total: " + str(s / len(gres)))
        # self._log += "\nTotal: " + str(s / len(gres)) + "\n\n"
        self._compare_descriptors(f_imgobj, s_imgobj)

    def _compare_descriptors(self, f_imgobj, s_imgobj):
        matcher = FlannMatcher()
        matches = matcher.knnMatch(f_imgobj['descriptors'], s_imgobj['descriptors'], k=1)
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        stat = dict()
        for v in matches:
            if len(v) >= 1:
                # if len(v) >= 2:
                m = v[0]
                logger.logger.debug("Query Index: " + str(m.queryIdx) + " Train Index: " + str(m.trainIdx)
                                    + " Distance: " + str(m.distance))
                for i in range(0, 100, 1):
                    if m.distance <= i * 10:
                        val = stat.get(str(i * 10), 0)
                        val += 1
                        stat[str(i * 10)] = val
                        break
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        for k, z in stat.iteritems():
            logger.logger.debug(k + ": " + str(z))
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.logger.debug("First image descriptors number: " + str(len(f_imgobj['descriptors'])))
        logger.logger.debug("Second image descriptors number: " + str(len(s_imgobj['descriptors'])))
        ms = []
        for v in matches:
            if len(v) >= 1:
                # if len(v) >= 2:
                m = v[0]
                # n = v[1]
                if m.distance < self.kodsettings.neighbours_distance:
                    ms.append(m)
        prob = len(ms) / (1.0 * len(matches))
        logger.logger.debug("Positive matches: " + str(len(ms)) + " Probability: " + str(prob * 100))
        logger.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def _detect(self, data, detector):
        # ROI detection
        rect = self._eyeROI.detectAndJoin(data['roi'], False)
        if len(rect) <= 0:
            return False
        # ROI cutting
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[1] - lefteye[1]) / 2)
        centernose = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        centermouth = (centernose[0], centernose[1] + rect[3])
        leftmouth = (lefteye[0], centermouth[1])
        rightmouth = (righteye[0], centermouth[1])
        # out = drawLine(data['roi'], (lefteye[0], lefteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centereye[0], centereye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (righteye[0], righteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centermouth[0], centermouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (leftmouth[0], leftmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (rightmouth[0], rightmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        centers = [lefteye, righteye, centereye, centernose, leftmouth, rightmouth]
        self.filter_keypoints(data)

        clusters = KMeans(data['keypoints'], 0, centers, 3)
        # clusters = FOREL(obj['keypoints'], 40)
        # showClusters(clusters, out)
        data['true_clusters'] = clusters
        descriptors = []
        for cluster in clusters:
            desc = detector.computeImage(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
        data['clusters'] = descriptors
        return True

    def filter_keypoints(self, data):
        clusters = FOREL(data['keypoints'], 20)
        keypoints = []
        # cls = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            img = dict()
            img['data'] = data['roi']
            img['keypoints'] = cluster['items']
            if p > 0.02:
                # cls.append(cluster)
                for item in cluster['items']:
                    keypoints.append(item)
        data['keypoints'] = keypoints
