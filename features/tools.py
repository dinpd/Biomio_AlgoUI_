"""
Tools Module
Implementation of functions for basic processing of images based on OpenCV.
"""

import cv2
import numpy
import logger
from matplotlib import pyplot as plt


def getROIImage(image, rectangle):
    """
    Tools
    Cut rectangle ROI (Region of Image) on the image.

    :param image: numpy.ndarray image.
    :param rectangle: list[x, y, width, height]
    :return: numpy.ndarray ROI image.
    """
    im = numpy_darrayToIplImage(image)
    cv2.cv.SetImageROI(im, (rectangle[0], rectangle[1], rectangle[2], rectangle[3]))
    out = cv2.cv.CreateImage(cv2.cv.GetSize(im),
                             im.depth,
                             im.nChannels)
    cv2.cv.Copy(im, out)
    cv2.cv.ResetImageROI(out)

    return iplImageToNumpy_darray(out)


def numpy_darrayToIplImage(source):
    bitmap = cv2.cv.CreateImageHeader((source.shape[1], source.shape[0]), cv2.cv.IPL_DEPTH_8U, 3)
    cv2.cv.SetData(bitmap, source.tostring(), source.dtype.itemsize * 3 * source.shape[1])
    return bitmap


def iplImageToNumpy_darray(source):
    return numpy.asarray(source[:,:])


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
    Function for getting grayscale image with equalized histogram
    from input grayscale image.

    :param image: numpy.ndarray grayscale image.
    :return: numpy.ndarray grayscale equalized image.
    """
    return cv2.equalizeHist(image)


def readImage(filename):
    """
    Tools
    Wrapper for OpenCV imread(filename, flags=None) function.

    :param filename: Name of the image file (string)
    :return: numpy.ndarray image.
    """
    return cv2.imread(filename, cv2.CV_LOAD_IMAGE_COLOR)


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


def paintLines(image, order_list, color):
    dimg = image.copy()
    i = 0
    while i < len(order_list) - 1:
        key_one = order_list[i]
        key_two = order_list[i + 1]
        cv2.line(dimg, (int(key_one.pt[0]), int(key_one.pt[1])),
                 (int(key_two.pt[0]), int(key_two.pt[1])), color, 1)
        i += 1
    return dimg


def keypointsToArrays(keypoints):
    arrays = []
    for keypoint in keypoints:
        arrays.append(classKeyPointToArray(keypoint))
    return arrays


def classKeyPointToArray(keypoint):
    darray = []
    # darray.append(keypoint.pt[0])
    # darray.append(keypoint.pt[1])
    darray.append(keypoint.size)
    darray.append(keypoint.angle)
    darray.append(keypoint.response)
    darray.append(keypoint.octave)
    return numpy.array(darray)


def spiralSort(feature, width, height):
    if feature is not None:
        mid_x = width / 2.0
        mid_y = height / 2.0
        keys = []
        keypoints = []
        for keypoint in feature.keypoints():
            dis = distance(mid_x, mid_y, keypoint.pt[0], keypoint.pt[1])
            if len(keys) == 0:
                keys.append(dis)
                keypoints.append(keypoint)
            else:
                i = len(keys) - 1
                mark = False
                while i >= 0:
                    if keys[i] < dis:
                        keys.insert(i + 1, dis)
                        keypoints.insert(i + 1, keypoint)
                        mark = True
                        i = -1
                    i -= 1
                if not mark:
                    keys.insert(0, dis)
                    keypoints.insert(0, keypoint)
        logger.logger.debug(keys)
        logger.logger.debug(keypoints)
        return keypoints
    return None


def distance(x1, y1, x2, y2):
    return pow((pow(x1 - x2, 2) + pow(y1 - y2, 2)), 0.5)