from nearpy.filters import VectorFilter


class EmptyFilter(VectorFilter):
    """
    Empty filter implementation.
    """

    def __init__(self):
        pass

    def filter_vectors(self, input_list):
        """
        Returns input list.
        """
        return input_list
