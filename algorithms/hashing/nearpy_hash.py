import numpy

import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt

from nearpy import Engine
from nearpy.hashes import RandomDiscretizedProjections, RandomBinaryProjections
from nearpy.filters import NearestFilter, UniqueFilter
from nearpy.experiments import DistanceRatioExperiment


class NearPyHash:
    def __init__(self, dimension=100):
        self._dimension = dimension
        self._dataset = []
        self._bin_widths = []
        self._engines = []

    def addEngine(self, engine):
        if engine is not None:
            self._engines.append(engine)

    def RandomBinaryProjectionsEngine(self, projection_count=10):
        rbp = RandomBinaryProjections('rbp', projection_count)
        engine = Engine(self._dimension, lshashes=[rbp])
        return engine

    def addRandomBinaryProjectionsEngine(self, projection_count=10):
        self._engines.append(self.RandomBinaryProjectionsEngine(projection_count))

    def store_dataset(self, dataset):
        self._dataset = dataset

    def init_engines(self):
        i = 0
        for r in self._dataset:
            for engine in self._engines:
                engine.store_vector(r, 'set_%d' % i)
            i += 1

    def add_dataset(self, data, key):
        for engine in self._engines:
            engine.store_vector(data, key)

    def neighbours(self, set):
        res = []
        for engine in self._engines:
            neb = engine.neighbours(set)
            for els in neb:
                res.append(els)
        return res


    def activate_engine(self):
        # We are looking for the ten closest neighbours
        nearest = NearestFilter(10)
        # We want unique candidates
        unique = UniqueFilter()

        # We are going to test these bin widths
        self._bin_widths = [0.0001 * x for x in range(1, 20)]
        # Create engines for all configurations
        for bin_width in self._bin_widths:
            # Use four random 1-dim discretized projections
            rdp1 = RandomDiscretizedProjections('rdp1', 1, bin_width)
            rdp2 = RandomDiscretizedProjections('rdp2', 1, bin_width)
            rdp3 = RandomDiscretizedProjections('rdp3', 1, bin_width)
            rdp4 = RandomDiscretizedProjections('rdp4', 1, bin_width)

            # Create engine with this configuration
            engine = Engine(self._dimension, lshashes=[rdp1, rdp2, rdp3, rdp4],
                            vector_filters=[unique, nearest])

            # Add engine to list of engines to evaluate
            self._engines.append(engine)

    def distance_ratio_query(self, data, template):
        # Create experiment (looking for ten closest neighbours).
        # The constructor performs exact search for evaluation.
        # So the data set should not be too large for experiments.
        exp = DistanceRatioExperiment(template, data, coverage_ratio=0.2)

        # Perform experiment for all engines
        return exp.perform_experiment(self._engines)

    @classmethod
    def test(cls, dimension=100):
        print "==================================================="
        print "=                   NearPy Tests                  ="
        print "=           Test: NearPy General Test             ="
        print "==================================================="
        hash = NearPyHash(dimension)

        # Set dimension and vector count for this experiment
        vector_count = 100
        # Create data set from two clusters
        vectors = []

        print 'Creating test data...'

        center = numpy.random.randn(dimension)
        for index in range(vector_count / 2):
            vector = center + 0.01 * numpy.random.randn(dimension)
            vectors.append(vector)

        center = numpy.random.randn(dimension)
        for index in range(vector_count / 2):
            vector = center + 0.01 * numpy.random.randn(dimension)
            vectors.append(vector)

        print vectors

        print 'Creating engines...'

        hash.activate_engine()

        print 'Creating experiment and performing exact search...'

        print 'Performing experiment for all engines...'

        result = hash.distance_ratio_query(vectors, 2)

        print 'Plotting resulting graph...'

        # Collect these measures from all result items
        distance_ratios = []
        searchtimes = []
        resultsizes = []

        for item in result:
            distance_ratios.append(item[0])
            resultsizes.append(item[1])
            searchtimes.append(item[2])

        # Plot measures
        ticks = hash._bin_widths
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(ticks, distance_ratios)
        ax.legend(['distance_ratios'], loc='upper right')
        ax.set_xlabel('bin width')
        ax.set_title('random discretized 1-dim projections')
        plt.show()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(ticks, searchtimes)
        ax.legend(['search_time'], loc='upper right')
        ax.set_xlabel('bin width')
        ax.set_title('random discretized 1-dim projections')
        plt.show()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(ticks, resultsizes)
        ax.legend(['result_size'], loc='upper right')
        ax.set_xlabel('bin width')
        ax.set_title('random discretized 1-dim projections')
        plt.show()

        print 'Finished.'

    @classmethod
    def test2(cls):
        # Dimension of our vector space
        dimension = 5

        # Create a random binary hash with 10 bits
        rbp = RandomBinaryProjections('rbp', 10)

        # Create engine with pipeline configuration
        engine = Engine(dimension, lshashes=[rbp])

        # Index 1000000 random vectors (set their data to a unique string)
        for index in range(1000):
            v = numpy.random.randn(dimension)
            engine.store_vector(v, 'data_%d' % index)

        # Create random query vector
        query = numpy.random.randn(dimension)

        # Get nearest neighbours
        N = engine.neighbours(query)
        print N