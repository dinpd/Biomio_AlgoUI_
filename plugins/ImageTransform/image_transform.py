from guidata.qt.QtCore import SIGNAL, QObject, QCoreApplication, pyqtSignal
from guidata.qt.QtGui import QAction, QFileDialog, QMenu
from guidata.configtools import get_icon
from guiqwt.config import _
from biomio.algorithms.experimental.experimental import imageDifference
from biomio.algorithms.cvtools import equalizeHist, grayscale, resize
from biomio.algorithms.cascades.detectors import OptimalROIDetector
from plugins.ImageTransform.img_trans_widgets import ResizeWidget
from biomio.algorithms.imgobj import loadImageObject
from ui.algorithm_panel import AlgorithmPanel
from imageproperties import ImageProperties
from biomio.algorithms.logger import logger
from aiplugins import IAlgorithmPlugin

EQ_ACTION_TITLE = 'Action: EqualizeHist::'
GR_ACTION_TITLE = 'Action: Grayscale::'
DF_ACTION_TITLE = 'Action: Difference::'
OR_ACTION_TITLE = 'Action: Optimal ROI::'

IMAGE_TRANSFORM_RESIZE = 'ImageTransform.Resize'


class ImageTransformPlugin(QObject, IAlgorithmPlugin):
    def __init__(self):
        super(ImageTransformPlugin, self).__init__()

    def set_image_manager(self, manager):
        self._imanager = manager
        self._setwigets = []
        self._setwigets.append(self.create_transform_widget())

    def get_algorithms_actions(self, parent):
        transform_menu = QMenu(parent)
        transform_menu.setTitle(_("Image Transformation"))
        transform_menu.addAction(self.add_grayscale_action(transform_menu))
        transform_menu.addAction(self.add_equalize_action(transform_menu))
        transform_menu.addAction(self.add_difference_action(transform_menu))
        transform_menu.addAction(self.add_optimalroi_action(transform_menu))
        return [transform_menu, self.add_transform_action(parent)]

    def get_algorithms_list(self):
        return []

    def get_test_actions(self, parent):
        pass

    def get_interfaces(self):
        return self._setwigets

    def settings(self, name):
        pass

    def apply(self, name, settings=dict()):
        pass

    def add_grayscale_action(self, parent):
        gr_action = QAction(parent)
        gr_action.setText(_("Grayscale"))
        gr_action.setIcon(get_icon('grayscale.png'))
        self.connect(gr_action, SIGNAL("triggered()"), self.slot_grayscale)
        return gr_action

    def slot_grayscale(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(GR_ACTION_TITLE + curr.title())
            image.data(grayscale(curr.data()))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_equalize_action(self, parent):
        eq_action = QAction(parent)
        eq_action.setText(_("Equalize Histogram"))
        eq_action.setIcon(get_icon('equalize.png'))
        self.connect(eq_action, SIGNAL("triggered()"), self.slot_equalize)
        return eq_action

    def slot_equalize(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(EQ_ACTION_TITLE + curr.title())
            image.data(equalizeHist(curr.data()))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_difference_action(self, parent):
        df_action = QAction(parent)
        df_action.setText(_("Difference"))
        df_action.setIcon(get_icon('diff.png'))
        self.connect(df_action, SIGNAL("triggered()"), self.slot_difference)
        return df_action

    def slot_difference(self):
        curr = self._imanager.current_image()
        if self._imanager and curr:
            filelist = QFileDialog.getOpenFileNames(None, "Select source images", ".")
            source_list = []
            if not filelist.isEmpty():
                logger.debug("Loading started...")
                i = 0
                for imfile in filelist:
                    i += 1
                    obj = loadImageObject(str(imfile))
                    source_list.append(obj['data'])
                    QCoreApplication.processEvents()
                logger.debug("Loading finished.")
            image = ImageProperties()
            image.title(DF_ACTION_TITLE + curr.title())
            image.data(imageDifference(curr.data(), source_list))
            image.height(curr.height())
            image.width(curr.width())
            self._imanager.add_image(image)

    def add_optimalroi_action(self, parent):
        or_action = QAction(parent)
        or_action.setText(_("Optimal ROI"))
        or_action.setIcon(get_icon('roi.png'))
        self.connect(or_action, SIGNAL("triggered()"), self.slot_optimalroi)
        return or_action

    def slot_optimalroi(self):
        filelist = QFileDialog.getOpenFileNames(None, "Select source images", ".")
        source_list = []
        if not filelist.isEmpty():
            logger.debug("Loading started...")
            i = 0
            for imfile in filelist:
                i += 1
                obj = loadImageObject(str(imfile))
                source_list.append(obj)
                QCoreApplication.processEvents()
            logger.debug("Loading finished.")
        src = loadImageObject(str(filelist[0]))
        detector = OptimalROIDetector()
        source_list = detector.detect(source_list)

        i = 0
        for obj in source_list:
            image = ImageProperties()
            image.title(OR_ACTION_TITLE + "#" + str(i))
            image.data(obj['data'])
            image.height(obj['data'].shape[0])
            image.width(obj['data'].shape[1])
            self._imanager.add_image(image)
            i += 1

    def add_transform_action(self, parent):
        transform_action = QAction(parent)
        transform_action.setText(_("Image Transformation"))
        transform_action.setIcon(get_icon('img.png'))
        transform_action.setCheckable(True)
        self.connect(transform_action, SIGNAL("triggered(bool)"), self.settings_opened)
        return transform_action

    settings_opened = pyqtSignal(bool, name='settingsOpened')

    def create_transform_widget(self):
        self._settings_dock = AlgorithmPanel()
        self._settings_dock.setEnableSerialProcessing(False)
        self._settings_dock.setWindowTitle("Image Transformation Settings")
        self._settings_dock.setVisible(False)
        self.settings_opened.connect(self._settings_dock.setVisible)
        self.connect(self._settings_dock, SIGNAL("applied()"), self.image_transform)
        self._settings_dock.addAlgorithm(IMAGE_TRANSFORM_RESIZE, ResizeWidget())
        return self._settings_dock

    def image_transform(self):
        curr = self._imanager.current_image()
        algo_settings = self._settings_dock.settings()
        if self._imanager and curr:
            image = ImageProperties()
            image.title(str(algo_settings['name'] + curr.title()))
            method = _TRANSFORMATION_LIST.get(algo_settings['name'], None)
            if method is not None:
                res = method(curr.data(), algo_settings['settings'])
                image.data(res)
                image.height(res.shape[0])
                image.width(res.shape[1])
            else:
                image.data(curr.data())
                image.height(curr.height())
                image.width(curr.width())
            self._imanager.add_image(image)


def _resize(image, settings):
    logger.debug(settings)
    return resize(image, dsize=settings.get('dsize', None), fx=settings.get('fx', None), fy=settings.get('fy', None))


_TRANSFORMATION_LIST = {
    IMAGE_TRANSFORM_RESIZE: _resize
}
