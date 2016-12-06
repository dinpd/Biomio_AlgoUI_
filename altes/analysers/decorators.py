import time


def analyze_result(fn):
    def analyze(self, data):
        if type(data) == list:
            return fn(self, {'result': data})
        else:
            if data.get('result', None) is None:
                raise Exception('Nothing to analyze! Result is missing!')
        return fn(self, data)
    return analyze


def analyze_time(fn):
    def analyze(self, data):
        start = time.time()
        res = fn(self, data)
        end = time.time()
        print("####################################################################################################")
        print("Execution time: {} s.".format(end - start))
        print("####################################################################################################")
        return res
    return analyze
