from tests.openface_verification_preparation import OpenFaceVerificationPreparation
from tests.openface_verification_evaluation import OpenFaceVerificationEvaluation
from tests.statistical_measurement import StatisticalMeasurement
from tests.precision_measure import PrecisionMeasure
from tests.recall_measure import RecallMeasure
from tests.f_measure import FMeasure
import json


def read_configuration_file(path):
    json_data = dict()
    with open(path) as data_file:
        json_data = json.load(data_file)
    keys = ['test', 'stages', 'options', 'data']
    for key in keys:
        if not json_data.__contains__(key):
            raise "Configuration File hasn't {} key".format(key)
    return json_data


AVAILABLE_TEST = {
    OpenFaceVerificationPreparation.__name__: OpenFaceVerificationPreparation,
    OpenFaceVerificationEvaluation.__name__: OpenFaceVerificationEvaluation,
    StatisticalMeasurement.__name__: StatisticalMeasurement,
    PrecisionMeasure.__name__: PrecisionMeasure,
    RecallMeasure.__name__: RecallMeasure,
    FMeasure.__name__: FMeasure
}
