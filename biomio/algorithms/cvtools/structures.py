import numpy
import cv2


def pointPolygonTest(point, pts, measureDist=False):
    return cv2.pointPolygonTest(numpy.array(pts, numpy.int32), point, measureDist=measureDist)
