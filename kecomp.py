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
