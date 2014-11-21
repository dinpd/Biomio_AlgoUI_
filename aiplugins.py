from yapsy.IPlugin import IPlugin


class IAlgorithmPlugin(IPlugin):
    def set_image_manager(self, manager):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_action(self, parent):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()

    def get_interfaces(self):
        """
        This method should be reimplemented by custom plugins
        """
        raise NotImplementedError()