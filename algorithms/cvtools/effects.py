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