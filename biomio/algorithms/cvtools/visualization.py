"""
OpenCV Tools
Visualization Module
Implementation of functions for image drawing and visualization based on OpenCV.

 Types of methods:
    show - show image or some elements on image;
    draw - draw some object or objects on image and return image object;
"""
from biomio.algorithms.logger import logger
import scipy as sp
import random
import numpy
import cv2


def showIplImage(image, title=""):
    """
    OpenCV Tools/Visualization Module
        Shows IplImage file using OpenCV cv2.cv.ShowImage(name, image) function.

    :param image: IplImage image file
    :param title: Title for image window
    """
    cv2.cv.ShowImage(title, image)
    cv2.waitKey()


def showNumpyImage(image):
    """
    OpenCV Tools/Visualization Module
        Shows numpy.ndarray image object using matplotlib.pyplot.imshow(...) function.

    :param image: numpy.ndarray image object
    """
    cv2.imshow("image", image)
    cv2.waitKey()


def printKeyPoint(keypoint):
    if keypoint is not None:
        logger.debug(keypoint)
        logger.debug("angle=%s" % str(keypoint.angle))
        logger.debug("class_id=%s" % str(keypoint.class_id))
        logger.debug("octave=%s" % str(keypoint.octave))
        logger.debug("point=%s" % str(keypoint.pt))
        logger.debug("response=%s" % str(keypoint.response))
        logger.debug("size=%s" % str(keypoint.size))


def showKeypoints(imgobj):
    """
    OpenCV Tools/Visualization Module
        Shows list of keypoints on the image using OpenCV cv2.drawKeypoints(...) function.

    :param imgobj: image object. For details see algorithms.imgobj
    """
    out = cv2.drawKeypoints(imgobj['data'], imgobj['keypoints'])
    cv2.imshow("Keypoints Window", out)
    cv2.waitKey()


def drawKeypoints(imgobj, key='data'):
    """
    OpenCV Tools/Visualization Module
        Draws list of keypoints on the image using OpenCV cv2.drawKeypoints(...) function.

    :param imgobj: image object. For details see algorithms.imgobj
    :return: numpy.ndarray image with painted image keypoints
    """
    return cv2.drawKeypoints(imgobj[key], imgobj['keypoints'])


def showClusters(clusters, image):
    """
    OpenCV Tools/Visualization Module
        Shows keypoints cluster on image based on OpenCV cv2.drawKeypoints(...)
    function.

    Type definition: cluster = dict()
        cluster['center'] = tuple(x1,x2) - center of cluster
        cluster['items'] = list<KeyPoint> - list of cluster's items

    :param clusters: list of clusters
    :param image: numpy.ndarray image object
    """
    out = drawClusters(clusters, image)
    cv2.imshow("Clusters Window", out)
    cv2.waitKey()


def drawClusters(clusters, image):
    """
    OpenCV Tools/Visualization Module
        Draws keypoints cluster on image based on OpenCV cv2.drawKeypoints(...)
    function.

    Type definition: cluster = dict()
        cluster['center'] = tuple(x1,x2) - center of cluster
        cluster['items'] = list<KeyPoint> - list of cluster's items

    :param clusters: list of clusters
    :param image: numpy.ndarray image object
    :return: numpy.ndarray image object
    """
    out = image.copy()
    for cluster in clusters:
        out = cv2.drawKeypoints(out, cluster['items'], None,
                                cv2.cv.Scalar(random.randint(0, 255),
                                              random.randint(0, 255),
                                              random.randint(0, 255)))
    return out


def showMatches(imgobj1, imgobj2, matches, key='data'):
    """
    OpenCV Tools/Visualization Module
        Shows descriptor matches on two matched images.

    :param imgobj1: first image object. For details see algorithms.imgobj
    :param imgobj2: second image object. For details see algorithms.imgobj
    :param matches: list of matches
    :param key: image object key for image data
    """
    view = drawMatches(imgobj1, imgobj2, matches, key)
    cv2.imshow("view", view)
    cv2.waitKey()


