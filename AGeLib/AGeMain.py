# Astus General Library Main File

Version = "2.1.0"
# Using Semantic Versioning 2.0.0 https://semver.org/
version = Version
Author = "Robin \'Astus\' Albers"
"""
    Copyright (C) 2020  Robin Albers
"""

try:
    from AGeLib import AGeColour
except ModuleNotFoundError:
    import AGeColour

import sys
from PyQt5 import QtWidgets,QtCore,QtGui,Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView # pylint: disable=no-name-in-module
import datetime
import time
from time import time as timetime
import platform
import errno
import os
import re
import string
import traceback
import pathlib
import getpass
import importlib
from packaging.version import parse as versionParser

import sympy
from sympy.parsing.sympy_parser import parse_expr
from numpy import __version__ as numpy_version

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

from distutils.spawn import find_executable
if find_executable('latex') and find_executable('dvipng'): LaTeX_dvipng_Installed = True
else : LaTeX_dvipng_Installed = False

#TODO: Add documentation to ALL classes, methods and functions

#region Notifications and exceptions

common_exceptions = (TypeError , SyntaxError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError)
def ExceptionOutput(exc_info = None, extraInfo = True):
    """
    Console output for exceptions\n
    Use in `except:`: Error = ExceptionOutput(sys.exc_info())\n
    Prints Time, ExceptionType, Filename+Line and (if extraInfo in not False) the exception description to the console\n
    Returns a string
    """
    try:
        if False:
            if exc_info == None:
                exc_info = True
            return NC(exc=exc_info)
        else:
            print(cTimeSStr(),":")
            if exc_info==None:
                exc_type, exc_obj, exc_tb = sys.exc_info()
            else:
                exc_type, exc_obj, exc_tb = exc_info
            fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            if extraInfo:
                print(exc_type, " in", fName, " line", exc_tb.tb_lineno ,": ", exc_obj)
            else:
                print(exc_type, " in", fName, " line", exc_tb.tb_lineno)
            return str(exc_type)+": "+str(exc_obj)
    except common_exceptions as inst:
        print("An exception occurred while trying to print an exception!")
        print(inst)

# -----------------------------------------------------------------------------------------------------------------

class NotificationEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, N):
        QtCore.QEvent.__init__(self, NotificationEvent.EVENT_TYPE)
        self.N = N

class NC: # Notification Class
    """
    This is the basic notification class of AGeLib.  \n
    All notifications are stored and accessible via the Notification Window which is opened by pressing on Notification button of any (AWWF) window.   \n
    Notifications are used to communicate with the user and can be used for exception handling as they provide space for an entire bug report.   \n
    They contain the version number of all modules that are in MainApp.ModuleVersions and can extract all information from exceptions.   \n
    There are various levels of notifications: lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
    The notification sends itself automatically. If you want to modify the notification before it is send set ``send=False`` and call ``.send()`` after the modifications are done  \n
    The creation is very flexible. Here are a few examples:   \n
    ```python
    NC(10,"This message is directly displayed in the top bar and should be held very short and not contain any linebreaks (a single linebreak is ok in spacial cases)")
    NC("This creates a normal notification")
    NC(2,"This creates a warning")
    NC((2,"A tuple with level and message is also acceptable"))
    NC("This generates an error notification with the last caught exception",exc = sys.exc_info())
    NC("This notification includes the callstack",tb=True)
    ```
    Even this is valid: ``NC()`` (Though not recommended)   \n
    ``lvl=0`` can be useful if you want to create a notification in a function (with ``Notification = NC(lvl=0,send=False)``), fill it with information dynamically and return it for the caller.
    The caller can then send the Notification. If ``lvl=0`` the MainApp will ignore the notification thus the caller does not need to care whether the function actually had anything to notify the user about.   \n
    If you want to notify the user about exceptions ``exc`` should be ``True`` or ``sys.exc_info()``. If the exception should be logged but is usually not important set ``lvl=4``.
    If the exception is not critical but should be noted as it might lead to unwanted behaviour set ``lvl=2`` to warn the user.
    Exception notifications should set ``msg`` to give a short description that a regular user can understand (for example ``msg="The input could not be interpreted."`` or ``msg="Could not connect to the website."``).
    It is also useful to set ``input`` to log the input that lead to the error. This should also include any settings that were used.   \n
    Only ``lvl=int``,``time=datetime.datetime.now()``,``send=bool`` and ``exc=True or sys.exc_info()`` need a specific data type.
    Everything else will be stored (msg will be converted into a string before storing). The access methods will return a string (and cast all input to a string before saving)
    but the variables can still be accessed directly with the data type that was given to the init.  \n
    Please note that ``err`` and ``tb`` are ignored when ``exc != None`` as they will be extracted from the exception.  \n
    ``tb`` should be a string containing the callstack or ``True`` to generate a callstack
    """
    def __init__(self, lvl=None, msg=None, time=None, input=None, err=None, tb=None, exc=None, win=None, func=None, DplStr=None, send=True):
        """
        Creates a new notification object  \n
        The creation is very flexible. Here are a few examples:   \n
        ```python
        NC(10,"This message is directly displayed in the top bar and should be held short and without linebreaks")
        NC("This creates a normal notification")
        NC(2,"This creates a warning")
        NC((2,"A tuple with level and message is also acceptable"))
        NC("This generates an error notification with the last caught exception",exc = sys.exc_info())
        NC("This notification includes the callstack",tb=True)
        ```
        lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
        ``exc = True`` or ``sys.exc_info()``   \n
        ``tb`` should be a string containing the callstack or ``True`` to generate a callstack
        """
        self._time_time = timetime()
        self._init_Values()
        self._was_send = False
        try:
            self._time = datetime.datetime.now() if time == None else time
            self.Time = self._time.strftime('%H:%M:%S')
            self.DplStr = DplStr
            self.Window = win
            self.Function = func
            self.Input = input
            if exc != None:
                if exc == True:
                    self.exc_type, self.exc_obj, self.exc_tb = sys.exc_info()
                else:
                    self.exc_type, self.exc_obj, self.exc_tb = exc
                fName = os.path.split(self.exc_tb.tb_frame.f_code.co_filename)[1]
                if type(lvl)==str:
                    self.level = 1
                    self.Message = lvl
                elif msg==None and type(lvl) == tuple:
                    self.level, self.Message = lvl[0], lvl[1]
                else:
                    self.level = 1 if lvl == None else lvl
                    self.Message = str(msg) if msg!=None else None
                self.ErrorTraceback = str(self.exc_type)+"  in "+str(fName)+"  line "+str(self.exc_tb.tb_lineno)+"\n\n"+str(traceback.format_exc())#[:-1]) # TODO: Use traceback.format_exc() to get full traceback or something like traceback.extract_stack()[:-1] ([:-1] removes the NC.__init__())
                print(self.Time,":")
                if len(str(self.exc_obj))<150:
                    self.Error = str(self.exc_type)+": "+str(self.exc_obj)
                    print(self.exc_type, " in", fName, " line", self.exc_tb.tb_lineno,": ", self.exc_obj)
                else:
                    self.Error = str(self.exc_type)
                    self.ErrorLongDesc = str(self.exc_obj)
                    print(self.exc_type, " in", fName, " line", self.exc_tb.tb_lineno)
            else:
                if type(lvl)==str:
                    self.level = 3
                    self.Message = lvl
                elif msg==None and type(lvl) == tuple:
                    self.level, self.Message = lvl[0], lvl[1]
                else:
                    self.level = 3 if lvl == None else lvl
                    self.Message = str(msg) if msg!=None else None
                self.Error = err
                if tb == True:
                    self.ErrorTraceback = ""
                    try:
                        for i in traceback.format_stack()[0:-1]:
                            self.ErrorTraceback += str(i)
                    except:
                        self.ErrorTraceback = "Could not extract callstack"
                else:
                    self.ErrorTraceback = tb
            self.GenerateLevelName()
            if send == True:
                self.send()
        except common_exceptions as inst:
            self._init_Values()
            print(cTimeSStr(),": An exception occurred while trying to create a Notification")
            print(inst)
            self._time = datetime.datetime.now() if time == None else time
            self.Time = self._time.strftime('%H:%M:%S')
            self.Message = "An exception occurred while trying to create a Notification"
            self.exc_obj = inst
            self.Error = str(inst)
            self.GenerateLevelName()
            self.send(force=True)

    def _init_Values(self):
        self.exc_type, self.exc_obj, self.exc_tb = None,None,None
        self._time, self.Time, self.Error = None,None,None
        self.Window, self.ErrorTraceback, self.Function = None,None,None
        self.level, self.Level, self.Message = 1,"Notification level 1",None
        self.Input, self.ErrorLongDesc = None,None
        self.DplStr, self.TTStr = None,None
        self.icon = QtGui.QIcon()
        try:
            self.Flash = QtWidgets.QApplication.instance().NCF_NONE
        except common_exceptions as inst:
            print(inst)
            self.Flash = None
        self.itemDict = {"Time:\n":self.Time,"Level: ":self.Level,"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input}
  #---------- send, print ----------#
    def send(self,force=False):
        """
        Displays this notification (This method is thread save but this object should not be modified after using send)   \n
        A notification can only be send once. ``force=True`` allows to send an already send notification again
        """
        if force or not self._was_send:
            self._was_send = True
            QtWidgets.QApplication.postEvent(QtCore.QThread.currentThread(), NotificationEvent(self))

    def print(self):
        """Prints this notification to the console"""
        print("\n",self.Level, "at",self.Time,"\nMessage:",self.Message)
        if self.Error != None:
            print("Error:",self.Error,"Traceback:",self.ErrorTraceback,"\n")
  #---------- items, unpack ----------#
    def items(self):
        """
        Returns self.itemDict.items()   \n
        self.itemDict contains all relevant data about this notification.  \n
        Please note that not all values are strings and should be converted before diplaying them.
        This allows ``if v!=None:`` to filter out all empty entries.    \n
        The keys already end with ``:\\n`` thus it is advised to simply use ``k+str(v)`` for formatting.  \n
        For an example how to use this method see the source code of ``NotificationInfoWidget``.
        """
        self.itemDict = {"Time:\n":self.Time,"Level: ":"({})\n{}".format(str(self.level),self.Level),"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input,"Versions:\n":QtWidgets.QApplication.instance().ModuleVersions}
        return self.itemDict.items()

    def unpack(self): #CLEANUP: remove unpack
        """DEPRECATED: Returns a tuple ``(int(level),str(Message),str(Time))``"""
        return (self.level, str(self.Message), self.Time)
  #---------- access variables ----------#
    def l(self, level=None):
        """
        Returns int(level)  \n
        An int can be given to change the level
        """
        if level != None:
            self.level = level
            self.GenerateLevelName()
        return self.level

    def m(self, message=None):
        """
        Returns str(Message)  \n
        A str can be given to change the Message
        """
        if message != None:
            self.Message = str(message)
        if self.Message == None and self.Error != None:
            return str(self.Error)
        else:
            return str(self.Message)
        
    def DPS(self, DplStr = None):
        """
        Returns str(DplStr)  \n
        DplStr is the string that is intended to be displayed directly   \n
        A str can be given to change the DplStr
        """
        if DplStr != None:
            self.DplStr = str(DplStr)
        elif self.DplStr == None:
            if self.level == 10:
                self.DplStr = self.m()
            else:
                self.DplStr = self.Level + " at " + self.t()
        return str(self.DplStr)
        
    def TTS(self, TTStr = None):
        """
        Returns str(TTStr)  \n
        TTStr is the string that is intended to be displayed as the tool tip   \n
        A str can be given to change the TTStr
        """
        if TTStr != None:
            self.TTStr = str(TTStr)
        elif self.TTStr == None:
            if self.level == 10:
                self.TTStr = self.Level + " at " + self.t()
            else:
                self.TTStr = self.m()
        return str(self.TTStr)

    def t(self, time=None):
        """
        Returns the time as %H:%M:%S  \n
        datetime.datetime.now() can be given to change the time
        """
        if time != None:
            self._time = time
            self.Time = self._time.strftime('%H:%M:%S')
        return self.Time

    def e(self, Error=None, ErrorTraceback=None):
        """
        Returns str(Error)  \n
        strings can be given to change the Error and ErrorTraceback
        """
        if Error != None:
            self.Error = str(Error)
        if ErrorTraceback != None:
            self.ErrorTraceback = str(ErrorTraceback)
        return str(self.Error)

    def tb(self, ErrorTraceback=None):
        """
        Returns str(ErrorTraceback)  \n
        A str can be given to change the ErrorTraceback
        """
        if ErrorTraceback != None:
            self.ErrorTraceback = str(ErrorTraceback)
        return str(self.ErrorTraceback)

    def f(self, func=None):
        """
        Returns str(Function)  \n
        A str can be given to change the Function  \n
        Function is the name of the function from which this notification originates
        """
        if func != None:
            self.Function = str(func)
        return str(self.Function)

    def w(self, win=None):
        """
        Returns str(Window)  \n
        A str can be given to change the Window  \n
        Window is the name of the window from which this notification originates
        """
        if win != None:
            self.Window = str(win)
        return str(self.Window)

    def i(self, input=None):
        """
        Returns str(Input)  \n
        A str can be given to change the Input  \n
        Input is the (user-)input that caused this notification
        """
        if input != None:
            self.Input = str(input)
        return str(self.Input)
  #---------- GenerateLevelName ----------#
    def GenerateLevelName(self):
        """
        Generates str(self.Level) from int(self.level)
        """
        try:
            if self.level == 0:
                self.Level = "Empty Notification"
                self.icon = QtGui.QIcon()
                self.Flash = QtWidgets.QApplication.instance().NCF_NONE
            elif self.level == 1:
                self.Level = "Error"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical)
                self.Flash = QtWidgets.QApplication.instance().NCF_r
            elif self.level == 2:
                self.Level = "Warning"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning)
                self.Flash = QtWidgets.QApplication.instance().NCF_y
            elif self.level == 3:
                self.Level = "Notification"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
                self.Flash = QtWidgets.QApplication.instance().NCF_b
            elif self.level == 4:
                self.Level = "Advanced Mode Notification"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
                self.Flash = QtWidgets.QApplication.instance().NCF_b
            elif self.level == 10:
                self.Level = "Direct Notification"
                self.icon = QtGui.QIcon()
                self.Flash = QtWidgets.QApplication.instance().NCF_NONE
            else:
                self.Level = "Notification level "+str(self.level)
                self.Flash = QtWidgets.QApplication.instance().NCF_b
            return self.Level
        except common_exceptions as inst:
            print(inst)
            return "Could not generate Level Name"
  #---------- __...__ ----------#
    def __add__(self,other):
        if self.Error != None:
            return str(self.Error) + str(other)
        else:
            return str(self.Message) + str(other)

    def __radd__(self,other):
        if self.Error != None:
            return str(other) + str(self.Error)
        else:
            return str(other) + str(self.Message)

    def __call__(self):
        return str(self.Message)

    def __str__(self):
        if self.Error != None:
            if self.Message == None:
                return "Exception at "+str(self.Time)+":\n"+str(self.Error)
            else:
                return str(self.Level)+" at "+str(self.Time)+":\n"+str(self.Message)+"\n"+str(self.Error)
        else:
            return str(self.Level)+" at "+str(self.Time)+":\n"+str(self.Message)

#endregion

#region Helper Classes
class ColourDict(dict):
    """
    This class is used to store the special colours. \n
    It is used to ensure that a missing colour does not cause a crash by returning the "Blue" colour.
    """
    def __getitem__(self, key):
        try:
            Colour = dict.__getitem__(self, key)
        except:
            for v in self.values():
                Colour = v
                break
        return Colour
    
    def copyFromDict(self, dict):
        for i,v in dict.items():
            self[i] = v

#endregion

#region Functions

def cTimeStr():
    """
    Returns the time (excluding seconds) as a string\n
    %H:%M
    """
    return str(datetime.datetime.now().strftime('%H:%M'))

