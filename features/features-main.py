#!/usr/bin/env python2.7

import tools
from detectors import FeatureDetector, ComplexDetector
from hashing.hash_test import lshash_test, nearpy_test


def main():
    # cdetector = ComplexDetector()
    # cobj = cdetector.detect("data/external/palm.png")
    # tools.drawKeypoints(cobj)
    # tools.saveKeypoints("data/external/palm_EqGaborORBBased.png", cobj)
    # tools.saveImage("data/external/palm_Eq.png", cobj.image())

    detector = FeatureDetector()
    obj = detector.detectAndCompute("data/external/palm.png")
    tools.drawKeypoints(obj)
    key_arrays = tools.keypointsToArrays(obj.keypoints())
    # Two hash tests for face regions
    lshash_test(key_arrays, [801.0, 1664.0, 31.0, 166.5230255126953, 0, 0])
    nearpy_test(key_arrays, [801.0, 1664.0, 31.0, 166.5230255126953, 0, 0])

    # tools.saveKeypoints("data/external/palm_ORB.png", obj)
    # scn = detector.detectAndCompute("data/test_scene.jpg")
    # tools.drawKeypoints(scn)
    # detector.match(obj, scn)
    pass


if __name__ == '__main__':
    main()