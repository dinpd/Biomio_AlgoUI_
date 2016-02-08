from tools import distance, mass_center, sort_clusters
import random


def get_cluster(id, center, items):
    return {
        'center': center,
        'items': items,
        'id': id,
    }

def KMeans(items, cluster_count, init_centers=[], max_distance=0):
    cents = []
    if not len(init_centers) > 0:
        currs = random.sample(items, cluster_count)
        clusters = [get_cluster(i, item.pt, []) for i, item in currs]
    else:
        currs = [c for c in init_centers]
        clusters = [get_cluster(i, c, []) for i, c in enumerate(init_centers)]

    while cents != currs:
        cents = currs
        for cluster in clusters:
            cluster['items'] = []
        for item in items:
            cl = min(clusters, key=lambda x: distance(item.pt, x['center']))
            cl['items'].append(item)
        currs = []
        for cluster in clusters:
            if len(cluster['items']) > 0:
                c = mass_center(cluster['items'])
                if (max_distance > 0) and (distance(c, cluster['center']) < max_distance):
                    currs.append(c)
                    cluster['center'] = c
                    continue
            currs.append(cluster['center'])
    return sort_clusters(clusters)
