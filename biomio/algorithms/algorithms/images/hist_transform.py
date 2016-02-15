import numpy as np

def histtruncate(img, low, high):
    h = len(img)
    w = 0
    if not np.isscalar(img[0]):
        w = len(img[0])
    values = []
    for i in range(0, h, 1):
        for j in range(0, w, 1):
            values.append(img[i][j])
    values.sort()
    low_value = values[int(low * w * h / 100.0)]
    high_value = values[int(w * h * (1 - high / 100.0))]
    for i in range(0, h, 1):
        for j in range(0, w, 1):
            if img[i][j] < low_value:
                img[i][j] = low_value
            elif img[i][j] > high_value:
                img[i][j] = high_value
    return img, low_value, high_value
