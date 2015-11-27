"""
Based on opencv2/flann/defines.h
Description of parameters of Flann-based descriptor matcher.
"""

# Nearest neighbour index algorithms
###################################################################
# enum flann_algorithm
###################################################################
FLANN_INDEX_LINEAR = 0
FLANN_INDEX_KDTREE = 1
FLANN_INDEX_KMEANS = 2
FLANN_INDEX_COMPOSITE = 3
FLANN_INDEX_KDTREE_SINGLE = 4
FLANN_INDEX_HIERARCHICAL = 5
FLANN_INDEX_LSH = 6
FLANN_INDEX_SAVED = 254
FLANN_INDEX_AUTOTUNED = 255
# deprecated constants, should use the FLANN_INDEX_* ones instead
LINEAR = 0
KDTREE = 1
KMEANS = 2
COMPOSITE = 3
KDTREE_SINGLE = 4
SAVED = 254
AUTOTUNED = 255
###################################################################

###################################################################
# enum flann_centers_init
###################################################################
FLANN_CENTERS_RANDOM = 0
FLANN_CENTERS_GONZALES = 1
FLANN_CENTERS_KMEANSPP = 2
# deprecated constants, should use the FLANN_CENTERS_* ones instead
CENTERS_RANDOM = 0
CENTERS_GONZALES = 1
CENTERS_KMEANSPP = 2
###################################################################

###################################################################
# enum flann_log_level
###################################################################
FLANN_LOG_NONE = 0
FLANN_LOG_FATAL = 1
FLANN_LOG_ERROR = 2
FLANN_LOG_WARN = 3
FLANN_LOG_INFO = 4
###################################################################

###################################################################
# enum flann_distance
###################################################################
FLANN_DIST_EUCLIDEAN = 1
FLANN_DIST_L2 = 1
FLANN_DIST_MANHATTAN = 2
FLANN_DIST_L1 = 2
FLANN_DIST_MINKOWSKI = 3
FLANN_DIST_MAX   = 4
FLANN_DIST_HIST_INTERSECT   = 5
FLANN_DIST_HELLINGER = 6
FLANN_DIST_CHI_SQUARE = 7
FLANN_DIST_CS = 7
FLANN_DIST_KULLBACK_LEIBLER = 8
FLANN_DIST_KL = 8
# deprecated constants, should use the FLANN_DIST_* ones instead
EUCLIDEAN = 1
MANHATTAN = 2
MINKOWSKI = 3
MAX_DIST = 4
HIST_INTERSECT = 5
HELLINGER = 6
CS = 7
KL = 8
KULLBACK_LEIBLER = 8
###################################################################

###################################################################
# enum flann_datatype
###################################################################
FLANN_INT8 = 0
FLANN_INT16 = 1
FLANN_INT32 = 2
FLANN_INT64 = 3
FLANN_UINT8 = 4
FLANN_UINT16 = 5
FLANN_UINT32 = 6
FLANN_UINT64 = 7
FLANN_FLOAT32 = 8
FLANN_FLOAT64 = 9
###################################################################

###################################################################
# enum flann_checks
###################################################################
FLANN_CHECKS_UNLIMITED = -1
FLANN_CHECKS_AUTOTUNED = -2
###################################################################
