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


def color_normalization(image, normal=(127, 127, 127)):
    avg = [0.0, 0.0, 0.0]
    for inx in range(0, image.shape[0], 1):
        for jnx in range(0, image.shape[1], 1):
            avg += image[inx, jnx]
    avg /= (1.0 * image.shape[0] * image.shape[1])
    coeff = normal / avg
    img = image.copy()
    for inx in range(0, image.shape[0], 1):
        for jnx in range(0, image.shape[1], 1):
            if len(image.shape) > 2:
                img[inx, jnx] *= coeff
            else:
                img[inx, jnx] *= coeff[0]
    return img
