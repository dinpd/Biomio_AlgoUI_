from biomio.algorithms.features.matchers import SelfGraph, SelfGraph2, SelfGraphRelativeDistance, SelfGraphMatching
from base_template_estimate import BaseTemplateEstimation
from biomio.algorithms.clustering import distance
from biomio.algorithms.logger import logger
import sys


class ClusterSelfGraphEstimation(BaseTemplateEstimation):
    def __init__(self, detector_type, knn):
        BaseTemplateEstimation.__init__(self, detector_type, knn)

    @staticmethod
    def defaultDatabase():
        return []

    def estimate_training(self, data, database):
        template = database
        template.append(data['true_clusters'])
        return template

    ######################################################################################
    #   Average Descriptors
    ######################################################################################
    # def estimate_verification(self, data, database):
    #     prob = 0
    #     for data_set in database:
    #         d_prob = 0
    #         for index, et_cluster in enumerate(data_set):
    #             dt_cluster = data['true_clusters'][index]
    #             if et_cluster is None or len(et_cluster.keys()) <= 0:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #                 continue
    #             if dt_cluster is None:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " +
    #                              str(len(data_set['descriptors'])) + " Positive: 0")
    #                 continue
    #             cross_pairs = []
    #             for idx, item in enumerate(et_cluster['items']):
    #                 neigh_dt = self.neighbour(item, dt_cluster['items'])
    #                 if neigh_dt is None:
    #                     continue
    #                 neigh_et = self.neighbour(neigh_dt[1], et_cluster['items'])
    #                 if neigh_et is not None and idx == neigh_et[0]:
    #                     cross_pairs.append({'template': neigh_et, 'test': neigh_dt})
    #             # logger.debug(cross_pairs)
    #             et_self = SelfGraph(et_cluster['items'], self._knn)
    #             dt_self = SelfGraph(dt_cluster['items'], self._knn)
    #             SelfGraphRelativeDistance(et_self, dt_self, cross_pairs)
    #             # logger.debug(et_self)
    #             # logger.debug(dt_self)
    #             matches = SelfGraphMatching(et_self, dt_self, cross_pairs)
    #             # logger.debug(matches)
    #             c_prob = 0
    #             for match in matches:
    #                 # coeff = 0
    #                 # if corr[2] == c[2] == 0:
    #                 #     coeff = 1
    #                 # elif corr[2] > c[2]:
    #                 #     coeff = c[2] / corr[2]
    #                 # else:
    #                 #     coeff = corr[2] / c[2]
    #                 et_pair = match[0]
    #                 dt_pair = match[1]
    #                 if et_pair[4] > dt_pair[4]:
    #                     c_prob += (dt_pair[4] / et_pair[4])
    #                     # c_prob += coeff * (dt_pair[4] / et_pair[4])
    #                 else:
    #                     c_prob += (et_pair[4] / dt_pair[4])
    #                     # c_prob += coeff * (et_pair[4] / dt_pair[4])
    #             if len(matches) > 0:
    #                 c_prob /= (1.0 * len(matches))
    #             val = c_prob * 100
    #             logger.debug("Cluster #" + str(index + 1) + ": " + str(len(matches)) + " Positive: "
    #                          + str(c_prob) + " Probability: " + str(val))
    #             d_prob += val
    #         d_prob /= (1.0 * len(data_set))
    #         logger.debug("Total for image: " + str(d_prob))
    #         prob += d_prob
    #     prob /= (1.0 * len(database))
    #     logger.debug("Probability: " + str(prob))
    #     return prob

    ######################################################################################
    #   Adding Vectors
    ######################################################################################
    # def estimate_verification(self, data, database):
    #     prob = 0
    #     for data_set in database:
    #         d_prob = 0
    #         for index, et_cluster in enumerate(data_set):
    #             dt_cluster = data['true_clusters'][index]
    #             if et_cluster is None or len(et_cluster.keys()) <= 0 or len(et_cluster.get('items', [])) <= 0:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #                 continue
    #             if dt_cluster is None or len(dt_cluster.keys()) <= 0 or len(dt_cluster.get('items', [])) <= 0:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #                 continue
    #             coeff = et_cluster['radius'] / dt_cluster['radius']
    #             dt_norm_cluster = [(coeff * center[0], coeff * center[1]) for center in dt_cluster['subncenters']]
    #             # dt_norm_cluster = dt_cluster['subncenters']
    #             cross_pairs = []
    #             for idx, item in enumerate(et_cluster['subncenters']):
    #                 neigh_dt = self.neighbour(item, dt_norm_cluster)
    #                 if neigh_dt is None:
    #                     continue
    #                 neigh_et = self.neighbour(neigh_dt[1], et_cluster['subncenters'])
    #                 if neigh_et is not None and idx == neigh_et[0]:
    #                     cross_pairs.append({'template': neigh_et, 'test': neigh_dt})
    #             # logger.debug(cross_pairs)
    #             et_self = SelfGraph2(et_cluster['subncenters'], self._knn)
    #             dt_self = SelfGraph2(dt_norm_cluster, self._knn)
    #             SelfGraphRelativeDistance(et_self, dt_self, cross_pairs)
    #             # logger.debug(et_self)
    #             # logger.debug(dt_self)
    #             matches = SelfGraphMatching(et_self, dt_self, cross_pairs)
    #             # logger.debug(matches)
    #             c_prob = 0
    #             for match in matches:
    #                 # coeff = 0
    #                 # if corr[2] == c[2] == 0:
    #                 #     coeff = 1
    #                 # elif corr[2] > c[2]:
    #                 #     coeff = c[2] / corr[2]
    #                 # else:
    #                 #     coeff = corr[2] / c[2]
    #                 et_pair = match[0]
    #                 dt_pair = match[1]
    #                 ########################################################################
    #                 # Default Coefficient
    #                 ########################################################################
    #                 c = 1.0
    #                 ########################################################################
    #                 # Distance Compensation Coefficient
    #                 ########################################################################
    #                 # c = ((1.0 / (1.0 + distance(et_pair[0], dt_pair[0]))) *
    #                 #      (1.0 / (1.0 + distance(et_pair[2], dt_pair[2]))))
    #                 ########################################################################
    #                 # Vector Distance Compensation Coefficient
    #                 ########################################################################
    #                 # f_x = et_pair[0][0] - dt_pair[0][0]
    #                 # f_y = et_pair[0][1] - dt_pair[0][1]
    #                 # s_x = et_pair[2][0] - dt_pair[2][0]
    #                 # s_y = et_pair[2][1] - dt_pair[2][1]
    #                 # f_et_cluster = None
    #                 # s_et_cluster = None
    #                 # for subcluster in et_cluster['subclusters']:
    #                 #     if et_pair[0] == subcluster['ncenter']:
    #                 #         f_et_cluster = subcluster
    #                 #     if et_pair[2] == subcluster['ncenter']:
    #                 #         s_et_cluster = subcluster
    #                 #     if f_et_cluster is not None and s_et_cluster is not None:
    #                 #         break
    #                 # f_dt_cluster = None
    #                 # s_dt_cluster = None
    #                 # for jdx, jcenter in enumerate(dt_norm_cluster):
    #                 #     if dt_pair[0] == jcenter:
    #                 #         f_dt_cluster = dt_cluster['subclusters'][jdx]
    #                 #     if dt_pair[2] == jcenter:
    #                 #         s_dt_cluster = dt_cluster['subclusters'][jdx]
    #                 #     if f_dt_cluster is not None and s_dt_cluster is not None:
    #                 #         break
    #                 # logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #                 # logger.debug(f_et_cluster)
    #                 # logger.debug(f_dt_cluster)
    #                 # logger.debug(s_et_cluster)
    #                 # logger.debug(s_dt_cluster)
    #                 # logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #                 # f_dt_vector = (f_dt_cluster['vector_point'][0] + f_x, f_dt_cluster['vector_point'][1] + f_y)
    #                 # s_dt_vector = (s_dt_cluster['vector_point'][0] + s_x, s_dt_cluster['vector_point'][1] + s_y)
    #                 # f_vector_dist = distance(f_et_cluster['vector_point'], f_dt_vector)
    #                 # s_vector_dist = distance(s_et_cluster['vector_point'], s_dt_vector)
    #                 # c = (1.0 / (1.0 + f_vector_dist)) * (1.0 / (1.0 + s_vector_dist))
    #                 ########################################################################
    #                 if et_pair[4] > dt_pair[4]:
    #                     diff = (dt_pair[4] / et_pair[4])
    #                 else:
    #                     diff = (et_pair[4] / dt_pair[4])
    #                 c_prob += c * diff
    #             if len(matches) > 0:
    #                 c_prob /= (1.0 * len(matches))
    #             val = c_prob * 100
    #             logger.debug("Cluster #" + str(index + 1) + ": " + str(len(matches)) + " Positive: "
    #                          + str(c_prob) + " Probability: " + str(val))
    #             d_prob += val
    #         d_prob /= (1.0 * len(data_set))
    #         logger.debug("Total for image: " + str(d_prob))
    #         prob += d_prob
    #     prob /= (1.0 * len(database))
    #     logger.debug("Probability: " + str(prob))
    #     return prob

    ######################################################################################
    #   Hexagon Vector Estimation based on FOREL Subclustering
    ######################################################################################
    def estimate_verification(self, data, database):
        prob = 0
        for data_set in database:
            d_prob = 0
            for index, et_cluster in enumerate(data_set):
                dt_cluster = data['true_clusters'][index]
                if et_cluster is None or len(et_cluster.keys()) <= 0 or len(et_cluster.get('items', [])) <= 0:
                    logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
                    continue
                if dt_cluster is None or len(dt_cluster.keys()) <= 0 or len(dt_cluster.get('items', [])) <= 0:
                    logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
                    continue
                coeff = et_cluster['radius'] / dt_cluster['radius']
                dt_norm_cluster = [(coeff * center[0], coeff * center[1]) for center in dt_cluster['subncenters']]
                # dt_norm_cluster = dt_cluster['subncenters']
                cross_pairs = []
                for idx, item in enumerate(et_cluster['subncenters']):
                    neigh_dt = self.neighbour(item, dt_norm_cluster)
                    if neigh_dt is None:
                        continue
                    neigh_et = self.neighbour(neigh_dt[1], et_cluster['subncenters'])
                    if neigh_et is not None and idx == neigh_et[0]:
                        cross_pairs.append({'template': neigh_et, 'test': neigh_dt})
                # logger.debug(cross_pairs)
                et_self = SelfGraph2(et_cluster['subncenters'], self._knn)
                dt_self = SelfGraph2(dt_norm_cluster, self._knn)
                SelfGraphRelativeDistance(et_self, dt_self, cross_pairs)
                # logger.debug(et_self)
                # logger.debug(dt_self)
                matches = SelfGraphMatching(et_self, dt_self, cross_pairs)
                # logger.debug(matches)
                c_prob = 0
                for match in matches:
                    et_pair = match[0]
                    dt_pair = match[1]
                    ########################################################################
                    # Default Coefficient
                    ########################################################################
                    c = 1.0
                    ########################################################################
                    # Distance Compensation Coefficient
                    ########################################################################
                    # c = ((1.0 / (1.0 + distance(et_pair[0], dt_pair[0]))) *
                    #      (1.0 / (1.0 + distance(et_pair[2], dt_pair[2]))))
                    ########################################################################
                    # Vector Distance Compensation Coefficient
                    ########################################################################
                    f_et_cluster = None
                    s_et_cluster = None
                    for subcluster in et_cluster['subclusters']:
                        if et_pair[0] == subcluster['ncenter']:
                            f_et_cluster = subcluster
                        if et_pair[2] == subcluster['ncenter']:
                            s_et_cluster = subcluster
                        if f_et_cluster is not None and s_et_cluster is not None:
                            break
                    f_dt_cluster = None
                    s_dt_cluster = None
                    for jdx, jcenter in enumerate(dt_norm_cluster):
                        if dt_pair[0] == jcenter:
                            f_dt_cluster = dt_cluster['subclusters'][jdx]
                        if dt_pair[2] == jcenter:
                            s_dt_cluster = dt_cluster['subclusters'][jdx]
                        if f_dt_cluster is not None and s_dt_cluster is not None:
                            break
                    first_length = self.relation(f_et_cluster['vector_length'], f_dt_cluster['vector_length'])
                    second_length = self.relation(s_et_cluster['vector_length'], s_dt_cluster['vector_length'])
                    first_angle = self.angle_distance(f_et_cluster['vector_angle'], f_dt_cluster['vector_angle'])
                    second_angle = self.angle_distance(s_et_cluster['vector_angle'], s_dt_cluster['vector_angle'])
                    c = first_length * first_angle * second_length * second_angle
                    ########################################################################
                    if et_pair[4] > dt_pair[4]:
                        diff = (dt_pair[4] / et_pair[4])
                    else:
                        diff = (et_pair[4] / dt_pair[4])
                    c_prob += c * diff
                if len(matches) > 0:
                    c_prob /= (1.0 * len(matches))
                val = c_prob * 100
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(matches)) + " Positive: "
                             + str(c_prob) + " Probability: " + str(val))
                d_prob += val
            d_prob /= (1.0 * len(data_set))
            logger.debug("Total for image: " + str(d_prob))
            prob += d_prob
        prob /= (1.0 * len(database))
        logger.debug("Probability: " + str(prob))
        return prob

    ######################################################################################
    #   Hexagons Subclustering
    ######################################################################################
    # def estimate_verification(self, data, database):
    #     prob = 0
    #     for data_set in database:
    #         d_prob = 0
    #         for index, et_cluster in enumerate(data_set):
    #             dt_cluster = data['true_clusters'][index]
    #             if et_cluster is None or len(et_cluster.keys()) <= 0 or len(et_cluster.get('items', [])) <= 0:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #                 continue
    #             if dt_cluster is None or len(dt_cluster.keys()) <= 0 or len(dt_cluster.get('items', [])) <= 0:
    #                 logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #                 continue
    #             coeff = et_cluster['radius'] / dt_cluster['radius']
    #             dt_norm_cluster = [(coeff * center[0], coeff * center[1]) for center in dt_cluster['subncenters']]
    #             # dt_norm_cluster = dt_cluster['subncenters']
    #             cross_pairs = []
    #             for idx, item in enumerate(et_cluster['subncenters']):
    #                 neigh_dt = self.neighbour(item, dt_norm_cluster)
    #                 if neigh_dt is None:
    #                     continue
    #                 neigh_et = self.neighbour(neigh_dt[1], et_cluster['subncenters'])
    #                 if neigh_et is not None and idx == neigh_et[0]:
    #                     cross_pairs.append({'template': neigh_et, 'test': neigh_dt})
    #             # logger.debug(cross_pairs)
    #             et_self = SelfGraph2(et_cluster['subncenters'], self._knn)
    #             dt_self = SelfGraph2(dt_norm_cluster, self._knn)
    #             SelfGraphRelativeDistance(et_self, dt_self, cross_pairs)
    #             # logger.debug(et_self)
    #             # logger.debug(dt_self)
    #             matches = SelfGraphMatching(et_self, dt_self, cross_pairs)
    #             # logger.debug(matches)
    #             c_prob = 0
    #             for match in matches:
    #                 # coeff = 0
    #                 # if corr[2] == c[2] == 0:
    #                 #     coeff = 1
    #                 # elif corr[2] > c[2]:
    #                 #     coeff = c[2] / corr[2]
    #                 # else:
    #                 #     coeff = corr[2] / c[2]
    #                 et_pair = match[0]
    #                 dt_pair = match[1]
    #                 ########################################################################
    #                 # Default Coefficient
    #                 ########################################################################
    #                 # c = 1.0
    #                 ########################################################################
    #                 # Distance Compensation Coefficient
    #                 ########################################################################
    #                 # c = ((1.0 / (1.0 + distance(et_pair[0], dt_pair[0]))) *
    #                 #      (1.0 / (1.0 + distance(et_pair[2], dt_pair[2]))))
    #                 ########################################################################
    #                 # Vector Distance Compensation Coefficient
    #                 ########################################################################
    #                 f_et_cluster = None
    #                 s_et_cluster = None
    #                 for subcluster in et_cluster['subclusters']:
    #                     if et_pair[0] == subcluster['ncenter']:
    #                         f_et_cluster = subcluster
    #                     if et_pair[2] == subcluster['ncenter']:
    #                         s_et_cluster = subcluster
    #                     if f_et_cluster is not None and s_et_cluster is not None:
    #                         break
    #                 f_dt_cluster = None
    #                 s_dt_cluster = None
    #                 for jdx, jcenter in enumerate(dt_norm_cluster):
    #                     if dt_pair[0] == jcenter:
    #                         f_dt_cluster = dt_cluster['subclusters'][jdx]
    #                     if dt_pair[2] == jcenter:
    #                         s_dt_cluster = dt_cluster['subclusters'][jdx]
    #                     if f_dt_cluster is not None and s_dt_cluster is not None:
    #                         break
    #                 first_length = self.relation(f_et_cluster['vector_length'], f_dt_cluster['vector_length'])
    #                 second_length = self.relation(s_et_cluster['vector_length'], s_dt_cluster['vector_length'])
    #                 first_angle = self.angle_distance(f_et_cluster['vector_angle'], f_dt_cluster['vector_angle'])
    #                 second_angle = self.angle_distance(s_et_cluster['vector_angle'], s_dt_cluster['vector_angle'])
    #                 c = first_length * first_angle * second_length * second_angle
    #                 ########################################################################
    #                 if et_pair[4] > dt_pair[4]:
    #                     diff = (dt_pair[4] / et_pair[4])
    #                 else:
    #                     diff = (et_pair[4] / dt_pair[4])
    #                 c_prob += c * diff
    #             if len(matches) > 0:
    #                 c_prob /= (1.0 * len(matches))
    #             val = c_prob * 100
    #             logger.debug("Cluster #" + str(index + 1) + ": " + str(len(matches)) + " Positive: "
    #                          + str(c_prob) + " Probability: " + str(val))
    #             d_prob += val
    #         d_prob /= (1.0 * len(data_set))
    #         logger.debug("Total for image: " + str(d_prob))
    #         prob += d_prob
    #     prob /= (1.0 * len(database))
    #     logger.debug("Probability: " + str(prob))
    #     return prob

    @staticmethod
    def relation(v1, v2):
        if v1 == v2 == 0:
            return 1.0
        elif v1 > v2:
            return v2 / v1
        else:
            return v1 / v2

    @staticmethod
    def angle_distance(a1, a2):
        if a1 > a2:
            h = a1
            l = a2
        else:
            h = a2
            l = a1
        f_diff = h - l
        s_diff = l + 360 - h
        r_diff = f_diff if f_diff < s_diff else s_diff
        return 1.0 - r_diff / 360.0

    def neighbour(self, point, items):
        min_dis = sys.maxint
        neigh = None
        for index, item in enumerate(items):
            dis = distance(point, item)
            if min_dis > dis:
                min_dis = dis
                neigh = index
        if neigh is None:
            return None
        return neigh, items[neigh]
