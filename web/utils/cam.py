import cv2
import time
from threading import Thread

class ThreadedCamera(object):    
  def __init__(self, src=0):
    self.capture = cv2.VideoCapture(src)
    self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    
    self.FPS = 1/30
    self.FPS_MS = int(self.FPS * 1000)

    self.thread = Thread(target=self.update, args=())
    self.thread.daemon = True
    self.thread.start()

  def update(self):
    while True:
      if self.capture.isOpened():
        (self.status, self.frame) = self.capture.read()
      time.sleep(self.FPS)

  def get(self):
    return self.FPS_MS, self.frame