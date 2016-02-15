from defs import STATUS_ERROR, STATUS_RESULT

def create_error_message(message_type, param, message, userID=None):
    return create_message(STATUS_ERROR, message_type, param=param, message=message, userID=userID)


def create_result_message(result, result_type=None):
    return {
        'status': STATUS_RESULT,
        'type': result_type,
        'data': result
    }


def create_message(status, message_type, **kwargs):
    record = {
        'status': status,
        'type': message_type,
    }
    if len(kwargs.keys()) > 0:
        record['details'] = kwargs
    return record
