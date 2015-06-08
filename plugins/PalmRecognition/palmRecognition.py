import json
import os

from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget,
                              QFileDialog,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QPushButton, QGroupBox, QDoubleSpinBox,
                              QLabel, QProgressBar)
from guidata.qt.QtCore import QObject, QCoreApplication
from guidata.configtools import get_icon
from guiqwt.config import _
from logger import logger
from aiplugins import IAlgorithmPlugin
from algorithms.faces.biom.utils import files_list
from ui.detdialog import DetectorSettingsDialog
from imageproperties import ImageProperties
from algorithms.recognition.palm.palm_keypoints import PalmKeypointsDetector
from algorithms.recognition.palm.detection import palm_contours
from algorithms.imgobj import loadImageObject


PALM_DETECTION = "Action:: Palm Detection:: "


class PalmRecognitionPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(PalmRecognitionPlugin, self).__init__()
        self._setwigets = []
        self.init_keysrecg_algorithm()
        self._setwigets.append(self.create_keysrecg_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        recognition_menu = QMenu(parent)
        recognition_menu.setTitle(_("Palm Recognition"))

        recognition_menu.addAction(self.add_keysrecg_action(recognition_menu))
        recognition_menu.addAction(self.add_detection_action(recognition_menu))
        return [recognition_menu]

    def get_algorithms_list(self):
        return []

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

    def init_keysrecg_algorithm(self):
        self.settings_dialog = DetectorSettingsDialog()
        self.settings_dialog.setWindowTitle(_("Keypoints Detector Settings"))
        self.init_detector()

    def init_detector(self):
        self._keysrecg_detector = PalmKeypointsDetector()

    def add_keysrecg_action(self, parent):
        keysrecg_action = QAction(parent)
        keysrecg_action.setText(_("Keypoints-based Palm Recognition"))
        keysrecg_action.setIcon(get_icon('kprecg.png'))
        keysrecg_action.setCheckable(True)
        self.connect(keysrecg_action, SIGNAL("triggered(bool)"), self.keysrecg_opened)
        return keysrecg_action

    keysrecg_opened = pyqtSignal(bool, name='keyspalmRecgOpened')

    def create_keysrecg_widget(self):
        keysrecg_dock = QDockWidget()
        keysrecg_dock.setWindowTitle("Keypoints Palm Recognition Settings")
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
            logger.debug("Database updating...")
            self._load_label.setText("Database updating...")
            self._keysrecg_detector.update_database()
            self._load_label.setText("Database updated.")
            logger.debug("Database updated.")

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
            self._keysrecg_detector.kodsettings.detector_type = self.settings_dialog.result_type()
            self._keysrecg_detector.kodsettings.brisk_settings = self.settings_dialog.brisk()
            self._keysrecg_detector.kodsettings.orb_settings = self.settings_dialog.orb()
            self._keysrecg_detector.kodsettings.probability = self._probBox.value()
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

    def add_detection_action(self, parent):
        detect_action = QAction(parent)
        detect_action.setText(_("Palm Detection"))
        detect_action.setIcon(get_icon('pdetect.png'))
        self.connect(detect_action, SIGNAL("triggered(bool)"), self.palm_detect)
        return detect_action

    def palm_detect(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str(PALM_DETECTION + curr.title()))
            image.data(palm_contours(curr.data()))
            self._imanager.add_image(image)