"""
Image Processing Module
Implementation of image processing algorithms.

Last modification: 21.01.2016

Algorithms:
colour_tools.py
    rgb_to_hsv(color)
    hsv_to_rgb(color)
    hsv_values_extraction(image)
hist_transform.py
    histtruncate(img, low, high)
self_quotient_image.py
    gaussian(x, y, sigmaX, sigmaY)
    getGaussianKernel(ksize, sigma=1.0)
    matrix_multiplication(m1, m2)
    image_division2(image1, image2)
    image_division(image1, image2)
    applyWeightedFilter(img, kernel)
    self_quotient_image(image)
"""