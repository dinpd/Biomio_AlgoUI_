from biomio.algorithms.interfaces import AlgorithmProcessInterface


class IdentificationREProcess(AlgorithmProcessInterface):
    """
        Identification Results Estimation Process
    """
    def __init__(self):
        AlgorithmProcessInterface.__init__(self)

    def handler(self, result):
        pass

    def job(self, callback_code, **kwargs):
        pass

    def process(self, **kwargs):
        """

        :param kwargs: dict
            "results": list of dicts
                "cluster_size": length of cluster of the test image,
                "cluster_id": cluster ID,
                "candidates_size": number of found candidates,
                "candidates_score": dict
                    <key>: <value>, where <key> - ID of database,
                                          <value> - number of candidates for this database
            "test_size": numbers of descriptors in test dataset
        :return:
        """
        results = kwargs["results"]
        test_size = kwargs["test_size"]
        if len(results) > 0:
            db_score = {}
            gsum = 0
            for result in results:
                res_score = result.get("candidates_score", {})
                gsum += result.get("candidates_size", 0)
                score_cost = 1#result.get("cluster_size", 0) / (1.0 * test_size)
                for key, value in res_score.iteritems():
                    lcount = db_score.get(key, 0)
                    lcount += score_cost * value
                    db_score[key] = lcount
            print db_score
            print gsum * 0.3
