from nearpy.engine import Engine, np
from xmemorystorage import xMemoryStorage
from emptyfilter import EmptyFilter

class xEngine(Engine):
    def __init__(self, dim, lshashes=None,
                 distance=None,
                 fetch_vector_filters=None,
                 vector_filters=None,
                 storage=None):
        Engine.__init__(self, dim, lshashes, distance, [EmptyFilter()],
                        vector_filters, xMemoryStorage())

    def store_vector(self, v, data=None):
        """
        Hashes vector v and stores it in all matching buckets in the storage.
        The data argument must be JSON-serializable. It is stored with the
        vector and will be returned in search results.
        """
        # We will store the normalized vector (used during retrieval)
        nv = v / np.linalg.norm(v)
        # Store vector in each bucket of all hashes
        bucket_keys = []
        for lshash in self.lshashes:
            for bucket_key in lshash.hash_vector(v):
                bucket_keys.append(bucket_key)
                self.storage.store_vector(lshash.hash_name, bucket_key,
                                          nv, data)
        return bucket_keys

    def clean_vectors_by_data(self, hash_name, data, bucket_keys=[]):
        self.storage.clean_vectors_by_data(hash_name, data, bucket_keys)

    def clean_all_vectors(self, hash_name, data):
        self.storage.clean_all_vectors(hash_name, data)

    def dump(self):
        self.storage.dump()
