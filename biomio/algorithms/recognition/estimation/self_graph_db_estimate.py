from self_graph_estimate import SelfGraphEstimation
from biomio.algorithms.logger import logger


class SelfGraphDatabaseEstimation(SelfGraphEstimation):
    def __init__(self, detector_type, knn):
        SelfGraphEstimation.__init__(self, detector_type, knn)

    @staticmethod
    def defaultDatabase():
        return []

    @staticmethod
    def exportDatabase(data):
        return [SelfGraphEstimation.exportDatabase(d) for d in data]

    @staticmethod
    def importDatabase(data):
        return [SelfGraphEstimation.importDatabase(d) for d in data]

    def estimate_training(self, data, database):
        template = database
        template.append({'clusters': data['clusters'], 'key_desc': data['key_desc'], 'data': data['roi']})
        return template

    def estimate_verification(self, data, database):
        prob = 0
        for db in database:
            prob += SelfGraphEstimation.estimate_verification(self, data, db)
        logger.debug("Total probability: " + str(prob / (1.0 * len(database))))
        return prob / (1.0 * len(database))
