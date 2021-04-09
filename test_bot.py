import sys

from .scripts.manager import read_commands, command2message
from .utils.message import MessageType
from .base_bot import BaseBot


class TestBot(BaseBot):
    def __init__(self, commands_path, processor, logpath, output_path):
        super().__init__(processor, logpath/'test_bot.log')
        self._output_path = output_path
        self._output_path.mkdir(exist_ok=True, parents=True)
        for command in read_commands(commands_path):
            try:
                idx, message = command2message(command)
                cmd = self._get_command(message)

                self._log_message('test_user', message)
                cmd = self._get_command(message)
                result = cmd(message)
                self._return_data('test_user', result, idx)
            except Exception:
                self._logger.log_traceback(sys.exc_info(),
                                           'test_user')
                raise

    def _return_data(self, user, data, idx):
        name = str(idx)
        if data.type == MessageType.TEXT:
            (self._output_path/f'{name}.txt').write_text(data.data)
        elif data.type == MessageType.IMAGE:
            (self._output_path/f'{name}.jpg').write_bytes(self._encode_image(data.data))
        elif data.type == MessageType.VIDEO:
            (self._output_path/f'{name}.mkv').write_bytes(data.data.getvalue())
        elif data.type == MessageType.FILE:
            (self._output_path/name).write_bytes(data.data.getvalue())
        else:
            raise Exception('Unknown message type {data.type}')
