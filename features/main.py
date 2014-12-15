#!/usr/bin/env python2.7

import tools
from detectors import ImageFeatures, FeatureDetector, ComplexDetector

def main():
    cdetector = ComplexDetector()
    cobj = cdetector.detect("data/external/palm.png")
    FeatureDetector.drawKeypoints(cobj)
    FeatureDetector.saveKeypoints("data/external/palm_EqGaborORBBased.png", cobj)
    tools.saveImage("data/external/palm_Eq.png", cobj.image())

    detector = FeatureDetector()
    obj = detector.detectAndCompute("data/external/palm.png")
    FeatureDetector.drawKeypoints(obj)
    FeatureDetector.saveKeypoints("data/external/palm_ORB.png", obj)
    scn = detector.detectAndCompute("data/test_scene.jpg")
    detector.drawKeypoints(scn)
    detector.match(obj, scn)
    pass


if __name__ == '__main__':
    main()