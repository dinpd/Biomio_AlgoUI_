from keypoints import KeypointsObjectDetector, NearPyHash
from faces.biom.utils import label_list, files_list, read_file
import logging


def main():
    detector = KeypointsObjectDetector(NearPyHash)
    detector.kodsettings.cascade_list.append("../data/data/haarcascades/haarcascade_frontalface_alt_tree.xml")
    for imfile in files_list("../data/images"):
        if imfile is not "../data/images/s3/7.pgm":
            obj = read_file(imfile)
            detector.addSource(obj)
    detector.identify(read_file("../data/images/s3/7.pgm"))


if __name__ == '__main__':

    logging.basicConfig(
        format='%(levelname)-8s [%(asctime)s] %(message)s',
        level=logging.DEBUG
    )

    main()