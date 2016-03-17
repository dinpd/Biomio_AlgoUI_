from guidata.qt.QtGui import (QLineEdit, QSpinBox, QIntValidator, QFormLayout, QRadioButton)
from ui.settings_widget import SettingsWidget
from guidata.qt.QtCore import SIGNAL


class ResizeWidget(SettingsWidget):
    def __init__(self, parent=None):
        SettingsWidget.__init__(self, parent)
        self._create_widget()
        self._pixels_button.setChecked(True)

    def settings(self):
        dsize = (int(self._width_line_edit.text()),
                 int(self._height_line_edit.text())) if self._pixels_button.isChecked() else None
        return dict(
            dsize=dsize,
            fx=(self._width_box.value() / 100.0) if self._percentage_button.isChecked() else None,
            fy=(self._height_box.value() / 100.0) if self._percentage_button.isChecked() else None
        )

    def load_settings(self, settings):
        self._width_line_edit.setText(str(settings.get('dsize', (1000, 1000))[0]))
        self._height_line_edit.setText(str(settings.get('dsize', (1000, 1000))[1]))
        self._width_box.setValue(settings.get('fx', 100))
        self._height_box.setValue(settings.get('fy', 100))
        if settings.get('fx', None) is None:
            self._pixels_button.setChecked(True)
        else:
            self._percentage_button.setChecked(True)

    def _create_widget(self):
        self._pixels_button = QRadioButton(self)
        self._pixels_button.setText("Pixel Size:")
        self.connect(self._pixels_button, SIGNAL("toggled(bool)"), self._controls_state)
        self._width_line_edit = QLineEdit(self)
        self._width_line_edit.setValidator(QIntValidator())
        self._width_line_edit.setText('1000')
        self._height_line_edit = QLineEdit(self)
        self._height_line_edit.setValidator(QIntValidator())
        self._height_line_edit.setText('1000')
        self._percentage_button = QRadioButton(self)
        self._percentage_button.setText("Percentage Size:")
        self.connect(self._percentage_button, SIGNAL("toggled(bool)"), self._controls_state)
        self._width_box = QSpinBox(self)
        self._width_box.setMinimum(0)
        self._width_box.setMaximum(100)
        self._width_box.setSingleStep(1)
        self._width_box.setValue(100)
        self._width_box.setSuffix(" %")
        self._height_box = QSpinBox(self)
        self._height_box.setMinimum(0)
        self._height_box.setMaximum(100)
        self._height_box.setSingleStep(1)
        self._height_box.setValue(100)
        self._height_box.setSuffix(" %")
        widget_layout = QFormLayout()
        widget_layout.addWidget(self._pixels_button)
        widget_layout.addRow('Width', self._width_line_edit)
        widget_layout.addRow('Height', self._height_line_edit)
        widget_layout.addWidget(self._percentage_button)
        widget_layout.addRow('Width', self._width_box)
        widget_layout.addRow('Height', self._height_box)
        self.setLayout(widget_layout)

    def _controls_state(self):
        if self._pixels_button.isChecked():
            self._width_line_edit.setEnabled(True)
            self._height_line_edit.setEnabled(True)
            self._width_box.setEnabled(False)
            self._height_box.setEnabled(False)
        else:
            self._width_line_edit.setEnabled(False)
            self._height_line_edit.setEnabled(False)
            self._width_box.setEnabled(True)
            self._height_box.setEnabled(True)
