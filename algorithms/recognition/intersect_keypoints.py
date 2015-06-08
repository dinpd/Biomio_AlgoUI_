from algorithms.features.matchers import FlannMatcher
from keypoints import (KeypointsObjectDetector,
                       meanDistance,
                       listToNumpy_ndarray,
                       verifying)
import logger
import sys


class TubeSet:
    def __init__(self):
        self._keypoints = []
        self._descriptors = []
        self._info = []
        self._base_distance = -1

    def add(self, keypoint, descriptor, info=""):
        self._keypoints.append(keypoint)
        self._descriptors.append(descriptor)
        self._info.append(info)
        return len(self._keypoints) - 1

    def set_basic_distance(self, distance):
        self._base_distance = distance

    def basic_distance(self):
        return self._base_distance

    def count(self):
        return len(self._keypoints)

    def get(self, index):
        return [self._keypoints[index], self._descriptors[index], self._info[index]]

    def get_keypoint(self, index):
        return self._keypoints[index]

    def get_descriptor(self, index):
        return self._descriptors[index]

    def get_info(self, index):
        return self._info[index]

    def keypoints(self):
        return self._keypoints

    def descriptors(self):
        return self._descriptors

    def info(self):
        return self._info

    def printSet(self):
        print self
        print "Keypoints: \tDescriptors: \tInfo:"
        for index in range(0, len(self._keypoints), 1):
            line = str(self._keypoints[index])
            if index < len(self._descriptors):
                line += "\t" + str(self._descriptors[index])
            if index < len(self._info):
                line += "\t" + str(self._info[index])
            print line


class IntersectMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = []
        self._max_set = []
        self._base_pair = []
        self._db = []
        self._item_index = 0

    def update_hash(self, data):
        # del data['data']
        # del data['roi']
        # del data['keypoints']
        # del data['descriptors']
        self._hash.append(data)

    def update_database(self):
        if len(self._hash) > 1:
            self.update_base()
            for item in self._hash:
                self.add_to_db(item)
            # for tube_set in self._db:
            #     tube_set.printSet()
            # showMatches(self._base_pair[0], self._base_pair[1], self._max_set, 'roi')

    def update_base(self):
        self._db = []
        matcher = FlannMatcher()
        for item1 in self._hash:
            for item2 in self._hash:
                if item1['path'] != item2['path']:
                    matches = matcher.knnMatch(item1['descriptors'], item2['descriptors'], k=1)
                    opt_matches = []
                    mean = meanDistance(matches)
                    for match in matches:
                        for m in match:
                            dx = (int(item1['keypoints'][m.queryIdx].pt[0]) -
                                  int(item2['keypoints'][m.trainIdx].pt[0]))
                            dy = (int(item1['keypoints'][m.queryIdx].pt[1]) -
                                  int(item2['keypoints'][m.trainIdx].pt[1]))
                            if abs(dx) + abs(dy) < 10 and abs(dy) < 4 and m.distance < mean:
                                # if pow(pow(dx, 2) + pow(dy, 2), 0.5) < 40:
                                # if m.distance < mean * 0.5:
                                opt_matches.append([m])
                    if len(self._max_set) < len(opt_matches):
                        self._max_set = opt_matches
                        self._base_pair = (item1, item2)
            first_item = []
            second_item = []
            for match in self._max_set:
                for m in match:
                    first_item.append(m.queryIdx)
                    second_item.append(m.trainIdx)
                    tube = TubeSet()
                    tube.add(self._base_pair[0]['keypoints'][m.queryIdx],
                             self._base_pair[0]['descriptors'][m.queryIdx], "1")
                    tube.add(self._base_pair[1]['keypoints'][m.trainIdx],
                             self._base_pair[1]['descriptors'][m.trainIdx], "2")
                    tube.set_basic_distance(m.distance)
                    self._db.append(tube)
            for index in range(0, len(self._base_pair[0]['keypoints']), 1):
                if not first_item.__contains__(index):
                    tube = TubeSet()
                    tube.add(self._base_pair[0]['keypoints'][index],
                             self._base_pair[0]['descriptors'][index], "1")
                    self._db.append(tube)
            for index in range(0, len(self._base_pair[1]['keypoints']), 1):
                if not second_item.__contains__(index):
                    tube = TubeSet()
                    tube.add(self._base_pair[1]['keypoints'][index],
                             self._base_pair[1]['descriptors'][index], "2")
                    self._db.append(tube)
        self._item_index = 2

    def add_to_db(self, item):
        if (item['path'] != self._base_pair[0]['path']
            and item['path'] != self._base_pair[1]['path']):
            matcher = FlannMatcher()
            self._item_index += 1
            for tube_set in self._db:
                matches = matcher.knnMatch(listToNumpy_ndarray(tube_set.descriptors()),
                                           listToNumpy_ndarray(item['descriptors']), k=1)
                local_set = dict()
                match_set = dict()
                for match in matches:
                    for m in match:
                        value = local_set.get(m.trainIdx, 0)
                        value += 1
                        local_set[m.trainIdx] = value
                        mset = match_set.get(m.trainIdx, [])
                        mset.append(m)
                        match_set[m.trainIdx] = mset
                max_value = 0
                max_keys = []
                for k, v in local_set.iteritems():
                    if max_value < v:
                        max_keys = []
                        max_value = v
                        max_keys.append(k)
                    elif max_value == v:
                        max_keys.append(k)
                best = -1
                max_dis = 0
                m_dis = []
                best_dist = sys.maxint
                for key in max_keys:
                    m_max = match_set[key]
                    m_dis.append(m_max)
                    dist = 0
                    dis = 0
                    for m in m_max:
                        dist += m.distance
                        if dis < m.distance:
                            dis = m.distance
                    if best_dist > dist:
                        best_dist = dist
                        best = key
                        max_dis = dis
                d_dist = 0.8 * meanDistance(m_dis)
                if tube_set.basic_distance() >= 0:
                    if tube_set.basic_distance() < d_dist:
                        if max_dis <= tube_set.basic_distance() + d_dist:
                            tube_set.add(item['keypoints'][best], item['descriptors'][best], str(self._item_index))
                    else:
                        if max_dis <= tube_set.basic_distance():
                            tube_set.add(item['keypoints'][best], item['descriptors'][best], str(self._item_index))
                else:
                    dx = (int(tube_set.get_keypoint(0).pt[0]) - int(item['keypoints'][best].pt[0]))
                    dy = (int(tube_set.get_keypoint(0).pt[1]) - int(item['keypoints'][best].pt[1]))
                    size = tube_set.get_keypoint(0).size
                    if size > item['keypoints'][best].size:
                        size = item['keypoints'][best].size
                    if pow(pow(dx, 2) + pow(dy, 2), 0.5) < size / 2.0 and abs(dy) < pow(size / 2.0, 0.5):
                        tube_set.add(item['keypoints'][best], item['descriptors'][best], str(self._item_index))
                        matches = matcher.knnMatch(listToNumpy_ndarray([item['descriptors'][best]]),
                                                   listToNumpy_ndarray(tube_set.descriptors()), k=1)
                        tube_set.set_basic_distance(matches[0][0].distance)

    @verifying
    def verify(self, data):
        matcher = FlannMatcher()
        ni = []
        ci = []
        Nmax = 0
        for tube_set in self._db:
            if tube_set.count() > 1:
                ni.append(tube_set.count())
                Nmax += tube_set.count()
                self._item_index += 1
                matches = matcher.knnMatch(listToNumpy_ndarray(tube_set.descriptors()),
                                           listToNumpy_ndarray(data['descriptors']), k=1)
                local_set = dict()
                match_set = dict()
                key_set = dict()
                for match in matches:
                    for m in match:
                        value = local_set.get(m.trainIdx, 0)
                        value += 1
                        local_set[m.trainIdx] = value
                        mset = match_set.get(m.trainIdx, [])
                        mset.append(m)
                        match_set[m.trainIdx] = mset
                        kset = key_set.get(m.trainIdx, [])
                        kset.append(data['keypoints'][m.trainIdx])
                        key_set[m.trainIdx] = kset
                max_value = 0
                max_keys = []
                for k, v in local_set.iteritems():
                    if max_value < v:
                        max_keys = []
                        max_value = v
                        max_keys.append(k)
                    elif max_value == v:
                        max_keys.append(k)
                best = -1
                max_dis = 0
                m_dis = []
                best_dist = sys.maxint
                for key in max_keys:
                    m_max = match_set[key]
                    m_dis.append(m_max)
                    dist = 0
                    dis = 0
                    for m in m_max:
                        dist += m.distance
                        if dis < m.distance:
                            dis = m.distance
                    if best_dist > dist:
                        best_dist = dist
                        best = key
                        max_dis = dis
                d_dist = 0.5 * meanDistance(m_dis)
                if tube_set.basic_distance() >= 0:
                    if tube_set.basic_distance() < d_dist:
                        if max_dis <= tube_set.basic_distance() + d_dist:
                            ci.append(True)
                        else:
                            ci.append(False)
                    else:
                        if max_dis <= tube_set.basic_distance():
                            ci.append(True)
                        else:
                            ci.append(False)
                else:
                    dx = (int(tube_set.get_keypoint(0).pt[0]) - int(data['keypoints'][best].pt[0]))
                    dy = (int(tube_set.get_keypoint(0).pt[1]) - int(data['keypoints'][best].pt[1]))
                    size = tube_set.get_keypoint(0).size
                    if size > data['keypoints'][best].size:
                        size = data['keypoints'][best].size
                    if pow(pow(dx, 2) + pow(dy, 2), 0.5) < size / 2.0 and abs(dy) < pow(size / 2.0, 0.5):
                        ci.append(True)
                    else:
                        ci.append(False)
        prob = 0
        for index in range(0, len(ci), 1):
            if ci[index]:
                prob += ni[index]
        prob /= 1.0 * Nmax
        print "Max count " + str(Nmax)
        print "Length of set " + str(len(ni))
        print "Probability: " + str(prob) + " %"
        return prob * 100.0