"""
Interface for Biom.io algorithms.

Algorithm Settings
   Key           Value
   'database'  Name of database
   'data'      Test object image

Algorithms Results:
Algorithm: KeypointsVerificationAlgorithm
Result: dictionary
   Key           Value
   'log'       Log of the algorithm
   'result'    Boolean. Contain 'True' if verification successfully,
               otherwise return 'False'
"""
from webalgomanager import (WebAlgorithmsManager,
                            USER_DATABASE_SETTINGS, ALGO_DATABASE_SETTINGS, FULL_DATABASE_SETTINGS)


class AlgorithmsInterface:
    def __init__(self):
        self._imanager = WebAlgorithmsManager()

    def getDatabasesList(self):
        """
        Return list of current supported databases.

        :return: list of databases.
        """
        return self._imanager.databases_list()

    def getDatabaseSettings(self, database_name, settings_type=USER_DATABASE_SETTINGS):
        """
        Return dictionary with database settings.

        :param database_name: name of database from AlgorithmsInterface.getDatabasesList()
        :param settings_type: type of settings dictionary
            USER_DATABASE_SETTINGS - only general parameters: size of databases, general and
             average number of key features.
            ALGO_DATABASE_SETTINGS - detector- and extractor-based parameters: detector type,
             detector settings and other algorithm settings.
            FULL_DATABASE_SETTINGS - all (USER_DATABASE_SETTINGS and ALGO_DATABASE_SETTINGS)
             parameters.
        :return: dictionary with database settings.
        """
        return self._imanager.database_settings(database_name, settings_type)

    def getAlgorithmsList(self):
        """
        Return list of current supported algorithms.

        :return: list of algorithms.
        """
        return self._imanager.algorithms_list()

    def getSettingsTemplate(self, algorithm_name):
        """
        Return settings dictionary with keys and empty value for filling algorithm settings.

        :param algorithm_name: name of algorithm from AlgorithmsInterface.getAlgorithmsList()
        :return: dictionary for customizing of algorithm's settings
        """
        return self._imanager.algosettings(algorithm_name)

    def applyAlgorithm(self, algorithm_name, settings=dict()):
        """
        Starts algorithm for execution by algorithm_name using algorithm settings.

        :param algorithm_name: name of algorithm from AlgorithmsInterface.getAlgorithmsList()
        :param settings: dictionary with algorithm settings
        :return: dictionary of the results of the algorithm
        """
        return self._imanager.apply_algorithm(algorithm_name, settings)