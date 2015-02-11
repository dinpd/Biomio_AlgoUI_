from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, QObject
from guidata.qt.QtGui import QAction
from guidata.configtools import get_icon
from imageproperties import ImageProperties
from algorithms.cvtools.effects import equalizeHist, grayscale
from guiqwt.config import _
import logging

logger = logging.getLogger(__name__)

EQ_ACTION_TITLE = 'Action: EqualizeHist::'
GR_ACTION_TITLE = 'Action: Grayscale::'


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

        return [gr_action, eq_action]

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
