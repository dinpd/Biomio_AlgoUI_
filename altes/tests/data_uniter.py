from corealgorithms.flows import AlgorithmFlow
import os


DATA_UNITER_PROCESSING = "data_separator::processing"


class DataUniter(AlgorithmFlow):
    def __init__(self):
        AlgorithmFlow.__init__(self)

    def setProcessingStage(self, stage):
        self.addStage(DATA_UNITER_PROCESSING, stage)

    def processingStage(self):
        return self._stages.get(DATA_UNITER_PROCESSING, None)

    def apply(self, data):
        if data is not None:
            collect_data = {}
            inx = 0
            load_path = data.get('load_path')
            while True:
                new_load_path = load_path
                if load_path is not None:
                    new_load_path, file_name = os.path.split(load_path)
                    file_names = file_name.split('.')
                    file_names[0] = "{}_{}".format(file_names[0], inx)
                    new_load_path = os.path.join(new_load_path, '.'.join(file_names))
                if not os.path.exists(new_load_path):
                    break
                data_copy = data.copy()
                data_copy.update({'load_path': new_load_path})
                res_data = self.processingStage().apply(data_copy)
                collect_data.update(res_data.get('data'))
                inx += 1
            gen_data = data.copy()
            gen_data.update({'data': collect_data})
            return gen_data
        return data
