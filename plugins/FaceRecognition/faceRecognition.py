from logger import logger

from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget, QListWidget,
                              QFileDialog,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QPushButton, QGroupBox, QDoubleSpinBox,
                              QSpinBox, QLabel, QProgressBar, QLineEdit)
from guidata.qt.QtCore import QObject, QCoreApplication
from guidata.configtools import get_icon
from imageproperties import ImageProperties
import algorithms.faces.biom.faces as fs
from algorithms.cvtools.visualization import drawRectangle
from algorithms.features.classifiers import CascadeROIDetector, getROIImage, CascadeClassifierSettings
from algorithms.features.matchers import FlannMatcher
from algorithms.faces.biom.utils import files_list
from plugins.FaceRecognition.detdialog import DetectorSettingsDialog
from algorithms.recognition.detcreator import (DetectorCreator,
                                               ClustersObjectMatching, IntersectMatching,
                                               FaceCascadeClassifier, EyesCascadeClassifier)
from algorithms.imgobj import loadImageObject
from guiqwt.config import _
import json
import os


VerificationAlgorithm = "KeypointsVerificationAlgorithm"


class FaceRecognitionPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FaceRecognitionPlugin, self).__init__()
        self._setwigets = []
        self.init_keysrecg_algorithm()
        self._setwigets.append(self.create_detect_widget())
        self._setwigets.append(self.create_keysrecg_widget())
        self._setwigets.append(self.create_compare_widget())
        self._setwigets.append(self.create_kod_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        recognition_menu = QMenu(parent)
        recognition_menu.setTitle(_("Face Recognition"))

        recognition_menu.addAction(self.add_detect_action(recognition_menu))
        recognition_menu.addAction(self.add_keysrecg_action(recognition_menu))
        recognition_menu.addAction(self.add_kod_action(recognition_menu))
        return [recognition_menu, self.add_compare_action(recognition_menu)]

    def get_algorithms_list(self):
        return [VerificationAlgorithm]

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        return self._setwigets

    def settings(self, name):
        setting = dict()
        if name == VerificationAlgorithm:
            setting['database'] = "default"
            setting['max_neigh'] = self.checkMaxNeigh
            setting['data'] = None
        return setting

    @staticmethod
    def checkMaxNeigh(value):
        res = False
        if type(value) == type(float):
            if 0 < value < 1000.0:
                res = True
        return res

    def add_detect_action(self, parent):
        detect_action = QAction(parent)
        detect_action.setText(_("Face Detection"))
        detect_action.setIcon(get_icon('fdetect.png'))
        detect_action.setCheckable(True)
        self.connect(detect_action, SIGNAL("triggered(bool)"), self.detect_opened)
        return detect_action

    detect_opened = pyqtSignal(bool, name='detectOpened')

    def create_detect_widget(self):
        detect_dock = QDockWidget()
        detect_dock.setWindowTitle("Face Detection Settings")
        detect_dock.setVisible(False)
        self.detect_opened.connect(detect_dock.setVisible)
        detect_widget = QWidget(detect_dock)
        self._cascades_box = QGroupBox(detect_widget)
        self._cascades_box.setTitle(_("Cascades:"))

        scale_label = QLabel(detect_widget)
        scale_label.setText(_("Scale Factor:"))
        self._scaleBox = QDoubleSpinBox(detect_widget)
        self._scaleBox.setSingleStep(0.10)
        self._scaleBox.setMinimum(1.01)
        self._scaleBox.setValue(1.1)
        self.connect(self._scaleBox, SIGNAL("valueChanged(double)"), self.face_detect)
        scale_layout = QVBoxLayout()
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self._scaleBox)

        neighbors_label = QLabel(detect_widget)
        neighbors_label.setText(_("Min Neighbors:"))
        self._neighborsBox = QSpinBox(detect_widget)
        self._neighborsBox.setValue(3)
        self.connect(self._neighborsBox, SIGNAL("valueChanged(int)"), self.face_detect)
        neighbors_layout = QVBoxLayout()
        neighbors_layout.addWidget(neighbors_label)
        neighbors_layout.addWidget(self._neighborsBox)

        param_layout = QHBoxLayout()
        param_layout.addLayout(scale_layout)
        param_layout.addLayout(neighbors_layout)

        self._cascades_list = QListWidget(detect_widget)
        self.connect(self._cascades_list, SIGNAL("currentRowChanged(int)"), self.face_detect)
        add_button = QPushButton(detect_widget)
        add_button.setText('Add')
        self.connect(add_button, SIGNAL("clicked()"), self.add_cascade)

        cut_button = QPushButton(detect_widget)
        cut_button.setText('Cut')
        self.connect(cut_button, SIGNAL("clicked()"), self.cut_image)

        right_layout = QVBoxLayout()
        right_layout.addWidget(add_button)
        right_layout.addWidget(cut_button)
        right_layout.addStretch(2)

        cascades_layout = QHBoxLayout()
        cascades_layout.addWidget(self._cascades_list)
        cascades_layout.addLayout(right_layout)

        box_layout = QVBoxLayout()
        box_layout.addLayout(param_layout)
        box_layout.addLayout(cascades_layout)
        self._cascades_box.setLayout(box_layout)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self._cascades_box)
        detect_widget.setLayout(widget_layout)
        detect_dock.setWidget(detect_widget)
        return detect_dock

    def add_cascade(self):
        filenames = QFileDialog.getOpenFileNames(None, "Select cascades", ".")
        if not filenames.isEmpty():
            self._cascades_list.addItems(filenames)

    def cut_image(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            casc = self._cascades_list.item(self._cascades_list.currentRow()).text()

            img = curr.data()
            # Refactor code
            ff = CascadeROIDetector()
            ff.classifierSettings.scaleFactor = self._scaleBox.value()
            ff.classifierSettings.minNeighbors = self._neighborsBox.value()
            ff.add_cascade(str(casc))

            faces = ff.detect(img, True)

            logger.info("Detection finished.")
            for face in faces:
                image = ImageProperties()
                image.title(str('ROI Detection by Haar Cascade::' + str(face) + '::' + curr.title()))
                det = getROIImage(img, face)
                image.data(det)
                image.height(curr.height())
                image.width(curr.width())
                self._imanager.add_image(image)

    def face_detect(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str('ROI Detection by Haar Cascade::' + curr.title()))

            casc = self._cascades_list.item(self._cascades_list.currentRow()).text()

            img = curr.data()
            # Refactor code
            ff = CascadeROIDetector()
            ff.classifierSettings.scaleFactor = self._scaleBox.value()
            ff.classifierSettings.minNeighbors = self._neighborsBox.value()
            ff.add_cascade(str(casc))

            faces = ff.detect(img, True)

            inx = 0
            for face in faces:
                print face
                img = drawRectangle(img, face, (0, 0, 0))
                inx += 1

            logger.info("Detection finished.")
            image.data(img)
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_temp_image(image)

    def add_kod_action(self, parent):
        kod_action = QAction(parent)
        kod_action.setText(_("Keypoints Object Detectors"))
        kod_action.setIcon(get_icon('kod.png'))
        kod_action.setCheckable(True)
        self.connect(kod_action, SIGNAL("triggered(bool)"), self.kod_opened)
        return kod_action

    kod_opened = pyqtSignal(bool, name='kodOpened')

    def create_kod_widget(self):
        kod_dock = QDockWidget()
        kod_dock.setWindowTitle("Keypoints Object Detectors Settings")
        kod_dock.setVisible(False)
        self.kod_opened.connect(kod_dock.setVisible)
        kod_widget = QWidget(kod_dock)
        self._kod_settings_box = QGroupBox(kod_widget)
        self._kod_settings_box.setTitle(_("Settings:"))

        change_button = QPushButton(self._kod_settings_box)
        change_button.setText(_("Change"))
        self.connect(change_button, SIGNAL("clicked()"), self.det_change)

        form_layout = QFormLayout()
        form_layout.addRow(_("Keypoints Detector Settings:"), change_button)

        face_cascade_box = QGroupBox(kod_widget)
        face_cascade_box.setTitle(_("Face Cascade ROI Detector Settings:"))

        self._kod_face_scaleBox = QDoubleSpinBox(face_cascade_box)
        self._kod_face_scaleBox.setSingleStep(0.10)
        self._kod_face_scaleBox.setMinimum(1.01)
        self._kod_face_scaleBox.setValue(1.1)
        self._kod_face_neighborsBox = QSpinBox(face_cascade_box)
        self._kod_face_neighborsBox.setValue(2)

        face_cascade_layout = QFormLayout()
        face_cascade_layout.addRow(_("Scale Factor:"), self._kod_face_scaleBox)
        face_cascade_layout.addRow(_("Min Neighbors:"), self._kod_face_neighborsBox)
        face_cascade_box.setLayout(face_cascade_layout)

        eye_cascade_box = QGroupBox(kod_widget)
        eye_cascade_box.setTitle(_("Eyes Cascade ROI Detector Settings:"))

        self._kod_eye_scaleBox = QDoubleSpinBox(eye_cascade_box)
        self._kod_eye_scaleBox.setSingleStep(0.10)
        self._kod_eye_scaleBox.setMinimum(1.01)
        self._kod_eye_scaleBox.setValue(1.1)
        self._kod_eye_neighborsBox = QSpinBox(eye_cascade_box)
        self._kod_eye_neighborsBox.setValue(2)

        eye_cascade_layout = QFormLayout()
        eye_cascade_layout.addRow(_("Scale Factor:"), self._kod_eye_scaleBox)
        eye_cascade_layout.addRow(_("Min Neighbors:"), self._kod_eye_neighborsBox)
        eye_cascade_box.setLayout(eye_cascade_layout)

        settings_layout = QVBoxLayout()
        settings_layout.addLayout(form_layout)
        settings_layout.addWidget(face_cascade_box)
        settings_layout.addWidget(eye_cascade_box)
        settings_layout.addStretch(2)

        self._kod_settings_box.setLayout(settings_layout)

        apply_button = QPushButton(kod_widget)
        apply_button.setText(_("Apply"))
        self.connect(apply_button, SIGNAL("clicked()"), self.kod_apply)

        button_layout = QHBoxLayout()
        button_layout.addStretch(2)
        button_layout.addWidget(apply_button)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self._kod_settings_box)
        widget_layout.addLayout(button_layout)
        widget_layout.addStretch(2)
        kod_widget.setLayout(widget_layout)
        kod_dock.setWidget(kod_widget)
        return kod_dock

    def kod_apply(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            data = {
                'path': curr.path(),
                'name': curr.title(),
                'data': curr.data()
            }
            face_cascade_settings = CascadeClassifierSettings()
            face_cascade_settings.minNeighbors = self._kod_face_neighborsBox.value()
            face_cascade_settings.scaleFactor = self._kod_face_scaleBox.value()

            eye_cascade_settings = CascadeClassifierSettings()
            eye_cascade_settings.minNeighbors = self._kod_eye_neighborsBox.value()
            eye_cascade_settings.scaleFactor = self._kod_eye_scaleBox.value()

            creator = DetectorCreator(type=IntersectMatching)
            creator.addClassifier(FaceCascadeClassifier, face_cascade_settings)
            creator.addCascade(FaceCascadeClassifier,
                               "algorithms/data/haarcascades/haarcascade_frontalface_alt_tree.xml")
            creator.addCascade(FaceCascadeClassifier,
                               "algorithms/data/haarcascades/haarcascade_frontalface_alt2.xml")
            creator.addCascade(FaceCascadeClassifier,
                               "algorithms/data/haarcascades/haarcascade_frontalface_alt.xml")
            creator.addCascade(FaceCascadeClassifier,
                               "algorithms/data/haarcascades/haarcascade_frontalface_default.xml")
            creator.addClassifier(EyesCascadeClassifier, eye_cascade_settings)
            creator.addCascade(EyesCascadeClassifier,
                               "algorithms/data/haarcascades/haarcascade_mcs_eyepair_big.xml")
            detector = creator.detector()
            # detector.kodsettings.neighbours_distance = self._neighBox.value()
            detector.kodsettings.detector_type = self.settings_dialog.result_type()
            detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            detector.kodsettings.orb_settings = self.settings_dialog.orb()
            detector.detect(data)
            print data.keys()
            imag = ImageProperties()
            imag.title(str('ROI::' + curr.title()))
            imag.data(data['roi'])
            imag.height(data['roi'].shape[1])
            imag.width(data['roi'].shape[0])
            self._imanager.add_image(imag)
            image = ImageProperties()
            image.title(str('Keypoints Object Detector::' + curr.title()))
            image.data(data['clustering'])
            image.height(data['clustering'].shape[1])
            image.width(data['clustering'].shape[0])
            self._imanager.add_image(image)

    def init_keysrecg_algorithm(self):
        self.settings_dialog = DetectorSettingsDialog()
        self.settings_dialog.setWindowTitle(_("Keypoints Detector Settings"))
        self.init_detector()

    def init_detector(self):
        creator = DetectorCreator(type=ClustersObjectMatching)
        creator.addClassifier(FaceCascadeClassifier)
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt_tree.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt2.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_alt.xml")
        creator.addCascade(FaceCascadeClassifier, "algorithms/data/haarcascades/haarcascade_frontalface_default.xml")
        settings = CascadeClassifierSettings()
        settings.minNeighbors = 1
        creator.addClassifier(EyesCascadeClassifier, settings)
        creator.addCascade(EyesCascadeClassifier, "algorithms/data/haarcascades/haarcascade_mcs_eyepair_big.xml")
        self._keysrecg_detector = creator.detector()

    def add_keysrecg_action(self, parent):
        keysrecg_action = QAction(parent)
        keysrecg_action.setText(_("Keypoints-based Face Recognition"))
        keysrecg_action.setIcon(get_icon('krecg.png'))
        keysrecg_action.setCheckable(True)
        self.connect(keysrecg_action, SIGNAL("triggered(bool)"), self.keysrecg_opened)
        return keysrecg_action

    keysrecg_opened = pyqtSignal(bool, name='keysrecgOpened')

    def create_keysrecg_widget(self):
        keysrecg_dock = QDockWidget()
        keysrecg_dock.setWindowTitle("Keypoints Face Recognition Settings")
        keysrecg_dock.setVisible(False)
        self.keysrecg_opened.connect(keysrecg_dock.setVisible)
        keysrecg_widget = QWidget(keysrecg_dock)
        self._settings_box = QGroupBox(keysrecg_widget)
        self._settings_box.setTitle(_("Settings:"))

        change_button = QPushButton(self._settings_box)
        change_button.setText(_("Change"))
        self.connect(change_button, SIGNAL("clicked()"), self.det_change)

        self._neighBox = QDoubleSpinBox(self._settings_box)
        self._neighBox.setSingleStep(0.10)
        self._neighBox.setMinimum(0)
        self._neighBox.setMaximum(10000)
        self._neighBox.setValue(1.0)

        self._probBox = QDoubleSpinBox(self._settings_box)
        self._probBox.setSingleStep(1.0)
        self._probBox.setMinimum(0)
        self._probBox.setMaximum(100)
        self._probBox.setValue(10.0)

        settings_layout = QFormLayout()
        settings_layout.addRow(_("Keypoints Detector Settings:"), change_button)
        settings_layout.addRow(_("Max Neighbours Distance:"), self._neighBox)
        settings_layout.addRow(_("Min Probability:"), self._probBox)
        self._settings_box.setLayout(settings_layout)

        self._sources_box = QGroupBox(keysrecg_widget)
        self._sources_box.setTitle(_("Sources:"))

        self._load_bar = QProgressBar(keysrecg_widget)
        self._load_bar.setMinimum(0)
        self._load_bar.setMaximum(100)
        self._load_bar.setValue(100)

        self._load_label = QLabel(keysrecg_widget)

        add_button = QPushButton(keysrecg_widget)
        add_button.setText('Add')
        self.connect(add_button, SIGNAL("clicked()"), self.add_source)
        add_img_button = QPushButton(keysrecg_widget)
        add_img_button.setText('Add Images')
        self.connect(add_img_button, SIGNAL("clicked()"), self.add_source_images)
        clear_button = QPushButton(keysrecg_widget)
        clear_button.setText(_('Clear'))
        self.connect(clear_button, SIGNAL("clicked()"), self.clear_detector)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self._load_bar)
        top_layout.addWidget(add_button)
        top_layout.addWidget(add_img_button)
        top_layout.addWidget(clear_button)

        sources_layout = QVBoxLayout()
        sources_layout.addLayout(top_layout)
        sources_layout.addWidget(self._load_label)
        self._sources_box.setLayout(sources_layout)

        identify_button = QPushButton(keysrecg_widget)
        identify_button.setText(_('Identify'))
        self.connect(identify_button, SIGNAL("clicked()"), self.keysrecg)

        iden_all_button = QPushButton(keysrecg_widget)
        iden_all_button.setText(_('Identify All'))
        self.connect(iden_all_button, SIGNAL("clicked()"), self.identify_all)

        verify_button = QPushButton(keysrecg_widget)
        verify_button.setText(_('Verify'))
        self.connect(verify_button, SIGNAL("clicked()"), self.verify)

        verify_all_button = QPushButton(keysrecg_widget)
        verify_all_button.setText(_('Verify All'))
        self.connect(verify_all_button, SIGNAL("clicked()"), self.verify_all)

        import_button = QPushButton(keysrecg_widget)
        import_button.setText(_('Import'))
        self.connect(import_button, SIGNAL("clicked()"), self.import_database)

        export_button = QPushButton(keysrecg_widget)
        export_button.setText(_('Export'))
        self.connect(export_button, SIGNAL("clicked()"), self.export_database)

        identify_layout = QHBoxLayout()
        identify_layout.addStretch(2)
        identify_layout.addWidget(identify_button)
        identify_layout.addWidget(iden_all_button)
        identify_layout.addWidget(verify_button)
        identify_layout.addWidget(verify_all_button)

        load_layout = QHBoxLayout()
        load_layout.addStretch(2)
        load_layout.addWidget(import_button)
        load_layout.addWidget(export_button)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self._settings_box)
        widget_layout.addWidget(self._sources_box)
        widget_layout.addLayout(identify_layout)
        widget_layout.addLayout(load_layout)
        widget_layout.addStretch(2)
        keysrecg_widget.setLayout(widget_layout)
        keysrecg_dock.setWidget(keysrecg_widget)
        return keysrecg_dock

    def add_source(self):
        self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
        self._keysrecg_detector.kodsettings.probability = self._probBox.value()
        filedir = QFileDialog.getExistingDirectory(None, "Select source directory", ".")
        if not filedir.isEmpty():
            logger.debug("Loading started...")
            flist = files_list(str(filedir))
            i = 0
            for imfile in flist:
                i += 1
                obj = loadImageObject(imfile)
                self._keysrecg_detector.addSource(obj)
                self._load_label.setText("Load file: " + imfile)
                self._load_bar.setValue((i * 100) / len(flist))
                QCoreApplication.processEvents()
            self._load_label.setText("Loading finished.")
            self._load_bar.setValue(100)
            logger.debug("Loading finished.")

    def add_source_images(self):
        self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
        self._keysrecg_detector.kodsettings.probability = self._probBox.value()
        filelist = QFileDialog.getOpenFileNames(None, "Select source images", ".")
        if not filelist.isEmpty():
            logger.debug("Loading started...")
            i = 0
            for imfile in filelist:
                i += 1
                obj = loadImageObject(str(imfile))
                self._keysrecg_detector.addSource(obj)
                self._load_label.setText("Load file: " + imfile)
                self._load_bar.setValue((i * 100) / len(filelist))
                QCoreApplication.processEvents()
            self._load_label.setText("Loading finished.")
            self._load_bar.setValue(100)
            logger.debug("Loading finished.")
            logger.debug("Database updating...")
            self._load_label.setText("Database updating...")
            self._keysrecg_detector.update_database()
            self._load_label.setText("Database updated.")
            logger.debug("Database updated.")

    def clear_detector(self):
        self.init_detector()
        self._load_label.setText("The data has been cleared.")

    def keysrecg(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            data = {
                'path': curr.path(),
                'name': curr.title(),
                'data': curr.data()
            }
            self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
            self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
            self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
            self._keysrecg_detector.kodsettings.probability = self._probBox.value()
            self._keysrecg_detector.setUseROIDetection(True)
            self._keysrecg_detector.identify(data)

    def identify_all(self):
        if self._imanager:
            rtrue = 0
            rfalse = 0
            for curr in self._imanager.images():
                logger.debug(curr.path())
                data = {
                    'path': curr.path(),
                    'name': curr.title(),
                    'data': curr.data()
                }
                self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
                self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
                self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
                self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
                self._keysrecg_detector.kodsettings.probability = self._probBox.value()
                res = self._keysrecg_detector.identify(data)
                logger.debug("Result: " + os.path.split(res)[1] + "\t"
                             + os.path.split(os.path.split(curr.path())[0])[1])
                if os.path.split(res)[1] == os.path.split(os.path.split(curr.path())[0])[1]:
                    rtrue += 1
                else:
                    rfalse += 1
            logger.debug("Positive identification: " + str(rtrue) + "\t"
                         + str((rtrue / (1.0 * (rtrue + rfalse))) * 100))
            logger.debug("Negative identification: " + str(rfalse) + "\t"
                         + str((rfalse / (1.0 * (rtrue + rfalse))) * 100))

    def verify(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            data = {
                'path': curr.path(),
                'name': curr.title(),
                'data': curr.data()
            }
            self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
            # self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
            # self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            # self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
            self._keysrecg_detector.kodsettings.probability = self._probBox.value()
            self._keysrecg_detector.setUseROIDetection(True)
            self._keysrecg_detector.verify(data)

    def verify_all(self):
        if self._imanager:
            rtrue = dict() #0
            rfalse = dict() #0
            for inx in range(0, 20):
                rtrue[str(5 * inx)] = 0
                rfalse[str(5 * inx)] = 0
            for curr in self._imanager.images():
                logger.debug(curr.path())
                data = {
                    'path': curr.path(),
                    'name': curr.title(),
                    'data': curr.data()
                }
                self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
                self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
                self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
                self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
                self._keysrecg_detector.kodsettings.probability = self._probBox.value()
                res = self._keysrecg_detector.verify(data)
                if res is not False:
                    print "yaleB11" == os.path.split(os.path.split(curr.path())[0])[1]
                    print res > self._keysrecg_detector.kodsettings.probability
                    print self._keysrecg_detector.kodsettings.probability
                    print res
                    # if ("yaleB11" == os.path.split(os.path.split(curr.path())[0])[1]) == \
                    #         (res > self._keysrecg_detector.kodsettings.probability):
                    #     rtrue += 1
                    # else:
                    #     rfalse += 1
                    for inx in range(0, 20):
                        if ("yaleB11" == os.path.split(os.path.split(curr.path())[0])[1]) == \
                                (res > 5.0 * inx):
                            value = rtrue.get(str(5 * inx), 0)
                            value += 1
                            rtrue[str(5 * inx)] = value
                        else:
                            value = rfalse.get(str(5 * inx), 0)
                            value += 1
                            rfalse[str(5 * inx)] = value
            for inx in range(0, 20):
                logger.debug("Threshold: " + str(5 * inx))
                logger.debug("Positive verification: " + str(rtrue.get(str(5 * inx), 0)) + "\t"
                             + str((rtrue.get(str(5 * inx), 0) / (1.0 * (rtrue.get(str(5 * inx), 0) +
                                                                      rfalse.get(str(5 * inx), 0)))) * 100))
                logger.debug("Negative verification: " + str(rfalse.get(str(5 * inx), 0)) + "\t"
                             + str((rfalse.get(str(5 * inx), 0) / (1.0 * (rtrue.get(str(5 * inx), 0) +
                                                                       rfalse.get(str(5 * inx), 0)))) * 100))

    def export_database(self):
        source = self._keysrecg_detector.exportSources()
        info = self._keysrecg_detector.exportSettings()
        print source
        print info
        json_encoded = json.dumps(source)
        info_encoded = json.dumps(info)
        filedir = QFileDialog.getExistingDirectory(None, "Select database directory", ".")
        if not filedir.isEmpty():
            source_file = os.path.join(str(filedir), 'data.json')
            with open(source_file, "w") as data_file:
                data_file.write(json_encoded)
            data_file.close()
            jinfo_file = os.path.join(str(filedir), 'info.json')
            with open(jinfo_file, "w") as info_file:
                info_file.write(info_encoded)
            data_file.close()

    def import_database(self):
        filedir = QFileDialog.getExistingDirectory(None, "Select database directory", ".")
        if not filedir.isEmpty():
            source_file = os.path.join(str(filedir), 'data.json')
            with open(source_file, "r") as data_file:
                source = json.load(data_file)
                self._keysrecg_detector.importSources(source)
            info_file = os.path.join(str(filedir), 'info.json')
            with open(info_file, "r") as info_data_file:
                info = json.load(info_data_file)
                self._keysrecg_detector.importSettings(info)
            self._neighBox.setValue(self._keysrecg_detector.kodsettings.neighbours_distance)
            self._probBox.setValue(self._keysrecg_detector.kodsettings.probability)
            self._keysrecg_detector.kodsettings.dump()
            self._keysrecg_detector._cascadeROI.classifierSettings.dump()
            self._keysrecg_detector._eyeROI.classifierSettings.dump()

    def det_change(self):
        if self.settings_dialog.exec_():
            self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
            self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()

    def add_compare_action(self, parent):
        compare_action = QAction(parent)
        compare_action.setText(_("Compare Images"))
        compare_action.setIcon(get_icon('compi.png'))
        compare_action.setCheckable(True)
        self.connect(compare_action, SIGNAL("triggered(bool)"), self.compare_opened)
        return compare_action

    compare_opened = pyqtSignal(bool, name='compareImagesOpened')

    def create_compare_widget(self):
        compare_dock = QDockWidget()
        compare_dock.setWindowTitle("Keypoints Face Recognition Settings")
        compare_dock.setVisible(False)
        self.compare_opened.connect(compare_dock.setVisible)
        compare_widget = QWidget(compare_dock)
        self._keysett_box = QGroupBox(compare_widget)
        self._keysett_box.setTitle(_("Settings:"))

        change_button = QPushButton(compare_widget)
        change_button.setText(_("Change"))
        self.connect(change_button, SIGNAL("clicked()"), self.det_change)

        self._compare_neighBox = QDoubleSpinBox(compare_widget)
        self._compare_neighBox.setSingleStep(0.10)
        self._compare_neighBox.setMinimum(0)
        self._compare_neighBox.setMaximum(10000)
        self._compare_neighBox.setValue(1.0)

        keysett_layout = QFormLayout()
        keysett_layout.addRow(_("Keypoints Detector: "), change_button)
        keysett_layout.addRow(_("Max Neighbours Distance:"), self._compare_neighBox)
        self._keysett_box.setLayout(keysett_layout)

        self._first_box = QGroupBox(compare_widget)
        self._first_box.setTitle(_("First Image:"))

        self._fimage_edit = QLineEdit(compare_widget)
        self._fimage_edit.setReadOnly(True)

        fbrowse_button = QPushButton(compare_widget)
        fbrowse_button.setText('Browse...')
        self.connect(fbrowse_button, SIGNAL("clicked()"), self.add_fimage)

        fbrowse_layout = QHBoxLayout()
        fbrowse_layout.addWidget(self._fimage_edit)
        fbrowse_layout.addWidget(fbrowse_button)
        self._first_box.setLayout(fbrowse_layout)

        self._second_box = QGroupBox(compare_widget)
        self._second_box.setTitle(_("Second Image:"))

        self._simage_edit = QLineEdit(compare_widget)
        self._simage_edit.setReadOnly(True)

        sbrowse_button = QPushButton(compare_widget)
        sbrowse_button.setText('Browse...')
        self.connect(sbrowse_button, SIGNAL("clicked()"), self.add_simage)

        sbrowse_layout = QHBoxLayout()
        sbrowse_layout.addWidget(self._simage_edit)
        sbrowse_layout.addWidget(sbrowse_button)
        self._second_box.setLayout(sbrowse_layout)

        compare_button = QPushButton(compare_widget)
        compare_button.setText('Compare')
        self.connect(compare_button, SIGNAL("clicked()"), self.compare)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(2)
        bottom_layout.addWidget(compare_button)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self._keysett_box)
        widget_layout.addWidget(self._first_box)
        widget_layout.addWidget(self._second_box)
        widget_layout.addLayout(bottom_layout)
        widget_layout.addStretch(2)
        compare_widget.setLayout(widget_layout)
        compare_dock.setWidget(compare_widget)
        return compare_dock

    def add_fimage(self):
        filename = QFileDialog.getOpenFileName(None, "Select first image to compare", ".")
        if not filename.isEmpty():
            self._fimage_edit.setText(filename)

    def add_simage(self):
        filename = QFileDialog.getOpenFileName(None, "Select second image to compare", ".")
        if not filename.isEmpty():
            self._simage_edit.setText(filename)

    def compare(self):
        if (not self._fimage_edit.text().isEmpty()) and (not self._simage_edit.text().isEmpty()):
            first_data = loadImageObject(str(self._fimage_edit.text()))
            second_data = loadImageObject(str(self._simage_edit.text()))
            self._keysrecg_detector.kodsettings.neighbours_distance = self._compare_neighBox.value()
            self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
            self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
            self._keysrecg_detector.kodsettings.probability = self._probBox.value()
            self._keysrecg_detector.setUseROIDetection(True)
            res = self._keysrecg_detector.compare(first_data, second_data)