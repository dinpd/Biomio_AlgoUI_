class CascadesCCDetector:
    def __init__(self, eye_detector=None, nose_detector=None, mouth_detector=None):
        self._eye_detector = eye_detector
        self._nose_detector = nose_detector
        self._mouth_detector = mouth_detector
        self._last_error = None

    def last_error(self):
        return self._last_error

    def detect(self, data):
        """
            Center types:
                - lefteye
                - righteye
                - centereye
                - centernose
                - leftmouth
                - rightmouth
                - centermouth
        :param data:
        :return:
        """
        if (self._eye_detector is None) and (self._nose_detector is None) and (self._mouth_detector is None):
            self._last_error = "No detector found."
            return None
        eyes_rect = None
        nose_rect = None
        mouth_rect = None
        if self._eye_detector is not None:
            eyes_rect = self._eye_detector.detect(data['roi'])
        if self._nose_detector is not None:
            nose_rect = self._nose_detector.detect(data['roi'])
        if self._mouth_detector is not None:
            mouth_rect = self._mouth_detector.detect(data['roi'])

        if len(rect) <= 0 or len(rect[0]) <= 0:
            self._last_error = "Eye ROI not found."
            return None
        rect = rect[0]
        lefteye = (rect[0] + rect[3] / 2, rect[1] + rect[3] / 2)
        righteye = (rect[0] + rect[2] - rect[3] / 2, rect[1] + rect[3] / 2)
        centereye = (lefteye[0] + (righteye[0] - lefteye[0]) / 2, lefteye[1] + (righteye[1] - lefteye[1]) / 2)
        centernose = (centereye[0], rect[1] + 2 * rect[3])
        centermouth = (centernose[0], centernose[1] + rect[3])
        if centermouth[1] < data['roi'].shape[0] - 2 * rect[3]:
            centermouth = (centermouth[0], centermouth[1] + rect[3])
        leftmouth = (lefteye[0], centermouth[1])
        rightmouth = (righteye[0], centermouth[1])
        return {
            'lefteye': lefteye,
            'righteye': righteye,
            'centereye': centereye,
            'centernose': centernose,
            'leftmouth': leftmouth,
            'rightmouth': rightmouth,
            'centermouth': centermouth
        }
