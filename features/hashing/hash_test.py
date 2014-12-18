from lshash import LSHash
from nearpy_hash import NearPyHash
from logger import logger


def lshash_test(rects, template):
    print "==================================================="
    print "=                    Test Module                  ="
    print "=                 Test: lshash Query              ="
    print "==================================================="
    print "Input: ", rects
    print "Initializing..."
    lsh = LSHash(64, len(rects[0]))
    for r in rects:
        lsh.index(r)
    print "Select..."
    print "Output: ", lsh.query(template)
    print "==================================================="


def nearpy_test(rects, template):
    print "==================================================="
    print "=                   Test Module                   ="
    print "=                Test: NearPy Query               ="
    print "==================================================="
    print "Input: ", rects
    dis = len(rects[0])
    print "Initializing..."
    nhash = NearPyHash(dis)
    nhash.addRandomBinaryProjectionsEngine(10)
    nhash.store_dataset(rects)
    nhash.init_engines()
    print "Select..."
    print "Output: ", nhash.neighbours(template)
    print "==================================================="