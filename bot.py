import cv2
import io
import numpy as np
from pathlib import Path
import telebot
import traceback
import sys

from .src.logger import LogProcessor
from .utils.command import Command
from .utils.logger import Logger
from .utils.message import MessageType, ImageData, TextData, VideoData
from .utils.singleton_processor import SingletonProcessor


class Bot:
    def __init__(self, token, processor, logpath):
        self._log_processor = SingletonProcessor(LogProcessor,
                                                 logpath/'bot.log',
                                                 5, 1000000)
        self._logger = Logger('bot', self._log_processor)
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

        @self.bot.message_handler(content_types=['video'])
        def get_video_message(message):
            self._logger.log_message(message.chat.username, message.text)
            cmd = self._CMD.get(MessageType.VIDEO, self._process_unknown)
            input_data = TextData(message.text)
            try:
                result = cmd(input_data)
                self._return_data(message.from_user.id, result)
            except Exception:
                exc_info = sys.exc_info()
                exc = traceback.format_exception(*exc_info)
                self._logger.log_message(message.chat.username, ''.join(exc))

        @self.bot.message_handler(content_types=['photo'])
        def get_image_message(message):
            self._logger.log_message(message.chat.username, message.photo)
            cmd = self._CMD.get(MessageType.IMAGE, self._process_unknown)
            input_data = ImageData(self._get_message_photo(message))
            try:
                result = cmd(input_data)
                self._return_data(message.from_user.id, result)
            except Exception:
                exc_info = sys.exc_info()
                exc = traceback.format_exception(*exc_info)
                self._logger.log_message(message.chat.username, ''.join(exc))

        self.bot.polling(none_stop=True, interval=0)

    def _get_message_photo(self, message, photo_idx=-1):
        file_id = message.photo[photo_idx].file_id
        file_info = self.bot.get_file(file_id)
        encoded_image = self.bot.download_file(file_info.file_path)
        return cv2.imdecode(np.fromstring(encoded_image, dtype=np.uint8),
                            cv2.IMREAD_UNCHANGED)

    def _construct_default_commands(self):
        self._CMD = {MessageType.TEXT: {}}
        self._CMD[MessageType.TEXT]['/stat'] = Command(
                'Prints usage statistics', self._get_stat)
        self._CMD[MessageType.TEXT]['/help'] = Command(
                'Prints help message', self._print_help)

    def _join_commands(self, processor):
        processor_cmds = processor.get_commands()
        for cmd_type, cmds in processor_cmds.items():
            if isinstance(cmds, Command):
                assert cmd_type not in self._CMD
                self._CMD[cmd_type] = cmds
            elif isinstance(cmds, dict):
                # check duplicate
                if cmd_type not in self._CMD:
                    self._CMD[cmd_type] = {}
                common_cmds = set(self._CMD[cmd_type].keys()) \
                              .intersection(set(cmds.keys()))
                assert len(common_cmds) == 0, "Processor shouldn't contain " \
                                              f"commands {common_cmds} of " \
                                              f"type {cmd_type}"
                # merge commands
                self._CMD[cmd_type].update(cmds)
            else:
                assert False

    def _print_help(self, message):
        commands = []
        for name, command in self._CMD[MessageType.TEXT].items():
            commands.append(f'[TEXT] {name}: {command}')
        if MessageType.IMAGE in self._CMD:
            commands.append(f'[IMAGE]: {self._CMD[MessageType.IMAGE]}')
        if MessageType.VIDEO in self._CMD:
            commands.append(f'[VIDEO]: {self._CMD[MessageType.VIDEO]}')
        return TextData('\n'.join(commands))

    def _get_stat(self, message):
        try:
            stat = self._logger.get_stat()
            stat = '\n'.join(stat.split('\n')[-10:])
        except:
            exc_info = sys.exc_info()
            exc = traceback.format_exception(*exc_info)
            self._logger.log_message(message.chat.username, ''.join(exc))
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
        elif isinstance(data, VideoData):
            if isinstance(data._message_data, (str, Path)):
                with open(data._message_data, 'rb') as buf:
                    self.bot.send_video(user_id, buf)
            else:
                assert isinstance(data._message_data, io.BytesIO)
                self.bot.send_video(user_id, data._message_data)
        else:
            assert False, f'unsupported data type {type(data)}'
