"""
Astus' General Library  \n
This library provides a prebuild QApplication (with standard options window (alt+O) and basic global shortcuts)
and custom windows (including custom frames and a space efficient notification display) for PyQt5 applications. \n
Use Main_App instead of QtWidgets.QApplication and AWWF instead of QtWidgets.QMainWindow. \n
For communication with the user and exception output use NC.
NC is AGeLib's standard notification class and is especially useful for exception handling as it can create a full bug report. \n
Import the exc submodule to access the most common functions (most notably NC and App). \n \n
In addition to this AGeLib also provides several advanced widgets to provide a sophisticated alterernative to the barebone Qt base widgets. \n
AGeMain.py includes a basic example with a main function and a test window. \n
For a more advanced example please visit https://github.com/AstusRush/AMaDiA .\n
AMaDiA was not only build to fully utilise most to all features of AGeLib but was also the origin of AGeLib: \n
As AMaDiA's basic application grew it became apparent that it should be turned into a separate Library: AGeLib \n
\n
QtCore, QtGui, QtWidgets, pyqtSignal, and pyqtProperty should be imported from AGeLib rather than separately as AGeLib provides
support for PyQt5, PyQt6, PySide2, and PySide6 and loads whichever is available on the machine. \n
(The bindings AGeLib provides have the structure of PyQt5.
The support for PyQt6 and PySide6 is WIP and I might have missed some minor rebinds for PySide2 but if you find any problems feel free to contact me so that I can fix them.)\n
To set a specific Qt distribution use: \n
```
import builtins
builtins.QtVersion = "PyQt5" # Options: "PyQt5", "PyQt6", "PySide2", "PySide6"
```
before importing this module. (If the import fails the distribution falls back to PyQt5.)\n
"""

breaking_the_rules = """
Hi there!
If you have some programming experience you will have noticed that I am breaking many rules and conventions in this Library.
For example: I use camelCase in python.
But I have always (I hope... its probably more like "almost always" or "often") good reasons to do so. (Ok I don't have a good reason to program with british spelling except for that it is objectively the correct spelling.)
For example: I was originally using snake_case but Qt uses camelCase and I would argue that mixing camelCase and snake_case in a program is even worse than using camelCase in python.
    So I switched most things to camelCase for consistency. (And while yes, PySide6 does support snake_case this library is older than PySide6 and I won't change everything.)

Things like
    saving data as code (AGeToPy) instead of using something like JSON,
    catching all exceptions by redirecting them,
    and completely throwing "never touch a running system" out of the window with AGeIDE
may seem like war crimes to some but these things allow for an enormous flexibility that in my opinion outweighs the consequences.

If I want good solid code that can run undisturbed for years and has a completely predictable behaviour I write in C.
If I want flexible code that is fast to write and can be easily modified I use Python.
This library builds upon pythons flexibility to allow for things that are enormously powerful like
      tweaking some functions in a simulation program without restarting it so that you don't have to generate all the basic data every time
   or tweaking a function and comparing the result to the previous version without saving the data as it is simply stored as a variable
and if there is a typo the exception is caught and no simulation data is lost.
This alone has saved me hours of work.

To Sum this up:
    It is just more fun if you break some rules! (Just be mindful of the broken rules and be prepared for the consequences.)
"""

#region Import
from .AGeQt import * #QtCore, QtGui, QtWidgets, pyqtSignal, pyqtProperty
#from _AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC, common_exceptions
#from _AGeFunctions import *
#from _AGeWidgets import *
#from _AGeSpecialWidgets import *
#from _AGeGW import *
#from _AGeAWWF import *
#from _AGeWindows import *
#from _AGeApp import *
#from _AGeQuick import *
#from _AGeIDE import *
from . import AGeCore
from . import AGeWidgets
from . import AGeAux
from . import AGeWindows
from . import AGeGW
from . import AGeSpecialWidgets
from . import AGeQuick
from . import AGeIDE
from . import AGeToPy
from .AGeCore import *
#endregion Import

