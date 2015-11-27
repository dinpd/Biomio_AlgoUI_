from biomio.algorithms.logger import logger


class AlgorithmProcessInterface:
    def __init__(self, temp_data_path='', worker=None):
        self._temp_data_path = temp_data_path
        self._worker = worker
        self._classname = "AlgorithmProcessInterface"
        self._error_process = None

    def set_error_handler_process(self, process):
        self._error_process = process

    def handler(self, result):
        raise NotImplementedError

    def job(self, callback_code, **kwargs):
        raise NotImplementedError

    def process(self, **kwargs):
        raise NotImplementedError

    def run(self, worker, kwargs_list_for_results_gatherer=None, **kwargs):
        if worker is not None:
            worker.run_job(self.job, callback=self.handler,
                           kwargs_list_for_results_gatherer=kwargs_list_for_results_gatherer, **kwargs)

    def _handler_logger_info(self, result):
        logger.debug("+++++++++++++++++++++++++++++++++++")
        logger.debug("%s::Handler", self._classname)
        logger.debug(result)
        logger.debug("+++++++++++++++++++++++++++++++++++")

    def _job_logger_info(self, **kwargs):
        logger.debug("-----------------------------------")
        logger.debug("%s::Job", self._classname)
        logger.debug(kwargs)
        logger.debug("-----------------------------------")

    def _process_logger_info(self, **kwargs):
        logger.debug("===================================")
        logger.debug("%s::Process", self._classname)
        logger.debug(kwargs)
        logger.debug("===================================")


class AlgorithmInterface:

    def training(self, callback=None, **kwargs):
        raise NotImplementedError

    def apply(self, callback=None, **kwargs):
        raise NotImplementedError
