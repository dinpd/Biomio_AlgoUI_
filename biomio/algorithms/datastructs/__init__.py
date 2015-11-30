from nearpyhash import NearPyHash

__structures_list = {
    NearPyHash.type(): NearPyHash
}

def get_data_structure(structure_type):
    return __structures_list.get(structure_type, None)
