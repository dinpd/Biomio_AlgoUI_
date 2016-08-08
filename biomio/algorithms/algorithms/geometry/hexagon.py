from distances import euclidean_distance
import numpy
import math
import cv2

HEXAGON_HORIZONTAL = 0
HEXAGON_VERTICAL = 1


def hexagon_grid(center, radius, size, orientation=HEXAGON_HORIZONTAL):
    centers = [center]
    next_level = [center]
    while len(next_level) > 0:
        curr = next_level[0]
        next_level.remove(curr)
        start = 0
        if orientation == HEXAGON_VERTICAL:
            start = 30
        new_centers = _get_hexagon_layer(curr, radius, start)
        for nc in new_centers:
            flag = True
            for c in centers:
                if euclidean_distance(c, nc) < radius:
                    flag = False
                    break
            if flag and euclidean_distance(center, nc) < size:
                centers.append(nc)
                next_level.append(nc)
    return centers


def hexagon_shape(center, radius, start=0):
    pts = []
    for inx in range(0, 6, 1):
        angle = ((60.0 * inx + start) * math.pi) / 180.0
        pts.append([int(center[0] + radius * math.cos(angle)), int(center[1] + radius * math.sin(angle))])
    return pts


def hexagon_segments(center, radius, start=0):
    pts = hexagon_shape(center, radius, start)
    segments = []
    for inx in range(0, 6, 1):
        end = inx + 1
        if inx == 5:
            end = 0
        segments.append([center, pts[inx], pts[end]])
    return segments


def pointHexagonTest(point, center, radius, start=0, measureDist=False):
    pts = hexagon_shape(center, radius, start)
    return cv2.pointPolygonTest(numpy.array(pts), point, measureDist=measureDist)


def _get_hexagon_layer(center, radius, start=0):
    height = radius * pow(3, 0.5) / 2.0
    centers = []
    for inx in range(0, 6, 1):
        angle = ((60.0 * inx + start) * math.pi) / 180.0
        next_cnt_x = center[0] + 2 * height * math.cos(angle)
        next_cnt_y = center[1] + 2 * height * math.sin(angle)
        centers.append((next_cnt_x, next_cnt_y))
    return centers
