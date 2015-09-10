from tools import inside
import numpy

class ROIManagementStrategy:
    def __init__(self, settings=dict()):
        self._settings = settings

    @staticmethod
    def type():
        return "none"

    def apply(self, rects, template=[]):
        return rects


class ROIIntersectionStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "intersection"

    def apply(self, rects, template=[]):
        if len(rects) == 0:
            return rects
        if len(rects) == 1:
            return rects[0]

        half = len(rects) / 2
        left = self.apply(rects[:half])
        right = self.apply(rects[half:])
        rect = self._interRect(left, right)
        if rect[2] <= 0 or rect[3] <= 0:
            rect[2] = 0
            rect[3] = 0
        return rect

    def _interRect(self, left, right):
        p_left = left[0]
        if p_left < right[0]:
            p_left = right[0]
        p_top = left[1]
        if p_top < right[1]:
            p_top = right[1]
        p_right = left[0] + left[2]
        if p_right > right[0] + right[2]:
            p_right = right[0] + right[2]
        p_bottom = left[1] + left[3]
        if p_bottom > right[1] + right[3]:
            p_bottom = right[1] + right[3]
        return [p_left, p_top, p_right - p_left, p_bottom - p_top]

class ROIUnionStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "union"

    def apply(self, rects, template=[]):
        return [self._merge(rects)]

    def _merge(self, rects):
        if len(rects) == 0:
            return rects
        if len(rects) == 1:
            return rects[0]
        half = len(rects) / 2
        left = self._merge(rects[:half])
        right = self._merge(rects[half:])
        return self._mergeRect(left, right)

    def _mergeRect(self, left, right):
        p_left = left[0]
        if p_left > right[0]:
            p_left = right[0]
        p_top = left[1]
        if p_top > right[1]:
            p_top = right[1]
        p_right = left[0] + left[2]
        if p_right < right[0] + right[2]:
            p_right = right[0] + right[2]
        p_bottom = left[1] + left[3]
        if p_bottom < right[1] + right[3]:
            p_bottom = right[1] + right[3]
        return [p_left, p_top, p_right - p_left, p_bottom - p_top]


class ROIFilteringStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "filtering"

    def apply(self, rects, template=[]):
        return [self._filtering(rects)]

    def _filtering(self, rects):
        if len(rects) == 0:
            return rects
        if len(rects) == 1:
            return rects[0]

        rect = [0, 0, 0, 0]
        for r in rects:
            if r[2] > rect[2] and r[3] > rect[3]:
                rect = r
        return rect


class ROIPositionStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "position"

    def apply(self, rects, template=[]):
        res = self._position(rects)
        if len(res) == 0:
            return [[]]
        else:
            return res

    def _position(self, rects):
        res = []
        if len(rects) == 0:
            return [res]
        if len(rects) == 1:
            return [rects[0]]
        if numpy.isscalar(rects[0][0]):
            rects = [rects]
        for item in rects:
            temp = None
            for r in item:
                if temp is None:
                    temp = r
                else:
                    if inside(r, temp, 0.1):
                        if self._settings.get("kind", "min") == "min":
                            if r[1] <= temp[1] + self._settings.get("pos", 1.0) * temp[3]:
                                res.append([temp, r])
                        else:
                            if r[1] >= temp[1] + self._settings.get("pos", 0.0) * temp[3]:
                                res.append([temp, r])
        return res


class ROIIncludeStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "include"

    def apply(self, rects, template=[]):
        print rects
        res = self._include(rects)
        if len(res) == 0:
            return [[]]
        else:
            return res

    def _include(self, rects):
        res = []
        if len(rects) == 0:
            return [res]
        if len(rects) == 1:
            return [rects[0]]
        if numpy.isscalar(rects[0][0]):
            rects = [rects]
        for item in rects:
            temp = None
            for r in item:
                if temp is None:
                    temp = r
                else:
                    if inside(r, temp, 0.1):
                        res.append(r)
        return res


class ROISizingStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "sizing"

    def apply(self, rects, template=[]):
        print self.type()
        print rects
        return self._sizing(rects)

    def _sizing(self, rects):
        print rects
        if len(rects) == 0:
            return [[]]
        if len(rects) == 1:
            return [rects[0]]
        temp = [-1, -1, 10000, 10000]
        if self._settings.get("kind", "min") == "max":
            temp = [-1, -1, 0, 0]
        scale = self._settings.get("scale", 1)
        for item in rects:
            print "next"
            print temp
            print item
            if self._settings.get("kind", "min") == "min":
                if scale * temp[2] > item[2]:
                    temp[0] = item[0]
                    temp[2] = item[2]
                if scale * temp[3] > item[3]:
                    temp[1] = item[1]
                    temp[3] = item[3]
            else:
                if scale * temp[2] < item[2]:
                    temp[0] = item[0]
                    temp[2] = item[2]
                if scale * temp[3] < item[3]:
                    temp[1] = item[1]
                    temp[3] = item[3]
        if temp[0] == -1 and temp[1] == -1:
            return [[]]
        else:
            return [temp]

class StrategyFactory:
    strategies = {
        ROIIntersectionStrategy.type(): ROIIntersectionStrategy,
        ROIManagementStrategy.type(): ROIManagementStrategy,
        ROIFilteringStrategy.type(): ROIFilteringStrategy,
        ROIPositionStrategy.type(): ROIPositionStrategy,
        ROIIncludeStrategy.type(): ROIIncludeStrategy,
        ROISizingStrategy.type(): ROISizingStrategy,
        ROIUnionStrategy.type(): ROIUnionStrategy,
        "": ROIManagementStrategy
    }

    def __init__(self):
        pass

    @staticmethod
    def get(strategy):
        return StrategyFactory.strategies[strategy["type"]](strategy["settings"])
