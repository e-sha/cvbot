from __future__ import print_function
import multiprocessing as mp
import traceback


class SubprocessException(Exception):
    def __init__(self, exception, traceback):
        super().__init__()
        self.exception = exception
        self.traceback = traceback


class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
            if isinstance(self._exception, tuple):
                self._exception = SubprocessException(*self._exception)
        return self._exception
