import json
import os

def load_json(path):
    """
        Loads json object by path.

    :param path: Absolute path to the json text file.
    :return: json dict instance,
    """
    if not os.path.exists(path):
        return dict()
    with open(path, "r") as data_file:
        source = json.load(data_file)
        return source

def save_json(path, data):
    """
        Save json into text file.

    :param path: Absolute path to the json text file.
    :param data: dict object with json serializable data.
    :return: success status.
    """
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
    return True
