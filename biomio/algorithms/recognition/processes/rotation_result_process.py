from biomio.algorithms.interfaces import AlgorithmProcessInterface, logger
from biomio.algorithms.cascades.classifiers import (CascadeROIDetector, RectsFiltering, CascadeClassifierSettings)
from biomio.algorithms.cascades.scripts_detectors import CascadesDetectionInterface
from biomio.algorithms.cascades import SCRIPTS_PATH, CASCADES_PATH, mergeRectangles
from biomio.algorithms.recognition.processes.settings.settings import get_settings
from defs import STATUS_ERROR, STATUS_RESULT, INTERNAL_TRAINING_ERROR
from biomio.algorithms.cascades.tools import loadScript, getROIImage
from messages import create_error_message, create_result_message
from biomio.algorithms.cvtools.types import listToNumpy_ndarray
from handling import load_temp_data, save_temp_data
import ast
import os


class RotationResultProcess(AlgorithmProcessInterface):
    def __init__(self, temp_data_path, worker):
        AlgorithmProcessInterface.__init__(self, temp_data_path, worker)
        self._classname = "RotationResultProcess"
        self._data_detect_process = AlgorithmProcessInterface()

    def data_detection_process(self, process):
        self._data_detect_process = process

    def handler(self, result):
        self._handler_logger_info(result)
        if result is not None:
            if result['status'] == STATUS_ERROR:
                pass
            elif result['status'] == STATUS_RESULT:
                self._data_detect_process.run(self._worker, **result['data'])

    def job(self, callback_code, **kwargs):
        self._job_logger_info(**kwargs)
        images_res_list = [ast.literal_eval(dict_str) for dict_str in kwargs['data_list']]
        kwargs['data_list'] = images_res_list
        record = self.process(**kwargs)
        BaseDataStore.instance().store_job_result(record_key=REDIS_DO_NOT_STORE_RESULT_KEY % callback_code,
                                                  record_dict=record, callback_code=callback_code)

    def process(self, **kwargs):
        self._process_logger_info(**kwargs)
        images_res_list = kwargs['data_list']
        if len(images_res_list) > 0:
            data_list = [load_temp_data(im_res['data_file'], remove=False) for im_res in images_res_list]
            result = dict()
            result['algoID'] = data_list[0]['algoID']
            result["name"] = data_list[0]["name"]
            result["path"] = data_list[0]["path"]
            result["userID"] = data_list[0]["userID"]
            settings = get_settings(result['algoID'])
            images = dict()
            datagram = dict()
            rects = []
            for res in data_list:
                images[res['data_angle']] = res['data']
                for ki, di in res['datagram'].iteritems():
                    datagram[ki] = di
                for rect in res['roi_rects']:
                    rects.append(rect)
            datagram[str([])] = 1
            rotation_script_dict = loadScript(os.path.join(SCRIPTS_PATH, settings['rotation_script']))
            rotation_script = CascadesDetectionInterface.init_stage(rotation_script_dict)
            logger.debug(rotation_script.strategy.type())
            rect = rotation_script.strategy.apply(rects)
            count = {1: 0, 2: 0, 3: 0, 4: 2}
            gl = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0], 3: [0, 0, 0, 0], 4: [0, 0, 0, 0]}
            logger.debug(datagram)
            logger.debug(rect)
            for rs in rect:
                logger.debug(rs)
                if len(rs) < 1:
                    continue
                count[datagram[str(listToNumpy_ndarray(rs[1]))]] += 1
                if ((gl[datagram[str(listToNumpy_ndarray(rs[1]))]][2] < rs[0][2]) and
                        (gl[datagram[str(listToNumpy_ndarray(rs[1]))]][3] < rs[0][3])):
                    gl[datagram[str(listToNumpy_ndarray(rs[1]))]] = rs[0]
            logger.debug(count)
            logger.debug(gl)
            max_count = -1
            midx = 0
            for index in range(1, 5, 1):
                if count[index] > max_count:
                    max_count = count[index]
                    midx = index
                elif count[index] == max_count:
                    if gl[index][2] > gl[midx][2] and gl[index][3] > gl[midx][3]:
                        midx = index
            logger.debug(midx)
            result['data'] = images[midx]

            detector = CascadesDetectionInterface(loadScript(os.path.join(SCRIPTS_PATH, settings['detect_script'])))
            img, rects = detector.detect(result['data'])
            optimal_rect = mergeRectangles(rects)
            if len(optimal_rect) != 4:
                face_classifier = CascadeROIDetector()
                settings = CascadeClassifierSettings()
                settings.minNeighbors = 1
                settings.minSize = (100, 100)
                face_classifier.classifierSettings = settings
                face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt.xml"))
                face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt_tree.xml"))
                face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt2.xml"))
                face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_default.xml"))
                optimal_rect = face_classifier.detectAndJoin(result['data'], False, RectsFiltering)
            result['roi'] = getROIImage(result['data'], optimal_rect)
            detection_process_data = save_temp_data(result, self._temp_data_path, ['data', 'roi'])
            record = create_result_message({'data_file': detection_process_data}, 'detection')
        else:
            record = create_error_message(INTERNAL_TRAINING_ERROR, "data_list", "Empty list of data.")
        return record
