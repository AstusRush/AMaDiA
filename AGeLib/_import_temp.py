#region Import
# Astus General Library Main File

Version = "3.0.dev3"
# Using Semantic Versioning 2.0.0 https://semver.org/ and complying to PEP440 https://www.python.org/dev/peps/pep-0440/
version = Version
Author = "Robin \'Astus\' Albers"
"""
    Copyright (C) 2021  Robin Albers
"""
#CRITICAL: All config files should include the version number of the AGeLib that created it!
#CRITICAL: AGeLib should warn the user before overwriting/modifying a file that has a higher version number!

#CRITICAL: This file should be a permanent addition to AGeLib since it cleans up the imports
#          This file should furthermore be importable by applications to streamline their imports and allow them to take advantage of the Qt destribution rebind!

#try:
#    from AGeLib.QtVersion import UsePyQt5,UseVersion
#except ModuleNotFoundError:
#    from QtVersion import UsePyQt5,UseVersion
##try:
##    from AGeLib import QtVersion
##except ModuleNotFoundError:
##    import QtVersion
##UsePyQt5 = QtVersion.UsePyQt5

import sys
import os

#
#try: #TODO: Print which version is used
#    if QtVersion == "PySide6": # pylint: disable=undefined-variable
#        import PySide6
#        dirname = os.path.dirname(PySide6.__file__)
#        plugin_path = os.path.join(dirname, 'plugins', 'platforms')
#        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
#        from PySide6 import QtWidgets,QtCore,QtGui
#        pyqtSignal = QtCore.Signal
#        pyqtProperty = QtCore.Property
#        QtWidgets.QAction = QtGui.QAction
#    elif QtVersion == "PySide2": # pylint: disable=undefined-variable
#        from PySide2 import QtWidgets,QtCore,QtGui
#        pyqtSignal = QtCore.Signal
#        pyqtProperty = QtCore.Property
#    elif QtVersion == "PyQt6": # pylint: disable=undefined-variable
#        from PyQt6 import QtWidgets,QtCore,QtGui
#        pyqtSignal = QtCore.Signal
#        pyqtProperty = QtCore.Property
#    else: # QtVersion == "PyQt5":
#        #TODO: print if QtVersion != "PyQt5" to inform that there was a spelling mistake
#        from PyQt5 import QtWidgets,QtCore,QtGui
#        pyqtSignal = QtCore.pyqtSignal
#        pyqtProperty = QtCore.pyqtProperty
#        #
#        import builtins
#        builtins.QtVersion = "PyQt5"
#except: #TODO: Try to import other Qt Distribution in case PyQt5 is not installed. After all Qt5 will only supported until 2023 and Qt6 will become more and more dominant. PyQt should still be preferred over PySide because of Qsci
#    from PyQt5 import QtWidgets,QtCore,QtGui
#    pyqtSignal = QtCore.pyqtSignal
#    pyqtProperty = QtCore.pyqtProperty
#    #
#    import builtins
#    builtins.QtVersion = "PyQt5"

#try:
#    import QtCore, QtGui, QtWidgets, pyqtSignal, pyqtProperty
#except:
#    from AGeLib import QtCore, QtGui, QtWidgets, pyqtSignal, pyqtProperty
from .AGeQt import * #QtCore, QtGui, QtWidgets, pyqtSignal, pyqtProperty

#

from . import AGeColour

#

import datetime
import time
from time import time as timetime
import platform
import errno
import re
import string
import traceback
import pathlib
import getpass
import importlib
import inspect
import textwrap


from packaging.version import parse as versionParser
#CRITICAL: This is no standard module! It usually is installed everywhere but not guaranteed!
# Helpfull Link: https://stackoverflow.com/questions/11887762/how-do-i-compare-version-numbers-in-python
# It would probably be best to move this into a new function in _AGeFunctions that is called versionParser.
# In this function we can try to import packaging.version and return one of its Version objects but if we can't import it we return either the build-in "from distutils.version import LooseVersion, StrictVersion"
#   or if that import fails we can simply use a brute force approach to try to turn it into a tuple like
###
## def versiontuple(v):
##    return tuple(map(int, (v.split("."))))
###
# (which might already take care of non-digit-characters like a leading "v" but this must be checked! There is also talk about padding everything with leading 0's to deal with strings...)

try:
    import typing
except:
    pass

try:
    import numpy as np
    from numpy import __version__ as numpy_version
except:
    print("Could not import numpy:")
    traceback.print_exc()
    print("numpy is used for processing data concerning plotting graphs. As a result some elements of the User Interface may be blank.")
    numpyImported = False
else:
    numpyImported = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT #mpl control
    from matplotlib.backend_bases import key_press_handler as mpl_key_press_handler #mpl control
except:
    print("Could not import matplotlib:")
    traceback.print_exc()
    print("matplotlib is used for plotting graphs and displaying LaTeX. As a result some elements of the User Interface may be blank.")
    matplotlibImported = False
else:
    matplotlibImported = True

#endregion Import

