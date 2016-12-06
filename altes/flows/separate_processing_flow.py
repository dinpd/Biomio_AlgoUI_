from corealgorithms.flows import AlgorithmFlow


SEPARATION_STAGE = 'flows::separation_stage'
PROCESSING_STAGE = 'flows::processing_stage'
JOINING_STAGE = 'flows::joining_stage'


class SeparateProcessingFlow(AlgorithmFlow):
    def __init__(self):
        AlgorithmFlow.__init__(self)
        self._flow = [SEPARATION_STAGE, PROCESSING_STAGE, JOINING_STAGE]

    def setSeparationStage(self, stage):
        if stage is not None:
            self._stages[SEPARATION_STAGE] = stage

    def separationStage(self):
        return self._stages.get(SEPARATION_STAGE, None)

    def setProcessingStage(self, stage):
        if stage is not None:
            self._stages[PROCESSING_STAGE] = stage

    def processingStage(self):
        return self._stages.get(PROCESSING_STAGE, None)

    def setJoiningStage(self, stage):
        if stage is not None:
            self._stages[JOINING_STAGE] = stage

    def joiningStage(self):
        return self._stages.get(JOINING_STAGE, None)

    def addStage(self, key, stage=None):
        if stage is not None and self._flow.__contains__(key):
            self._stages[key] = stage

    def apply(self, data):
        if self.processingStage() is None:
            raise Exception("Processing stage isn't initialized.")
        data_list = self.separationStage().apply(data) if self.separationStage() is not None else data
        results = []
        for data_item in data_list:
            results.append(self.processingStage().apply(data_item))
        return self.joiningStage().apply(results) if self.joiningStage() is not None else results
