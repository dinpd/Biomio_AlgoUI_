import random
from tools import distance, mass_center


# def FOREL(items, radius, get_point):
#     clusters = []
#     local_items = []
#     for item in items:
#         local_items.append(item)
#     while len(local_items) > 0:
#         index = random.randint(0, len(local_items) - 1)
#         curr = get_point(local_items[index])
#         neigh = neighbour_objects(local_items, curr, radius, get_point)
#         cen = mass_center(neigh, get_point)
#         while cen != curr:
#             curr = cen
#             neigh = neighbour_objects(local_items, curr, radius, get_point)
#             cen = mass_center(neigh, get_point)
#
#         cluster = dict()
#         cluster['center'] = cen
#         cluster['items'] = neigh
#         clusters.append(cluster)
#         for i in neigh:
#             local_items.remove(i)
#     return clusters
def FOREL(items, radius):
    clusters = []
    local_items = items[:]
    while len(local_items) > 0:
        index = random.randint(0, len(local_items) - 1)
        curr = local_items[index].pt
        neigh = neighbour_objects(local_items, curr, radius)
        cen = mass_center(neigh)
        while cen != curr:
            curr = cen
            neigh = neighbour_objects(local_items, curr, radius)
            cen = mass_center(neigh)
        clusters.append({
            'center': cen,
            'items': neigh
        })
        for i in neigh:
            local_items.remove(i)
    return clusters


def neighbour_objects(items, center, radius):
    return filter(lambda i: distance(i.pt, center) <= radius, items)
# def neighbour_objects(items, center, radius, get_point):
#     result = []
#     for i in items:
#         point = get_point(i)
#         dis = distance(point, center)
#         if dis <= radius:
#             result.append(i)
#     return result