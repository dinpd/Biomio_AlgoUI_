from corealgorithms.flows import AlgorithmFlow
import scipy.spatial.distance as distance

BASIC_ESTIMATION_STAGE = 'flows:basic_estimation'

class EmbeddingsRepresentationEstimation(AlgorithmFlow):
    def __init__(self):
        AlgorithmFlow.__init__(self)

    def setBasicEstimationStage(self, stage):
        self._stages[BASIC_ESTIMATION_STAGE] = stage

    def apply(self, data):
        if data is None:
            return data
        res = self._stages[BASIC_ESTIMATION_STAGE].apply(data)
        result = res['result']
        train_imgs = res['database']['data']
        test_img = res['data']['img']
        emb_dist = 0
        for train_data in train_imgs:
            emb_dist += distance.euclidean(test_img.attribute('embeddings'), train_data['img'].attribute('embeddings'))
        emb_dist /= (1.0 * len(train_imgs))
        res.update({'result': result if result > emb_dist else emb_dist,
                    'basic_result': result, 'emb_result': emb_dist})
        return res
