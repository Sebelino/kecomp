#!/usr/bin/env python

from pykeyboard import PyKeyboardEvent
from pymouse import PyMouse
from enum import Enum
from threading import Thread
from time import sleep
import os
import argparse


def readconfig(path):
    with open(path, 'r') as f:
        contents = f.read()
        return contents


def defaultconfig():
    """
    If there is a kecomp.conf in the user's working directory, use it.
    Else, if there is a kecomp.conf in the same directory as this file, use it.
    Else, use the fallback configuration defined below.
    """
    fallback = """
    steer <Up>    0 -1
    steer <Down>  0  1
    steer <Left> -1  0
    steer <Right> 1  0
    default speed 15
    speed B 30
    speed C /3
    speed V *0.2
    map Z <LeftMouse>
    map X <RightMouse>
    refreshrate 10
    """
    filename = "kecomp.conf"
    path = os.path.realpath(os.path.join(os.getcwd(), filename))
    if not os.path.exists(path):
        path = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.dirname(__file__),
                                             filename))
        if not os.path.exists(path):
            return fallback
    contents = readconfig(path)
    return contents


def adaptsym(sym):
    """ Translate Vim sym notation into PyUserInput notation. """
    syms = {
        "<Up>": "Up",
        "<Right>": "Right",
        "<Down>": "Down",
        "<Left>": "Left",
    }
    if sym in syms:
        return syms[sym]

    def lettermap(c):
        if os.name == 'posix':
            return c.lower()
        elif os.name == 'nt':
            return c.upper()
        else:
            raise("Unknown operating system.")
    return lettermap(sym)


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
            conf['steer'][adaptsym(key)] = (int(x), int(y))
        elif tokens[0] == 'speed':
            (key, speedstr) = tokens[1:]
            conf['speed'][adaptsym(key)] = modifier(speedstr)
        elif tokens[0] == 'map':
            (fromkey, tokey) = tokens[1:]
            conf['map'][adaptsym(fromkey)] = tokey
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
        if os.name == 'posix':
            self.x11handler(reply)
        elif os.name == 'nt':
            self.windowshandler(reply)
            return True
        else:
            raise("Unknown operating system.")

    def windowshandler(self, reply):
        if reply.IsTransition():
            action = Action.release
        else:
            action = Action.press
        key = reply.GetKey()
        continuous = action == Action.press and key in self.pressedkeys
        if continuous:
            return  # We are not concerned with these kinds of events
        self.pressedkeys.add(key)
        if key not in self.pressedkeys and action == Action.press:
            self.pressedkeys.add(key)
        elif key in self.pressedkeys and action == Action.release:
            self.pressedkeys.remove(key)

    def x11handler(self, reply):
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


class Mouse(PyMouse):
    def __init__(self):
        PyMouse.__init__(self)
        self.leftmousepressed = False
        self.rightmousepressed = False

    def press(self, x, y, button=1):
        PyMouse.press(self, x, y, button)
        if button == 1:
            self.leftmousepressed = True
        elif button == 2:
            self.rightmousepressed = True

    def release(self, x, y, button=1):
        PyMouse.release(self, x, y, button)
        if button == 1:
            self.leftmousepressed = False
        elif button == 2:
            self.rightmousepressed = False


def update(conf, mouse, keylistener):
    """
    Updates the mouse pointer according to the set of currently pressed keys.
    """
    (x, y) = mouse.position()
    (dx, dy) = (0, 0)
    speed = conf['defaultspeed'] if 'defaultspeed' in conf else 1
    leftpress = False
    rightpress = False
    for pressedkey in keylistener.pressedkeys:
        if pressedkey in conf['steer']:
            (ddx, ddy) = conf['steer'][pressedkey]
            (dx, dy) = (dx+ddx, dy+ddy)
        if pressedkey in conf['speed']:
            try:
                speed = float(conf['speed'][pressedkey])
            except TypeError:
                f = conf['speed'][pressedkey]
                speed = f(speed)
        if pressedkey in conf['map']:
            if conf['map'][pressedkey] == '<LeftMouse>':
                leftpress = True
            if conf['map'][pressedkey] == '<RightMouse>':
                rightpress = True
    newx = round(x+speed*dx)
    newy = round(y+speed*dy)
    mouse.move(newx, newy)
    if leftpress and not mouse.leftmousepressed:
        mouse.press(newx, newy, 1)
    elif not leftpress and mouse.leftmousepressed:
        mouse.release(newx, newy, 1)
    if rightpress and not mouse.rightmousepressed:
        mouse.press(newx, newy, 2)
    elif not rightpress and mouse.rightmousepressed:
            mouse.release(newx, newy, 2)


def run(config=defaultconfig()):
    """ Run the program with the specified configuration. """
    conf = parseconfig(config)
    keylistener = KeyListener()
    t = Thread(target=keylistener.run)
    t.start()
    mouse = Mouse()
    while True:
        update(conf, mouse, keylistener)
        sleep(conf['refreshrate'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="KEyboard COntrolled Mouse Pointer.")
    parser.add_argument('-c', '--config', help="Path to configuration file.")
    args = parser.parse_args()

    if args.config:
        config = readconfig(args.config)
        run(config)
    else:
        run()
