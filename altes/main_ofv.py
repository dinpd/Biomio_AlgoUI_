from openface_verification_test import run_openface_verification_flow
import argparse
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "./data/BFD/small"
TEST_DIR = "./data/BFD/test"
TEST_IMG = os.path.join(TEST_DIR, "VP", "VP0101.png")
TEST_IMG_DIR = os.path.join(TEST_DIR, "VP")


########################################################################################################################
# Verification Tests
VER_TRAIN_DIR = os.path.join(APP_ROOT, "./data/TS_OpenFace_Verify/train")
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
VER_TEST_DIR = os.path.join(APP_ROOT, "./data/TS_OpenFace_Verify/test")
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


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_path', type=str, help="Training data directory.", default=VER_TRAIN_DIR)
    parser.add_argument('--train_data', type=str, help="Training dataset folder.", default=VP07_TRAIN_SUB)
    parser.add_argument('--test_path', type=str, help="Testing data directory.", default=VER_TEST_DIR)
    parser.add_argument('--test_data', type=str, help="Testing dataset folder.", default=VP_BFD_100_SUB)

    args = parser.parse_args()

    run_openface_verification_flow(os.path.join(args.train_path, args.train_data),
                                   os.path.join(args.test_path, args.test_data))
    # run_simple_distance_test()
    # run_openface_detection()


if __name__ == '__main__':
    run()
