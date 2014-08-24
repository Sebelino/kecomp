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

import win32api, win32con
from time import sleep

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
def move(coord):
    win32api.SetCursorPos(coord)
def inverse(event):
    if win32con.MOUSEEVENTF_LEFTDOWN:
        return win32con.MOUSEEVENTF_LEFTUP
    raise Exception('Inverse for event does not exist.')
    
def parseconfig(config):
    conf = {'speed': dict(),'steer': dict(),'map': dict()}
    for line in config.strip().splitlines():
        tokens = line.split()
        if tokens[0] == 'steer':
            (key,x,y) = tokens[1:]
            conf['steer'][keymap[key]] = (int(x),int(y))
        elif tokens[0] == 'speed':
            (key,speed) = tokens[1:]
            conf['speed'][keymap[key]] = int(speed)
        elif tokens[0] == 'map':
            (fromkey,tokey) = tokens[1:]
            conf['map'][keymap[fromkey]] = keymap[tokey]
    return conf

if __name__ == '__main__':
    keymap = {
        '<Up>':    win32con.VK_UP,
        '<Down>':  win32con.VK_DOWN,
        '<Left>':  win32con.VK_LEFT,
        '<Right>': win32con.VK_RIGHT,
        '<LeftMouse>': win32con.MOUSEEVENTF_LEFTDOWN,
    }
    alphakeys = 'abcdefghijklmnopqrstuvxyz'
    for letter in alphakeys+alphakeys.upper():
        keymap[letter] = ord(letter)

    '''
    conf = {
        'speed': {
            ord('X'): 1,
            ord('C'): 5,
        },
        'steer': {
            win32con.VK_UP:    (0,-1),
            win32con.VK_DOWN:  (0, 1),
            win32con.VK_LEFT:  (-1,0),
            win32con.VK_RIGHT: (1, 0),
        },
        'map': {
            ord('Z'): win32con.MOUSEEVENTF_LEFTDOWN,
        },
    }
    '''

    conf = parseconfig(config)

    state = {
        'pressed': True,
    }
    while True:
        delay = 0.01
        step = 20
        for k,v in conf['speed'].items():
            if win32api.GetAsyncKeyState(k):
                step = v
        sleep(delay)
        tempx,tempy = win32api.GetCursorPos()
        for k,v in conf['steer'].items():
            if win32api.GetAsyncKeyState(k):
                move(tuple(map(sum,zip((tempx,tempy),(step*x for x in v)))))
                tempx,tempy = win32api.GetCursorPos()
        for k,v in conf['map'].items():
            if win32api.GetAsyncKeyState(k):
                if not state['pressed']:
                    state['pressed'] = True
                    win32api.mouse_event(v,tempx,tempy,0,0)
                    print("Pressar")
            else:
                if state['pressed']:
                    state['pressed'] = False
                    win32api.mouse_event(inverse(v),tempx,tempy,0,0)
                    print("Slutade pressa")
