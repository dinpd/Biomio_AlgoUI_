from guidata.qt.QtGui import QDockWidget, QListWidget, QWidget, QLineEdit, QVBoxLayout
from biomio.algorithms.cvtools.system import saveNumpyImage
from guidata.qt.QtCore import QObject, Qt, SIGNAL
from imageproperties import ImageProperties
from guiqwt.signals import SIG_LUT_CHANGED
from viewers import AbstractImageViewer
from imageviewer import ImageViewer
from guiqwt.plot import ImageWidget
from guiqwt.builder import make
from guiqwt.config import _
import shutil
import os
# from guidata.utils import update_dataset
# from guidata.dataset.qtwidgets import DataSetEditGroupBox


class ImageManager(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._imagelist = None
        self._imagedocks = None
        self._taglist = None
        self.imagewidget()

        self._images = []  # List of ImageParam instances

        self._view = ImageViewer()

        # self._properties = DataSetEditGroupBox(_("Properties"), ImageParam)
        # self._properties.setEnabled(False)

    def current_image_index(self):
        if self._imagelist is not None:
            return self._imagelist.currentRow()
        return -1

    def current_image(self):
        if len(self._images) > 0:
            return self._images[self._imagelist.currentRow()]
        return None

    def count(self):
        return len(self._images)

    def images(self):
        return self._images

    def delete_image(self, index):
        if len(self._images) > index:
            cur = self._imagelist.currentRow()
            if cur >= index:
                cur -= 1
            self._images.pop(index)
            self.refresh_list()
            self._imagelist.setCurrentRow(cur)
            self._view.update_plot()

    def delete_all(self):
        self._images = []
        self.refresh_list()
        self._view.update_plot()

    def save_image(self, filename, i):
        image = self._images[i]
        if image is not None:
            saveNumpyImage(filename, image.data())

    def save_images_by_tags(self, dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        for image in self._images:
            tag = image.tags()
            file_path = os.path.join(dir_name, os.path.basename(image.path()) + ".jpg")
            if tag is not None and len(tag) > 0:
                tag_path = os.path.join(dir_name, tag)
                if not os.path.exists(tag_path):
                    os.mkdir(tag_path)
                file_path = os.path.join(tag_path, os.path.basename(image.path()) + ".jpg")
            saveNumpyImage(file_path, image.data())

    def copy_images_by_tags(self, dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        for image in self._images:
            tag = image.tags()
            file_path = os.path.join(dir_name, os.path.basename(image.path()) + ".jpg")
            if tag is not None and len(tag) > 0:
                tag_path = os.path.join(dir_name, tag)
                if not os.path.exists(tag_path):
                    os.mkdir(tag_path)
                file_path = os.path.join(tag_path, os.path.basename(image.path()) + ".jpg")
            shutil.copyfile(image.path(), file_path)

    def get_view(self):
        return self._view

    def get_ui_manager(self):
        return self._imagedocks

    def install_ui_manager(self):
        self.parent().addDockWidget(Qt.DockWidgetArea(1), self._imagedocks)

    def add_temp_image(self, image):
        self._view.setImage(image)

    def add_image(self, image):
        self._images.append(image)
        self.refresh_list()
        self._imagelist.setCurrentRow(len(self._images) - 1)
        self._view.update_plot()

    def add_image_from_file(self, filename):
        image = ImageProperties(filename)
        self.add_image(image)

    def imagewidget(self):
        self._imagedocks = QDockWidget(_("Image Manager"))
        imagewidget = QWidget(self._imagedocks)
        self._imagelist = QListWidget(imagewidget)
        self._taglist = QLineEdit(imagewidget)
        elLayout = QVBoxLayout()
        elLayout.addWidget(self._imagelist)
        elLayout.addWidget(self._taglist)
        imagewidget.setLayout(elLayout)
        self._imagedocks.setWidget(imagewidget)
        self.connect(self._imagelist, SIGNAL("currentRowChanged(int)"),
                     self.current_item_changed)
        self.connect(self._taglist, SIGNAL("editingFinished()"), self.current_tags_modified)
        # self.connect(self._imagelist, SIGNAL("itemSelectionChanged()"),
        #              self.selection_changed)

    def refresh_list(self):
        self._imagelist.clear()
        self._imagelist.addItems(["[{}] {}".format(image.tags(), image.title()) for image in self._images])

    # def selection_changed(self):
    #     print "selection_changed"
    #     row = self._imagelist.currentRow()
    #     self._view.setImage(self._images[row])
    #     # self._properties.setDisabled(row == -1)

    def current_item_changed(self, row):
        if len(self._images) > row >= 0:
            image = self._images[row]
            self._view.setImage(image)
            self._taglist.setText(image.tags())
            # update_dataset(self._properties.dataset, image.toImageParam())
            #  self._properties.get()
        else:
            self._view.setImage(None)
            self._taglist.setText("")

    def current_tags_modified(self):
        if (self._imagelist.currentRow() >= 0) and (self._imagelist.currentRow() < len(self._images)):
            img = self._images[self._imagelist.currentRow()]
            if img is not None:
                img.tags(str(self._taglist.text()))
                self._imagelist.currentItem().setText("[{}] {}".format(img.tags(), img.title()))


class GuiQwtImageViewer(ImageWidget, AbstractImageViewer):
    def __init__(self, parent=None):
        super(GuiQwtImageViewer, self).__init__(parent)

        self._current_image = None

        self.setContentsMargins(10, 10, 10, 10)
        self.connect(self.plot, SIG_LUT_CHANGED,
                     self.lut_range_changed)
        self._item = None  # image item

    def update_plot(self):
        plot = self.plot
        plot.do_autoscale()

    def setImage(self, image):
        if image is None:
            return
        self._current_image = image
        plot = self.plot
        if self._item is not None:
            self._item.set_data(image.data())
            if image.lut_range() is None:
                lut_range = self._item.get_lut_range()
            self._view.set_contrast_range(*lut_range)
            self._view.update_cross_sections()
        else:
            self._item = make.image(image.data())
            plot.add_item(self._item, z=0)
        plot.replot()

    def lut_range_changed(self):
        if self._current_image is not None:
            self._current_image.lut_range(self._item.get_lut_range())
