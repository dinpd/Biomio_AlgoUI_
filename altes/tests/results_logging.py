from corealgorithms.flows import AlgorithmFlow


class ResultsLogging(AlgorithmFlow):
    def __init__(self, path, use_stage_name=True):
        AlgorithmFlow.__init__(self)
        self._use_stage_name = use_stage_name
        self._log_file = open(path, 'a')

    def apply(self, data):
        if data is not None:
            self._log_file.write("{}:\n".format(data.get('name', 'N/A')))
            self._log_file.write("-------------------------\n")
            self._log_file.write("True Positives (TP): {}\n".format(data['data'].get('TP', None)))
            self._log_file.write("False Positives (FP): {}\n".format(data['data'].get('FP', None)))
            self._log_file.write("True Negatives (TN): {}\n".format(data['data'].get('TN', None)))
            self._log_file.write("False Negatives (FN): {}\n".format(data['data'].get('FN', None)))
            self._log_file.write("-------------------------\n")
            for flow in self._flow:
                stage = self._stages.get(flow, None)
                if stage is not None:
                    self._log_file.write("{}:\t{}\n".format(flow if self._use_stage_name else stage.__class__.__name__,
                                                           stage.apply(data['data']).get('result', 'N/A')))
            self._log_file.write("==================================================\n")