from corealgorithms.flows import AlgorithmFlow
import os


DATA_SEPARATOR_PROCESSING = "data_separator::processing"


class DataSeparator(AlgorithmFlow):
    def __init__(self, size=None):
        AlgorithmFlow.__init__(self)
        self._size = size

    def setProcessingStage(self, stage):
        self.addStage(DATA_SEPARATOR_PROCESSING, stage)

    def processingStage(self):
        return self._stages.get(DATA_SEPARATOR_PROCESSING, None)

    def apply(self, data):
        if data is not None:
            if self._size is None:
                return self.processingStage().apply(data)
            else:
                inx = 0
                collect_data = {}
                data_subsets = []
                subset = {}
                index = 0
                for p_key, p_data in data['data'].iteritems():
                    subset[p_key] = p_data
                    index += 1
                    if index >= self._size:
                        index = 0
                        data_subsets.append(subset)
                        subset = {}
                if len(subset.keys()) > 0:
                    data_subsets.append(subset)
                for data_subset in data_subsets:
                    store_path = data.get('store_path')
                    new_store_path = store_path
                    if store_path is not None:
                        new_store_path, file_name = os.path.split(store_path)
                        file_names = file_name.split('.')
                        file_names[0] = "{}_{}".format(file_names[0], inx)
                        new_store_path = os.path.join(new_store_path, '.'.join(file_names))
                    data_copy = data.copy()
                    data_copy.update({'data': data_subset, 'store_path': new_store_path})
                    res_data = self.processingStage().apply(data_copy)
                    collect_data.update(res_data.get('data'))
                    inx += 1
                gen_data = data.copy()
                gen_data.update({'data': collect_data})
                return gen_data
        return data
