from tools import get_files, get_dirs
import cv2
import os


class ImageContainer:
    def __init__(self, filepath, isread=False):
        self._filepath = None
        self._isread = None
        self._image = None
        self._attributes = {}
        self.read(filepath, isread)

    def valid(self):
        return self._image is not None or os.path.exists(self._filepath)

    def path(self):
        return self._filepath

    def image(self):
        if not self._isread:
            return self.read_image(self._filepath)
        return self._image

    def attribute(self, key, value=None):
        if value is None:
            return self._attributes.get(key, None)
        self._attributes[key] = value

    def read(self, filepath, isread=False):
        if os.path.exists(filepath):
            self._filepath = filepath
            self._isread = isread
            if self._isread == True:
                self._image = self.read_image(self._filepath)

    @staticmethod
    def read_image(path):
        return cv2.imread(path)

    def __str__(self):
        return "ImageContainer({})[{}, {}]".format(self._filepath, 'valid' if self.valid() else 'invalid',
                                                   'read' if self._isread else 'not read')


class ImageDirectory:
    def __init__(self, dirpath, isread=False):
        self._images = []
        self._dir = None
        self.read(dirpath, isread)

    def empty(self):
        return len(self._images) <= 0

    def add(self, image):
        if image is not None:
            self._images.append(image)

    def image(self, index):
        if index < len(self._images):
            return self._images[index]
        raise Exception("index out of range")

    def images(self):
        return self._images

    def count(self):
        return len(self._images)

    def read(self, dirpath, isread=False):
        if os.path.exists(dirpath):
            self._dir = dirpath
            files = get_files(dirpath)
            for rel_file in files:
                full_path = os.path.join(dirpath, rel_file)
                img = ImageContainer(full_path, isread)
                if img.valid():
                    self._images.append(img)

    def __str__(self):
        return "ImageDirectory({}): {} images.".format(self._dir, len(self._images))


class RawImagesStruct:
    def __init__(self, path=None, isread=False):
        self._dirs = []
        self._path = None
        self.read(path, isread)

    def empty(self):
        return len(self._dirs) <= 0

    def add(self, directory):
        if directory is not None:
            self._dirs.append(directory)

    def directory(self, index):
        if index < len(self._dirs):
            return self._dirs[index]
        raise Exception("index out of range")

    def directories(self):
        return self._dirs

    def count(self):
        return len(self._dirs)

    def read(self, path, isread=False):
        if os.path.exists(path):
            self._path = path
            dirs = get_dirs(path)
            for rel_dir in dirs:
                full_path = os.path.join(path, rel_dir)
                img_dir = ImageDirectory(full_path, isread)
                if not img_dir.empty():
                    self._dirs.append(img_dir)

    def __str__(self):
        return "RawImagesStruct({}): {} directories.".format(self._path, len(self._dirs))
