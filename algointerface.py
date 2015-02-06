

USER_DATABASE_SETTINGS = 0
ALGO_DATABASE_SETTINGS = 1
FULL_DATABASE_SETTINGS = 2


class AlgorithmsInterface:
    @staticmethod
    def getDatabasesList():
        pass

    @staticmethod
    def getDatabaseSettings(database_name, settings_type=USER_DATABASE_SETTINGS):
        pass

    @staticmethod
    def getAlgorithmsList():
        pass

    @staticmethod
    def getSettingsTemplate(algorithm_name):
        pass

    @staticmethod
    def applyAlgorithm(algorithm_name, settings=dict()):
        pass