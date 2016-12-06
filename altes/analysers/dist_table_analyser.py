from corealgorithms.flows import IAlgorithm
from decorators import analyze_result


class DistanceTableAnalyser(IAlgorithm):
    def __init__(self):
        pass

    @analyze_result
    def apply(self, data):
        if data is None:
            return data
        res_table = {}
        for res_dict in data['result']:
            row = res_table.get(res_dict['result'], [])
            row.append(res_dict)
            res_table[res_dict['result']] = row
        table_keys = res_table.keys()
        table_keys.sort()
        data.update({'table': res_table, 'table_keys': table_keys})
        return data
