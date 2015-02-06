"""
Interface for Biom.io algorithms.
"""

USER_DATABASE_SETTINGS = 0
ALGO_DATABASE_SETTINGS = 1
FULL_DATABASE_SETTINGS = 2


class AlgorithmsInterface:
    @staticmethod
    def getDatabasesList():
        """
        Return list of current supported databases.

        :return: list of databases.
        """
        pass

    @staticmethod
    def getDatabaseSettings(database_name, settings_type=USER_DATABASE_SETTINGS):
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
        pass

    @staticmethod
    def getAlgorithmsList():
        """
        Return list of current supported algorithms.

        :return: list of algorithms.
        """
        pass

    @staticmethod
    def getSettingsTemplate(algorithm_name):
        """
        Return settings dictionary with keys and empty value for filling algorithm settings.

        :param algorithm_name: name of algorithm from AlgorithmsInterface.getAlgorithmsList()
        :return: dictionary for customizing of algorithm's settings
        """
        pass

    @staticmethod
    def applyAlgorithm(algorithm_name, settings=dict()):
        """
        Starts algorithm for execution by algorithm_name using algorithm settings.

        :param algorithm_name: name of algorithm from AlgorithmsInterface.getAlgorithmsList()
        :param settings: dictionary with algorithm settings
        :return: dictionary of the results of the algorithm
        """
        pass