import multiprocessing as mp
import socket
import sys

from .message_passing import send, recv
from .process_with_exception import Process, SubprocessException
from ..src.logger import BaseLogger


def Processing(constructor, port, controll_queue, args, kwargs):
    logger = BaseLogger('SingletonProcessor')
    try:
        processor = constructor(*args, **kwargs)
    except Exception:
        logger.log_traceback(sys.exc_info())
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
        logger.log_traceback(sys.exc_info())
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
        self._processor = Process(target=Processing,
                                  args=(processor_constructor,
                                        self._port,
                                        controll_queue,
                                        args,
                                        kwargs))
        self._processor.start()
        status = controll_queue.get()
        assert status == 'ready'
        controll_queue.close()

    def terminate(self):
        self._processor.terminate()
        self._processor.join()

    @staticmethod
    def _is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def _check(self):
        if not self._processor.is_alive():
            if self._processor.exception() is not None:
                raise self._processor.exception
            raise Exception("The processor finished")

    def __call__(self, *args, **kwargs):
        logger = BaseLogger('SingletonProcessor')
        s = None
        result = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._check()
            s.connect(('0.0.0.0', self._port))
            self._check()
            send(s, args)
            self._check()
            send(s, kwargs)
            self._check()
            result = recv(s)
            self._check()
        except SubprocessException as e:
            logger.logger.error(str(e))
            logger.logger.error(''.join(e.traceback))
        except Exception as e:
            logger.logger.error(str(e))
            logger.log_traceback(sys.exc_info())
        finally:
            if s is not None:
                s.close()
        return result
