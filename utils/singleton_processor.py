import multiprocessing as mp
import socket
import numpy as np
import pickle


def send(conn, data, size_type):
    pickled = pickle.dumps(data)
    length = size_type(len(pickled))
    conn.sendall(length.tobytes())
    conn.sendall(pickled)


def recv(conn, size_type, block_size=4096):
    size_length = size_type().nbytes

    length = conn.recv(size_length)
    assert len(length) == size_length
    length = np.frombuffer(length, dtype=size_type)
    length = int(length)

    data = b""
    for i in range(0, int(length), block_size):
        cur_block_size = min(block_size, length - i)
        data += conn.recv(cur_block_size)

    return pickle.loads(data)


def Processing(constructor, port, size_type, controll_queue, args, kwargs):
    processor = constructor(*args, **kwargs)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    controll_queue.put('ready')

    conn = None
    try:
        while True:
            conn, address = s.accept()
            args = recv(conn, size_type)
            assert isinstance(args, tuple)
            kwargs = recv(conn, size_type)
            assert isinstance(kwargs, dict)
            result = processor(*args, **kwargs)
            send(conn, result, size_type)
            conn.close()
    finally:
        if conn is not None:
            conn.close()


class SingletonProcessor:
    def __init__(self, processor_constructor, *args, **kwargs):
        self._port = 9000
        self._size_type = np.uint64
        self._controll_queue = mp.Queue()
        self._processor = mp.Process(target=Processing,
                                     args=(processor_constructor,
                                           self._port,
                                           self._size_type,
                                           self._controll_queue,
                                           args,
                                           kwargs))
        self._processor.start()
        status = self._controll_queue.get()
        assert status == 'ready'

    def __call__(self, *args, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('0.0.0.0', self._port))
        send(s, args, self._size_type)
        send(s, kwargs, self._size_type)
        result = recv(s, self._size_type)
        s.close()
        return result
