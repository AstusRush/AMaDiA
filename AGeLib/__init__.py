"""
Astus' General Library
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
           "advancedMode"
           ]