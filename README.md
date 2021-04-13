# Compute Vision Bot (CVBot)

An interface for creating a telegram bot with computer vision.

# Features
1. Provides an interface for sending and receiving data of different types (Text, Image, Video and File).
2. Provides a logger of the input requests.
3. Provides standard commands like `/help` and `/stat`.
4. Provides an interface for receiving images from a webcam with multiple threads.
5. Provides an interface for making Singleton processor that handles requests on a GPU.
6. Allows local testing without telegram usage

# Usage

In order to run the bot create a Bot object with your processor.
```
from cvbot import
Bot(token, processor, logpath)
```

## Processor

Processor is an object with the following structure:
```
class Processor:
    def terminate(self):
        ...

    def get_commands(self):
        commands = ...
        return commands
```
`terminate` is used as a destructor.
`commands` is a dictionary that maps `MessageType` to a command:
```
commands = {MessageType.TEXT: {'/hello': Command(description='Help for "/hello" command',
                                                 processor=lambda x: TextData('You wrote "/hello"')),
                               '/world': Command(description='Help for /world command',
                                                 processor=lambda x: TextData('You wrote "/world"')},
            MessageType.IMAGE: Command(description='echo image',
                                       processor=lambda x: x),
            MessageType.VIDEO: Command(description='echo video',
                                       processor=lambda x: x),
            MessageType.FILE: Command(description='echo file',
                                      processor=lambda x: x)}
```
Each [command](https://github.com/e-sha/cvbot/blob/master/utils/command.py) has a description that is used in `/help` command and a message processor (callable) that process data of that type.

The bot supports 4 types of [messages](https://github.com/e-sha/cvbot/blob/master/utils/message.py): TEXT, IMAGE, VIDEO and FILE.

TEXT messages can have different processors for different texts.

IMAGE message contains image as a `numpy.ndarray`.

VIDEO and FILE messages contain a `io.BytesIO` of the file.

## Debugging

To debug your bot you can try [TestBot](https://github.com/e-sha/cvbot/blob/master/test_bot.py) instead of [Bot](https://github.com/e-sha/cvbot/blob/master/bot.py).
In this mode the bot receives commands from a file and writes results to the output directory.

Use `cvbot.command_manager` to create commands for debugging:
```Python
# display commands in commands.txt file
python -m cvbot.command_manager -i data/commands.txt list
# add "/help" as a text command 
python -m cvbot.command_manager -i data/commands.txt add -t TEXT --text "/help"
# add image.jpg as an image command
python -m cvbot.command_manager -i data/commands.txt add -t IMAGE --image image.jpg
# add video.mkv as a video comand
python -m cvbot.command_manager -i data/commands.txt add -t VIDEO --video video.mkv
```

# Example
1. [CamBot](https://github.com/e-sha/cambot) shows an image from a webcam with the detected objects.
