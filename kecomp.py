#!/usr/bin/env python

config = """
steer <Up>    0 -1
steer <Down>  0  1
steer <Left> -1  0
steer <Right> 1  0
speed X 1
speed C 5
map Z <LeftMouse>
"""

from pprint import pprint
from pykeyboard import PyKeyboardEvent
from enum import Enum


class KeyListener(PyKeyboardEvent):
    Action = Enum('Action', 'press release init')

    def __init__(self):
        PyKeyboardEvent.__init__(self)
        self.callno = 0
        self.action = self.Action.init
        self.key = None

    def handler(self, reply):
        self.callno = self.callno + 1
        r = reply._data['data']
        if not r:
            return
        actioncode = r[0]
        if actioncode == 2:
            self.action = self.Action.press
        elif actioncode == 3:
            self.action = self.Action.release
        else:
            raise("Unknown action code: %d" % actioncode)
        continuouscode = r[2]
        if continuouscode not in {0, 1}:
            raise("Unknown continuous code: %d" % continuouscode)
        keycode = r[1]
        self.key = self.lookup_char_from_keycode(keycode)


def parseconfig(config):
    conf = {'speed': dict(), 'steer': dict(), 'map': dict()}
    for line in config.strip().splitlines():
        tokens = line.split()
        if tokens[0] == 'steer':
            (key, x, y) = tokens[1:]
            conf['steer'][key] = (int(x), int(y))
        elif tokens[0] == 'speed':
            (key, speed) = tokens[1:]
            conf['speed'][key] = int(speed)
        elif tokens[0] == 'map':
            (fromkey, tokey) = tokens[1:]
            conf['map'][fromkey] = tokey
    return conf

if __name__ == '__main__':
    conf = parseconfig(config)

    print("Configuration:")
    pprint(conf)

    e = KeyListener()
    e.run()
