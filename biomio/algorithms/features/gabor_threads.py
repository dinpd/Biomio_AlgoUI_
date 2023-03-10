#!/usr/bin/env python

"""
gabor_threads.py
=========
Sample demonstrates:
- use of multiple Gabor filter convolutions to get Fractalius-like image effect (http://www.redfieldplugins.com/filterFractalius.htm)
- use of python threading to accelerate the computation
Usage
-----
gabor_threads.py [image filename]
"""

import numpy as np
import cv2
from multiprocessing.pool import ThreadPool


def build_filters():
    filters = []
    ksize = 15
    for theta in np.arange(0, np.pi, np.pi / 32):
        kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        kern /= 1.5*kern.sum()
        filters.append(kern)
    return filters


def process(img, filters):
    accum = np.zeros_like(img)
    for kern in filters:
        fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
        np.maximum(accum, fimg, accum)
    return accum


def process_kernel(img, filter_kernel):
    accum = np.zeros_like(img)
    fimg = cv2.filter2D(img, cv2.CV_8UC3, filter_kernel)
    np.maximum(accum, fimg, accum)
    return accum


def process_threaded(img, filters, threadn = 8):
    accum = np.zeros_like(img)
    def f(kern):
        return cv2.filter2D(img, cv2.CV_8UC3, kern)
    pool = ThreadPool(processes=threadn)
    for fimg in pool.imap_unordered(f, filters):
        np.maximum(accum, fimg, accum)
    return accum


if __name__ == '__main__':
    import sys

    print __doc__
    try:
        img_fn = sys.argv[1]
    except:
        img_fn = '../data/baboon.jpg'

    img = cv2.imread(img_fn)
    if img is None:
        print 'Failed to load image file:', img_fn
        sys.exit(1)

    filters = build_filters()

    res2 = process_threaded(img, filters)

    cv2.imwrite(sys.argv[2], res2)
    cv2.imshow('img', img)
    cv2.imshow('result', res2)
    cv2.waitKey()
    cv2.destroyAllWindows()

