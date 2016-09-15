from tester import Tester


class ImageTester(Tester):
    def __init__(self):
        Tester.__init__(self)

    def run(self, test_data):
        if not test_data.valid():
            raise Exception("Test data object is invalid.")
        if not self.ready():
            raise Exception("Tester is not ready!!!")

        results = []
        print "Prepare Database"
        for img_set in self._struct.directories():
            for img in img_set.images():
                data = {'img': img}
                res = self._algo.apply(data)
                if res is not None:
                    img.attribute('rep', res['rep'])
        print "Prepare Test Data"
        res = self._algo.apply({'img': test_data})
        print "###", res
        if res is not None:
            test_data.attribute('rep', res['rep'])
        print "Estimate"
        for img_set in self._struct.directories():
            data = {
                'test': test_data,
                'train': img_set
            }
            results.append(self._est.apply(data))
        print results

