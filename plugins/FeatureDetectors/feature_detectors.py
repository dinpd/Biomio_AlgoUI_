from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget,
                              QFormLayout, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton, QGroupBox, QDial, QCheckBox,
                              QDoubleValidator, QIntValidator)
from guidata.qt.QtCore import QObject
from guidata.configtools import get_icon
from imageproperties import ImageProperties
from algorithms.cvtools.visualization import drawKeypoints
from algorithms.features.detectors import BRISKDetector, ORBDetector
from algorithms.features.gabor_threads import build_filters, process_kernel, process
from logger import logger

from guiqwt.config import _

ACTION_TITLE = 'Action: %s Features Detector::'
GF_ACTION_TITLE = 'Action: Gabor Filtering::'


class FeatureDetectorsPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FeatureDetectorsPlugin, self).__init__()
        self._setwigets = []
        self._setwigets.append(self.create_brisk_widget())
        self._setwigets.append(self.create_orb_widget())
        self._setwigets.append(self.create_gabor_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        detector_menu = QMenu(parent)
        detector_menu.setTitle(_("Feature Detectors"))

        detector_menu.addAction(self.add_brisk_action(detector_menu))
        detector_menu.addAction(self.add_orb_action(detector_menu))
        return [detector_menu, self.add_gabor_filter_action(parent)]

    def get_algorithms_list(self):
        return []

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        return self._setwigets

    def settings(self, name):
        pass

    def apply(self, name, settings=dict()):
        pass

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
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str(ACTION_TITLE % 'BRISK' + curr.title()))
            detector = BRISKDetector(thresh=int(self._thresh_line_edit.text()),
                                     octaves=int(self._octaves_line_edit.text()),
                                     scale=float(self._pattern_scale_line_edit.text()))
            fea = dict()
            fea['data'] = curr.data()
            keypoints = detector.detect(curr.data())
            fea['keypoints'] = keypoints
            image.data(drawKeypoints(fea))
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
        if self._imanager and curr:
            image = ImageProperties()
            image.title(ACTION_TITLE % 'ORB' + curr.title())
            detector = ORBDetector(features=int(self._features_line_edit.text()),
                                   scale=float(self._scale_line_edit.text()),
                                   levels=int(self._levels_line_edit.text()))
            fea = dict()
            fea['data'] = curr.data()
            keypoints, descriptors = detector.detectAndCompute(curr.data())
            fea['keypoints'] = keypoints
            fea['descriptors'] = descriptors
            image.data(drawKeypoints(fea))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_gabor_filter_action(self, parent):
        gabor_action = QAction(parent)
        gabor_action.setText(_("Gabor Filtering"))
        gabor_action.setIcon(get_icon('gabor.png'))
        gabor_action.setCheckable(True)
        self.connect(gabor_action, SIGNAL("triggered(bool)"), self.gabor_opened)
        return gabor_action

    gabor_opened = pyqtSignal(bool, name='gaborOpened')

    def create_gabor_widget(self):
        gabor_dock = QDockWidget()
        gabor_dock.setWindowTitle("Gabor Filter Settings")
        gabor_dock.setVisible(False)
        self.gabor_opened.connect(gabor_dock.setVisible)
        gabor_widget = QWidget(gabor_dock)
        self.kernel_box = QGroupBox(gabor_widget)
        self.kernel_box.setTitle(_("Filter Kernel:"))
        self.allkernel_box = QCheckBox(gabor_widget)
        self.allkernel_box.setText(_("Apply all kernels"))
        self.connect(self.allkernel_box, SIGNAL("clicked()"), self.gabor_temp)
        self.kernel_dial = QDial(gabor_widget)
        self.kernel_dial.setMaximum(len(build_filters()) + 1)
        self.kernel_dial.setSingleStep(1)
        self.kernel_dial.setValue(self.kernel_dial.maximum())
        self.kernel_dial.setWrapping(True)
        self.connect(self.kernel_dial, SIGNAL("valueChanged(int)"), self.gabor_temp)
        kern_layout = QVBoxLayout()
        kern_layout.addWidget(self.allkernel_box)
        kern_layout.addWidget(self.kernel_dial)
        self.kernel_box.setLayout(kern_layout)
        accept = QPushButton(gabor_widget)
        accept.setText('Accept')
        self.connect(accept, SIGNAL("clicked()"), self.gabor_filter)
        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self.kernel_box)
        button_layout = QHBoxLayout()
        button_layout.addStretch(2)
        button_layout.addWidget(accept)
        widget_layout.addLayout(button_layout)
        gabor_widget.setLayout(widget_layout)
        gabor_dock.setWidget(gabor_widget)
        return gabor_dock

    def gabor_temp(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(curr.title())

            gabor = build_filters()
            if self.allkernel_box.isChecked():
                self.kernel_dial.setEnabled(False)
                image.data(process(curr.data(), gabor))
            else:
                self.kernel_dial.setEnabled(True)
                value = self.kernel_dial.value() - 1
                if len(gabor) > value >= 0:
                    image.data(process_kernel(curr.data(), gabor[value]))
                else:
                    image.data(curr.data())

            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_temp_image(image)

    def gabor_filter(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(GF_ACTION_TITLE + curr.title())

            gabor = build_filters()
            if self.allkernel_box.isChecked():
                image.data(process(curr.data(), gabor))
            else:
                value = self.kernel_dial.value() - 1
                if len(gabor) > value >= 0:
                    image.data(process_kernel(curr.data(), gabor[value]))
                else:
                    image.data(curr.data())

            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)