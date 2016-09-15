from server.biomio.algorithms.flows.base import IAlgorithm
from decorators import analyze_result
from operator import add
import scipy.spatial.distance as distance


class EuclideanDistanceAnalyser(IAlgorithm):
    def __init__(self):
        pass

    @analyze_result
    def apply(self, data):
        if data is None:
            return data
        min_res = None
        min_dist = 1000
        max_res = None
        max_dist = 0
        avg_dist = 0
        sum_rep = [0 for _ in range(0, 128, 1)]
        for res_dict in data['result']:
            avg_dist += res_dict['result']
            sum_rep = map(add, sum_rep, res_dict['database']['rep'])
            if res_dict['result'] < min_dist:
                min_dist = res_dict['result']
                min_res = res_dict
            if res_dict['result'] > max_dist:
                max_dist = res_dict['result']
                max_res = res_dict
        sum_rep = [item / (1.0 * len(data['result'])) for item in sum_rep]
        mc_dist = distance.euclidean(sum_rep, data['result'][0]['data']['rep'])
        print(mc_dist)
        print("---------------------------------")
        test_rep = data['result'][0]['data']['rep']
        for res_dict in data['result']:
            dist = distance.euclidean(sum_rep, res_dict['database']['rep'])
            conv = 0
            for inx in range(0, 128, 1):
                if (test_rep[inx] > 0 and res_dict['database']['rep'][inx] > 0) \
                        or (test_rep[inx] < 0 and res_dict['database']['rep'][inx] < 0):
                    conv += 1
            print (dist, res_dict['result']), conv
        avg_dist /= (1.0 * len(data['result']))
        data.update({
            'min': {'value': min_dist, 'data': min_res},
            'max': {'value': max_dist, 'data': max_res},
            'avg': {'value': avg_dist},
            'mass_center': {'rep': sum_rep}
        })
        return data
