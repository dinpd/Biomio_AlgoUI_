

class Tester:
    def __init__(self, test=None):
        self._algo = None
        self._struct = None
        self._est = None
        self._analyser = None
        self._test = test

    def ready(self):
        return self._algo is not None \
               and self._struct is not None \
               and self._est is not None

    def set_algorithm(self, algo):
        if algo is not None:
            self._algo = algo

    def set_structure(self, struct):
        if struct is not None:
            self._struct = struct

    def set_estimation(self, est):
        if est is not None:
            self._est = est

    def set_test(self, test):
        if test is not None:
            self._test = test

    def set_analyser(self, analyser):
        if analyser is not None:
            self._analyser = analyser

    def run(self, test_data):
        out = []
        if type(test_data) == list:
            for data in test_data:
                out.append(self._test.apply(data))
        else:
            for data in test_data.images():
                out.append(self._test.apply(data))
        if self._analyser is not None:
            self._analyser.apply(out)
