from biomio.algorithms.cvtools.effects import rotate90
from tools import skipEmptyRectangles, isRectangle
from classifiers import CascadeROIDetector
from strategies import StrategyFactory


class DetectorStage:
    def __init__(self):
        self.name = "default"
        self.type = "main"
        self.stages = []
        self.classifiers = []
        self.strategy = None


class CascadesDetectionInterface:
    def __init__(self, detect_script, template_script=dict()):
        self._stage = None
        if len(detect_script.keys()) > 0:
            self._stage = self.init_stage(detect_script)
        self._template = None
        if len(template_script.keys()) > 0:
            self._template = self.init_stage(template_script)
        self._backup = {}
        self._result_backup = True

    @staticmethod
    def init_stage(detect_script):
        stage = DetectorStage()
        stage.type = detect_script["type"]
        stage.name = detect_script["name"]
        stage.strategy = StrategyFactory.get(detect_script["strategy"])
        if detect_script["type"] == "main":
            stages = detect_script["action"]
            for sub in stages:
                stage.stages.append(CascadesDetectionInterface.init_stage(sub))
        else:
            settings_list = []
            if isinstance(detect_script["action"]["settings"], dict):
                settings_list = [detect_script["action"]["settings"]]
            elif isinstance(detect_script["action"]["settings"], list):
                settings_list = detect_script["action"]["settings"]
            cascades = detect_script["action"]["cascades"]
            for settings in settings_list:
                classifier = CascadeROIDetector()
                classifier.classifierSettings.importSettings(settings)
                for cascade in cascades:
                    classifier.add_cascade(cascade)
                stage.classifiers.append(classifier)
        return stage

    def detect(self, image):
        self._backup = {}
        temp = []
        if self._template:
            temp = self.apply_stage(image, self._template)
        if self._stage:
            return image, self.apply_stage(image, self._stage, temp)
        return image, []

    def apply_stage(self, image, stage, template=[]):
        if self._backup.get(stage.name, None) is not None:
            return self._backup[stage.name]
        rects = []
        if stage.type == "main":
            for s in stage.stages:
                rects += self.apply_stage(image, s)
        else:
            for classifier in stage.classifiers:
                classifier.classifierSettings.dump()
                rects += classifier.detect(image, True)
        new_rects = skipEmptyRectangles(rects)
        result = stage.strategy.apply(new_rects, template)
        if self._result_backup:
            self._backup[stage.name] = result
        return result


class RotatedCascadesDetector(CascadesDetectionInterface):
    def __init__(self, rotate_script, detect_script, template_script=dict()):
        CascadesDetectionInterface.__init__(self, detect_script, template_script)
        self._rotation = None
        if len(rotate_script.keys()) > 0:
            self._rotation = self.init_stage(rotate_script)

    def detect(self, image):
        self._backup = {}
        img = self._apply_rotate(image)
        self._backup = {}
        res = CascadesDetectionInterface.detect(self, img)
        return res

    def _apply_rotate(self, image):
        if self._rotation:
            img = image
            img2 = rotate90(img)
            img3 = rotate90(img2)
            img4 = rotate90(img3)
            images = {
                1: img,
                2: img2,
                3: img3,
                4: img4
            }
            d = dict()
            rects = []
            if len(self._rotation.stages) > 1:
                r1 = []
                r2 = []
                r3 = []
                r4 = []
                for stage in self._rotation.stages:
                    self._backup = {}
                    lr1 = self.apply_stage(img, stage)
                    r1 += lr1
                    for lr in lr1:
                        d[str(lr)] = 1
                    self._backup = {}
                    lr2 = self.apply_stage(img2, stage)
                    r2 += lr2
                    for lr in lr2:
                        d[str(lr)] = 2
                    self._backup = {}
                    lr3 = self.apply_stage(img3, stage)
                    r3 += lr3
                    for lr in lr3:
                        d[str(lr)] = 3
                    self._backup = {}
                    lr4 = self.apply_stage(img4, stage)
                    r4 += lr4
                    for lr in lr4:
                        d[str(lr)] = 4
                if isRectangle(r1[0]):
                    rects.append(skipEmptyRectangles(r1))
                if isRectangle(r2[0]):
                    rects.append(skipEmptyRectangles(r2))
                if isRectangle(r3[0]):
                    rects.append(skipEmptyRectangles(r3))
                if isRectangle(r4[0]):
                    rects.append(skipEmptyRectangles(r4))
            else:
                stage = self._rotation.stages[0]
                self._backup = {}
                r1 = self.apply_stage(img, stage)
                rects += r1
                for lr in r1:
                    d[str(lr)] = 1
                self._backup = {}
                r2 = self.apply_stage(img2, stage)
                rects += r2
                for lr in r2:
                    d[str(lr)] = 2
                self._backup = {}
                r3 = self.apply_stage(img3, stage)
                rects += r3
                for lr in r3:
                    d[str(lr)] = 3
                self._backup = {}
                r4 = self.apply_stage(img4, stage)
                rects += r4
                for lr in r4:
                    d[str(lr)] = 4
                rects = skipEmptyRectangles(rects)
            d[str([])] = 1
            rect = self._rotation.strategy.apply(rects)
            count = {
                1: 0,
                2: 0,
                3: 0,
                4: 0
            }
            gl = {
                1: [0, 0, 0, 0],
                2: [0, 0, 0, 0],
                3: [0, 0, 0, 0],
                4: [0, 0, 0, 0]
            }
            for rs in rect:
                if len(rs) > 1:
                    count[d[str(rs[1])]] += 1
                    if (gl[d[str(rs[1])]][2] < rs[0][2]) and (gl[d[str(rs[1])]][3] < rs[0][3]):
                        gl[d[str(rs[1])]] = rs[0]
            max = -1
            midx = 0
            for index in range(1, 5, 1):
                if count[index] > max:
                    max = count[index]
                    midx = index
                elif count[index] == max:
                    if gl[index][2] > gl[midx][2] and gl[index][3] > gl[midx][3]:
                        midx = index
            return images[midx]
        return image
