from server.biomio.algorithms.flows.base import IAlgorithm
from defs import SEPARATOR_LINE


class DistanceTableOutput(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        print(SEPARATOR_LINE)
        print("Distance Table Visualization")
        print("Database:")
        for data_item in data['result']:
            print(data_item['database']['img'].path())
        print('Test:')
        print(data['result'][0]['data']['img'].path())
        print("Table:")
        table_dict = data.get('table', {})
        print("Distance:\tData")
        keys = data.get('table_keys', None)
        if keys is None:
            for key, items in table_dict.iteritems():
                paths_string = ""
                for item in items:
                    paths_string += item['database']['img'].path() + " "
                print("{}:\t{}".format(key, paths_string))
        else:
            for key in keys:
                items = table_dict[key]
                paths_string = ""
                for item in items:
                    paths_string += item['database']['img'].path() + " "
                print("{}:\t{}".format(key, paths_string))
        print(SEPARATOR_LINE)
        return data
