
def filterRectangles(rects):
    if len(rects) == 0:
        return rects
    if len(rects) == 1:
        return rects[0]

    rect = [0, 0, 0, 0]
    for r in rects:
        if r[2] > rect[2] and r[3] > rect[3]:
            rect = r
    return rect