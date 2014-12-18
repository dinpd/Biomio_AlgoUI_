"""
Tools Module
Implementation of functions for basic processing of images based on OpenCV.
"""

import cv2
import numpy
from matplotlib import pyplot as plt


def loadImage(filename):
    """
    Tools
    Wrapper for OpenCV cv2.cv.LoadImage(filename, iscolor=None) function.

    :param filename: Name of the image file (string)
    :return: IplImage image file.
    """
    img = cv2.cv.LoadImage(filename, cv2.CV_LOAD_IMAGE_COLOR)
    return img


def showImage(image, title=""):
    """
    Tools
    Wrapper for OpenCV cv2.cv.ShowImage(name, image) function.

    :param image: IplImage image file.
    :param title: Title for image window.
    """
    cv2.cv.ShowImage(title, image)
    cv2.waitKey()


def grayscale(image):
    """
    Tools
    Function for getting grayscale image.

    :param image: numpy.ndarray image.
    :return: numpy.ndarray grayscale image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def equalizeHist(image):
    """
    Tools
    Function for getting grayscale image with equalized histogram.

    :param image: numpy.ndarray image.
    :return: numpy.ndarray grayscale equalized image.
    """
    return cv2.equalizeHist(image)


def saveImage(filename, image):
    """
    Tools
    Wrapper for OpenCV imwrite(filename, img, params=None) function.

    :param filename: Name of saving image file.
    :param image: numpy.ndarray image.
    """
    print cv2.imwrite(filename, image)


def drawImage(image):
    """
    Tools
    Simple wrapper for matplotlib.pyplot.imshow(...) function.

    :param image: numpy.ndarray image.
    """
    plt.imshow(image)
    plt.show()

def saveKeypoints(filename, features):
    """
    Tools
    Simple wrapper for save image with keypoints.

    :param filename: Name of saving image file.
    :param features: Image features container.
    """
    out = cv2.drawKeypoints(features.image(), features.keypoints())
    print cv2.imwrite(filename, out)


def drawKeypoints(features):
    """
    Tools
    Simple wrapper for OpenCV cv2.drawKeypoints(...) function.

    :param features: Image features container.
    """
    out = cv2.drawKeypoints(features.image(), features.keypoints())
    plt.imshow(out)
    plt.show()


def paintKeypoints(features):
    """
    Tools
    Simple wrapper for OpenCV cv2.drawKeypoints(...) function.

    :param features: Image features container.
    :return: numpy.ndarray image with image keypoints.
    """
    return cv2.drawKeypoints(features.image(), features.keypoints())


def keypointsToArrays(keypoints):
    arrays = []
    for keypoint in keypoints:
        arrays.append(classKeyPointToArray(keypoint))
    return arrays


def classKeyPointToArray(keypoint):
    darray = []
    darray.append(keypoint.pt[0])
    darray.append(keypoint.pt[1])
    darray.append(keypoint.size)
    darray.append(keypoint.angle)
    darray.append(keypoint.response)
    darray.append(keypoint.octave)
    return numpy.array(darray)