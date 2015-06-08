from algorithms.clustering.forel import FOREL
from algorithms.cvtools.visualization import showNumpyImage
import numpy as np
import random
import cv2
import sys


def palm_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray = cv2.equalizeHist(gray)
    # gray = image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh1 = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # thresh1 = gray

    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(image.shape, np.uint8)
    max_area = 0
    eps = 5
    cntr = list()
    last = None
    # file = open("D:/Projects/Biomio/images/realpalm/contours.txt", "w")
    for i in range(len(contours)):
        for point in contours[i]:
            # file.write(str(point))
            if last is None:
                last = point
            else:
                if abs(last[0][0] - point[0][0]) > eps and abs(last[0][1] - point[0][1]) > eps:
                    cntr.append(point)
                    last = point
        # file.write("\n")
    # file.close()

    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            ci = i
    cnt = contours[ci]
    center, radius = inside_contours(cnt)
    hull = cv2.convexHull(cnt)
    moments = cv2.moments(cnt)
    if moments['m00'] != 0:
        cx = int(moments['m10']/moments['m00']) # cx = M10/M00
        cy = int(moments['m01']/moments['m00']) # cy = M01/M00

    points = list()
    for i in range(len(contours)):
        for point in contours[i]:
            points.append(point)

    def gpoint(element):
        return element[0][0], element[0][1]
    # clusters = FOREL(points, 5, gpoint)

    centr = (cx, cy)
    cv2.circle(image, centr, 5, [0, 0, 255], 2)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 2)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 2)
    cv2.circle(drawing, (int(center[0]), int(center[1])), int(radius), (255, 255, 255), 2)
    poi = None
    draws = list()
    r = min(drawing.shape[0], drawing.shape[1]) / 10
    for p in hull:
        if poi is None:
            poi = p
        else:
            if abs(poi[0][0] - p[0][0]) < r and abs(poi[0][1] - p[0][1]) < r:
                poi = p
                continue
            stats = False
            for d in draws:
                if abs(d[0][0] - p[0][0]) < r and abs(d[0][1] - p[0][1]) < r:
                    stats = True
            if stats:
                continue
            poi = p
        if pow((center[0] - p[0][0])**2 + (center[1] - p[0][1])**2, 0.5) > 2 * radius:
            draws.append(p)
            cv2.line(drawing, (int(center[0]), int(center[1])), (p[0][0], p[0][1]), (255, 255, 255), 2)
    for i in range(len(contours)):
        for point in contours[i]:
            cv2.circle(drawing, (point[0][0], point[0][1]), 3, (255, 0, 0))

    cnt = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
    hull = cv2.convexHull(cnt, returnPoints=False)

    if 1:
        defects = cv2.convexityDefects(cnt, hull)
        mind = 0
        maxd = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            dist = cv2.pointPolygonTest(cnt, centr, True)
            cv2.line(image, start, end, [0, 255, 0], 2)
            cv2.circle(image, far, 5, [0, 0, 255], -1)
        i=0

    return drawing


def inside_contours(contour):
    if contour is not None:
        x,y,w,h = cv2.boundingRect(contour)
        center_point = (0, 0)
        center_dist = 0
        max_point = None
        max_dist = 0
        while center_point != max_point:
            if max_point is not None:
                if center_dist < max_dist:
                    center_point = max_point
                    center_dist = max_dist
                w = float(w) / pow(2, 0.5)
                x = center_point[0] - w / 2.0
                h = float(h) / pow(2, 0.5)
                y = center_point[1] - h / 2.0
                if w < 1 or h < 1:
                    break
            dist = 0
            for i in range(0, 100):
                p = (random.uniform(x, w), random.uniform(y, h))
                r = cv2.cv.PointPolygonTest(cv2.cv.fromarray(contour), p, True)
                if r > 0 and dist < r:
                    dist = r
                    max_point = p
            max_dist = dist
        return center_point, center_dist
    return 0, 0