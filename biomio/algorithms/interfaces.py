from biomio.algorithms.logger import logger


class AlgorithmProcessInterface:
    def __init__(self, temp_data_path='', worker=None):
        self._temp_data_path = temp_data_path
        self._worker = worker
        self._classname = "AlgorithmProcessInterface"
        self._error_process = None
        self._callback = None

    def set_error_handler_process(self, process):
        self._error_process = process

    def external_callback(self, callback):
        self._callback = callback

    def handler(self, result):
        raise NotImplementedError

    @staticmethod
    def job(callback_code, **kwargs):
        raise NotImplementedError

    @staticmethod
    def process(**kwargs):
        """
          Method for handle worker-independent process functionality.
        :param kwargs: settings dictionary
        """
        raise NotImplementedError

    def run(self, worker, kwargs_list_for_results_gatherer=None, **kwargs):
        raise NotImplementedError

    def _run(self, worker, job, kwargs_list_for_results_gatherer=None, **kwargs):
        if worker is not None:
            worker.run_job(job, callback=self.handler,
                           kwargs_list_for_results_gatherer=kwargs_list_for_results_gatherer, **kwargs)

    def _run_external(self, worker, job, kwargs_list_for_results_gatherer=None, **kwargs):
        if worker is not None:
            worker.run_job(job, callback=self._callback,
                           kwargs_list_for_results_gatherer=kwargs_list_for_results_gatherer, **kwargs)

    def _handler_logger_info(self, result):
        logger.debug("+++++++++++++++++++++++++++++++++++")
        logger.debug("%s::Handler", self._classname)
        logger.debug(result)
        logger.debug("+++++++++++++++++++++++++++++++++++")

    @staticmethod
    def _job_logger_info(class_name, **kwargs):
        logger.debug("-----------------------------------")
        logger.debug("%s::Job", class_name)
        logger.debug(kwargs)
        logger.debug("-----------------------------------")

    @staticmethod
    def _process_logger_info(class_name, **kwargs):
        logger.debug("===================================")
        logger.debug("%s::Process", class_name)
        logger.debug(kwargs)
        logger.debug("===================================")


class AlgorithmInterface:

    def training(self, callback=None, **kwargs):
        raise NotImplementedError

    def apply(self, callback=None, **kwargs):
        raise NotImplementedError


class AlgorithmEstimation:

    def estimate_training(self, data, database):
        raise NotImplementedError

    def estimate_verification(self, data, database):
        raise NotImplementedError
