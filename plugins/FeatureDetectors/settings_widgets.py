from guidata.qt.QtGui import (QWidget, QLineEdit, QCheckBox, QIntValidator, QDoubleValidator,
                              QFormLayout)

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)

    def settings(self):
        return dict()

    def load_settings(self, settings):
        raise NotImplementedError

class BRISKWidget(SettingsWidget):
    def __init__(self, parent=None):
        SettingsWidget.__init__(self, parent)
        self._create_widget()

    def settings(self):
        return dict(
            thresh=int(self._thresh_line_edit.text()),
            octaves=int(self._octaves_line_edit.text()),
            patternScale=float(self._pattern_scale_line_edit.text())
        )

    def load_settings(self, settings):
        self._thresh_line_edit.setText(str(settings.get('thresh', 10)))
        self._octaves_line_edit.setText(str(settings.get('octaves', 0)))
        self._pattern_scale_line_edit.setText(str(settings.get('patternScale', 1.0)))

    def _create_widget(self):
        self._thresh_line_edit = QLineEdit(self)
        self._thresh_line_edit.setValidator(QIntValidator())
        self._thresh_line_edit.setText('10')
        self._octaves_line_edit = QLineEdit(self)
        self._octaves_line_edit.setValidator(QIntValidator())
        self._octaves_line_edit.setText('0')
        self._pattern_scale_line_edit = QLineEdit(self)
        self._pattern_scale_line_edit.setValidator(QDoubleValidator())
        self._pattern_scale_line_edit.setText('1.0')
        widget_layout = QFormLayout()
        widget_layout.addRow('Thresh', self._thresh_line_edit)
        widget_layout.addRow('Octaves', self._octaves_line_edit)
        widget_layout.addRow('Pattern Scale', self._pattern_scale_line_edit)
        self.setLayout(widget_layout)


class ORBWidget(SettingsWidget):
    def __init__(self, parent=None):
        SettingsWidget.__init__(self, parent)
        self._create_widget()

    def settings(self):
        return dict(
            features=int(self._features_line_edit.text()),
            scaleFactor=float(self._scale_line_edit.text()),
            nlevels=int(self._levels_line_edit.text())
        )

    def load_settings(self, settings):
        self._features_line_edit.setText(str(settings.get('features', 500)))
        self._scale_line_edit.setText(str(settings.get('scaleFactor', 1.1)))
        self._levels_line_edit.setText(str(settings.get('nlevels', 8)))

    def _create_widget(self):
        self._features_line_edit = QLineEdit(self)
        self._features_line_edit.setValidator(QIntValidator())
        self._features_line_edit.setText('500')
        self._scale_line_edit = QLineEdit(self)
        self._scale_line_edit.setValidator(QDoubleValidator())
        self._scale_line_edit.setText('1.1')
        self._levels_line_edit = QLineEdit(self)
        self._levels_line_edit.setValidator(QIntValidator())
        self._levels_line_edit.setText('8')

        widget_layout = QFormLayout()
        widget_layout.addRow('Number of Features', self._features_line_edit)
        widget_layout.addRow('Scale Factor', self._scale_line_edit)
        widget_layout.addRow('Number of Levels', self._levels_line_edit)
        self.setLayout(widget_layout)


class SURFWidget(SettingsWidget):
    def __init__(self, parent=None):
        SettingsWidget.__init__(self, parent)
        self._create_widget()

    def settings(self):
        return dict(
            threshold=int(self._threshold_line_edit.text())
        )

    def load_settings(self, settings):
        self._threshold_line_edit.setText(str(settings.get('threshold', 500)))

    def _create_widget(self):
        self._threshold_line_edit = QLineEdit(self)
        self._threshold_line_edit.setValidator(QIntValidator())
        self._threshold_line_edit.setText('500')
        widget_layout = QFormLayout()
        widget_layout.addRow('Threshold', self._threshold_line_edit)
        self.setLayout(widget_layout)


class MahotasSURFWidget(SettingsWidget):
    def __init__(self, parent=None):
        SettingsWidget.__init__(self, parent)
        self._create_widget()

    def settings(self):
        return dict(
            octaves=int(self._octaves_line_edit.text()),
            scales=int(self._scale_line_edit.text()),
            init_step_size=int(self._step_size_line_edit.text()),
            threshold=float(self._thresh_line_edit.text()),
            max_points=int(self._max_points_line_edit.text()),
            is_integral=self._is_integral_check_box.isChecked()
        )

    def load_settings(self, settings):
        self._octaves_line_edit.setText(str(settings.get('octaves', 4)))
        self._scale_line_edit.setText(str(settings.get('scales', 6)))
        self._step_size_line_edit.setText(str(settings.get('init_step_size', 1)))
        self._thresh_line_edit.setText(str(settings.get('threshold', 0.1)))
        self._max_points_line_edit.setText(str(settings.get('max_points', 1000)))
        self._is_integral_check_box.setChecked(settings.get('is_integral', False))

    def _create_widget(self):
        self._octaves_line_edit = QLineEdit(self)
        self._octaves_line_edit.setValidator(QIntValidator())
        self._octaves_line_edit.setText('4')
        self._scale_line_edit = QLineEdit(self)
        self._scale_line_edit.setValidator(QIntValidator())
        self._scale_line_edit.setText('6')
        self._step_size_line_edit = QLineEdit(self)
        self._step_size_line_edit.setValidator(QIntValidator())
        self._step_size_line_edit.setText('1')
        self._thresh_line_edit = QLineEdit(self)
        self._thresh_line_edit.setValidator(QDoubleValidator())
        self._thresh_line_edit.setText('0.1')
        self._max_points_line_edit = QLineEdit(self)
        self._max_points_line_edit.setValidator(QIntValidator())
        self._max_points_line_edit.setText('1000')
        self._is_integral_check_box = QCheckBox(self)
        self._is_integral_check_box.setText("Is Integral")
        self._is_integral_check_box.setChecked(False)

        widget_layout = QFormLayout()
        widget_layout.addRow('Octaves', self._octaves_line_edit)
        widget_layout.addRow('Scales', self._scale_line_edit)
        widget_layout.addRow('Initial Step Size', self._step_size_line_edit)
        widget_layout.addRow('Threshold', self._thresh_line_edit)
        widget_layout.addRow('Maximum points count', self._max_points_line_edit)
        widget_layout.addWidget(self._is_integral_check_box)
        self.setLayout(widget_layout)
