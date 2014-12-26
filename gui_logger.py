import logging
import sys
from guidata.qt.QtGui import QDockWidget, QTextBrowser
from guidata.qt.QtCore import QObject, pyqtSignal
from guiqwt.config import _


class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write('%s\n'%record)
        # originally: XStream.stdout().write("{}\n".format(record))


class XStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class LogManager(QDockWidget):
    def __init__( self, parent=None):
        super(LogManager, self).__init__(parent)
        self.setWindowTitle(_("Log"))

        self._console = QTextBrowser(self)
        self.setWidget(self._console)

        XStream.stdout().messageWritten.connect(self._console.insertPlainText)
        XStream.stderr().messageWritten.connect(self._console.insertPlainText)