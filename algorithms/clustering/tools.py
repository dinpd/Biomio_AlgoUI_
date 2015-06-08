

def distance(p1, p2):
    return pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)


def mass_center(items, get_point=None):
    massaX = 0
    massaY = 0
    for i in items:
        if get_point is None:
            point = i.pt
        else:
            point = get_point(i)
        massaX += point[0]
        massaY += point[1]
    result = (massaX / len(items), massaY / len(items))
    return result


def sort_clusters(clusters):
    clus = []
    for i in range(0, len(clusters), 1):
        clus.append(dict())
    for cluster in clusters:
        clus[cluster['id']] = cluster
    return clus