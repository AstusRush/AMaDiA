# Astus General Library Main File

Version = "1.0.3"
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
import datetime
import time
from time import time as timetime
import platform
import errno
import os
import re
import traceback
import pathlib
import getpass

import sympy
from sympy.parsing.sympy_parser import parse_expr

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

from distutils.spawn import find_executable
if find_executable('latex') and find_executable('dvipng'): LaTeX_dvipng_Installed = True
else : LaTeX_dvipng_Installed = False


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
    This class represents all Notifications  \n
    lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
    exc = True or sys.exc_info()
    """
    def __init__(self, lvl=None, msg=None, time=None, input=None, err=None, tb=None, exc=None, win=None, func=None, DplStr=None):
        """
        Creates a new notification object  \n
        lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
        exc = True or sys.exc_info()
        """
        self._time_time = timetime()
        self._init_Values()
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
                if len(str(self.exc_obj))<50:
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
                self.ErrorTraceback = tb
            self.GenerateLevelName()
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
            self.send()

    def _init_Values(self):
        self.exc_type, self.exc_obj, self.exc_tb = None,None,None
        self._time, self.Time, self.Error = None,None,None
        self.Window, self.ErrorTraceback, self.Function = None,None,None
        self.level, self.Level, self.Message = 1,"Notification level 1",None
        self.Input, self.ErrorLongDesc = None,None
        self.DplStr, self.TTStr = None,None
        self.icon = QtGui.QIcon()
        self.Flash = QtWidgets.QApplication.instance().NCF_NONE
        self.itemDict = {"Time:\n":self.Time,"Level: ":self.Level,"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input}
  #---------- send, print ----------#
    def send(self):
        """Displays this notification (This method is thread save but this object should not be modified after using send)"""
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
        self.itemDict contains all relevant data about this notification.
        """
        self.itemDict = {"Time:\n":self.Time,"Level: ":"({})\n{}".format(str(self.level),self.Level),"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input}
        return self.itemDict.items()

    def unpack(self):
        """Returns a tuple (int(level),str(Message),str(Time))"""
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

#endregion

#region Application
# ---------------------------------- Main Application ----------------------------------
AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier
MetaModifier = QtCore.Qt.MetaModifier

class Main_App(QtWidgets.QApplication):
    """Standard AGeLib Application"""
 #
    # See:
    # https://doc.qt.io/qt-5/qapplication.html
    # https://doc.qt.io/qt-5/qguiapplication.html
    # https://doc.qt.io/qt-5/qcoreapplication.html
    S_New_Notification = QtCore.pyqtSignal(NC)
    S_FontChanged = QtCore.pyqtSignal()
    S_advanced_mode_changed = QtCore.pyqtSignal(bool)
    def __init__(self, args):
        super(Main_App, self).__init__(args)
        
        try:
            msg = "Welcome " + getpass.getuser()
        except:
            msg = "Welcome"
        self.LastNotificationText = msg
        self.LastNotificationToolTip = msg
        self.LastNotificationIcon = QtGui.QIcon()

        self.installEventFilter(self)
        self.aboutToQuit.connect(self.SaveClipboard)
        
        self.MainWindow = None
        self.Notification_Window = None
        self.exec_Window = None
        self.optionWindow = None # FEATURE: Standard options window for colour and font
                                 # The Option tabs from AMaDiA should be made in a way to extend the standard options menu
                                 # There must be a cool way to make this work

        self.advanced_mode = False
        
        self.setOrganizationName("Robin Albers")
        self.setOrganizationDomain("https://github.com/AstusRush")
        self.Notification_List = []

        self.Palette , self.BG_Colour , self.TextColour = AGeColour.Dark()
        self.colour_Pack = (self.Palette , self.BG_Colour , self.TextColour)
        self.Colour_Font_Init()

    def setMainWindow(self, TheWindow):
        self.MainWindow = TheWindow
    
    #def notify(self, obj, event): # Reimplementation of notify that does nothing other than redirecting to normal implementation for now...
        #try:
        #    return super().notify(obj, event)
        #except:
        #    ExceptionOutput(sys.exc_info())
        #    print("Caught: ",obj,event)
        #    return False
    
    def eventFilter(self, source, event):
        if event.type() == 6: # QtCore.QEvent.KeyPress
            if event.modifiers() == ControlModifier:
                if event.key() == QtCore.Qt.Key_0: # TODO: Inform the User that this feature exists
                    for w in self.topLevelWidgets():
                        try:
                            w.resize(*w.standardSize)
                        except common_exceptions:
                            w.resize(900, 600)
                        try:
                            frameGm = w.frameGeometry()
                            screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                            centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
                            frameGm.moveCenter(centerPoint)
                            w.move(frameGm.topLeft())
                        except common_exceptions:
                            ExceptionOutput(sys.exc_info())
                    return True
                if event.key() == QtCore.Qt.Key_T:
                    self.Show_exec_Window()
                    return True
            if event.modifiers() == AltModifier:
                if event.key() == QtCore.Qt.Key_A:
                    self.ToggleAdvancedMode(not self.advanced_mode)
                    return True
                #elif event.key() == QtCore.Qt.Key_O:
                #    self.Show_Options()
                #    return True
        elif event.type() == NotificationEvent.EVENT_TYPE:
            self.NotifyUser(event.N)
            return True
        return super(Main_App, self).eventFilter(source, event)

    def SaveClipboard(self):
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
        try:
            self.advanced_mode = checked
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeAdvancedCB:
                        i.AdvancedCB.setChecked(self.advanced_mode)
            self.S_advanced_mode_changed.emit(self.advanced_mode)
        except:
            NC(1,"Exception while toggling advanced mode",exc=sys.exc_info(),func="Main_App.ToggleAdvancedMode",input="{}: {}".format(str(type(checked)),str(checked))).send()

 # ---------------------------------- Colour and Font ----------------------------------
    def Recolour(self, Colour = "Dark"):
        if Colour == "Dark":
            self.Palette , self.BG_Colour , self.TextColour = AGeColour.Dark()
        elif Colour == "Bright":
            self.Palette , self.BG_Colour , self.TextColour = AGeColour.Bright()
        self.colour_Pack = (self.Palette , self.BG_Colour , self.TextColour)
        self.setPalette(self.Palette)
        QtWidgets.QToolTip.setPalette(self.Palette)
        self.init_NCF()

        for w in self.topLevelWidgets():
            for i in w.findChildren(MplWidget):
                i.SetColour(self.BG_Colour, self.TextColour)
            #for i in w.findChildren(Window_Frame_Widget):
            #    i.setPalette(FramePalette)
        
    def Colour_Font_Init(self):
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
                    NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="Main_App.SetFont",win=source.windowTitle()).send()
                except common_exceptions:
                    NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="Main_App.SetFont").send()
                PointSize = 9
        if type(PointSize) != int:
            print(type(PointSize)," is an invalid type for font size (",PointSize,")")
            try:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="Main_App.SetFont",win=source.windowTitle()).send()
            except:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="Main_App.SetFont").send()
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

    def init_NCF(self): # Notification_Flash
        self.NCF_NONE = QtCore.QPropertyAnimation(self)
        
        self.NCF_r = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_r.setDuration(1000)
        self.NCF_r.setLoopCount(1)
        self.NCF_r.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setKeyValueAt(0.5, QtGui.QColor(255, 0, 0))
        self.NCF_r.finished.connect(self.NCF_Finished)
        
        self.NCF_y = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_y.setDuration(1000)
        self.NCF_y.setLoopCount(1)
        self.NCF_y.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setKeyValueAt(0.5, QtGui.QColor(255, 255, 0))
        self.NCF_y.finished.connect(self.NCF_Finished)
        
        self.NCF_g = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_g.setDuration(1000)
        self.NCF_g.setLoopCount(1)
        self.NCF_g.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setKeyValueAt(0.5, QtGui.QColor(0, 255, 0))
        self.NCF_g.finished.connect(self.NCF_Finished)
        
        self.NCF_b = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_b.setDuration(1000)
        self.NCF_b.setLoopCount(1)
        self.NCF_b.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setKeyValueAt(0.5, QtGui.QColor(0, 0, 255))
        self.NCF_b.finished.connect(self.NCF_Finished)

    def _set_FLASH_colour(self, col): # Handles changes to the Property FLASH_colour
        palette = self.Palette
        palette.setColor(QtGui.QPalette.Window, col)
        self.setPalette(palette)
    FLASH_colour = QtCore.pyqtProperty(QtGui.QColor, fset=_set_FLASH_colour) # Defines the Property FLASH_colour
    
    def NCF_Finished(self):
        pass#self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.NoFrame)

    def NotifyUser(self, N):
        """
        Sends the notification N to the user
        """
        if N.l() == 0:
            return
        elif N.l()!=4 or self.advanced_mode:
            Error_Text_TT,icon = self.ListVeryRecentNotifications(N)
            self.LastNotificationText = N.DPS()
            self.LastNotificationToolTip = Error_Text_TT
            self.LastNotificationIcon = icon
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeErrorButton:
                        i.Error_Label.setText(N.DPS())
                        i.Error_Label.setToolTip(Error_Text_TT)
                        i.Error_Label.setIcon(icon)
            if not N.Flash == self.NCF_NONE:
                N.Flash.start()
        
        self.Notification_List.append(N)
        self.S_New_Notification.emit(N)
        # Allow the button to adjust to the new text:
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                if i.IncludeErrorButton:
                    i.parentWidget().adjustSize()
        # REMINDER: Somewhere you need to make the error message "Sorry Dave, I can't let you do this."
        
    def ListVeryRecentNotifications(self, N):
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
    
    def Show_Notification_Window(self):
        self.Notification_Window = Notification_Window(self.Notification_List)
        self.S_New_Notification.connect(self.Notification_Window.NotificationsWidget.AddNotification)
        self.Notification_Window.show()
        self.Notification_Window.activateWindow()

    def Show_exec_Window(self):
        self.exec_Window = exec_Window()
        self.exec_Window.show()
        self.exec_Window.activateWindow()

    #def Show_Options(self):
    #    self.optionWindow.show()
    #    self.optionWindow.activateWindow()

 # ---------------------------------- Other ----------------------------------

