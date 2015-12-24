KEyboard-COntrolled Mouse Pointer
======

Allows you to control the mouse pointer with your keyboard. Supported on Linux and Windows.

## Dependencies
* Python 3
* [PyUserInput](https://github.com/SavinaRoja/PyUserInput) (see if the latest commit works, otherwise try commit d45f45ffbb2399d964eb515c887c493a1837c09d)

## Usage
```
usage: kecomp.py [-h] [-c CONFIG]

KEyboard COntrolled Mouse Pointer.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file.
```

### Configuration
The program can be configured to some extent. There are four alternatives for supplying a configuration:
1. By supplying a path to your configuration file like so: ``$ python kecomp.py -c ~/.mykecomp.conf``
2. By storing your configuration in a file named ``kecomp.conf`` in the current working directory and running the program normally: ``python kecomp.py``. Alternative 1 overrides this.
3. By storing your configuration in a file named ``kecomp.conf`` in the same directory as ``kecomp.py`` and running the program normally: ``python kecomp.py``. Alternative 2 overrides this.
4. If none of the conditions above are met, the program defaults to a fallback configuration.

The configuration file follows a Vimscript-like syntax. Each line in the configuration file is either of the following:
* ``steer KEY XDIFF YDIFF`` moves the mouse pointer XDIFF pixels to the right and YDIFF pixels down when keyboard key KEY is pressed.
* ``default speed DEFAULTSPEED`` multiplies XDIFF and YDIFF above by a factor DEFAULTSPEED.
* ``speed KEY SPEED`` multiplies XDIFF and YDIFF mentioned above by a factor SPEED when key KEY is pressed.
* ``speed KEY *SPEED`` multiplies XDIFF and YDIFF mentioned above by DEFAULTSPEED*SPEED when key KEY is pressed.
* ``speed KEY /SPEED`` multiplies XDIFF and YDIFF mentioned above by DEFAULTSPEED/SPEED when key KEY is pressed.
* ``map KEY MOUSEBUTTON`` causes mouse button MOUSEBUTTON to be pressed/released whenever key KEY is pressed/released.
* ``refreshrate MILLISECONDS`` tells the program to handle key events every MILLISECONDS milliseconds. This affects the speed at which the mouse is moved.

## Example
``sample.conf`` contains a sample configuration. To use it, supply the ``--config`` flag:
```
$ python kecomp.py -c sample.conf
```
Alternatively, rename it to ``kecomp.conf``.
