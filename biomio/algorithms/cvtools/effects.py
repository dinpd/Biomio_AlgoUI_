"""
OpenCV Tools
Effects Module
Implementation of functions for image processing based on OpenCV.
"""
import cv2


def grayscale(image):
    """
    OpenCV Tools/Effects Module
        Returns grayscale image object converted using cvtColor(...)
    transformation.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray grayscale image object
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def equalizeHist(image):
    """
    OpenCV Tools/Effects Module
        Returns grayscale image with equalized histogram converted
    from input grayscale image object.

    :param image: numpy.ndarray grayscale image object
    :return: numpy.ndarray grayscale equalized image
    """
    return cv2.equalizeHist(image)


def grayscaleAndEqualize(image):
    """
    OpenCV Tools/Effects Module
        Returns grayscale image with equalized histogram.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray grayscale equalized image object
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def binarization(image):
    """
    OpenCV Tools/Effects Module
        Returns the binary image converted from input image object.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray binary image object
    """
    res, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    return binary


def gaussianBlurring(image, kernel=(5, 5)):
    """
    OpenCV Tools/Effects Module
        Blur the image using GaussianBlur function.

    :param image: numpy.ndarray image object
    :param kernel: tuple object which represent size of filter kernel
    :return: numpy.ndarray image object
    """
    return cv2.GaussianBlur(image, kernel, 0)


def rotate90(image):
    """
    OpenCV Tools/Effects Module
        Rotates the image 90 degrees counterclockwise.

    :param image: numpy.ndarray image object
    :return: numpy.ndarray image object
    """
    rows = image.shape[0]
    cols = image.shape[1]
    M = cv2.getRotationMatrix2D((cols/2.0 - 0.5, cols/2.0 - 0.5), 90, 1)
    img = cv2.warpAffine(image, M, (rows, cols))
    return img


INTER_NEAREST = cv2.INTER_NEAREST   # a nearest-neighbor interpolation.
INTER_LINEAR = cv2.INTER_LINEAR     # a bilinear interpolation (used by default).
INTER_AREA = cv2.INTER_AREA         # resampling using pixel area relation. It may be a preferred method
                                    # for image decimation, as it gives moire-free results. But when the
                                    # image is zoomed, it is similar to the INTER_NEAREST method.
INTER_CUBIC = cv2.INTER_CUBIC       # a bicubic interpolation over 4x4 pixel neighborhood.
INTER_LANCZOS4 = cv2.INTER_LANCZOS4 # a Lanczos interpolation over 8x8 pixel neighborhood.


def resize(image, dsize=None, fx=None, fy=None, interpolation=INTER_CUBIC):
    if dsize is None:
        return cv2.resize(image, (0, 0), fx=fx, fy=fy, interpolation=interpolation)
    else:
        return cv2.resize(image, dsize=dsize, interpolation=interpolation)
