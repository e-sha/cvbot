import logging
import re


class Logger():
    def __init__(self, logpath):
        self.log_path = logpath
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.template = re.compile(r'log(\d+).log')
        index = max(self.get_existing_indices() + [-1]) + 1
        self.logfile = self.log_path/f'log{index}.log'

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)-15s %(message)s',
                            filename=self.logfile,
                            level=logging.INFO)

    def _get_existing_info(self):
        files = list(self.log_path.glob(r'log*.log'))
        match = [(x, self.template.match(x.name)) for x in files]
        return {int(x[1].groups()[0][0]): x[0]
                for x in match
                if not x[1] is None}

    def get_existing_files(self):
        info = self._get_existing_info()
        return [info[k] for k in sorted(info.keys())]

    def get_existing_indices(self):
        return list(self._get_existing_info().keys())

    def log_message(self, user, text):
        self.logger.info(f'{user}: {text}')

    def get_stat(self):
        return ''.join([f.read_text()
                        for f in self.get_existing_files()
                        if f != self.logfile])