def cTimeSStr():
    """
    Returns the time (including seconds) as a string\n
    %H:%M:%S
    """
    return str(datetime.datetime.now().strftime('%H:%M:%S'))

def cTimeFullStr(separator = None):
    """
    Returns the date and time as a string\n
    If given uses `separator` to separate the values\n
    %Y.%m.%d-%H:%M:%S or separator.join(['%Y','%m','%d','%H','%M','%S'])
    """
    if separator == None:
        return str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    else:
        TheFormat = separator.join(['%Y','%m','%d','%H','%M','%S'])
        return str(datetime.datetime.now().strftime(TheFormat))

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, send info
    NC(1,"An unhandled exception occurred in a QThread!!!",err=str(args))
#endregion

#region Shortcut Functions

def advancedMode() -> bool:
    """
    Used to check whether the advanced mode is active in the application.   \n
    The ``Main_App`` emits ``S_advanced_mode_changed`` when ``ToggleAdvancedMode`` is called.   \n
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

def App() -> QtWidgets.QApplication:
    """Convenient shortcut for ``QtWidgets.QApplication.instance()``"""
    return QtWidgets.QApplication.instance()
#endregion

#region Application
# ---------------------------------- Main Application ----------------------------------
AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier
MetaModifier = QtCore.Qt.MetaModifier

class Main_App(QtWidgets.QApplication):
    """
    This class is the core of AGeLib.   \n
    Methods beginning with ``r_`` are virtual templates that can be reimplemented.   \n
    TODO: MORE INFO
    """
    #MAYBE: Make standard hotkeys optional (in case a dev wants to use these hotkeys) but write a warning that changing these is not recommended as it might confuse users that are used to the standard AGeLib Hotkeys
 #
    # See:
    # https://doc.qt.io/qt-5/qapplication.html
    # https://doc.qt.io/qt-5/qguiapplication.html
    # https://doc.qt.io/qt-5/qcoreapplication.html
    S_New_Notification = QtCore.pyqtSignal(NC)
    S_FontChanged = QtCore.pyqtSignal()
    S_ColourChanged = QtCore.pyqtSignal()
    S_advanced_mode_changed = QtCore.pyqtSignal(bool)
    def __init__(self, args):
        self.enableHotkeys = True
        super(Main_App, self).__init__(args)
        self.setStyle("fusion")
        sys.excepthook = trap_exc_during_debug
        try:
            msg = "Welcome " + getpass.getuser()
        except:
            msg = "Welcome"
        self.LastNotificationText = msg
        self.LastNotificationToolTip = msg
        self.LastNotificationIcon = QtGui.QIcon()

        self.MainWindow = None
        self.Notification_Window = None
        self.exec_Window = None
        self.optionWindow = None
        self.AppPalettes = {}
        
        self.installEventFilter(self)
        self.aboutToQuit.connect(self._SaveClipboard)

        self.advanced_mode = False
        
        self.setOrganizationName("Robin Albers")
        self.setOrganizationDomain("https://github.com/AstusRush")
        self.Notification_List = []
        self._init_NCF()
        self._MakeAGeLibPath()
        ###########################
        #TODO: Load Settings like standard palette and font
        #self.Palette , self.BG_Colour , self.TextColour = AGeColour.Dark()
        #self.colour_Pack = (self.Palette , self.BG_Colour , self.TextColour)
        self.Colour_Font_Init()
        self.ModuleVersions = "Python %s\nAGeLib %s\nSymPy %s\nNumpy %s\nMatplotLib %s\nPyQt %s (Qt %s)" % ("%d.%d" % (sys.version_info.major, sys.version_info.minor),
                version,
                sympy.__version__,
                numpy_version,
                matplotlib.__version__,
                QtCore.PYQT_VERSION_STR, QtCore.qVersion())
        
        self.r_init_Options()

    def setMainWindow(self, TheWindow):
        """
        This method allows you to declare the primary window of your application.   \n
        You can use ``self.MainWindow`` to access it.   \n
        Setting a main window is not obligatory and does nothing on its own.   \n
        The intention behind declaring a main window is to make the code more readable
        and to provide a convenient way to refer to it.   \n
        This can also be useful if a function needs to access the main window in an application where the main window changes.
        """
        self.MainWindow = TheWindow
    
    #def notify(self, obj, event): # Reimplementation of notify that does nothing other than redirecting to normal implementation for now...
        #try:
        #    return super().notify(obj, event)
        #except:
        #    ExceptionOutput(sys.exc_info())
        #    print("Caught: ",obj,event)
        #    return False
    
    def eventFilter(self, source, event):
        if event.type() == 6 and self.enableHotkeys: # QtCore.QEvent.KeyPress
            if event.key() == QtCore.Qt.Key_F12:
                if self.AGeLibPathOK:
                    name = self.applicationName()
                    nameValid = ""
                    for i in name:
                        if i in string.ascii_letters + string.digits + "~ -_.":
                            nameValid += i
                    nameValid = nameValid.replace(" ","")
                    Filename = nameValid + "-" + cTimeFullStr("-") + ".png"
                    Filename = os.path.join(self.ScreenshotFolderPath,Filename)
                    try:
                        try:
                            WID = source.window().winId()
                            screen = source.window().screen()
                        except:
                            WID = source.winId()
                            screen = source.screen()
                        screen.grabWindow(WID).save(Filename)
                        print(Filename)
                    except:
                        NC(msg="Could not save Screenshot",exc=sys.exc_info(),func="Main_App.eventFilter",input=Filename)
                    else:
                        NC(3,"Screenshot of currently active window saved as:\n"+Filename,func="Main_App.eventFilter",input=Filename)
                else:
                    print("Could not save Screenshot: Could not validate save location")
                    NC(1,"Could not save Screenshot: Could not validate save location",func="Main_App.eventFilter",input=self.AGeLibPath)
                return True
            if event.modifiers() == ControlModifier:
                if event.key() == QtCore.Qt.Key_0: # FEATURE: HelpWindow: Inform the User that this feature exists. Make Help window that is opened with F1
                    for w in self.topLevelWidgets():
                        if w.isVisible():
                            w.positionReset()
                    return True
                if event.key() == QtCore.Qt.Key_T:
                    self.Show_exec_Window()
                    return True
            if event.modifiers() == AltModifier:
                if event.key() == QtCore.Qt.Key_A:
                    self.ToggleAdvancedMode(not self.advanced_mode)
                    return True
                elif event.key() == QtCore.Qt.Key_O:
                    self.Show_Options()
                    return True
        elif event.type() == NotificationEvent.EVENT_TYPE:
            self._NotifyUser(event.N)
            return True
        return super(Main_App, self).eventFilter(source, event)

    def _SaveClipboard(self):
        """
        On MS Windows this method ensures that the clipboard is kept:\n
        The contents of the clipboard are only stored as references.
        When you copy text from an application it can be pasted in all other applications
        but as soon as you close the application the reference is no longer valid and the clipboard is empty.  \n
        Note: This is not a problem if the user has a clipboard manager as they don't use references but instead copy the data.  \n
        On MS Windows this method writes the text into the clipboard.
        On other platforms it gives the clipboard manager an additional chance to copy the data.  \n
        This method is called automatically when the application exits and does not need to be called manually
        except if you expect your program to crash regularly and want to ensure that the clipboard is not lost
        on systems that have no active clipboard manager.
        """
        clipboard = Qt.QApplication.clipboard()
        if platform.system() == 'Windows':
            try:
                import win32clipboard
                text = clipboard.text()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()
            except:
                print("Could not save clipboard data:")
                ExceptionOutput(sys.exc_info())
        else: #FEATURE: Find a linux version of win32clipboard
            print("Clipboard is only saved if a clipboard manager is installed due to OS limitations.")
            event = QtCore.QEvent(QtCore.QEvent.Clipboard)
            Qt.QApplication.sendEvent(clipboard, event)
            self.processEvents()
            
    def ToggleAdvancedMode(self, checked):
        """
        This function changes the state of the advanced mode to ``checked``.   \n
        ``S_advanced_mode_changed`` is emitted and the checkbox ``AdvancedCB`` of all ``TopBar_Widget``'s is updated. \n
        Do not change ``advanced_mode`` manually!!! Always use this function!
        """
        try:
            self.advanced_mode = checked
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeAdvancedCB:
                        i.AdvancedCB.setChecked(self.advanced_mode)
            self.S_advanced_mode_changed.emit(self.advanced_mode)
        except:
            NC(1,"Exception while toggling advanced mode",exc=sys.exc_info(),func="Main_App.ToggleAdvancedMode",input="{}: {}".format(str(type(checked)),str(checked)))

 # ---------------------------------- Colour and Font ----------------------------------
    def Recolour(self, Colour = "Dark"):
        """
        Applies a colour scheme:   \n
        This method takes the name (string) of a colour scheme. \n
        First AGeColour (standard AGeLib colours) and CustomColourPalettes (user created colours) are (re-)imported and their dictionaries are loaded. \n
        Then the AGeColour dict is searched for the name. If it is not found the dict of CustomColourPalettes is searched. AppPalettes is searched last.  \n
        As soon as the name is found the colourpalette is applied (by calling _Recolour). \n
        Please note: \n
        If you have code that needs to run after the palette has changed (like applying colours to specific widgets) reimplement ``r_Recolour``. \n
        ``r_Recolour`` is called by ``_Recolour`` after the new palette has been applied. \n
        Furthermore the signal ``S_ColourChanged`` is emitted after ``_Recolour``. \n
        To add custom colour palettes for your application use the method ``AddPalette``. \n \n
        COLOURS
        ===========
        + ``Palette1``, ``Palette2`` and ``Palette3`` and full QPalettes that can be used to colour different ports of the UI. Use ``r_Recolour`` to apply these Palettes to widgets.
        ``Palette`` is deprecated and only accessible for compatibility reasons! It will be removed in future versions!
        + ``BG_Colour`` and ``TextColour`` can be used to colour different parts that are incompatible with QPalettes.
        These are tuples with 3 floats between 0 and 1 that specify RGB values and are taken from the Base and Text colours from Palette1.
        + ``PenColours`` is a dict containing QBrushes. Use ``.color()`` to access the QColor.
        The colours in this dict are visually distinct from the background (and don't necessarily correspond to their name).
        These colours should be used for graphs (and are automatically set as the numpy colour cycle), pen colours for editors,
        player colours for games and all other cases where visually distinct colours are needed.
        + ``NotificationColours`` is a dict that contains the colours for the notification flashes but can also be used for similar purposes like highlighting text.
        + ``MiscColours`` is a dict for all other colour needs. It contains some basic colours that are labelled for games but I encourage creative interpretation!
        The colours that are labelled for rarity for example could also be used to colourcode a dataset regarding the importance of the values:
        Common values are coloured as common and rare values that need attention are coloured as rare. \n

        These dicts are subclassed to ensure that a bracket access (dict["key"]) on an invalid key returns a random colour instead of raising an exception to allow expansion.
        However it is not advisable to expand these dicts at the moment. This colour system is still WIP and might change in the future.
        """
        try:
            try:
                importlib.reload(AGeColour)
            except:
                NC(2,"Could not reload AGeColour",exc=sys.exc_info(),func="Main_App.Recolour",input=str(Colour))
            try:
                spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(self.AGeLibSettingsPath,"CustomColourPalettes.py"))
                CustomColours = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(CustomColours)
                #CustomColours.MyClass()
            except:
                NC(4,"Could not load custom colours",exc=sys.exc_info(),func="Main_App.Recolour",input=str(Colour))
            try:
                self._Recolour(*AGeColour.Colours[Colour]())
            except:
                try:
                    self._Recolour(*CustomColours.Colours[Colour]())
                except:
                    self._Recolour(*self.AppPalettes[Colour]())
        except:
            NC(1,"Exception while loading colour palette",exc=sys.exc_info(),func="Main_App.Recolour",input=str(Colour))
            
    def AddPalette(self, name, palette):
        """
        Use this method to add custom colour palettes. (They are saved in the dict ``AppPalettes``.) \n
        ``name`` should be a string and ``palette`` must be a function that returns the palette. \n
        Please note that the users custom colours take priority over application palettes
        thus you need to add a tag in front of your names that no user would ever use
        (for example your application name in square brackets (like ``[AMaDiA] Dark``)). \n
        The tag must be unique enough to ensure that no user would ever use it in a custom name!
        """
        self.AppPalettes[name] = palette
            
    def _Recolour(self, Palette1, Palette2, Palette3, PenColours, NotificationColours, MiscColours):
        """
        This method is called by ``Recolour`` to apply the colour palette. \n
        For all colour palette changes ``Recolour`` should be used. \n
        If you have code that needs to run after the palette has changed (like applying colours to specific widgets) reimplement ``r_Recolour``.
        """
        self.Palette = Palette1 #TODO: Remove self.Palette
        self.Palette1 = Palette1
        self.Palette2 = Palette2
        self.Palette3 = Palette3
        self.PenColours = ColourDict()
        self.PenColours.copyFromDict(PenColours)
        self.NotificationColours = ColourDict()
        self.NotificationColours.copyFromDict(NotificationColours)
        self.MiscColours = ColourDict()
        self.MiscColours.copyFromDict(MiscColours)
        Colour = self.Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base)
        self.BG_Colour = (Colour.red()/255,Colour.green()/255,Colour.blue()/255)
        Colour = self.Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text)
        self.TextColour = (Colour.red()/255,Colour.green()/255,Colour.blue()/255)
        self.colour_Pack = (self.Palette , self.BG_Colour , self.TextColour) #TODO: remove self.colour_Pack
        self.setPalette(self.Palette)
        QtWidgets.QToolTip.setPalette(self.Palette)
        self._update_NCF()
        
        c=[]
        for v in self.PenColours.values():
            c.append(v.color().name(0))
        self.mplCycler = matplotlib.cycler(color=c) 
        matplotlib.rcParams['axes.prop_cycle'] = self.mplCycler

        for w in self.topLevelWidgets():
            for i in w.findChildren(MplWidget):
                i.SetColour(self.BG_Colour, self.TextColour, self.mplCycler)
            #for i in w.findChildren(Window_Frame_Widget):
            #    i.setPalette(FramePalette)
        self.r_Recolour()
        self.S_ColourChanged.emit()
        
    def r_Recolour(self):
        """
        This method is called after the colour palette has changed.   \n
        All GUI elements usually use the palette of the application but if the method ``setPalette`` is called
        the element looses the ability to inherit from the Application and needs special treatment.   \n
        Reimplement this method to provide such special treatment. \n
        For example ``Palette2`` and ``Palette3`` should only be applied to widgets in this method! \n
        Furthermore everything that uses ``PenColours``, ``NotificationColours`` or ``MiscColours`` should be updated here or by connecting a custom function to ``S_ColourChanged``.
        """
        pass
    
    def Colour_Font_Init(self):
        # TODO: Accept more arguments for FontFamily, PointSize and colour Palette Name and use defaults if none were given or if something went wrong while applying them
        self.FontFamily = "Arial"
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.setFont(font)
        self.Recolour()

        # Always keep Statusbar Font small
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        for w in self.topLevelWidgets():
            for i in w.findChildren(QtWidgets.QStatusBar):
                try:
                    i.setFont(font)
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())

    def SetFont(self, Family=None, PointSize=0, source=None, emitSignal=True):
        """
        Changes the font to ``Family`` and the font size to ``PointSize`` for the entire application.  \n
        ``Family``: QFont, string or None (None keeps old family and only changes font size)  \n
        ``PointSize``: int, if 0 ans ``Family`` is QFont the pointsize of QFont is used. \n
        ``source`` : The window from which the font was changed  \n
        If ``PointSize`` is less than 5 the value from the Font_Size_spinBox of ``source`` will be taken. If this fails it defaults to 9. \n
        ``emitSignal``: If True (default) ``S_FontChanged`` is emitted after the new font is applied. \n\n
        Furthermore the Font_Size_spinBox of all windows is updated with the new value (the signals of Font_Size_spinBox are blocked during the update).\n
        All ``TopBar_Widget``s are resized. \n
        The fontsize of all statusbars is always kept at 9 but the font family is updated.
        """
        if type(Family) == QtGui.QFont:
            if PointSize==0:
                PointSize = Family.pointSize()
            Family = Family.family()
            self.FontFamily = Family
        elif Family == None:
            Family = self.FontFamily
        else:
            self.FontFamily = Family
        if type(PointSize) == str:
            PointSize = int(PointSize)
        if PointSize < 5:
            try:
                PointSize = source.TopBar.Font_Size_spinBox.value()
            except common_exceptions:
                try:
                    NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="Main_App.SetFont",win=source.windowTitle())
                except common_exceptions:
                    NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="Main_App.SetFont")
                PointSize = 9
        if type(PointSize) != int:
            print(type(PointSize)," is an invalid type for font size (",PointSize,")")
            try:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="Main_App.SetFont",win=source.windowTitle())
            except:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="Main_App.SetFont")
            PointSize = 9
                
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                try:
                    if i.IncludeFontSpinBox:
                        # setValue emits ValueChanged and thus calls ChangeFontSize if the new Value is different from the old one.
                        # If the new Value is the same it is NOT emitted.
                        # To ensure that this behaves correctly either way the signals are blocked while changing the Value.
                        i.Font_Size_spinBox.blockSignals(True)
                        i.Font_Size_spinBox.setValue(PointSize)
                        i.Font_Size_spinBox.blockSignals(False)
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
        
        font = QtGui.QFont()
        font.setFamily(Family)
        font.setPointSize(PointSize)
        self.setFont(font)
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                try:
                    if type(i.parentWidget()) == MMenuBar:
                        i.setMinimumHeight(i.parentWidget().minimumHeight())
                    elif type(i.parentWidget()) == QtWidgets.QTabWidget:
                        i.setMinimumHeight(i.parentWidget().tabBar().minimumHeight())
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
        # Always keep Statusbar Font small
        font = QtGui.QFont()
        font.setFamily(Family)
        font.setPointSize(9)
        for w in self.topLevelWidgets():
            for i in w.findChildren(QtWidgets.QStatusBar):
                try:
                    i.setFont(font)
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
        if emitSignal:
            self.S_FontChanged.emit()

 # ---------------------------------- Notifications ----------------------------------

    def _init_NCF(self): # Notification_Flash
        """
        NO INTERACTION NEEDED \n
        Initiates the notification flash animations. This method is called automatically.
        """
        self.NCF_NONE = QtCore.QPropertyAnimation(self)
        
        self.NCF_r = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_r.setDuration(1000)
        self.NCF_r.setLoopCount(1)
        #self.NCF_r.finished.connect(self._NCF_Finished)
        
        self.NCF_y = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_y.setDuration(1000)
        self.NCF_y.setLoopCount(1)
        #self.NCF_y.finished.connect(self._NCF_Finished)
        
        self.NCF_g = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_g.setDuration(1000)
        self.NCF_g.setLoopCount(1)
        #self.NCF_g.finished.connect(self._NCF_Finished)
        
        self.NCF_b = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_b.setDuration(1000)
        self.NCF_b.setLoopCount(1)
        #self.NCF_b.finished.connect(self._NCF_Finished)

    def _update_NCF(self):
        """
        NO INTERACTION NEEDED \n
        Updates the notification flash animations. This method is called automatically.
        """

        self.NCF_r.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setKeyValueAt(0.5, self.NotificationColours["Error"].color())
        
        self.NCF_y.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setKeyValueAt(0.5, self.NotificationColours["Warning"].color())
        
        self.NCF_g.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setKeyValueAt(0.5, self.NotificationColours["Message"].color())
        
        self.NCF_b.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setKeyValueAt(0.5, self.NotificationColours["Notification"].color())

    def _set_FLASH_colour(self, col): # Handles changes to the Property FLASH_colour
        """
        NO INTERACTION NEEDED \n
        Helpfunction that handles changes to the Property FLASH_colour.
        """
        palette = self.Palette
        palette.setColor(QtGui.QPalette.Window, col)
        self.setPalette(palette)
    FLASH_colour = QtCore.pyqtProperty(QtGui.QColor, fset=_set_FLASH_colour) # Defines the Property FLASH_colour
    
    #def _NCF_Finished(self):
    #    """
    #    This method is called when a notification flash animation is finished. \n
    #    """
    #    pass#self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.NoFrame)

    def _NotifyUser(self, N):
        """
        NO INTERACTION NEEDED \n
        Displays the notification ``N`` to the user. \n
        This method should not be used manually!
        """
        if N.l() == 0:
            return
        elif N.l()!=4 or self.advanced_mode:
            Error_Text_TT,icon = self._ListVeryRecentNotifications(N)
            self.LastNotificationText = N.DPS()
            self.LastNotificationToolTip = Error_Text_TT
            self.LastNotificationIcon = icon
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeErrorButton:
                        i.Error_Label.setText(N.DPS())
                        i.Error_Label.setToolTip(Error_Text_TT)
                        i.Error_Label.setIcon(icon)
            if (not N.Flash == self.NCF_NONE) and (not N.Flash == None):
                N.Flash.start()
        
        self.Notification_List.append(N)
        self.S_New_Notification.emit(N)
        # Allow the button to adjust to the new text:
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                if i.IncludeErrorButton:
                    i.parentWidget().adjustSize()
        # REMINDER: Somewhere you need to make the error message "Sorry Dave, I can't let you do this."
        
    def _ListVeryRecentNotifications(self, N):
        """
        NO INTERACTION NEEDED \n
        This helpfunction is used by _NotifyUser to generate the tooltip for the notification button.
        """
        cTime = time.time()
        Error_Text_TT = N.TTS()
        level = N.l()
        icon = N.icon
        for i in range(len(self.Notification_List)):
            if i< 10 and cTime - self.Notification_List[-i-1]._time_time < 2 and len(Error_Text_TT.splitlines())<40:
                if self.Notification_List[-i-1].l()!=0 and (self.Notification_List[-i-1].l()!=4 or self.advanced_mode):
                    Error_Text_TT += "\n\n"
                    Error_Text_TT += str(self.Notification_List[-i-1])
                    cTime = self.Notification_List[-i-1]._time_time
                    if level > self.Notification_List[-i-1].l():
                        level = self.Notification_List[-i-1].l()
                        icon = self.Notification_List[-i-1].icon
            else:
                break
        return (Error_Text_TT,icon)

 # ---------------------------------- SubWindows ----------------------------------

    def r_init_Options(self):
        """
        This method initializes the standard options window and is called automatically. \n
        If you want a custom options window reimplement this method with the following code:\n
        ```python
        self.optionWindow = Custom_Options_Window()
        ```
        and replace ``Custom_Options_Window`` with your own class that is derived from AWWF. \n
        Your custom options window should include the widget ``OptionsWidget_1_Appearance``!!!
        """
        self.optionWindow = Options_Window()
    
    def Show_Notification_Window(self):
        """
        Shows a window that lists all notifications and displays their details. \n
        Default access: pressing the notification button
        """
        if self.Notification_Window == None:
            self.Notification_Window = Notification_Window()
        self.Notification_Window.show()
        self.processEvents()
        self.Notification_Window.positionReset()
        self.processEvents()
        self.Notification_Window.activateWindow()

    def Show_exec_Window(self):
        """
        Shows a window that can execute code within the program. (This window is very useful for debugging) \n
        Default shortcut (applicationwide): ctrl+T
        """
        if self.exec_Window == None:
            self.exec_Window = exec_Window()
        self.exec_Window.show()
        self.processEvents()
        self.exec_Window.positionReset()
        self.processEvents()
        self.exec_Window.activateWindow()

    def Show_Options(self):
        """
        Shows the options window. \n
        Default shortcut (applicationwide): alt+O
        """
        self.optionWindow.show()
        self.optionWindow.activateWindow()

 # ---------------------------------- Other ----------------------------------

    def _MakeAGeLibPath(self):
        """
        NO INTERACTION NEEDED \n
        This method creates/finds/validates the path to the AGeLib config directory.
        """
        self.AGeLibPathOK = False
        self.AGeLibPath = False
        self.AGeLibSettingsPath = False
        self.ScreenshotFolderPath = False
        try:
            self.AGeLibPath = os.path.join(os.path.expanduser("~"),"AGeLib")
            os.makedirs(self.AGeLibPath,exist_ok=True)
            #
            self.AGeLibSettingsPath = os.path.join(self.AGeLibPath,"Settings")#ProgramFiles
            os.makedirs(self.AGeLibSettingsPath,exist_ok=True)
            FileName = os.path.join(self.AGeLibSettingsPath,"CustomColourPalettes.py")
            with open(FileName,'a',encoding="utf-8") as text_file:
                pass
            if os.stat(FileName).st_size == 0:
                with open(FileName,'w',encoding="utf-8") as text_file:
                    text_file.write(r"Colours={}")
            # Create Screenshots folder
            self.ScreenshotFolderPath = os.path.join(self.AGeLibPath,"Screenshots")
            os.makedirs(self.ScreenshotFolderPath,exist_ok=True)
            #
            self.ProgramFilesFolderPath = os.path.join(self.AGeLibPath,"ProgramFiles")
            os.makedirs(self.ProgramFilesFolderPath,exist_ok=True)
            #
            self.AGeLibPathOK = True
        except:
            NC(1,"Could not create/validate AGeLib folder",exc=sys.exc_info())
        try:
            self.r_CreateFolders()
        except:
            NC(1,"Could not create/validate program specific folders",exc=sys.exc_info())

    def r_CreateFolders(self):
        """
        This Function is called automatically at the end of ``_MakeAGeLibPath`` which is called by the ``__init__``. \n
        Reimplement this function to create folders. \n
        It is recommended to create a program specific folder in ``self.AGeLibPath``. \n
        Example:\n
        ```python
        self.Folder = os.path.join(self.AGeLibPath,"PROGRAM_NAME")
        os.makedirs(self.Folder,exist_ok=True)
        ```
        """
        pass
#endregion

#region Widgets
#FEATURE: Make a more performant Plotter Widget using pyqtgraph. This boost in performance should allow plot interactions. See https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/
#FEATURE: All plot widgets should be able to give the coordinates of the mouse cursor to make them easier to read. (This should be toggleable to not interfere with other interactions.)
#MAYBE: Make a plotting widget that can take in any lists and make a plot. This specifically means detecting the dimensions and making a 2D or 3D plot depending on the input
#FEATURE: Make a more performant LaTeX Widget

#LaTeX Widget:
#import sys
#from PyQt5.QtWebEngineWidgets import QWebEngineView
#
#pageSource = r"""
#             <html><head>
#             <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
#             </script></head>
#             <body bgcolor=" """+str(App().palette().base().color().name(0))+r""" ">
#             <p><mathjax style="font-size:2.3em; color: """+str(App().palette().text().color().name(0))+r"""">$$\displaystyle \frac{2 \cdot 3 \int \left(x + 2 x\right)\, dx}{6} $$</mathjax></p>
#             </body></html>
#             """
#self.webWindow = AWWF()
#self.webView = QWebEngineView()
#self.webView.setHtml(pageSource)
##self.webView.setUrl(QtCore.QUrl("https://www.google.com"))
#self.webWindow.setCentralWidget(self.webView)
#self.webWindow.show()

class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MplWidget, self).__init__(parent)
        self.background_Colour = QtWidgets.QApplication.instance().BG_Colour
        self.TextColour = QtWidgets.QApplication.instance().TextColour
        self.Cycler = QtWidgets.QApplication.instance().mplCycler

    def SetColour(self,BG=None,FG=None,Cycler=None):
        if BG!=None:
            self.background_Colour = BG
        if FG!=None:
            self.TextColour = FG
        if type(Cycler)!=None:
            self.Cycler = Cycler
        self.HexcolourText = '#%02x%02x%02x' % (int(self.TextColour[0]*255),int(self.TextColour[1]*255),int(self.TextColour[2]*255))
        try:
            self.canvas.fig.set_facecolor(self.background_Colour)
            self.canvas.fig.set_edgecolor(self.background_Colour)
            self.canvas.ax.set_facecolor(self.background_Colour)
            self.canvas.ax.set_prop_cycle(self.Cycler)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
        try:
            self.canvas.draw()
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

    #def eventFilter(self, source, event):
    #    if event.type() == QtCore.QEvent.PaletteChange:
    #        try:
    #            source.SetColour(QtWidgets.QApplication.instance().BG_Colour , QtWidgets.QApplication.instance().TextColour)
    #        except common_exceptions:
    #            ExceptionOutput(sys.exc_info())
    #    return super(MplWidget, self).eventFilter(source, event)

# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_2D_Plot(Canvas):
    def __init__(self):
        #plt.style.use('dark_background')
        self.fig = Figure(constrained_layout =True)
        self.fig.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        Canvas.updateGeometry(self)

class MplWidget_2D_Plot(MplWidget):
    # Inspired by https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5?noredirect=1&lq=1 from 10.07.2019
    def __init__(self, parent=None):
        super(MplWidget_2D_Plot, self).__init__(parent)
        self.canvas = MplCanvas_2D_Plot()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.layout().setContentsMargins(0,0,0,0)
        
    def SetColour(self,BG=None,FG=None,Cycler=None):
        super(MplWidget_2D_Plot, self).SetColour(BG,FG,Cycler)
        self.canvas.ax.spines['bottom'].set_color(self.TextColour)
        self.canvas.ax.spines['left'].set_color(self.TextColour)
        self.canvas.ax.xaxis.label.set_color(self.TextColour)
        self.canvas.ax.yaxis.label.set_color(self.TextColour)
        self.canvas.ax.tick_params(axis='x', colors=self.TextColour)
        self.canvas.ax.tick_params(axis='y', colors=self.TextColour)
        self.canvas.draw()
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']

# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_LaTeX(Canvas):
    def __init__(self,w,h):
        #plt.style.use('dark_background')
        #self.fig = Figure(constrained_layout =True)
        self.fig = Figure(figsize = (w,h),dpi=90)
        self.fig.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        #h = [Size.Fixed(1.0), Size.Fixed(4.5)]
        #v = [Size.Fixed(0.7), Size.Fixed(5.)]
        #divider = Divider(self.fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
        
        self.ax = self.fig.add_subplot(111)
        #self.ax = Axes(self.fig, divider.get_position())
        
        self.ax.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        self.ax.set_anchor('W')
        self.fig.subplots_adjust(left=0.01)
        self.ax.axis('off')
        
        #self.ax.set_axes_locator(divider.new_locator(nx=1, ny=1))
        #self.fig.add_axes(self.ax)
        
        Canvas.__init__(self, self.fig)
        #Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        #Canvas.updateGeometry(self)

