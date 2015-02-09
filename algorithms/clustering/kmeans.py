import random
import sys
from tools import distance, mass_center


def KMeans(items, cluster_count, init_centers=[]):
    clusters = []
    cents = []
    currs = []
    get_random = True
    count = cluster_count
    if len(init_centers) > 0:
        count = len(init_centers)
        get_random = False
    for i in range(0, count, 1):
        val = []
        if get_random:
            center = random.randint(0, len(items) - 1)
            while val.__contains__(center):
                center = random.randint(0, len(items) - 1)
            val.append(center)
            item = items[center]
            currs.append(item.pt)
            cluster = dict()
            cluster['center'] = item.pt
            cluster['items'] = []
            clusters.append(cluster)
        else:
            item = init_centers[i]
            currs.append(item)
            cluster = dict()
            cluster['center'] = item
            cluster['items'] = []
            clusters.append(cluster)

    while cents != currs:
        cents = currs
        news = []
        for cluster in clusters:
            cluster['items'] = []
            news.append(cluster)
        clusters = news
        for item in items:
            min_dis = sys.float_info.max
            cl = dict()
            for cluster in clusters:
                c_dis = distance(item.pt, cluster['center'])
                if c_dis < min_dis:
                    min_dis = c_dis
                    cl = cluster
            clusters.remove(cl)
            elements = cl['items']
            elements.append(item)
            cl['items'] = elements
            clusters.append(cl)
        news = []
        currs = []
        for cluster in clusters:
            c = mass_center(cluster['items'])
            currs.append(c)
            cluster['center'] = c
            news.append(cluster)
        clusters = news
    return clusters
