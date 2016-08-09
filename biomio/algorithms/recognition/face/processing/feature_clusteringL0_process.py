from biomio.algorithms.clustering import FOREL, KMeans
from biomio.algorithms.cvtools.visualization import (drawLine, showClusters, drawCircle)


class FeatureClusteringL0Processing:
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
        # out = data['roi']
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

        clusters = KMeans(data['keypoints'], 0, centers)
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

    def filter_keypoints(self, data):
        clusters = FOREL(data['keypoints'], 20)
        keypoints = []
        for cluster in clusters:
            p = len(cluster['items']) / (1.0 * len(data['keypoints']))
            if p > 0.02:
                keypoints += [item for item in cluster['items']]
        data['keypoints'] = keypoints
