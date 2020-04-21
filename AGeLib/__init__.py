"""
Astus' General Library  \n
This library provides a prebuild QApplication (with standard options window (alt+O) and basic global shortcuts)
and custom windows (including custom frames and a space efficient notification display) for PyQt5 applications. \n
Use Main_App instead of QtWidgets.QApplication and AWWF instead of QtWidgets.QMainWindow. \n
For communication with the user and exception output use NC.
NC is AGeLib's standard notification class and is especially useful for exception handling as it can create a full bug report. \n
Import the exc submodule to access all exception handling functions. \n \n
In addition to this AGeLib also provides several advanced widgets to provide a sophisticated alterernative to the barebone Qt base widgets. \n
AGeMain.py includes a basic example with a main function and a test window. \n
For a more advanced example please visit https://github.com/AstusRush/AMaDiA .\n
AMaDiA was not only build to fully utilise most to all features of AGeLib but was also the origin of AGeLib: \n
As AMaDiA's basic application grew it became apparent that it should be turned into a separate Library: AGeLib
"""
try:
    from AGeLib.AGeMain import *
except ModuleNotFoundError:
    from AGeMain import *
try:
    from AGeLib import exc
except ModuleNotFoundError:
    import exc
__version__ = Version
__all__ = ["Main_App",
           "AWWF","common_exceptions",
           "ExceptionOutput",
           "NC",
           "MplWidget",
           "MplWidget_2D_Plot",
           "MplWidget_LaTeX",
           "ListWidget",
           "NotificationInfoWidget",
           "TextEdit",
           "LineEdit",
           "TableWidget",
           "TableWidget_Delegate",
           "TopBar_Widget",
           "MenuAction",
           "advancedMode",
           "App"
           ]