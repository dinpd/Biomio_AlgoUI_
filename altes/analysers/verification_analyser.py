from server.biomio.algorithms.flows.base import IAlgorithm
from decorators import analyze_result


class VerificationAnalyser(IAlgorithm):
    def __init__(self):
        pass

    @analyze_result
    def apply(self, data):
        if data is None:
            return data
        steps = 400
        precision = 100.0
        count = 0
        res_table = {}
        for inx in range(0, steps, 1):
            res_table[inx] = 0
        for d_list in data['result']:
            for e_res in d_list:
                res = e_res['result']
                for inx in range(0, steps, 1):
                    if res < (inx + 1) / precision:
                        count += 1
                        value = res_table[inx]
                        value += 1
                        res_table[inx] = value
                        break
        data.update({'res_table': res_table, 'res_options': {'steps': steps, 'precision': precision, 'count': count}})
        return data
