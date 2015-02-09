import random
from tools import distance, mass_center


def FOREL(items, radius):
    clusters = []
    local_items = items
    while len(local_items) > 0:
        index = random.randint(0, len(local_items) - 1)
        curr = local_items[index].pt
        neigh = neighbour_objects(local_items, curr, radius)
        cen = mass_center(neigh)
        while cen != curr:
            curr = cen
            neigh = neighbour_objects(local_items, curr, radius)
            cen = mass_center(neigh)

        cluster = dict()
        cluster['center'] = cen
        cluster['items'] = neigh
        clusters.append(cluster)
        for i in neigh:
            local_items.remove(i)
    return clusters


def neighbour_objects(items, center, radius):
    result = []
    for i in items:
        point = i.pt
        dis = distance(point, center)
        if dis <= radius:
            result.append(i)
    return result