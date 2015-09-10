from algorithms.cascades.classifiers import (CascadeROIDetector, RectsUnion, RectsFiltering,
                                             CascadeClassifierSettings)
from algorithms.cascades.detectors import ROIDetectorInterface
from algorithms.cascades.scripts_detectors import RotatedCascadesDetector
from algorithms.cascades.rectmerge import mergeRectangles
from algorithms.cascades.tools import getROIImage, loadScript
import logging
import cv2
import os

logger = logging.getLogger(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CASCADES_PATH = os.path.join(APP_ROOT, "..", "data", "haarcascades")
SCRIPTS_PATH = os.path.join(APP_ROOT, "scripts")

class OptimalROIDetector(ROIDetectorInterface):
    def __init__(self):
        ROIDetectorInterface.__init__(self)
        self._d = 100

        self._face_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.minNeighbors = 1
        settings.minSize = (100, 100)
        self._face_classifier.classifierSettings = settings
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt_tree.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt2.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_default.xml"))

        self._eyes_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.scaleFactor = 1.2
        self._eyes_classifier.classifierSettings = settings
        self._eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_eye_tree_eyeglasses.xml"))
        self._eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_lefteye_2splits.xml"))
        self._eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_eyepair_big.xml"))
        self._eyes_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_eyepair_small.xml"))

        self._nose_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.scaleFactor = 1.5
        settings.minNeighbors = 5
        self._nose_classifier.classifierSettings = settings
        self._nose_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_nose.xml"))

        self._mouth_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.scaleFactor = 3.0
        settings.minNeighbors = 15
        self._mouth_classifier.classifierSettings = settings
        self._mouth_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_mcs_mouth.xml"))

    def detect(self, data):
        new_images = []
        for obj in data:
            img, rects = self._face_classifier.detectAndJoinWithRotation(obj['data'], False, RectsFiltering)
            if len(rects) <= 0:
                logger.debug("optimalROIDetection: Face doesn't found on image %s" % obj['name'])
                continue
            obj['data'] = img
            new_images.append(obj)
        images = new_images
        for obj in images:
            logger.debug(obj['path'])
            image = obj['data']
            lrects = self._eyes_classifier.detectAndJoin(image, False, RectsUnion)
            obj['eyes'] = lrects
            lrects = self._nose_classifier.detectAndJoin(image, False, RectsUnion)
            obj['nose'] = lrects
            lrects = self._mouth_classifier.detectAndJoin(image, False, RectsFiltering)
            obj['mouth'] = lrects
            temp = image[self._d:image.shape[0] - self._d, self._d:image.shape[1] - self._d]
            res = cv2.minMaxLoc(cv2.matchTemplate(images[0]['data'], temp, cv2.cv.CV_TM_CCORR_NORMED))
            obj['displacement'] = (self._d - res[3][0], self._d - res[3][1])

        rects = []
        for image in images:
            di = image['displacement']
            if len(image['eyes']) == 4:
                rects.append([image['eyes'][0] - di[0], image['eyes'][1] - di[1], image['eyes'][2], image['eyes'][3]])
            if len(image['nose']) == 4:
                rects.append([image['nose'][0] - di[0], image['nose'][1] - di[1], image['nose'][2], image['nose'][3]])
            if len(image['mouth']) == 4:
                rects.append([image['mouth'][0] - di[0], image['mouth'][1] - di[1],
                              image['mouth'][2], image['mouth'][3]])
        optimal_rect = mergeRectangles(rects)
        if len(optimal_rect) == 4:
            if 1.5 * optimal_rect[2] > optimal_rect[3]:
                diff = 1.5 * optimal_rect[2] - optimal_rect[3]
                optimal_rect[1] -= int(0.3 * diff)
                optimal_rect[3] += int(0.7 * diff)
            for image in images:
                di = image['displacement']
                res_roi = [optimal_rect[0] + di[0], optimal_rect[1] + di[1], optimal_rect[2], optimal_rect[3]]
                image['data'] = getROIImage(image['data'], res_roi)
        else:
            new_images = []
            for image in images:
                rects = self._face_classifier.detectAndJoin(image['data'], False, RectsFiltering)
                if len(rects) <= 0:
                    continue
                image['data'] = getROIImage(image['data'], rects)
                new_images.append(image)
            images = new_images
        return images


class OptimalROIDetectorSAoS(ROIDetectorInterface):
    def __init__(self):
        ROIDetectorInterface.__init__(self)
        self._d = 100

        self._face_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.minNeighbors = 1
        settings.minSize = (100, 100)
        self._face_classifier.classifierSettings = settings
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt_tree.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt2.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_default.xml"))

        self._detector = RotatedCascadesDetector(loadScript(os.path.join(SCRIPTS_PATH,
                                                                         "main_rotation_haarcascade_face_eyes.json")),
                                                 loadScript(os.path.join(SCRIPTS_PATH,
                                                                         "main_haarcascade_face_size.json")))

    def detect(self, data):
        new_images = []
        for obj in data:
            img, rects = self._detector.detect(obj['data'])
            if len(rects) <= 0:
                logger.debug("optimalROIDetection: Face doesn't found on image %s" % obj['name'])
                continue
            obj['data'] = img
            obj['roi_rect'] = rects
            new_images.append(obj)
        images = new_images
        for obj in images:
            image = obj['data']
            temp = image[self._d:image.shape[0] - self._d, self._d:image.shape[1] - self._d]
            res = cv2.minMaxLoc(cv2.matchTemplate(images[0]['data'], temp, cv2.cv.CV_TM_CCORR_NORMED))
            obj['displacement'] = (self._d - res[3][0], self._d - res[3][1])

        rects = []
        for image in images:
            di = image['displacement']
            for rec in image['roi_rect']:
                if len(rec) == 4:
                    rects.append([rec[0] - di[0], rec[1] - di[1], rec[2], rec[3]])
        optimal_rect = mergeRectangles(rects)
        if len(optimal_rect) == 4:
            if 1.3 * optimal_rect[2] > optimal_rect[3]:
                diff = 1.3 * optimal_rect[2] - optimal_rect[3]
                optimal_rect[1] -= int(0.3 * diff)
                optimal_rect[3] += int(0.7 * diff)
            for image in images:
                di = image['displacement']
                res_roi = [optimal_rect[0] + di[0], optimal_rect[1] + di[1], optimal_rect[2], optimal_rect[3]]
                image['data'] = getROIImage(image['data'], res_roi)
        else:
            new_images = []
            for image in images:
                rects = self._face_classifier.detectAndJoin(image['data'], False, RectsFiltering)
                if len(rects) <= 0:
                    continue
                image['data'] = getROIImage(image['data'], rects)
                new_images.append(image)
            images = new_images
        return images


class FaceSAoSDetector(ROIDetectorInterface):
    def __init__(self):
        ROIDetectorInterface.__init__(self)

        self._face_classifier = CascadeROIDetector()
        settings = CascadeClassifierSettings()
        settings.minNeighbors = 1
        settings.minSize = (100, 100)
        self._face_classifier.classifierSettings = settings
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt_tree.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_alt2.xml"))
        self._face_classifier.add_cascade(os.path.join(CASCADES_PATH, "haarcascade_frontalface_default.xml"))

        self._detector = RotatedCascadesDetector(loadScript(os.path.join(SCRIPTS_PATH,
                                                                         "main_rotation_haarcascade_face_eyes.json")),
                                                 loadScript(os.path.join(SCRIPTS_PATH, "main_haarcascade_face.json")))

    def detect(self, data):
        pass
