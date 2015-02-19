import cv2

# Detector types
BRISKDetectorType = 'BRISK'
ORBDetectorType = 'ORB'


class BaseDetector:
    def __init__(self, detector):
        self._detector = detector

    def detect(self, image, mask=None):
        return self._detector.detect(image, mask)

    def detectAndCompute(self, image, mask=None):
        return self._detector.detectAndCompute(image, mask)

    def compute(self, image, keypoints):
        return self._detector.compute(image, keypoints)

    @staticmethod
    def extractor():
        """
        Supported formats:
        enum
            cv2.descriptorExtractorType
                'BRISK'
                'ORB'
        """
        pass


class BRISKDetectorSettings:
    thresh = 10
    octaves = 0
    patternScale = 1.0


class BRISKDetector(BaseDetector):
    def __init__(self, thresh=10, octaves=0, scale=1.0):
        BaseDetector.__init__(self, cv2.BRISK(thresh=thresh, octaves=octaves, patternScale=scale))

    @staticmethod
    def extractor():
        return cv2.DescriptorExtractor_create('BRISK')


class ORBDetectorSettings:
    features = 500
    scaleFactor = 1.1
    nlevels = 8


class ORBDetector(BaseDetector):
    def __init__(self, features=500, scale=1.2, levels=8):
        BaseDetector.__init__(self, cv2.ORB(nfeatures=features, scaleFactor=scale, nlevels=levels))

    @staticmethod
    def extractor():
        return cv2.DescriptorExtractor_create('ORB')