from distances import euclidean_distance
import math


def angleForPoint(center, point):
    radians = math.asin(euclidean_distance(point, (point[0], center[1])) /
                        (euclidean_distance(center, point) if euclidean_distance(center, point) > 0 else 1))
    angle = (180 * radians) / math.pi
    if point[0] < center[0]:
        if point[1] < center[1]:
            angle = 180 - angle
        else:
            angle += 180
    else:
        if point[1] > center[1]:
            angle = 360 - angle
    return angle
