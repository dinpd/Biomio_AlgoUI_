import logging

logger = logging.getLogger(__name__)

from aiplugins import IAlgorithmPlugin
from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QAction, QMenu,
                              QWidget, QDockWidget, QListWidget,
                              QFileDialog,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QPushButton, QGroupBox, QDoubleSpinBox,
                              QSpinBox, QLabel, QProgressBar)
from guidata.qt.QtCore import QObject, QCoreApplication
from guidata.configtools import get_icon
from imageproperties import ImageProperties
import faces.biom.faces as fs
from faces.biom.utils import files_list, read_file
from faces.recognition.keypoints import KeypointsObjectDetector, NearPyHash

from guiqwt.config import _


class FaceRecognitionPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(FaceRecognitionPlugin, self).__init__()
        self._setwigets = []
        self.init_keysrecg_algorithm()
        self._setwigets.append(self.create_detect_widget())
        self._setwigets.append(self.create_keysrecg_widget())

    def set_image_manager(self, manager):
        self._imanager = manager

    def get_algorithms_actions(self, parent):
        recognition_menu = QMenu(parent)
        recognition_menu.setTitle(_("Face Recognition"))

        recognition_menu.addAction(self.add_detect_action(recognition_menu))
        recognition_menu.addAction(self.add_keysrecg_action(recognition_menu))
        return [recognition_menu]

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        return self._setwigets

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

        right_layout = QVBoxLayout()
        right_layout.addWidget(add_button)
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

    def face_detect(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str('ROI Detection by Haar Cascade::' + curr.title()))

            casc = self._cascades_list.item(self._cascades_list.currentRow()).text()

            img = curr.data()
            # Refactor code
            ff = fs.FisherFaces()
            ff.classifierSettings.scaleFactor = self._scaleBox.value()
            ff.classifierSettings.minNeighbors = self._neighborsBox.value()
            ff.add_cascade(str(casc))

            faces = ff.detect(img)

            inx = 0
            for face in faces:
                print face
                img = fs.paintRectangle(img, face, (0, 0, 0))
                inx += 1

            logger.info("Detection finished.")
            image.data(img)
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_temp_image(image)

    def init_keysrecg_algorithm(self):
        self._keysrecg_detector = KeypointsObjectDetector(NearPyHash)
        self._keysrecg_detector.kodsettings.cascade_list.append(
            "faces/data/data/haarcascades/haarcascade_frontalface_alt_tree.xml")
        self._keysrecg_detector.kodsettings.cascade_list.append(
            "faces/data/data/haarcascades/haarcascade_frontalface_alt2.xml")
        self._keysrecg_detector.kodsettings.cascade_list.append(
            "faces/data/data/haarcascades/haarcascade_frontalface_alt.xml")
        self._keysrecg_detector.kodsettings.cascade_list.append(
            "faces/data/data/haarcascades/haarcascade_frontalface_default.xml")

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

        self._neighBox = QDoubleSpinBox(keysrecg_widget)
        self._neighBox.setSingleStep(0.10)
        self._neighBox.setMinimum(0)
        self._neighBox.setValue(1.0)

        settings_layout = QFormLayout()
        settings_layout.addRow(_("Max Neighbours Distance:"), self._neighBox)
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

        top_layout = QHBoxLayout()
        top_layout.addWidget(self._load_bar)
        top_layout.addWidget(add_button)

        sources_layout = QVBoxLayout()
        sources_layout.addLayout(top_layout)
        sources_layout.addWidget(self._load_label)
        self._sources_box.setLayout(sources_layout)

        identify_button = QPushButton(keysrecg_widget)
        identify_button.setText(_('Identify'))
        self.connect(identify_button, SIGNAL("clicked()"), self.keysrecg)

        identify_layout = QHBoxLayout()
        identify_layout.addStretch(2)
        identify_layout.addWidget(identify_button)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self._settings_box)
        widget_layout.addWidget(self._sources_box)
        widget_layout.addLayout(identify_layout)
        widget_layout.addStretch(2)
        keysrecg_widget.setLayout(widget_layout)
        keysrecg_dock.setWidget(keysrecg_widget)
        return keysrecg_dock

    def add_source(self):
        filedir = QFileDialog.getExistingDirectory(None, "Select source directory", ".")
        if not filedir.isEmpty():
            flist = files_list(str(filedir))
            i = 0
            for imfile in flist:
                i += 1
                obj = read_file(imfile)
                self._keysrecg_detector.addSource(obj)
                self._load_label.setText("Load file: " + imfile)
                self._load_bar.setValue((i * 100) / len(flist))
                QCoreApplication.processEvents()
            self._load_label.setText("Loading finished.")
            self._load_bar.setValue(100)

    def keysrecg(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            data = {
                'path': curr.path(),
                'name': curr.title(),
                'data': curr.data()
            }
            self._keysrecg_detector.kodsettings.neighbours_distance = self._neighBox.value()
            self._keysrecg_detector.identify(data)