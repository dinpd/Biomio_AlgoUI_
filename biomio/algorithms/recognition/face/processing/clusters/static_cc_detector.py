class StaticCCDetector:
    def __init__(self, eye_detector):
        self._eye_detector = eye_detector
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
        rect = self._eye_detector.detect(data['roi'])[1]
        if len(rect) <= 0 or len(rect[0]) <= 0:
            self._last_error = "Eye ROI wasn't found."
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
