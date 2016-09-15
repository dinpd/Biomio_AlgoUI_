from server.biomio.algorithms.flows.base import IAlgorithm


class GeneralEstimationPreparing(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return data
        return [{'test': data['test'], 'train': train_data} for train_data in data['train']]


class EstimationPreparing(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return data
        test_obj = data['test']
        results = []
        for train_data in data['train']:
            data_set = {
                'database': {'rep': train_data.attribute('rep'), 'img': train_data},
                'data': {'rep': test_obj.attribute('rep'), 'img': test_obj}
            }
            results.append(data_set)
        return results