def drawMatches(imgobj1, imgobj2, matches, key='data'):
    """
    OpenCV Tools/Visualization Module
        Draws descriptor matches on two matched images.

    :param imgobj1: first image object. For details see algorithms.imgobj
    :param imgobj2: second image object. For details see algorithms.imgobj
    :param matches: list of matches
    :param key: image object key for image data
    :return: numpy.ndarray image object
    """
    h1, w1 = imgobj1[key].shape[:2]
    h2, w2 = imgobj2[key].shape[:2]
    view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    view[:h1, :w1] = imgobj1[key]
    view[:h2, w1:] = imgobj2[key]
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    for knn in matches:
        for match in knn:
            color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
            cv2.line(view, (int(imgobj1['keypoints'][match.queryIdx].pt[0]),
                            int(imgobj1['keypoints'][match.queryIdx].pt[1])),
                     (int(imgobj2['keypoints'][match.trainIdx].pt[0] + w1),
                      int(imgobj2['keypoints'][match.trainIdx].pt[1] + h1)), color)
    return view


def printMatches(imgobj1, imgobj2, matches):
    """
    OpenCV Tools/Visualization Module
        Prints descriptor matches on two matched images.

    :param imgobj1: first image object. For details see algorithms.imgobj
    :param imgobj2: second image object. For details see algorithms.imgobj
    :param matches: list of matches
    """
    for knn in matches:
        for match in knn:
            print "=================="
            print "(" + str(int(imgobj1['keypoints'][match.queryIdx].pt[0])) + ", " + \
                  str(int(imgobj1['keypoints'][match.queryIdx].pt[1])) + ") (" + \
                  str(int(imgobj2['keypoints'][match.trainIdx].pt[0])) + ", " + \
                  str(int(imgobj2['keypoints'][match.trainIdx].pt[1])) + ") :" + str(match.distance)
            dx = int(imgobj1['keypoints'][match.queryIdx].pt[0]) - int(imgobj2['keypoints'][match.trainIdx].pt[0])
            dy = int(imgobj1['keypoints'][match.queryIdx].pt[1]) - int(imgobj2['keypoints'][match.trainIdx].pt[1])
            print dx
            print dy
            print pow(pow(dx, 2) + pow(dy, 2), 0.5)
            print "=================="

def drawSelfMatches(imgobj, matches, key='data'):
    """
    OpenCV Tools/Visualization Module
        Draws descriptor self-matches on the image.

    :param imgobj: image object. For details see algorithms.imgobj
    :param matches: list of match pair (descriptor, descriptor, distance)
    :param key: image object key for image data
    :return: numpy.ndarray image object
    """
    res = imgobj[key].copy()
    for match in matches:
        color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
        f_index = -1
        s_index = -1
        for index, desc in enumerate(imgobj['descriptors']):
            if numpy.array_equal(desc, match[0]):
                f_index = index
            if numpy.array_equal(desc, match[1]):
                s_index = index
            if f_index >= 0 and s_index >= 0:
                break
        if f_index >= 0 and s_index >= 0:
            cv2.line(res, (int(imgobj['keypoints'][f_index].pt[0]), int(imgobj['keypoints'][f_index].pt[1])),
                     (int(imgobj['keypoints'][s_index].pt[0]), int(imgobj['keypoints'][s_index].pt[1])), color)
    return res


def drawSelfGraph(imgobj, edges, key='data'):
    """
    OpenCV Tools/Visualization Module
        Draws keypoints-based self-graph on the image.

    :param imgobj: image object. For details see algorithms.imgobj
    :param matches: list of match pair (descriptor, descriptor, distance)
    :param key: image object key for image data
    :return: numpy.ndarray image object
    """
    res = imgobj[key].copy()
    for edge in edges:
        color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
        cv2.line(res, (int(edge[0].pt[0]), int(edge[0].pt[1])), (int(edge[2].pt[0]), int(edge[2].pt[1])), color)
    return res


def drawRectangle(image, rect, color):
    """
    OpenCV Tools/Visualization Module
        Draws rectangle on image object with color borders.

    :param image: numpy.ndarray image object
    :param rect: rectangle = [x, y, width, height]
    :param color: scalar color = (r, g, b)
    :return: numpy.ndarray image object
    """
    img = image.copy()
    cv2.rectangle(img, (rect[0], rect[1]),
                  (rect[0] + rect[2], rect[1] + rect[3]),
                  color, 1)
    return img


def drawLine(image, line, color):
    """
    OpenCV Tools/Visualization Module
        Draws line object with color on the image object.

    :param image: numpy.ndarray image object
    :param line: line list [x1, y1, x2, y2]
    :param color: scalar color = (r, g, b)
    :return: numpy.ndarray image object
    """
    img = image.copy()
    cv2.line(img, (line[0], line[1]), (line[2], line[3]), color, 1)
    return img


def drawCircle(image, center, radius, color):
    img = image.copy()
    cv2.circle(img, center, radius, color)
    return img