class MplWidget_LaTeX(MplWidget):
    def __init__(self, parent=None):
        super(MplWidget_LaTeX, self).__init__(parent)
        self.canvas = MplCanvas_LaTeX(1,1)                  # Create canvas object
        #self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        #self.vbl.addWidget(self.canvas)
        #self.setLayout(self.vbl)
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidget(self.canvas)
        
        #self.Tab_2_LaTeX_LaTeXOutput.nav = NavigationToolbar(self.Tab_2_LaTeX_LaTeXOutput.canvas, self.Tab_2_LaTeX_LaTeXOutput)
        #self.Tab_2_LaTeX_LaTeXOutput.layout().addWidget(self.Tab_2_LaTeX_LaTeXOutput.nav)
        self.layout().addWidget(self.scroll)
        self.layout().setContentsMargins(0,0,0,0)
        
        self.LastCall = False
        self.LaTeX = ""
        
        self.ContextMenu_cid = self.canvas.mpl_connect('button_press_event', self.Context_Menu)
        
        
    def Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            menu = self.add_context_action(menu)
            cursor = QtGui.QCursor()
            menu.setPalette(self.palette())
            menu.setFont(self.font())
            menu.exec_(cursor.pos())
    
    def add_context_action(self,menu):
        """Adds standard actions to menu and return menu"""
        action = menu.addAction('Copy LaTeX')
        action.triggered.connect(self.action_Copy_LaTeX)
        action = menu.addAction('Copy LaTeX (with format)')
        action.triggered.connect(self.action_Copy_LaTeX_L)
        return menu
    
    def action_Copy_LaTeX(self):
        try:
            Qt.QApplication.clipboard().setText(self.LaTeX)
        except common_exceptions:
            NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX")
    
    def action_Copy_LaTeX_L(self):
        try:
            Qt.QApplication.clipboard().setText(self.LaTeX_L)
        except common_exceptions:
            NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX_L")
        
    def SetColour(self,BG=None,FG=None,Cycler=None):
        super(MplWidget_LaTeX, self).SetColour(BG,FG,Cycler)
        if self.LastCall != False:
            self.DisplayRaw(self.LastCall[0],self.LastCall[1],self.LastCall[2],self.LastCall[3])
        else:
            try:
                self.canvas.draw()
            except common_exceptions:
                pass
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']

    def PreloadLaTeX(self):
        try:
            self.UseTeX(True)
            self.canvas.ax.clear()
            self.canvas.ax.set_title(r"$\frac{2 \cdot 3 \int \left(x + 2 x\right)\, dx}{6}$",
                        loc = "left",
                        y=(1.15-(20/5000)),
                        horizontalalignment='left',
                        verticalalignment='top',
                        fontsize=20,
                        color = "white"
                        ,bbox=dict(boxstyle="round", facecolor="black",
                        ec="0.1", pad=0.1, alpha=0)
                        )
            self.canvas.ax.axis('off')
            self.canvas.draw()
            time.sleep(0.1)
            self.canvas.ax.clear()
            self.canvas.ax.axis('off')
            self.canvas.draw()
            self.UseTeX(False)
        except common_exceptions:
            try:
                self.UseTeX(False)
            except common_exceptions:
                ExceptionOutput(sys.exc_info())
            ExceptionOutput(sys.exc_info())
    
    def Display(self, Text, Font_Size = None, Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        #SIMPLIFY: https://matplotlib.org/3.1.1/_modules/matplotlib/text.html#Text _get_rendered_text_width and similar
        # Use this to adjust the size of the "plot" to the Text?
        
        # Reminder: You can set Usetex for each individual text object. Example:
        # plt.xlabel('$x$', usetex=True)
        
        self.LaTeX = Text
        
        #return self.DisplayRaw(r"$\displaystyle " + self.LaTeX + "$", "$" + self.LaTeX + "$", Font_Size=Font_Size,Use_LaTeX=Use_LaTeX)
        
        Lines_L = self.LaTeX.splitlines()
        Lines_N = self.LaTeX.splitlines()
        #for i in Lines_L:
        #    #if i == "":
        #    #    i = 
        #    i = r"$\displaystyle " + i + "$"
        Text_L = r" \begin{alignat*}{2} & " + r" \\ & ".join(Lines_L) + r" \end{alignat*}  "
        #Text_L = r" \begin{align*} " + r" \\ & ".join(Lines_L) + r" \end{align*}  "
        #Text_L = r" \\ ".join(Lines_L)
        Text_N = "$" + "$\n$".join(Lines_N) + "$"
        return self.DisplayRaw(Text_L, Text_N, Font_Size=Font_Size,Use_LaTeX=Use_LaTeX)
        
    def DisplayRaw(self, Text_L, Text_N, Font_Size = None, Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        if Font_Size == None:
            Font_Size = App().font().pointSize()
        self.LastCall = [Text_L, Text_N, Font_Size, Use_LaTeX]
        self.LaTeX_L = Text_L
        self.LaTeX_N = Text_N
        self.Font_Size = Font_Size * 2
        Notification = NC(lvl=0,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
        
        if Use_LaTeX:
            self.UseTeX(True)
            self.Text = self.LaTeX_L
        else:
            self.UseTeX(False)
            try:
                self.Text = self.LaTeX_N.replace(r"\limits","")
            except:
                self.Text = self.LaTeX_N
        
        #self.w=9
        #self.h=9
        #self.canvas = MplCanvas_LaTeX(self.w+1, self.h+1) 
        #self.scroll.setWidget(self.canvas)
        #self.layout().addWidget(self.scroll)
        #self.canvas.resize(self.w+1, self.h+1)
        #self.canvas.__init__(self.w+1, self.h+1)
        
        try:
            self._Display(self.Text)
        except common_exceptions:
            Notification = NC(4,"Could not display in Mathmode",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display",send=False)
            self.Text = self.LaTeX_N
            if Use_LaTeX:
                self.UseTeX(True)
            else:
                self.UseTeX(False)
            try:
                self._Display(self.Text)
            except common_exceptions:
                Notification = NC(2,"Could not display with LaTeX. Displaying with matplotlib instead.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display",send=False)
                try:
                    self.Text = self.LaTeX_N.replace(r"\limits","")
                except:
                    self.Text = self.LaTeX_N
                self.UseTeX(False)
                try:
                    self._Display(self.Text)
                except common_exceptions:
                    Notification = NC(1,"Could not display at all.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display",send=False)
                    self.UseTeX(False)
                    if Use_LaTeX:
                        ErrorText = "The text can't be displayed. Please send your input and a description of your problem to the developer"
                    else:
                        ErrorText = "The text can't be displayed. Please note that many things can't be displayed without LaTeX Mode."
                        if not LaTeX_dvipng_Installed:
                            ErrorText += "\n Please install LaTeX (and dvipng if it is not already included in your LaTeX distribution)"
                    try:
                        self._Display(ErrorText)
                    except common_exceptions:
                        Notification = NC(1,"Critical Error: MatPlotLib Display seems broken. Could not display anything",exc=sys.exc_info(),input=ErrorText,win=self.window().windowTitle(),func=str(self.objectName())+".Display",send=False)
        finally:
            self.UseTeX(False)
            return Notification

    def _Display(self,text):
        self.canvas.ax.clear() # makes Space for the new text
        y = 1.15-(self.Font_Size/5000) # For Figure(figsize = (100,100),dpi=90)
        #y = 1.195-(self.Font_Size/180) # For Figure(figsize = (100,10),dpi=90)
        t = self.canvas.ax.set_title(text,
                                    loc = "left",
                                    #x=-0.12,
                                    y=y,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    fontsize=self.Font_Size,
                                    color = self.TextColour
                                    ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,ec="0.1", pad=0.1, alpha=0)
                                    )
        #
        r = self.canvas.get_renderer()
        #t = self.canvas.ax.get_title()
        bb = t.get_window_extent(renderer=r)

        #NC(10,str(self.canvas.fig.dpi_scale_trans.inverted().transform((bb.width,bb.height))))
        x,y = self.canvas.fig.dpi_scale_trans.inverted().transform((bb.width,bb.height))+self.canvas.fig.dpi_scale_trans.inverted().transform((0,y))
        self.canvas.fig.set_size_inches(x+0.4,y+1, forward=True)
        self.canvas.ax.clear()
        t = self.canvas.ax.set_title(text,
                                    loc = "left",
                                    x=0.1,
                                    y=y+0.5,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    fontsize=self.Font_Size,
                                    color = self.TextColour,
                                    #bbox=dict(boxstyle="round", facecolor=self.background_Colour,ec="0.1", pad=0.1, alpha=0),
                                    transform = self.canvas.fig.dpi_scale_trans#.inverted()
                                    )
        #
        self.canvas.ax.axis('off')
        self.canvas.draw()
        self.canvas.adjustSize()
        #self.scroll.adjustSize()
        #self.adjustSize()

class MplWidget_LaTeX_J(QWebEngineView,MplWidget): # TODO: New LaTeX widget WIP
    """
    This widget is WORK IN PROGRESS and should NOT be used. \n
    New updates might break compatibility without warning. \n
    Even the name of this widget will change without warning!!! \n
    It is only included here to allow an insight into the active development of this Library!
    """
    def __init__(self, parent=None):
        super(MplWidget_LaTeX_J, self).__init__(parent)
        self.canvas = MplCanvas_LaTeX(100,100) 
        self.LastCall = False
        self.LaTeX = ""
        self.ContextMenu_cid = self.canvas.mpl_connect('button_press_event', self.Context_Menu)
        
        
    def Context_Menu(self,event):
        pass
    
    def add_context_action(self,menu):
        """Adds standard actions to menu and return menu"""
        #action = menu.addAction('Copy LaTeX')
        #action.triggered.connect(self.action_Copy_LaTeX)
        return menu
    
    def action_Copy_LaTeX(self):
        #try:
        #    Qt.QApplication.clipboard().setText(self.LaTeX)
        #except common_exceptions:
        #    NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX")
        pass
        
    def SetColour(self,BG=None,FG=None,Cycler=None):
        #super(MplWidget_LaTeX, self).SetColour(BG,FG,Cycler)
        #if self.LastCall != False:
        #    self.Display(self.LastCall[0],self.LastCall[1],self.LastCall[2],self.LastCall[3])
        #else:
        #    try:
        #        self.canvas.draw()
        #    except common_exceptions:
        #        pass
        pass
    
    def UseTeX(self,TheBool):
        return TheBool

    def PreloadLaTeX(self):
        pass
    
    def Display(self, Text, Font_Size = None, Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        #SIMPLIFY: https://matplotlib.org/3.1.1/_modules/matplotlib/text.html#Text _get_rendered_text_width and similar
        # Use this to adjust the size of the "plot" to the Text?
        
        # Reminder: You can set Usetex for each individual text object. Example:
        # plt.xlabel('$x$', usetex=True)
        
        self.LaTeX = Text
        
        #return self.DisplayRaw(r"$\displaystyle " + self.LaTeX + "$", "$" + self.LaTeX + "$", Font_Size=Font_Size,Use_LaTeX=Use_LaTeX)
        
        Lines_L = self.LaTeX.splitlines()
        Lines_N = self.LaTeX.splitlines()
        for i in Lines_L:
            #if i == "":
            #    i = 
            i = r"$\displaystyle " + i + "$"
        for i in Lines_N:
            i = "$" + i + "$"
        Text_L = r" \begin{alignat*}{2} & " + r" \\ & ".join(Lines_L) + r" \end{alignat*}  "
        #Text_L = r" \begin{align*} " + r" \\ & ".join(Lines_L) + r" \end{align*}  "
        #Text_L = r" \\ ".join(Lines_L)
        Text_N = r" \\ ".join(Lines_N)
        return self.DisplayRaw(Text_L, Text_N, Font_Size=Font_Size,Use_LaTeX=Use_LaTeX)
        
    def DisplayRaw(self,Text_L,Text_N,Font_Size,Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        self.LastCall = [Text_L, Text_N, Font_Size, Use_LaTeX]
        self.LaTeX = Text_L
        self.Text = Text_L
        self.Font_Size = Font_Size * 2
        Notification = NC(lvl=0,win=self.window().windowTitle(),func=str(self.objectName())+".Display",send=False)
        #-----------IMPORTANT-----------
        pageSource = r"""
                     <html><head>
                     <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                     </script></head>
                     <body bgcolor=" """+str(App().Palette1.base().color().name(0))+r""" ">
                     <p><mathjax style="font-size:2.3em; color: """+str(App().palette().text().color().name(0))+r"""">$"""+Text_L+r"""$</mathjax></p>
                     </body></html>
                     """
        self.setHtml(pageSource)
        return Notification

# -----------------------------------------------------------------------------------------------------------------

class ListWidget(QtWidgets.QListWidget):
    """
    The base class for list widgets of AGeLib. \n
    QtGui.QKeySequence.Copy has been reimplemented to allow copying of multiple items. (Text of items is separated by linebreaks.) \n
    The scrollmode is set to ScrollPerPixel and the selectionmode is set to ExtendedSelection.
    """
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.installEventFilter(self)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)>1:
                    string = ""
                    for i in SelectedItems:
                        string += i.text()
                        string += "\n"
                    Qt.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(ListWidget, self).keyPressEvent(event)
        except common_exceptions:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(ListWidget).keyPressEvent",input=str(event))
            super(ListWidget, self).keyPressEvent(event)

class NotificationsWidget(QtWidgets.QSplitter):
    """
    This widget displays all notifications and allows (read)access to their details. \n
    All previous notifications are automatically loaded and all new notifications are automatically added
    """
    def __init__(self, parent=None):
        super(NotificationsWidget, self).__init__(parent)
        #sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(20)
        #sizePolicy.setHeightForWidth(self.Splitter.sizePolicy().hasHeightForWidth())
        #self.Splitter.setSizePolicy(sizePolicy)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.NotificationList = NotificationListWidget(self)
        self.NotificationInfo = NotificationInfoWidget(self)
        self.NotificationList.setObjectName("NotificationList")
        self.NotificationInfo.setObjectName("NotificationInfo")
        
        App().S_New_Notification.connect(self.AddNotification)
        for i in App().Notification_List:
            self.AddNotification(i)
        
        self.NotificationList.currentItemChanged.connect(self.NotificationInfo.ShowNotificationDetails)

    def AddNotification(self,Notification):
        try:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(Notification))
            item.setData(100,Notification)
            item.setIcon(Notification.icon)
            
            self.NotificationList.addItem(item)
            self.NotificationList.scrollToBottom()
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            text = "Could not add notification: "+Error
            item = QtWidgets.QListWidgetItem()
            item.setText(text)
            item.setData(100,NC(1,"Could not add notification",err=Error,func=str(self.objectName())+".(NotificationsWidget).AddNotification",win=self.window().windowTitle()))
            
            self.NotificationList.addItem(item)
            self.NotificationList.scrollToBottom()

class NotificationListWidget(ListWidget):
    """
    This widget is used by NotificationsWidget to display all notifications.
    """
    def __init__(self, parent=None):
        super(NotificationListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)

class NotificationInfoWidget(ListWidget): #TODO: Add a button to copy the details of the current notification to the clipboard with a tooltip that explains how to send it to the developer
    """
    This widget is used by NotificationsWidget to display the details of the currently selected notification.
    """
    def __init__(self, parent=None):
        super(NotificationInfoWidget, self).__init__(parent)
        self.setAlternatingRowColors(True)
        self.installEventFilter(self)
        
        item = QtWidgets.QListWidgetItem()
        item.setText("For more information select a notification")
        self.addItem(item)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)>1:
                    string = ""
                    for i in SelectedItems:
                        string += i.text()
                        string += "\n\n"
                    Qt.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(NotificationInfoWidget, self).keyPressEvent(event)
        except common_exceptions:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).keyPressEvent",input=str(event))
            super(NotificationInfoWidget, self).keyPressEvent(event)

    def ShowNotificationDetails(self,Notification):
        try:
            Notification = Notification.data(100)
            self.clear()
            for k,v in Notification.items():
                try:
                    if v != None:
                        item = QtWidgets.QListWidgetItem()
                        item.setText(k+str(v))
                        self.addItem(item)
                except common_exceptions:
                    NC(msg="Could not display{}".format(str(k)),exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails")
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails")

# -----------------------------------------------------------------------------------------------------------------

class ATextEdit(QtWidgets.QTextEdit):
    """
    The base class for Texteditor of AGeLib. \n
    Includes the signals returnPressed and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set ATextEdit``.setTabChangesFocus(False)``.
    """
    returnPressed = QtCore.pyqtSignal()
    returnCtrlPressed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.installEventFilter(self)
        self.setTabChangesFocus(True)
        
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter: # Connects to returnPressed but does not accept the signal to allow linebreaks
                source.returnPressed.emit()
            if (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter) and event.modifiers() == QtCore.Qt.ControlModifier:
                source.returnCtrlPressed.emit()
            if event.key() == QtCore.Qt.Key_Up and source.textCursor().blockNumber() == 0: # Move to beginning if up key pressed and in first line
                cursor = source.textCursor()
                if event.modifiers() == QtCore.Qt.ShiftModifier: # If shift is pressed select the text
                    cursor.movePosition(cursor.Start,1)
                else:
                    cursor.movePosition(cursor.Start)
                source.setTextCursor(cursor)
                return True
            elif event.key() == QtCore.Qt.Key_Down and source.textCursor().blockNumber() == source.document().blockCount()-1: # Move to end if down key pressed and in last line
                cursor = source.textCursor()
                if event.modifiers() == QtCore.Qt.ShiftModifier: # If shift is pressed select the text
                    cursor.movePosition(cursor.End,1)
                else:
                    cursor.movePosition(cursor.End)
                source.setTextCursor(cursor)
                return True
        return super(ATextEdit, self).eventFilter(source, event)

    def text(self):
        return self.toPlainText()

    def insertFromMimeData(self, MIMEData):
        try:
            Text = MIMEData.text()
            self.textCursor().insertText(Text)
        except common_exceptions:
            pass

class TextEdit(ATextEdit):
    """
    The base multiline texteditor of AGeLib. \n
    Includes the signals returnPressed and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set TextEdit``.setTabChangesFocus(False)``.
    """
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.installEventFilter(self)

        # FEATURE: Make subscript and superscript work and add an option to disable it (fro small font)
        # See https://www.qtcentre.org/threads/38633-(SOLVED)-QTextEdit-subscripted-text for a startingpoint
        
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter) and event.modifiers() == QtCore.Qt.ControlModifier:
                source.returnCtrlPressed.emit()
                return True
        return super(TextEdit, self).eventFilter(source, event)

class LineEdit(ATextEdit):
    """
    The base single line texteditor of AGeLib. \n
    In contrast to QLineEdit, AGeLib's LineEdit supports QtGui.QSyntaxHighlighter since it is derived from QtWidgets.QTextEdit . \n
    Includes the signals returnPressed and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set TextEdit``.setTabChangesFocus(False)``. \n
    Please note that multiline text is converted to a single line in which each former line is placed in brackets and separated by plus signs.
    To change this behaviour reimplement ``.insertFromMimeData(self,Data)``.
    """
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        
        self.RowHeight = QtGui.QFontMetrics(self.font()).lineSpacing()
        self.setFixedHeight(2 * self.RowHeight)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.installEventFilter(self)
        # Connect Signals
        #self.textChanged.connect(self.validateCharacters) # Turned off to fix Undo/Redo # CLEANUP: validateCharacters

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
            source.RowHeight = QtGui.QFontMetrics(source.font()).lineSpacing()+9
            source.setFixedHeight(source.RowHeight)
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                source.returnPressed.emit()
                return True
        return super(LineEdit, self).eventFilter(source, event)

    #def validateCharacters(self): # CLEANUP: validateCharacters
     #   forbiddenChars = ['\n']
     #   cursor = self.textCursor()
     #   curPos = cursor.position()
     #   Text = self.toPlainText()
     #   found = 0
     #   for e in forbiddenChars:
     #       found += Text.count(e)
     #       Text = Text.replace(e, '')
     #   
     #   self.blockSignals(True)
     #   self.setText(Text)
     #   self.blockSignals(False)
     #   try:
     #       cursor.setPosition(curPos-found)
     #       self.setTextCursor(cursor)
     #   except common_exceptions:
     #       ExceptionOutput(sys.exc_info())
     #   super(LineEdit, self).validateCharacters()

    def insertFromMimeData(self,Data):
        if Data.hasText():
            text = Data.text()
            #text = text.replace('\n', ' + ').replace('\r', '')
            lines = []
            for i in text.splitlines():
                if i.strip() != "":
                    lines.append(i)
            if len(lines) > 1:
                text = "( "+" ) + ( ".join(lines)+" )"
            else:
                text = "".join(lines)
            self.insertPlainText(text)
            #Data.setText(text)
        else:
            super(LineEdit, self).insertFromMimeData(Data)

# -----------------------------------------------------------------------------------------------------------------

class TableWidget(QtWidgets.QTableWidget):
    """
    The base class for table widgets of AGeLib. \n
    The Navigation is changed exit the widget when tab is pressed on the last item
    and AGeLib's LineEdit is used for the cell editing (which enables the use of QtGui.QSyntaxHighlighter). \n
    Includes the signal S_Focus_Next which is emitted when tab is pressed while the last item is selected.
    This can be used to automatically redirect the focus to a specific widget which can not be reached via the use of Qt's tab stops. \n
    """
    S_Focus_Next = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        #print(type(self.itemDelegate()))
        self.TheDelegate = TableWidget_Delegate(self)
        self.setItemDelegate(self.TheDelegate)
        self.installEventFilter(self)
        
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and source in self.window().findChildren(QtWidgets.QTableWidget) and source.isEnabled() and source.tabKeyNavigation():
            index = source.currentIndex()
            if event.key() == QtCore.Qt.Key_Backtab:
                if index.row() == index.column() == 0:
                    source.setCurrentCell(0,0)
                    source.clearSelection()
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(source, False)
                    return True
            elif event.key() == QtCore.Qt.Key_Tab:
                model = source.model()
                if (index.row() == model.rowCount() - 1 and index.column() == model.columnCount() - 1):
                    source.setCurrentCell(0,0)
                    source.clearSelection()
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(source, True)
                    self.S_Focus_Next.emit()
                    return True
            elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Space:
                self.edit(index)
                return True
        return super(TableWidget, self).eventFilter(source, event)

class TableWidget_Delegate(QtWidgets.QStyledItemDelegate):
    """
    TableWidget delegate for AGeLib's TableWidget. \n
    This delegate uses AGeLib's LineEdit to enable the use of QtGui.QSyntaxHighlighter. \n
    The usual navigation (key press enters edit, enter closes edit, tab focuses next item, etc) is supported.
    """
    def __init__(self, parent=None):
        super(TableWidget_Delegate, self).__init__(parent)
        self.installEventFilter(self)

    def createEditor(self, parent, options, index):
        return LineEdit(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data())
        editor.selectAll()

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Tab or event.key() == QtCore.Qt.Key_Backtab)):
            # Commit Editing, end Editing mode and re-send Tab/Backtab
            self.commitData.emit(source)
            self.closeEditor.emit(source, QtWidgets.QAbstractItemDelegate.NoHint)
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers())
            QtWidgets.QApplication.instance().sendEvent(self.parent(),event)
            return True
        elif (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
            # Commit Editing and end Editing mode
            self.commitData.emit(source)
            self.closeEditor.emit(source, QtWidgets.QAbstractItemDelegate.NoHint)
            #event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers())
            #QtWidgets.QApplication.instance().sendEvent(self.parent(),event)
            return True
        return super(TableWidget_Delegate, self).eventFilter(source, event)


# -----------------------------------------------------------------------------------------------------------------
        
class ColourPicker(QtWidgets.QToolButton):
    """
    This widget is used to display and modify a single colour. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    def __init__(self, Type, Element, parent=None):
        super(ColourPicker, self).__init__(parent)
        self.Type, self.Element = Type, Element
        self.setText("")
        self.LoadCurrentPalette()
        self.clicked.connect(self.PickColour)
        self.setAutoRaise(True)
        self.setAutoFillBackground(True)
        
    def LoadCurrentPalette(self):
        try:
            if self.Type == "Pen":
                self.Colour = QtWidgets.QApplication.instance().PenColours[self.Element].color()
            elif self.Type == "Notification":
                self.Colour = QtWidgets.QApplication.instance().NotificationColours[self.Element].color()
            elif self.Type == "Misc":
                self.Colour = QtWidgets.QApplication.instance().MiscColours[self.Element].color()
        except:
            self.Colour = QtGui.QColor(255, 0, 255)
        self.ColourSelf()
        
    def PickColour(self):
        Colour = QtWidgets.QColorDialog.getColor(self.Colour,None,"Choose the {} colour \"{}\"".format(self.Type,self.Element))
        if Colour.isValid(): # If the QColorDialog was aborted by the user the returned colour is invalid
            self.Colour = Colour
        self.ColourSelf()
        
    def ColourSelf(self):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(self.Colour)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        # Generate readable text colour
        textColour = QtGui.QColor("black") if (0.299 * self.Colour.red() + 0.587 * self.Colour.green() + 0.114 * self.Colour.blue())/255 > 0.5 else QtGui.QColor("white")
        brush = QtGui.QBrush(textColour)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.setPalette(palette)
        # Display the HexRgb code of the colour
        #self.setText("#"+str(hex(self.Colour.rgb()))[4:]) # Does the same as the next line
        self.setText(self.Colour.name(0)) # 0 = HexRgb

class PaletteColourPicker(ColourPicker):
    """
    This widget is used to display and modify a single colour of a QPalette. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    def __init__(self, Mode, Element, ModeText, ElementText, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.Mode, self.Element = Mode, Element
        self.ModeText, self.ElementText = ModeText, ElementText
        self.setText("")
        self.LoadCurrentPalette()
        self.clicked.connect(self.PickColour)
        if self.ElementText != "Button": #MAYBE: Link the Button colour buttons to the ButtonText colour buttons
            self.setAutoRaise(True)
            self.setAutoFillBackground(True)
        
    def LoadCurrentPalette(self):
        try:
            if self.ModeText.endswith("Version 1"):
                self.Colour = QtWidgets.QApplication.instance().Palette1.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
            elif self.ModeText.endswith("Version 2"):
                self.Colour = QtWidgets.QApplication.instance().Palette2.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
            elif self.ModeText.endswith("Version 3"):
                self.Colour = QtWidgets.QApplication.instance().Palette3.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
        except:
            self.Colour = QtGui.QColor(255, 0, 255)
        self.ColourSelf()
        
    def PickColour(self):
        Colour = QtWidgets.QColorDialog.getColor(self.Colour,None,"Choose colour for {} when {}".format(self.ElementText,self.ModeText))
        if Colour.isValid(): # If the QColorDialog was aborted by the user the returned colour is invalid
            self.Colour = Colour
        self.ColourSelf()
    

class OptionsWidget_1_Appearance(QtWidgets.QWidget):
    """
    This widget allows the user to change the Font and the colourpalette of the application. \n
    It furthermore allows the user to create, save and load their own colour palette. \n
    If you create your own options menu it is STRONGLY advised to include this widget! \n
    The freedome this widget provides to the user is the foundation of AGeLib. \n
    The initial reason to create this library was because I couldn't stand most applications anymore because they wouldn't allow me to change their colour.
    """
    def __init__(self, parent=None):
        super(OptionsWidget_1_Appearance, self).__init__(parent)
        self.PaletteColours = []
        self.PenColours = []
        self.NotificationColours = []
        self.MiscColours = []
        
        #IMPROVE: Draw more attention to the palette selector!!! Changing the colours currently looks far too intimidating!
        #           The users first look should be drawn to the palette selector BY ANY MEANS NECESSARY!!!
        #TODO: Add this link somewhere: https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum
        #TODO: Add Tooltips that contain the info from https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum and say which colours are used for BG and FG
        #TODO: Add a checkbox somewhere to help automate the creation of Inactive and Disabled (keep tooltip behaviour in mind!!)
        #MAYBE: Add Mpl/Special Colour selection
        #MAYBE: Add a button to revert ?the last? change
        
        self.setLayout(QtWidgets.QGridLayout())
        self.FontLabel = QtWidgets.QLabel(self)
        self.FontLabel.setText("Choose a font:")
        self.FontLabel.setToolTip("The displayed fonts are the fonts that are installed on your copmuter")
        self.layout().addWidget(self.FontLabel,0,0)
        self.fontComboBox = QtWidgets.QFontComboBox(self)
        self.fontComboBox.currentFontChanged.connect(self.SetFontFamily)
        self.layout().addWidget(self.fontComboBox,0,1)
        self.ColourListLabel = QtWidgets.QLabel(self)
        self.ColourListLabel.setText("Choose a colour palette:")
        self.layout().addWidget(self.ColourListLabel,1,0)
        self.ColourList = QtWidgets.QComboBox(self)
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.setCurrentText("Dark")
        if versionParser(QtCore.qVersion())>=versionParser("5.14"):
            self.ColourList.textActivated.connect(QtWidgets.QApplication.instance().Recolour)
        else:
            self.ColourList.currentTextChanged.connect(QtWidgets.QApplication.instance().Recolour)
        self.layout().addWidget(self.ColourList,1,1)
        self.ColourTableLabel = QtWidgets.QLabel(self)
        self.ColourTableLabel.setText("Or create you own:")
        self.layout().addWidget(self.ColourTableLabel,2,0)
        self.LoadToEditorButton = QtWidgets.QPushButton(self)
        self.LoadToEditorButton.setText("Load current palette to editor")
        self.LoadToEditorButton.clicked.connect(lambda: self.LoadCurrentPalette())
        self.layout().addWidget(self.LoadToEditorButton,2,1)
        # Colour Tabs #TODO: The 3 misc tabs should be combined into one tab with 3 Tables
        self.ColourTabs = QtWidgets.QTabWidget(self)
        self.layout().addWidget(self.ColourTabs,3,0,1,2)
        self.PaletteTable = QtWidgets.QTableWidget(len(AGeColour.PaletteElements),len(AGeColour.PaletteStates),self)
        self.ColourTabs.addTab(self.PaletteTable,"Palettes")
        #self.layout().addWidget(self.PaletteTable,3,0,1,2)
        self.PenTable_Labels = ["Red","Green","Blue","Yellow","Cyan","Magenta","Orange","Light Blue","White","Black"]
        self.PenTable = QtWidgets.QTableWidget(len(self.PenTable_Labels),1,self)
        self.PenTable.setVerticalHeaderLabels(self.PenTable_Labels)
        self.ColourTabs.addTab(self.PenTable,"Pen Colours")
        self.NotificationTable_Labels = ["Error","Warning","Notification","Message"]
        self.NotificationTable = QtWidgets.QTableWidget(len(self.NotificationTable_Labels),1,self)
        self.NotificationTable.setVerticalHeaderLabels(self.NotificationTable_Labels)
        self.ColourTabs.addTab(self.NotificationTable,"Notification Colours")
        self.MiscTable_Labels = ["Friendly","Hostile","Neutral","Ally","Self",
                                "Common","Uncommon","Rare","Legendary","Mythical","Artefact","Broken","Magical","Important",
                                "Gradient1","Gradient2","Gradient3"]
        self.MiscTable = QtWidgets.QTableWidget(len(self.MiscTable_Labels),1,self)
        self.MiscTable.setVerticalHeaderLabels(self.MiscTable_Labels)
        self.ColourTabs.addTab(self.MiscTable,"Misc Colours")
        #
        self.ApplyPaletteButton = QtWidgets.QPushButton(self)
        self.ApplyPaletteButton.setText("Apply Palette")
        self.ApplyPaletteButton.clicked.connect(lambda: self.MakePalette())
        self.layout().addWidget(self.ApplyPaletteButton,4,0)
        self.SavePaletteButton = QtWidgets.QPushButton(self)
        self.SavePaletteButton.setText("Save Palette")
        self.SavePaletteButton.clicked.connect(lambda: self.SavePalette())
        self.layout().addWidget(self.SavePaletteButton,4,1)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(3)
        HLabel = ["Active Version 1","Inactive Version 1","Disabled Version 1","Active Version 2","Inactive Version 2","Disabled Version 2","Active Version 3","Inactive Version 3","Disabled Version 3"]
        VLabel = []
        y = 0
        for i, v in AGeColour.PaletteElements.items():
            VLabel.append(i)
            #CLEANUP
            #widget = PaletteColourPicker(AGeColour.PaletteStates["Active"],v,"Active",i,self.PaletteTable)
            #self.PaletteColours.append(widget)
            #self.PaletteTable.setCellWidget(y,0,widget)
            #widget = PaletteColourPicker(AGeColour.PaletteStates["Inactive"],v,"Inactive",i,self.PaletteTable)
            #self.PaletteColours.append(widget)
            #self.PaletteTable.setCellWidget(y,1,widget)
            #widget = PaletteColourPicker(AGeColour.PaletteStates["Disabled"],v,"Disabled",i,self.PaletteTable)
            #self.PaletteColours.append(widget)
            #self.PaletteTable.setCellWidget(y,2,widget)
            x = 0
            for ii, vi in AGeColour.PaletteStates.items():
                widget = PaletteColourPicker(vi,v,ii,i,self.PaletteTable)
                self.PaletteColours.append(widget)
                self.PaletteTable.setCellWidget(y,x,widget)
                x+=1
            y+=1
        self.PaletteTable.setHorizontalHeaderLabels(HLabel)
        self.PaletteTable.setVerticalHeaderLabels(VLabel)
        y = 0
        for i in self.PenTable_Labels:
            widget = ColourPicker("Pen",i,self.PenTable)
            self.PenColours.append(widget)
            self.PenTable.setCellWidget(y,0,widget)
            y+=1
        y = 0
        for i in self.NotificationTable_Labels:
            widget = ColourPicker("Notification",i,self.NotificationTable)
            self.NotificationColours.append(widget)
            self.NotificationTable.setCellWidget(y,0,widget)
            y+=1
        y = 0
        for i in self.MiscTable_Labels:
            widget = ColourPicker("Misc",i,self.MiscTable)
            self.MiscColours.append(widget)
            self.MiscTable.setCellWidget(y,0,widget)
            y+=1
        
    def SetFontFamily(self,Family):
        QtWidgets.QApplication.instance().SetFont(Family,self.window().TopBar.Font_Size_spinBox.value(),self)
        
    def LoadCurrentPalette(self):
        for i in self.PaletteColours+self.PenColours+self.NotificationColours+self.MiscColours:
            i.LoadCurrentPalette()
        #self.PenColours = []
        #self.NotificationColours = []
        #self.MiscColours = []
        
    def LoadPaletteList(self):
        ColourList = []
        try:
            try:
                importlib.reload(AGeColour)
            except:
                NC(2,"Could not reload AGeColour",exc=sys.exc_info(),func="Main_App.Recolour")
            try:
                if QtWidgets.QApplication.instance().AGeLibPathOK:
                    spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(QtWidgets.QApplication.instance().AGeLibSettingsPath,"CustomColourPalettes.py"))
                    CustomColours = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(CustomColours)
                    #CustomColours.MyClass()
                else:
                    raise Exception("AGeLibPath is not OK")
            except:
                NC(4,"Could not load custom colours",exc=sys.exc_info(),func="Main_App.Recolour")
            try:
                for i in AGeColour.Colours.keys():
                    ColourList.append(i)
                for i in CustomColours.Colours.keys():
                    ColourList.append(i)
            except:
                pass
        except:
            NC(1,"Exception while loading colour palette",exc=sys.exc_info(),func="Main_App.Recolour")
        return ColourList
        
    def MakePalette(self):
        self.ColourList.blockSignals(True)
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.blockSignals(False)
        palette1,palette2,palette3 = QtGui.QPalette(),QtGui.QPalette(),QtGui.QPalette()
        PenColours , NotificationColours , MiscColours = {},{},{}
        for i in self.PaletteColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            if int(i.ModeText[-1]) == 1:
                palette1.setBrush(i.Mode, i.Element, brush)
            elif int(i.ModeText[-1]) == 2:
                palette2.setBrush(i.Mode, i.Element, brush)
            elif int(i.ModeText[-1]) == 3:
                palette3.setBrush(i.Mode, i.Element, brush)
        for i in self.PenColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            PenColours[i.Element] = brush
        for i in self.NotificationColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            NotificationColours[i.Element] = brush
        for i in self.MiscColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            MiscColours[i.Element] = brush
            #
        QtWidgets.QApplication.instance()._Recolour(palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours)
        return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours
    
    def PaletteToPython(self,Palette,FunctionName,Name):
        #window.AMaDiA_About_Window_Window.TextBrowser.setText(app.optionWindow.ColourPicker.PaletteToPython(AGeColour.Colours[app.optionWindow.ColourPicker.LoadPaletteList()[0]],app.optionWindow.ColourPicker.LoadPaletteList()[0])[0])
        Palette1, Palette2, Palette3, _PenColours, _NotificationColours, _MiscColours = Palette()
        PenColours, NotificationColours, MiscColours = ColourDict(),ColourDict(),ColourDict()
        PenColours.copyFromDict(_PenColours)
        NotificationColours.copyFromDict(_NotificationColours)
        MiscColours.copyFromDict(_MiscColours)
        Text = "\ndef "+FunctionName+"():\n    palette1 = QtGui.QPalette()\n    palette2 = QtGui.QPalette()\n    palette3 = QtGui.QPalette()"
        for i, v in AGeColour.PaletteElements.items():
            for ii,iv in AGeColour.PaletteStates.items():
                if int(ii[-1]) == 1:
                    Colour = Palette1.brush(iv, v).color()
                elif int(ii[-1]) == 2:
                    Colour = Palette2.brush(iv, v).color()
                elif int(ii[-1]) == 3:
                    Colour = Palette3.brush(iv, v).color()
                Text += "\n    brush = QtGui.QBrush(QtGui.QColor({},{},{}))".format(str(Colour.red()),str(Colour.green()),str(Colour.blue()))
                Text += "\n    brush.setStyle(QtCore.Qt.SolidPattern)"
                Text += "\n    palette{}.setBrush(QtGui.QPalette.{}, QtGui.QPalette.{}, brush)".format(ii[-1],ii.split()[0],i)
        Text += "\n    PenColours = {"
        for i in self.PenTable_Labels:
            Colour = PenColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    NotificationColours = {"
        for i in self.NotificationTable_Labels:
            Colour = NotificationColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    MiscColours = {"
        for i in self.MiscTable_Labels:
            Colour = MiscColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours\n"
        return Text,FunctionName,Name
    
    def SavePalette(self,Name=None):
        # window.AMaDiA_About_Window_Window.TextBrowser.setText(app.optionWindow.ColourPicker.SavePalette("Test"))
        if Name == None:
            Name = QtWidgets.QInputDialog.getText(self,"Palette Name","What should the palette be called?")[0].strip()
            # VALIDATE: Ensure that the names can not break the dictionary
            if Name == None or Name == "":
                NC(2,"SavePalette has been cancelled")
                return ""
        Text = "from PyQt5 import QtCore, QtGui\n\ndef NewColour():\n    palette1 = QtGui.QPalette()\n    palette2 = QtGui.QPalette()\n    palette3 = QtGui.QPalette()"
        for i in self.PaletteColours:
            Text += "\n    brush = QtGui.QBrush(QtGui.QColor({},{},{}))".format(str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
            Text += "\n    brush.setStyle(QtCore.Qt.SolidPattern)"
            Text += "\n    palette{}.setBrush(QtGui.QPalette.{}, QtGui.QPalette.{}, brush)".format(i.ModeText.split()[2],i.ModeText.split()[0],i.ElementText)
        Text += "\n    PenColours = {"
        for i in self.PenColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        Text = Text[:-1]+"}\n    NotificationColours = {"
        for i in self.NotificationColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        Text = Text[:-1]+"}\n    MiscColours = {"
        for i in self.MiscColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        #
        Text = Text[:-1]+"}\n    return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours\n"
        try:
            if not QtWidgets.QApplication.instance().AGeLibPathOK: raise Exception("AGeLibPath is not OK")
            ##
            TheDict = {}
            try:
                nText = Text
                spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(QtWidgets.QApplication.instance().AGeLibSettingsPath,"CustomColourPalettes.py"))
                CustomColours = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(CustomColours)
                i=1
                for k,v in CustomColours.Colours.items():
                    fn = "c"+str(i)
                    t,fn,n = self.PaletteToPython(v,fn,k)
                    if n == Name:
                        msgBox = QtWidgets.QMessageBox(self)
                        msgBox.setText("\"{}\" already exists".format(Name))
                        msgBox.setInformativeText("Do you want to overwrite \"{}\"?".format(Name))
                        msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                        ret = msgBox.exec()
                        if ret != QtWidgets.QMessageBox.Save:
                            return Text
                        else:
                            continue
                    nText += "\n"
                    nText += t
                    TheDict[n.replace("\\","\\\\").replace("\"","\\\"")] = fn
                    i+=1
            except:
                NC(2,"Could not load custom colours",exc=sys.exc_info(),func="Main_App.Recolour")
                msgBox = QtWidgets.QMessageBox(self)
                msgBox.setText("Could not load previous custom colours!")
                msgBox.setInformativeText("Do you want to save the colour anyways?\nWARNING: This will overwrite any previous colour palettes!!!")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                ret = msgBox.exec()
                if ret != QtWidgets.QMessageBox.Save:
                    return Text
            Text = nText
            ##
            fText = Text+"\nColours = {\""+Name.replace("\\","\\\\").replace("\"","\\\"")+"\":NewColour"
            for k,v in TheDict.items():
                fText += ",\"{}\":{}".format(k,v)
            fText += "}"
            FileName = os.path.join(QtWidgets.QApplication.instance().AGeLibSettingsPath,"CustomColourPalettes.py")
            with open(FileName,'w',encoding="utf-8") as text_file:
                text_file.write(fText)
        except:
            NC(1,"Could not save",exc=sys.exc_info())
        self.ColourList.blockSignals(True)
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.blockSignals(False)
        return Text

# -----------------------------------------------------------------------------------------------------------------

#endregion

#region AWWF

class AWWF(QtWidgets.QMainWindow): # Astus Window With Frame
    """
    AWWF (Astus Window With Frame) is the face of AGeLib! This window is a full reimplementation
    of the standard window that operating systems (technically their window manager) provide. \n
    todo: Remove this line: (The regular window frames are boring and all professional applications use their own frame. This is my frame so I am a professional now!!!) \n
    TODO: Explain how the init and the top bar work! Make some simple examples!
    """
    #MAYBE: Implement borderless windowed mode as an alternative to full screen. This could be handled by adding a flag that is read in showFullScreen to decide which full screen mode to apply
    #TODO: Remove dependencies for TopBar and StatusBar to make these entirely optional
    def __init__(self, parent = None, includeTopBar=True, initTopBar=True, includeStatusBar=True, FullscreenHidesBars = False):
        self.BarsHidden = False
        super(AWWF, self).__init__(parent)
        self.includeTopBar, self.includeStatusBar, self.FullscreenHidesBars = includeTopBar, includeStatusBar, FullscreenHidesBars
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint,True)
        self.AWWF_CentralWidget = Window_Frame_Widget(self)
        self.AWWF_CentralWidget_layout =  QtWidgets.QGridLayout(self.AWWF_CentralWidget)
        self.AWWF_CentralWidget_layout.setContentsMargins(0, 0, 0, 0)
        self.AWWF_CentralWidget_layout.setSpacing(0)
        self.AWWF_CentralWidget_layout.setObjectName("gridLayout")
        self.AWWF_CentralWidget.setLayout(self.AWWF_CentralWidget_layout)
        
        self.AWWF_CentralWindow = QtWidgets.QMainWindow(self)
        self.AWWF_CentralWidget_layout.addWidget(self.AWWF_CentralWindow,1,0)
        
        super(AWWF, self).setCentralWidget(self.AWWF_CentralWidget)
        self.AWWF_p_MenuBar = None
        self.AWWF_p_CentralWidget = None
        self.AWWF_p_StatusBar = None
        self.standardSize = (900, 500)
        self.LastOpenState = self.showNormal
        self.OnTop = False

        self.installEventFilter(self)

        if includeTopBar:
            self.TopBar = TopBar_Widget(self,initTopBar)
            self.MenuBar = MMenuBar(self)
            self.setMenuBar(self.MenuBar)
            self.MenuBar.setCornerWidget(self.TopBar)
            self.MenuBar.setContentsMargins(0,0,0,0)
        if includeStatusBar:
            self.statusbar = StatusBar_Widget(self)
            self.statusbar.setObjectName("statusbar")
            self.setStatusBar(self.statusbar)
            self.statusbar.setSizeGripEnabled(False)
            self.windowTitleChanged.connect(self.statusbar.setWindowTitle)

 ##################### Layout Attempt
  #    def setMenuBar(self, MenuBar):
  #        if MenuBar == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.addWidget(QtWidgets.QWidget(self),0,0)
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
  #            except common_exceptions:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(MenuBar,0,0)
  #            MenuBar.setCursor(MenuBar.cursor())
  #        self.AWWF_p_MenuBar = MenuBar
  #        return True
  #
  #    def menuBar(self):
  #        return self.AWWF_p_MenuBar
  #
  #    def setCentralWidget(self, CentralWidget):
  #        if CentralWidget == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_CentralWidget)
  #            except common_exceptions:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(CentralWidget,1,0)
  #            CentralWidget.setCursor(CentralWidget.cursor())
  #        self.AWWF_p_CentralWidget = CentralWidget
  #        return True
  #
  #    def centralWidget(self):
  #        return self.AWWF_p_CentralWidget
  #        
  #    def setStatusBar(self, StatusBar):
  #        if StatusBar == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_StatusBar)
  #            except common_exceptions:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(StatusBar,2,0)
  #            StatusBar.setCursor(StatusBar.cursor())
  #        self.AWWF_p_StatusBar = StatusBar
  #        return True
  #
  #    def statusBar(self):
  #        return self.AWWF_p_StatusBar
  #
  #
 ##################### MenuBar/CentralWidget/StatusBar/ToolBar

    def setMenuBar(self, MenuBar):
        if MenuBar == None:
            try:
                self.AWWF_CentralWindow.setMenuBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except common_exceptions:
                pass
        else:
            self.AWWF_CentralWindow.setMenuBar(MenuBar)
            MenuBar.setCursor(MenuBar.cursor())
        self.AWWF_p_MenuBar = MenuBar
        return True
        # TODO: The following seems to be cleaner and more efficient... Use this for all of these redirects...
        #r = self.AWWF_CentralWindow.setMenuBar(MenuBar)
        #try:
        #    MenuBar.setCursor(MenuBar.cursor())
        #except:
        #    pass
        #return r

    def menuBar(self):
        return self.AWWF_CentralWindow.menuBar()

    def setCentralWidget(self, CentralWidget):
        if CentralWidget == None:
            try:
                self.AWWF_CentralWindow.setCentralWidget(None)
            except common_exceptions:
                pass
        else:
            self.AWWF_CentralWindow.setCentralWidget(CentralWidget)
            CentralWidget.setCursor(CentralWidget.cursor())
        self.AWWF_p_CentralWidget = CentralWidget
        return True

    def centralWidget(self):
        return self.AWWF_CentralWindow.centralWidget()
        
    def setStatusBar(self, StatusBar):
        if StatusBar == None:
            try:
                self.AWWF_CentralWindow.setStatusBar(None)
            except common_exceptions:
                pass
        else:
            self.AWWF_CentralWindow.setStatusBar(StatusBar)
            StatusBar.setCursor(StatusBar.cursor())
        self.AWWF_p_StatusBar = StatusBar
        return True

    def statusBar(self):
        return self.AWWF_CentralWindow.statusBar()

    # ToolBar #TODO:Expand
    def addToolBar(self, *ToolBar):
        if ToolBar == None:
            try:
                self.AWWF_CentralWindow.addToolBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except common_exceptions:
                pass
        else:
            self.AWWF_CentralWindow.addToolBar(*ToolBar)
        return True

    def insertToolBar(self, *ToolBar):
        if ToolBar == None:
            try:
                self.AWWF_CentralWindow.insertToolBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except common_exceptions:
                pass
        else:
            self.AWWF_CentralWindow.insertToolBar(*ToolBar)
        return True

    def toolBarArea(self):
        return self.AWWF_CentralWindow.toolBarArea()

 ##################### show, restoreState and positionReset
    def HideBars(self,b):
        """
        If b=True  the menu, top and status bar are permanently hidden. \n
        If b=False the menu, top and status bar will be shown again. \n
        Hiding these bars is not recommended!
        """
        self.BarsHidden = b
        self.TopBar.setVisible(b)
        try:
            self.MenuBar.setVisible(b)
        except:
            pass
        try:
            self.statusbar.setVisible(b)
        except:
            pass
    def setTopBarVisible(self,b):
        if not self.BarsHidden:
            self.TopBar.setVisible(b)
            try:
                self.MenuBar.setVisible(b)
            except:
                pass
            try:
                self.statusbar.setVisible(b)
            except:
                pass

    def showNormal(self):
        self.setTopBarVisible(True)
        self.AWWF_CentralWidget.showFrame()
        self.TopBar.MaximizeButton.setText("🗖")
        super(AWWF, self).showNormal()
    def show(self):
        self.setTopBarVisible(True)
        super(AWWF, self).show()
        QtWidgets.QApplication.instance().processEvents()
        if self.isFullScreen() or self.isMaximized():
            self.AWWF_CentralWidget.hideFrame()
            self.TopBar.MaximizeButton.setText("🗗")
        else:
            self.AWWF_CentralWidget.showFrame()
            self.TopBar.MaximizeButton.setText("🗖")
        if self.isFullScreen() and self.FullscreenHidesBars:
            self.setTopBarVisible(False)
    def showMaximized(self):
        self.setTopBarVisible(True)
        self.AWWF_CentralWidget.hideFrame()
        self.TopBar.MaximizeButton.setText("🗗")
        super(AWWF, self).showMaximized()
    def showFullScreen(self):
        if self.FullscreenHidesBars:
            self.setTopBarVisible(False)
        else:
            self.setTopBarVisible(True)
        self.AWWF_CentralWidget.hideFrame()
        self.TopBar.MaximizeButton.setText("🗗")
        super(AWWF, self).showFullScreen()
        
    def restoreState(self,state,version=0):
        self.setTopBarVisible(True)
        super(AWWF, self).restoreState(state,version)
        QtWidgets.QApplication.instance().processEvents()
        if self.isFullScreen() or self.isMaximized():
            self.AWWF_CentralWidget.hideFrame()
            self.TopBar.MaximizeButton.setText("🗗")
        else:
            self.AWWF_CentralWidget.showFrame()
            self.TopBar.MaximizeButton.setText("🗖")
        if self.isFullScreen() and self.FullscreenHidesBars:
            self.setTopBarVisible(False)
            
    def positionReset(self):
        self.showNormal()
        QtWidgets.QApplication.instance().processEvents()
        try:
            self.resize(*self.standardSize)
        except common_exceptions:
            self.resize(900, 600)
        QtWidgets.QApplication.instance().processEvents()
        try:
            frameGm = self.frameGeometry()
            screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
            centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
            frameGm.moveCenter(centerPoint)
            self.move(frameGm.topLeft())
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
        QtWidgets.QApplication.instance().processEvents()

 ##################### eventFilter
    def eventFilter(self, source, event):
        if event.type() == 6 and App().enableHotkeys: # QtCore.QEvent.KeyPress
            if event.modifiers() == QtCore.Qt.AltModifier:
                if event.key() == QtCore.Qt.Key_T and source is self: # Alt+T to toggle on top
                    if not self.OnTop:
                        print("Try OnTop")
                        self.OnTop = True
                        self.setWindowFlag(QtCore.Qt.X11BypassWindowManagerHint,True)
                        self.setWindowFlag(QtCore.Qt.BypassWindowManagerHint,True)
                        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,True)
                        QtWidgets.QApplication.instance().processEvents()
                        self.show()
                    else:
                        print("No longer OnTop")
                        self.OnTop = False
                        self.setWindowFlag(QtCore.Qt.X11BypassWindowManagerHint,False)
                        self.setWindowFlag(QtCore.Qt.BypassWindowManagerHint,False)
                        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,False)
                        QtWidgets.QApplication.instance().processEvents()
                        self.show()
            else:
                if event.key() == QtCore.Qt.Key_F11 and source is self: # F11 to toggle Fullscreen
                    if not self.isFullScreen():
                        if self.isMaximized():
                            self.LastOpenState = self.showMaximized
                            self.TopBar.MaximizeButton.setText("🗖")
                        else:
                            self.LastOpenState = self.showNormal
                            self.TopBar.MaximizeButton.setText("🗗")
                        self.showFullScreen()
                    else:
                        if self.LastOpenState == self.showMaximized:
                            self.TopBar.MaximizeButton.setText("🗗")
                        else:
                            self.TopBar.MaximizeButton.setText("🗖")
                        self.LastOpenState()
        #    #if event.modifiers() == QtCore.Qt.MetaModifier: # Does not work on windows as the meta key is not detected this way
        #    modifiers = QtWidgets.QApplication.keyboardModifiers() # Detects the meta key
        #    if modifiers == QtCore.Qt.MetaModifier: # Does not work on windows as windows eats all other key while the Meta Key is pressed...
        #        print("win")
        #        screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        #        screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
        #        Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
        #        Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
        #        Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
        #        Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
        #        # Left Side
        #        if event.key() == QtCore.Qt.Key_Left:
        #            self.window().resize(Half_X, Full_Y)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopLeft(screen.topLeft())
        #            self.window().move(frameGm.topLeft())
        #        # Right Side
        #        elif event.key() == QtCore.Qt.Key_Right:
        #            self.window().resize(Half_X, Full_Y)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopRight(screen.topRight())
        #            self.window().move(frameGm.topLeft())
        #        # Top Side
        #        elif event.key() == QtCore.Qt.Key_Up:
        #            self.window().resize(Full_X, Half_Y)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopRight(screen.topRight())
        #            self.window().move(frameGm.topLeft())
        #        # Bottom Side
        #        elif event.key() == QtCore.Qt.Key_Down:
        #            self.window().resize(Full_X, Half_Y)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveBottomLeft(screen.bottomLeft())
        #            self.window().move(frameGm.topLeft())
        
        #if type(source) == QtWidgets.QAction and event.type() == QtCore.QEvent.Enter and source.toolTip()!="": #==10
        #    QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),source.toolTip(),source)
        return super(AWWF, self).eventFilter(source, event) # let the normal eventFilter handle the event

