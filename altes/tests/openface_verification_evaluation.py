from corealgorithms.flows import IAlgorithm, LinearAlgorithmFlow, OpenFaceSimpleDistanceEstimation
from openface_verification_estimation import OpenFaceVerificationEstimation
from database_storage import DatabaseStorage
from data_uniter import DataUniter


class OpenFaceVerificationEvaluation(IAlgorithm):
    def __init__(self, database_size, threshold, normal_negatives):
        self._init(database_size, threshold, normal_negatives)

    def _init(self, database_size, threshold, normal_negatives):
        uniter = DataUniter()
        uniter.setProcessingStage(DatabaseStorage(False))

        self._evaluation = LinearAlgorithmFlow()
        self._evaluation.addStage("DATABASE_LOADER", uniter)

        estimator = OpenFaceVerificationEstimation(database_size=database_size, threshold=threshold,
                                                   normal_negatives=normal_negatives)
        estimator.setVerificationEstimator(OpenFaceSimpleDistanceEstimation())
        self._evaluation.addStage('DATABASE_ESTIMATION', estimator)
        self._evaluation.addStage("DATABASE_STORAGE", DatabaseStorage())

    def apply(self, data):
        if data is not None:
            return self._evaluation.apply(data)
        return data
