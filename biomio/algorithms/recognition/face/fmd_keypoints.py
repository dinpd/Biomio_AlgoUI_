from biomio.algorithms.recognition.keypoints import (KeypointsObjectDetector, BRISKDetectorType,
                                                     identifying)


class FeaturesMatchingDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._data_keys = dict()
        if self.kodsettings.detector_type is BRISKDetectorType:
            size = 64
        else:
            size = 32
        self._hash = NearPyHash(size)
        self._hash.addRandomBinaryProjectionsEngine(10)

    def update_hash(self, data):
        # for keypoint in data['keypoints']:
        for keypoint in data['descriptors']:
            self._hash.add_dataset(keypoint, os.path.split(data['path'])[0])
            value = self._data_keys.get(os.path.split(data['path'])[0], 0)
            value += 1
            self._data_keys[os.path.split(data['path'])[0]] = value

    @identifying
    def identify(self, data):
        imgs = dict()
        for keypoint in data['descriptors']:
            neig = self._hash.neighbours(keypoint)
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
        logger.logger.debug(self._data_keys[max_key])
        logger.logger.debug(len(data['descriptors']))
        logger.logger.debug(imgs[max_key] / (self._data_keys[max_key] * 1.0))
        return max_key

    def _detect(self, data, detector):
        key_arrays = keypointsToArrays(data['keypoints'])
        data['keypoints'] = key_arrays
        return True