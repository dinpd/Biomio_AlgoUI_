import itertools


def distance(p1, p2):
    return pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)


def mass_center(items):
    return tuple(map(lambda x: sum(x)/len(items), itertools.izip(
        *itertools.imap(lambda x: x.pt, items))))


def sort_clusters(clusters):
    return sorted(clusters, key=lambda x: x['id'])
