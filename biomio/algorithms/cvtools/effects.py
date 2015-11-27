"""
Open CV Tools
Effects Module
Implementation of functions for image processing based on OpenCV.
"""
import cv2


def grayscale(image):
    """
    Open CV Tools/Effects Module
    Function for getting grayscale image object using cvtColor(...) transformation.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray grayscale image object
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def equalizeHist(image):
    """
    Open CV Tools/Effects Module
    Function for getting grayscale image with equalized histogram
     from input grayscale image object.

    :param image: numpy.ndarray grayscale image object
    :return: numpy.ndarray grayscale equalized image
    """
    return cv2.equalizeHist(image)


def grayscaleAndEqualize(image):
    """
    Open CV Tools/Effects Module
    Function for getting grayscale image with equalized histogram.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray grayscale equalized image object
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def binarization(image):
    res, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    return binary


def gaussianBlurring(image, kernel=(5, 5)):
    return cv2.GaussianBlur(image, kernel, 0)


def rotate90(image):
    rows = image.shape[0]
    cols = image.shape[1]
    M = cv2.getRotationMatrix2D((cols/2.0, cols/2.0), 90, 1)
    img = cv2.warpAffine(image, M, (rows, cols))
    return img
