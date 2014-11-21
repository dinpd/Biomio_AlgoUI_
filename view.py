from guidata.qt.QtCore import QObject
from guidata.qt.QtGui import QDockWidget, QListWidget
from guidata.qt.QtCore import (Qt, SIGNAL)

from guiqwt.plot import ImageWidget
from guidata.dataset.datatypes import DataSet, GetAttrProp
from guidata.dataset.dataitems import (IntItem, FloatArrayItem, StringItem)
from guidata.utils import update_dataset
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from guiqwt.signals import SIG_LUT_CHANGED
from guiqwt.builder import make
from guiqwt.config import _
from guiqwt import io


class ImageParam(DataSet):
    _hide_data = False
    _hide_size = True
    title = StringItem(_("Title"), default=_("Untitled"))
    data = FloatArrayItem(_("Data")).set_prop("display",
                                              hide=GetAttrProp("_hide_data"))
    width = IntItem(_("Width"), help=_("Image width (pixels)"), min=1,
                    default=100).set_prop("display",
                                          hide=GetAttrProp("_hide_size"))
    height = IntItem(_("Height"), help=_("Image height (pixels)"), min=1,
                     default=100).set_prop("display",
                                           hide=GetAttrProp("_hide_size"))


class ImageManager(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._imagelist = None
        self._imagedocks = None
        self.imagewidget()

        self._images = [] # List of ImageParam instances
        self._lut_ranges = [] # List of LUT ranges

        self._view = ImageWidget()
        self._view.setContentsMargins(10, 10, 10, 10)
        self.connect(self._view.plot, SIG_LUT_CHANGED,
                     self.lut_range_changed)
        self._properties = DataSetEditGroupBox(_("Properties"), ImageParam)
        self._properties.setEnabled(False)
        self._item = None # image item

    def current_image(self):
        return self._images[self._imagelist.currentRow()]

    def get_view(self):
        return self._view

    def get_ui_manager(self):
        return self._imagedocks

    def install_ui_manager(self):
        self.parent().addDockWidget(Qt.DockWidgetArea(1), self._imagedocks)

    def add_image(self, image):
        self._images.append(image)
        self._lut_ranges.append(None)
        self.refresh_list()
        self._imagelist.setCurrentRow(len(self._images)-1)
        plot = self._view.plot
        plot.do_autoscale()

    def add_image_from_file(self, filename):
        image = ImageParam()
        image.title = unicode(filename)
        image.data = io.imread(filename)
        # image.height, image.width = image.data.shape
        self.add_image(image)

    def show_image(self, image):
        plot = self._view.plot
        plot.do_autoscale()

    def imagewidget(self):
        self._imagedocks = QDockWidget(_("Image Manager"))
        self._imagelist = QListWidget(self._imagedocks)
        self._imagedocks.setWidget(self._imagelist)
        self.connect(self._imagelist, SIGNAL("currentRowChanged(int)"),
                     self.current_item_changed)
        self.connect(self._imagelist, SIGNAL("itemSelectionChanged()"),
                     self.selection_changed)

    def refresh_list(self):
        self._imagelist.clear()
        self._imagelist.addItems([image.title for image in self._images])

    def selection_changed(self):
        row = self._imagelist.currentRow()
        self._properties.setDisabled(row == -1)

    def current_item_changed(self, row):
        image, lut_range = self._images[row], self._lut_ranges[row]
        self.show_data(image.data, lut_range)
        update_dataset(self._properties.dataset, image)
        self._properties.get()

    def lut_range_changed(self):
        row = self._imagelist.currentRow()
        self._lut_ranges[row] = self._item.get_lut_range()

    def show_data(self, data, lut_range=None):
        plot = self._view.plot
        if self._item is not None:
            self._item.set_data(data)
            if lut_range is None:
                lut_range = self._item.get_lut_range()
            self._view.set_contrast_range(*lut_range)
            self._view.update_cross_sections()
        else:
            self._item = make.image(data)
            plot.add_item(self._item, z=0)
        plot.replot()