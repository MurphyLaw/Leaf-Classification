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
from pyimagesearch.classify import ClassifyImage
import argparse

kivy.require("1.10.1")

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

	def findImage_button(self):
		self.show_load("Image")

	def labelBin_button(self):
		self.show_load("LabelBin")

	def model_button(self):
		self.show_load("Model")

	def saveData(self, information):
		self.data.update(information)

	def classify_button(self):
		label = ClassifyImage(self.data)
		self.ids.labelclassification.text = label
		print("[INFO] {}".format(label))

	def dismiss_popup(self):
		self._popup.dismiss()

	def show_load(self, title):
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title=title, content=content,
		                    size_hint=(0.9, 0.9))
		self._popup.open()

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
	pass

Factory.register('ConnectPage', cls=ConnectPage)

if __name__ == "__main__":
	EpicApp().run()