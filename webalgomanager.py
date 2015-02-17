from yapsy.PluginManager import PluginManager
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from aiplugins import IAlgorithmPlugin
from ConfigParser import ConfigParser
import json
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(APP_ROOT, 'databases')
PLUGIN_PATH = os.path.join(APP_ROOT, 'webplugins')

PLUGIN_PLACES = [PLUGIN_PATH]
DATABASE_PLACES = [DATABASE_PATH]

USER_DATABASE_SETTINGS = 0
ALGO_DATABASE_SETTINGS = 1
FULL_DATABASE_SETTINGS = 2


def get_config_file_path():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(curr_dir, 'plugin_config.ini')
    return config_file_path


def config_change_trigger():
    print 'config changed!'


class WebAlgorithmsManager(object):
    def __init__(self):
        self._plmanager = None
        self._cpmanager = None
        self._algorithms = []
        self._algolist = dict()
        self.init_plugin_manager()
        self.get_actions()
        self._databases = []
        self._databases_list = []
        self.get_databases()
        pass

    def databases_list(self):
        return self._databases_list

    def database_settings(self, name, settings_type):
        for database in self._databases:
            if database['name'] == name or database['id'] == name:
                return database['info']
        return dict()

    def algorithms_list(self):
        return self._algorithms

    def get_actions(self):
        for plugin_info in self._plmanager.getAllPlugins():
            if plugin_info.is_activated:
                algo_list = plugin_info.plugin_object.get_algorithms_list()
                for algo in algo_list:
                    self._algolist[algo['pk']] = {'info': algo,
                                                  'object': plugin_info.plugin_object}
                    self._algorithms.append(algo)

    def get_databases(self):
        for path in DATABASE_PLACES:
            if os.path.exists(path):
                self._databases = []
                i = 0
                for d in os.listdir(path):
                    database = dict()
                    d_list = dict()
                    database['name'] = d
                    database['id'] = i
                    d_list['name'] = d
                    d_list['pk'] = i
                    info = path + "/" + d + "/info.json"
                    data = path + "/" + d + "/data.json"
                    with open(data, "r") as data_file:
                        source = json.load(data_file)
                        database['data'] = source
                    with open(info, "r") as info_file:
                        information = json.load(info_file)
                        database['info'] = information
                    d_list['support'] = database.get('info', dict()).get('support', "")
                    self._databases.append(database)
                    self._databases_list.append(d_list)
                    i += 1

    def algosettings(self, name):
        plugin = self._algolist.get(name)
        if plugin is not None:
            return plugin.settings(name)
        return None

    def apply_algorithm(self, name, settings=dict()):
        plugin = self._algolist.get(name)
        if plugin is not None:
            return plugin.apply(name, settings)
        return None

    def init_plugin_manager(self):
        # Configuring plugin locator
        plugin_locator = PluginFileLocator()
        plugin_locator.setPluginPlaces(PLUGIN_PLACES)

        # Initializing plugin manager...
        # categories_filter={"Default": IPlugin, "Custom": ICustomPlugin},
        self._plmanager = PluginManager(categories_filter={"Default": IAlgorithmPlugin},
                                        plugin_locator=plugin_locator)

        # decorate plugin manager with configurable feature
        self._cpmanager = ConfigurablePluginManager(decorated_manager=self._plmanager)

        # create parser for config file
        config_parser = ConfigParser()

        # set config file location
        config_parser.read(get_config_file_path())

        # set parser to configurable decorator
        self._cpmanager.setConfigParser(configparser_instance=config_parser,
                                        config_change_trigger=config_change_trigger)

        # plugin_manager.collectPlugins()
        # configurable_plugin_manager.loadPlugins()
        self._cpmanager.collectPlugins()

        self.plugins_info()

        # for plugin_info in self._plmanager.getAllPlugins():
        #     if plugin_info.is_activated:
        #         plugin_info.plugin_object.set_image_manager()

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
            #        plugin_name=plugin_info.name, option_name='option1')