from threading import Thread, RLock, Event
import time
import cv2
from copy import deepcopy


class CamHolder:
    def __init__(self, camera_id):
        self._camera_id = camera_id
        self._data = None
        self._lock = RLock()
        self._kill_event = Event()
        self._thread = Thread(target=self._start)
        self._thread.start()

    def _start(self):
        cam = cv2.VideoCapture(self._camera_id)
        while True:
            if self._kill_event.is_set():
                break
            s, img = cam.read()
            if s:
                with self._lock:
                    self._data = img
            time.sleep(1)
        cam.release()

    def get_image(self):
        with self._lock:
            return deepcopy(self._data)

    def terminate(self):
        self._kill_event.set()
        self._thread.join()
