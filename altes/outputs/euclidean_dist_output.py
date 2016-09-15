from server.biomio.algorithms.flows.base import IAlgorithm
from defs import SEPARATOR_LINE


class EuclideanDistanceOutput(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        print(SEPARATOR_LINE)
        print("Euclidean Distance Estimation")
        print("Database:")
        for data_item in data['result']:
            print(data_item['database']['img'].path())
        print('Test:')
        print(data['result'][0]['data']['img'].path())
        print("Estimation:")
        print("Minimal Distance: {} for {}".format(data['min']['value'],
                                                   data['min']['data']['database']['img'].path()))
        print("Maximal Distance: {} for {}".format(data['max']['value'],
                                                   data['max']['data']['database']['img'].path()))
        print("Average Distance: {}".format(data['avg']['value']))
        print(SEPARATOR_LINE)
        return data
