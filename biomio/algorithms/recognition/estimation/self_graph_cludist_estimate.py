from biomio.algorithms.clustering.tools import distance
from self_graph_estimate import SelfGraphEstimation
from biomio.algorithms.logger import logger


class SelfGraphDistanceEstimation(SelfGraphEstimation):
    def __init__(self, detector_type, knn):
        SelfGraphEstimation.__init__(self, detector_type, knn)

    def estimate_training(self, data, database):
        template = SelfGraphEstimation.estimate_training(self, data, database)
        if len(database) == 0:
            template.update(data)
        else:
            centers = []
            for index, c in enumerate(database['centers']):
                dc = data['centers'][index]
                centers.append(((c[0] + dc[0]) / 2.0, (c[1] + dc[1]) / 2.0))
            template.update({'centers': centers})
        return template

    def estimate_verification(self, data, database):
        prob = SelfGraphEstimation.estimate_verification(self, data, database)
        database_dist = []
        for f_index, f_center in enumerate(database['centers']):
            for s_index, s_center in enumerate(database['centers']):
                if f_index != s_index:
                    database_dist.append(distance(f_center, s_center))
        data_dist = []
        for f_index, f_center in enumerate(data['centers']):
            for s_index, s_center in enumerate(data['centers']):
                if f_index != s_index:
                    data_dist.append(distance(f_center, s_center))
        database_dist = [d / (1.0 * database_dist[0]) for d in database_dist]
        data_dist = [d / (1.0 * data_dist[0]) for d in data_dist]
        coeff = 0
        count = 0
        for index, d_database in enumerate(database_dist):
            d_data = data_dist[index]
            if d_database == d_data == 0:
                coeff += 1
            elif d_database > d_data:
                coeff += d_data / (1.0 * d_database)
            else:
                coeff += d_database / (1.0 * d_data)
            count += 1
        # prob /= 1.0 * len(database)
        prob *= coeff / (1.0 * count)
        logger.debug("Probability: " + str(prob))
        return prob
