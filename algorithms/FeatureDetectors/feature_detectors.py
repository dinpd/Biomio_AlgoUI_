from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget,
                              QFormLayout,
                              QLineEdit, QPushButton,
                              QDoubleValidator, QIntValidator)
from guidata.qt.QtCore import QObject
from guidata.configtools import get_icon
from imageproperties import ImageProperties
from features.detectors import BRISKDetector, ORBDetector, ImageFeatures
from features.tools import paintKeypoints, grayscale

from guiqwt.config import _

ACTION_TITLE = 'Action: %s Features Detector::'


class FeatureDetectorsPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FeatureDetectorsPlugin, self).__init__()
        self._setwigets = []
        self._setwigets.append(self.create_brisk_widget())
        self._setwigets.append(self.create_orb_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        detector_menu = QMenu(parent)
        detector_menu.setTitle(_("Feature Detectors"))

        detector_menu.addAction(self.add_brisk_action(detector_menu))
        detector_menu.addAction(self.add_orb_action(detector_menu))
        print detector_menu
        return [detector_menu]

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        return self._setwigets

    def add_brisk_action(self, parent):
        brisk_action = QAction(parent)
        brisk_action.setText(_("BRISK Features Detection"))
        brisk_action.setIcon(get_icon('brisk.png'))
        brisk_action.setCheckable(True)
        self.connect(brisk_action, SIGNAL("triggered(bool)"), self.brisk_opened)
        return brisk_action

    brisk_opened = pyqtSignal(bool, name='briskOpened')

    def create_brisk_widget(self):
        brisk_dock = QDockWidget()
        brisk_dock.setWindowTitle("BRISK Feature Detector Settings")
        brisk_dock.setVisible(False)
        self.brisk_opened.connect(brisk_dock.setVisible)
        brisk_widget = QWidget(brisk_dock)
        self._thresh_line_edit = QLineEdit(brisk_widget)
        self._thresh_line_edit.setValidator(QIntValidator())
        self._thresh_line_edit.setText('10')
        self._octaves_line_edit = QLineEdit(brisk_widget)
        self._octaves_line_edit.setValidator(QIntValidator())
        self._octaves_line_edit.setText('0')
        self._pattern_scale_line_edit = QLineEdit(brisk_widget)
        self._pattern_scale_line_edit.setValidator(QDoubleValidator())
        self._pattern_scale_line_edit.setText('1.0')
        detect = QPushButton(brisk_widget)
        detect.setText('Detect')
        self.connect(detect, SIGNAL("clicked()"), self.brisk)
        widget_layout = QFormLayout()
        widget_layout.addRow('Thresh', self._thresh_line_edit)
        widget_layout.addRow('Octaves', self._octaves_line_edit)
        widget_layout.addRow('Pattern Scale', self._pattern_scale_line_edit)
        widget_layout.addWidget(detect)
        brisk_widget.setLayout(widget_layout)
        brisk_dock.setWidget(brisk_widget)
        return brisk_dock

    def brisk(self):
        curr = self._imanager.current_image()
        if (self._imanager and curr):
            image = ImageProperties()
            image.title(str(ACTION_TITLE % 'BRISK' + curr.title()))
            detector = BRISKDetector(thresh=int(self._thresh_line_edit.text()),
                                     octaves=int(self._octaves_line_edit.text()),
                                     scale=float(self._pattern_scale_line_edit.text()))
            fea = ImageFeatures()
            fea.image(curr.data())
            keypoints = detector.detect(curr.data())
            fea.keypoints(keypoints)
            image.data(paintKeypoints(fea))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_orb_action(self, parent):
        orb_action = QAction(parent)
        orb_action.setText(_("ORB Features Detection"))
        orb_action.setIcon(get_icon('orb.png'))
        orb_action.setCheckable(True)
        self.connect(orb_action, SIGNAL("triggered(bool)"), self.orb_opened)
        return orb_action

    orb_opened = pyqtSignal(bool, name='orbOpened')

    def create_orb_widget(self):
        orb_dock = QDockWidget()
        orb_dock.setWindowTitle("ORB Feature Detector Settings")
        orb_dock.setVisible(False)
        self.orb_opened.connect(orb_dock.setVisible)
        orb_widget = QWidget(orb_dock)
        self._features_line_edit = QLineEdit(orb_widget)
        self._features_line_edit.setValidator(QIntValidator())
        self._features_line_edit.setText('500')
        self._scale_line_edit = QLineEdit(orb_widget)
        self._scale_line_edit.setValidator(QDoubleValidator())
        self._scale_line_edit.setText('1.2')
        self._levels_line_edit = QLineEdit(orb_widget)
        self._levels_line_edit.setValidator(QIntValidator())
        self._levels_line_edit.setText('8')
        detect = QPushButton(orb_widget)
        detect.setText('Detect')
        self.connect(detect, SIGNAL("clicked()"), self.orb)
        widget_layout = QFormLayout()
        widget_layout.addRow('Number of Features', self._features_line_edit)
        widget_layout.addRow('Scale Factor', self._scale_line_edit)
        widget_layout.addRow('Number of Levels', self._levels_line_edit)
        widget_layout.addWidget(detect)
        orb_widget.setLayout(widget_layout)
        orb_dock.setWidget(orb_widget)
        return orb_dock

    def orb(self):
        curr = self._imanager.current_image()
        if (self._imanager and curr):
            image = ImageProperties()
            image.title(ACTION_TITLE % 'ORB' + curr.title())
            detector = ORBDetector(features=int(self._features_line_edit.text()),
                                   scale=float(self._scale_line_edit.text()),
                                   levels=int(self._levels_line_edit.text()))
            fea = ImageFeatures()
            fea.image(curr.data())
            keypoints = detector.detect(curr.data())
            fea.keypoints(keypoints)
            image.data(paintKeypoints(fea))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)