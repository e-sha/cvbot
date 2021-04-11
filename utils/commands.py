from argparse import ArgumentParser
import base64
import json
from pathlib import Path
import sys

from ..utils.message import MessageType, Data


def read_commands(path):
    if not path.is_file():
        return []
    commands = path.read_text().strip()
    if commands == '':
        return []
    return list(map(json.loads, commands.split('\n')))


def encode_file_data(path):
    return {'path': str(path.resolve()),
            'data': base64.b64encode(path.read_bytes()).decode('utf-8')}


def decode_file_data(data):
    return {'path': data['path'],
            'data': base64.b64decode(data['data'].encode('utf-8'))}


def command2message(command):
    idx = command['idx']
    cmd = command['command']
    t = MessageType(cmd['type'])
    if t == MessageType.TEXT:
        data = cmd['data']
    else:
        data = decode_file_data(cmd['data'])['data']
    return idx, Data(t, data)
