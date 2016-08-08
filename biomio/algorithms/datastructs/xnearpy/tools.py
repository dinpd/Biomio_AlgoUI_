from itertools import imap
import operator

def _hamdist1(str1, str2):
    """Count the # of differences between equal length strings str1 and str2"""
    diffs = 0
    for ch1, ch2 in zip(str1, str2):
        if ch1 != ch2:
            diffs += 1
    return diffs


def _hamdist2(str1, str2):
    ne = operator.ne
    return sum(imap(ne, str1, str2))

def hamming_distance(str1, str2):
    """
    Hamming distance function optimized to the string length.
    Optimization based on the post:
    http://code.activestate.com/recipes/499304-hamming-distance/

    :param str1: string
    :param str2: string
    :return: distance between strings
    """
    assert len(str1) == len(str2)
    if len(str1) < 100:
        return _hamdist1(str1, str2)
    else:
        return _hamdist2(str1, str2)
