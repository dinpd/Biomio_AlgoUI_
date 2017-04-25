from corealgorithms.flows import AlgorithmFlow
import random


VERIFICATION_ESTIMATOR = "stage::openface_verification_estimator"


class OpenFaceVerificationEstimation(AlgorithmFlow):
    def __init__(self, database_size=5, threshold=0.5, normal_negatives=False):
        AlgorithmFlow.__init__(self)
        self._db_size = database_size
        self._threshold = threshold
        self._normal_negatives = normal_negatives


    def setVerificationEstimator(self, stage):
        self.addStage(VERIFICATION_ESTIMATOR, stage)

    def verificationEstimator(self):
        return self._stages.get(VERIFICATION_ESTIMATOR, None)

    def apply(self, data):
        if data is not None and self.verificationEstimator() is not None:
            print data
            results = {}
            for pkey, pdata in data['data'].iteritems():
                stats = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
                database = []
                pdata_copy = pdata.copy()
                active_size = self._db_size
                while active_size > 0:
                    curr_key = pdata_copy.keys()[random.randint(0, len(pdata_copy.keys()) - 1)]
                    if pdata_copy[curr_key] is not None:
                        database.append({'rep': pdata_copy[curr_key]})
                        active_size -= 1
                    del pdata_copy[curr_key]
                print database
                for tkey, tdata in pdata_copy.iteritems():
                    if tdata is None:
                        continue
                    res = self.verificationEstimator().apply({'database': {'data': database}, 'data': {'rep': tdata}})
                    if res['result'] < self._threshold:
                        value = stats['TP']
                        value += 1
                        stats.update({'TP': value})
                    else:
                        value = stats['FP']
                        value += 1
                        stats.update({'FP': value})
                if not self._normal_negatives:
                    for fkey, fdata in data['data'].iteritems():
                        if fkey != pkey:
                            for dkey, ddata in fdata.iteritems():
                                if ddata is None:
                                    continue
                                res = self.verificationEstimator().apply(
                                    {'database': {'data': database}, 'data': {'rep': ddata}})
                                if res['result'] > self._threshold:
                                    value = stats['TN']
                                    value += 1
                                    stats.update({'TN': value})
                                else:
                                    value = stats['FN']
                                    value += 1
                                    stats.update({'FN': value})
                else:
                    neg_count = len(pdata_copy.keys())
                    while neg_count > 0:
                        ident_key = data['data'].keys()[random.randint(0, len(data['data'].keys()) - 1)]
                        if ident_key != pkey:
                            ident_data = data['data'][ident_key]
                            img_key = ident_data.keys()[random.randint(0, len(ident_data.keys()) - 1)]
                            img_data = ident_data.get(img_key, None)
                            if img_data is None:
                                continue
                            res = self.verificationEstimator().apply({'database': {'data': database},
                                                                      'data': {'rep': img_data}})
                            if res['result'] > self._threshold:
                                value = stats['TN']
                                value += 1
                                stats.update({'TN': value})
                            else:
                                value = stats['FN']
                                value += 1
                                stats.update({'FN': value})
                            neg_count -= 1
                results[pkey] = stats
            data_copy = data.copy()
            data_copy.update({'data': results})
            return data_copy
        return data
