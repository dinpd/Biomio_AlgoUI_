"""
OpenCV Tools
Types Module
Implementation of functions for basic type conversion based on OpenCV.
"""
import numpy
import cv2


def numpy_darrayToIplImage(source):
    """
    OpenCV Tools/Types Module
        Convert numpy.ndarray object to IplImage object.

    :param source: numpy.ndarray object
    :return: IplImage object
    """
    bitmap = cv2.cv.CreateImageHeader((source.shape[1], source.shape[0]), cv2.cv.IPL_DEPTH_8U, 3)
    cv2.cv.SetData(bitmap, source.tostring(), source.dtype.itemsize * 3 * source.shape[1])
    return bitmap


def iplImageToNumpy_darray(source):
    """
    OpenCV Tools/Types Module
        Convert IplImage object to numpy.ndarray object.

    :param source: IplImage object
    :return: numpy.ndarray object
    """
    return numpy.asarray(source[:, :])


def numpy_ndarrayToList(source):
    """
    OpenCV Tools/Types Module
        Convert numpy.ndarray object to list object.

    :param source: numpy.ndarray object
    :return: list object
    """
    return source.tolist()


def listToNumpy_ndarray(source, dtype=None):
    """
    OpenCV Tools/Types Module
        Convert list object to numpy.ndarray object.

    :param source: list object
    :return: numpy.ndarray object
    """
    return numpy.array(source, dtype=dtype)


def classKeyPointToArray(keypoint, with_points=False):
    """
    OpenCV Tools/Types Module
        Convert KeyPoint Class to numpy.ndarray object.
    If with_points is True, method include coordinates of keypoint
    into output array, otherwise returns array without them.

    :param keypoint: KeyPoint OpenCV object
    :param with_points: bool flag
    :return: numpy.ndarray object
    """
    darray = []
    if with_points:
        darray.append(keypoint.pt[0])
        darray.append(keypoint.pt[1])
    darray.append(keypoint.size)
    darray.append(keypoint.angle)
    darray.append(keypoint.response)
    darray.append(keypoint.octave)
    return numpy.array(darray)


def arrayToKeyPointClass(array, with_points=False):
    """
    OpenCV Tools/Types Module
        Convert numpy.ndarray object to KeyPoint Class.
    If with_points is True, method include coordinates of keypoint
    into output array, otherwise returns array without them.

    :param array: numpy.ndarray object
    :param with_points: bool flag
    :return: KeyPoint OpenCV object
    """
    x = array[0]
    y = array[1]
    if not with_points:
        x = 0
        y = 0
    return cv2.KeyPoint(x, y, array[2], array[3], array[4], int(array[5]))


def copyKeyPoint(keypoint):
    """
    OpenCV Tools/Types Module
        Copy KeyPoint object and return copy.

    :param keypoint: KeyPoint object instance
    :return: KeyPoint object instance
    """
    return cv2.KeyPoint(keypoint.pt[0], keypoint.pt[1],
                        keypoint.size, keypoint.angle,
                        keypoint.response, keypoint.octave,
                        keypoint.class_id)
