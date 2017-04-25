import logging

logging.basicConfig(
    format='%(levelname)-8s [%(asctime)s] %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)