from effects import grayscale, grayscaleAndEqualize




def imageDifference(template, images):
    templ_gray = grayscale(template)
    res = list()
    for j in range(0, templ_gray.shape[0], 1):
        row = list()
        for i in range(0, templ_gray.shape[1], 1):
            row.append(0.0)
        res.append(row)
    for j in range(0, templ_gray.shape[0], 1):
        for i in range(0, templ_gray.shape[1], 1):
            res[j][i] = templ_gray[j, i]
    k = 0
    for img in images:
        k += 1
        logger.debug("Image #%d" % k)
        templ_img = grayscale(img)
        h = templ_gray.shape[0] if templ_gray.shape[0] < templ_img.shape[0] else templ_img.shape[0]
        w = templ_gray.shape[1] if templ_gray.shape[1] < templ_img.shape[1] else templ_img.shape[1]
        for j in range(0, h, 1):
            for i in range(0, w, 1):
                templ_pixel = templ_gray[j, i]
                img_pixel = templ_img[j, i]
                res[j][i] += int(img_pixel) #abs(int(templ_pixel) - int(img_pixel))
    for j in range(0, templ_gray.shape[0], 1):
        for i in range(0, templ_gray.shape[1], 1):
            templ_gray[j, i] = res[j][i] / (1.0 * (len(images) + 1.0))
    return templ_gray

