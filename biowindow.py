from guidata.qt.QtGui import QMainWindow
from guidata.qt.QtCore import (Qt)
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.qt.compat import getsavefilename, getopenfilenames

from guiqwt.config import _
from guiqwt import io

import sys

from view import ImageManager
from algorithmsmanager import AlgorithmsManager
from gui_logger import LogManager
from logger import logger

APP_NAME = _("BioQ Algorithms Interface")
VERSION = '0.1.0'


class BioWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self._amanager = None
        self._imanager = None
        self.setup()

    def setup(self):
        self.setWindowIcon(get_icon('python.png'))
        self.setWindowTitle(APP_NAME)

        self._imanager = ImageManager(self)
        self._amanager = AlgorithmsManager(self._imanager)
        self.init_actions()
        self.menuBar().addMenu(self._imanager.get_view().viewer_menu())
        self.menuBar().addMenu(self._amanager.algorithms_menu())
        self.init_widgets()

        toolbar = self.addToolBar("Image")
        # self._imanager.get_view().add_toolbar(toolbar, "default")
        # self._imanager.get_view().register_all_image_tools()
        self.setCentralWidget(self._imanager.get_view())
        self._imanager.install_ui_manager()

        self._logmanager = LogManager(self)
        self.addDockWidget(Qt.DockWidgetArea(8), self._logmanager)

    def init_actions(self):
        file_menu = self.menuBar().addMenu(_("File"))
        open_action = create_action(self, _("Open..."),
                                    shortcut="Ctrl+O",
                                    icon=get_icon('open.png'),
                                    tip=_("Open an image"),
                                    triggered=self.open_image)
        save_action = create_action(self, _("Save"),
                                    shortcut="Ctrl+S",
                                    icon=get_icon('save.png'),
                                    tip=_("Save an image"),
                                    triggered=self.save_image)
        close_action = create_action(self, _("Close"),
                                     shortcut="Del",
                                     icon=get_icon('close.png'),
                                     tip=_("Close an current image"),
                                     triggered=self.close_image)
        close_all_action = create_action(self, _("Close All"),
                                     icon=get_icon('closeall.png'),
                                     tip=_("Close an all images"),
                                     triggered=self.close_all)
        quit_action = create_action(self, _("Quit"),
                                    shortcut="Ctrl+Q",
                                    icon=get_std_icon("DialogCloseButton"),
                                    tip=_("Quit application"),
                                    triggered=self.close)
        add_actions(file_menu, (open_action, save_action, close_action, close_all_action, None, quit_action))

        file_toolbar = self.addToolBar("FileToolBar")
        add_actions(file_toolbar, (open_action, save_action, close_action, close_all_action))

        log_menu = self.menuBar().addMenu(_("Log"))
        clear_action = create_action(self, _("Clear"),
                                     icon=get_icon('clear.png'),
                                     tip=_("Clear log"),
                                     triggered=self.clear)
        log_menu.addAction(clear_action)

    def init_widgets(self):
        widgets = self._amanager.algorithms_settings()
        for widget in widgets:
            if widget:
                self.addDockWidget(Qt.DockWidgetArea(1), widget)

    def open_image(self):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filenames, _filter = getopenfilenames(self, _("Open"), "")
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        if len(filenames) > 0:
            for filename in filenames:
                self._imanager.add_image_from_file(filename)

    def save_image(self):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filename, _filter = getsavefilename(self, _("Save"), "",
                                            io.iohandler.get_filters('save'))
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        if filename:
            self._imanager.save_image(filename, self._imanager.current_image_index())

    def close_image(self):
        self._imanager.delete_image(self._imanager.current_image_index())

    def close_all(self):
        self._imanager.delete_all()

    def clear(self):
        self._logmanager.clear()
