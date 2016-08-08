from xmemorystorage import xMemoryStorage
from tools import hamming_distance


class HammingMemoryStorage(xMemoryStorage):
    def __init__(self, max_distance=None):
        xMemoryStorage.__init__(self)
        self._hamming_max = max_distance

    def get_bucket(self, hash_name, bucket_key):
        """
        Returns bucket content as list of tuples (vector, data).
        """
        print bucket_key
        if hash_name in self.buckets:
            buckets = []
            # selected_keys = [k for k in self.buckets[hash_name].keys()
            #                  if hamming_distance(bucket_key, k) < self._hamming_max]
            selected_keys = []
            if self._hamming_max is None:
                selected_keys.append(bucket_key)
            else:
                for k in self.buckets[hash_name].keys():
                    if hamming_distance(bucket_key, k) < self._hamming_max:
                        print bucket_key, k, self._hamming_max, hamming_distance(bucket_key, k)
                        selected_keys.append(k)
            print len(selected_keys)
            for key in selected_keys:
                values = self.buckets[hash_name].get(key, [])
                for v in values:
                    buckets.append(v)
            return buckets
        return []
