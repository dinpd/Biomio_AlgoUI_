from guidata.qt.QtCore import SIGNAL, pyqtSignal
from guidata.qt.QtGui import (QStackedWidget, QWidget, QDockWidget,
                              QVBoxLayout, QHBoxLayout,
                              QPushButton, QGroupBox, QComboBox, QLabel, QCheckBox)
from settings_widget import SettingsWidget


class AlgorithmPanel(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)
        self._create_widget()

    applied = pyqtSignal(name='applied')

    def addAlgorithm(self, name, settings_widget=None):
        s_widget = settings_widget
        if settings_widget is None:
            s_widget = SettingsWidget()
        s_widget.setParent(self._stacked_widget)
        self._combo_box.addItem(name)
        self._stacked_widget.addWidget(s_widget)

    def change_settings(self):
        self._stacked_widget.setCurrentIndex(self._combo_box.currentIndex())

    def settings(self):
        return dict(
            name=str(self._combo_box.currentText()),
            settings=self._stacked_widget.currentWidget().settings(),
            serial_processing=self._serial_processing.isChecked()
        )

    def setEnableSerialProcessing(self, enable):
        self._serial_processing.setEnabled(enable)

    def _create_widget(self):
        widget = QWidget(self)
        label = QLabel(widget)
        label.setText("Algorithm:")
        self._combo_box = QComboBox(widget)
        self.connect(self._combo_box, SIGNAL("currentIndexChanged(int)"), self.change_settings)
        group_box = QGroupBox(widget)
        group_box.setTitle("Settings:")
        group_layout = QVBoxLayout()
        self._stacked_widget = QStackedWidget(widget)
        group_layout.addWidget(self._stacked_widget)
        group_box.setLayout(group_layout)
        algorithms_layout = QHBoxLayout()
        algorithms_layout.addWidget(label)
        algorithms_layout.addWidget(self._combo_box)
        self._serial_processing = QCheckBox(widget)
        self._serial_processing.setText("Serial Processing")
        self._serial_processing.setChecked(False)
        apply_button = QPushButton(widget)
        apply_button.setText('Apply')
        self.connect(apply_button, SIGNAL("clicked()"), self.applied)
        button_layout = QHBoxLayout()
        button_layout.addStretch(2)
        button_layout.addWidget(apply_button)
        main_layout = QVBoxLayout()
        main_layout.addLayout(algorithms_layout)
        main_layout.addWidget(group_box)
        main_layout.addWidget(self._serial_processing)
        main_layout.addLayout(button_layout)
        widget.setLayout(main_layout)
        self.setWidget(widget)
