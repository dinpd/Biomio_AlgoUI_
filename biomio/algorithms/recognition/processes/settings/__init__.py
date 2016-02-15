import json
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_DIR = os.path.join(APP_ROOT, 'detectors')

def loadSettings(settings_file):
    settings_path = os.path.join(SETTINGS_DIR, settings_file)
    if not os.path.exists(settings_path):
        return dict()
    with open(settings_path, "r") as data_file:
        source = json.load(data_file)
        return source
