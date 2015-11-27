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
import os

from biomio.algorithms.cvtools.system import loadNumpyImage


def loadImageObject(path):
    if os.path.exists(path):
        data = {
            'name': os.path.split(path)[1],
            'path': path,
            'data': loadNumpyImage(path)}
        return data
    return None

