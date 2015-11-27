import os
import sys
import logger
import shutil

IMAGE_DIR = "faces/data/images"


def label_list(dir=IMAGE_DIR):
    l = os.listdir(dir)
    n = map(lambda x: len(os.listdir(os.path.join(dir, x))), l)
    return zip(l,n)


def files_list(dir=IMAGE_DIR):
    files = []
    for x in [dir + "/" + d for d in os.listdir(dir)]:
        if os.path.isdir(x):
            tfiles = files_list(x)
            for temp in tfiles:
                files.append(temp)
        else:
            files.append(x)
    return files


def label_count(label):
    return len(os.listdir(os.path.join(IMAGE_DIR, x)))


def label_add(label):
    os.mkdir(os.path.join(IMAGE_DIR, label))


def label_remove(label):
    shutil.rmtree(os.path.join(IMAGE_DIR, label), True)

