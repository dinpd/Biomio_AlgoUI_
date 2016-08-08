from guidata.qt.QtGui import (QAction, QWidget, QDockWidget, QFileDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton, QGroupBox, QDial, QCheckBox, QSpinBox)
from guidata.qt.QtCore import SIGNAL, pyqtSignal, QObject
from guidata.configtools import get_icon
from guiqwt.config import _
from plugins.FeatureDetectors.features_settings_widgets import BRISKWidget, ORBWidget, SURFWidget, MahotasSURFWidget
from biomio.algorithms.features import constructDetector, constructSettings, BRISKDetectorType, ORBDetectorType, \
    SURFDetectorType, MahotasSURFDetectorType
from biomio.algorithms.features.gabor_threads import build_filters, process_kernel, process
from biomio.algorithms.cascades.scripts_detectors import RotatedCascadesDetector
from biomio.algorithms.cascades.tools import getROIImage, loadScript
from biomio.algorithms.cvtools.visualization import drawKeypoints
from biomio.algorithms.features.features import FeatureDetector
from ui.algorithm_panel import AlgorithmPanel
from imageproperties import ImageProperties
import biomio.algorithms.cvtools.dsp as dsp
from biomio.algorithms.logger import logger
from aiplugins import IAlgorithmPlugin

ACTION_TITLE = 'Action: %s Features Detector::'
GF_ACTION_TITLE = 'Action: Gabor Filtering::'
SPC_ACTION_TITLE = 'Action: Spectrum::'
LPF_ACTION_TITLE = 'Action: Low Pass Filter::'
HPF_ACTION_TITLE = 'Action: High Pass Filter::'
RD_ACTION_TITLE = 'Action: ROI Detection::'


class FeatureDetectorsPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FeatureDetectorsPlugin, self).__init__()
        self._setwigets = []
        self._setwigets.append(self.create_feature_detect_widget())
        self._setwigets.append(self.create_gabor_widget())
        self._setwigets.append(self.create_dsp_widget())
        self._setwigets.append(self.create_roi_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        return [self.add_feature_action(parent), self.add_gabor_filter_action(parent),
                self.add_dsp_action(parent), self.add_roi_action(parent)]

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

    def add_feature_action(self, parent):
        feature_action = QAction(parent)
        feature_action.setText(_("Feature Detection"))
        feature_action.setIcon(get_icon('fea.png'))
        feature_action.setCheckable(True)
        self.connect(feature_action, SIGNAL("triggered(bool)"), self.settings_opened)
        return feature_action

    settings_opened = pyqtSignal(bool, name='settingsOpened')

    def create_feature_detect_widget(self):
        self._settings_dock = AlgorithmPanel()
        self._settings_dock.setEnableSerialProcessing(False)
        self._settings_dock.setWindowTitle("Feature Detector Settings")
        self._settings_dock.setVisible(False)
        self.settings_opened.connect(self._settings_dock.setVisible)
        self.connect(self._settings_dock, SIGNAL("applied()"), self.feature_detection)
        self._settings_dock.addAlgorithm(BRISKDetectorType, BRISKWidget())
        self._settings_dock.addAlgorithm(ORBDetectorType, ORBWidget())
        self._settings_dock.addAlgorithm(SURFDetectorType, SURFWidget())
        self._settings_dock.addAlgorithm(MahotasSURFDetectorType, MahotasSURFWidget())
        return self._settings_dock

    def feature_detection(self):
        curr = self._imanager.current_image()
        algo_settings = self._settings_dock.settings()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str(ACTION_TITLE % algo_settings['name'] + curr.title()))
            settings = constructSettings(algo_settings['name'])
            settings.importSettings(algo_settings['settings'])
            detector = FeatureDetector(constructDetector(algo_settings['name'], settings), mode=None)
            fea = dict()
            fea['data'] = curr.data()
            features = detector.detectAndCompute(curr.data())
            logger.debug(len(features['keypoints']))
            logger.debug(len(features['descriptors']))
            # keypair = [copyKeyPoint(keypoints[0])]
            # item = copyKeyPoint(keypoints[0])
            # item.pt = (100.0, 100.0)
            # keypair.append(item)
            # keypair.append(copyKeyPoint(keypoints[4]))
            # keypair.append(copyKeyPoint(keypoints[100]))
            # for index, keypoint in enumerate(keypoints):
            #     logger.debug("===========================")
            #     printKeyPoint(keypoint)
            #     logger.debug(descriptors[index])
            #     logger.debug("===========================")
            # matcher = Matcher(matcherForDetector(algo_settings['name']))
            # dtype = dtypeForDetector(algo_settings['name'])
            fea['keypoints'] = features['keypoints']
            fea['descriptors'] = features['descriptors']
            fea['keypoints_image'] = drawKeypoints(fea)
            # image.data(drawSelfMatches(fea, SelfMatching(fea['descriptors'], matcher, dtype, 2), key='keypoints_image'))
            # self_graph = SelfGraph(fea['keypoints'], 3, descriptors)
            # logger.debug(self_graph)
            # image.data(drawSelfGraph(fea, self_graph, key='keypoints_image'))
            image.data(fea['keypoints_image'])
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

    def add_roi_action(self, parent):
        roi_action = QAction(parent)
        roi_action.setText(_("ROI SAoS Detection"))
        roi_action.setIcon(get_icon('roi.png'))
        roi_action.setCheckable(True)
        self.connect(roi_action, SIGNAL("triggered(bool)"), self.roi_opened)
        return roi_action

    roi_opened = pyqtSignal(bool, name='roiOpened')

    def create_roi_widget(self):
        roi_dock = QDockWidget()
        roi_dock.setWindowTitle("Cascades ROIs SAoS Detector Settings")
        roi_dock.setVisible(False)
        self.roi_opened.connect(roi_dock.setVisible)
        roi_widget = QWidget(roi_dock)
        self._rotation_edit = QLineEdit(roi_widget)
        self._rotation_edit.setReadOnly(True)
        browse_rotation = QPushButton(roi_widget)
        browse_rotation.setText('Browse...')
        self.connect(browse_rotation, SIGNAL("clicked()"), self.load_rotation_script)
        self._script_edit = QLineEdit(roi_widget)
        self._script_edit.setReadOnly(True)
        browse = QPushButton(roi_widget)
        browse.setText('Browse...')
        self.connect(browse, SIGNAL("clicked()"), self.load_script)
        detect = QPushButton(roi_widget)
        detect.setText('Detect')
        self.connect(detect, SIGNAL("clicked()"), self.roi)
        detectAll = QPushButton(roi_widget)
        detectAll.setText('Detect All')
        self.connect(detectAll, SIGNAL("clicked()"), self.roiAll)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(detect)
        buttons_layout.addWidget(detectAll)
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self._rotation_edit)
        rotation_layout.addWidget(browse_rotation)
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self._script_edit)
        browse_layout.addWidget(browse)
        widget_layout = QVBoxLayout()
        widget_layout.addLayout(rotation_layout)
        widget_layout.addLayout(browse_layout)
        widget_layout.addLayout(buttons_layout)
        roi_widget.setLayout(widget_layout)
        roi_dock.setWidget(roi_widget)
        return roi_dock

    def load_rotation_script(self):
        filename = QFileDialog.getOpenFileName(None, "Select rotation script", ".")
        if not filename.isEmpty():
            self._rotation_edit.setText(filename)

    def load_script(self):
        filename = QFileDialog.getOpenFileName(None, "Select detection script", ".")
        if not filename.isEmpty():
            self._script_edit.setText(filename)

    def roi(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            detector = RotatedCascadesDetector(loadScript(str(self._rotation_edit.text())),
                                               loadScript(str(self._script_edit.text())))
            img, rois = detector.detect(curr.data())
            print rois
            for roi in rois:
                image = ImageProperties()
                image.title(str(RD_ACTION_TITLE + str(roi) + "::" + curr.title()))
                image.data(getROIImage(img, roi))
                image.height(curr.height())
                image.width(curr.width())
                self._imanager.add_image(image)
            if len(rois) == 0:
                image = ImageProperties()
                image.title(str(RD_ACTION_TITLE + "ROTATION" + "::" + curr.title()))
                image.data(img)
                image.height(curr.height())
                image.width(curr.width())
                self._imanager.add_image(image)

    def roiAll(self):
        if self._imanager:
            detector = RotatedCascadesDetector(loadScript(str(self._rotation_edit.text())),
                                               loadScript(str(self._script_edit.text())))
            images = []
            for curr in self._imanager.images():
                images.append(curr)
            for curr in images:
                img, rois = detector.detect(curr.data())
                for roi in rois:
                    image = ImageProperties()
                    image.title(str(RD_ACTION_TITLE + str(roi) + "::" + curr.title()))
                    image.data(getROIImage(img, roi))
                    image.height(curr.height())
                    image.width(curr.width())
                    self._imanager.add_image(image)
                if len(rois) == 0:
                    image = ImageProperties()
                    image.title(str(RD_ACTION_TITLE + "ROTATION" + "::" + curr.title()))
                    image.data(img)
                    image.height(curr.height())
                    image.width(curr.width())
                    self._imanager.add_image(image)