#endregion

#region Widgets

class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MplWidget, self).__init__(parent)
        self.background_Colour = QtWidgets.QApplication.instance().BG_Colour
        self.TextColour = QtWidgets.QApplication.instance().TextColour

    def SetColour(self,BG=None,FG=None):
        if BG!=None:
            self.background_Colour = BG
        if FG!=None:
            self.TextColour = FG
        self.HexcolourText = '#%02x%02x%02x' % (int(self.TextColour[0]*255),int(self.TextColour[1]*255),int(self.TextColour[2]*255))
        try:
            self.canvas.fig.set_facecolor(self.background_Colour)
            self.canvas.fig.set_edgecolor(self.background_Colour)
            self.canvas.ax.set_facecolor(self.background_Colour)
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
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas_2D_Plot()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.layout().setContentsMargins(0,0,0,0)
        
    def SetColour(self,BG=None,FG=None):
        super(MplWidget_2D_Plot, self).SetColour(BG,FG)
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
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas_LaTeX(100,100)                  # Create canvas object
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
        return menu
    
    def action_Copy_LaTeX(self):
        try:
            Qt.QApplication.clipboard().setText(self.LaTeX)
        except common_exceptions:
            NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX").send()
        
    def SetColour(self,BG=None,FG=None):
        super(MplWidget_LaTeX, self).SetColour(BG,FG)
        if self.LastCall != False:
            self.Display(self.LastCall[0],self.LastCall[1],self.LastCall[2],self.LastCall[3])
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
    
    def Display(self,Text_L,Text_N,Font_Size,Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        self.LastCall = [Text_L, Text_N, Font_Size, Use_LaTeX]

        #SIMPLIFY: https://matplotlib.org/3.1.1/_modules/matplotlib/text.html#Text _get_rendered_text_width and similar
        # Use this to adjust the size of the "plot" to the Text?

        # You can set Usetex for each individual text object. Example:
        # plt.xlabel('$x$', usetex=True)

        self.LaTeX = Text_L
        self.Text = Text_L
        self.Font_Size = Font_Size * 2
        Notification = NC(lvl=0,win=self.window().windowTitle(),func=str(self.objectName())+".Display")
        #-----------IMPORTANT-----------
        if Use_LaTeX:
            self.Text = Text_L
            self.UseTeX(True)
        else:
            self.UseTeX(False)
            Text_N = Text_N.replace("\limits","") # pylint: disable=anomalous-backslash-in-string
            self.Text = Text_N
        #-----------IMPORTANT-----------
        self.w=9
        self.h=9
        #self.canvas = MplCanvas_LaTeX(self.w+1, self.h+1) 
        #self.scroll.setWidget(self.canvas)
        #self.layout().addWidget(self.scroll)
        #self.canvas.resize(self.w+1, self.h+1)
        #self.canvas.__init__(self.w+1, self.h+1)
        self.canvas.ax.clear() # makes Space for the new text
        
        
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
                      
        """ For Figure(figsize = (100,100),dpi=90)
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
        """
        """ For Figure(figsize = (100,10),dpi=90)
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.195-(self.Font_Size/180)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
        """
        
        self.canvas.ax.axis('off')
        # Show the "graph"
        try:
            self.canvas.draw()
        except common_exceptions:
            Notification = NC(4,"Could not display in Mathmode",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display")
            self.Text = Text_N
            if Use_LaTeX:
                self.UseTeX(True)
            else:
                self.UseTeX(False)
            self.canvas.ax.clear()
            self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
            self.canvas.ax.axis('off')
            #--------------------------
            
            try:
                self.canvas.draw()
            except common_exceptions:
                Notification = NC(2,"Could not display with LaTeX. Displaying with matplotlib instead.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display")
                self.Text = Text_N.replace("\limits","") # pylint: disable=anomalous-backslash-in-string
                self.UseTeX(False)
                self.canvas.ax.clear()
                self.canvas.ax.set_title(self.Text,
                          loc = "left",
                          #x=-0.12,
                          y=(1.15-(self.Font_Size/5000)),
                          horizontalalignment='left',
                          verticalalignment='top',
                          fontsize=self.Font_Size,
                          color = self.TextColour
                          ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                          ec="0.1", pad=0.1, alpha=0)
                          )
                self.canvas.ax.axis('off')
                #--------------------------
                try:
                    self.canvas.draw()
                except common_exceptions:
                    Notification = NC(1,"Could not display at all.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".Display")
                    self.UseTeX(False)
                    self.canvas.ax.clear()
                    if Use_LaTeX:
                        ErrorText = "The text can't be displayed. Please send your input and a description of your problem to the developer"
                    else:
                        ErrorText = "The text can't be displayed. Please note that many things can't be displayed without LaTeX Mode."
                        if not LaTeX_dvipng_Installed:
                            ErrorText += "\n Please install LaTeX (and dvipng if it is not already included in your LaTeX distribution)"
                    self.canvas.ax.set_title(ErrorText,
                            loc = "left",
                            #x=-0.12,
                            y=(1.15-(self.Font_Size/5000)),
                            horizontalalignment='left',
                            verticalalignment='top',
                            fontsize=self.Font_Size,
                            color = self.TextColour
                            ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,
                            ec="0.1", pad=0.1, alpha=0)
                            )
                    self.canvas.ax.axis('off')
                    try:
                        self.canvas.draw()
                    except common_exceptions:
                        Notification = NC(1,"Critical Error: MatPlotLib Display seems broken. Could not display anything",exc=sys.exc_info(),input=ErrorText,win=self.window().windowTitle(),func=str(self.objectName())+".Display")
                
        finally:
            self.UseTeX(False)
            return Notification

# -----------------------------------------------------------------------------------------------------------------

class ListWidget(QtWidgets.QListWidget):
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
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(ListWidget).keyPressEvent",input=str(event)).send()
            super(ListWidget, self).keyPressEvent(event)

class NotificationsWidget(QtWidgets.QSplitter):
    def __init__(self, parent=None, Notifications=[]):
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

        for i in Notifications:
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
    def __init__(self, parent=None):
        super(NotificationListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)

class NotificationInfoWidget(ListWidget):
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
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).keyPressEvent",input=str(event)).send()
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
                    NC(msg="Could not display{}".format(str(k)),exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails").send()
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails").send()

# -----------------------------------------------------------------------------------------------------------------

class ATextEdit(QtWidgets.QTextEdit):
    returnPressed = QtCore.pyqtSignal()
    returnCtrlPressed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.installEventFilter(self)
        self.setTabChangesFocus(True)
        
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
                and event.modifiers() == QtCore.Qt.ControlModifier):
            source.returnCtrlPressed.emit()
        if (event.type() == QtCore.QEvent.KeyPress # Connects to returnPressed
                and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
            source.returnPressed.emit()
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
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.installEventFilter(self)

        # FEATURE: Make subscript and superscript work and add an option to disable it (fro small font)
        # See https://www.qtcentre.org/threads/38633-(SOLVED)-QTextEdit-subscripted-text for a startingpoint
        
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
                and event.modifiers() == QtCore.Qt.ControlModifier):
            source.returnCtrlPressed.emit()
            return True
        return super(TextEdit, self).eventFilter(source, event)

