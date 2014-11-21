from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL
from guidata.qt.QtCore import QObject
from guidata.qt.QtGui import QAction
from guidata.configtools import get_icon
from view import ImageParam
from features.tools import equalizeHist

from guiqwt.config import _

ACTION_TITLE = 'Action: EqualizeHist::'

class EqualizeHistPlugin(IAlgorithmPlugin, QObject):
    def set_image_manager(self, manager):
        self._imanager = manager

    def get_action(self, parent):
        action = QAction(parent)
        action.setText(_("Equalize Histogram"))
        action.setIcon(get_icon('equalize.png'))
        action.setShortcut("Ctrl+E")
        self.connect(action, SIGNAL("triggered()"), self.equalize)
        return action

    def get_interfaces(self):
        pass

    def equalize(self):
        curr = self._imanager.current_image()
        if (self._imanager and curr):
            image = ImageParam()
            image.title = ACTION_TITLE + curr.title
            image.data = equalizeHist(curr.data)
            image.height, image.width = image.data.shape
            self._imanager.add_image(image)
