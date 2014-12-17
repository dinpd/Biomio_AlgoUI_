from guidata.qt.QtCore import QObject
from guidata.qt.QtGui import QAction, QMenu
from guidata.qthelpers import create_action, add_actions, get_std_icon

from yapsy.PluginManager import PluginManager
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from aiplugins import IAlgorithmPlugin

from ConfigParser import ConfigParser

from guiqwt.config import _

import os

PLUGIN_PLACES = ['./algorithms']


def get_config_file_path():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(curr_dir, 'plugin_config.ini')
    return config_file_path


def config_change_trigger():
    print 'config changed!'


class AlgorithmsManager(QObject):
    def __init__(self, imanager):
        QObject.__init__(self)
        self._plmanager = None
        self._cpmanager = None
        self._immanager = imanager
        self._algorithms = []
        self._menu = QMenu(_("Algorithms"))
        self.init_plugin_manager()
        self.get_actions()
        self.get_widgets()
        pass

    def algorithms_menu(self):
        return self._menu

    def algorithms_settings(self):
        return self._algorithms

    def get_actions(self):
        for plugin_info in self._plmanager.getAllPlugins():
            if plugin_info.is_activated:
                actions = plugin_info.plugin_object.get_action(self._menu)
                for action in actions:
                    if (action and isinstance(action, QAction)):
                        self._menu.addAction(action)
                    if (action and isinstance(action, QMenu)):
                        self._menu.addMenu(action)

    def get_widgets(self):
        for plugin_info in self._plmanager.getAllPlugins():
            if plugin_info.is_activated:
                widgets = plugin_info.plugin_object.get_interfaces()
                if (widgets):
                    for widget in widgets:
                        if (widget):
                            self._algorithms.append(widget)

    def init_plugin_manager(self):
        #Configuring plugin locator
        plugin_locator = PluginFileLocator()
        plugin_locator.setPluginPlaces(PLUGIN_PLACES)

        #Initializing plugin manager...
        #categories_filter={"Default": IPlugin, "Custom": ICustomPlugin},
        self._plmanager = PluginManager(categories_filter={"Default": IAlgorithmPlugin}, plugin_locator=plugin_locator)

        # decorate plugin manager with configurable feature
        self._cpmanager = ConfigurablePluginManager(decorated_manager=self._plmanager)

        # create parser for config file
        config_parser = ConfigParser()

        # set config file location
        config_parser.read(get_config_file_path())

        # set parser to configurable decorator
        self._cpmanager.setConfigParser(configparser_instance=config_parser,
                                        config_change_trigger=config_change_trigger)

        #plugin_manager.collectPlugins()
        #configurable_plugin_manager.loadPlugins()
        self._cpmanager.collectPlugins()

        self.plugins_info()

        for plugin_info in self._plmanager.getAllPlugins():
            if plugin_info.is_activated:
                plugin_info.plugin_object.set_image_manager(self._immanager)

    def plugins_info(self):
        # Output of various information and activation of each plugin
        for plugin_info in self._plmanager.getAllPlugins():
            print "Loading plugin '%s' ..." % plugin_info.name
            # configurable_plugin_manager.activatePluginByName(plugin_info.name)
            print "      name : %s" % plugin_info.name
            print "      path : %s" % plugin_info.path
            print "      version : %s" % plugin_info.version
            print "      author : %s" % plugin_info.author
            print "      copyright : %s" % plugin_info.copyright
            print "      website : %s" % plugin_info.website
            print "      description : %s" % plugin_info.description
            print "      details : %s" % plugin_info.details
            print "      is Activated : %s" % plugin_info.is_activated
            print "      categories : %s" % plugin_info.categories
            print "      plugin object : %s" % plugin_info.plugin_object
            print "      error : %s" % plugin_info.error
            # configurable_plugin_manager.registerOptionFromPlugin(category_name='Default',
            #     plugin_name=plugin_info.name, option_name='option1', option_value='value1')
            # print "      option1 : %s" % self._cpmanager.readOptionFromPlugin(category_name='Default',
            #                                                                   plugin_name=plugin_info.name, option_name='option1')