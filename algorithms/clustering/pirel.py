from logger import logger

def PIREL(pixels, threshold):
    clusters = []
    for curr in pixels:
        ccolor = curr["color"]
        if len(clusters) > 0:
            neigh = None
            for cluster in clusters:
                center = cluster['center']
                if (abs(center[0] - ccolor[0]) < threshold and
                            abs(center[1] - ccolor[1]) < threshold and
                            abs(center[2] - ccolor[2]) < threshold):
                    neigh = cluster
            if neigh is None:
                cluster = dict()
                cluster['center'] = ccolor
                cluster['items'] = [curr]
                clusters.append(cluster)
            else:
                r = 0
                g = 0
                b = 0
                neigh["items"].append(curr)
                for color in neigh["items"]:
                    r += color["color"][0]
                    g += color["color"][1]
                    b += color["color"][2]
                r /= len(neigh["items"])
                g /= len(neigh["items"])
                b /= len(neigh["items"])
                neigh["center"] = (r, g, b)
        else:
            cluster = dict()
            cluster['center'] = ccolor
            cluster['items'] = [curr]
            clusters.append(cluster)
        logger.debug(len(clusters))
    return clusters
