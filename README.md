KEyboard-COntrolled Mouse Pointer
======

Allows you to control the mouse using the keyboard.

To configure, edit the ``config`` variable in the beginning of the source file for now.

Currently only for MS Windows.

Dependencies
======
* Python 3
* pywin32

Usage
======
```
python kecomp.py
```

Example configuration
======
```
config = """
steer <Up>    0 -1
steer <Down>  0  1
steer <Left> -1  0
steer <Right> 1  0
speed X 1
speed C 5
map Z <LeftMouse>
"""
```
