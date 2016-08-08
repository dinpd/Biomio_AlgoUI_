from biomio.algorithms.cvtools.types import numpy_darrayToIplImage, iplImageToNumpy_darray
from biomio.algorithms.cascades import SCRIPTS_PATH
import json
import cv2
import os


def getROIImage(image, rectangle):
    """
    Cut rectangle ROI (Region of Image) on the image.

    :param image: numpy.ndarray image.
    :param rectangle: list[x, y, width, height]
    :return: numpy.ndarray ROI image.
    """
    if len(rectangle) != 4:
        return image
    im = numpy_darrayToIplImage(image)
    cv2.cv.SetImageROI(im, (rectangle[0], rectangle[1], rectangle[2], rectangle[3]))
    out = cv2.cv.CreateImage(cv2.cv.GetSize(im), im.depth, im.nChannels)
    cv2.cv.Copy(im, out)
    cv2.cv.ResetImageROI(out)
    return iplImageToNumpy_darray(out)


def isRectangle(rect):
    return len(rect) == 4


def inside(test, template, ds=0):
    dx = ds * template[2]
    dy = ds * template[3]
    if (template[0] - dx > test[0]) or (template[1] - dy > test[1]):
        return False
    if template[0] + template[2] + dx < test[0] + test[2]:
        return False
    if template[1] + template[3] + dy < test[1] + test[3]:
        return False
    return True


def skipEmptyRectangles(rects):
    new_rects = []
    for rect in rects:
        if len(rect) == 4:
            new_rects.append(rect)
    return new_rects


def loadScript(file_name, relative=False):
    abs_file = file_name
    if relative:
        abs_file = os.path.join(SCRIPTS_PATH, file_name)
    if os.path.exists(abs_file):
        with open(abs_file, "r") as data_file:
            source = json.load(data_file)
            if source.get('name', None) is None:
                source['name'] = os.path.basename(abs_file)
            if source["type"] == "main":
                stages = source["action"]
                loaded_stages = []
                for sub in stages:
                    if type(sub) == type(dict()):
                        loaded_stages.append(sub)
                    else:
                        if os.path.exists(sub):
                            loaded_stages.append(loadScript(sub))
                        else:
                            head = os.path.split(abs_file)[0]
                            path = os.path.join(head, sub)
                            if os.path.exists(path):
                                loaded_stages.append(loadScript(path))
                source["action"] = loaded_stages
            return source
    return dict()
