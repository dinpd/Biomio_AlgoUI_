import ast
from biomio.algorithms.interfaces import AlgorithmProcessInterface, logger
from defs import (STATUS_RESULT, STATUS_ERROR, REDIS_GENERAL_DATA, REDIS_CLUSTER_JOB_ACTION,
                  JOB_STATUS_ACTIVE, JOB_STATUS_FINISHED,
                  INTERNAL_TRAINING_ERROR)
from biomio.algorithms.cascades.scripts_detectors import CascadesDetectionInterface
from biomio.algorithms.recognition.kodsettings import KODSettings
from biomio.algorithms.features.features import FeatureDetector
from biomio.algorithms.cvtools.types import numpy_ndarrayToList
from biomio.algorithms.features import constructDetector
from biomio.algorithms.cascades.tools import loadScript
from biomio.algorithms.clustering import KMeans, FOREL
from messages import create_error_message, create_result_message
from handling import load_temp_data, save_temp_data
from settings.settings import get_settings
from settings import loadSettings


class DataDetectionProcess(AlgorithmProcessInterface):
    def __init__(self, temp_data_path):
        AlgorithmProcessInterface.__init__(self)
        self._classname = "DataDetectionProcess"
        self._temp_data_path = temp_data_path
        self._cluster_match_process = AlgorithmProcessInterface()
        self._final_process = AlgorithmProcessInterface()

    def cluster_matching_process(self, process):
        self._cluster_match_process = process

    def final_training_process(self, process):
        self._final_process = process

    def handler(self, result):
        self._handler_logger_info(result)
        if result is not None:
            if result['status'] == STATUS_ERROR:
                general_key = REDIS_GENERAL_DATA % result['details']['userID']
                data = dict()
                fault = 0
                if RedisStorage.persistence_instance().exists(general_key):
                    data = ast.literal_eval(RedisStorage.persistence_instance().get_data(general_key))
                    RedisStorage.persistence_instance().delete_data(general_key)
                    fault = data.get('image_fault', 0)
                data['image_fault'] = fault + 1
                RedisStorage.persistence_instance().store_data(general_key, **data)
                logger.algo_logger.debug("IMAGE FAULT")
                logger.algo_logger.debug(data['image_fault'])
            elif result['status'] == STATUS_RESULT:
                logger.algo_logger.debug(result['data'][0]['data_file'])
                res_data = load_temp_data(result['data'][0]['data_file'], remove=False)
                logger.algo_logger.debug(res_data["name"])
                worker = WorkerInterface.instance()
                for key, cluster in res_data['clusters'].iteritems():
                    current_key = REDIS_CLUSTER_JOB_ACTION % key
                    logger.debug(current_key)
                    if RedisStorage.persistence_instance().exists(current_key):
                        data = ast.literal_eval(RedisStorage.persistence_instance().get_data(current_key))
                        RedisStorage.persistence_instance().delete_data(current_key)
                        logger.debug("@$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$@")
                        logger.debug(data['status'])
                        if data['status'] == JOB_STATUS_ACTIVE:
                            if cluster is not None and len(cluster) > 0:
                                queue = data.get('queued_data', [])
                                queue.append(cluster)
                                data['queued_data'] = queue
                            else:
                                step = data['step']
                                data['step'] = step + 1
                            RedisStorage.persistence_instance().store_data(current_key, **data)
                        elif data['status'] == JOB_STATUS_FINISHED:
                            step = data['step']
                            data['step'] = step + 1
                            logger.debug("TEST#---#CLUSTERS")
                            logger.debug(current_key)
                            logger.debug(data['step'])
                            if cluster is not None and len(cluster) > 0:
                                data['status'] = JOB_STATUS_ACTIVE
                                RedisStorage.persistence_instance().store_data(current_key, **data)
                                job_data = {
                                    'cluster': cluster,
                                    'template': data['template'],
                                    'userID': data['userID'],
                                    'algoID': data['algoID'],
                                    'cluster_id': key
                                }
                                worker.run_job(self._cluster_match_process.job,
                                               callback=self._cluster_match_process.handler, **job_data)
                            else:
                                if data['step'] == 5:
                                    template_key = REDIS_TEMPLATE_RESULT % data['userID']
                                    final_data = dict()
                                    ended = 0
                                    if RedisStorage.persistence_instance().exists(template_key):
                                        final_data = ast.literal_eval(
                                            RedisStorage.persistence_instance().get_data(template_key))
                                        RedisStorage.persistence_instance().delete_data(template_key)
                                        ended = final_data['ended']
                                    else:
                                        final_data['userID'] = data['userID']
                                        final_data['algoID'] = data['algoID']
                                    if final_data.get(str(key), None) is None:
                                        final_data['ended'] = ended + 1
                                        final_data[str(key)] = data['template']
                                        key_list = final_data.get('clusters_list', [])
                                        key_list.append(str(key))
                                        final_data['clusters_list'] = key_list
                                        if final_data['ended'] == 6:
                                            self._final_process.process(final_data)
                                        else:
                                            RedisStorage.persistence_instance().store_data(template_key, **final_data)
                                else:
                                    RedisStorage.persistence_instance().store_data(current_key, **data)
                        else:
                            logger.algo_logger.info(ERROR_FORMAT % (INTERNAL_TRAINING_ERROR, UNKNOWN_ERROR))
                    else:
                        data = {
                            'template': cluster,
                            'status': JOB_STATUS_FINISHED,
                            'userID': res_data['userID'],
                            'algoID': res_data['algoID'],
                            'step': 1
                        }
                        RedisStorage.persistence_instance().store_data(key=current_key, **data)

    def job(self, callback_code, **kwargs):
        self._job_logger_info(**kwargs)
        record = self.process(**kwargs)
        BaseDataStore.instance().store_job_result(record_key=REDIS_DO_NOT_STORE_RESULT_KEY % callback_code,
                                                  record_dict=record, callback_code=callback_code)

    def process(self, **kwargs):
        self._process_logger_info(**kwargs)
        source = load_temp_data(kwargs['data_file'], remove=False)
        settings = get_settings(source['algoID'])
        logger.debug(settings)
        logger.debug(loadSettings(settings['kodsettings']))
        kodsettings = KODSettings()
        print loadSettings(settings['kodsettings'])
        kodsettings.importSettings(loadSettings(settings['kodsettings'])['KODSettings'])
        detector = FeatureDetector(constructDetector(kodsettings.detector_type, kodsettings.settings))

        # try:
        obj = detector.detectAndCompute(source['roi'])
        source['keypoints'] = obj['keypoints']
        source['descriptors'] = obj['descriptors']
        if source['descriptors'] is None:
            source['descriptors'] = []
        record = self._detect_process(source, detector, self._temp_data_path)
        # except Exception as err:
        #     logger.debug(err.message)
        #     record = create_error_message(INTERNAL_TRAINING_ERROR, 'data', err.message)
        return record

    def _detect_process(self, data, detector, path):
        eyeROI = CascadesDetectionInterface(loadScript("main_haarcascade_eyes_union.json", True))
        rect = eyeROI.detect(data['roi'])[1]
        if len(rect) <= 0 or len(rect[0]) <= 0:
            logger.algo_logger.info("Eye ROI wasn't found.")
            return create_error_message(INTERNAL_TRAINING_ERROR, "data", "Eye ROI wasn't found.", data['userID'])
        # ROI cutting
        rect = rect[0]
        lefteye = (rect[0] + rect[3], rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3], rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[1] - lefteye[1]) / 2)
        centernose = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, rect[1] + 2 * rect[3])
        centermouth = (centernose[0], centernose[1] + rect[3])
        leftmouth = (lefteye[0], centermouth[1])
        rightmouth = (righteye[0], centermouth[1])
        centers = [lefteye, righteye, centereye, centernose, leftmouth, rightmouth]
        self._filter_keypoints(data)

        clusters = KMeans(data['keypoints'], 0, centers)
        data['true_clusters'] = clusters
        descriptors = dict()
        active_clusters = 0
        for index, cluster in enumerate(clusters):
            desc = detector.compute(data['roi'], cluster['items'])
            curr_cluster = desc['descriptors']
            if curr_cluster is not None:
                descriptors[str(index)] = (numpy_ndarrayToList(curr_cluster)
                                           if type(curr_cluster) != list else curr_cluster)
            else:
                descriptors[str(index)] = []
            if curr_cluster is not None and len(curr_cluster) > 0:
                active_clusters += 1
        data['clusters'] = descriptors
        if active_clusters < len(centers) - 2:
            logger.info("Number of clusters are insufficient for the recognition.")
            return create_error_message(INTERNAL_TRAINING_ERROR, "clusters",
                                        "Number of clusters are insufficient for the recognition.", data['userID'])
        data.pop("keypoints", None)
        data.pop("true_clusters", None)
        data["descriptors"] = numpy_ndarrayToList(data["descriptors"])
        matching_process_data = save_temp_data(data, path, ['data', 'roi'])
        return create_result_message([{'data_file': matching_process_data}], 'matching')

    def _filter_keypoints(self, data):
        clusters = FOREL(data['keypoints'], 20)
        keypoints = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            if p > 0.02:
                keypoints += [item for item in cluster['items']]
        data['keypoints'] = keypoints
