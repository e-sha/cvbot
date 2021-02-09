import cv2
import io
import telebot
import traceback
import sys

from .utils.command import Command
from .utils.logger import Logger
from .utils.message import MessageType, ImageData, TextData


class Bot:
    def __init__(self, token, processor, logpath):
        self._logger = Logger(logpath)
        self._construct_default_commands()
        self._join_commands(processor)
        self.bot = telebot.TeleBot(token)
        del token

        @self.bot.message_handler(content_types=['text'])
        def get_text_message(message):
            self._logger.log_message(message.chat.username, message.text)
            cmd = self._CMD[MessageType.TEXT].get(message.text,
                                                  self._process_unknown)
            input_data = TextData(message.text)
            try:
                result = cmd(input_data)
                self._return_data(message.from_user.id, result)
            except Exception:
                exc_info = sys.exc_info()
                exc = traceback.format_exception(*exc_info)
                self._logger.log_message(message.chat.username, ''.join(exc))

        self.bot.polling(none_stop=True, interval=0)

    def _construct_default_commands(self):
        self._CMD = {t: {} for t in MessageType}
        self._CMD[MessageType.TEXT]['/stat'] = Command(
                'Prints usage statistics', self._get_stat)
        self._CMD[MessageType.TEXT]['/help'] = Command(
                'Prints help message', self._print_help)

    def _join_commands(self, processor):
        processor_cmds = processor.get_commands()
        for cmd_type, cmds in processor_cmds.items():
            # check duplicate
            common_cmds = set(self._CMD[cmd_type].keys()) \
                          .intersection(set(cmds.keys()))
            assert len(common_cmds) == 0, "Processor shouldn't contain " \
                                          f"commands {common_cmds} of " \
                                          f"type {cmd_type}"
            # merge commands
            self._CMD[cmd_type].update(cmds)

    def _print_help(self, message):
        commands = []
        for name, command in self._CMD[MessageType.TEXT].items():
            commands.append(f'{name}: {command}')
        return TextData('\n'.join(commands))

    def _get_stat(self, message):
        stat = self._logger.get_stat()
        stat = '\n'.join(stat.split('\n')[-10:])
        return TextData(stat)

    def _process_unknown(self, message):
        return TextData('Unknow command.\n/help to get availabe commands')

    def _return_data(self, user_id, data):
        if data is None:
            return
        if isinstance(data, TextData):
            self.bot.send_message(user_id, data._message_data)
        elif isinstance(data, ImageData):
            buf = io.BytesIO()
            buf.write(bytes(cv2.imencode('.jpg', data._message_data)[1]))
            buf.seek(0)
            self.bot.send_photo(user_id, buf)
            del buf
        else:
            assert False, f'unsupported data type {type(data)}'
