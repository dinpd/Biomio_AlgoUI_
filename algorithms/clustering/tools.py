

def distance(p1, p2):
    return pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)


def mass_center(items):
    massaX = 0
    massaY = 0
    for i in items:
        point = i.pt
        massaX += point[0]
        massaY += point[1]
    result = (massaX / len(items), massaY / len(items))
    return result