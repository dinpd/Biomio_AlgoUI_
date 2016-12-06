from corealgorithms.flows import IAlgorithm
from defs import SEPARATOR_LINE


class OpenFaceDistanceOutput(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        print(SEPARATOR_LINE)
        print("OpenFace Euclidean Distance Estimation")
        print("Database:")
        for data_item in data['database']['data']:
            print(data_item['img'].path())
        print('Test:')
        print(data['data']['img'].path())
        print("Estimation:")
        print("Average Distance: {}".format(data['result']))
        print(SEPARATOR_LINE)
        return data
