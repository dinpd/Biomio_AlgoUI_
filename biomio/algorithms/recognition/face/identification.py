from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.distances.euclidean import EuclideanDistance

from biomio.algorithms.plugins.face_identification_plugin import IdentificationSAInterface


class NearPyIdentifierSettings:
    def __init__(self):
        self.projection_count = 10
        self.distance = EuclideanDistance
        self.descriptorSize = 0
        self.detector = None
        self.threshold = 0.25


class NearPyFaceIdentifier:
    def __init__(self, database=[]):
        self.settings = NearPyIdentifierSettings()
        self.length = 64
        self.size = 100
        self._db = database
        self._engines = []
        self.interface = IdentificationSAInterface()
        if len(database) > 0:
            self._update_hash()

    def set_database(self, database):
        self._db = database
        self._engines = []
        self._update_hash()

    def _update_hash(self):
        if len(self._db) > 0:
            dimension = self.settings.descriptorSize
            for idx in range(0, 6, 1):
                rbp = RandomBinaryProjections('rbp', self.settings.projection_count)
                engine = Engine(dimension, lshashes=[rbp], distance=self.settings.distance())
                self._engines.append(engine)
            for key, database in self._db.iteritems():
                for inx in range(0, len(database["template"]), 1):
                    cluster = database["template"][inx]
                    for desc in cluster:
                        self._engines[inx].store_vector(desc, key)

    @staticmethod
    def _linear_list(data):
        desc_list = []
        for desc in data:
            for item in desc:
                desc_list.append(item)
        return desc_list

    # def _update_hash(self):
    #     print
    #     if len(self._db) > 0:
    #         dimension = self.length * self.size #len(self._db[0][0])
    #         rbp = RandomBinaryProjections('rbp', 10)
    #         self._engines.append(Engine(dimension, lshashes=[rbp], distance=ManhattanDistance()))
    #         for database in self._db:
    #             print database[0]
    #             data = []
    #             for cluster in database[0]:
    #                 data.append(self._linear_list(cluster))
    #             if len(data) > 0:
    #                 while len(data) < self.size:
    #                     inx = numpy.random.randint(len(data))
    #                     data.append(data[inx])
    #             data = self._linear_list(data)
    #             print data
    #             print len(data)
    #             fixeddata = []
    #             for idx in range(0, dimension, 1):
    #                 if len(data) > idx:
    #                     fixeddata.append(data[idx])
    #                 else:
    #                     fixeddata.append(0)
    #             self._engines[0].store_vector(fixeddata, database[2])

    # def _update_hash(self):
    #     if len(self._db) > 0:
    #         dimension = self.length * self.size
    #         #len(self._db[0][0])
    #         print dimension
    #         for idx in range(0, 6, 1):
    #             rbp = RandomBinaryProjections('rbp', 10)
    #             self._engines.append(Engine(dimension, lshashes=[rbp], distance=EuclideanDistance()))
    #         for database in self._db:
    #             print database[0]
    #             data = []
    #             id = 0
    #             for cluster in database[0]:
    #                 if len(cluster) > 0:
    #                     cluster = numpy_ndarrayToList(cluster)
    #                     while len(cluster) < self.size:
    #                         inx = numpy.random.randint(len(cluster))
    #                         cluster.append(cluster[inx])
    #                     local = self._linear_list(cluster)
    #                     print len(local)
    #                     fixeddata = []
    #                     for idx in range(0, dimension, 1):
    #                         if len(local) > idx:
    #                             fixeddata.append(local[idx])
    #                         else:
    #                             fixeddata.append(0)
    #                     print len(fixeddata)
    #                     self._engines[id].store_vector(fixeddata, database[2])
    #                 id += 1

    def identify(self, data):
        self.interface.training(**{"databases": self._db})
        clusters = data['clusters']
        self.interface.apply(**{"data": clusters})
        # glo_res = []
        # iden_stat = []
        # mcount = 0
        # mdcounts = {}

        #     engine = self._engines[idx]
        #     res = []
        #     desc_stat = []
        #     clus_stat = {
        #         "cluster_id": idx
        #     }
        #     gcount = 0
        #     dcounts = {}
        #     for desc in cluster:
        #         local = engine.neighbours(desc)
        #         res.append(local)
        #         stat = {
        #             "descriptor": numpy_ndarrayToList(desc),
        #             "count": len(local),
        #             "databases": {}
        #         }
        #         gcount += len(local)
        #         db = stat.get("databases", {})
        #         for item in local:
        #             lcount = db.get(item[1], 0)
        #             lcount += 1
        #             db[item[1]] = lcount
        #         stat["databases"] = db
        #         for key, value in db.iteritems():
        #             vcount = dcounts.get(key, 0)
        #             vcount += value
        #             dcounts[key] = vcount
        #         desc_stat.append(stat)
        #     clus_stat["items"] = desc_stat
        #     clus_stat["count"] = gcount
        #     clus_stat["databases"] = dcounts
        #     logger.logger.debug("++++++++++++++++++++++++++++")
        #     logger.logger.debug(idx)
        #     logger.logger.debug(gcount)
        #     logger.logger.debug(dcounts)
        #     mcount += gcount
        #     for key, value in dcounts.iteritems():
        #         vcount = mdcounts.get(key, 0)
        #         vcount += value
        #         mdcounts[key] = vcount
        #     iden_stat.append(clus_stat)
        #     glo_res.append(res)
        # logger.logger.debug("============================")
        # logger.logger.debug("Results:")
        # logger.logger.debug(mcount)
        # logger.logger.debug(mdcounts)
        # for key, value in mdcounts.iteritems():
        #     if value > self.settings.threshold * mcount:
        #         detector = self.settings.detector
        #         detector.importSources()


            # def identify(self, data):
            #     dimension = self.length * self.size
            #     clusters = data['clusters']
            #     data = []
            #     for cluster in clusters:
            #         data.append(self._linear_list(cluster))
            #     if len(data) > 0:
            #         while len(data) < self.size:
            #             inx = numpy.random.randint(len(data))
            #             data.append(data[inx])
            #     data = self._linear_list(data)
            #     fixeddata = []
            #     for idx in range(0, dimension, 1):
            #         if len(data) > idx:
            #             fixeddata.append(data[idx])
            #         else:
            #             fixeddata.append(0)
            #     engine = self._engines[0]
            #     glo_res = engine.neighbours(fixeddata)
            #     logger.logger.debug(glo_res)

            # def identify(self, data):
            #     dimension = self.length * self.size
            #     clusters = data['clusters']
            #     glo_res = []
            #     for index, cluster in enumerate(clusters):
            #         if len(cluster) > 0:
            #             cluster = numpy_ndarrayToList(cluster)
            #             while len(cluster) < self.size:
            #                 inx = numpy.random.randint(len(cluster))
            #                 cluster.append(cluster[inx])
            #             local = self._linear_list(cluster)
            #             fixeddata = []
            #             for idx in range(0, dimension, 1):
            #                 if len(local) > idx:
            #                     fixeddata.append(local[idx])
            #                 else:
            #                     fixeddata.append(0)
            #             print len(fixeddata)
            #             engine = self._engines[index]
            #             glo_res.append(engine.neighbours(fixeddata))
            #         else:
            #             glo_res.append([])
            #     logger.logger.debug(glo_res)
