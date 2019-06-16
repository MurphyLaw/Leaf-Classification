
import io
# for windows
import urllib.request
# for Ubuntu
# from urllib2 import urlopen
import threading
from kivy.uix.image import Image
from kivy.app import App
from kivy.properties import StringProperty
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from collections import deque
import time

class MjpegViewer(Image):

    url = "http://localhost:5000/video_feed"

    def start(self):
        time.sleep(2)
        self.quit = False
        self._queue = deque()
        self._thread = threading.Thread(target=self.read_stream)
        self._thread.daemon = True
        self._thread.start()
        self._image_lock = threading.Lock()
        self._image_buffer = None
        Clock.schedule_interval(self.update_image, 1 / 30.)

    def stop(self):
        self.quit = True
        self._thread.join()
        Clock.unschedule(self.read_queue)

    def read_stream(self):
# for Windows
        stream = urllib.request.urlopen(self.url)
	# for Ubuntu
	# stream = urlopen(self.url)
        bytes = b''
        while not self.quit:
            bytes += stream.read(1024)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                bytes = bytes[b + 2:]

                data = io.BytesIO(jpg)
                im = CoreImage(data,
                               ext="jpeg",
                               nocache=True)
                with self._image_lock:
                    self._image_buffer = im

    def update_image(self, *args):
        im = None
        with self._image_lock:
            im = self._image_buffer
            self._image_buffer = None
        if im is not None:
            self.texture = im.texture
            self.texture_size = im.texture.size
