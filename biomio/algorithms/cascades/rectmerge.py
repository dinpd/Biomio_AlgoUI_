def mergeRectangles(rects):
    if len(rects) == 0:
        return rects
    if len(rects) == 1:
        return rects[0]
    half = len(rects) / 2
    left = mergeRectangles(rects[:half])
    right = mergeRectangles(rects[half:])
    return _mergeRect(left, right)


def _mergeRect(left, right):
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


def main():
    rects = [[0, 0, 4, 2], [1, 1, 2, 2], [2, 2, 4, 2], [7, 1, 2, 2]]
    print mergeRectangles(rects)


if __name__ == '__main__':
    main()
