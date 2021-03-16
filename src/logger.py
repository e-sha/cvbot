import io
import logging
import logging.handlers
import multiprocessing as mp
from pathlib import Path
import sys


_log_format = '%(asctime)-15s %(message)s'
_logger_lock = mp.Lock()
_logger_lock.acquire()
try:
    if not 'log_queue' in globals():
        log_queue = mp.Queue(-1)
finally:
    _logger_lock.release()


class BaseLogger:
    def __init__(self, name):
        global log_queue
        queue_handler = logging.handlers.QueueHandler(log_queue)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(queue_handler)

    def log_message(self, user, text):
        self.logger.info(f'{user}: {text}')


class LogProcessor:
    def __init__(self,
                 logfile,
                 backupCount,
                 maxBytes):
        self.logfile = logfile
        self.logfile.parent.mkdir(exist_ok=True, parents=True)
        self.previous_logs = self._read_previous_logs()
        self.stream = io.StringIO()

        file_handler = self._get_file_hanlder(maxBytes, backupCount)
        stream_handler = self._get_stream_handler(self.stream)
        stderr_handler = self._get_stream_handler(sys.stderr)
        global log_queue
        self.listener = logging.handlers.QueueListener(log_queue,
                                                       stream_handler,
                                                       file_handler)
        self.listener.start()

    def __call__(self, rows):
        self.listener.stop()
        new_logs = self.stream.getvalue()
        self.listener.start()
        all_logs = '\n'.join([previous_logs, new_logs])
        return '\n'.join(all_logs.split('\n')[-rows:])

    def _read_previous_logs(self):
        existing_logfiles = [self.logfile] if self.logfile.is_file() else []
        i = 1
        while True:
            filename = Path(f'{self.logfile}.{i}')
            if filename.is_file():
                existing_logfiles = [filename] + existing_logfiles
                i += 1
            else:
                break
        return '\n'.join([x.read_text() for x in existing_logfiles])

    def _get_file_hanlder(self, maxBytes, backupCount):
        file_handler = logging.handlers.RotatingFileHandler(self.logfile,
                                                            maxBytes=maxBytes,
                                                            backupCount=backupCount)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(_log_format))
        return file_handler

    def _get_stream_handler(self, stream):
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(logging.Formatter(_log_format))
        stream_handler.setLevel(logging.INFO)
        return stream_handler
