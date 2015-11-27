def filterRectangles(rects):
    if len(rects) == 0:
        return rects
    if len(rects) == 1:
        return rects[0]
    return reduce(lambda p, q: q if q[2] > p[2] and q[3] > p[3] else p, rects, [0]*4)
