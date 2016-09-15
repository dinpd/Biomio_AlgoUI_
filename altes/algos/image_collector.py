from server.biomio.algorithms.flows.base import IAlgorithm


class ImageCollector(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if type(data) == list:
            test_data = None
            train_data = []
            for data_item in data:
                if len(data_item) == 1 and data_item[0]['img'].attribute('type') == 'test':
                    test_data = data_item[0]['img']
                else:
                    data_list = [item['img'] for item in data_item]
                    train_data.append(data_list)
            return {'test': test_data, 'train': train_data}
        return None
