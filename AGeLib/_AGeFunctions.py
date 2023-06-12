#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
#endregion Import

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from ._AGeApp import AGeApp
except:
    pass

#region Time Format Functions

def cTimeStr():
    # type: () -> str
    """
    Returns the time (excluding seconds) as a string\n
    %H:%M
    """
    return str(datetime.datetime.now().strftime('%H:%M'))

def cTimeSStr():
    # type: () -> str
    """
    Returns the time (including seconds) as a string\n
    %H:%M:%S
    """
    return str(datetime.datetime.now().strftime('%H:%M:%S'))

def cTimeFullStr(separator = None):
    # type: (str) -> str
    """
    Returns the date and time as a string\n
    If given uses `separator` to separate the values\n
    %Y.%m.%d-%H:%M:%S or separator.join(['%Y','%m','%d','%H','%M','%S'])
    """
    if separator is None:
        return str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    else:
        TheFormat = separator.join(['%Y','%m','%d','%H','%M','%S'])
        return str(datetime.datetime.now().strftime(TheFormat))

#endregion

#region Shortcut Functions

def advancedMode():
    # type: () -> bool
    """
    Used to check whether the advanced mode is active in the application.   \n
    The `MainApp` emits `S_advanced_mode_changed` when `toggleAdvancedMode` is called.   \n
    "Dangerous" functions and "rarely used" should only be accessible if the advanced mode is on.
    - "Dangerous": Dev-functions and anything that a user should not accidentely press.
    - "rarely used": Anything that is rarely used and would clutter up the UI.   \n
    The advanced mode can also be used to determine the behaviour of certain function:
    - off: Functionality is easy to use but is limited to the most frequent use cases
    - on: User has full control over behaviour (which makes the controls more complex and time consuming) \n
    This can also be used to control the displayed information:
    - off: Only relevant information is shown
    - on: All information is shown (but the GUI is flooded with text)
    """
    return QtWidgets.QApplication.instance().advanced_mode

def App():
    # type: () -> AGeApp
    """Convenient shortcut for `QtWidgets.QApplication.instance()`"""
    return QtWidgets.QApplication.instance()

#endregion


#region Functions

def recolourIcon(icon,colour=None,size=128):
    # type: (QtGui.QIcon, QtGui.QColor, int) -> QtGui.QIcon
    """
    Recolour the none transparent part of `icon` (QIcon) to `colour` (QColor). The returned Icon will have a resolution of `size` * `size`. \n
    If no colour is given `App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text)` is used. The size defaults to 128. \n
    Remember to update the colour of the icon when the app's colour palette changes if you use a colour of one of the 3 palettes or any of the colour dictionaries of the app. \n
    To do this it is recommended to make a method that sets the icons and connect it to the global signal: `App().S_ColourChanged.connect(lambda: self.recolourIcons())`
    """
    if colour is None:
        colour = App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text)
    pixmap = icon.pixmap(size)
    mask = pixmap.createMaskFromColor(QtGui.QColor('transparent'), QtCore.Qt.MaskInColor)
    pixmap.fill(colour)
    pixmap.setMask(mask)
    return QtGui.QIcon(pixmap)

def getPath(mustExist=False):
    # type: (bool) -> str
    """
    Opens a prompt for the user to input a path. If `mustExist` the file must already exist. If the user cancels the prompt a `FileNotFoundError` exception is raised.
    """
    if mustExist:
        p = QtWidgets.QFileDialog.getOpenFileName()[0]
    else:
        p = QtWidgets.QFileDialog.getSaveFileName()[0]
    if p:
        return p
    else:
        raise FileNotFoundError("The file name was empty")

def isInstanceOrSubclass(obj, cls):
    if isinstance(obj, type):
        return issubclass(obj, cls)
    else:
        return isinstance(obj, cls)
#endregion


