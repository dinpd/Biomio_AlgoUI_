from guidata.qt.QtGui import QWidget

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)

    def settings(self):
        return dict()

    def load_settings(self, settings):
        raise NotImplementedError
