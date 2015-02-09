import json
import base64

from tornado_json.requesthandlers import APIHandler
from tornado_json.routes import get_routes
from tornado_json import schema

import  biom.utils as utils
import  biom.faces as fs

class TrainHandler(APIHandler):

	__url_names__ = ["train"]
	
	@schema.validate(
		input_schema={
			"type": "object",
			"required":["images", "count"],
			"properties": {
				"count": {"type": "number"},
				"images": {
					"type":"array",
					"items": {
						"type": "string",
						"media": {
							"binaryEncoding": "base64",
							"type": "image/png"
						}
					}
				}
			}
		},
		output_schema={
			"type": "object",
			"required":["count"],
			"properties": {
				"count": {"type": "number"},
			}
		}
	)
	def post(self, uid):
		'''
		Add a new user and/or new faces for the user. Training is triggered if number of faces is equal or exceed value of the input parameter "count."
		Value of the output parameter "count" corresponds to a deficit of the faces after transaction.

		"Images" is an array of base64 encoded PNG images.  Images, with no faces detected, are ignored in all the calculations, described above.
		'''
		count = self.body.count
		images = self.body.images

		logging.info("Got label %s" %  uid)
		d = [numpy.asarray(base64.b64decode(img)) for img in images]
		n = utils.label_count(uid)
		fs.faces_persist(uid, d, n < count)
		n = utils.label_count(uid)
		if n >= count:
			fs.FisherFaces().train()
		return {"count": count - n}

class IdentifyHandler(APIHandler):

	__url_names__ = ["identiffy"]
	
	@schema.validate(
		input_schema={
			"type": "object",
			"required":["image"],
			"properties": {
				"image": {
					"type": "string",
					"media": {
						"binaryEncoding": "base64",
						"type": "image/png"
					}
				}
			}
		},
		output_schema={
			"type": "object",
			"properties": {
				"distance": {"type": "number"},
				"label": {"type": "string"},
				"face": {
					"type": "object",
					"required":["x", "y", "width", "height"],
					"properties": {
						"x": {"type": "number"},
						"y": {"type": "number"},
						"width": {"type": "number"},
						"height": {"type": "number"}
					}
				}
			}
		}
	)
	def post(self):
		'''
		Match an input image vs. faces in a recognizer's model (currently, only Fisher recognizer is available.)

		"Distance": estimate of how bad the match is (the lower the better.)
		"Label": UID, corresponded to the match
		"Face": coordinates of the upper left corner, as well as width and height, of a detected face area

		Empty JSON object is returned in case of no match
		'''

		image = self.body.image

		d = numpy.asarray(base64.b64decode(image))
		ff = fs.FisherFaces()
		face, label, distance = ff.predict(d)
		if distance < 1000.0: # config
			return {}
		return {
			"distance": distance,
			"label": label,
			"face": {
				"x": face[0],
				"y": face[1],
				"width": face[2],
				"height": face[3]
			}
		}

class VerifyHandler(APIHandler):

	__url_names__ = ["verify"]
	
	@schema.validate(
		input_schema={
			"type": "object",
			"required":["image"],
			"properties": {
				"image": {
					"type": "string",
					"media": {
						"binaryEncoding": "base64",
						"type": "image/png"
					}
				}
			}
		},
		output_schema={
			"type": "object",
			"required":["match"],
			"properties": {
				"distance": {"type": "number"},
				"match": {"type": "bool"}
			}
		}
	)
	def post(self, uid):
		'''
		Match an input image and UID vs. faces in a recognizer's model.
		'''

		image = self.body.image

		d = numpy.asarray(base64.b64decode(image))
		ff = fs.FisherFaces()
		face, label, distance = ff.predict(d)
		if distance < 1000.0 or label != uid: # config
			return {"match": False}
		return {
			"distance": distance,
			"match": True
		}

class LabelHandler(APIHandler):

	__url_names__ = ["labels"]

	@schema.validate(
		output_schema={
			"type":"array",
			"items": {
				"type": "object",
				"properties": {
					"label": {"type": "string"},
					"img_count": {"type": "number"}
				}
			}
		}
	)
	def get(self):
		'''
		List labels and number of faces associated with the label
		'''

		json_item = '{"label":"%s","img_count":%d}'
		json_array = ''

		for lable, count in utils.label_list():
			json_array = '%s,%s' % (json_array, json_item % (lable, count))

		if len(json_array) > 0:
			return json.loads('[%s]' % json_array[1:])
		else:
			return []

	@schema.validate(
		output_schema={
			"type": "object",
			"properties": {
				"img_count": {"type": "number"}
			}
		}
	)
	def get(self, label):
		'''
		Provide a number of faces associated with a label
		'''

		return {"img_count": utils.label_count()}

	def post(self, label):
		'''
		Add a label
		'''
		utils.label_add(label)
		return "ok"

	def delete(self, label):
		'''
		Remove a label, together with associated faces
		'''
		utils.label_remove(label)
		return "ok"
