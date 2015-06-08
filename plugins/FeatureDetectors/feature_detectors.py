from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget,
                              QFormLayout, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton, QGroupBox, QDial, QCheckBox, QSpinBox,
                              QDoubleValidator, QIntValidator)
from guidata.qt.QtCore import QObject
from guidata.configtools import get_icon
from imageproperties import ImageProperties
from algorithms.cvtools.visualization import drawKeypoints
from algorithms.features.detectors import BRISKDetector, ORBDetector
from algorithms.features.gabor_threads import build_filters, process_kernel, process
from logger import logger
import algorithms.cvtools.dsp as dsp
import cv2

from guiqwt.config import _

ACTION_TITLE = 'Action: %s Features Detector::'
GF_ACTION_TITLE = 'Action: Gabor Filtering::'
PD_ACTION_TITLE = 'Action: Palm Detection::'
SPC_ACTION_TITLE = 'Action: Spectrum::'
LPF_ACTION_TITLE = 'Action: Low Pass Filter::'
HPF_ACTION_TITLE = 'Action: High Pass Filter::'


class FeatureDetectorsPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FeatureDetectorsPlugin, self).__init__()
        self._setwigets = []
        self._setwigets.append(self.create_brisk_widget())
        self._setwigets.append(self.create_orb_widget())
        self._setwigets.append(self.create_gabor_widget())
        self._setwigets.append(self.create_palm_widget())
        self._setwigets.append(self.create_dsp_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        detector_menu = QMenu(parent)
        detector_menu.setTitle(_("Feature Detectors"))

        detector_menu.addAction(self.add_brisk_action(detector_menu))
        detector_menu.addAction(self.add_orb_action(detector_menu))
        return [detector_menu, self.add_gabor_filter_action(parent),
                self.add_palm_detect_action(parent), self.add_dsp_action(parent)]

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
            logger.debug(len(keypoints))
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
            logger.debug(len(keypoints))
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

    def add_palm_detect_action(self, parent):
        palm_action = QAction(parent)
        palm_action.setText(_("Palm Detection"))
        palm_action.setIcon(get_icon('palm.png'))
        palm_action.setCheckable(True)
        self.connect(palm_action, SIGNAL("triggered(bool)"), self.palm_opened)
        return palm_action

    palm_opened = pyqtSignal(bool, name='palmOpened')

    def create_palm_widget(self):
        palm_dock = QDockWidget()
        palm_dock.setWindowTitle("Palm Detection Settings")
        palm_dock.setVisible(False)
        self.palm_opened.connect(palm_dock.setVisible)
        palm_widget = QWidget(palm_dock)

        accept = QPushButton(palm_widget)
        accept.setText('Accept')
        self.connect(accept, SIGNAL("clicked()"), self.palm_detect)
        widget_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addStretch(2)
        button_layout.addWidget(accept)
        widget_layout.addLayout(button_layout)
        palm_widget.setLayout(widget_layout)
        palm_dock.setWidget(palm_widget)
        return palm_dock

    def palm_detect(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(PD_ACTION_TITLE + curr.title())

            gabor = build_filters()
            images = list()
            for i in range(0, len(gabor), 1):
                logger.debug("Applying Gabor Filter. Kernel No. " + str(i))
                images.append(cv2.threshold(process_kernel(curr.data(), gabor[i]), 5, 255, 0)[1])

            result = images[0]
            for j in range(0, curr.height(), 1):
                for i in range(0, curr.width(), 1):
                    b = 0
                    g = 0
                    r = 0
                    for k in range(0, len(images), 1):
                        img = images[k]
                        pixel = img[j, i]
                        b += pixel[0]
                        g += pixel[1]
                        r += pixel[2]
                    result[j, i] = [b / len(images), g / len(images), r / len(images)]

            image.data(cv2.threshold(result, 200, 255, 0)[1])
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_dsp_action(self, parent):
        dsp_action = QAction(parent)
        dsp_action.setText(_("Digital Signal Processing"))
        dsp_action.setIcon(get_icon('dsp.png'))
        dsp_action.setCheckable(True)
        self.connect(dsp_action, SIGNAL("triggered(bool)"), self.dsp_opened)
        return dsp_action

    dsp_opened = pyqtSignal(bool, name='dspOpened')

    def create_dsp_widget(self):
        dsp_dock = QDockWidget()
        dsp_dock.setWindowTitle("DSP Settings")
        dsp_dock.setVisible(False)
        self.dsp_opened.connect(dsp_dock.setVisible)
        dsp_widget = QWidget(dsp_dock)

        self._sizeBox = QSpinBox(dsp_widget)
        self._sizeBox.setMinimum(0)
        self._sizeBox.setMaximum(1000000)
        self._sizeBox.setSingleStep(1)
        self._sizeBox.setValue(30)

        spc_apply = QPushButton(dsp_widget)
        spc_apply.setText('Spectrum')
        self.connect(spc_apply, SIGNAL("clicked()"), self.spc)
        lpf_apply = QPushButton(dsp_widget)
        lpf_apply.setText('Low Pass Filter')
        self.connect(lpf_apply, SIGNAL("clicked()"), self.lpf)
        hpf_apply = QPushButton(dsp_widget)
        hpf_apply.setText('High Pass Filter')
        self.connect(hpf_apply, SIGNAL("clicked()"), self.hpf)
        widget_layout = QVBoxLayout()
        control_layout = QFormLayout()
        control_layout.addRow("Filter Kernel Size: ", self._sizeBox)
        widget_layout.addLayout(control_layout)
        button_layout = QHBoxLayout()
        button_layout.addWidget(spc_apply)
        button_layout.addWidget(lpf_apply)
        button_layout.addWidget(hpf_apply)
        button_layout.addStretch(2)
        widget_layout.addLayout(button_layout)
        dsp_widget.setLayout(widget_layout)
        dsp_dock.setWidget(dsp_widget)
        return dsp_dock

    def spc(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(SPC_ACTION_TITLE + curr.title())
            image.data(dsp.dsp_spectrum(curr.data()))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def lpf(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(LPF_ACTION_TITLE + curr.title())
            mask = dsp.dsp_lpf_mask(curr.data(), self._sizeBox.value())
            image.data(dsp.dsp_filter(curr.data(), mask))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def hpf(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(HPF_ACTION_TITLE + curr.title())
            mask = dsp.dsp_hpf_mask(curr.data(), self._sizeBox.value())
            image.data(dsp.dsp_filter(curr.data(), mask))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)