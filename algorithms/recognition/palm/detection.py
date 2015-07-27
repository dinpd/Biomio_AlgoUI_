import random
import math

import numpy as np
import cv2

from algorithms.cvtools.types import listToNumpy_ndarray
from algorithms.features.gabor_threads import build_filters, process_kernel
from algorithms.cvtools.effects import grayscale, binarization
from algorithms.cascades.classifiers import CascadeROIDetector, RectsFiltering
from logger import logger


def getPalmContourClassic(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray = image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh1 = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # thresh1 = gray

    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            ci = i
    cnt = contours[ci]
    center, radius = getContourInnerRegion(cnt)
    hull = cv2.convexHull(cnt)
    moments = cv2.moments(cnt)
    if moments['m00'] != 0:
        cx = int(moments['m10']/moments['m00']) # cx = M10/M00
        cy = int(moments['m01']/moments['m00']) # cy = M01/M00
    centr = (cx, cy)

    points = list()
    for i in range(len(contours)):
        for point in contours[i]:
            points.append(point)

    drawing = np.zeros(image.shape, np.uint8)
    cv2.circle(image, centr, 5, [0, 0, 255], 2)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 2)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 2)
    cv2.circle(drawing, (int(center[0]), int(center[1])), int(radius), (255, 255, 255), 2)
    for i in range(len(contours)):
        for point in contours[i]:
            cv2.circle(drawing, (point[0][0], point[0][1]), 3, (255, 0, 0))
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


def getContourInnerRegion(contour):
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
                w = float(w) / pow(1.21, 0.5)
                x = center_point[0] - w / 2.0
                h = float(h) / pow(1.21, 0.5)
                y = center_point[1] - h / 2.0
                if w < 1 or h < 1:
                    break
            dist = 0
            for i in range(0, 1000):
                p = (random.uniform(x, w), random.uniform(y, h))
                r = cv2.cv.PointPolygonTest(cv2.cv.fromarray(contour), p, True)
                if r > 0 and dist < r:
                    dist = r
                    max_point = p
            max_dist = dist
        return center_point, center_dist
    return 0, 0


def getPalmContourHaar(image):
    cascade_detector = CascadeROIDetector()
    cascade_detector.add_cascade("algorithms/data/haarcascades/haarcascade-hand.xml")
    cascade_detector.add_cascade("algorithms/data/haarcascades/haarcascade_palm.xml")
    img, rect = cascade_detector.detectAndJoinWithRotation(image, False, RectsFiltering)
    gabor = build_filters()
    images = list()
    for i in range(0, len(gabor), 1):
        logger.debug("Applying Gabor Filter. Kernel No. " + str(i))
        images.append(cv2.threshold(process_kernel(image, gabor[i]), 5, 255, 0)[1])
    if rect is None:
        h, w = image.shape[0], image.shape[1]
    else:
        h, w = rect[1] + rect[3] / 2, rect[0] + rect[2] / 2
    result = images[0]
    for j in range(0, h, 1):
        for i in range(0, w, 1):
            b = 0
            g = 0
            r = 0
            for img in images:
                pixel = img[j, i]
                b += pixel[0]
                g += pixel[1]
                r += pixel[2]
            result[j, i] = [b / len(images), g / len(images), r / len(images)]

    result = cv2.threshold(result, 200, 255, 0)[1]
    gray = grayscale(result)
    binary = binarization(gray)

    points = []
    R = 400
    imcenter = (w / 2, h / 2)
    maxLength = max(w, h)
    for angle in range(0, 360, 1):
        y2 = imcenter[1] - R * math.sin((angle * math.pi) / 180.0)
        x2 = imcenter[0] + R * math.cos((angle * math.pi) / 180.0)
        dx = x2 - imcenter[0] + 0.001
        dy = y2 - imcenter[1]
        next_points = []
        last = None
        for r in range(0, maxLength, 1):
            if angle == 90 or angle == 270:
                xi = imcenter[0]
                yi = imcenter[1] - r * math.sin((angle * math.pi) / 180.0)
            else:
                xi = imcenter[0] + r * math.cos((angle * math.pi) / 180.0)
                yi = (dy / dx) * (xi - imcenter[0]) + imcenter[1]
            xi = int(xi)
            yi = int(yi)
            if 0 < xi < w and 0 < yi < h:
                last = (xi, yi)
                if binary[yi, xi] != 255:
                    next_points.append((xi, yi))
        if len(next_points) == 0:
            next_points.append(last)
        points.append(next_points)
    contour = [listToNumpy_ndarray([listToNumpy_ndarray([group[0][0], group[0][1]])]) for group in points]
    contour.append(listToNumpy_ndarray([listToNumpy_ndarray([contour[0][0][0], contour[0][0][1]])]))
    prev = None
    for point in contour:
        if prev is None:
            prev = point
        else:
            cv2.line(binary, (prev[0][0], prev[0][1]), (point[0][0], point[0][1]), (120, 120, 120), 2)
            prev = point

    center, radius = getContourInnerRegion(listToNumpy_ndarray(contour))
    cv2.circle(binary, (int(center[0]), int(center[1])), int(radius), (50, 50, 50), 2)
    return binary
