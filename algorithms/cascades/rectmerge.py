
def mergeRectangles(rects, general=True, convex=True):
    if len(rects) == 0:
        return rects
    if len(rects) == 1:
        return rects[0]

    left = []
    right = []
    half = len(rects) / 2
    i = 0
    for rect in rects:
        if i < half:
            left.append(rect)
        else:
            right.append(rect)
        i += 1
    left = mergeRectangles(left, general, convex)
    right = mergeRectangles(right, general, convex)
    return _mergeRect(left, right, general, convex)


def _mergeRect(left, right, general, convex):
    if convex:
        if general:
            p_left = left[0]
            if p_left > right[0]:
                p_left = right[0]
            p_top = left[1]
            if p_top > right[1]:
                p_top = right[1]
            p_right = left[0] + left[2]
            if p_right < right[0] + right[2]:
                p_right = right[0] + right[2]
            p_bottom = left[1] + left[3]
            if p_bottom < right[1] + right[3]:
                p_bottom = right[1] + right[3]
            return [p_left, p_top, p_right - p_left, p_bottom - p_top]
        else:
            pass
    else:
        if general:
            pass
        else:
            pass


def main():
    rects = []
    rects.append([0, 0, 4, 2])
    rects.append([1, 1, 2, 2])
    rects.append([2, 2, 4, 2])
    rects.append([7, 1, 2, 2])
    print mergeRectangles(rects, True, True)

if __name__ == '__main__':
    main()