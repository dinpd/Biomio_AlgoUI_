from server.biomio.algorithms.flows.base import IAlgorithm
from defs import SEPARATOR_LINE


class OutputConsolePrint(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        print(SEPARATOR_LINE)
        print(data.get('output', ""))
        print(SEPARATOR_LINE)
        return data
