from biomio.algorithms.interfaces import AlgorithmProcessInterface
from biomio.algorithms.cascades.scripts_detectors import CascadesDetectionInterface, RotatedCascadesDetector
from biomio.algorithms.cascades.tools import (skipEmptyRectangles, isRectangle, loadScript)
from biomio.algorithms.recognition.processes.settings.settings import get_settings
from messages import create_error_message, create_result_message
from biomio.algorithms.cvtools.types import numpy_ndarrayToList
from biomio.algorithms.cvtools.effects import rotate90
from biomio.algorithms.cascades import SCRIPTS_PATH
from handling import load_temp_data, save_temp_data
import os


class RotationDetectionProcess(AlgorithmProcessInterface):
    def __init__(self, temp_data_path):
        AlgorithmProcessInterface.__init__(self, temp_data_path)
        self._classname = "RotationDetectionProcess"
        self._r_result_process = AlgorithmProcessInterface()

    def set_rotation_result_process(self, process):
        self._r_result_process = process

    def handler(self, result):
        self._handler_logger_info(result)
        if result is not None:
            if result['status'] == STATUS_ERROR:
                pass
            elif result['status'] == STATUS_RESULT:
                worker = WorkerInterface.instance()
                self._r_result_process.run(worker, **result['data'])

    def job(self, callback_code, **kwargs):
        self._job_logger_info(**kwargs)
        record = {'data_file': self.process(**kwargs)}
        RedisStorage.persistence_instance().append_value_to_list(key=REDIS_PARTIAL_RESULTS_KEY % callback_code,
                                                                 value=record)
        results_counter = RedisStorage.persistence_instance().decrement_int_value(REDIS_RESULTS_COUNTER_KEY %
                                                                                  callback_code)
        if results_counter <= 0:
            gathered_results = RedisStorage.persistence_instance().get_stored_list(REDIS_PARTIAL_RESULTS_KEY %
                                                                                   callback_code)
            if results_counter < 0:
                result = create_error_message(INTERNAL_TRAINING_ERROR, "jobs_counter", "Number of jobs is incorrect.")
            else:
                result = create_result_message({'data_list': gathered_results}, 'detection')
            store_verification_results(result=result, callback_code=callback_code)

    def process(self, **kwargs):
        self._process_logger_info(**kwargs)
        source = load_temp_data(kwargs['data_file'], remove=False)
        settings = get_settings(source['algoID'])
        img = source['data']
        for i in range(0, kwargs["angle"], 1):
            img = rotate90(img)
        rects = []
        d = dict()
        rotation_script_dict = loadScript(os.path.join(SCRIPTS_PATH, settings['rotation_script']))
        rotation_script = CascadesDetectionInterface.init_stage(rotation_script_dict)
        detector = RotatedCascadesDetector(rotation_script_dict, dict())
        if len(rotation_script.stages) > 1:
            r = []
            for stage in rotation_script.stages:
                lr1 = detector.apply_stage(img, stage)
                r += lr1
                for lr in lr1:
                    d[str(lr)] = kwargs["angle"] + 1
            if isRectangle(r[0]):
                rects = skipEmptyRectangles(r)
        else:
            stage = rotation_script.stages[0]
            r1 = detector.apply_stage(img, stage)
            rects += r1
            for lr in r1:
                d[str(lr)] = kwargs["angle"] + 1
            rects = skipEmptyRectangles(rects)
        source['data'] = img
        source['data_angle'] = kwargs["angle"] + 1
        source['roi_rects'] = [numpy_ndarrayToList(r) for r in rects]
        source['datagram'] = d
        training_process_data = save_temp_data(source, self._temp_data_path, ['data'])
        return training_process_data
