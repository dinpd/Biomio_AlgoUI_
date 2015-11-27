"""
Open CV Tools Module
Implementation of functions for basic processing of images based on OpenCV.
"""
from types import (listToNumpy_ndarray, numpy_ndarrayToList,
                   iplImageToNumpy_darray, numpy_darrayToIplImage, classKeyPointToArray)
from system import loadIplImage, loadNumpyImage, saveNumpyImage, saveKeypoints
from effects import equalizeHist, grayscale, grayscaleAndEqualize
