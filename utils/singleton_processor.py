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
    name = str(constructor).split('.')[-1].split("'")[0]
    logger = BaseLogger('SingletonProcessor')
    try:
        processor = constructor(*args, **kwargs)
    except Exception:
        exc_info = sys.exc_info()
        exc = traceback.format_exception(*exc_info)
        logger.logger.error(''.join(exc))
    logger.logger.error(f'{name}_{port}')
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
        logger.logger.error(f'{name}\n' + ''.join(exc))
        raise
    finally:
        if conn is not None:
            conn.close()


class SingletonProcessor:
    def __init__(self, processor_constructor, *args, **kwargs):
        self.p_name = str(processor_constructor).split('.')[-1].split("'")[0]
        print(self.p_name)
        Path(f'/logs/{self.p_name}_0').write_text('123')
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
        Path(f'/logs/{self.p_name}_1').write_text('123')

    @staticmethod
    def _is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def __call__(self, *args, **kwargs):
        Path(f'/logs/{self.p_name}_2').write_text('123')
        logger = BaseLogger('SingletonProcessor')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('0.0.0.0', self._port))
        send(s, args)
        send(s, kwargs)
        result = recv(s)
        s.close()
        Path(f'/logs/{self.p_name}_3').write_text('123')
        return result
