from biomio.algorithms.cvtools.types import listToNumpy_ndarray
from base_template_estimate import BaseTemplateEstimation
from biomio.algorithms.logger import logger


class AverageDescriptorEstimation(BaseTemplateEstimation):
    def __init__(self, detector_type, knn):
        BaseTemplateEstimation.__init__(self, detector_type, knn)

    @staticmethod
    def defaultDatabase():
        return []

    # def estimate_training(self, data, database):
    #     template = database
    #     if len(database) == 0:
    #         for index, _ in enumerate(data['true_clusters']):
    #             template.append({'descriptors': []})
    #     for index, cluster in enumerate(data['true_clusters']):
    #         template_desc = template[index]
    #         template_desc['descriptors'].append(cluster['avg_descriptor'])
    #     return template

    def estimate_training(self, data, database):
        template = database
        if len(database) == 0:
            for index, _ in enumerate(data['true_clusters']):
                template.append({'descriptors': []})
        for index, cluster in enumerate(data['true_clusters']):
            template_desc = template[index]
            for desc in cluster['avg_descriptors']:
                template_desc['descriptors'].append(desc)
        return template

    # def estimate_verification(self, data, database):
    #     prob = 0
    #     for index, data_set in enumerate(database):
    #         dt_cluster = data['true_clusters'][index]
    #         if data_set is None or len(data_set['descriptors']) <= 0:
    #             logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
    #             continue
    #         if dt_cluster is None:
    #             logger.debug("Cluster #" + str(index + 1) + ": " + str(len(data_set['descriptors'])) + " Positive: 0"
    #                          # + " Probability: 0 (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")"
    #                          )
    #             continue
    #         matches = self._matcher.knnMatch(listToNumpy_ndarray([dt_cluster['avg_descriptor']], self._dtype),
    #                                          listToNumpy_ndarray(data_set['descriptors'], self._dtype), k=self._knn)
    #         c_prob = 0
    #         if len(matches) > 0:
    #             for m in matches[0]:
    #                 c_prob += 1.0 / (1.0 + m.distance)
    #         c_prob /= 1.0 * len(data_set['descriptors'])
    #         logger.debug("Cluster #" + str(index + 1) + ": " + str(len(data_set['descriptors'])) + " Probability: " +
    #                      str(c_prob * 100))
    #         prob += c_prob
    #     prob = (prob / (1.0 * len(database))) * 100
    #     logger.debug("Probability: " + str(prob))
    #     return prob

    def estimate_verification(self, data, database):
        prob = 0
        for index, data_set in enumerate(database):
            dt_cluster = data['true_clusters'][index]
            if data_set is None or len(data_set['descriptors']) <= 0:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(-1) + " Invalid. (Weight: 0)")
                continue
            if dt_cluster is None:
                logger.debug("Cluster #" + str(index + 1) + ": " + str(len(data_set['descriptors'])) + " Positive: 0"
                             # + " Probability: 0 (Weight: " + str(len(et_cluster) / (1.0 * summ)) + ")"
                             )
                continue
            matches = self._matcher.knnMatch(listToNumpy_ndarray(dt_cluster['avg_descriptors'], self._dtype),
                                             listToNumpy_ndarray(data_set['descriptors'], self._dtype), k=self._knn)
            c_prob = 0
            count = 0
            for mmain in matches:
                count += len(mmain)
                for m in mmain:
                    c_prob += 1.0 / (1.0 + m.distance)
            # c_prob /= 1.0 * len(data_set['descriptors'])
            if count > 0:
                c_prob /= 1.0 * count
            logger.debug("Cluster #" + str(index + 1) + ": " + str(len(data_set['descriptors'])) + " Probability: " +
                         str(c_prob * 100))
            prob += c_prob
        prob = (prob / (1.0 * len(database))) * 100
        logger.debug("Probability: " + str(prob))
        return prob
