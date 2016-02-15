import logging

from guidata.qt.QtCore import SIGNAL, QObject, QCoreApplication
from guidata.qt.QtGui import QAction, QFileDialog
from guidata.configtools import get_icon
from guiqwt.config import _

from aiplugins import IAlgorithmPlugin
from imageproperties import ImageProperties
from biomio.algorithms.cvtools import equalizeHist, grayscale
from biomio.algorithms.experimental.experimental import imageDifference
from biomio.algorithms.cascades.detectors import OptimalROIDetector
from biomio.algorithms.imgobj import loadImageObject

logger = logging.getLogger(__name__)

EQ_ACTION_TITLE = 'Action: EqualizeHist::'
GR_ACTION_TITLE = 'Action: Grayscale::'
DF_ACTION_TITLE = 'Action: Difference::'
OR_ACTION_TITLE = 'Action: Optimal ROI::'


class EqualizeHistPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(EqualizeHistPlugin, self).__init__()

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        gr_action = QAction(parent)
        gr_action.setText(_("Grayscale"))
        gr_action.setIcon(get_icon('grayscale.png'))
        self.connect(gr_action, SIGNAL("triggered()"), self.slot_grayscale)

        eq_action = QAction(parent)
        eq_action.setText(_("Equalize Histogram"))
        eq_action.setIcon(get_icon('equalize.png'))
        self.connect(eq_action, SIGNAL("triggered()"), self.slot_equalize)

        df_action = QAction(parent)
        df_action.setText(_("Difference"))
        df_action.setIcon(get_icon('diff.png'))
        self.connect(df_action, SIGNAL("triggered()"), self.slot_difference)

        or_action = QAction(parent)
        or_action.setText(_("Optimal ROI"))
        or_action.setIcon(get_icon('roi.png'))
        self.connect(or_action, SIGNAL("triggered()"), self.slot_optimalroi)

        return [gr_action, eq_action, df_action, or_action]

    def get_algorithms_list(self):
        return []

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        pass

    def settings(self, name):
        pass

    def apply(self, name, settings=dict()):
        pass

    def slot_grayscale(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(GR_ACTION_TITLE + curr.title())
            image.data(grayscale(curr.data()))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def slot_equalize(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(EQ_ACTION_TITLE + curr.title())
            image.data(equalizeHist(curr.data()))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def slot_difference(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            filelist = QFileDialog.getOpenFileNames(None, "Select source images", ".")
            source_list = []
            if not filelist.isEmpty():
                logger.debug("Loading started...")
                i = 0
                for imfile in filelist:
                    i += 1
                    obj = loadImageObject(str(imfile))
                    source_list.append(obj['data'])
                    QCoreApplication.processEvents()
                logger.debug("Loading finished.")
            image = ImageProperties()
            image.title(DF_ACTION_TITLE + curr.title())
            image.data(imageDifference(curr.data(), source_list))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def slot_optimalroi(self):
        filelist = QFileDialog.getOpenFileNames(None, "Select source images", ".")
        source_list = []
        if not filelist.isEmpty():
            logger.debug("Loading started...")
            i = 0
            for imfile in filelist:
                i += 1
                obj = loadImageObject(str(imfile))
                source_list.append(obj)
                QCoreApplication.processEvents()
            logger.debug("Loading finished.")
        src = loadImageObject(str(filelist[0]))
        detector = OptimalROIDetector()
        source_list = detector.detect(source_list)

        i = 0
        for obj in source_list:
            image = ImageProperties()
            image.title(OR_ACTION_TITLE + "#" + str(i))
            image.data(obj['data'])
            image.height(obj['data'].shape[0])
            image.width(obj['data'].shape[1])
            self._imanager.add_image(image)
            i += 1
