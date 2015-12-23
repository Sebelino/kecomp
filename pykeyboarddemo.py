#!/usr/bin/env python

from pykeyboard import PyKeyboardEvent


class EventDemo(PyKeyboardEvent):
    def __init__(self):
        PyKeyboardEvent.__init__(self)
        self.callno = 0

    def handler(self, reply):
        self.callno = self.callno + 1
        print("callno: %d" % self.callno)
        r = reply._data['data']
        if not r:
            return
        print("data: %s" % " ".join("%3d" % c for c in r))
        action = "v" if r[0] == 2 else "^" if r[0] == 3 else "?"
        keycode = r[1]
        keysym = self.lookup_char_from_keycode(keycode)
        continuous = "!" if r[2] == 1 else " " if r[2] == 0 else "?"
        outstr = "output: %s%s %s" % (action, continuous, keysym)
        print(outstr)

if __name__ == '__main__':
    e = EventDemo()
    e.run()
