from enum import Enum


class MessageType(Enum):
    TEXT = 0
    IMAGE = 1
    FILE = 2
    VIDEO = 3


class Data:
    def __init__(self, message_type, message_data):
        self._message_type = message_type
        self._message_data = message_data

    def get_type(self):
        return self._message_type


class TextData(Data):
    def __init__(self, text):
        super().__init__(MessageType.TEXT, text)


class ImageData(Data):
    def __init__(self, img):
        super().__init__(MessageType.IMAGE, img)
