import cv2
import sys

from .src.logger import LogProcessor
from .utils.command import Command
from .utils.logger import Logger
from .utils.message import MessageType, ImageData, TextData, VideoData
from .utils.singleton_processor import SingletonProcessor


class BaseBot:
    def __init__(self, processor, logpath):
        self._log_processor = SingletonProcessor(LogProcessor,
                                                 logpath,
                                                 5, 1000000)
        self._logger = Logger('bot', self._log_processor)
        self._construct_commands(processor)

    def _process_unknown(self, message):
        return TextData('Unknow command.\n/help to get availabe commands')

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
        except Exception:
            self._logger.log_traceback(sys.exc_info(), message.chat.username)
        return TextData(stat)

    def _log_message(self, user, message):
        text = None
        if message.type == MessageType.TEXT:
            text = f'[TEXT] {message.data}'
        elif message.type == MessageType.IMAGE:
            text = '[IMAGE]'
        elif message.type == MessageType.VIDEO:
            text = '[VIDEO]'
        elif message.type == MessageType.FILE:
            text = '[FILE]'
        else:
            raise Exception('Unknown message type {messate.type}')
        self._logger.log_message(user, text)

    def _get_command(self, message):
        cmd = self._CMD[message.type]
        if message.type == MessageType.TEXT:
            return cmd.get(message.data, self._process_unknown)
        return cmd

    def _construct_commands(self, processor):
        self._construct_default_commands()
        self._join_commands(processor)

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

    def _encode_image(self, image):
        is_ok, enc_image = cv2.imencode('.jpg', image)
        assert is_ok
        return bytes(enc_image)
