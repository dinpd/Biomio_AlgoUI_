"""
Module: algorithms.imgobj
Description of structure for saving image and different image data

 imgobj = dict()
    imgobj['name']        - name of image file;
    imgobj['path']        - path to image file;
    imgobj['data']        - numpy.ndarray image object;
    imgobj['keypoints']   - list of keypoints object = list<KeyPoint>;
    imgobj['descriptors'] - list of descriptors vectors;
"""
from cvtools.system import loadNumpyImage
import os


def loadImageObject(path):
    """
        Loads image by path and return basic image dict object.

    :param path: Absolute path to the image file
    :return: Image dict object instance.
    """
    if os.path.exists(path):
        data = {
            'name': os.path.split(path)[1],
            'path': path,
            'data': loadNumpyImage(path)}
        return data
    return None
