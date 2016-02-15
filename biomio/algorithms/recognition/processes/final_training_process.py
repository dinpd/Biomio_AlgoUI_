from biomio.algorithms.interfaces import AlgorithmProcessInterface, logger

class FinalTrainingProcess(AlgorithmProcessInterface):
    def __init__(self):
        AlgorithmProcessInterface.__init__(self)
        self._classname = "FinalTrainingProcess"

    def handler(self, result):
        raise NotImplementedError

    def job(self, callback_code, **kwargs):
        raise NotImplementedError

    def process(self, **kwargs):
        self._process_logger_info(kwargs)
        data = kwargs["data"]
        sources = dict()
        for k in data['clusters_list']:
            sources[k] = data[k]
        res_record = {
            'status': "update",
            'algoID': data['algoID'],
            'userID': data['userID'],
            'database': sources
        }
        logger.info('Status::The database updated.')
        self._result_handler(res_record)

    @staticmethod
    def _result_handler(algo_result):
        ai_response_type = dict()
        probe_id = algo_result['userID']
        if isinstance(algo_result, dict) and algo_result.get('status', '') == "update":
            # record = dictionary:
            # key          value
            #      'status'     "update"
            #      'userID'     Unique user identificator
            #      'algoID'     Unique algorithm identificator
            #      'database'   BLOB data of user, with userID, for verification algorithm algoID
            #
            # Need update record in algorithms database or create record for user userID and algorithm
            # algoID if it doesn't exists
            database = algo_result.get('database', None)
            if database is not None:
                _store_training_db(database, probe_id)
                result = True
        elif isinstance(algo_result, list):
            for algo_result_item in algo_result:
                if algo_result_item.get('status', '') == "error":
                    worker_logger.exception('Error during education - %s, %s, %s' % (algo_result_item.get('status'),
                                                                                     algo_result_item.get('type'),
                                                                                     algo_result_item.get('details')))
                    ai_response_type.update({'status': 'error'})
                    if 'Internal Training Error' in algo_result_item.get('type', ''):
                        error = algo_result_item.get('details', {}).get('message', '')
                elif algo_result_item.get('status', '') == 'update':
                    database = algo_result_item.get('database', None)
                    if database is not None:
                        _store_training_db(database, probe_id)
            # record = dictionary:
            # key          value
            #      'status'     "error"
            #      'type'       Type of error
            #      'userID'     Unique user identificator
            #      'algoID'     Unique algorithm identificator
            #      'details'    Error details dictionary
            #
            # Algorithm can have three types of errors:
            #       "Algorithm settings are empty"
            #        in this case fields 'userID', 'algoID', 'details' are empty
            #       "Invalid algorithm settings"
            #        in this case 'details' dictionary has following structure:
            #               key         value
            #               'params'    Parameters key ('data')
            #               'message'   Error message (for example "File <path> doesn't exists")
            #       "Internal algorithm error"
            # Need save to redis
            pass
        elif algo_result.get('status', '') == "error":
            worker_logger.exception('Error during education - %s, %s, %s' % (algo_result.get('status'),
                                                                             algo_result.get('type'),
                                                                             algo_result.get('details')))
            ai_response_type.update({'status': 'error'})
            if 'Internal Training Error' in algo_result.get('type', ''):
                error = algo_result.get('details', {}).get('message', '')
            # record = dictionary:
            # key          value
            #      'status'     "error"
            #      'type'       Type of error
            #      'userID'     Unique user identificator
            #      'algoID'     Unique algorithm identificator
            #      'details'    Error details dictionary
            #
            # Algorithm can have three types of errors:
            #       "Algorithm settings are empty"
            #        in this case fields 'userID', 'algoID', 'details' are empty
            #       "Invalid algorithm settings"
            #        in this case 'details' dictionary has following structure:
            #               key         value
            #               'params'    Parameters key ('data')
            #               'message'   Error message (for example "File <path> doesn't exists")
            #       "Internal algorithm error"
            # Need save to redis
            pass
        worker_logger.info('training finished for user - %s, with result - %s' % (algo_result.get('userID'), result))

    @staticmethod
    def _store_training_db(database, probe_id):
        training_data = base64.b64encode(cPickle.dumps(database, cPickle.HIGHEST_PROTOCOL))
        try:
            MySQLDataStoreInterface.create_data(table_name=TRAINING_DATA_TABLE_CLASS_NAME, probe_id=probe_id,
                                                data=training_data)
        except Exception as e:
            if '1062 Duplicate entry' in str(e):
                worker_logger.info('Training data already exists, updating the record.')
                MySQLDataStoreInterface.update_data(table_name=TRAINING_DATA_TABLE_CLASS_NAME,
                                                    object_id=probe_id, data=training_data)
            else:
                worker_logger.exception(e)
