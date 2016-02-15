from biomio.algorithms.interfaces import AlgorithmProcessInterface
import os


class MainTrainingProcess(AlgorithmProcessInterface):
    def __init__(self, temp_data_path, worker):
        AlgorithmProcessInterface.__init__(self, temp_data_path, worker)
        self._classname = "MainTrainingProcess"
        self._training_process = AlgorithmProcessInterface()

    def set_data_training_process(self, process):
        self._training_process = process

    def handler(self, result):
        raise NotImplementedError

    def job(self, callback_code, **kwargs):
        raise NotImplementedError

    def process(self, **kwargs):
        self._process_logger_info(kwargs)
        if not os.path.exists(self._temp_data_path):
            os.mkdir(self._temp_data_path, 0o777)
            os.chmod(self._temp_data_path, 0o777)
        for image_path in kwargs["data"]:
            settings = kwargs.copy()
            settings['path'] = image_path
            self._training_process.run(self._worker, **settings)
