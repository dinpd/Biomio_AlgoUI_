import logging
from gui_logger import QtHandler

logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)-1s" + '\t' + " [%(asctime)s]" + '\t' + " %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)