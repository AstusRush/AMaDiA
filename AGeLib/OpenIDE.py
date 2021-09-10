
import traceback
import sys
sys.path.append('..')
from AGeLib import *

import numpy as np
import matplotlib as mpl
import datetime
import time
import os
import re

import inspect

import sympy

def main():
    app = AGeApp([])
    app.showWindow_IDE()
    try: # on windows minimize the console
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
    except:
        pass
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
