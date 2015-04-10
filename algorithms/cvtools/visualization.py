"""
Open CV Tools
Visualization Module
Implementation of functions for image drawing and visualization based on OpenCV.

 Types of methods:
    show - show image or some elements on image;
    draw - draw some object or objects on image and return image object;
"""
from matplotlib import pyplot as plt
import scipy as sp
import random
import cv2


def showIplImage(image, title=""):
    """
    Open CV Tools/Visualization Module
    Wrapper for OpenCV cv2.cv.ShowImage(name, image) function.

    :param image: IplImage image file
    :param title: Title for image window
    """
    cv2.cv.ShowImage(title, image)
    cv2.waitKey()


def showNumpyImage(image):
    """
    Open CV Tools/Visualization Module
    Simple wrapper for matplotlib.pyplot.imshow(...) function.

    :param image: numpy.ndarray image object
    """
    plt.imshow(image)
    plt.show()


def showKeypoints(imgobj):
    """
    Open CV Tools/Visualization Module
    Simple wrapper for OpenCV cv2.drawKeypoints(...) function.

    :param imgobj: image object. For details see algorithms.imgobj
    """
    out = cv2.drawKeypoints(imgobj['data'], imgobj['keypoints'])
    plt.imshow(out)
    plt.show()


def showClusters(clusters, image):
    """
    Open CV Tools/Visualization Module
    Functionality for drawing keypoints cluster on image based on
     OpenCV cv2.drawKeypoints(...) function.

     Type definition: cluster = dict()
         cluster['center'] = tuple(x1,x2) - center of cluster
         cluster['items'] = list<KeyPoint> - list of cluster's items

    :param clusters: list of clusters
    """
    out = image
    for cluster in clusters:
        out = cv2.drawKeypoints(out, cluster['items'], None,
                                cv2.cv.Scalar(random.randint(0, 255),
                                              random.randint(0, 255),
                                              random.randint(0, 255)))
    # plt.imshow(out)
    # plt.show()
    cv2.imshow("Clusters Window", out)
    cv2.waitKey()


def showMatches(imgobj1, imgobj2, matches, key='data'):
    h1, w1 = imgobj1[key].shape[:2]
    h2, w2 = imgobj2[key].shape[:2]
    view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    view[:h1, :w1] = imgobj1[key]
    view[:h2, w1:] = imgobj2[key]
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    for knn in matches:
        for match in knn:
            # print m.queryIdx, m.trainIdx, m.distance
            color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
            print "=================="
            print color
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
            cv2.line(view, (int(imgobj1['keypoints'][match.queryIdx].pt[0]),
                            int(imgobj1['keypoints'][match.queryIdx].pt[1])),
                     (int(imgobj2['keypoints'][match.trainIdx].pt[0] + w1),
                      int(imgobj2['keypoints'][match.trainIdx].pt[1])), color)
    # plt.imshow(view)
    # plt.show()
    cv2.imshow("view", view)
    cv2.waitKey()


def drawRectangle(image, rect, color):
    """
    Open CV Tools/Visualization Module
    Draw rectangle <rect> on <image> with <color> borders.

    :param image: numpy.ndarray image object
    :param rect: rectangle = [x, y, width, height]
    :param color: Scalar color = (r, g, b)
    """
    img = image.copy()
    cv2.rectangle(img, (rect[0], rect[1]),
                  (rect[0] + rect[2], rect[1] + rect[3]),
                  color, 1)
    return img


def drawKeypoints(imgobj):
    """
    Open CV Tools/Visualization Module
    Simple wrapper for OpenCV cv2.drawKeypoints(...) function.

    :param features: image object
    :return: numpy.ndarray image with image keypoints
    """
    return cv2.drawKeypoints(imgobj['data'], imgobj['keypoints'])


def drawLine(image, line, color):
    img = image.copy()
    cv2.line(img, (line[0], line[1]), (line[2], line[3]), color, 1)
    return img


def drawClusters(clusters, image):
    """
    Open CV Tools/Visualization Module
    Functionality for drawing keypoints cluster on image based on
     OpenCV cv2.drawKeypoints(...) function.

     Type definition: cluster = dict()
         cluster['center'] = tuple(x1,x2) - center of cluster
         cluster['items'] = list<KeyPoint> - list of cluster's items

    :param clusters: list of clusters
    """
    out = image
    for cluster in clusters:
        out = cv2.drawKeypoints(out, cluster['items'], None,
                                cv2.cv.Scalar(random.randint(0, 255),
                                              random.randint(0, 255),
                                              random.randint(0, 255)))
    return out


def drawMatches(imgobj1, imgobj2, matches):
    h1, w1 = imgobj1['data'].shape[:2]
    h2, w2 = imgobj2['data'].shape[:2]
    view = sp.zeros((h1 + h2, w1 + w2, 3), sp.uint8)
    view[:h1, :w1, 3] = imgobj1['data']
    view[h1:, w1:, 3] = imgobj2['data']
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    for knn in matches:
        for match in knn:
            # print m.queryIdx, m.trainIdx, m.distance
            color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
            cv2.line(view, (int(imgobj1['keypoints'][match.queryIdx].pt[0]),
                            int(imgobj1['keypoints'][match.queryIdx].pt[1])),
                     (int(imgobj2['keypoints'][match.trainIdx].pt[0] + w1),
                      int(imgobj2['keypoints'][match.trainIdx].pt[1] + h1)), color)
    return view