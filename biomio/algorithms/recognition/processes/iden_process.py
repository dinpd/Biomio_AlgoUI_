from biomio.algorithms.interfaces import AlgorithmProcessInterface


class IdentificationProcess(AlgorithmProcessInterface):
    def __init__(self):
        AlgorithmProcessInterface.__init__(self)

    def handler(self, result):
        pass

    def job(self, callback_code, **kwargs):
        self._job_logger_info(**kwargs)

    def process(self, **kwargs):
        """

        :param kwargs:
        :return: dict
            "cluster_size": length of cluster of the test image,
            "cluster_id": cluster ID,
            "candidates_size": number of found candidates,
            "candidates_score": dict
                <key>: <value>, where <key> - ID of database,
                                      <value> - number of candidates for this database
        """
        cluster = kwargs['cluster']
        database = kwargs['database']
        db = {
            "cluster_size": len(cluster),
            "cluster_id": kwargs["cluster_id"],
            "candidates_size": 0,
            "candidates_score": {}
        }
        for desc in cluster:
            local = database.neighbours(desc)
            db["candidates_size"] += len(local)
            for item in local:
                lcount = db["candidates_score"].get(item[1], 0)
                lcount += 1
                db["candidates_score"][item[1]] = lcount
        return db
