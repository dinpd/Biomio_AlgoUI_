from yapsy.IPlugin import IPlugin


class IAlgorithmPlugin(IPlugin):
    def set_image_manager(self, manager):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def set_resources_manager(self, manager):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_algorithms_actions(self, parent):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_algorithms_list(self):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_test_actions(self, parent):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_interfaces(self):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def settings(self, name):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def apply(self, name, settings=dict()):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()