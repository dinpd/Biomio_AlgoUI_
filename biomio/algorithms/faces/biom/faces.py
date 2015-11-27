import os
import sys
import threading

import cv2.cv as cv
import cv2
import numpy as np

from logger import logger
from algorithms.cascades.classifiers import CascadeClassifierSettings
from biomio.algorithms.faces.biom import utils

IMAGE_DIR = "faces/data/images"


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class BaseModel(SingletonMixin):
    MODEL_FILE = "model.mdl"

    def __init__(self, model=None):
        self.__model = model
        self.__model_loaded = False
        self.__labels = []
        self.__load_labels()
        if not self.__load_model():
            self.train()

    def __load_model(self):
        if os.path.isfile(self.MODEL_FILE):
            self.__model.load(self.MODEL_FILE)
            self.__model_loaded = True
        else:
            self.__model_loaded = False
        return self.__model_loaded

    def __load_labels(self):
        self.__labels = zip(*utils.label_list())

    def __load_images(self):
        images = []
        person = []
        for i, label in enumerate(self.__labels[0]):
            dirpath = os.path.join(IMAGE_DIR, str(label))
            for filename in os.listdir(dirpath):
                path = os.path.join(dirpath, filename)
                try:
                    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    img = cv2.resize(img, (100, 100))
                    images.append(np.asarray(img, dtype=np.uint8))
                    person.append(i)
                    logging.info("Image %s loaded" % path)
                except IOError, (errno, strerror):
                    logging.error("{0}: IOError({1}): {2}".format(path, errno, strerror))
                except:
                    logging.error("{0}: Unexpected error: {1}".format(path, sys.exc_info()[0]))
        return [images, person]

    def train(self):
        images = self.__load_images()
        self.__model.train(images[0], np.array(images[1])) #np.array(self.__labels[0]))
        self.__model.save(self.MODEL_FILE)
        self.__model_loaded = True

    def predict(self, faces):
        prediction = self.__model.predict(faces)
        f = self.__labels[0]
        return (f[prediction[0]], prediction[1])

    def is_model_loaded(self):
        return self.__model_loaded


class FisherModel(BaseModel):
    def __init__(self):
        super(FisherModel, self).__init__(cv2.createFisherFaceRecognizer())


class BaseFaces(object):
    classifierSettings = CascadeClassifierSettings()

    def __init__(self, model=None):
        self.__model = model
        self.__cascades = []

    def add_cascade(self, path):
        if os.path.exists(path):
            self.__cascades.append(cv2.CascadeClassifier(path))
            logger.debug("Cascade is loaded.")
        else:
            logger.debug("Such file does not exist.")

    def model_loaded(self):
        return self.__model.is_model_loaded()

    def train(self):
        self.__model.train()

    def predict(self, img):
        faces = self.detect(img)
        if len(faces) == 0:
            return None

        cropped = utils.grayscaleAndEqualize(self.crop_faces(img, faces))
        resized = cv2.resize(cropped, (100, 100))
        return (faces[0],) + self.__model.predict(resized)

    def detect(self, img):
        rects = list()
        gray = utils.grayscaleAndEqualize(img)
        if len(self.__cascades) == 0:
            logger.debug("Detection impossible. Any cascade not found.")
            return rects
        for cascade in self.__cascades:
            lrects = cascade.detectMultiScale(
                gray,
                scaleFactor=self.classifierSettings.scaleFactor,
                minNeighbors=self.classifierSettings.minNeighbors,
                minSize=self.classifierSettings.minSize,
                flags=cv.CV_HAAR_SCALE_IMAGE)
            # if len(lrects) != 0:
            #     lrects[:,2:] += lrects[:,:2]
            for r in lrects:
                rects.append(r)
        if len(rects) == 0:
            return []
        return rects

    def contains_face(self, img):
        return len(self.detect(img)) > 0

    def crop_faces(self, img, faces):
        for face in faces:
            x, y, h, w = [result for result in face]
        return img[y:y+h,x:x+w]


class FisherFaces(BaseFaces):
    def __init__(self):
        super(FisherFaces, self).__init__(FisherModel.instance())


def faces_persist(label, images, add=False):
    bf = BaseFaces()
    dirpath = os.path.join(IMAGE_DIR, label)

    def save(img):
        faces = bf.detect(img)
        if len(faces) == 0:
            return
        path = os.path.join(dirpath, "%d.png" % label_count(label))
        path = os.path.abspath(path)
        logger.info("Saving %s" % path)
        cropped = utils.grayscaleAndEqualize(bf.crop_faces(img, faces))
        cv2.imwrite(path, cropped)

    if not add:
        label_remove(label)
        label_add(label)
    map(save, images)


def load_test(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (100, 100))
    # plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
    # plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    # plt.show()
    return img