from corealgorithms.flows import IAlgorithm, LinearAlgorithmFlow
from openface_data_extractor import OpenfaceDataExtractor
from database_storage import DatabaseStorage
from database_reader import DatabaseReader


class OpenFaceVerificationPreparation(IAlgorithm):
    def __init__(self):
        self._init()

    def _init(self):
        self.prepare = LinearAlgorithmFlow()
        self.prepare.addStage("DATABASE_READER", DatabaseReader())
        self.prepare.addStage("OPENFACE_EXTRACTOR", OpenfaceDataExtractor())
        self.prepare.addStage("DATABASE_STORAGE", DatabaseStorage())

    def apply(self, data):
        if data is not None:
            return self.prepare.apply(data)
        return data
