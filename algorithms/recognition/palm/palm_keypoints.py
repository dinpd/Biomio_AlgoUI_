from __future__ import absolute_import
import logger
from algorithms.features.matchers import FlannMatcher
from algorithms.recognition.keypoints import (KeypointsObjectDetector,
                                              verifying)


class PalmKeypointsDetector(KeypointsObjectDetector):
    def __init__(self):
        KeypointsObjectDetector.__init__(self)
        self._hash = []
        self._use_roi = False

    def threshold(self):
        return self.kodsettings.probability

    def update_hash(self, data):
        del data['data']
        del data['roi']
        del data['keypoints']
        # del data['descriptors']
        self._hash.append(data)

    @verifying
    def verify(self, data):
        self._last_error = ""
        matcher = FlannMatcher()
        res = []
        self._log += "Test: " + data['path'] + "\n"
        for d in self._hash:
            logger.logger.debug("Source: " + d['path'])
            self._log += "Source: " + d['path'] + "\n"
            test = data['descriptors']
            source = d['descriptors']
            if (test is None) or (source is None):
                logger.logger.debug("Any descriptors weren't found.")
            else:
                matches = matcher.knnMatch(test, source, k=2)
                ms = []
                for v in matches:
                    if len(v) >= 2:
                        m = v[0]
                        n = v[1]
                        if m.distance < self.kodsettings.neighbours_distance * n.distance:
                            ms.append(m)
                prob = len(ms) / (1.0 * len(matches))
                res.append(prob * 100)
                logger.logger.debug("Result: " + " (Size: " + str(len(source)) + "): "
                                             + str(prob * 100) + "%")
        suma = 0
        for val in res:
            suma += val
        logger.logger.debug("Total: " + str(suma / len(res)))
        return suma / len(res)

    def _detect(self, data, detector):
        return True
