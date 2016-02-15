from biomio.algorithms.cvtools.types import listToNumpy_ndarray
from biomio.algorithms.clustering.tools import distance
from biomio.algorithms.logger import logger
import itertools
import defines
import numpy
import cv2
import sys

BruteForceMatcherType = 0
FlannBasedMatcherType = 1


def MatcherCreator(descriptorMatcherType):
    """
    Function that create <DescriptorMatcher object> by the selected type.

    :param descriptorMatcherType: enum
        'BruteForce'            - Brute-force matcher (it uses L2)

        'BruteForce-L1'         - Brute-force matcher (it uses L1)
         L1 and L2 norms are preferable choices for SIFT and SURF descriptors.

        'BruteForce-Hamming'    - BruteForce-Hamming matcher should be used
        with ORB, BRISK and BRIEF.

        'BruteForce-Hamming(2)' - BruteForce-Hamming Second matcher should be
        used with ORB when WTA_K==3 or 4 (see ORB::ORB constructor
        description).

        'FlannBased'            - Flann-based matcher

        **********************************************************************
         Brute-force descriptor matcher. For each descriptor in the first set,
        this matcher finds the closest descriptor in the second set by trying
        each one. This descriptor matcher supports masking permissible matches
        of descriptor sets.
        **********************************************************************
         Flann-based descriptor matcher. This matcher trains flann::Index_ on
        a train descriptor collection and calls its nearest search methods to
        find the best matches. So, this matcher may be faster when matching a
        large train collection than the brute force matcher. FlannBasedMatcher
        does not support masking permissible matches of descriptor sets
        because flann::Index does not support this.
        **********************************************************************
    """
    return cv2.DescriptorMatcher_create(descriptorMatcherType)


def FlannMatcher():
    # index_params = defaultFlannBasedLSHIndexParams()
    index_params = defaultFlannBasedKDTreeIndexParams()
    search_params = dict(checks=100)
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    return matcher


def BruteForceMatcher():
    matcher = cv2.BFMatcher(normType=cv2.NORM_HAMMING, crossCheck=False)
    return matcher


def defaultFlannBasedLSHIndexParams():
    """
        Returns default Flann-based LSH Index parameters dict object.
    :return: dict object instance.
    """
    return dict(algorithm=defines.FLANN_INDEX_LSH,
                table_number=12,
                key_size=20,
                multi_probe_level=2)


def defaultFlannBasedKDTreeIndexParams():
    """
        Returns default Flann-based KD-Tree Index parameters dict object.
    :return: dict object instance.
    """
    return dict(algorithm=defines.FLANN_INDEX_KDTREE, trees=5)


def Matcher(type=BruteForceMatcherType):
    if type == BruteForceMatcherType:
        return BruteForceMatcher()
    else:
        return FlannMatcher()


def LowesMatchingScheme(match1, match2, threshold=0.5):
    if (match1 is not None) and (match2 is not None):
        return match1.distance < threshold * match2.distance
    else:
        return False

CROSS_MATCHING_MATCHES = 'cm_matches'
CROSS_MATCHING_DESCRIPTORS = 'cm_descriptors'

def CrossMatching(descriptors1, descriptors2, matcher, knn, result_type=CROSS_MATCHING_MATCHES):
    if len(descriptors1) < knn or len(descriptors2) < knn:
        return []
    matches1 = matcher.knnMatch(descriptors1, descriptors2, k=knn)
    matches2 = matcher.knnMatch(descriptors2, descriptors1, k=knn)
    ml = []
    if result_type == CROSS_MATCHING_MATCHES:
        ml = [
            x for (x, _) in itertools.ifilter(
                lambda (m, n): m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx, itertools.product(
                    itertools.chain(*matches1), itertools.chain(*matches2)
                )
            )
        ]
    elif result_type == CROSS_MATCHING_DESCRIPTORS:
        ml = list(itertools.chain.from_iterable(itertools.imap(
            lambda(x, _): (descriptors1[x.queryIdx], descriptors2[x.trainIdx]), itertools.ifilter(
                lambda(m, n): m.queryIdx == n.trainIdx and m.trainIdx == n.queryIdx, itertools.product(
                    itertools.chain(*matches1), itertools.chain(*matches2)
                )
            )
        )))
    return ml


def SelfMatching(descriptors, matcher, dtype, knn):
    self_match = []
    for desc in descriptors:
        query_set = [desc]
        train_set = [d for d in descriptors if not numpy.array_equal(desc, d)]
        s_match = matcher.knnMatch(listToNumpy_ndarray(query_set, dtype),
                                   listToNumpy_ndarray(train_set, dtype), k=knn)
        for m in itertools.chain(*s_match):
            self_match.append([query_set[m.queryIdx], train_set[m.trainIdx], m.distance])
    return self_match


def SelfGraph(keypoints, knn, descriptors=None):
    edges = []
    for ik, keypoint1 in enumerate(keypoints):
        pairs = []
        for idx in range(0, knn, 1):
            pairs.append((None, None, sys.maxint))
        for jk, keypoint2 in enumerate(keypoints):
            if keypoint1.pt != keypoint2.pt:
                dist = distance(keypoint1.pt, keypoint2.pt)
                for idx in range(0, knn, 1):
                    if pairs[idx][2] > dist:
                        for i in range(knn - 1, idx, -1):
                            pairs[i] = (pairs[i - 1][0], pairs[i - 1][1], pairs[i - 1][2])
                        if descriptors is None:
                            pairs[idx] = (keypoint2, None, dist)
                        else:
                            pairs[idx] = (keypoint2, descriptors[jk], dist)
                        break
        for idx in range(0, knn, 1):
            if pairs[idx][0] is not None:
                desc = None
                if descriptors is not None:
                    desc = descriptors[ik]
                edges.append([keypoint1, desc, pairs[idx][0], pairs[idx][1], pairs[idx][2]])
    return edges


def SubsetsCalculation(matches):
    sorted_matches = sorted(matches, key=lambda match: match.distance)
    exclude_f = []
    exclude_s = []
    subset = []
    for match in sorted_matches:
        if (not exclude_f.__contains__(match.queryIdx)) and (not exclude_s.__contains__(match.trainIdx)):
            subset.append(match)
            exclude_f.append(match.queryIdx)
            exclude_s.append(match.trainIdx)
    return subset
