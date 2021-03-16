from ..src.logger import BaseLogger


class Logger(BaseLogger):
    def __init__(self, name, processor):
        super().__init__(name)
        self._log_Processor = processor

    def get_stat(self, num_rows=10):
        return self._log_processor(num_rows)
