from corealgorithms.flows import IAlgorithm
import scipy.spatial.distance as distance


class EuclideanEstimation(IAlgorithm):
    """
    Input:
    {
        'database': database based on the training data
        {
            'rep': representation array
        }
        'data': test data
        {
            'rep': representation array
        }
    }
    Output:
    {
        'database': database based on the training data
        {
            'rep': representation array
        }
        'data': test data
        {
            'rep': representation array
        }
        'result: distance between database and test data
    }
    """
    def __init__(self):
        pass

    def apply(self, data):
        tdatabase = data.get('database')
        tdata = data.get('data')
        if tdatabase is None or tdata is None:
            # TODO: Write Error handler
            return {'result': 0}
        avg = distance.euclidean(tdata['rep'], tdatabase['rep'])
        data.update({'result': avg})
        return data
