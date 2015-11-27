"""
Open CV Tools
System Module
Implementation of functions for image loading and saving based on OpenCV.

 Types of methods:
    load - load image using file path in some type;
    save - save image object in file in some type;
"""
import cv2


def loadIplImage(filename):
    """
    Open CV Tools/System Module
    Wrapper for OpenCV cv2.cv.LoadImage(filename, iscolor=None) function.

    :param filename: Name of the image file (string)
    :return: IplImage image object
    """
    img = cv2.cv.LoadImage(filename, cv2.CV_LOAD_IMAGE_COLOR)
    return img


def loadNumpyImage(filename):
    """
    Open CV Tools/System Module
    Wrapper for OpenCV cv2.imread(filename, flags=None) function.

    :param filename: Name of the image file (string)
    :return: numpy.ndarray image object
    """
    return cv2.imread(filename, cv2.CV_LOAD_IMAGE_COLOR)


def saveNumpyImage(filename, image):
    """
    Open CV Tools/System Module
    Wrapper for OpenCV cv2.imwrite(filename, img, params=None) function.

    :param filename: Name of saving image file
    :param image: numpy.ndarray image object
    :return: status of save image (bool)
    """
    return cv2.imwrite(filename, image)


def saveKeypoints(filename, imgobj):
    """
    Open CV Tools/System Module
    Simple wrapper for save image with keypoints.

    :param filename: Name of saving image file
    :param imgobj: image object. For details see algorithms.imgobj
    :return: status of save image (bool)
    """
    out = cv2.drawKeypoints(imgobj['data'], imgobj['keypoints'])
    return cv2.imwrite(filename, out)