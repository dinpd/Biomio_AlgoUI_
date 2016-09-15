def analyze_result(fn):
    def analyze(self, data):
        if type(data) == list:
            return fn(self, {'result': data})
        else:
            if data.get('result', None) is None:
                raise Exception('Nothing to analyze! Result is missing!')
        return fn(self, data)
    return analyze