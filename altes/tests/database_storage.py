from corealgorithms.flows import IAlgorithm
import cPickle


class DatabaseStorage(IAlgorithm):
    def __init__(self, store=True):
        self._store = store

    def apply(self, data):
        if data is not None:
            if data.get('store_path', None) is not None and self._store:
                raw_data = cPickle.dumps(data['data'], cPickle.HIGHEST_PROTOCOL)
                with open(data['store_path'], 'w') as f:
                    f.write(raw_data)
                f.close()
                data['load_path'] = data['store_path']
            elif data.get('load_path', None) is not None and not self._store:
                with open(data['load_path'], 'r') as f:
                    raw_data = f.read()
                f.close()
                data['data'] = cPickle.loads(raw_data)
        return data
