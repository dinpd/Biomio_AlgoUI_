from algorithms.recognition.keypoints import (KeypointsObjectDetector,
                                              identifying)
import logger


class SpiralKeypointsVectorDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = NearPyHash(self.kodsettings.max_hash_length)
        self._hash.addRandomBinaryProjectionsEngine(10)

    def update_hash(self, data):
        self._hash.add_dataset(data['descriptors'], os.path.split(data['path'])[0])

    @identifying
    def identify(self, data):
        imgs = dict()
        neig = self._hash.neighbours(data['keypoints'])
        logger.logger.debug(neig)
        for el in neig:
            if el[2] < self.kodsettings.neighbours_distance:
                value = imgs.get(el[1], 0)
                value += 1
                imgs[el[1]] = value
        keys = imgs.keys()
        vmax = 0
        max_key = ""
        for key in keys:
            if imgs[key] > vmax:
                max_key = key
                vmax = imgs[key]
        logger.logger.debug(imgs)
        logger.logger.debug(max_key)
        return max_key

    def _detect(self, data, detector):
        height, width = data['roi'].shape[0], data['roi'].shape[1]
        order_keys = obj.keypoints()  # spiralSort(obj, width, height)
        order_keys = minimizeSort(obj)
        obj.keypoints(keypointsToArrays(order_keys))
        key_arr = joinVectors(obj.keypoints())
        while len(key_arr) < self.kodsettings.max_hash_length:
            key_arr.append(0)
        data['keypoints'] = listToNumpy_ndarray(key_arr)
        return True