class TopBar_Widget(QtWidgets.QWidget):
    def __init__(self, parent=None, DoInit=False, IncludeMenu = False, IncludeFontSpinBox = True, IncludeErrorButton = False, IncludeAdvancedCB = False):
        super(TopBar_Widget, self).__init__(parent)
        self.moving = False
        self.offset = 0
        self.IncludeMenu, self.IncludeFontSpinBox = IncludeMenu, IncludeFontSpinBox
        self.IncludeErrorButton, self.IncludeAdvancedCB = IncludeErrorButton, IncludeAdvancedCB
        if DoInit:
            self.init(IncludeMenu, IncludeFontSpinBox, IncludeErrorButton, IncludeAdvancedCB)

    def init(self, IncludeMenu = False, IncludeFontSpinBox = False, IncludeErrorButton = False, IncludeAdvancedCB = False):
        # TODO: restrict the height and add the Option for a QtWidgets.QSpacerItem to make the horizontal spacing work if not corner widget
        self.IncludeMenu, self.IncludeFontSpinBox = IncludeMenu, IncludeFontSpinBox
        self.IncludeErrorButton, self.IncludeAdvancedCB = IncludeErrorButton, IncludeAdvancedCB
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setObjectName("TopBar")
        if self.layout() == None:
            self.gridLayout = QtWidgets.QGridLayout(self)
            self.gridLayout.setContentsMargins(0, 0, 0, 0)
            self.gridLayout.setSpacing(0)
            self.gridLayout.setObjectName("gridLayout")
            #self.gridLayout.setSizeConstraint(QtWidgets.QGridLayout.SetNoConstraint)
            self.setLayout(self.gridLayout)

        self.ButtonSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.CloseButton = QtWidgets.QToolButton(self)
        self.CloseButton.setObjectName("CloseButton")
        self.layout().addWidget(self.CloseButton, 0, 108, 1, 1,QtCore.Qt.AlignRight)
        self.CloseButton.setText("🗙")

        self.RedHighlightPalette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(155, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.RedHighlightPalette.setBrush(QtGui.QPalette.All, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.RedHighlightPalette.setBrush(QtGui.QPalette.All, QtGui.QPalette.ButtonText, brush)
        self.CloseButton.installEventFilter(self)
        self.CloseButton.setAutoRaise(True)
        self.CloseButton.setSizePolicy(self.ButtonSizePolicy)

        self.MaximizeButton = QtWidgets.QToolButton(self)
        self.MaximizeButton.setObjectName("MaximizeButton")
        self.layout().addWidget(self.MaximizeButton, 0, 107, 1, 1,QtCore.Qt.AlignRight)
        self.MaximizeButton.setText("🗖")
        self.MaximizeButton.installEventFilter(self)
        self.MaximizeButton.setAutoRaise(True)
        self.MaximizeButton.setSizePolicy(self.ButtonSizePolicy)

        self.MinimizeButton = QtWidgets.QToolButton(self)
        self.MinimizeButton.setObjectName("MinimizeButton")
        self.layout().addWidget(self.MinimizeButton, 0, 106, 1, 1,QtCore.Qt.AlignRight)
        self.MinimizeButton.setText("🗕")
        self.MinimizeButton.installEventFilter(self)
        self.MinimizeButton.setAutoRaise(True)
        self.MinimizeButton.setSizePolicy(self.ButtonSizePolicy)

        self.OptionsButton = QtWidgets.QToolButton(self)
        self.OptionsButton.setObjectName("OptionsButton")
        self.layout().addWidget(self.OptionsButton, 0, 105, 1, 1,QtCore.Qt.AlignRight)
        self.OptionsButton.setText("⚙")
        self.OptionsButton.setToolTip("Show the options window")
        self.OptionsButton.installEventFilter(self)
        self.OptionsButton.setAutoRaise(True)
        self.OptionsButton.setSizePolicy(self.ButtonSizePolicy)

        self.MoveMe = QtWidgets.QLabel(self)
        self.MoveMe.setObjectName("MoveMe")
        self.layout().addWidget(self.MoveMe, 0, 104, 1, 1,QtCore.Qt.AlignRight)
        self.MoveMe.setText("  🖐  ")#▨#🖐
        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

        self.CloseButton.clicked.connect(self.Exit)
        self.MaximizeButton.clicked.connect(self.ToggleMinMax)
        self.MinimizeButton.clicked.connect(self.Minimize)
        self.OptionsButton.clicked.connect(App().Show_Options)

        try:
            #self.window().menuBar().installEventFilter(self)
            if IncludeMenu:
                self.Menu = QtWidgets.QToolButton(self)
                self.Menu.setObjectName("Menu")
                self.layout().addWidget(self.Menu, 0, 103, 1, 1,QtCore.Qt.AlignRight)
                self.Menu.setText("\u2630")#☰ #("≡")
                self.Menu.setAutoRaise(True)
                self.Menu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
                self.Menu.setMenu(self.window().Menu)
                self.Menu.setSizePolicy(self.ButtonSizePolicy)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
        
        if IncludeAdvancedCB:
            self.AdvancedCB = QtWidgets.QCheckBox(self)
            self.AdvancedCB.setText("")
            self.AdvancedCB.setToolTip("Advanced Mode (alt+A)")
            self.AdvancedCB.setChecked(QtWidgets.QApplication.instance().advanced_mode)
            self.AdvancedCB.setObjectName("AdvancedCB")
            self.layout().addWidget(self.AdvancedCB, 0, 102, 1, 1,QtCore.Qt.AlignRight)
            self.AdvancedCB.clicked.connect(QtWidgets.QApplication.instance().ToggleAdvancedMode)

        if IncludeFontSpinBox:
            self.Font_Size_spinBox = QtWidgets.QSpinBox(self)
            self.Font_Size_spinBox.setMinimum(5)
            self.Font_Size_spinBox.setMaximum(25)
            self.Font_Size_spinBox.setProperty("value", self.font().pointSize())
            self.Font_Size_spinBox.setObjectName("Font_Size_spinBox")
            self.layout().addWidget(self.Font_Size_spinBox, 0, 101, 1, 1,QtCore.Qt.AlignRight)
            self.Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)

        if IncludeErrorButton:
            self.Error_Label = QtWidgets.QPushButton(self)
            self.Error_Label.setObjectName("Error_Label")
            self.Error_Label.setText(QtWidgets.QApplication.instance().LastNotificationText)
            self.Error_Label.setToolTip(QtWidgets.QApplication.instance().LastNotificationToolTip)
            self.Error_Label.setIcon(QtWidgets.QApplication.instance().LastNotificationIcon)
            self.layout().addWidget(self.Error_Label, 0, 100, 1, 1,QtCore.Qt.AlignRight)
            self.Error_Label.installEventFilter(self)
            self.Error_Label.clicked.connect(QtWidgets.QApplication.instance().Show_Notification_Window)

    def Minimize(self):
        self.window().showMinimized()

    def ToggleMinMax(self):
        if not self.window().isFullScreen():
            if self.window().isMaximized():
                self.window().showNormal()
                self.MaximizeButton.setText("🗖")
            else:
                self.window().setGeometry(
                    Qt.QStyle.alignedRect(
                        QtCore.Qt.LeftToRight,
                        QtCore.Qt.AlignCenter,
                        self.window().size(),
                        QtWidgets.QApplication.instance().desktop().availableGeometry(self.window())))
                self.window().showMaximized()
                self.MaximizeButton.setText("🗗")
        else:
            try:
                if self.window().LastOpenState == self.window().showMaximized:
                    self.MaximizeButton.setText("🗗")
                else:
                    self.MaximizeButton.setText("🗖")
                self.window().LastOpenState()
            except AttributeError:
                self.MaximizeButton.setText("🗗")
                self.window().showMaximized()

    def Exit(self):
        self.window().close()

    def ChangeFontSize(self):
        try:
            QtWidgets.QApplication.instance().SetFont(PointSize = self.Font_Size_spinBox.value(), source=self.window())
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
        
    def eventFilter(self, source, event):
        #if event.type() == 5: # QtCore.QEvent.MouseMove
        #    if self.moving: self.window().move(event.globalPos()-self.offset)
        #elif event.type() == 2: # QtCore.QEvent.MouseButtonPress
        #    if event.button() == QtCore.Qt.LeftButton:
        #        self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #        self.MaximizeButton.setText("🗖")
        #        self.moving = True; self.offset = event.globalPos()-self.window().geometry().topLeft()
        #elif event.type() == 3: # QtCore.QEvent.MouseButtonRelease
        #    self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #    self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        #    self.moving = False
        #    if event.button() == QtCore.Qt.LeftButton:
        #        pos = self.window().pos()
        #        #if (pos.x() < 0):
        #        #    pos.setX(0)
        #        #    self.window().move(pos)
        #        if (pos.y() < 0):
        #            pos.setY(0)
        #            self.window().move(pos)
        if event.type() == 10 or event.type() == 11:# QtCore.QEvent.Enter or QtCore.QEvent.Leave
            if source == self.CloseButton:
                if event.type() == QtCore.QEvent.Enter:#HoverMove
                    self.CloseButton.setPalette(self.RedHighlightPalette)
                elif event.type() == QtCore.QEvent.Leave:#HoverLeave
                    self.CloseButton.setPalette(self.palette())
            elif source == self.MaximizeButton:
                if event.type() == QtCore.QEvent.Enter:
                    self.MaximizeButton.setAutoRaise(False)
                elif event.type() == QtCore.QEvent.Leave:
                    self.MaximizeButton.setAutoRaise(True)
            elif source == self.MinimizeButton:
                if event.type() == QtCore.QEvent.Enter:
                    self.MinimizeButton.setAutoRaise(False)
                elif event.type() == QtCore.QEvent.Leave:
                    self.MinimizeButton.setAutoRaise(True)
        elif self.IncludeErrorButton and source is self.Error_Label and event.type() == QtCore.QEvent.Enter: #==10
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),self.Error_Label.toolTip(),self.Error_Label)
        return super(TopBar_Widget, self).eventFilter(source, event)

    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            #if self.window().isMaximized() or self.window().isFullScreen(): # If moving the window while in fullscreen or maximized make it normal first
            #    corPos = self.window().geometry().topRight()
            #    self.window().showNormal()
            #    self.window().AWWF_CentralWidget.showFrame()
            #    QtWidgets.QApplication.instance().processEvents()
            #    self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
            self.moving = True; self.offset = event.globalPos()-self.window().geometry().topLeft()

    def mouseReleaseEvent(self,event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode(): # MAYBE: Make this behaviour for advanced mode toggable in the options if a user never wants this
                        self.window().resize(Full_X, Half_Y)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="TopBar_Widget.mouseReleaseEvent")

    def mouseMoveEvent(self,event):
        if self.moving:
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                # TODO: Make normalizing the window relative to the previous and current window width to keep the cursor on the window regardless wether clicking right or left
                self.MaximizeButton.setText("🗖")
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)

