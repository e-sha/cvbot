import cv2
import io
import numpy as np
from pathlib import Path
import sys

from .src.base_bot import BaseBot
from .src.logger import LogProcessor
from .utils.command import Command
from .utils.logger import Logger
from .utils.message import MessageType, ImageData, TextData, VideoData
from .utils.singleton_processor import SingletonProcessor


class Bot(BaseBot):
    def __init__(self, token, processor, logpath):
        super().__init__(processor, logpath/'bot.log')
        import telebot
        self.bot = telebot.TeleBot(token)
        del token

        @self.bot.message_handler(content_types=['text'])
        def get_text_message(message):
            try:
                input_data = TextData(message.text)
                self._process_message(message.from_user.id,
                                      input_data,
                                      message.chat.username)
            except Exception:
                self._logger.log_traceback(sys.exc_info(),
                                           message.chat.username)

        @self.bot.message_handler(content_types=['video'])
        def get_video_message(message):
            try:
                input_data = VideoData(self._get_message_video(message))
                self._process_message(message.from_user.id,
                                      input_data,
                                      message.chat.username)
            except Exception:
                self._logger.log_traceback(sys.exc_info(),
                                           message.chat.username)

        @self.bot.message_handler(content_types=['photo'])
        def get_image_message(message):
            try:
                input_data = ImageData(self._get_message_photo(message))
                self._process_message(message.from_user.id,
                                      input_data,
                                      message.chat.username)
            except Exception:
                self._logger.log_traceback(sys.exc_info(),
                                           message.chat.username)

        self.bot.polling(none_stop=True, interval=0)

    def _process_message(self, user_id, message, username):
        self._log_message(username, message)
        cmd = self._get_command(message)
        result = cmd(message)
        self._return_data(user_id, result)

    def _get_message_photo(self, message, photo_idx=-1):
        file_id = message.photo[photo_idx].file_id
        file_info = self.bot.get_file(file_id)
        encoded_image = self.bot.download_file(file_info.file_path)
        return cv2.imdecode(np.fromstring(encoded_image, dtype=np.uint8),
                            cv2.IMREAD_UNCHANGED)

    def _get_message_video(self, message):
        file_id = message.video.file_id
        file_info = self.bot.get_file(file_id)
        return self.bot.download_file(file_info.file_path)

    def _return_data(self, user_id, data):
        if data is None:
            return
        if data.type == MessageType.TEXT:
            self.bot.send_message(user_id, data.data)
        elif data.type == MessageType.IMAGE:
            buf = io.BytesIO()
            buf.write(self._encode_image(data.data))
            buf.seek(0)
            self.bot.send_photo(user_id, buf)
            del buf
        elif data.type == MessageType.VIDEO:
            video = data.data
            if isinstance(video, (str, Path)):
                with open(video, 'rb') as buf:
                    self.bot.send_video(user_id, buf)
            else:
                assert isinstance(video, io.BytesIO)
                video.seek(0)
                if len(video.getvalue()) == 0:
                    self.bot.send_message(user_id, "Empty video response")
                else:
                    self.bot.send_video(user_id, video)
        else:
            assert False, f'unsupported data type {data.type}'
