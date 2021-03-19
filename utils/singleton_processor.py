import multiprocessing as mp
import socket
import numpy as np
import pickle
import sys
import traceback

from pathlib import Path

from .message_passing import send, recv
from ..src.logger import BaseLogger


def Processing(constructor, port, controll_queue, args, kwargs):
    logger = BaseLogger('SingletonProcessor')
    try:
        processor = constructor(*args, **kwargs)
    except Exception:
        exc_info = sys.exc_info()
        exc = traceback.format_exception(*exc_info)
        logger.logger.error(''.join(exc))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    controll_queue.put('ready')

    conn = None
    try:
        while True:
            conn, address = s.accept()
            args = recv(conn)
            if args is None:
                conn.close()
                continue
            assert isinstance(args, tuple)
            kwargs = recv(conn)
            assert isinstance(kwargs, dict)
            result = processor(*args, **kwargs)
            send(conn, result)
            conn.close()
    except Exception:
        exc_info = sys.exc_info()
        exc = traceback.format_exception(*exc_info)
        logger.logger.error(''.join(exc))
        raise
    finally:
        if conn is not None:
            conn.close()


class SingletonProcessor:
    def __init__(self, processor_constructor, *args, **kwargs):
        self._port = 9000
        while self._is_port_in_use(self._port):
            self._port += 1
        controll_queue = mp.Queue()
        self._processor = mp.Process(target=Processing,
                                     args=(processor_constructor,
                                           self._port,
                                           controll_queue,
                                           args,
                                           kwargs))
        self._processor.start()
        status = controll_queue.get()
        assert status == 'ready'
        controll_queue.close()

    @staticmethod
    def _is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def __call__(self, *args, **kwargs):
        logger = BaseLogger('SingletonProcessor')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('0.0.0.0', self._port))
        send(s, args)
        send(s, kwargs)
        result = recv(s)
        s.close()
        return result
