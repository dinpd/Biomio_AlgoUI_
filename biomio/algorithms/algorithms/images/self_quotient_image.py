from hist_transform import histtruncate
import numpy as np


def gaussian(x, y, sigmaX, sigmaY):
    return (1 / (2.0 * np.pi * sigmaX * sigmaY)) * np.exp(-(x * x + y * y)/(2.0 * sigmaX * sigmaY))


def getGaussianKernel(ksize, sigma=1.0):
    kernel = []
    w = ksize[0] / 2
    h = ksize[1] / 2
    if sigma == 0:
        sigma = 0.3 * ((ksize[0] - 1) * 0.5 - 1) + 0.8
    for i in range(-h, h + 1, 1):
        row = []
        for j in range(-w, w + 1, 1):
            row.append(gaussian(j, -i, sigma, sigma))
        kernel.append(row)
    return kernel


def matrix_multiplication(m1, m2):
    res = []
    summ = 0
    if (m1 is not None) and (m2 is not None):
        for i in range(0, min(len(m1), len(m2)), 1):
            line = []
            for j in range(0, min(len(m1[i]), len(m2[i])), 1):
                val = m1[i][j] * m2[i][j]
                summ += val
                line.append(val)
            res.append(line)
    res /= (1.0 * summ)
    return res


def image_division2(image1, image2):
    shape = image1.shape if image1.shape < image2.shape else image2.shape
    out = image1.copy()
    for i in range(0, shape[0], 1):
        for j in range(0, shape[1], 1):
            for k in range(0, shape[2], 1):
                # coeff = 1
                # if image2[i][j][k] != 0:
                coeff = image1[i][j][k] / (1.0 * image2[i][j][k] + 0.01)
                # if coeff * out[i][j][k] > 255:
                #     coeff = 1
                out[i][j][k] = coeff
    return out


def image_division(image1, image2):
    shape = image1.shape if image1.shape < image2.shape else image2.shape
    out_min = [255, 255, 255]
    out_max = [0, 0, 0]
    unnorm_img = []
    for i in range(0, shape[0], 1):
        column_img = []
        for j in range(0, shape[1], 1):
            cell_img = []
            for k in range(0, shape[2], 1):
                coeff = image1[i][j][k] / (1.0 * image2[i][j][k] + 0.01)
                cell_img.append(coeff)
                # out_min[k] = min(out_min[k], coeff)
                # out_max[k] = max(out_max[k], coeff)
            column_img.append(cell_img)
        unnorm_img.append(column_img)
    for k in range(0, shape[2], 1):
        level_matrix = []
        for i in range(0, shape[0], 1):
            column_img = []
            for j in range(0, shape[1], 1):
                column_img.append(unnorm_img[i][j][k])
            level_matrix.append(column_img)
        norm_img, level_min, level_max = histtruncate(level_matrix, 2, 2)
        out_min[k] = level_min
        out_max[k] = level_max
        for i in range(0, shape[0], 1):
            for j in range(0, shape[1], 1):
                unnorm_img[i][j][k] = norm_img[i][j]
    out = image1.copy()
    for i in range(0, shape[0], 1):
        for j in range(0, shape[1], 1):
            for k in range(0, shape[2], 1):
                coeff = unnorm_img[i][j][k]
                out[i][j][k] = (coeff - out_min[k]) * (255 / (out_max[k] - out_min[k]))
    return out


def applyWeightedFilter(img, kernel):
    h = len(kernel)
    w = 0
    if not np.isscalar(kernel[0]):
        w = len(kernel[0])
    shape = img.shape
    out = img.copy()
    for i in range(0, shape[0], 1):
        for j in range(0, shape[1], 1):
            suma = [0, 0, 0]
            count = 0
            for k in range(-h/2 + 1, h/2 + 1, 1):
                for l in range(-w/2 + 1, w/2 + 1, 1):
                    li = i + k if i + k >= 0 else 0
                    lj = j + l if j + l >= 0 else 0
                    li = li if li < shape[0] else shape[0] - 1
                    lj = lj if lj < shape[1] else shape[1] - 1
                    suma += img[li][lj]
                    count += 1
            suma /= 1.0 * count
            countM1 = [0, 0, 0]
            countM2 = [0, 0, 0]
            for k in range(-h/2 + 1, h/2 + 1, 1):
                for l in range(-w/2 + 1, w/2 + 1, 1):
                    li = i + k if i + k >= 0 else 0
                    lj = j + l if j + l >= 0 else 0
                    li = li if li < shape[0] else shape[0] - 1
                    lj = lj if lj < shape[1] else shape[1] - 1
                    for inx, v in enumerate(img[li][lj]):
                        if v <= suma[inx]:
                            countM1[inx] += 1
                        else:
                            countM2[inx] += 1
            for inx in range(0, shape[2], 1):
                valM1 = 1 if countM1[inx] >= countM2[inx] else 0
                valM2 = 1 if countM1[inx] <= countM2[inx] else 0
                W = []
                for k in range(-h/2 + 1, h/2 + 1, 1):
                    linearW = []
                    for l in range(-w/2 + 1, w/2 + 1, 1):
                        li = i + k if i + k >= 0 else 0
                        lj = j + l if j + l >= 0 else 0
                        li = li if li < shape[0] else shape[0] - 1
                        lj = lj if lj < shape[1] else shape[1] - 1
                        if img[li][lj][inx] <= suma[inx]:
                            linearW.append(valM1)
                        else:
                            linearW.append(valM2)
                    W.append(linearW)
                W = matrix_multiplication(W, kernel)
                con = 0
                for k in range(-h/2 + 1, h/2 + 1, 1):
                    for l in range(-w/2 + 1, w/2 + 1, 1):
                        li = i + k if i + k >= 0 else 0
                        lj = j + l if j + l >= 0 else 0
                        li = li if li < shape[0] else shape[0] - 1
                        lj = lj if lj < shape[1] else shape[1] - 1
                        con += W[k + h/2 - 1][l + w/2 - 1] * img[li][lj][inx]
                out[i][j][inx] = con
                del W
    return out


def self_quotient_image(image):
    kernelM = getGaussianKernel((5, 5), 1)
    res = applyWeightedFilter(image, kernelM)
    image_res = image_division(image, res)
    return image_res
