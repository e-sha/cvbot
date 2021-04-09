from enum import Enum


class MessageType(Enum):
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    FILE = 'FILE'
    VIDEO = 'VIDEO'


class Data:
    def __init__(self, message_type, message_data):
        self.type = message_type
        self.data = message_data


def TextData(text):
    return Data(MessageType.TEXT, text)


def ImageData(img):
    return Data(MessageType.IMAGE, img)


def VideoData(video):
    return Data(MessageType.VIDEO, video)
