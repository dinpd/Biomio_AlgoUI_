from nearpy.storage import MemoryStorage


class xMemoryStorage(MemoryStorage):
    def __init__(self):
        MemoryStorage.__init__(self)

    def clean_vectors_by_data(self, hash_name, data, bucket_keys=[]):
        bucket_hash = self.buckets.get(hash_name, {})
        new_bucket_hash = {}
        for key in bucket_keys:
            item = bucket_hash.get(key, None)
            if item is not None:
                new_items = []
                for item in items:
                    if item[1] != data:
                        new_items.append(item)
                new_bucket_hash[key] = new_items
        self.buckets[hash_name] = new_bucket_hash

    def clean_all_vectors(self, hash_name, data):
        bucket_hash = self.buckets.get(hash_name, {})
        new_bucket_hash = {}
        for key, items in bucket_hash.iteritems():
            new_items = []
            for item in items:
                if item[1] != data:
                    new_items.append(item)
            new_bucket_hash[key] = new_items
        self.buckets[hash_name] = new_bucket_hash

    def dump(self):
        for hash_name, hash_content in self.buckets.iteritems():
            print hash_name
            for bucket_key, items in hash_content.iteritems():
                print bucket_key
                print len(items)
