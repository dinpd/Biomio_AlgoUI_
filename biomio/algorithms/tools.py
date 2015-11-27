import json
import os


def loadJSONFile(file_name):
        if os.path.exists(file_name):
            with open(file_name, "r") as data_file:
                source = json.load(data_file)
                return source
        return dict()
