from biomio.algorithms.interfaces import AlgorithmProcessInterface, logger
from biomio.algorithms.recognition.processes.defs import ERROR_FORMAT, INTERNAL_TRAINING_ERROR, UNKNOWN_ERROR
from biomio.algorithms.datastructs import get_data_structure


class UpdateDataStructureProcess(AlgorithmProcessInterface):
    def __init__(self):
        AlgorithmProcessInterface.__init__(self)
        self._classname = "UpdateDataStructureProcess"

    def handler(self, result):
        pass

    def job(self, callback_code, **kwargs):
        self._job_logger_info(**kwargs)
        engines = self.process(**kwargs)
        if len(engines) > 0:
            pass
        else:
            logger.info(ERROR_FORMAT % (INTERNAL_TRAINING_ERROR, UNKNOWN_ERROR))

    def process(self, **kwargs):
        self._process_logger_info(**kwargs)
        data_struct = kwargs.get("database", None)
        settings = kwargs["settings"]
        print settings
        print data_struct
        if data_struct is None:
            data_struct = get_data_structure(settings.get("database_type"))(settings.get("settings", {}))
        print data_struct
        db = kwargs.get("template", [])
        if len(db) > 0:
            cluster_id = kwargs.get("cluster_id", -1)
            if cluster_id >= 0:
                cluster = db[cluster_id]
            else:
                cluster = db
            for desc in cluster:
                data_struct.store_vector(desc, kwargs.get("uuid"))
        return data_struct
