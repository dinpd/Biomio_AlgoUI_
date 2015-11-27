from rectsect import intersectRectangles
from rectfilter import filterRectangles
from rectmerge import mergeRectangles
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CASCADES_PATH = os.path.join(APP_ROOT, "..", "data", "haarcascades")
SCRIPTS_PATH = os.path.join(APP_ROOT, "scripts")
