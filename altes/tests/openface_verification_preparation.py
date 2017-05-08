from corealgorithms.flows import IAlgorithm, LinearAlgorithmFlow
from openface_data_extractor import OpenfaceDataExtractor
from database_storage import DatabaseStorage
from database_reader import DatabaseReader
from data_separator import DataSeparator


class OpenFaceVerificationPreparation(IAlgorithm):
    def __init__(self, size=None):
        self._init(size)

    def _init(self, size):
        prepare_int = LinearAlgorithmFlow()
        prepare_int.addStage("OPENFACE_EXTRACTOR", OpenfaceDataExtractor())
        prepare_int.addStage("DATABASE_STORAGE", DatabaseStorage())
        separator = DataSeparator(size)
        separator.setProcessingStage(prepare_int)

        self.prepare = LinearAlgorithmFlow()
        self.prepare.addStage("DATABASE_READER", DatabaseReader())
        self.prepare.addStage("DATA_SEPARATOR", separator)

    def apply(self, data):
        if data is not None:
            return self.prepare.apply(data)
        return data
