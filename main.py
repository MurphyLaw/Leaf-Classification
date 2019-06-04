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
# from pyimagesearch.classify import ClassifyImage
import argparse
from flask import Flask, jsonify, render_template, Response
from threading import Thread
from logging import Logger
import cv2
import time
from camera_opencv import Camera

from mjpegviewer import MjpegViewer

kivy.require("1.10.1")
app = Flask(__name__)

scanning = False
source = ""

leafs = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}



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
		source = leafs.get(leaf_id, "Not in Model")
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
	source = ""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.add_widget(self.start_camera())

	def start_camera(self):
		viewer = MjpegViewer(
		    url=
		    "http://localhost:5000/video_feed")
		viewer.start()
		return viewer

	def findImage_button(self):
		self.show_load("Image")

	def labelBin_button(self):
		self.show_load("LabelBin")

	def model_button(self):
		self.show_load("Model")

	def saveData(self, information):
		self.data.update(information)

	def classify_button(self):
		self.ids.labelclassification.text = "Scanning..."
		def got_json(req, result):
			self.ids.labelclassification.text = result
		UrlRequest('http://localhost:5000/setting', got_json)

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
		self.ids.labelclassification.text = ""

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
	EpicApp().run()