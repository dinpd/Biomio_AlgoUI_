from corealgorithms.flows import AlgorithmFlow
from database_storage import DatabaseStorage
from results_logging import ResultsLogging


class StatisticalMeasurement(AlgorithmFlow):
    def __init__(self):
        AlgorithmFlow.__init__(self)
        self._reader = DatabaseStorage(False)

    def apply(self, data):
        if data is not None:
            logger = ResultsLogging(data['result_path'])
            for key, stage in self._stages.iteritems():
                logger.addStage(key, stage)
            est_data = self._reader.apply(data)
            total = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
            for s_key, s_data in est_data['data'].iteritems():
                total.update({'TP': total['TP'] + s_data['TP'], 'FP': total['FP'] + s_data['FP'],
                              'TN': total['TN'] + s_data['TN'], 'FN': total['FN'] + s_data['FN']})
                logger.apply({'name': s_key, 'data': s_data})
            logger.apply({'name': "Total", 'data': total})
