#!/usr/bin/env python

config = """
steer <Up>    0 -1
steer <Down>  0  1
steer <Left> -1  0
steer <Right> 1  0
default speed 15
speed V 30
speed X /3
speed C *0.2
map Z <LeftMouse>
refreshrate 10
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


def modifier(string):
    """ Parse a string into either a value or an operation. """
    try:
        speed = float(string)
        return speed
    except ValueError:
        operation = string[0]
        multiplier = float(string[1:])
        if operation == '*':
            def operation(speed):
                return speed*multiplier
        elif operation == '/':
            def operation(speed):
                return speed/multiplier
        else:
            raise("Unknown modifier string format: %s" % string)
        return operation


def parseconfig(config):
    conf = {'speed': dict(), 'steer': dict(), 'map': dict()}
    for line in config.strip().splitlines():
        tokens = line.split()
        if tokens[0] == 'steer':
            (key, x, y) = tokens[1:]
            conf['steer'][adaptkeysym(key)] = (int(x), int(y))
        elif tokens[0] == 'speed':
            (key, speedstr) = tokens[1:]
            conf['speed'][adaptkeysym(key)] = modifier(speedstr)
        elif tokens[0] == 'map':
            (fromkey, tokey) = tokens[1:]
            conf['map'][adaptkeysym(fromkey)] = adaptkeysym(tokey)
        elif tokens[0] == 'refreshrate':
            ratemilliseconds = tokens[1]
            conf['refreshrate'] = float(ratemilliseconds)/1000
        elif tokens[0] == 'default' and tokens[1] == 'speed':
            defaultspeed = tokens[2]
            conf['defaultspeed'] = int(defaultspeed)
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
        speed = conf['defaultspeed'] if 'defaultspeed' in conf else 1
        for pressedkey in e.pressedkeys:
            if pressedkey in conf['steer']:
                (ddx, ddy) = conf['steer'][pressedkey]
                (dx, dy) = (dx+ddx, dy+ddy)
            if pressedkey in conf['speed']:
                try:
                    speed = float(conf['speed'][pressedkey])
                except TypeError:
                    f = conf['speed'][pressedkey]
                    speed = f(speed)
        m.move(round(x+speed*dx), round(y+speed*dy))
        sleep(conf['refreshrate'])
