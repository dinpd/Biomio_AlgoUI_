from structs import RawImagesStruct, ImageDirectory, ImageContainer
from server.biomio.algorithms.flows.base import LinearAlgorithmFlow
from tests.openface_verify_test import OpenFaceVerificationTest
from outputs import VerificationTableOutput, OutputConsolePrint
from tests.face_detect_test import FaceDetectionTest
from tests.single_image_test import SingleImageTest
from analysers import VerificationAnalyser
from tester import Tester
import os


DATA_DIR = "./data/BFD/small"
TEST_DIR = "./data/BFD/test"
TEST_IMG = os.path.join(TEST_DIR, "VP", "VP0101.png")
TEST_IMG_DIR = os.path.join(TEST_DIR, "VP")

########################################################################################################################
# Various source test
TRAIN_DIR = "./data/web_tests/train"
MAIN_TEST_DIR = "./data/web_tests/test"
BFD_TEST_SUB = "BFD"
WEB22_TEST_SUB = "WEB160712_22"
WEB26_TEST_SUB = "WEB160712_26"
WEB32_TEST_SUB = "WEB160712_32"
WEB35_TEST_SUB = "WEB160712_35"
W1_TEST_SUB = "WEB_W1"
W2_TEST_SUB = "WEB_W2"
X2_TEST_SUB = "WEB_X2"

########################################################################################################################
STS_ERROR06_DIR = "./data/STS_error0.6"
STS_ERR06_TRAIN_DIR = os.path.join(STS_ERROR06_DIR, "train")
STS_ERR06_TEST_DIR = os.path.join(STS_ERROR06_DIR, "test")
STS_TRUE_TEST_DIR = os.path.join(STS_ERROR06_DIR, "test_true")


def run_simple_distance_test():
    raw_struct = RawImagesStruct(STS_ERR06_TRAIN_DIR, True)
    # test_img_dir = ImageDirectory(STS_ERR06_TEST_DIR, True)
    test_img_dir = ImageDirectory(STS_TRUE_TEST_DIR, True)
    si_test = SingleImageTest(raw_struct)
    tester = Tester(si_test)
    tester.run(test_img_dir)

########################################################################################################################
# Verification Tests
VER_TRAIN_DIR = "./data/TS_OpenFace_Verify/train"
VP01_TRAIN_SUB = "VP01"
VP07_TRAIN_SUB = "VP07"
VP0713_TRAIN_SUB = "VP07_13"
VP071319_TRAIN_SUB = "VP07_13_19"
VP12G_TRAIN_SUB = "VP12g"
VP13_TRAIN_SUB = "VP13"
VP19_TRAIN_SUB = "VP19"
VP26_TRAIN_SUB = "VP26"
VP32_TRAIN_SUB = "VP32"
VP38_TRAIN_SUB = "VP38"
VP44_TRAIN_SUB = "VP44"
VP50_TRAIN_SUB = "VP50"
WEB_W1_TRAIN_SUB = "WEB_W1"
WEB_W2_TRAIN_SUB = "WEB_W2"
WEB_X1_TRAIN_SUB = "WEB_X1"
WEB22_TRAIN_SUB = "WEB160712_22"
WEB26_TRAIN_SUB = "WEB160712_26"
WEB35_TRAIN_SUB = "WEB160712_35"
WEB11_TRAIN_SUB = "WEB160718_11"
WEB12_TRAIN_SUB = "WEB160718_12"
VER_TEST_DIR = "./data/TS_OpenFace_Verify/test"
VP_BFD_G_SUB = "VP_BFD_G"
VP_BFD_26_SUB = "VP_BFD_26"
VP_BFD_52_SUB = "VP_BFD_52"
VP_BFD_100_SUB = "VP_BFD_100"
VP_BFD_200_SUB = "VP_BFD_200"
VP_BFD_300_SUB = "VP_BFD_300"
NG_BFD_26_SUB = "NG_BFD_26"
NG_BFD_52_SUB = "NG_BFD_52"
NG_BFD_100_SUB = "NG_BFD_100"
NG_BFD_200_SUB = "NG_BFD_200"
NG_BFD_300_SUB = "NG_BFD_300"
VP_WEB_26_SUB = "VP_web_26"
VP_WEB_G_SUB = "VP_web_glasses"


def run_openface_verification():
    raw_struct = RawImagesStruct(os.path.join(VER_TRAIN_DIR, VP0713_TRAIN_SUB), True)
    test_img_dir = ImageDirectory(os.path.join(VER_TEST_DIR, NG_BFD_300_SUB), True)
    op_test = OpenFaceVerificationTest(raw_struct)
    tester = Tester(op_test)
    tester_analyser = LinearAlgorithmFlow()
    tester_analyser.addStage('flows:analyser', VerificationAnalyser())
    tester_analyser.addStage('flows:output', VerificationTableOutput())
    tester_analyser.addStage('flows:print', OutputConsolePrint())
    tester.set_analyser(tester_analyser)
    tester.run(test_img_dir)

########################################################################################################################

ERR_TEST_DIR = "./data/errorImages"
ERR_OF_PL = "openface_pl"
ERR_OF_VP = "openface_vp"
ERR_PD_PH = "prod_photo"


def run_openface_detection():
    test_img_dir = ImageDirectory(os.path.join(ERR_TEST_DIR, ERR_OF_PL), True)
    # test_img_dir = ImageDirectory(os.path.join(VER_TEST_DIR, VP_BFD_G_SUB), True)
    test = FaceDetectionTest()
    tester = Tester(test)
    tester.run(test_img_dir)

########################################################################################################################


def run():
    run_openface_verification()
    # run_simple_distance_test()
    # run_openface_detection()


if __name__ == '__main__':
    run()