AGeLibVersion = AGeCore.AGeLibVersion
#__all__ = ["MainApp",
#           "AWWF",
#           "App",
#           "NC",
#           "common_exceptions",
#           "ExceptionOutput",
#           "MplWidget",
#           "MplWidget_2D_Plot",
#           "MplWidget_LaTeX",
#           "ListWidget",
#           "NotificationInfoWidget",
#           "TextEdit",
#           "LineEdit",
#           "TableWidget",
#           "TableWidget_Delegate",
#           "TopBar_Widget",
#           "MenuAction",
#           "advancedMode",
#           "Button",
#           "QuickSetup",
#           "QuickWindow"
#           ]

#CRITICAL: Currently importing a module is a mess since everything conatians everything.
#       The solution is to rename all modules with a leading underscore and make new modules that import only the important items from the underscored modules.
#       This way the imports don't even need to be overhauled since the important things would be included in the new modules.
#       Though this adds a bit more maintenance work when making new functions and classes it cleans up the importing procedure

#CRITICAL: Streamline the name scheme of EVERYTHING!
#       Class
#       method
#       _helperMethod
#       self.MemberVariable
#       self._TemporaryMemberVariable
#       self.Widget
#       localVariablesInMethod
#       function
#       FunctionToAccessGlobalObjects (App should stay App which I justify by arguing that App() returns an object just like Class() does)
#       argument
#       Window_NameOfTheWindow (Maybe... windows have their own module so this is not necessary...)
#
#   Generally CamelCase should be used but underscores are great to separate words like namespaces like TextAddon_Finder ... Though maybe it should really be QGeLibTextAddons.Finder ? Better example: Lexer_Python
#   Widgets that improve upon QtWidgets should keep the name but drop the leading Q. Should AWWF be renamed to MainWindow or Window? I don't like this change but it would be much easier to understand for other people...
#   Everything should only have one name! There should not be unnecessary rebindings as they make the code unreadable! (Exception: toPlainText = text since they do the same but QtWidgets have either one or the other (depending on wether they support html etc.) which is confusing)
#   Members with a similar purpose should start with the same letters/word to make autocomplete easier. For Example all AGeLib folder paths should be named "FolderPath_{name of folder}" (instead of the current "{name of folder}FolderPath")
#
#
#   Dear Future Robin: I know this is a lot of work and needs a lot of changes in other projects but IT IS NECESSARY! Do this refactor and stick to this schema in the future!
#                       Maybe you can collect all renamed words and store them in a dictionary. Then you can make a regex and scan all files with VSCode and use the dict in a minimal Python GUI to find the new name?
#                       Or write a Python GUI to help you with the renaming? A textfield with drag'n'drop to load files. It then goes through the dict, automatically highlights all entries of the dict one by one and asks if you want to rename the current selection.
#   Do not delete these notes but add them as a string to AGeLib so that everyone can read up on the naming convention.
#   TODO: Add to these naming conventions

#V3: Things that need to be done in update 3.0.0
# Put the Mpl Widgets in their own submodule so that mpl is no longer a forced import for all programs
# Try to eliminate some imports to speed up start time
# Reevaluate the names of all widgets
# Reevaluate the names of EVERYTHING (Re: Streamline the name scheme of EVERYTHING!)
# Make easily importable submodules (just like Qt) and overhaul all projects to use these new submodules. Having averything in one module was nice in the beginning but AGeLib has become too big for that approach.
# Make import errors more easily traceable for users
# Remove dead variables and unnecessary rebindings
# ~~Change import to make reloadAll work~~ This is no longer necessary (thanks to AGeIDE) and has always been a very bad idea that wouldn't have worked anyways!
# Make compatible with PySide2, PySide6 and PyQt6
# Make Everything easier to find with autocomplete (for example by making everything begin with A) OR remove some A's in the beginning (like the one from AButton)!!!
#       The current state (especially AButton's A in the beginning) is a bit confusing
#       UPDATE: Just make the submodules from which everything can be imported! This solves the autocomplete problems
# Plan for the future!!! Version 4 should be avoided as long as possible! Do what you can to make Version 4 avoidable! Leave things space to grow! The interface should not change, only grow. How can you avoid future changes?
# Plan for subfolders!!! They will come sooner or later! Allow for them to come in V3! They should not force a V4!
