__author__ = 'vitalius.parubochyi'


def minDistance(matches):
    dist = []
    for match in matches:
        for m in match:
            dist.append(m.distance)
    # print 'distance: min: %.3f' % min(dist)
    return min(dist)


def maxDistance(matches):
    dist = []
    for match in matches:
        for m in match:
            dist.append(m.distance)
    # print 'distance: max: %.3f' % max(dist)
    return max(dist)


def meanDistance(matches):
    dist = []
    for match in matches:
        for m in match:
            dist.append(m.distance)

    # print 'distance: mean: %.3f' % (sum(dist) / len(dist))
    return sum(dist) / len(dist)


def medianDistance(matches):
    dist = []
    for match in matches:
        for m in match:
            dist.append(m.distance)

    dist.sort()
    return dist[int(len(dist) / 2)]
