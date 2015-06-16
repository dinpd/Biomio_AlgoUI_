from algorithms.features.matchers import FlannMatcher
from algorithms.recognition.keypoints import (KeypointsObjectDetector,
                                              identifying, verifying)
from algorithms.cvtools.types import listToNumpy_ndarray
import logger


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
        # #############################################
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
                    # ms.append(m)
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
