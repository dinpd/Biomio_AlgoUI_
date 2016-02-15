from biomio.algorithms.features.matchers import CrossMatching, CROSS_MATCHING_MATCHES, SelfGraph, SubsetsCalculation
from biomio.algorithms.cvtools.types import listToNumpy_ndarray, numpy_ndarrayToList, \
    classKeyPointToArray, arrayToKeyPointClass
from base_template_estimate import BaseTemplateEstimation
from biomio.algorithms.logger import logger
import numpy as np
import copy


class SelfGraphEstimation(BaseTemplateEstimation):
    def __init__(self, detector_type, knn):
        BaseTemplateEstimation.__init__(self, detector_type, knn)

    @staticmethod
    def exportDatabase(data):
        ser = []
        for cl in data['key_desc']:
            pairs = [(classKeyPointToArray(pair[0], True), numpy_ndarrayToList(pair[1])) for pair in cl]
            ser.append(pairs)

        return {
            'clusters': BaseTemplateEstimation.exportDatabase(data['clusters']),
            'key_desc': ser
        }

    @staticmethod
    def importDatabase(data):
        ser = []
        for cl in data['key_desc']:
            pairs = [(arrayToKeyPointClass(pair[0], True), listToNumpy_ndarray(pair[1])) for pair in cl]
            ser.append(pairs)

        return {
            'clusters': BaseTemplateEstimation.importDatabase(data['clusters']),
            'key_desc': ser
        }

    def estimate_training(self, data, database):
        template = database
        if len(database.keys()) == 0 or len(database.get('clusters', [])) == 0:
            template = {'clusters': data['clusters'], 'key_desc': data['key_desc']}
        else:
            for index, et_cluster in enumerate(database['clusters']):
                dt_cluster = data['clusters'][index]
                if et_cluster is None or len(et_cluster) == 0 or len(et_cluster) < self._knn:
                    template['clusters'][index] = et_cluster
                elif dt_cluster is None or len(dt_cluster) == 0 or len(dt_cluster) < self._knn:
                    template['clusters'][index] = et_cluster
                else:
                    ml = CrossMatching(listToNumpy_ndarray(et_cluster, self._dtype),
                                       listToNumpy_ndarray(dt_cluster, self._dtype),
                                       self._matcher, self._knn, CROSS_MATCHING_MATCHES)
                    cluster = []
                    key_pairs = []
                    for m in ml:
                        et_desc = et_cluster[m.queryIdx]
                        dt_desc = dt_cluster[m.trainIdx]
                        if not self._find_ndarray(cluster, et_desc):
                            cluster.append(et_desc)
                            for pair in database['key_desc'][index]:
                                if np.array_equal(et_desc, pair[1]):
                                    key_pairs.append((pair[0], et_desc))
                                    break
                        if not self._find_ndarray(cluster, dt_desc):
                            cluster.append(dt_desc)
                            for pair in data['key_desc'][index]:
                                if np.array_equal(dt_desc, pair[1]):
                                    key_pairs.append((pair[0], dt_desc))
                                    break
                    template['clusters'][index] = listToNumpy_ndarray(cluster)
                    template['key_desc'][index] = key_pairs
        return template

    def _find_ndarray(self, data, x):
        found = False
        for d in data:
            if np.array_equal(d, x):
                found = True
                break
        return found

    def estimate_verification(self, data, database):
        prob = 0
        summ = 0
        for index, et_cluster in enumerate(database['clusters']):
            dt_cluster = data['clusters'][index]
            if et_cluster is None or len(et_cluster) < self._knn:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
                continue
            if dt_cluster is None or len(dt_cluster) < self._knn:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(et_cluster))
                             + " Positive: 0 Probability: 0 (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")")
                continue
            if len(et_cluster) > 0 and len(dt_cluster) > 0:
                ml = CrossMatching(listToNumpy_ndarray(et_cluster, self._dtype),
                                   listToNumpy_ndarray(dt_cluster, self._dtype),
                                   self._matcher, self._knn, CROSS_MATCHING_MATCHES)
                corr_matches = SubsetsCalculation(ml)
                corr_nodes = [[et_cluster[m.queryIdx], dt_cluster[m.trainIdx], m.distance] for m in corr_matches]
                et_nodes = []
                et_keys = []
                dt_nodes = []
                dt_keys = []
                for m in corr_nodes:
                    for pair in database['key_desc'][index]:
                        if np.array_equal(m[0], pair[1]):
                            et_nodes.append(m[0])
                            et_keys.append(pair[0])
                            break
                    for pair in data['key_desc'][index]:
                        if np.array_equal(m[1], pair[1]):
                            dt_nodes.append(m[1])
                            dt_keys.append(pair[0])
                            break
                et_self_graph = SelfGraph(et_keys, self._knn, et_nodes)
                dt_self_graph = SelfGraph(dt_keys, self._knn, dt_nodes)
                summ += len(et_self_graph)
                # self._print_data(corr_nodes, et_self_match, dt_self_match)
                et_normal = 0
                dt_normal = 0
                end = False
                for corr in corr_nodes:
                    for et_pair in et_self_graph:
                        if np.array_equal(corr[0], et_pair[1]):
                            for dt_pair in dt_self_graph:
                                if np.array_equal(corr[1], dt_pair[1]):
                                    for c in corr_nodes:
                                        if np.array_equal(c[0], et_pair[3]) and np.array_equal(c[1], dt_pair[3]):
                                            et_normal = et_pair[4]
                                            dt_normal = dt_pair[4]
                                            end = True
                                            break
                                if end:
                                    break
                        if end:
                            break
                    if end:
                        break
                if et_normal == 0 or dt_normal == 0:
                    continue
                for et_pair in et_self_graph:
                    et_pair[4] /= 1.0 * et_normal
                for dt_pair in dt_self_graph:
                    dt_pair[4] /= 1.0 * dt_normal
                # self._print_data(corr_nodes, et_self_match, dt_self_match)
                c_prob = 0
                for et_pair in et_self_graph:
                    end = False
                    for corr in corr_nodes:
                        if np.array_equal(corr[0], et_pair[1]):
                            for c in corr_nodes:
                                if np.array_equal(c[0], et_pair[3]):
                                    for dt_pair in dt_self_graph:
                                        if np.array_equal(corr[1], dt_pair[1]) and np.array_equal(c[1], dt_pair[3]):
                                            # coeff = 0
                                            # if corr[2] == c[2] == 0:
                                            #     coeff = 1
                                            # elif corr[2] > c[2]:
                                            #     coeff = c[2] / corr[2]
                                            # else:
                                            #     coeff = corr[2] / c[2]
                                            if et_pair[4] > dt_pair[4]:
                                                c_prob += (dt_pair[4] / et_pair[4])
                                                # c_prob += coeff * (dt_pair[4] / et_pair[4])
                                            else:
                                                c_prob += (et_pair[4] / dt_pair[4])
                                                # c_prob += coeff * (et_pair[4] / dt_pair[4])
                                            end = True
                                            break
                                    if end:
                                        break
                            if end:
                                break
                val = (c_prob / (1.0 * len(et_self_graph))) * 100 # * (len(ml) / (1.0 * len(et_cluster)))
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(et_self_graph)) + " Positive: "
                             + str(c_prob) + " Probability: " + str(val)
                             + " (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")"
                             )
                # prob += (len(et_cluster) / (1.0 * summ)) * val
                prob += c_prob
            else:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(et_cluster)) + " Invalid.")
                continue
        prob = (prob / (1.0 * summ)) * 100
        # prob /= 1.0 * len(database)
        logger.debug("Probability: " + str(prob))
        return prob

    def _print_data(self, corr_nodes, et_matches, dt_matches):
        desc_list = []
        corr_nodes_copy = copy.deepcopy(corr_nodes)
        et_matches_copy = copy.deepcopy(et_matches)
        dt_matches_copy = copy.deepcopy(dt_matches)
        for corr in corr_nodes_copy:
            corr_first = -1
            corr_second = -1
            for desc in desc_list:
                if np.array_equal(desc[0], corr[0]):
                    corr_first = desc[1]
                if np.array_equal(desc[0], corr[1]):
                    corr_second = desc[1]
                if corr_first >= 0 and corr_second >= 0:
                    break
            if corr_first < 0:
                corr_first = len(desc_list)
                desc_list.append((corr[0], corr_first))
            corr[0] = corr_first
            if corr_second < 0:
                corr_second = len(desc_list)
                desc_list.append((corr[1], corr_second))
            corr[1] = corr_second
        for et in et_matches_copy:
            corr_first = -1
            corr_second = -1
            for desc in desc_list:
                if np.array_equal(desc[0], et[0]):
                    corr_first = desc[1]
                if np.array_equal(desc[0], et[1]):
                    corr_second = desc[1]
                if corr_first >= 0 and corr_second >= 0:
                    break
            if corr_first < 0:
                corr_first = len(desc_list)
                desc_list.append((et[0], corr_first))
            et[0] = corr_first
            if corr_second < 0:
                corr_second = len(desc_list)
                desc_list.append((et[1], corr_second))
            et[1] = corr_second
        for dt in dt_matches_copy:
            corr_first = -1
            corr_second = -1
            for desc in desc_list:
                if np.array_equal(desc[0], dt[0]):
                    corr_first = desc[1]
                if np.array_equal(desc[0], dt[1]):
                    corr_second = desc[1]
                if corr_first >= 0 and corr_second >= 0:
                    break
            if corr_first < 0:
                corr_first = len(desc_list)
                desc_list.append((dt[0], corr_first))
            dt[0] = corr_first
            if corr_second < 0:
                corr_second = len(desc_list)
                desc_list.append((dt[1], corr_second))
            dt[1] = corr_second
        # logger.debug("######################################")
        # logger.debug(desc_list)
        logger.debug("######################################")
        logger.debug(corr_nodes_copy)
        logger.debug("######################################")
        logger.debug(et_matches_copy)
        logger.debug("######################################")
        logger.debug(dt_matches_copy)
        logger.debug("######################################")

