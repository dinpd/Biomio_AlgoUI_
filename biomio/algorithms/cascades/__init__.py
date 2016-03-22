"""
Cascade Classification Module
Implementation of cascade classification algorithms.

Last modification: 22.03.2016

Algorithms:
classifiers.py
    class CascadeClassifierSettings
    class CascadeROIDetector
detectors.py
    class ROIDetectorInterface
    class OptimalROIDetector(ROIDetectorInterface)
    class OptimalROIDetectorSAoS(ROIDetectorInterface)
rectfilter.py
    filterRectangles(rects)
rectmerge.py
    mergeRectangles(rects)
rectsect.py
    intersectRectangles(rects)
scripts_detectors.py
    class DetectorStage
    class CascadesDetectionInterface
    class RotatedCascadesDetector(CascadesDetectionInterface)
strategies.py
    class ROIManagementStrategy
    class ROIIntersectionStrategy(ROIManagementStrategy)
    class ROIUnionStrategy(ROIManagementStrategy)
    class ROIFilteringStrategy(ROIManagementStrategy)
    class ROIPositionStrategy(ROIManagementStrategy)
    class ROICenterStrategy(ROIManagementStrategy)
    class ROIIncludeStrategy(ROIManagementStrategy)
    class ROISizingStrategy(ROIManagementStrategy)
    class StrategyFactory
tools.py
    getROIImage(image, rectangle)
    isRectangle(rect)
    inside(test, template, ds=0)
    skipEmptyRectangles(rects)
    loadScript(file_name, relative=False)
"""
from rectsect import intersectRectangles
from rectfilter import filterRectangles
from rectmerge import mergeRectangles
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CASCADES_PATH = os.path.join(APP_ROOT, "..", "data", "haarcascades")
SCRIPTS_PATH = os.path.join(APP_ROOT, "scripts")
ALGO_DB_PATH = os.path.join(APP_ROOT, 'algorithms', 'data')