class LineEdit(ATextEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        
        QTextEditFontMetrics =  QtGui.QFontMetrics(self.font())
        self.QTextEditRowHeight = QTextEditFontMetrics.lineSpacing()
        self.setFixedHeight(2 * self.QTextEditRowHeight)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.installEventFilter(self)
        # Connect Signals
        #self.textChanged.connect(self.validateCharacters) # Turned off to fix Undo/Redo # MAYBE: Try to make both work together

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
            QTextEdFontMetrics =  QtGui.QFontMetrics(source.font())
            source.QTextEdRowHeight = QTextEdFontMetrics.lineSpacing()+9
            source.setFixedHeight(source.QTextEdRowHeight)
        if (event.type() == QtCore.QEvent.KeyPress # Move to beginning if up key pressed
                and event.key() == QtCore.Qt.Key_Up):
            cursor = source.textCursor()
            cursor.movePosition(cursor.Start)
            source.setTextCursor(cursor)
            return True
        if (event.type() == QtCore.QEvent.KeyPress # Move to end if down key pressed
                and event.key() == QtCore.Qt.Key_Down):
            cursor = source.textCursor()
            cursor.movePosition(cursor.End)
            source.setTextCursor(cursor)
            return True
        if (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
            source.returnPressed.emit()
            return True
        return super(LineEdit, self).eventFilter(source, event)

    #def validateCharacters(self):
    #    forbiddenChars = ['\n']
    #    cursor = self.textCursor()
    #    curPos = cursor.position()
    #    Text = self.toPlainText()
    #    found = 0
    #    for e in forbiddenChars:
    #        found += Text.count(e)
    #        Text = Text.replace(e, '')
    #    
    #    self.blockSignals(True)
    #    self.setText(Text)
    #    self.blockSignals(False)
    #    try:
    #        cursor.setPosition(curPos-found)
    #        self.setTextCursor(cursor)
    #    except common_exceptions:
    #        ExceptionOutput(sys.exc_info())
    #    super(LineEdit, self).validateCharacters()

    def insertFromMimeData(self,Data):
        if Data.hasText():
            text = Data.text()
            #text = text.replace('\n', ' + ').replace('\r', '')
            lines = text.splitlines()
            if len(lines)>1:
                text = "( "+" ) + ( ".join(lines)+" )"
                self.insertPlainText(text)
            else:
                super(LineEdit, self).insertFromMimeData(Data)
            #Data.setText(text)
        else:
            super(LineEdit, self).insertFromMimeData(Data)

# -----------------------------------------------------------------------------------------------------------------

class TableWidget(QtWidgets.QTableWidget):
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

#endregion

#region AWWF

class AWWF(QtWidgets.QMainWindow): # Astus Window With Frame
    def __init__(self, parent = None, includeTopBar=True, initTopBar=True, includeStatusBar=True):
        super(AWWF, self).__init__(parent)
        self.includeTopBar, self.includeStatusBar = includeTopBar, includeStatusBar
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

 #####################
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
 #####################

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

 #####################

    def showNormal(self):
        self.AWWF_CentralWidget.showFrame()
        super(AWWF, self).showNormal()
    def show(self):
        self.AWWF_CentralWidget.showFrame()
        super(AWWF, self).show()
    def showMaximized(self):
        self.AWWF_CentralWidget.hideFrame()
        super(AWWF, self).showMaximized()
    def showFullScreen(self):
        self.AWWF_CentralWidget.hideFrame()
        super(AWWF, self).showFullScreen()

    def eventFilter(self, source, event):
        #if event.type() == 6: # QtCore.QEvent.KeyPress
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

class TopBar_Widget(QtWidgets.QWidget): # FEATURE: Make an advanced mode checkbox 
    # Make an advanced mode checkbox with default=False
    # integrate it with the application using a variable (Main_App: self.advanced_mode), a function in Main_App to set/unset and signals
    # Update AMaDiA to use this and change the advanced mode to be compatible with the new one
    # Add an application wide shortcut (alt+A) to toggle the advanced mode
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
        self.layout().addWidget(self.CloseButton, 0, 104, 1, 1,QtCore.Qt.AlignRight)
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
        self.layout().addWidget(self.MaximizeButton, 0, 103, 1, 1,QtCore.Qt.AlignRight)
        self.MaximizeButton.setText("🗖")
        self.MaximizeButton.installEventFilter(self)
        self.MaximizeButton.setAutoRaise(True)
        self.MaximizeButton.setSizePolicy(self.ButtonSizePolicy)

        self.MinimizeButton = QtWidgets.QToolButton(self)
        self.MinimizeButton.setObjectName("MinimizeButton")
        self.layout().addWidget(self.MinimizeButton, 0, 102, 1, 1,QtCore.Qt.AlignRight)
        self.MinimizeButton.setText("🗕")
        self.MinimizeButton.installEventFilter(self)
        self.MinimizeButton.setAutoRaise(True)
        self.MinimizeButton.setSizePolicy(self.ButtonSizePolicy)

        self.MoveMe = QtWidgets.QLabel(self)
        self.MoveMe.setObjectName("MoveMe")
        self.layout().addWidget(self.MoveMe, 0, 101, 1, 1,QtCore.Qt.AlignRight)
        self.MoveMe.setText("  🖐  ")#▨#🖐
        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

        self.CloseButton.clicked.connect(self.Exit)
        self.MaximizeButton.clicked.connect(self.ToggleMinMax)
        self.MinimizeButton.clicked.connect(self.Minimize)

        try:
            #self.window().menuBar().installEventFilter(self)
            if IncludeMenu:
                self.Menu = QtWidgets.QToolButton(self)
                self.Menu.setObjectName("Menu")
                self.layout().addWidget(self.Menu, 0, 100, 1, 1,QtCore.Qt.AlignRight)
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
            self.layout().addWidget(self.AdvancedCB, 0, 99, 1, 1,QtCore.Qt.AlignRight)
            self.AdvancedCB.clicked.connect(QtWidgets.QApplication.instance().ToggleAdvancedMode)

        if IncludeFontSpinBox:
            self.Font_Size_spinBox = QtWidgets.QSpinBox(self)
            self.Font_Size_spinBox.setMinimum(5)
            self.Font_Size_spinBox.setMaximum(25)
            self.Font_Size_spinBox.setProperty("value", self.font().pointSize())
            self.Font_Size_spinBox.setObjectName("Font_Size_spinBox")
            self.layout().addWidget(self.Font_Size_spinBox, 0, 98, 1, 1,QtCore.Qt.AlignRight)
            self.Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)

        if IncludeErrorButton:
            self.Error_Label = QtWidgets.QPushButton(self)
            self.Error_Label.setObjectName("Error_Label")
            self.Error_Label.setText(QtWidgets.QApplication.instance().LastNotificationText)
            self.Error_Label.setToolTip(QtWidgets.QApplication.instance().LastNotificationToolTip)
            self.Error_Label.setIcon(QtWidgets.QApplication.instance().LastNotificationIcon)
            self.layout().addWidget(self.Error_Label, 0, 97, 1, 1,QtCore.Qt.AlignRight)
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
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="TopBar_Widget.mouseReleaseEvent").send()

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
    def __init__(self, parent=None):
        super(MenuAction, self).__init__(parent)
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
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MMenuBar.mouseReleaseEvent").send()
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
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except common_exceptions:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MTabWidget.mouseReleaseEvent").send()
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
    def __init__(self,Notifications,parent = None):
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
            
            self.NotificationsWidget = NotificationsWidget(self, Notifications)
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


            self.gridLayout.addWidget(self.Input_Field, 0, 0, 0, 0)
            self.setCentralWidget(self.centralwidget)

            self.Input_Field.returnCtrlPressed.connect(self.execute_code)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.__init__").send()

    def execute_code(self):
        input_text = self.Input_Field.toPlainText()
        try:
            exec(input_text)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.execute_code",input=input_text).send()

#endregion


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
    sys.exit(app.exec_())
