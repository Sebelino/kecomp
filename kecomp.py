#!/usr/bin/env python

config = """
steer <Up>    0 -1
steer <Down>  0  1
steer <Left> -1  0
steer <Right> 1  0
speed X 2
speed C 5
map Z <LeftMouse>
"""

from pprint import pprint
from pykeyboard import PyKeyboardEvent
from pymouse import PyMouse
from enum import Enum
from threading import Thread
from time import sleep


def adaptkeysym(keysym):
    """ Translate Vim key sym notation into PyUserInput notation. """
    keys = {
        "<Up>": "Up",
        "<Right>": "Right",
        "<Down>": "Down",
        "<Left>": "Left",
    }
    if keysym in keys:
        return keys[keysym]

    def lettermap(c):
        return c.lower()
    return lettermap(keysym)


def parseconfig(config):
    conf = {'speed': dict(), 'steer': dict(), 'map': dict()}
    for line in config.strip().splitlines():
        tokens = line.split()
        if tokens[0] == 'steer':
            (key, x, y) = tokens[1:]
            conf['steer'][adaptkeysym(key)] = (int(x), int(y))
        elif tokens[0] == 'speed':
            (key, speed) = tokens[1:]
            conf['speed'][adaptkeysym(key)] = float(speed)
        elif tokens[0] == 'map':
            (fromkey, tokey) = tokens[1:]
            conf['map'][adaptkeysym(fromkey)] = adaptkeysym(tokey)
    return conf

Action = Enum('Action', 'press release init')


class KeyListener(PyKeyboardEvent):
    def __init__(self):
        PyKeyboardEvent.__init__(self)
        self.callno = 0
        self.pressedkeys = set()

    def handler(self, reply):
        self.callno = self.callno + 1
        r = reply._data['data']
        if not r:
            return
        continuouscode = r[2]
        if continuouscode == 1:
            continuous = True
        elif continuouscode == 0:
            continuous = False
        else:
            raise("Unknown continuous code: %d" % continuouscode)
        if continuous:
            return  # We are not concerned with these kinds of events
        actioncode = r[0]
        if actioncode == 2:
            action = Action.press
        elif actioncode == 3:
            action = Action.release
        else:
            raise("Unknown action code: %d" % actioncode)
        keycode = r[1]
        key = self.lookup_char_from_keycode(keycode)
        if key not in self.pressedkeys and action == Action.press:
            self.pressedkeys.add(key)
        elif key in self.pressedkeys and action == Action.release:
            self.pressedkeys.remove(key)

if __name__ == '__main__':
    conf = parseconfig(config)

    print("Configuration:")
    pprint(conf)

    e = KeyListener()
    t = Thread(target=e.run)
    t.start()

    m = PyMouse()

    while True:
        (x, y) = m.position()
        (dx, dy) = (0, 0)
        speed = 1
        for pressedkey in e.pressedkeys:
            if pressedkey in conf['steer']:
                (ddx, ddy) = conf['steer'][pressedkey]
                (dx, dy) = (dx+ddx, dy+ddy)
            if pressedkey in conf['speed']:
                speed = speed*conf['speed'][pressedkey]
        m.move(round(x+speed*dx), round(y+speed*dy))
        sleep(0.01)
