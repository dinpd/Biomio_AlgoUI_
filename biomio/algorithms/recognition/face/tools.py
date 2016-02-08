import itertools
import numpy

def minDistance(matches):
    return min(itertools.chain(*matches), key=lambda p: p.distance).distance


def maxDistance(matches):
    return max(itertools.chain(*matches), key=lambda p: p.distance).distance


def meanDistance(matches):
    return numpy.mean([m.distance for m in itertools.chain(*matches)])


def medianDistance(matches):
    return numpy.median([m.distance for m in itertools.chain(*matches)])
