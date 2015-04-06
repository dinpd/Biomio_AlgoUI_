import logging
from gui_logger import QtHandler

logging.basicConfig(
    format='%(levelname)-8s [%(asctime)s] %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sys_logger = logging.getLogger("algorithms.full")
sys_logger.setLevel(logging.DEBUG)

handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)-1s" + '\t' + " [%(asctime)s]" + '\t' + " %(message)s"))
logger.addHandler(handler)
sys_logger.addHandler(handler)

file_handler = logging.FileHandler("D:/Projects/Biomio/algoui/basic_log.txt")
file_handler.setFormatter(logging.Formatter("%(levelname)-1s" + '\t' + " [%(asctime)s]" + '\t' + " %(message)s"))
logger.addHandler(file_handler)

ext_handler = logging.FileHandler("D:/Projects/Biomio/algoui/ext_log.txt")
ext_handler.setFormatter(logging.Formatter("%(levelname)-1s" + '\t' + " [%(asctime)s]" + '\t' + " %(message)s"))
logger.addHandler(ext_handler)
sys_logger.addHandler(ext_handler)