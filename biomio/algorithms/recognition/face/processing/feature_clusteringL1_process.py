from biomio.algorithms.clustering import FOREL, KMeans, mass_center, distance
from biomio.algorithms.cvtools.visualization import (drawLine, showClusters, drawCircle, showNumpyImage, drawKeypoints,
                                                     drawClusters, drawHexagon)
from biomio.algorithms.algorithms.geometry.hexagon import hexagon_grid, hexagon_segments, hexagon_shape, \
    pointHexagonTest
from biomio.algorithms.algorithms.geometry.angles import angleForPoint
from biomio.algorithms.cvtools.structures import pointPolygonTest
from biomio.algorithms.cvtools.system import saveNumpyImage
from biomio.algorithms.logger import logger


class FeatureClusteringL1Processing:
    def __init__(self, cc_detector):
        self._cc_detector = cc_detector
        self._last_error = None

    def last_error(self):
        return self._last_error

    def detect(self, data, detector):
        ccenters = self._cc_detector.detect(data)
        if ccenters is None:
            self._last_error = self._cc_detector.last_error()
            return False
        # out = drawLine(data['roi'], (lefteye[0], lefteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centereye[0], centereye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (righteye[0], righteye[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (centermouth[0], centermouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (leftmouth[0], leftmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        # out = drawLine(out, (rightmouth[0], rightmouth[1], centernose[0], centernose[1]), (255, 0, 0))
        centers = [ccenters['lefteye'], ccenters['righteye'], ccenters['centereye'],
                   ccenters['centernose'], ccenters['leftmouth'], ccenters['rightmouth']]
        # for point in centers:
        #     out = drawCircle(out, point, 5, (255, 0, 0))
        # out = drawLine(out, (rect[0], rect[1], rect[0] + rect[2], rect[1]), (0, 255, 0))
        # out = drawLine(out, (rect[0], rect[1], rect[0], rect[1] + rect[3]), (0, 255, 0))
        # out = drawLine(out, (rect[0] + rect[2], rect[1] + rect[3], rect[0] + rect[2], rect[1]), (0, 255, 0))
        # out = drawLine(out, (rect[0] + rect[2], rect[1] + rect[3], rect[0], rect[1] + rect[3]), (0, 255, 0))
        # self.filter_keypoints(data)

        out = data['roi']
        clusters = KMeans(data['keypoints'], 0, centers)
        for i, cluster in enumerate(clusters):
            outi = data['roi']
            # cluster['center'] = mass_center(cluster['items'])
            # desc = detector.compute(data['roi'], cluster['items'])
            # logger.debug(desc['descriptors'])
            # summ = 0
            # coeff = []
            # for keypoint in desc['keypoints']:
            #     summ += keypoint.response
            #     coeff.append(keypoint.response)
            # logger.debug(coeff)
            # logger.debug(summ)
            # coeff = [c / summ for c in coeff]
            # logger.debug(coeff)
            # cluster['avg_descriptor'] = self.average_descriptor(desc['descriptors'], coeff)
            ########################################################################
            # cluster.center - keypoint.point
            ########################################################################
            radius = 0
            for item in cluster['items']:
                dist = distance(cluster['center'], item.pt)
                if dist > radius:
                    radius = dist
            cluster['radius'] = radius
            ########################################################################
            # Hexagons
            ########################################################################
            # out = self.hexagon_subclustering(cluster, radius, **{'out_image': out})
            ########################################################################
            self.forel_hexagon_subclustering(cluster)
            # self.forel_subclustering(cluster)
            # out = drawCircle(out, (int(cluster['center'][0]), int(cluster['center'][1])), 4, (255, 0, 0), thickness=-1)
            # outi = drawCircle(outi, (int(cluster['center'][0]), int(cluster['center'][1])), 4, (255, 0, 0), thickness=-1)
            # saveNumpyImage("D:/clusters/cluster#" + str(i) + ".png", out)
        # saveNumpyImage("D:/clusters/clusters.png", out)
        # showNumpyImage(out)

        # for cluster in clusters:
        #     out = drawCircle(out, (int(cluster['center'][0]), int(cluster['center'][1])), 5, (0, 0, 255))
        # showClusters(clusters, out)
        data['true_clusters'] = clusters
        descriptors = []
        centers = []
        weights = []
        keydescriptors = []
        for cluster in clusters:
            desc = detector.compute(data['roi'], cluster['items'])
            descriptors.append(desc['descriptors'])
            centers.append(cluster['center'])
            pairs = []
            sum = 0
            for index, item in enumerate(cluster['items']):
                # pairs.append((desc['descriptors'][index], item.response))
                sum += item.response
            weights.append((pairs, sum))
            cluster_keypoints = []
            for index, item in enumerate(cluster['items']):
                cluster_keypoints.append((item, desc['descriptors'][index]))
            keydescriptors.append(cluster_keypoints)
        data['clusters'] = descriptors
        data['centers'] = centers
        data['weights'] = weights
        data['key_desc'] = keydescriptors

        # logger.debug(os.path.join("D:\Projects\Biomio\Test1", "roi", data['name'] + ".jpg"))
        # saveNumpyImage(os.path.join("D:/Projects/Biomio/Test1/roi", data['name'] + ".jpg"), data['roi'])
        # data['keypoints_image'] = drawKeypoints(data, 'roi')
        # for idx, cluster in enumerate(data['true_clusters']):
        #     self_graph = SelfGraph(cluster['items'], 3, data['clusters'][idx])
        #     data['keypoints_image'] = drawSelfGraph(data, self_graph, key='keypoints_image')
        # import cv2
        # cv2.imshow("Window", data['keypoints_image'])
        # cv2.waitKey()
        return True

    def forel_subclustering(self, cluster):
        small_clusters = FOREL(cluster['items'], 20)
        cluster['subclusters'] = []
        cluster['subncenters'] = []
        for cl in small_clusters:
            cl['center'] = mass_center(cl['items'])
            cl['ncenter'] = (cl['center'][0] - cluster['center'][0], cl['center'][1] - cluster['center'][1])
            cluster['subclusters'].append(cl)
            cluster['subncenters'].append(cl['ncenter'])
            ########################################################################
            # cluster.center - subcluster.center
            ########################################################################
            # dist = distance(cluster['center'], cl['center'])
            # if dist > radius:
            #     radius = dist
            ########################################################################
            # Subclustering Vector
            ########################################################################
            # length = 0
            # v_x = 0
            # v_y = 0
            # logger.debug("#########################################################")
            # for item in cl['items']:
            #     local_pt = (item.pt[0] - cl['center'][0], item.pt[1] - cl['center'][1])
            #     logger.debug(item.pt)
            #     logger.debug(local_pt)
            #     vlength = distance((0, 0), local_pt)
            #     logger.debug(vlength)
            #     length += pow(vlength, 2)
            #     v_x += local_pt[0]
            #     v_y += local_pt[1]
            # length = pow(length, 0.5)
            # cl['vector_length'] = length
            # cl['vector_alength'] = length / (1.0 * len(cl['items']))
            # cl['vector_point'] = (v_x, v_y)
            # logger.debug(cl['vector_length'])
            # logger.debug(cl['vector_point'])
            # logger.debug("#########################################################")
            ########################################################################
            # out = drawClusters([cl], out)
            # out = drawCircle(out, (int(cl['center'][0]), int(cl['center'][1])), 3, (0, 0, 255), thickness=-1)
            # outi = drawClusters([cl], outi)
            # outi = drawCircle(outi, (int(cl['center'][0]), int(cl['center'][1])), 3, (0, 0, 255), thickness=-1)
            count = 0
            # for item in cl['items']:
            #     count += item.response
            # desc = detector.compute(data['roi'], cl['items'])
            # cluster['avg_descriptors'].append(self.average_descriptor(desc['descriptors']))
            # logger.debug(desc['descriptors'])
            # logger.debug("===============================================")
            # logger.debug(cl['center'])
            # logger.debug(count)
            # logger.debug(len(cl['items']))
            # logger.debug("===============================================")

    def forel_hexagon_subclustering(self, cluster):
        radius = 30
        small_clusters = FOREL(cluster['items'], radius)
        cluster['subclusters'] = []
        cluster['subncenters'] = []
        for cl in small_clusters:
            cl['center'] = mass_center(cl['items'])
            ########################################################################
            # cluster.center - subcluster.center
            ########################################################################
            # dist = distance(cluster['center'], cl['center'])
            # if dist > radius:
            #     radius = dist
            ########################################################################
            # Subclustering Vector
            ########################################################################
            max_length = radius
            start_angle = 30
            for item in cl['items']:
                dist = distance(cl['center'], item.pt)
                if dist > max_length:
                    max_length = dist
            vector = self.hexagon_estimation_vector(cl, max_length, start_angle)
            cl['vector_length'] = vector[0]
            cl['vector_angle'] = vector[1]
            cl['vector_mass'] = vector[2]
            ########################################################################
            cl['ncenter'] = (cl['center'][0] - cluster['center'][0], cl['center'][1] - cluster['center'][1])
            cluster['subclusters'].append(cl)
            cluster['subncenters'].append(cl['ncenter'])
            # out = drawClusters([cl], out)
            # out = drawCircle(out, (int(cl['center'][0]), int(cl['center'][1])), 3, (0, 0, 255), thickness=-1)
            # outi = drawClusters([cl], outi)
            # outi = drawCircle(outi, (int(cl['center'][0]), int(cl['center'][1])), 3, (0, 0, 255), thickness=-1)
            # count = 0
            # for item in cl['items']:
            #     count += item.response
            # desc = detector.compute(data['roi'], cl['items'])
            # cluster['avg_descriptors'].append(self.average_descriptor(desc['descriptors']))
            # logger.debug(desc['descriptors'])
            # logger.debug("===============================================")
            # logger.debug(cl['center'])
            # logger.debug(count)
            # logger.debug(len(cl['items']))
            # logger.debug("===============================================")

    def hexagon_subclustering(self, cluster, radius, **kwargs):
        # logger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        out = kwargs['out_image']
        # outi = kwargs['out_cluster']
        hex_radius = 20
        start_angle = 30
        hexagons = hexagon_grid(cluster['center'], hex_radius, radius)
        # logger.debug(hexagons)
        # out = data['roi']
        hexagons_points = [{'center': hexagon, 'items': []} for hexagon in hexagons]
        for point in cluster['items']:
            for hex_data in hexagons_points:
                if pointHexagonTest(point.pt, hex_data['center'], hex_radius, start_angle) >= 0:
                    hex_data['items'].append(point)
                    break
        hexagons_points = [hex_data for hex_data in hexagons_points if len(hex_data['items']) > 0]

        cluster['subclusters'] = []
        cluster['subncenters'] = []
        for hex_data in hexagons_points:
            vector = self.hexagon_estimation_vector(hex_data, hex_radius, start_angle)
            hex_data['vector_length'] = vector[0]
            hex_data['vector_angle'] = vector[1]
            hex_data['vector_mass'] = vector[2]
            hex_data['mass_center'] = mass_center(hex_data['items'])
            ########################################################################
            # Hexagon Cluster Center
            ########################################################################
            hex_data['ncenter'] = (hex_data['center'][0] - cluster['center'][0],
                                   hex_data['center'][1] - cluster['center'][1])
            ########################################################################
            # Hexagon Cluster Mass Center
            ########################################################################
            # hex_data['ncenter'] = (hex_data['mass_center'][0] - cluster['center'][0],
            #                        hex_data['mass_center'][1] - cluster['center'][1])
            ########################################################################
            # Hexagon Segment Mass Center
            ########################################################################
            # hex_data['ncenter'] = (hex_data['vector_mass'][0] - cluster['center'][0],
            #                        hex_data['vector_mass'][1] - cluster['center'][1])
            ########################################################################
            cluster['subclusters'].append(hex_data)
            cluster['subncenters'].append(hex_data['ncenter'])
        out = drawClusters(hexagons_points, out)
        # outi = drawClusters(hexagons_points, outi)
        cluster['subclusters'] = hexagons_points
        for hexagon in hexagons_points:
            out = drawHexagon(out, hexagon['center'], hex_radius, start_angle, (255, 0, 0), 1)
            # outi = drawHexagon(outi, hexagon['center'], hex_radius, start_angle, (255, 0, 0), 1)
        # showNumpyImage(out)
        # showNumpyImage(outi)
        # logger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        return out  # {'out_image': out, 'out_cluster': outi}

    @staticmethod
    def hexagon_estimation_vector(data, radius, start_angle):
        segments = hexagon_segments(data['center'], radius, start_angle)
        ext_segments = [{'contour': segment, 'items': [], 'center': data['center'], 'weight': 0,
                         'angle': 360 - 30 * (2 * inx + 1) - start_angle} for inx, segment in enumerate(segments)]
        for point in data['items']:
            for segment in ext_segments:
                if pointPolygonTest(point.pt, segment['contour']) >= 0:
                    segment['items'].append(point)
                    segment['weight'] += abs(point.response)
                    break
        max_weight = 0
        segm = None
        total_weight = 0
        for segment in ext_segments:
            total_weight += segment['weight']
            if segment['weight'] > max_weight:
                max_weight = segment['weight']
                segm = segment
        vector_point = [segm['center'][0], segm['center'][1]]
        for item in segm['items']:
            vector_point[0] += item.pt[0] - segm['center'][0]
            vector_point[1] += item.pt[1] - segm['center'][1]
        angle = angleForPoint(segm['center'], tuple(vector_point))
        segm_mass = mass_center(segm['items'])
        return segm['weight'] / total_weight, angle, segm_mass

    def average_descriptor(self, descriptors, coefficients=[]):
        avg_desc = []
        if len(descriptors) <= 0:
            return avg_desc
        for d in descriptors[0]:
            avg_desc.append(0)
        for index, descriptor in enumerate(descriptors):
            coeff = 1.0
            if len(coefficients) > 0:
                coeff = coefficients[index]
            avg_desc += coeff * descriptor
        # logger.debug(avg_desc)
        avg_desc /= len(descriptors)
        # logger.debug(avg_desc)
        return avg_desc

    def filter_keypoints(self, data):
        clusters = FOREL(data['keypoints'], 20)
        keypoints = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            if p > 0.02:
                keypoints += [item for item in cluster['items']]
        data['keypoints'] = keypoints
