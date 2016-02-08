from xnearpy import get_projection_by_type, get_type_by_projection, RANDOM_BINARY_PROJECTIONS
from nearpy.filters import NearestFilter, UniqueFilter
from nearpy.distances import CosineDistance
from biomio.algorithms.cvtools.types import numpy_ndarrayToList
import numpy as np

DEFAULT_NEAR_PY_HASH_SETTINGS = {
    'projections': [(RANDOM_BINARY_PROJECTIONS, {})],
    'projection_name': "rbp",
    'projection_count': 10,
    'dimension': 32
}

class wNearPyHash:
    def __init__(self, settings=DEFAULT_NEAR_PY_HASH_SETTINGS, distance=None, vector_filters=None,
                 fetch_vector_filters=None, storage=None):
        self._settings = settings
        self._storage = storage
        self.lshashes = []
        """ Keeps the configuration. """
        if distance is None:
            distance = CosineDistance()
        self.distance = distance
        if vector_filters is None:
            vector_filters = [NearestFilter(10)]
        self.vector_filters = vector_filters
        if fetch_vector_filters is None:
            fetch_vector_filters = [UniqueFilter()]
        self.fetch_vector_filters = fetch_vector_filters
        for projection in settings.get('projections', []):
            proj = get_projection_by_type(projection[0])(settings['projection_name'], settings['projection_count'])
            proj.reset(settings['dimension'])
            if len(projection[1].keys()) > 0:
                proj.apply_config(projection[1])
            self.lshashes.append(proj)

    @staticmethod
    def type():
        return "wNearPyHash"

    def hash_list(self):
        hashes = [lshash.hash_name for lshash in self.lshashes]
        return hashes


    def hash_vectors(self, vs, data=None):
        """
        [
            [
                (bucket_key, normalized_vector),
                ...
            ]
        ]
        :param vs:
        :param data:
        :return:
        """
        nvs = [v / np.linalg.norm(v) for v in vs]
        # Store vector in each bucket of all hashes
        buckets = []
        for lshash in self.lshashes:
            data_vs = []
            for nv in nvs:
                for bucket_key in lshash.hash_vector(nv):
                    data_vs.append((bucket_key, nv))
            buckets.append((lshash.hash_name, data_vs))
        return buckets

    def hash_vector(self, v):
        nv = v / np.linalg.norm(v)

        buckets = []
        for lshash in self.lshashes:
            for bucket_key in lshash.hash_vector(nv):
                buckets.append((lshash.hash_name, bucket_key))
        return buckets

    def neighbours(self, v):
        """
        Hashes vector v, collects all candidate vectors from the matching
        buckets in storage, applys the (optional) distance function and
        finally the (optional) filter function to construct the returned list
        of either (vector, data, distance) tuples or (vector, data) tuples.
        """

        # Collect candidates from all buckets from all hashes
        candidates = []
        if self._storage is None:
            return candidates

        # nv = v / np.linalg.norm(v)

        for lshash in self.lshashes:
            for bucket_key in lshash.hash_vector(v, querying=True):
                bucket_content = self._storage.get_bucket(lshash.hash_name, bucket_key)
                # print 'Bucket %s size %d' % (bucket_key, len(bucket_content))
                candidates.extend(bucket_content)

        # print 'Candidate count is %d' % len(candidates)

        # Apply fetch vector filters if specified and return filtered list
        if self.fetch_vector_filters:
            filter_input = candidates
            for fetch_vector_filter in self.fetch_vector_filters:
                filter_input = fetch_vector_filter.filter_vectors(filter_input)
            # Update candidates
            candidates = filter_input

        # Apply distance implementation if specified
        if self.distance:
            # Normalize vector (stored vectors are normalized)
            nv = v / np.linalg.norm(v)
            candidates = [(x[0], x[1], self.distance.distance(x[0], nv)) for x
                          in candidates]

        # Apply vector filters if specified and return filtered list
        if self.vector_filters:
            filter_input = candidates
            for vector_filter in self.vector_filters:
                filter_input = vector_filter.filter_vectors(filter_input)
            # Return output of last filter
            return filter_input

        # If there is no vector filter, just return list of candidates
        return candidates

    def get_config(self):
        projections = []
        for lshash in self.lshashes:
            config = lshash.get_config()
            config['normals'] = numpy_ndarrayToList(config['normals'])
            projections.append((get_type_by_projection(lshash), config))
        settings = {
            'projections': projections,
            'projection_name': self._settings['projection_name'],
            'projection_count': self._settings['projection_count'],
            'dimension': self._settings['dimension']
        }
        return settings
