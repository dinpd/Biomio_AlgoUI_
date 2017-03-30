from openface_verification_test import run_openface_verification_flow
from structs import RawImagesStruct, ImageDirectory, ImageContainer
from tests.openface_verify_test import OpenFaceVerificationTest
from outputs import VerificationTableOutput, OutputConsolePrint
from corealgorithms.flows import LinearAlgorithmFlow
from tests.face_detect_test import FaceDetectionTest
from tests.single_image_test import SingleImageTest
from analysers import VerificationAnalyser
from tester import Tester
import argparse
import time
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
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


PL_TRAIN_DIR = "./data/OpenFace_iOS_Android/train"
DI_I_TRAIN_SUB = "DI_iOS"
DI_I2_TRAIN_SUB = "DI_iOS2"
DI_A_TRAIN_SUB = "DI_Android"
DI_IA_TRAIN_SUB = "DI_iOS_Android"
VH_I_TRAIN_SUB = "VH_iOS"
VH_A_TRAIN_SUB = "VH_Android"
VH_IA_TRAIN_SUB = "VH_iOS_Android"
PL_TEST_DIR = "./data/OpenFace_iOS_Android/test"
DI_I_TEST_SUB = "DI_iOS"
N_I_TEST_SUB = "N_iOS"
N_A_TEST_SUB = "N_Android"
VH_A_TEST_SUB = "VH_Android"
N2_A_TEST_SUB = "N2_Android"


ZT_TRAIN_DIR = "./data/Android_Zero_Test/train"
T1_TRAIN_SUB = "T1"
T2_TRAIN_SUB = "T2"
ZT_TEST_DIR = "./data/Android_Zero_Test/test"
TE_TEST_SUB = "TE"


def run_openface_verification(train_data, test_data):
    raw_struct = RawImagesStruct(train_data, True)
    test_img_dir = ImageDirectory(test_data, True)
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

ANDROID_DIR = "./data/Android_Cut"
OVER_BORDER = "tmpZLahYG"
NORMAL_SONY = "tmp7_O0hc"
TABLE_BASE = "tmphI1jHa"
SMALLER = "tmpD52FJe"
AVG_MEIZU = "tmpNQlgyW"
NORMAL_MEIZU = "tmpZqTxnT"
OV_MEIZU = "tmpWCg0_a"
ETC_MEIZU = "tmpzLfCoi"
T1_SONY = "tmpgOpMoj"

def run_openface_detection():
    test_img_dir = ImageDirectory(os.path.join(ANDROID_DIR, T1_SONY), True)
    test = FaceDetectionTest()
    tester = Tester(test)
    tester.run(test_img_dir)

########################################################################################################################


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_path', type=str, help="Training data directory.", default=VER_TRAIN_DIR)
    parser.add_argument('--train_data', type=str, help="Training dataset folder.", default=VP07_TRAIN_SUB)
    parser.add_argument('--test_path', type=str, help="Testing data directory.", default=ANDROID_DIR)
    parser.add_argument('--test_data', type=str, help="Testing dataset folder.", default=T1_SONY)

    args = parser.parse_args()

    run_openface_verification(os.path.join(args.train_path, args.train_data),
                              os.path.join(args.test_path, args.test_data))
    # run_openface_verification_flow(os.path.join(args.train_path, args.train_data),
    #                                os.path.join(args.test_path, args.test_data))
    # run_simple_distance_test()
    # run_openface_detection()


if __name__ == '__main__':
    run()
