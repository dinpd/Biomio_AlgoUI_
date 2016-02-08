from nearpyhash import NearPyHash
from wnearpyhash import wNearPyHash, DEFAULT_NEAR_PY_HASH_SETTINGS

__structures_list = {
    NearPyHash.type(): NearPyHash,
    wNearPyHash.type(): wNearPyHash
}

def get_data_structure(structure_type):
    return __structures_list.get(structure_type, None)
