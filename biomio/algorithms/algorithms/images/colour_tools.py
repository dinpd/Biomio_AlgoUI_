

def rgb_to_hsv(color):
    Rl = color[0] / 255.0
    Gl = color[1] / 255.0
    Bl = color[2] / 255.0
    Cmax = max(Rl, Gl, Bl)
    Cmin = min(Rl, Gl, Bl)
    delta = Cmax - Cmin
    H = 0
    if delta != 0:
        if Cmax == Rl:
            H = ((Gl - Bl) / delta % 6)
        elif Cmax == Gl:
            H = ((Bl - Rl) / delta + 2)
        elif Cmax == Bl:
            H = ((Rl - Gl) / delta + 4)
    H *= 60
    S = 0
    if Cmax != 0:
        S = delta / Cmax
    return [H, S, Cmax]

def hsv_to_rgb(color):
    H = color[0]
    C = color[1] * color[2]
    X = C * (1 - abs((H / 60.0) % 2 - 1))
    m = color[2] - C
    Rl = 0
    Gl = 0
    Bl = 0
    if 0 <= H < 60:
        Rl = C
        Gl = X
    elif 60 <= H < 120:
        Rl = X
        Gl = C
    elif 120 <= H < 180:
        Gl = C
        Bl = X
    elif 180 <= H < 240:
        Gl = X
        Bl = C
    elif 240 <= H < 300:
        Rl = X
        Bl = C
    elif 300 <= H < 360:
        Rl = C
        Bl = X
    return [int((Rl + m) * 255), int((Gl + m) * 255), int((Bl + m) * 255)]


def hsv_values_extraction(image):
    out = image.copy()
    shape = image.shape
    for i in range(0, shape[0]):
        for j in range(0, shape[1]):
            color = image[i][j]
            out_color = rgb_to_hsv(color)
            out_color[0] = 0
            out_color[1] = 0
            out[i][j] = hsv_to_rgb(out_color)
    return out
