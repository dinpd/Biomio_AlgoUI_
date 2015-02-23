#!/usr/bin/env python2.7

import logging
import json
import tornado.ioloop
from tornado.options import define, options

#from ws.application import WsApplication

from tornado_json.routes import get_routes
from tornado_json.application import Application as ApiApplication

import biom.faces as fs
from hashing.hash_test import lshash_test, nearpy_test
# from hashing.nearpy_hash import NearPyHash

define("ws_port", default=8888, help="run on the given poort", type=int)
define("api_port", default=9999, help="run on the given poort", type=int)


def initWsApp(port):
    app = WsApplication()
    app.listen(port)

def initApiApp(port):
	import biom
	routes = get_routes(biom)
	logging.info("REST API Routes: " + json.dumps(
		[(url, repr(rh)) for url, rh in routes], indent=2)
	)
	app = ApiApplication(routes=routes, settings={})
	app.listen(port)


def main():
    # tornado.options.parse_command_line()

    print "Create classifier"
    ff = fs.FisherFaces()
    print "Initialization..."

    print ff.model_loaded()
    if not ff.model_loaded():
        print "Labels loaded"
        logging.info("Labels loaded")
        ff.train()
        print "Model trained"
        logging.info("Model trained")
    else:
        print "Model loaded"
        logging.info("Model loaded")
    print "Initialization finished."

    if ff.model_loaded():
        img = fs.load_test("data/images/s2/4.pgm")
        faces = ff.detect(img)
        print ff.predict(img)

        # Two hash tests for face regions
        lshash_test(faces)
        nearpy_test(faces)


    # initWsApp(options['ws_port'])
    # logging.info("WS App is listening on port {0}".format(options['ws_port']))

    # initApiApp(options['api_port'])
    # logging.info("REST API App is listening on port {0}".format(options['api_port']))

    # tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
