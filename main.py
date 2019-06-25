import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
# from pyimagesearch.classify import ClassifyImage
import argparse
from flask import Flask, jsonify, render_template, Response
from threading import Thread
from logging import Logger
import cv2
import time
from camera_opencv import Camera
import csv
import json

from mjpegviewer import MjpegViewer

# For Windows
kivy.require("1.10.1")
# For Ubuntu
# kivy.require("1.9.1")
app = Flask(__name__)

scanning = True
source = ""
leafs = []

with open('leafs.csv', encoding='windows-1252') as csv_file:
    leafs =  list(csv.reader(csv_file, delimiter=','))

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/setting', methods=['GET'])
def set_scanning():
	global scanning
	scanning = True
	return sourceChecker()

@app.route('/<int:leaf_id>', methods=['GET'])
def get_tasks(leaf_id):
	global scanning
	global source
	global leafs
	if scanning:
		leafinfo = {}
		for leaf in leafs:
			if int(leaf[0]) == leaf_id:
				leafinfo["name"] = leaf[1]
				leafinfo["desc"] = leaf[2]
				leafinfo["header1"] = leaf[3]
				leafinfo["ways"] = leaf[4]
				leafinfo["header2"] = leaf[5]
				leafinfo["medicinal"] = leaf[6]
				break
		if leafinfo:
			source = json.dumps(leafinfo, ensure_ascii=False)
		else:
			leafinfo["name"] = ""
			leafinfo["desc"] = ""
			leafinfo["header1"] = "Not in Model"
			leafinfo["ways"] = ""
			leafinfo["header2"] = ""
			leafinfo["medicinal"] = ""
			source = json.dumps(leafinfo, ensure_ascii=False)
	else:
		leafinfo["name"] = ""
		leafinfo["desc"] = ""
		leafinfo["header1"] = ""
		leafinfo["ways"] = ""
		leafinfo["header2"] = ""
		leafinfo["medicinal"] = ""
		source = json.dumps(leafinfo, ensure_ascii=False)
	return ''

def sourceChecker():
	global source
	global scanning
	while source == "" and scanning:
		time.sleep(2)
	return source

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ConnectPage(FloatLayout):
	data = {}
	model = "Model"
	labelbin = "Label Bin"
	resetbut = True
	def __init__(self, **kwargs):
		# for Windows
		# super().__init__(**kwargs)
		# for Ubuntu
		super(ConnectPage, self).__init__(**kwargs)

	def findImage_button(self):
		self.show_load("Image")

	def labelBin_button(self):
		self.show_load("LabelBin")

	def model_button(self):
		self.show_load("Model")

	def saveData(self, information):
		self.data.update(information)

	def classify_button(self):
		if self.resetbut:
			self.ids.resetbutton.text = "Reset"
			self.ids.labelclassificationlabel1.text = "Scanning..."
			def got_json(req, result):
				leaf = json.loads(result)
				self.ids.labelclassificationname.text = leaf["name"]
				self.ids.labelclassificationdesc.text = leaf["desc"]
				self.ids.labelclassificationlabel1.text = leaf["header1"]
				self.ids.labelclassificationways.text = leaf["ways"]
				self.ids.labelclassificationlabel2.text = leaf["header2"]
				self.ids.labelclassificationmedicine.text = leaf["medicinal"]
			UrlRequest('http://localhost:5000/setting', got_json)
			self.resetbut = False
		else:
			global scanning
			global source
			scanning = False
			source = ""
			self.ids.resetbutton.text = "Classify Image"
			self.ids.labelclassificationname.text = ""
			self.ids.labelclassificationdesc.text = ""
			self.ids.labelclassificationlabel1.text = ""
			self.ids.labelclassificationways.text = ""
			self.ids.labelclassificationlabel2.text = ""
			self.ids.labelclassificationmedicine.text = ""
			self.resetbut = True

	def dismiss_popup(self):
		self._popup.dismiss()

	def show_load(self, title):
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title=title, content=content,
		                    size_hint=(0.9, 0.9))
		self._popup.open()

	def reset_button(self):
		global scanning
		global source
		scanning = False
		source = ""
		self.ids.labelclassificationname.text = ""
		self.ids.labelclassificationdesc.text = ""

	def load(self, path, filename):
		if filename[0].find(".model") > 0:
			self.saveData({"model": filename[0]})
			data = filename[0]
			data = data.split('\\')
			self.ids.model.text = data[len(data)-1]
		elif filename[0].find(".pickle") > 0:
			self.saveData({"labelbin": filename[0]})
			data = filename[0]
			data = data.split('\\')
			self.ids.labelbin.text = data[len(data)-1]
		else:
			self.saveData({"image": filename[0]})
			self.ids.image.source = filename[0]
		self.dismiss_popup()


class EpicApp(App):
	def build(self):
		server = FlaskThread()
		server.daemon = True
		try:
			server.start()
		except (KeyboardInterrupt, SystemExit):
			sys.exit()

class FlaskThread(Thread):
	def run(self):
		Logger.manager.loggerDict['werkzeug'] = Logger.manager.loggerDict['kivy']
		app.run(host='0.0.0.0')

Factory.register('ConnectPage', cls=ConnectPage)

if __name__ == "__main__":
	Window.size = (1366, 768)
	Window.fullscreen = True
	EpicApp().run()
