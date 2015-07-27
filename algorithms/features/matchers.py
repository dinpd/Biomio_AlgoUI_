import defines
import cv2

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
    index_params = defaultFlannBasedLSHIndexParams()
    # index_params = defaultFlannBasedIndexKDTreeParams()
    search_params = dict(checks=100)
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    return matcher


def BruteForceMatcher():
    matcher = cv2.BFMatcher(normType=cv2.NORM_HAMMING, crossCheck=False)
    return matcher


def defaultFlannBasedLSHIndexParams():
    return dict(algorithm=defines.FLANN_INDEX_LSH,
                table_number=12,       # 12
                key_size=20,          # 20
                multi_probe_level=2)  # 2


def defaultFlannBasedIndexKDTreeParams():
    return dict(algorithm=defines.FLANN_INDEX_KDTREE,
                trees=5)

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