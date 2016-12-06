from corealgorithms.flows import AlgorithmFlow, OpenFaceSimpleDistanceEstimation


class OpenFaceVerificationEstimation(AlgorithmFlow):
    def __init__(self):
        AlgorithmFlow.__init__(self)
        self._estimation = OpenFaceSimpleDistanceEstimation()

    def apply(self, data):
        if data is None:
            return data
        train = data['train']
        train_data = [{'rep': train_img.attribute('rep'), 'img': train_img} for train_img in train]
        test_data = {'rep': data['test'].attribute('rep'), 'img': data['test']}
        dataset = {
            'database': {'data': train_data},
            'data': test_data
        }
        res = self._estimation.apply(dataset)
        dataset.update(res)
        return dataset
