from argparse import ArgumentParser
import json
from pathlib import Path


from .scripts.manager import read_commands, encode_file_data
from .utils.message import MessageType, Data


def check_commandfile_exists(args):
    assert args.input.is_file(), f'File {args.input} does not exist'


def parse_args():
    parser = ArgumentParser(description='Manage commands for debugging')
    parser.add_argument('-i', '--input', help='File with commands', required=True, type=Path)
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser_list = subparsers.add_parser('list', help='list stored commands')

    parser_add = subparsers.add_parser('add', help='add new command')
    parser_add.add_argument('-p', '--position', help='Position of the command', type=int, default=-1)
    parser_add.add_argument('-t', '--type', help='Type of the command', type=MessageType)
    parser_add.add_argument('--text', help='Text of the command', type=str, default=None)
    parser_add.add_argument('--file', help='File of the command', type=Path, default=None)
    parser_add.add_argument('--image', help='Image of the command', type=Path, default=None)
    parser_add.add_argument('--video', help='Video of the command', type=Path, default=None)

    parser_delete = subparsers.add_parser('delete', help='delete command')
    parser_delete.add_argument('-p', '--position', help='Position of the command', type=int, default=-1)
    return parser.parse_args()


def do_list(args):
    check_commandfile_exists(args)
    commands = read_commands(args.input)
    if len(commands) == 0:
        print('No commands fount')
    else:
        for c in commands:
            if isinstance(c['command']['data'], dict):
                c['command']['data'] = c['command']['data']['path']
        print('\n'.join(map(json.dumps, commands)))


def do_add(args):
    commands = read_commands(args.input)
    n = len(commands)
    assert args.position >= -(n+1) and args.position <= n, f'Bad position value {args.position}'
    args.position = args.position if args.position >= 0 else args.position + n + 1
    command = {'idx': args.position, 'command': {'type': args.type.name,
                                                 'data': None}}
    if args.type == MessageType.TEXT:
        assert args.text is not None, "You should specify text for a text message"
        assert args.image is None, "Image data for a text message is not supported"
        assert args.video is None, "Video data for a text message is not supported"
        assert args.file is None, "File data for a text message is not supported"
        command['command']['data'] = args.text
    elif args.type == MessageType.IMAGE:
        assert args.text is None, "Text data for an image message is not supported"
        assert args.image is not None, "You should specify an image for an image message"
        assert args.video is None, "Video data for an image message is not supported"
        assert args.file is None, "File data for an image message is not supported"
        command['command']['data'] = encode_file_data(args.image)
    elif args.type == MessageType.VIDEO:
        assert args.text is None, "Text data for a video message is not supported"
        assert args.image is None, "Image data for a video message is not supported"
        assert args.video is not None, "You should specify a video for a video message"
        assert args.file is None, "File data for a video message is not supported"
        command['command']['data'] = encode_file_data(args.video)
    elif args.type == MessageType.FILE:
        assert args.text is None, "Text data for a file message is not supported"
        assert args.image is None, "Image data for a file message is not supported"
        assert args.video is None, "Video data for a file message is not supported"
        assert args.file is not None, "You should specify a file for a file message"
        command['command']['data'] = encode_file_data(args.file)
    for c in commands[args.position:]:
        c['idx'] += 1
    commands = commands[:args.position] + [command] + commands[args.position:]
    commands = map(json.dumps, commands)
    args.input.write_text('\n'.join(commands))


def do_delete(args):
    check_commandfile_exists(args)
    commands = read_commands(args.input)
    n = len(commands)
    assert args.position >= -n and args.position < n, f'Bad position value {args.position}'
    args.position = args.position if args.position >= 0 else args.position + n
    commands = commands[:args.position] + commands[args.position+1:]
    for c in commands[args.position:]:
        c['idx'] -= 1
    commands = map(json.dumps, commands)
    args.input.write_text('\n'.join(commands))


def main(args):
    if args.command == 'list':
        do_list(args)
    elif args.command == 'add':
        do_add(args)
    elif args.command == 'delete':
        do_delete(args)


args = parse_args()
main(args)
