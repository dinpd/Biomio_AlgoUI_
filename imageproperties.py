from guidata.dataset.datatypes import DataSet, GetAttrProp
from guidata.dataset.dataitems import (IntItem, FloatArrayItem, StringItem)

from guiqwt.config import _
from guiqwt import io

import cv2


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


class ImageProperties:
    def __init__(self, filepath=None):
        if filepath is not None:
            self._title = unicode(filepath)
            self._path = filepath
            self._data = cv2.imread(filepath, cv2.CV_LOAD_IMAGE_COLOR)
            self._height = 0
            self._width = 0
            #self._height, self._width = self._data.shape
            self._lut_range = None
        else:
            self._title = "untitled"
            self._path = ""
            self._data = None
            self._height = 0
            self._width = 0
            self._lut_range = None

    def title(self, str_title=None):
        if str_title is not None:
            self._title = unicode(str_title)
        return self._title

    def path(self, fpath=None):
        if fpath is not None:
            self._path = fpath
        return self._path

    def data(self, image=None):
        if image is not None:
            self._data = image
        return self._data

    def height(self, h=None):
        if h is not None:
            self._height = h
        return self._height

    def width(self, w=None):
        if w is not None:
            self._width = w
        return self._width

    def lut_range(self, lrange=None):
        if lrange is not None:
            self._lut_range = lrange
        return self._lut_range

    def toImageParam(self):
        param = ImageParam()
        param.title = self._title
        if self._data is None:
            param.data = io.imread(self._path, to_grayscale=True)
        else:
            param.data(self._data)
        param.height, param.width = param.data.shape
        return param

    @classmethod
    def fromImageParam(cls, param):
        prop = ImageProperties()
        prop.title(param.title)
        prop.data(param.data)
        prop.height(param.height)
        prop.width(param.width)
        return prop