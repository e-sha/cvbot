from threading import Thread, RLock
import time
import cv2
from copy import deepcopy


class CamHolder:
    def __init__(self, camera_id):
        self._camera_id = camera_id
        self._data = None
        self._lock = RLock()
        self._thread = Thread(target=self._start)
        self._thread.start()

    def _start(self):
        cam = cv2.VideoCapture(self._camera_id)
        while True:
            s, img = cam.read()
            if s:
                with self._lock:
                    self._data = img
            time.sleep(1)
        cam.release()

    def get_image(self):
        with self._lock:
            return deepcopy(self._data)
