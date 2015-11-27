"""
Open CV Tools Module
Implementation of functions for basic processing of images based on OpenCV.
"""
import logger
import cv2


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


def joinVectors(vector_list):
    if vector_list is not None:
        gen_vec = []
        for el in vector_list:
            for item in el:
                gen_vec.append(item)
        return gen_vec
    return None


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
        # logger.logger.debug(keys)
        # logger.logger.debug(keypoints)
        return keypoints
    return None


def minimizeSort(feature):
    if feature is not None:
        keys = []
        for keypoint in feature.keypoints():
            if len(keys) == 0:
                keys.append(keypoint)
            else:
                i = 0
                for tkey in keys:
                    mark = False
                    for j in range(0, len(keypoint), 1):
                        if tkey[j] < keypoint[j]:
                            mark = True
                            i += 1
                            break
                    if not mark:
                        break
                keys.insert(i, keypoint)
        logger.logger.debug(keys)
        return keys
    return None


def distance(x1, y1, x2, y2):
    return pow((pow(x1 - x2, 2) + pow(y1 - y2, 2)), 0.5)