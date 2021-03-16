import numpy as np
import pickle


_size_type = np.uint64


def send(conn, data):
    pickled = pickle.dumps(data)
    length = _size_type(len(pickled))
    conn.sendall(length.tobytes())
    conn.sendall(pickled)


def recv(conn, block_size=4096):
    size_length = _size_type().nbytes

    length = conn.recv(size_length)
    if len(length) == 0:
        return None
    assert len(length) == size_length, f'Waiting {size_length} bytes, ' \
                                       f'but only {len(length)} bytes ' \
                                       f'are received'
    length = np.frombuffer(length, dtype=_size_type)
    length = int(length)

    data = b""
    for i in range(0, int(length), block_size):
        cur_block_size = min(block_size, length - i)
        data += conn.recv(cur_block_size)

    return pickle.loads(data)
