from nearpy.hashes import RandomBinaryProjections, PCABinaryProjections, \
    RandomDiscretizedProjections, PCADiscretizedProjections

RANDOM_BINARY_PROJECTIONS = 'RandomBinaryProjections'
RANDOM_DISCRETIZED_PROJECTIONS = 'RandomDiscretizedProjections'
PCA_BINARY_PROJECTIONS = 'PCABinaryProjections'
PCA_DISCRETIZED_PROJECTIONS = 'PCADiscretizedProjections'

_PROJ_DICT = {
    RANDOM_BINARY_PROJECTIONS: RandomBinaryProjections,
    RANDOM_DISCRETIZED_PROJECTIONS: RandomDiscretizedProjections,
    PCA_BINARY_PROJECTIONS: PCABinaryProjections,
    PCA_DISCRETIZED_PROJECTIONS: PCADiscretizedProjections
}

_TYPES_DICT = {
    RandomBinaryProjections("rbc", 10).__class__: RANDOM_BINARY_PROJECTIONS,
    RandomDiscretizedProjections("rbc", 10, 2).__class__: RANDOM_DISCRETIZED_PROJECTIONS,
    PCABinaryProjections("rbc", 10, None).__class__: PCA_BINARY_PROJECTIONS,
    PCADiscretizedProjections("rbc", 10, None, 2).__class__: PCA_DISCRETIZED_PROJECTIONS
}


def get_projection_by_type(proj_type):
    return _PROJ_DICT.get(proj_type, None)

def get_type_by_projection(projection):
    return _TYPES_DICT.get(projection.__class__)

