from structs.tools import get_dirs, get_files
from corealgorithms.flows import IAlgorithm
import os


class DatabaseReader(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is not None:
            path = data.get('path', None)
            if os.path.exists(path):
                db_data = {}
                labels_dirs = get_dirs(path)
                for label in labels_dirs:
                    label_data = {}
                    subdir = os.path.join(path, label)
                    files_list = get_files(subdir)
                    for file_name in files_list:
                        label_data[os.path.join(subdir, file_name)] = None
                    db_data[label] = label_data
                data['data'] = db_data
        return data
