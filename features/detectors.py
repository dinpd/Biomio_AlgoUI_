# General Modules
import cv2
import numpy
from matplotlib import pyplot as plt

# Own Modules
import defines
import tools
import gabor_threads as gfilter


class ImageFeatures:
    """
    A container for storing the original image, keypoints and descriptors.
    """
    def __init__(self):
        """
        Initialization of objects for data storage.
        """
        self._keypoints = None
        self._descriptors = None
        self._image = None

    def keypoints(self, value=None):
        """
        The combined get and set method for keypoints object.
        If the value is not equal to None, the method takes
        account data. If the value is None, the method returns the
        current contents of the keypoints object.

        :param value: keypoints array.
        :return: keypoints array.
        """
        if value is not None:
            self._keypoints = value
        return self._keypoints

    def descriptors(self, value=None):
        """
        The combined get and set method for descriptors object.
        If the value is not equal to None, the method takes
        account data. If the value is None, the method returns the
        current contents of the descriptors object.

        :param value: descriptors object.
        :return: descriptors object.
        """
        if value is not None:
            self._descriptors = value
        return self._descriptors

    def image(self, image=None):
        """
        The combined get and set method for image object.
        If the value is not equal to None, the method takes
        account data. If the value is None, the method returns the
        current contents of the image object.

        :param image: numpy.ndarray image object.
        :return: numpy.ndarray image object.
        """
        if image is not None:
            self._image = image
        return self._image


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


class BRISKDetector(BaseDetector):
    def __init__(self, thresh=10, octaves=0, scale=1.0):
        BaseDetector.__init__(self, cv2.BRISK(thresh=thresh, octaves=octaves, patternScale=scale))

    @staticmethod
    def extractor():
        return cv2.DescriptorExtractor_create('BRISK')


class ORBDetector(BaseDetector):
    def __init__(self, features=500, scale=1.2, levels=8):
        BaseDetector.__init__(self, cv2.ORB(nfeatures=features, scaleFactor=scale, nlevels=levels))

    @staticmethod
    def extractor():
        return cv2.DescriptorExtractor_create('ORB')


def MatcherCreator(descriptorMatcherType):
    """
    Function that create <DescriptorMatcher object> by the selected type.

    :param descriptorMatcherType: enum
        'BruteForce'            - Brute-force matcher (it uses L2)

        'BruteForce-L1'         - Brute-force matcher (it uses L1)
         L1 and L2 norms are preferable choices for SIFT and SURF descriptors.

        'BruteForce-Hamming'    - BruteForce-Hamming matcher should be used
        with ORB, BRISK and BRIEF.

        'BruteForce-Hamming(2)' - BruteForce-Hamming Second matcher should be
        used with ORB when WTA_K==3 or 4 (see ORB::ORB constructor
        description).

        'FlannBased'            - Flann-based matcher

        **********************************************************************
         Brute-force descriptor matcher. For each descriptor in the first set,
        this matcher finds the closest descriptor in the second set by trying
        each one. This descriptor matcher supports masking permissible matches
        of descriptor sets.
        **********************************************************************
         Flann-based descriptor matcher. This matcher trains flann::Index_ on
        a train descriptor collection and calls its nearest search methods to
        find the best matches. So, this matcher may be faster when matching a
        large train collection than the brute force matcher. FlannBasedMatcher
        does not support masking permissible matches of descriptor sets
        because flann::Index does not support this.
        **********************************************************************
    """
    return cv2.DescriptorMatcher_create(descriptorMatcherType)


def FlannMatcher():
    # index_params = dict(algorithm=defines.FLANN_INDEX_KDTREE,
    #                     trees=5)
    index_params = dict(algorithm=defines.FLANN_INDEX_LSH,
                        table_number=6,       # 12
                        key_size=12,          # 20
                        multi_probe_level=1)  # 2

    search_params = dict(checks=50)

    return cv2.FlannBasedMatcher(index_params, search_params)


class FeatureDetector:
    def __init__(self):
        self._detector = ORBDetector()
        self._extractor = ORBDetector.extractor()
        # self._matcher = MatcherCreator('BruteForce-Hamming')
        self._matcher = FlannMatcher() # MatcherCreator('FlannBased')

    def detect(self, filepath, maskpath=None):
        fea_image = ImageFeatures()

        img = cv2.imread(filepath, cv2.CV_LOAD_IMAGE_COLOR)
        if img is None:
            print "Couldn't find the object image with the provided path."
            sys.exit()
        fea_image.image(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = None
        if maskpath is not None:
            mask = cv2.imread(maskpath, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        keypoints = self._detector.detect(gray, mask)
        fea_image.keypoints(keypoints)
        return fea_image

    def detectAndCompute(self, filepath, maskpath=None):
        fea_image = ImageFeatures()

        img = cv2.imread(filepath, cv2.CV_LOAD_IMAGE_COLOR)
        if img is None:
            print "Couldn't find the object image with the provided path."
            sys.exit()
        fea_image.image(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = None
        if maskpath is not None:
            mask = cv2.imread(maskpath, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        keypoints = self._detector.detect(gray, mask)
        keypoints, descriptors = self._extractor.compute(gray, keypoints)
        fea_image.keypoints(keypoints)
        fea_image.descriptors(descriptors)
        return fea_image

    def match(self, obj_feature, scn_feature):
        matches = self._matcher.knnMatch(obj_feature.descriptors(),
                                         scn_feature.descriptors(), k=2)

        #Apply ratio test
        good = []
        for m, n in matches:
            print str(m.imgIdx) + " " + str(m.distance) + " " + str(n.imgIdx) + " " + str(n.distance)
            if m.distance < 0.75 * n.distance:
                good.append([m])
                print 'true'

        img1 = obj_feature.image()
        img2 = scn_feature.image()


class ComplexDetector:
    def __init__(self):
        self._detector = BRISKDetector()
        self._extractor = BRISKDetector.extractor()
        # self._matcher = MatcherCreator('BruteForce-Hamming')
        self._matcher = FlannMatcher() # MatcherCreator('FlannBased')

    def detect(self, filepath, maskpath=None):
        fea_image = ImageFeatures()

        rect = (100, 400, 1000, 1100)

        image = tools.loadImage(filepath)

        # roiImage = ComplexDetector.getROIImage(image, rect)
        roiImage = image

        convImage = numpy.asarray(roiImage[:,:])
        fea_image.image(convImage)

        grayImage = tools.grayscale(convImage)

        eqImage = cv2.equalizeHist(grayImage)
        fea_image.image(eqImage)

        gabor = gfilter.build_filters()
        gImage = gfilter.process(eqImage, gabor)
        # fea_image.image(gImage)
        i = 0
        for kern in gabor:
            fimg = gfilter.process_kernel(eqImage, kern)
            tools.saveImage(filepath + "_" + str(i) + ".png", fimg)
            i += 1

        mask = None
        if maskpath is not None:
            mask = cv2.imread(maskpath, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        keypoints = self._detector.detect(gImage, mask)
        fea_image.keypoints(keypoints)
        return fea_image

    @classmethod
    def getROIImage(cls, image, rectangle):
        im = image
        cv2.cv.SetImageROI(im, rectangle)
        out = cv2.cv.CreateImage(cv2.cv.GetSize(im),
                                 im.depth,
                                 im.nChannels)
        cv2.cv.Copy(im, out)
        cv2.cv.ResetImageROI(out)
        return out