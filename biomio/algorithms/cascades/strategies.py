from biomio.algorithms.clustering import distance
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
        if numpy.isscalar(rects[0][0]):
            rects = [rects]
        for item in rects:
            temp = None
            for r in item:
                if temp is None:
                    temp = r
                else:
                    if inside(r, temp, 0.1):
                        ans = False
                        if self._settings.get("kind", "min") == "min_center":
                            if r[1] + 0.5 * r[3] <= temp[1] + self._settings.get("pos", 1.0) * temp[3]:
                                ans = True
                        elif self._settings.get("kind", "min") == "max_center":
                            if r[1] + 0.5 * r[3] >= temp[1] + self._settings.get("pos", 1.0) * temp[3]:
                                ans = True
                        elif self._settings.get("kind", "min") == "min":
                            if r[1] <= temp[1] + self._settings.get("pos", 1.0) * temp[3]:
                                ans = True
                        else:
                            if r[1] >= temp[1] + self._settings.get("pos", 0.0) * temp[3]:
                                ans = True
                        if ans:
                            if self._settings.get("template", 1) == 1:
                                res.append([temp, r])
                            else:
                                res.append(r)
        return res


class ROICenterStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "center"

    def apply(self, rects, template=[]):
        if self._settings.get("kind", None) is None:
            res = self._center(rects)
        else:
            res = self._align_center(rects)
        if len(res) == 0:
            return [[]]
        else:
            return [res] if numpy.isscalar(res[0]) else res

    def _center(self, rects):
        res = []
        if len(rects) == 0 or len(rects) == 1:
            return res
        temp = None
        center = (0, 0)
        rect_list = []
        for r in rects:
            if temp is None:
                temp = r
                center = (temp[0] + temp[2] / 2.0, temp[1] + temp[3] / 2.0)
            else:
                if inside(r, temp, 0.1):
                    local_center = (r[0] + r[2] / 2.0, r[1] + r[3] / 2.0)
                    d = distance(center, local_center)
                    dist = 0.5
                    if self._settings.get("distance", 0) > 0:
                        dist = self._settings.get("distance")
                    if d < dist * r[2]:
                        rect_list.append(r)
        return rect_list

    def _align_center(self, rects):
        res = []
        if len(rects) == 0:
            return res
        if len(rects) == 1:
            return rects[0]
        temp = None
        center = (0, 0)
        rect_list = []
        for r in rects:
            if temp is None:
                temp = r
                if self._settings.get("kind").lower() == "horizontal":
                    center = (0, temp[1] + temp[3] / 2.0)
                elif self._settings.get("kind").lower() == "vertical":
                    center = (temp[0] + temp[2] / 2.0, 0)
            else:
                if inside(r, temp, 0.1):
                    local_center = (0, 0)
                    dist = r[2]
                    coeff = 0.5
                    if self._settings.get("distance", 0) > 0:
                        coeff = self._settings.get("distance")
                    if self._settings.get("kind").lower() == "horizontal":
                        local_center = (0, r[1] + 0.5 * r[3])
                        dist = coeff * r[3]
                    elif self._settings.get("kind").lower() == "vertical":
                        local_center = (r[0] + 0.5 * r[2], 0)
                        dist = coeff * r[2]

                    d = distance(center, local_center)
                    if d < dist:
                        rect_list.append(r)
        return rect_list


class ROIIncludeStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "include"

    def apply(self, rects, template=[]):
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
        return self._sizing(rects)

    def _sizing(self, rects):
        if len(rects) == 0:
            return [[]]
        if len(rects) == 1:
            return [rects[0]]
        temp = [-1, -1, 10000, 10000]
        if self._settings.get("kind", "min") == "max":
            temp = [-1, -1, 0, 0]
        scale = self._settings.get("scale", 1)
        for item in rects:
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


class ROIScaleStrategy(ROIManagementStrategy):
    def __init__(self, settings=dict()):
        ROIManagementStrategy.__init__(self, settings)

    @staticmethod
    def type():
        return "scale"

    def apply(self, rects, template=[]):
        return self._scale(rects)

    def _scale(self, rects):
        res = []
        if len(rects) == 0:
            return [res]
        factor = self._settings.get("factor", 1.0)
        temp = None
        for item in rects:
            if temp is None:
                temp = item
            else:
                if item[2] <= factor * temp[2] and item[3] <= factor * temp[3]:
                    res.append(item)
        return res


class StrategyFactory:
    strategies = {
        ROIIntersectionStrategy.type(): ROIIntersectionStrategy,
        ROIManagementStrategy.type(): ROIManagementStrategy,
        ROIFilteringStrategy.type(): ROIFilteringStrategy,
        ROIPositionStrategy.type(): ROIPositionStrategy,
        ROIIncludeStrategy.type(): ROIIncludeStrategy,
        ROISizingStrategy.type(): ROISizingStrategy,
        ROICenterStrategy.type(): ROICenterStrategy,
        ROIUnionStrategy.type(): ROIUnionStrategy,
        ROIScaleStrategy.type(): ROIScaleStrategy,
        "": ROIManagementStrategy
    }

    def __init__(self):
        pass

    @staticmethod
    def get(strategy):
        return StrategyFactory.strategies[strategy["type"]](strategy["settings"])
