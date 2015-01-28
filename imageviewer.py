from guidata.qt.QtGui import (QWidget,
                              QGraphicsView, QGraphicsScene,
                              QPixmap, QImage,
                              QHBoxLayout,
                              QAction, QKeySequence, QMenu,
                              QApplication)
from guidata.qt.QtCore import (Qt, SIGNAL, pyqtSlot)

from guiqwt.config import _
from guiqwt import io

from viewers import AbstractImageViewer

import cv2


def imageOpenCv2ToQImage(cv_img):
    height, width = cv_img.shape[0], cv_img.shape[1]
    if len(cv_img.shape) > 2:
        cv_img2 = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    else:
        cv_img2 = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
    bytesPerLine = 3 * width
    return QImage(cv_img2.data, width, height, bytesPerLine, QImage.Format_RGB888)


class ImageViewer(QWidget, AbstractImageViewer):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self._zoomFactorDelta = 1.25

        self.createActions()
        self.createMenus()

        self._scene = QGraphicsScene()
        self._view = QGraphicsView(self)
        self._view.setAlignment(Qt.AlignCenter)
        self._view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self._view.setScene(self._scene)

        central_layout = QHBoxLayout()
        central_layout.addWidget(self._view)
        self.setLayout(central_layout)

    def viewer_menu(self):
        return self._viewMenu

    def setImage(self, image):
        self._view.setScene(None)
        self._scene.clear()
        self._scene.deleteLater()
        self._scene = QGraphicsScene()
        if image is not None:
            self._current_pixmap = self._scene.addPixmap(QPixmap.fromImage(imageOpenCv2ToQImage(image.data())))
            if image.data() is None:
                self._current_pixmap = self._scene.addPixmap(QPixmap(image.path()))
                if self._smoothAct.isChecked():
                    self._current_pixmap.setTransformationMode(Qt.SmoothTransformation)
                else:
                    self._current_pixmap.setTransformationMode(Qt.FastTransformation)
        self._view.setScene(self._scene)

    def update_plot(self):
        QApplication.processEvents()

    def createActions(self):
        """Create actions for the menus."""

        self._smoothAct = QAction("&Smooth", self,
            triggered=self.isSmooth)
        self._smoothAct.setCheckable(True)
        #view actions
        self._scrollToTopAct = QAction("&Top", self,
            shortcut=QKeySequence.MoveToStartOfDocument,
            triggered=self.scrollToTop)

        self._scrollToBottomAct = QAction("&Bottom", self,
            shortcut=QKeySequence.MoveToEndOfDocument,
            triggered=self.scrollToBottom)

        self._scrollToBeginAct = QAction("&Left Edge", self,
            shortcut=QKeySequence.MoveToStartOfLine,
            triggered=self.scrollToBegin)

        self._scrollToEndAct = QAction("&Right Edge", self,
            shortcut=QKeySequence.MoveToEndOfLine,
            triggered=self.scrollToEnd)

        self._centerView = QAction("&Center", self,
            shortcut="5", triggered=self.centerView)

        #zoom actions
        self._zoomInAct = QAction("Zoo&m In (25%)", self,
            shortcut=QKeySequence.ZoomIn,
            triggered=self.zoomIn)

        self._zoomOutAct = QAction("Zoom &Out (25%)", self,
            shortcut=QKeySequence.ZoomOut,
            triggered=self.zoomOut)

        self._actualSizeAct = QAction("Actual &Size", self,
            shortcut="/", triggered=self.actualSize)

        self._fitToWindowAct = QAction("Fit &Image", self,
            shortcut="*", triggered=self.fitToWindow)

        self._fitWidthAct = QAction("Fit &Width", self,
            shortcut="Alt+Right", triggered=self.fitWidth)

        self._fitHeightAct = QAction("Fit &Height", self,
            shortcut="Alt+Down", triggered=self.fitHeight)

        # self._zoomToAct = QAction("&Zoom To...", self,
        #     shortcut="Z")

    def createMenus(self):
        """Create the menus."""

        #Create File Menu
        self._viewMenu = QMenu("&View")
        self._viewMenu.addAction(self._smoothAct)

        #Create Scroll Menu
        scrollMenu = QMenu("&Scroll", self._viewMenu)
        scrollMenu.addAction(self._scrollToTopAct)
        scrollMenu.addAction(self._scrollToBottomAct)
        scrollMenu.addAction(self._scrollToBeginAct)
        scrollMenu.addAction(self._scrollToEndAct)
        scrollMenu.addAction(self._centerView)
        self._viewMenu.addMenu(scrollMenu)

        #Create Zoom Menu
        zoomMenu = QMenu("&Zoom", self._viewMenu)
        zoomMenu.addAction(self._zoomInAct)
        zoomMenu.addAction(self._zoomOutAct)
        zoomMenu.addSeparator()
        zoomMenu.addAction(self._actualSizeAct)
        zoomMenu.addAction(self._fitToWindowAct)
        zoomMenu.addAction(self._fitWidthAct)
        zoomMenu.addAction(self._fitHeightAct)
        self._viewMenu.addMenu(zoomMenu)

    def getZoomFactor(self):
        """Zoom scale factor (*float*)."""
        return self._view.transform().m11()

    def setZoomFactor(self, newZoomFactor):
        newZoomFactor = newZoomFactor / self.getZoomFactor()
        self._view.scale(newZoomFactor, newZoomFactor)

    @pyqtSlot()
    def isSmooth(self):
        if self._smoothAct.isChecked():
            self._current_pixmap.setTransformationMode(Qt.SmoothTransformation)
        else:
            self._current_pixmap.setTransformationMode(Qt.FastTransformation)

    @pyqtSlot()
    def scrollToTop(self):
        """Scroll view to top."""
        sbar = self._view.verticalScrollBar()
        sbar.setValue(sbar.minimum())

    @pyqtSlot()
    def scrollToBottom(self):
        """Scroll view to bottom."""
        sbar = self._view.verticalScrollBar()
        sbar.setValue(sbar.maximum())

    @pyqtSlot()
    def scrollToBegin(self):
        """Scroll view to left edge."""
        sbar = self._view.horizontalScrollBar()
        sbar.setValue(sbar.minimum())

    @pyqtSlot()
    def scrollToEnd(self):
        """Scroll view to right edge."""
        sbar = self._view.horizontalScrollBar()
        sbar.setValue(sbar.maximum())

    @pyqtSlot()
    def centerView(self):
        """Center view."""
        sbar = self._view.verticalScrollBar()
        sbar.setValue((sbar.maximum() + sbar.minimum())/2)
        sbar = self._view.horizontalScrollBar()
        sbar.setValue((sbar.maximum() + sbar.minimum())/2)

    @pyqtSlot()
    def zoomIn(self):
        """Zoom in on image."""
        self.scaleImage(self._zoomFactorDelta)

    @pyqtSlot()
    def zoomOut(self):
        """Zoom out on image."""
        self.scaleImage(1 / self._zoomFactorDelta)

    @pyqtSlot()
    def actualSize(self):
        """Change zoom to show image at actual size.

        (image pixel is equal to screen pixel)"""
        self.scaleImage(1.0, combine=False)

    @pyqtSlot()
    def fitToWindow(self):
        """Fit image within view."""
        if not self._current_pixmap.pixmap():
            return
        self._view.fitInView(self._current_pixmap, Qt.KeepAspectRatio)
        # self._view.checkTransformChanged()

    @pyqtSlot()
    def fitWidth(self):
        """Fit image width to view width."""
        if not self._current_pixmap.pixmap():
            return
        margin = 2
        viewRect = self._view.viewport().rect().adjusted(margin, margin,
                                                         -margin, -margin)
        factor = (viewRect.width() * 1.0) / (self._current_pixmap.pixmap().width() * 1.0)
        self.scaleImage(factor, combine=False)

    @pyqtSlot()
    def fitHeight(self):
        """Fit image height to view height."""
        if not self._current_pixmap.pixmap():
            return
        margin = 2
        viewRect = self._view.viewport().rect().adjusted(margin, margin,
                                                         -margin, -margin)
        factor = (viewRect.height() * 1.0) / (self._current_pixmap.pixmap().height() * 1.0)
        self.scaleImage(factor, combine=False)

    def scaleImage(self, factor, combine=True):
        """Scale image by factor.

        :param float factor: either new :attr:`zoomFactor` or amount to scale
                             current :attr:`zoomFactor`

        :param bool combine: if ``True`` scales the current
                             :attr:`zoomFactor` by factor.  Otherwise
                             just sets :attr:`zoomFactor` to factor"""
        if not len(self._scene.items()):
            return

        if combine:
            self.setZoomFactor(self.getZoomFactor() * factor)
        else:
            self.setZoomFactor(factor)

    #     self._view.checkTransformChanged()
    #
    # def checkTransformChanged(self):
    #     """Return True if view transform has changed.
    #
    #     Overkill. For current implementation really only need to check
    #     if ``m11()`` has changed.
    #
    #     :rtype: bool"""
    #     delta = 0.001
    #     result = False
    #
    #     def different(t, u):
    #         if u == 0.0:
    #             d = abs(t - u)
    #         else:
    #             d = abs((t - u) / u)
    #         return d > delta
    #
    #     t = self._view.transform()
    #     u = self._transform
    #
    #     if False:
    #         print("t = ")
    #         self.dumpTransform(t, "    ")
    #         print("u = ")
    #         self.dumpTransform(u, "    ")
    #         print("")
    #
    #     if (different(t.m11(), u.m11()) or
    #         different(t.m22(), u.m22()) or
    #         different(t.m12(), u.m12()) or
    #         different(t.m21(), u.m21()) or
    #         different(t.m31(), u.m31()) or
    #         different(t.m32(), u.m32())):
    #         self._transform = t
    #         self.transformChanged.emit()
    #         result = True
    #     return result
    #
    # def dumpTransform(self, t, padding=""):
    #     """Dump the transform t to stdout.
    #
    #     :param t: the transform to dump
    #     :param str padding: each line is preceded by padding"""
    #     print("%s%5.3f %5.3f %5.3f" % (padding, t.m11(), t.m12(), t.m13()))
    #     print("%s%5.3f %5.3f %5.3f" % (padding, t.m21(), t.m22(), t.m23()))
    #     print("%s%5.3f %5.3f %5.3f" % (padding, t.m31(), t.m32(), t.m33()))