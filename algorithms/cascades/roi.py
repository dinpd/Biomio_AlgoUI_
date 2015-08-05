from algorithms.cascades.classifiers import (CascadeROIDetector, RectsUnion, RectsFiltering, getROIImage,
                                             CascadeClassifierSettings)
from algorithms.cascades.rectmerge import mergeRectangles
import logging
import cv2
import os

logger = logging.getLogger(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CASCADES_PATH = os.path.join(APP_ROOT, "..", "data", "haarcascades")

def optimalROIDetection(images):
    d = 100
    face_classifier = CascadeROIDetector()
    face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt.xml"))
    face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt_tree.xml"))
    face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt2.xml"))
    face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_default.xml"))
    eyes_classifier = CascadeROIDetector()
    settings = CascadeClassifierSettings()
    settings.scaleFactor = 1.2
    eyes_classifier.classifierSettings = settings
    # eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_eye.xml"))
    eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_eye_tree_eyeglasses.xml"))
    eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_lefteye_2splits.xml"))
    eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_eyepair_big.xml"))
    eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_eyepair_small.xml"))
    nose_classifier = CascadeROIDetector()
    settings = CascadeClassifierSettings()
    settings.scaleFactor = 1.5
    settings.minNeighbors = 5
    nose_classifier.classifierSettings = settings
    nose_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_nose.xml"))
    mouth_classifier = CascadeROIDetector()
    settings = CascadeClassifierSettings()
    settings.scaleFactor = 3.0
    settings.minNeighbors = 15
    mouth_classifier.classifierSettings = settings
    mouth_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_mouth.xml"))

    for obj in images:
        img, rects = face_classifier.detectAndJoinWithRotation(obj['data'], False, RectsFiltering)
        obj['data'] = img
    for obj in images:
        image = obj['data']
        lrects = eyes_classifier.detectAndJoin(image, False, RectsUnion)
        obj['eyes'] = lrects
        lrects = nose_classifier.detectAndJoin(image, False, RectsUnion)
        obj['nose'] = lrects
        lrects = mouth_classifier.detectAndJoin(image, False, RectsUnion)
        obj['mouth'] = lrects
        temp = image[d:image.shape[0] - d, d:image.shape[1] - d]
        res = cv2.minMaxLoc(cv2.matchTemplate(images[0]['data'], temp, cv2.cv.CV_TM_CCORR_NORMED))
        obj['displacement'] = (d - res[3][0], d - res[3][1])
        print "result", res

    rects = []
    for image in images:
        di = image['displacement']
        if len(image['eyes']) == 4:
            rects.append([image['eyes'][0] - di[0], image['eyes'][1] - di[1], image['eyes'][2], image['eyes'][3]])
        if len(image['nose']) == 4:
            rects.append([image['nose'][0] - di[0], image['nose'][1] - di[1], image['nose'][2], image['nose'][3]])
    optimal_rect = mergeRectangles(rects)
    if 1.5 * optimal_rect[2] > optimal_rect[3]:
        diff = 1.5 * optimal_rect[2] - optimal_rect[3]
        optimal_rect[1] -= int(0.3 * diff)
        optimal_rect[3] += int(0.7 * diff)
    for image in images:
        di = image['displacement']
        res_roi = [optimal_rect[0] + di[0], optimal_rect[1] + di[1], optimal_rect[2], optimal_rect[3]]
        image['data'] = getROIImage(image['data'], res_roi)
