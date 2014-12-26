import os
import sys
import logger
import shutil
import cv2
from features.tools import readImage

IMAGE_DIR = "faces/data/images"


def grayscaleAndEqualize(image):
    """
    Utils
    Function for getting grayscale image with equalized histogram.

    :param image: numpy.ndarray image.
    :return: numpy.ndarray grayscale equalized image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def read_file(path):
    if os.path.exists(path):
        data = {
            'name': os.path.split(path)[1],
            'path': path,
            'data': readImage(path)}
        return data
    return None


def label_list(dir=IMAGE_DIR):
    l = os.listdir(dir)
    n = map(lambda x: len(os.listdir(os.path.join(dir, x))), l)
    return zip(l,n)


def files_list(dir=IMAGE_DIR):
    files = []
    for x in [dir + "/" + d for d in os.listdir(dir)]:
        logger.logger.debug(x)
        for y in os.listdir(x):
            files.append(x + "/" + y)
    return files


def label_count(label):
    return len(os.listdir(os.path.join(IMAGE_DIR, x)))


def label_add(label):
    os.mkdir(os.path.join(IMAGE_DIR, label))


def label_remove(label):
    shutil.rmtree(os.path.join(IMAGE_DIR, label), True)