class StatusBar_Widget(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar_Widget, self).__init__(parent)
        self.WindowNameLabel = QtWidgets.QLabel(self)
        self.addPermanentWidget(self.WindowNameLabel)

    def setWindowTitle(self, WindowTitle):
        WindowTitle += " "
        self.WindowNameLabel.setText(WindowTitle)

class MenuAction(QtWidgets.QAction):
    def __init__(self, parent=None, text=None, tooltip=None, action=None, add=False, icon=None):
        if text != None:
            if icon != None:
                super(MenuAction, self).__init__(icon,text,parent)
            else:
                super(MenuAction, self).__init__(text,parent)
        else:
            super(MenuAction, self).__init__(parent)
        if tooltip != None:
            self.setToolTip(tooltip)
        if action != None:
            if type(action) != list:
                action = [action]
            for i in action:
                self.triggered.connect(i)
        if add:
            parent.addAction(self)
        self.hovered.connect(self.showToolTip)
    
    def showToolTip(self):
        #if self.toolTip() != "" and self.toolTip() != None and self.toolTip() != self.text():
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),self.toolTip())#,self)

class Window_Frame_Widget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(Window_Frame_Widget, self).__init__(parent)
        self.FrameEnabled = False
        self.moving = False
        self.setMouseTracking(True)

        
        # Resizing was inspired by an answer to https://stackoverflow.com/questions/37047236/qt-resizable-and-movable-main-window-without-title-bar (16.12.2019)
        self.offset = 0
        self.mPos = None# For dragging, relative mouse position to upper left
        self.global_mPos = None # For resizing, global mouse position at mouse click
        self.rs_mPos = None # for resizing
        self.storeWidth = 0 # fix window size at mouseclick for resizing
        self.storeHeight = 0
        self.adjXFac = 0
        self.adjYFac = 0
        self.transXFac = 0
        self.transYFac = 0
        self.Direction = "D"
    
    def showFrame(self):
        self.FrameEnabled = True
        self.setFrameStyle(self.Box | self.Sunken)
        self.setLineWidth(2)
        #self.setMidLineWidth(3)

    def hideFrame(self):
        self.FrameEnabled = False
        self.setFrameStyle(self.NoFrame)
        #self.setLineWidth(1)
        #self.setMidLineWidth(3)

    def mousePressEvent(self,event):
        if (event.button() == QtCore.Qt.LeftButton):
            # Coordinates have been mapped such that the mouse position is relative to the upper left of the main window
            self.mPos = event.globalPos() - self.window().frameGeometry().topLeft()

            # At the moment of mouse click, capture global position and lock the size of window for resizing
            self.global_mPos = event.globalPos()
            self.storeWidth = self.width()
            self.storeHeight= self.height()
            self.offset = event.globalPos()-self.window().geometry().topLeft() # event.globalPos()-frameGeometry().topLeft()
            rs_size = 20
            # Big if statement checks if the mouse is near the frame and if the frame is enabled
            if ( ((abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size) or
                    (abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size)or
                    (abs(self.offset.y()) < rs_size) or
                    (abs(self.offset.y()) <rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size))
                    and self.FrameEnabled):
                # Use 2x2 matrix to adjust how much you are resizing and how much you
                # are moving. Since the default coordinates are relative to upper left
                # You cannot just have one way of resizing and moving the window.
                # It will depend on which corner you are referring to
                # 
                # self.adjXFac and self.adjYFac are for calculating the difference between your
                # current mouse position and where your mouse was when you clicked.
                # With respect to the upper left corner, moving your mouse to the right
                # is an increase in coordinates, moving mouse to the bottom is increase etc.
                # However, with other corners this is not so and since I chose to subtract
                # This difference at the end for resizing, self.adjXFac and self.adjYFac should be
                # 1 or -1 depending on whether moving the mouse in the x or y directions
                # increases or decreases the coordinates respectively. 
                # 
                # self.transXFac self.transYFac is to move the window over. Resizing the window does not
                # automatically pull the window back toward your mouse. This is what
                # transfac is for (translate window in some direction). It will be either
                # 0 or 1 depending on whether you need to translate in that direction.
                #
                # Initialize Matrix:
                # Upper left corner section
                if ( (abs(self.offset.x()) < rs_size and abs(self.offset.y()) < rs_size)):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                    # Upper left. No flipping of axis, no translating window
                    self.adjXFac=1
                    self.adjYFac=1
                    self.transXFac=0
                    self.transYFac=0
                    self.Direction = "D"
                    self.moving = True
                # Upper right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y()) <rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    # upper right. Flip displacements in mouse movement across x axis
                    # and translate window left toward the mouse
                    self.adjXFac=-1
                    self.adjYFac=1
                    self.transXFac=1
                    self.transYFac=0
                    self.Direction = "D"
                    self.moving = True
                # Lower left corner section
                elif(abs(self.offset.x()) < rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    # lower left. Flip displacements in mouse movement across y axis
                    # and translate window up toward mouse
                    self.adjXFac=1
                    self.adjYFac=-1
                    self.transXFac=0
                    self.transYFac=1
                    self.Direction = "D"
                    self.moving = True
                # Lower right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                    # lower right. Flip mouse displacements on both axis and
                    # translate in both x and y direction left and up toward mouse.
                    self.adjXFac=-1
                    self.adjYFac=-1
                    self.transXFac=1
                    self.transYFac=1
                    self.Direction = "D"
                    self.moving = True


                # Upper Side
                elif abs(self.offset.y()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                    self.adjXFac=-1#1
                    self.adjYFac=1
                    self.transXFac=1#0
                    self.transYFac=0
                    self.Direction = "y"
                    self.moving = True
                # Lower side
                elif abs(self.offset.y()) > self.height()-rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                    self.adjXFac=-1
                    self.adjYFac=-1
                    self.transXFac=1
                    self.transYFac=1
                    self.Direction = "y"
                    self.moving = True
                # Right Side
                elif abs(self.offset.x()) > self.width()-rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    self.adjXFac=-1
                    self.adjYFac=-1#1
                    self.transXFac=1
                    self.transYFac=1#0
                    self.Direction = "x"
                    self.moving = True
                # Left Side
                elif abs(self.offset.x()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    self.adjXFac=1
                    self.adjYFac=-1
                    self.transXFac=0
                    self.transYFac=1
                    self.Direction = "x"
                    self.moving = True

            event.accept()

    def mouseReleaseEvent(self,event):
        self.moving = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def mouseMoveEvent(self,event):
        if self.moving:
            #if (event.buttons()==QtCore.Qt.LeftButton ):
            if self.Direction == "D":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth-adjXDiff, self.storeHeight-adjYDiff)
            elif self.Direction == "y":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth, self.storeHeight-adjYDiff)
            elif self.Direction == "x":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth-adjXDiff, self.storeHeight)
            event.accept()
        else:
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            rs_size = 20
            if ( ((abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size) or
                    (abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size)or
                    (abs(self.offset.y()) < rs_size) or
                    (abs(self.offset.y()) <rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size))
                    and self.FrameEnabled):
                # Upper left corner section
                if ( (abs(self.offset.x()) < rs_size and abs(self.offset.y()) < rs_size)):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                # Upper right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y()) <rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    self.Direction = "D"
                # Lower left corner section
                elif(abs(self.offset.x()) < rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                # Lower right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)


                # Upper Side
                elif abs(self.offset.y()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                # Lower side
                elif abs(self.offset.y()) > self.height()-rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                # Right Side
                elif abs(self.offset.x()) > self.width()-rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                # Left Side
                elif abs(self.offset.x()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    
            # In any move event if it is not in a resize region use the default cursor
            else:
                self.setCursor(QtCore.Qt.ArrowCursor)

    def leaveEvent(self,event):
        self.setCursor(QtCore.Qt.ArrowCursor)

class MMenuBar(QtWidgets.QMenuBar): # Moveable Menu Bar
    def __init__(self, parent=None):
        super(MMenuBar, self).__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.moving = False
        self.offset = 0
        self.setMouseTracking(True)

    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton and self.actionAt(event.pos())==None and self.moving == False and self.activeAction()==None:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.moving = True
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().AWWF_CentralWidget.moving = False
            event.accept()
        else:
            self.moving = False
        super(MMenuBar, self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.window().AWWF_CentralWidget.moving = False
        if event.button() == QtCore.Qt.LeftButton and self.moving:
            self.moving = False
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode():
                        self.window().resize(Full_X, Half_Y)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MMenuBar.mouseReleaseEvent")
        else:
            self.moving = False
            super(MMenuBar, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self,event):
        if self.moving:
            event.accept()
            self.window().AWWF_CentralWidget.moving = False
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                try:
                    self.window().TopBar.MaximizeButton.setText("🗖")
                except common_exceptions:
                    pass
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)
        else:
            if self.actionAt(event.pos())!=None:
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            super(MMenuBar, self).mouseMoveEvent(event)

class MTabWidget(QtWidgets.QTabWidget): # Moveable Tab Widget
    def __init__(self, parent=None):
        super(MTabWidget, self).__init__(parent)
        #self.TabBar = MTabBar(self)
        #self.setTabBar(self.TabBar)
        ####self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabBar().setUsesScrollButtons(True)
        self.moving = False
        self.offset = 0
        self.setMouseTracking(True)

    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton and self.moving == False and self.childAt(event.pos())==None:
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.moving = True
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().AWWF_CentralWidget.moving = False
        else:
            self.moving = False
        super(MTabWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.window().AWWF_CentralWidget.moving = False
        if event.button() == QtCore.Qt.LeftButton and self.moving:
            self.moving = False
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Half_X, Full_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode():
                        self.window().resize(Full_X, Half_Y)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MTabWidget.mouseReleaseEvent")
        else:
            self.moving = False
            super(MTabWidget, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self,event): # Only registers if mouse is pressed...
        if self.moving:
            event.accept()
            self.window().AWWF_CentralWidget.moving = False
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                try:
                    self.window().TopBar.MaximizeButton.setText("🗖")
                except common_exceptions:
                    pass
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)
        else:
            #if self.childAt(event.pos())==None:
            #    self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            #else: # Does not work... Maybe all widgets need self.setMouseTracking(True) ?
            #    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            super(MTabWidget, self).mouseMoveEvent(event)


# class MTabBar(QtWidgets.QTabBar): # Moveable Tab Bar # Does not work since the TabBar is only the space of the tab names but not the free space next to the names...
 #    def __init__(self, parent=None):
 #        super(MTabBar, self).__init__(parent)
 #        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #        self.moving = False
 #        self.setMouseTracking(True)
 #        self.offset = 0
 #
 #    def mousePressEvent(self,event):
 #        if event.button() == QtCore.Qt.LeftButton and self.tabAt(event.pos())==None and self.moving == False:
 #            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
 #            self.moving = True
 #            self.offset = event.globalPos()-self.window().geometry().topLeft()
 #        else:
 #            self.moving = False
 #        super(MTabBar, self).mousePressEvent(event)
 #
 #    def mouseReleaseEvent(self,event):
 #        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #        if event.button() == QtCore.Qt.LeftButton and self.moving:
 #            self.moving = False
 #            pos = self.window().pos()
 #            #if (pos.x() < 0):
 #            #    pos.setX(0)
 #            #    self.window().move(pos)
 #            if (pos.y() < 0):
 #                pos.setY(0)
 #                self.window().move(pos)
 #        else:
 #            self.moving = False
 #            super(MTabBar, self).mouseReleaseEvent(event)
 #
 #    def mouseMoveEvent(self,event):
 #        if self.moving:
 #            self.window().move(event.globalPos()-self.offset)
 #        else:
 #            if self.tabAt(event.pos())!=None:
 #                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
 #            else:
 #                self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #            super(MTabBar, self).mouseMoveEvent(event)


#endregion


#region Windows

class Notification_Window(AWWF):
    def __init__(self,parent = None):
        try:
            super(Notification_Window, self).__init__(parent)
            self.setWindowTitle("Notifications")
            self.standardSize = (900, 500)
            self.resize(*self.standardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation))
            
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.NotificationsWidget = NotificationsWidget(self)
            self.NotificationsWidget.setObjectName("NotificationsWidget")
            self.gridLayout.addWidget(self.NotificationsWidget, 0, 0)
            
            self.setCentralWidget(self.centralwidget)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

class exec_Window(AWWF):
    def __init__(self,parent = None):
        try:
            super(exec_Window, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Code Execution Window")
            self.standardSize = (900, 500)
            self.resize(*self.standardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
                
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.Input_Field = TextEdit(self)
            self.Input_Field.setObjectName("Input_Field")
            self.Input_Field.setTabChangesFocus(False)
            self.Input_Field.setText("# If you have Spyder installed use this to activate the 'Spyder/Dark' syntax highlighter:\nself.highlight()")
            
            self.gridLayout.addWidget(self.Input_Field, 0, 0, 0, 0)
            self.gridLayout.setContentsMargins(0,0,0,0)
            self.setCentralWidget(self.centralwidget)

            self.Input_Field.returnCtrlPressed.connect(self.execute_code)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.__init__")

    def execute_code(self):
        input_text = self.Input_Field.toPlainText()
        try:
            # Set app and window for the local dictionary so that they can be used in the execution
            app = QtWidgets.QApplication.instance() # pylint: disable=unused-variable
            window = QtWidgets.QApplication.instance().MainWindow # pylint: disable=unused-variable
            exec(input_text)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.execute_code",input=input_text)

    def highlight(self):
        try:
            from spyder.utils.syntaxhighlighters import PythonSH
            self.Input_Field_Highlighter = PythonSH(self.Input_Field.document(),color_scheme='Spyder/Dark')
        except:
            pass

class Options_Window(AWWF):
    def __init__(self,parent = None):
        #REMINDER: Add more tabs with other option stuff...
        try:
            super(Options_Window, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Options Window")
            self.standardSize = (900, 500)
            self.resize(*self.standardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
            
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            self.Input_Field = OptionsWidget_1_Appearance(self)
            self.Input_Field.setObjectName("Input_Field")
            
            self.gridLayout.addWidget(self.Input_Field, 0, 0, 0, 0)
            self.gridLayout.setContentsMargins(3,3,3,3)
            self.setCentralWidget(self.centralwidget)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.__init__")


#endregion

# TODO: Move this example to its own file and change the docu of the __init__ accordingly
# ---------------------------------- Main Window ----------------------------------
class _AGe_Test_Window(AWWF):
    def __init__(self, MainApp, parent = None):
        super(_AGe_Test_Window, self).__init__(parent, initTopBar=False)
        self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True)
        self.MainApp = MainApp
        self.MainApp.setMainWindow(self)
        self.standardSize = (906, 634)
        self.resize(*self.standardSize)
        self.setWindowTitle("AGe Test Window")
        self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_CommandLink))

# ---------------------------------- Main ----------------------------------

if __name__ == "__main__":
    latex_installed, dvipng_installed = find_executable('latex'), find_executable('dvipng')
    if latex_installed and dvipng_installed: print("latex and dvipng are installed --> Using pretty LaTeX Display")
    elif latex_installed and not dvipng_installed: print("latex is installed but dvipng was not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    elif not latex_installed and dvipng_installed: print("dvipng is installed but latex was not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    else: print("latex and dvipng were not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    print("Test Window Startup")
    app = Main_App([])
    app.setStyle("fusion")
    window = _AGe_Test_Window(app)
    app.setMainWindow(window)
    print(datetime.datetime.now().strftime('%H:%M:%S:'),"Test Window Started\n")
    window.show()
    sys.exit(app.exec())
