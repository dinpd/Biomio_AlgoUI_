from guidata.qt.QtCore import SIGNAL
from guidata.qt.QtGui import (QWidget, QStackedWidget,
                              QDialog,
                              QIntValidator, QDoubleValidator,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QPushButton, QLineEdit, QRadioButton)
from guiqwt.config import _

from biomio.algorithms.features.detectors import (BRISKDetectorSettings, ORBDetectorSettings,
                                                  mahotasSURFDetectorSettings)
from biomio.algorithms.features import BRISKDetectorType, ORBDetectorType


class DetectorSettingsDialog(QDialog):
    def __init__(self, parent=None):
        self._detector_type = BRISKDetectorType
        self._settings = BRISKDetectorSettings()
        super(DetectorSettingsDialog, self).__init__(parent)

        self._brisk_button = QRadioButton(self)
        self._brisk_button.setText(_("BRISK"))
        self._brisk_button.setChecked(True)
        self.connect(self._brisk_button, SIGNAL("clicked()"), self.change_method)
        self._orb_button = QRadioButton(self)
        self._orb_button.setText(_("ORB"))
        self.connect(self._orb_button, SIGNAL("clicked()"), self.change_method)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self._brisk_button)
        radio_layout.addWidget(self._orb_button)
        self._stacked_widget = QStackedWidget(self)
        self.brisk_tab()
        self.orb_tab()

        okButton = QPushButton(self)
        okButton.setText(_("OK"))
        self.connect(okButton, SIGNAL("clicked()"), self.acceptDialog)
        cancelButton = QPushButton(self)
        cancelButton.setText(_("Cancel"))
        self.connect(cancelButton, SIGNAL("clicked()"), self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch(2)
        button_layout.addWidget(okButton)
        button_layout.addWidget(cancelButton)

        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(radio_layout)
        dialog_layout.addWidget(self._stacked_widget)
        dialog_layout.addLayout(button_layout)
        self.setLayout(dialog_layout)

    def result_type(self):
        return 'mahotasSURF'
        # return self._detector_type

    def settings(self):
        return mahotasSURFDetectorSettings()
        # return self._settings

    def brisk_tab(self):
        brisk_widget = QWidget(self)
        self._thresh_line_edit = QLineEdit(brisk_widget)
        self._thresh_line_edit.setValidator(QIntValidator())
        self._octaves_line_edit = QLineEdit(brisk_widget)
        self._octaves_line_edit.setValidator(QIntValidator())
        self._pattern_scale_line_edit = QLineEdit(brisk_widget)
        self._pattern_scale_line_edit.setValidator(QDoubleValidator())
        temp = BRISKDetectorSettings()
        if self._detector_type == BRISKDetectorType:
            temp = self._settings
        self._thresh_line_edit.setText(str(temp.thresh))
        self._octaves_line_edit.setText(str(temp.octaves))
        self._pattern_scale_line_edit.setText(str(temp.patternScale))
        widget_layout = QFormLayout()
        widget_layout.addRow('Thresh', self._thresh_line_edit)
        widget_layout.addRow('Octaves', self._octaves_line_edit)
        widget_layout.addRow('Pattern Scale', self._pattern_scale_line_edit)
        brisk_widget.setLayout(widget_layout)
        self._stacked_widget.addWidget(brisk_widget)

    def orb_tab(self):
        orb_widget = QWidget(self)
        self._features_line_edit = QLineEdit(orb_widget)
        self._features_line_edit.setValidator(QIntValidator())
        self._scale_line_edit = QLineEdit(orb_widget)
        self._scale_line_edit.setValidator(QDoubleValidator())
        self._levels_line_edit = QLineEdit(orb_widget)
        self._levels_line_edit.setValidator(QIntValidator())
        temp = ORBDetectorSettings()
        if self._detector_type == ORBDetectorType:
            temp = self._settings
        self._features_line_edit.setText(str(temp.features))
        self._scale_line_edit.setText(str(temp.scaleFactor))
        self._levels_line_edit.setText(str(temp.nlevels))
        widget_layout = QFormLayout()
        widget_layout.addRow('Number of Features', self._features_line_edit)
        widget_layout.addRow('Scale Factor', self._scale_line_edit)
        widget_layout.addRow('Number of Levels', self._levels_line_edit)
        orb_widget.setLayout(widget_layout)
        self._stacked_widget.addWidget(orb_widget)

    def change_method(self):
        if self._brisk_button.isChecked():
            self._detector_type = BRISKDetectorType
            self._stacked_widget.setCurrentIndex(0)
        else:
            self._detector_type = ORBDetectorType
            self._stacked_widget.setCurrentIndex(1)

    def acceptDialog(self):
        if self._detector_type == BRISKDetectorType:
            self._settings = BRISKDetectorSettings()
            self._settings.thresh = int(self._thresh_line_edit.text())
            self._settings.octaves = int(self._octaves_line_edit.text())
            self._settings.patternScale = float(self._pattern_scale_line_edit.text())
        else:
            self._settings = ORBDetectorSettings()
            self._settings.features = int(self._features_line_edit.text())
            self._settings.scaleFactor = float(self._scale_line_edit.text())
            self._settings.nlevels = int(self._levels_line_edit.text())
        self.accept()
