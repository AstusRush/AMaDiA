# This Python file uses the following encoding: utf-8
Version = "0.13.0"
Author = "Robin \'Astus\' Albers"
WindowTitle = "AMaDiA v"
WindowTitle+= Version
WindowTitle+= " by "
WindowTitle+= Author

import datetime
if __name__ == "__main__":
    print()
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    print(WindowTitle)
    print("Loading Modules")#,end="")

from distutils.spawn import find_executable
import sys
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.Qt import QApplication, QClipboard
import PyQt5.Qt as Qt
import socket
import time
import platform
import errno
import os
import pathlib
import sympy
from sympy.parsing.sympy_parser import parse_expr
import importlib
import re

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors

# To Convert ui to py: (Commands for Anaconda Prompt)
# cd C:"\Users\Robin\Desktop\Projects\AMaDiA"
# pyuic5 AMaDiAUI.ui -o AMaDiAUI.py
from AMaDiAUI import Ui_AMaDiA_Main_Window
import AMaDiA_Widgets as AW
import AMaDiA_Functions as AF
import AMaDiA_Classes as AC
import AMaDiA_ReplacementTables as ART
import AMaDiA_Colour
import AMaDiA_Threads as AT
import AstusChat_Client
import AstusChat_Server

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
from Test_Input import Test_Input
import reprlib
r = reprlib.Repr()
r.maxlist = 20       # max elements displayed for lists
r.maxarray = 20       # max elements displayed for arrays
r.maxother = 500       # max elements displayed for other including np.ndarray
r.maxstring = 40    # max characters displayed for strings

try:
    from keyboard_master import keyboard
except AF.common_exceptions :
    AF.ExceptionOutput(sys.exc_info())

np.set_printoptions(threshold=100)

AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier


class MainApp(QtWidgets.QApplication):
    def __init__(self, args):
        super(MainApp, self).__init__(args)
    #    self.installEventFilter(self)
    #
    #def notify(self, obj, event): # Reimplementation of notify that does nothing other than redirecting to normal implementation for now...
    #    try:
    #        return super().notify(obj, event)
    #    except:
    #        AF.ExceptionOutput(sys.exc_info())
    #        print("Caught: ",obj,event)
    #        return False
    #
    #def eventFilter(self, source, event): #DOES NOT INTERCEPT ENOUGH to nagate all AltGr Stuff
    #    try:
    #        pass#print(event.key())
    #    except AF.common_exceptions:
    #        pass
    #    if event.type() == QtCore.QEvent.KeyPress and event.key() == 16777251:#event.modifiers() == (ControlModifier | AltModifier): #DOES NOT INTERCEPT ENOUGH
    #        #print("AltGr")
    #        return True
    #    return super(MainApp, self).eventFilter(source, event)


class AMaDiA_Main_Window(QtWidgets.QMainWindow, Ui_AMaDiA_Main_Window):
    def __init__(self,MainApp, parent = None):
        super(AMaDiA_Main_Window, self).__init__(parent)
        sympy.init_printing() # doctest: +SKIP
        self.MainApp = MainApp
        self.setupUi(self)
        

        # Create Folders if not already existing
        self.CreateFolders()
        
        # Set UI variables
        #Set starting tabs
        self.Tab_3_TabWidget.setCurrentIndex(0)
        self.Tab_5_tabWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        
        #Set Splitter Start Values
        self.Tab_2_UpperSplitter.setSizes([163,699])
        self.Tab_2_LowerSplitter.setSizes([391,70])
        self.Tab_3_splitter.setSizes([297,565])
        #To cofigure use:
        #print(self.Tab_2_UpperSplitter.sizes())
        #print(self.Tab_2_LowerSplitter.sizes())
        #print(self.Tab_3_splitter.sizes())
        
        #Set Tab 4 Matrix Input Column Width
        for i in range(self.Tab_5_1_Matrix_Input.columnCount()):
            self.Tab_5_1_Matrix_Input.setColumnWidth(i,75)
        
        # Initialize important variables and lists
        self.ans = "1"
        self.ThreadList = []
        self.Tab_2_Eval_checkBox.setCheckState(1)
        #QtWidgets.QCheckBox.setCheckState(1)
        
        
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AMaDiA" , WindowTitle))
        
        
        self.installEventFilter(self)
        # Set up context menus for the histories
        for i in self.findChildren(QtWidgets.QListWidget):
            i.installEventFilter(self)
        # Set up text input related Event Handlers
        for i in self.findChildren(QtWidgets.QTextEdit):
            i.installEventFilter(self)
        for i in self.findChildren(QtWidgets.QLineEdit):
            i.installEventFilter(self)
        for i in self.findChildren(QtWidgets.QTableWidget):
            i.installEventFilter(self)
        
        # Activate Pretty-LaTeX-Mode if the Computer supports it
        if AF.LaTeX_dvipng_Installed:
            self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.setEnabled(True)
            self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.setChecked(True)
        
        # Run other init methods
        self.ConnectSignals()
        self.Colour_Font_Init()
        self.OtherContextMenuSetup()
        self.InstallSyntaxHighlighter()
        self.INIT_Animation()

        # Initialize the first equation in Tab 4
        self.Tab_5_2_New_Equation_Name_Input.setText("Equation 1")
        self.Tab_5_F_New_Equation()
        self.Tab_5_2_New_Equation_Name_Input.clear()
        self.Tab_5_1_Dimension_Input.setText(" 3x3 ")
        self.Tab_5_Currently_Displayed = ""
        self.Tab_5_Currently_Displayed_Solution = ""

        # Other things:
        
        #Check if this fixes the bug on the Laptop --> The Bug is fixed but the question remains wether this is what fixed it
        self.Tab_3_F_Clear()
        #One Little Bug Fix:
            #If using LaTeX Display in LaTeX Mode before using the Plotter for the first time it can happen that the plotter is not responsive until cleared.
            #Thus the plotter is now leared on program start to **hopefully** fix this...
            #If it does not fix the problem a more elaborate method is required...
            # A new variable that checks if the plot has already been used and if the LaTeX view has been used.
            # If the first is False and the seccond True than clear when the plot button is pressed and cjange the variables to ensure that this only happens once
            #       to not accidentially erase the plots of the user as this would be really bad...

        self.Tab_1_InputField.setFocus()

        
# ---------------------------------- Init and Maintanance ----------------------------------

    def ConnectSignals(self):
        self.Menubar_Main_Options_action_Reload_Modules.triggered.connect(self.ReloadModules)
        self.Menubar_Main_Options_action_WindowStaysOnTop.changed.connect(self.ToggleWindowStaysOnTop)

        self.Menubar_Main_Chat_action_Open_Client.triggered.connect(self.OpenClient)
        self.Menubar_Main_Chat_action_Open_Server.triggered.connect(self.OpenServer)

        self.TopBar_Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)
        self.TopBar_Syntax_Highlighter_checkBox.toggled.connect(self.ToggleSyntaxHighlighter)
        self.TopBar_MathRemap_checkBox.toggled.connect(self.ToggleRemapper)
        
        self.Tab_1_InputField.returnPressed.connect(self.Tab_1_F_Calculate_Field_Input)
        
        self.Tab_2_ConvertButton.clicked.connect(self.Tab_2_F_Convert)
        
        self.Tab_3_Button_Plot.clicked.connect(self.Tab_3_F_Plot_Button)
        self.Tab_3_Formula_Field.returnPressed.connect(self.Tab_3_F_Plot_Button)
        self.Tab_3_Button_Clear.clicked.connect(self.Tab_3_F_Clear)
        self.Tab_3_Button_Plot_SymPy.clicked.connect(self.Tab_3_F_Sympy_Plot_Button)
        self.Tab_3_RedrawPlot_Button.clicked.connect(self.Tab_3_F_RedrawPlot)
        self.Tab_3_Button_SavePlot.clicked.connect(self.action_Tab_3_Display_SavePlt)
        
        self.Tab_5_FormulaInput.returnPressed.connect(self.Tab_5_F_Update_Equation)
        self.Tab_5_1_Dimension_Input.returnPressed.connect(self.Tab_5_F_Config_Matrix_Dim)
        self.Tab_5_1_Configure_Button.clicked.connect(self.Tab_5_F_Config_Matrix_Dim)
        self.Tab_5_1_Name_Input.returnPressed.connect(self.Tab_5_F_Save_Matrix)
        self.Tab_5_1_Save_Matrix_Button.clicked.connect(self.Tab_5_F_Save_Matrix)
        self.Tab_5_2_New_Equation_Button.clicked.connect(self.Tab_5_F_New_Equation)
        self.Tab_5_2_New_Equation_Name_Input.returnPressed.connect(self.Tab_5_F_New_Equation)
        self.Tab_5_2_Load_Selected_Button.clicked.connect(self.Tab_5_F_Load_Selected_Equation)
    
    def Colour_Font_Init(self):
        self.FontFamily = "Arial"
        self.Palette , self.BG_Colour , self.TextColour = AMaDiA_Colour.Dark()
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.setFont(font)
        self.setPalette(self.Palette)
        #self.Palette = palette
        #self.BG_Colour = BG
        #self.TextColour = FG
        for i in self.findChildren(AW.MplWidget):
            i.SetColour(self.BG_Colour, self.TextColour)

        #self.Error_Palette = AMaDiA_Colour.Red_ERROR()[0] # Currently not in use

    def SetFont(self,Family = None, PointSize = 0):
        if Family == None:
            Family = self.FontFamily
        else:
            self.FontFamily = Family
        if type(PointSize) == str:
            PointSize = int(PointSize)
        if PointSize <= 5:
            PointSize = self.TopBar_Font_Size_spinBox.value()
        else:
            # setValue emits ValueChanged and thus calls ChangeFontSize if the new Value is different from the old one.
            # If the new Value is the same it is NOT emited.
            # To ensure thatthis behaves correctly either way the signals are blocked while changeing the Value.
            self.TopBar_Font_Size_spinBox.blockSignals(True)
            self.TopBar_Font_Size_spinBox.setValue(PointSize)
            self.TopBar_Font_Size_spinBox.blockSignals(False)
        
        font = QtGui.QFont()
        font.setFamily(Family)
        font.setPointSize(PointSize)
        self.setFont(font)


    def Recolour(self, Colour = "Dark"):
        if Colour == "Dark":
            self.Palette , self.BG_Colour , self.TextColour = AMaDiA_Colour.Dark()
        elif Colour == "Bright":
            self.Palette , self.BG_Colour , self.TextColour = AMaDiA_Colour.Bright()
        self.setPalette(self.Palette)
        #self.Palette = palette
        #self.BG_Colour = BG
        #self.TextColour = FG
        for i in self.findChildren(AW.MplWidget):
            i.SetColour(self.BG_Colour, self.TextColour)
        
        
    def ChangeFontSize(self):
        Size = self.TopBar_Font_Size_spinBox.value()
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(Size)
        self.setFont(newFont)
        self.centralwidget.setFont(newFont)
        self.Menubar_Main.setFont(newFont)
        self.Menubar_Main_Options.setFont(newFont)

    def InstallSyntaxHighlighter(self):
        #self.Tab_1_InputField_BracesHighlighter = AW.BracesHighlighter(self.Tab_1_InputField.document())
        pass

    def INIT_Animation(self):
        self.init_ErrorFlash()
        
    def CreateFolders(self):
        self.pathOK = False
        # Find out Path
        self.selfPath = os.path.abspath(__file__)
        self.FolderPath = os.path.dirname(__file__)
        # Check if the path that was returned is correct
        fpath = self.FolderPath
        if platform.system() == 'Windows':
            fpath += "\\AMaDiA.py"
        elif platform.system() == 'Linux':
            fpath += "/AMaDiA.py"
        fpath = pathlib.Path(fpath)
        if fpath.is_file():
            self.pathOK = True
            # Create Plots folder to save plots
            self.PlotPath = self.FolderPath
            if platform.system() == 'Windows':
                self.PlotPath += "\\Plots\\"
            elif platform.system() == 'Linux':
                self.PlotPath += "/Plots/"
            try:
                os.makedirs(self.PlotPath[:-1])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    AF.ExceptionOutput(sys.exc_info())
                    self.pathOK = False
            # Create Config folder to save configs
            self.ConfigFolderPath = self.FolderPath
            if platform.system() == 'Windows':
                self.ConfigFolderPath += "\\Config\\"
            elif platform.system() == 'Linux':
                self.ConfigFolderPath += "/Config/"
            try:
                os.makedirs(self.ConfigFolderPath[:-1])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    AF.ExceptionOutput(sys.exc_info())
                    self.pathOK = False

    def ToggleRemapper(self):
        try:
            if self.TopBar_MathRemap_checkBox.isChecked():
                altgr = "altgr+"
                altgrshift = "altgr+shift+"
                #keyboard.add_hotkey("shift",keyboard.release, args=("altgr"),trigger_on_release=True)
                #keyboard.block_key("AltGr")
                #keyboard.add_hotkey("control+alt+altgr",keyboard.release, args=("altgr"), suppress=True)
                #keyboard.add_hotkey("control+alt+altgr+shift",keyboard.release, args=("altgr+shift"), suppress=True)
                for i in ART.KR_Map:
                    if i[2] != " ":
                        Key = altgr + i[0]
                        keyboard.add_hotkey(Key, keyboard.write, args=(i[2]), suppress=True, trigger_on_release=True)
                    if i[3] != " ":
                        Key = altgrshift + i[0]
                        keyboard.add_hotkey(Key, keyboard.write, args=(i[3]), suppress=True, trigger_on_release=True)
            else:
                keyboard.clear_all_hotkeys()
        except AF.common_exceptions :
            Error = AF.ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)
            try:
                print(i,Key)
            except AF.common_exceptions :
                pass

# ---------------------------------- Error Handling ----------------------------------
    def init_ErrorFlash(self):
        self.ErrorFlash = QtCore.QPropertyAnimation(self,b'ERROR_colour')
        self.ErrorFlash.setDuration(1000)
        self.ErrorFlash.setLoopCount(1)
        self.ErrorFlash.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.ErrorFlash.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.ErrorFlash.setKeyValueAt(0.5, QtGui.QColor(255, 0, 0))
        self.ErrorFlash.finished.connect(self.ErrorFlashFinished)
        
        self.WarningFlash = QtCore.QPropertyAnimation(self,b'ERROR_colour')
        self.WarningFlash.setDuration(1000)
        self.WarningFlash.setLoopCount(1)
        self.WarningFlash.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.WarningFlash.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.WarningFlash.setKeyValueAt(0.5, QtGui.QColor(255, 255, 0))
        self.WarningFlash.finished.connect(self.ErrorFlashFinished)

        self.NotificationFlash = QtCore.QPropertyAnimation(self,b'ERROR_colour')
        self.NotificationFlash.setDuration(1000)
        self.NotificationFlash.setLoopCount(1)
        self.NotificationFlash.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NotificationFlash.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NotificationFlash.setKeyValueAt(0.5, QtGui.QColor(0, 0, 255))
        self.NotificationFlash.finished.connect(self.ErrorFlashFinished)

    def _set_ERROR_colour(self, col): # Handles chnges to the Property ERROR_colour
        palette = self.Palette
        palette.setColor(QtGui.QPalette.Window, col)
        self.setPalette(palette)
    ERROR_colour = QtCore.pyqtProperty(QtGui.QColor, fset=_set_ERROR_colour) # Defines the Property ERROR_colour

    def NotifyUser(self,Type,Text,Time=None):
        """1 = Error , 2 = Warning , 3 = Notification"""
        if Type == 1:
            self.Error_Display(Text,Time)
        elif Type == 2:
            self.Warning_Display(Text,Time)
        elif Type == 3:
            self.Notification_Display(Text,Time)
        else:
            nText = "Notification of type "+str(Type)
            nText += " (Type unknown):\n"
            nText += Text
            self.Warning_Display(nText,Time)

    def Error_Display(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Error at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        #self.TopBar_Error_Label.setFrameShadow(QtWidgets.QFrame.Plain)

        self.ErrorFlash.start()

    def Warning_Display(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Warning at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        #self.TopBar_Error_Label.setFrameShadow(QtWidgets.QFrame.Plain)

        self.WarningFlash.start()

    def Notification_Display(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Notification at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        #self.TopBar_Error_Label.setFrameShadow(QtWidgets.QFrame.Plain)

        self.NotificationFlash.start()

    def ErrorFlashFinished(self):
        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.NoFrame)

# ---------------------------------- Option Toolbar Funtions ----------------------------------
    def ReloadModules(self):
        AC.ReloadModules()
        AF.ReloadModules()
        AC.ReloadModules()
        AT.ReloadModules()
        AW.ReloadModules()
        importlib.reload(AW)
        importlib.reload(AF)
        importlib.reload(AC)
        importlib.reload(ART)
        importlib.reload(AT)
        importlib.reload(AMaDiA_Colour)
        
        self.ColourMain()

    def ToggleSyntaxHighlighter(self):
        state = self.TopBar_Syntax_Highlighter_checkBox.isChecked()
        for i in self.findChildren(AW.ATextEdit):
            i.Highlighter.enabled = state

    def ToggleWindowStaysOnTop(self):
        if self.Menubar_Main_Options_action_WindowStaysOnTop.isChecked():
            print("OnTop")
            self.setWindowFlags(QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
        else:
            print("Normal")
            self.setWindowFlags(QtCore.Qt.WindowFlags())
            self.show()

    def RUNTEST(self):
        for i in Test_Input:
            self.Tab_1_InputField.setText(i)
            self.Tab_1_F_Calculate_Field_Input()
            time.sleep(0.1)
        Text = "Expected Entries after all calulations: "+str(len(Test_Input))
        print(Text)
        self.Tab_1_InputField.setText(Text)


# ---------------------------------- Chat Toolbar Funtions ----------------------------------

    def OpenClient(self):
        self.Chat = AstusChat_Client.MainWindow(self.Palette,self.FontFamily)
        self.Chat.show()

    def OpenServer(self):
        self.Sever = AstusChat_Server.MainWindow(self.Palette,self.FontFamily)
        self.Sever.show()


# ---------------------------------- Events and Context Menu ----------------------------------
    def OtherContextMenuSetup(self):
        self.Tab_3_Display.canvas.mpl_connect('button_press_event', self.Tab_3_Display_Context_Menu)
        self.Tab_5_Display.canvas.mpl_connect('button_press_event', self.Tab_5_Display_Context_Menu)
        
        
 # ---------------------------------- 2D Plot Context Menu ---------------------------------- 
    def Tab_3_Display_Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            action = menu.addAction('Save Plot')
            action.triggered.connect(self.action_Tab_3_Display_SavePlt)
            cursor = QtGui.QCursor()
            menu.exec_(cursor.pos())
            
 # ---------------------------------- Multi-Dim Display Context Menu ---------------------------------- 
    def Tab_5_Display_Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            action = menu.addAction('Copy Text')
            action.triggered.connect(self.action_Tab_5_Display_Copy_Displayed)
            action = menu.addAction('Copy Solution')
            action.triggered.connect(self.action_Tab_5_Display_Copy_Displayed_Solution)
            cursor = QtGui.QCursor()
            menu.exec_(cursor.pos())
    
    
# ---------------------------------- Event Filter ----------------------------------
    def eventFilter(self, source, event): # TODO: Add more
        #print(event.type())
     # ---------------------------------- History Context Menu ----------------------------------
        if (event.type() == QtCore.QEvent.ContextMenu and
            (source is self.Tab_1_History 
                or source is self.Tab_2_History 
                or source is self.Tab_3_History 
                or source is self.Tab_5_History #TODO: This is temporary. Implement this context menu properly
                )and source.itemAt(event.pos())):
            menu = QtWidgets.QMenu()
            action = menu.addAction('Copy Text')
            action.triggered.connect(lambda: self.action_H_Copy_Text(source,event))
            action = menu.addAction('Copy LaTeX')
            action.triggered.connect(lambda: self.action_H_Copy_LaTeX(source,event))
            if self.Menubar_Main_Options_action_Advanced_Mode.isChecked():
                action = menu.addAction('+ Copy Input')
                action.triggered.connect(lambda: self.action_H_Copy_Input(source,event))
                action = menu.addAction('+ Copy cString')
                action.triggered.connect(lambda: self.action_H_Copy_cstr(source,event))
            if source.itemAt(event.pos()).data(100).Evaluation != "Not evaluated yet.":
                action = menu.addAction('Copy Solution')
                action.triggered.connect(lambda: self.action_H_Copy_Solution(source,event))
            menu.addSeparator()
            # TODO: Maybe? Only "Calculate" if the equation has not been evaluated yet or if in Advanced Mode? Maybe? Maybe not?
            # It currently is handy to have it always because of the EvalF thing...
            action = menu.addAction('Calculate')
            action.triggered.connect(lambda: self.action_H_Calculate(source,event))
            action = menu.addAction('Display LaTeX')
            action.triggered.connect(lambda: self.action_H_Display_LaTeX(source,event))
            if source.itemAt(event.pos()).data(100).Evaluation != "Not evaluated yet.":
                action = menu.addAction('Display LaTeX Solution')
                action.triggered.connect(lambda: self.action_H_Display_LaTeX_Solution(source,event))
            menu.addSeparator()
            if source.itemAt(event.pos()).data(100).plot_data_exists :
                action = menu.addAction('Load Plot')
                action.triggered.connect(lambda: self.action_H_Load_Plot(source,event))
            if source.itemAt(event.pos()).data(100).plottable :
                action = menu.addAction('New Plot')
                action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
            elif self.Menubar_Main_Options_action_Advanced_Mode.isChecked() :
                action = menu.addAction('+ New Plot')
                action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
            if source.itemAt(event.pos()).data(100).plot_data_exists and self.Menubar_Main_Options_action_Advanced_Mode.isChecked():
                menu.addSeparator()
                action = menu.addAction('+ Copy x Values')
                action.triggered.connect(lambda: self.action_H_Copy_x_Values(source,event))
                action = menu.addAction('+ Copy y Values')
                action.triggered.connect(lambda: self.action_H_Copy_y_Values(source,event))
            menu.addSeparator()
            action = menu.addAction('Delete')
            action.triggered.connect(lambda: self.action_H_Delete(source,event))
            menu.exec_(event.globalPos())
            return True
     # ---------------------------------- Tab_5 Matrix List Context Menu ----------------------------------
        elif (event.type() == QtCore.QEvent.ContextMenu and
            (source is self.Tab_5_Matrix_List)and source.itemAt(event.pos())):
            menu = QtWidgets.QMenu()
            action = menu.addAction('Load to Editor')
            action.triggered.connect(lambda: self.action_Tab_5_M_Load_into_Editor(source,event))
            action = menu.addAction('Display')
            action.triggered.connect(lambda: self.action_Tab_5_M_Display(source,event))
            action = menu.addAction('Copy as String')
            action.triggered.connect(lambda: self.action_Tab_5_M_Copy_string(source,event))
            action = menu.addAction('Delete')
            action.triggered.connect(lambda: self.action_Tab_5_M_Delete(source,event))
            menu.exec_(event.globalPos())
            return True
     # ---------------------------------- LineEdit Events ----------------------------------
        elif type(source) == AW.LineEdit:
            if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
                QTextEdFontMetrics =  QtGui.QFontMetrics(source.font())
                source.QTextEdRowHeight = QTextEdFontMetrics.lineSpacing()+9
                source.setFixedHeight(source.QTextEdRowHeight)
            if (event.type() == QtCore.QEvent.KeyPress # Connects to returnPressed
            and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
                source.returnPressed.emit()
                return True
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
     # ---------------------------------- Tab_2_InputField ----------------------------------
        elif (event.type() == QtCore.QEvent.KeyPress  # Tab_2_InputField: use crtl+return to convert
              and source is self.Tab_2_InputField # TODO: Maybe use return to convert and shift+return for new lines...
              and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
              and event.modifiers() == QtCore.Qt.ControlModifier):
            self.Tab_2_F_Convert()
            return True
     # ---------------------------------- Remap Keys to allow for Math Unicode Symbol input ----------------------------------
        #if event.type() == QtCore.QEvent.KeyPress : print(event.key())
        #if event.type() == QtCore.QEvent.KeyPress and event.key() == 16777251:#event.modifiers() == (ControlModifier | AltModifier): #DOES NOT INTERCEPT ENOUGH
        #    print("AltGr")
        #    return True
        #if self.TopBar_MathRemap_checkBox.isChecked():    #DOES NOT WORK WITH QTableWidget
        #    if event.type() == QtCore.QEvent.KeyPress and event.modifiers() == (ControlModifier | AltModifier):
        #        print("AltGr")
        #        return True
        #    if event.type() == QtCore.QEvent.KeyPress : print(source)
        #    if event.type() == QtCore.QEvent.KeyPress and issubclass(type(source), (QtWidgets.QTextEdit, QtWidgets.QLineEdit, QtWidgets.QTableWidget)):
        #        print(event.key(), event.text())
        #        if event.key() == QtCore.Qt.Key_1 and event.text() in ["1","!"]:
        #            if event.modifiers() == GroupSwitchModifier or event.modifiers() == (ControlModifier | AltModifier):
        #                #event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,8747,event.modifiers(),text="∫")
        #                event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers(),text="2")#∫")
        #                self.MainApp.sendEvent(source,event)
        #                return True
        #            elif event.modifiers() == (GroupSwitchModifier | ShiftModifier) or event.modifiers() == (ControlModifier | AltModifier | ShiftModifier):
        #                event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,8747,event.modifiers(),text="₁")
        #                self.MainApp.sendEvent(source,event)
        #                return True


        #if self.TopBar_MathRemap_checkBox.isChecked():    #DOES NOT WORK WITH QTableWidget
        #    if event.type() == QtCore.QEvent.KeyPress and issubclass(type(source), (QtWidgets.QTextEdit, QtWidgets.QLineEdit, QtWidgets.QTableWidget)):
        #        print(0,event.key())
        #        if event.key() == QtCore.Qt.Key_3:
        #            print("1",event.key())
        #            if event.text() in ["3","\"","₃"]:
        #                print("2",event.key())
        #                if event.modifiers() == (GroupSwitchModifier | ShiftModifier) or event.modifiers() == (ControlModifier | AltModifier | ShiftModifier):
        #                    #event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,8747,event.modifiers(),text="∫")
        #                    event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers(),text="2")#∫")
        #                    print("3",event.key())
        #                    self.MainApp.sendEvent(source,event)
        #                    return True
     # ---------------------------------- let the normal eventFilter handle the event ----------------------------------
        return super(AMaDiA_Main_Window, self).eventFilter(source, event)
        


# ---------------------------------- History Context Menu Actions/Functions ----------------------------------
 # ----------------
         
    def action_H_Copy_Text(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).Text)
        
    def action_H_Copy_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).LaTeX)
        
    def action_H_Copy_Input(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).Input)
        
    def action_H_Copy_cstr(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).cstr)
        
    def action_H_Copy_Solution(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).Evaluation)
        
 # ----------------
         
    def action_H_Calculate(self,source,event):
        item = source.itemAt(event.pos())
        self.tabWidget.setCurrentIndex(0)
        self.Tab_1_F_Calculate(item.data(100))
        
    def action_H_Display_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        self.tabWidget.setCurrentIndex(1)
        self.Tab_2_F_Display(item.data(100))

    def action_H_Display_LaTeX_Solution(self,source,event):
        item = source.itemAt(event.pos())
        self.tabWidget.setCurrentIndex(1)
        self.Tab_2_F_Display(item.data(100),part="Evaluation")
        
 # ----------------
         
    def action_H_Load_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.Tab_3_History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.tabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.Tab_3_F_RedrawPlot()
            self.Tab_3_F_Plot(item.data(100))
        
    def action_H_New_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.Tab_3_History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.tabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.Tab_3_F_RedrawPlot()
            self.Tab_3_F_Plot_init(item.data(100))
        
 # ----------------
        
    def action_H_Copy_x_Values(self,source,event):
        try:
            item = source.itemAt(event.pos())
            Text = "[ "
            for i in item.data(100).plot_x_vals:
                Text += str(i)
                Text += " , "
            Text = Text[:-3]
            Text += " ]"
            QApplication.clipboard().setText(Text)
        except AF.common_exceptions:
            Error = AF.ExceptionOutput(sys.exc_info())
            self.NotifyUser(2,Error)
        
    def action_H_Copy_y_Values(self,source,event):
        try:
            item = source.itemAt(event.pos())
            Text = "[ "
            for i in item.data(100).plot_y_vals:
                Text += str(i)
                Text += " , "
            Text = Text[:-3]
            Text += " ]"
            QApplication.clipboard().setText(Text)
        except AF.common_exceptions:
            Error = AF.ExceptionOutput(sys.exc_info())
            self.NotifyUser(2,Error)

 # ----------------
         
    def action_H_Delete(self,source,event):
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            source.takeItem(source.row(item))
            # The cleanup below is apparetnly unnecessary but it is cleaner to do it anyways...
            if source is self.Tab_1_History:
                item.data(100).tab_1_is = False
                item.data(100).tab_1_ref = None
            elif source is self.Tab_2_History:
                item.data(100).tab_2_is = False
                item.data(100).tab_2_ref = None
            elif source is self.Tab_3_History:
                item.data(100).tab_3_is = False
                item.data(100).tab_3_ref = None
                if item.data(100).current_ax != None:
                    item.data(100).current_ax.remove()
                    item.data(100).current_ax = None
                    self.Tab_3_F_RedrawPlot()
            elif source is self.Tab_5_History:
                if item.data(100) == self.Tab_5_Active_Equation:
                    self.Tab_5_History.addItem(item)
                else:
                    item.data(100).Tab_5_is = False
                    item.data(100).Tab_5_ref = None
                    
# ---------------------------------- Tab_5_Matrix_List Context Menu Actions/Functions ----------------------------------
    def action_Tab_5_M_Load_into_Editor(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_5_F_Load_Matrix(Name,Matrix)
    
    def action_Tab_5_M_Display(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_5_F_Display_Matrix(Name,Matrix)
    
    def action_Tab_5_M_Copy_string(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(str(item.data(101)))
    
    def action_Tab_5_M_Delete(self,source,event):
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            a = source.takeItem(source.row(item))
            del self.Tab_5_Active_Equation.Variables[a.data(100)]
        
# ---------------------------------- Tab_3_Display_Context_Menu ----------------------------------
    def action_Tab_3_Display_SavePlt(self):
        if self.pathOK:
            Filename = self.PlotPath
            Filename += AF.cTimeFullStr("-")
            Filename += ".png"
            try:
                print(Filename)
                self.Tab_3_Display.canvas.fig.savefig(Filename , facecolor=self.BG_Colour , edgecolor=self.BG_Colour )
            except:
                Error = "Could not save Plot: "
                Error += AF.ExceptionOutput(sys.exc_info())
                self.NotifyUser(1,Error)
            else:
                self.NotifyUser(3,Filename)
        else:
            print("Could not save Plot: Could not validate save location")
            self.NotifyUser(1,"Could not save Plot: Could not validate save location")
        
# ---------------------------------- Tab_5_Display_Context_Menu ----------------------------------
    def action_Tab_5_Display_Copy_Displayed(self):
        QApplication.clipboard().setText(self.Tab_5_Currently_Displayed)
        
    def action_Tab_5_Display_Copy_Displayed_Solution(self):
        QApplication.clipboard().setText(self.Tab_5_Currently_Displayed_Solution)

# ---------------------------------- HistoryHandler ----------------------------------

    def HistoryHandler(self, AMaS_Object, Tab):
        

        if Tab == 1:
            if AMaS_Object.tab_1_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.EvaluationEquation)
                
                self.Tab_1_History.addItem(item)
                AMaS_Object.tab_1_is = True
                AMaS_Object.tab_1_ref = item
            else:
                self.Tab_1_History.takeItem(self.Tab_1_History.row(AMaS_Object.tab_1_ref))
                AMaS_Object.tab_1_ref.setText(AMaS_Object.EvaluationEquation)
                self.Tab_1_History.addItem(AMaS_Object.tab_1_ref)

            self.Tab_1_History.scrollToBottom()
        
        elif Tab == 2:
            if AMaS_Object.tab_2_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.Text)
                
                self.Tab_2_History.addItem(item)
                AMaS_Object.tab_2_is = True
                AMaS_Object.tab_2_ref = item
            else:
                self.Tab_2_History.takeItem(self.Tab_2_History.row(AMaS_Object.tab_2_ref))
                AMaS_Object.tab_2_ref.setText(AMaS_Object.Text)
                self.Tab_2_History.addItem(AMaS_Object.tab_2_ref)
            
            self.Tab_2_History.scrollToBottom()
        
        elif Tab == 3:
            if AMaS_Object.tab_3_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.Text)
                
                self.Tab_3_History.addItem(item)
                AMaS_Object.tab_3_is = True
                AMaS_Object.tab_3_ref = item
            else:
                self.Tab_3_History.takeItem(self.Tab_3_History.row(AMaS_Object.tab_3_ref))
                AMaS_Object.tab_3_ref.setText(AMaS_Object.Text)
                self.Tab_3_History.addItem(AMaS_Object.tab_3_ref)
            
            self.Tab_3_History.scrollToBottom()
        
        elif Tab == 4:
            if AMaS_Object.Tab_5_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.Name)
                
                self.Tab_5_History.addItem(item)
                AMaS_Object.Tab_5_is = True
                AMaS_Object.Tab_5_ref = item
            else:
                self.Tab_5_History.takeItem(self.Tab_5_History.row(AMaS_Object.Tab_5_ref))
                AMaS_Object.Tab_5_ref.setText(AMaS_Object.Name)
                self.Tab_5_History.addItem(AMaS_Object.Tab_5_ref)

            self.Tab_5_Active_Equation = AMaS_Object
            self.Tab_5_F_Load_Matrix_List()
            self.Tab_5_History.scrollToBottom()

        else:
            print("History of Tab {} is unknown".format(Tab))

# ---------------------------------- Thread Handler ----------------------------------

    def TR(self, AMaS_Object , Function , ID=-1 , Eval = -1): # Thread Return: Threads report back here when they are done
        self.Function = Function

        if Function == self.Tab_1_F_Calculate:
            if Eval == 0 : Eval = True
            elif Eval == 1 : Eval = False
            else: Eval = None
            if Eval == None:
                Eval=self.Menubar_Main_Options_action_Eval_Functions.isChecked()
            self.Function(AMaS_Object,Eval)
        else:
            self.Function(AMaS_Object)
        
    def TC(self,Thread): # Thread Creator: All new threads are created here
        ID = -1

        # TODO: This causes a creash due to garbagecollector deleting thrads before they are properly done cleaning themselves up
        #       but after they have claimed to be done cleaning up
        #for i,e in enumerate(self.ThreadList):
        #    # This is not 100% clean but only Threats that have reported back should
        #    #   leave the list and thus only those can be cleaned by pythons garbage collector while not completely done
        #    #   These would cause a crash but are intercepted by notify to ensure stability
        #    try:
        #        running = e.isRunning()
        #    except (RuntimeError,AttributeError):
        #        running = False
        #    if not running:
        #        try:
        #            e.setTerminationEnabled(True)
        #            e.terminate()
        #            e.wait()
        #        except (RuntimeError,AttributeError):
        #            pass
        #        self.ThreadList.pop(i)
        #        ID = i
        #        self.ThreadList.insert(i,Thread(i))
        #        break
        #if ID == -1:
        #    ID = len(self.ThreadList)
        #    self.ThreadList.append(Thread(ID))

        # TODO: This causes a memory leak but is better than random crashes
        ID = len(self.ThreadList)
        self.ThreadList.append(Thread(ID))


        self.ThreadList[ID].Return.connect(self.TR)
        self.ThreadList[ID].ReturnError.connect(self.Error_Redirect)
        self.ThreadList[ID].start()

    def Error_Redirect(self, AMaS_Object , ErrorType , Error_Text , ReturnFunction , ID):
        #TODO:Improve
        self.NotifyUser(ErrorType,Error_Text)

    def Set_AMaS_Flags(self,AMaS_Object, f_eval = None, f_powsimp = None):
        if f_eval == None:
            f_eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()

        #Temporary:
        if f_powsimp == None:
            f_powsimp = f_eval

        AMaS_Object.f_eval = f_eval
        AMaS_Object.f_powsimp = f_powsimp

# ---------------------------------- Tab_1_ Calculator ----------------------------------
    def Tab_1_F_Calculate_Field_Input(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = False
        else:
            Eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()
        # Input.EvaluateLaTeX() # Could be used to evaluate LaTeX but: left( and right) brakes it...
        TheInput = self.Tab_1_InputField.text()
        if TheInput == "RUNTEST":
            self.RUNTEST()
        else:
            TheInput = re.sub(r"(?<!\w)ans(?!\w)",self.ans,TheInput)
            if TheInput == "len()":
                TheInput = str(len(self.ThreadList))
            self.TC(lambda ID: AT.AMaS_Creator(self, TheInput,self.Tab_1_F_Calculate,ID=ID,Eval=Eval))
        
        
        
    def Tab_1_F_Calculate(self,AMaS_Object,Eval = None):
        if Eval == None:
            Eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()
        self.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        self.TC(lambda ID: AT.AMaS_Thread(self, AMaS_Object, lambda:AC.AMaS.Evaluate(AMaS_Object), self.Tab_1_F_Calculate_Display , ID))
        
    def Tab_1_F_Calculate_Display(self,AMaS_Object):
        self.HistoryHandler(AMaS_Object,1)
        self.ans = AMaS_Object.Evaluation
        
# ---------------------------------- Tab_2_ LaTeX ----------------------------------
    def Tab_2_F_Convert(self, Text=None):
        EvalL = self.Tab_2_Eval_checkBox.isChecked()
        if type(Text) != str:
            Text = self.Tab_2_InputField.toPlainText()
        self.TC(lambda ID: AT.AMaS_Creator(self, Text, self.Tab_2_F_Display,ID,EvalL=EvalL))
        
        
    def Tab_2_F_Display(self , AMaS_Object , part = "Normal"):
        
        self.HistoryHandler(AMaS_Object,2)
        
        if part == "Normal":
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX)
            returnTuple = self.Tab_2_Viewer.Display(AMaS_Object.LaTeX_L, AMaS_Object.LaTeX_N
                                            ,self.TopBar_Font_Size_spinBox.value(),self.BG_Colour,self.TextColour
                                            ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Evaluation":
            if AMaS_Object.LaTeX_E == "Not converted yet":
                AMaS_Object.Convert_Evaluation_to_LaTeX()
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX_E)
            returnTuple = self.Tab_2_Viewer.Display(AMaS_Object.LaTeX_E_L, AMaS_Object.LaTeX_E_N
                                            ,self.TopBar_Font_Size_spinBox.value(),self.BG_Colour,self.TextColour
                                            ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        if returnTuple[0] != 0:
            self.NotifyUser(returnTuple[0],returnTuple[1])
        
# ---------------------------------- Tab_3_ 2D-Plot ----------------------------------
    def Tab_3_F_Plot_Button(self):
        self.TC(lambda ID: AT.AMaS_Creator(self,self.Tab_3_Formula_Field.text() , self.Tab_3_F_Plot_init,ID=ID, Iam=AC.Iam_2D_plot))
        
        
    def Tab_3_F_Plot_init(self , AMaS_Object): #TODO: Maybe get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        if not AMaS_Object.Plot_is_initialized: AMaS_Object.init_2D_plot()
        AMaS_Object.plot_ratio = self.Tab_3_Axis_ratio_Checkbox.isChecked()
        AMaS_Object.plot_grid = self.Tab_3_Draw_Grid_Checkbox.isChecked()
        AMaS_Object.plot_xmin = self.Tab_3_From_Spinbox.value()
        AMaS_Object.plot_xmax = self.Tab_3_To_Spinbox.value()
        AMaS_Object.plot_steps = self.Tab_3_Steps_Spinbox.value()
        
        if self.Tab_3_Steps_comboBox.currentIndex() == 0:
            AMaS_Object.plot_per_unit = False
        elif self.Tab_3_Steps_comboBox.currentIndex() == 1:
            AMaS_Object.plot_per_unit = True
        
        AMaS_Object.plot_xlim = self.Tab_3_XLim_Check.isChecked()
        if AMaS_Object.plot_xlim:
            xmin , xmax = self.Tab_3_XLim_min.value(), self.Tab_3_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            AMaS_Object.plot_xlim_vals = (xmin , xmax)
        AMaS_Object.plot_ylim = self.Tab_3_YLim_Check.isChecked()
        if AMaS_Object.plot_ylim:
            ymin , ymax = self.Tab_3_YLim_min.value(), self.Tab_3_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            AMaS_Object.plot_ylim_vals = (ymin , ymax)
        
        self.TC(lambda ID: AT.AMaS_Thread(self,AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.Tab_3_F_Plot ,ID))
        
        
        
        
    def Tab_3_F_Plot(self , AMaS_Object):
        #TODO: MAYBE Add an extra option for this in the config tab... and change everything else accordingly
        #if self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked():
        #    self.Tab_3_Display.UseTeX(True)
        #else:
        #    self.Tab_3_Display.UseTeX(False)
        
        self.Tab_3_Display.UseTeX(False)

        self.HistoryHandler(AMaS_Object,3)
        
        try:
            if type(AMaS_Object.plot_x_vals) == int or type(AMaS_Object.plot_x_vals) == float:
                p = self.Tab_3_Display.canvas.ax.axvline(x = AMaS_Object.plot_x_vals,color='red')
            else:
                p = self.Tab_3_Display.canvas.ax.plot(AMaS_Object.plot_x_vals , AMaS_Object.plot_y_vals) #  (... , 'r--') for red colour and short lines
            try:
                AMaS_Object.current_ax = p[0]
            except AF.common_exceptions:
                AMaS_Object.current_ax = p
            
            if AMaS_Object.plot_grid:
                self.Tab_3_Display.canvas.ax.grid(True)
            else:
                self.Tab_3_Display.canvas.ax.grid(False)
            if AMaS_Object.plot_ratio:
                self.Tab_3_Display.canvas.ax.set_aspect('equal')
            else:
                self.Tab_3_Display.canvas.ax.set_aspect('auto')
            
            self.Tab_3_Display.canvas.ax.relim()
            self.Tab_3_Display.canvas.ax.autoscale()
            if AMaS_Object.plot_xlim:
                self.Tab_3_Display.canvas.ax.set_xlim(AMaS_Object.plot_xlim_vals)
            if AMaS_Object.plot_ylim:
                self.Tab_3_Display.canvas.ax.set_ylim(AMaS_Object.plot_ylim_vals)
            
            try:
                colour = p[0].get_color()
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.tab_3_ref.setForeground(brush)
            except AF.common_exceptions:
                colour = "#FF0000"
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.tab_3_ref.setForeground(brush)
            
            try:
                self.Tab_3_Display.canvas.draw()
            except RuntimeError:
                AF.ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.Tab_3_Display.UseTeX(False)
                self.Tab_3_Display.canvas.draw()
        except AF.common_exceptions :
            Error = AF.ExceptionOutput(sys.exc_info(),False)
            print("y_vals = ",r.repr(AMaS_Object.plot_y_vals),type(AMaS_Object.plot_y_vals),"\nYou can copy all elements in advanced mode in the contextmenu")
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
            self.NotifyUser(1,Error)
            
    def Tab_3_F_RedrawPlot(self):
        xmin , xmax = self.Tab_3_XLim_min.value(), self.Tab_3_XLim_max.value()
        if xmax < xmin:
            xmax , xmin = xmin , xmax
        xlims = (xmin , xmax)
        ymin , ymax = self.Tab_3_YLim_min.value(), self.Tab_3_YLim_max.value()
        if ymax < ymin:
            ymax , ymin = ymin , ymax
        ylims = (ymin , ymax)
        if self.Tab_3_Draw_Grid_Checkbox.isChecked():
            self.Tab_3_Display.canvas.ax.grid(True)
        else:
            self.Tab_3_Display.canvas.ax.grid(False)
        if self.Tab_3_Axis_ratio_Checkbox.isChecked():
            self.Tab_3_Display.canvas.ax.set_aspect('equal')
        else:
            self.Tab_3_Display.canvas.ax.set_aspect('auto')
        
        self.Tab_3_Display.canvas.ax.relim()
        self.Tab_3_Display.canvas.ax.autoscale()
        if self.Tab_3_XLim_Check.isChecked():
            self.Tab_3_Display.canvas.ax.set_xlim(xlims)
        if self.Tab_3_YLim_Check.isChecked():
            self.Tab_3_Display.canvas.ax.set_ylim(ylims)
        
        try:
            self.Tab_3_Display.canvas.draw()
        except RuntimeError:
            AF.ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_Display.UseTeX(False)
            self.Tab_3_Display.canvas.draw()
        
        
    def Tab_3_F_Clear(self):
        self.Tab_3_Display.UseTeX(False)
        self.Tab_3_Display.canvas.ax.clear()
        try:
            self.Tab_3_Display.canvas.draw()
        except RuntimeError:
            AF.ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_Display.UseTeX(False)
            self.Tab_3_Display.canvas.ax.clear()
            self.Tab_3_Display.canvas.draw()
        brush = QtGui.QBrush(QtGui.QColor(215, 213, 201))
        brush.setStyle(QtCore.Qt.SolidPattern)
        for i in range(self.Tab_3_History.count()):
            self.Tab_3_History.item(i).setForeground(brush)
            self.Tab_3_History.item(i).data(100).current_ax = None
            
    def Tab_3_F_Sympy_Plot_Button(self):
        self.TC(lambda ID: AT.AMaS_Creator(self,self.Tab_3_Formula_Field.text() , self.Tab_3_F_Sympy_Plot,ID))
        
    def Tab_3_F_Sympy_Plot(self , AMaS_Object):
        try:
            x,y,z = sympy.symbols('x y z')
            
            temp = AMaS_Object.cstr
            if AMaS_Object.cstr.count("=") == 1 :
                temp1 , temp2 = AMaS_Object.cstr.split("=",1)
                temp = "Eq("+temp1
                temp += ","
                temp += temp2
                temp += ")"
            temp = parse_expr(temp)
            xmin , xmax = self.Tab_3_XLim_min.value(), self.Tab_3_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            xlims = (xmin , xmax)
            ymin , ymax = self.Tab_3_YLim_min.value(), self.Tab_3_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            ylims = (ymin , ymax)
            if self.Tab_3_XLim_Check.isChecked() and self.Tab_3_YLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims , ylim = ylims)
            elif self.Tab_3_XLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims)
            elif self.Tab_3_YLim_Check.isChecked():
                sympy.plot(temp , ylim = ylims)
            else:
                sympy.plot(temp)
        except AF.common_exceptions: # TODO: plot_implicit uses other syntax for limits
            try:
                sympy.plot_implicit(temp)
            except AF.common_exceptions:
                try:
                    sympy.plot_implicit(parse_expr(AMaS_Object.string))
                except AF.common_exceptions:
                    Error = AF.ExceptionOutput(sys.exc_info())
                    self.NotifyUser(1,Error)

# ---------------------------------- Tab_4_ ??? ----------------------------------
        
# ---------------------------------- Tab_5_ Multi-Dim ----------------------------------
    def Tab_5_F_New_Equation(self):
        Name = ""+self.Tab_5_2_New_Equation_Name_Input.text().strip()
        if Name == "":
            Name="Unnamed Equation"
        self.TC(lambda ID: AT.AMaS_Creator(self,Name,self.Tab_5_F_New_Equation_Done,ID=ID,Iam=AC.Iam_Multi_Dim))
    def Tab_5_F_New_Equation_Done(self,AMaS_Object):
        self.HistoryHandler(AMaS_Object,4)

    def Tab_5_F_Load_Selected_Equation(self):
        item = self.Tab_5_History.selectedItems()
        if len(item) == 1:
            item = item[0]
            self.HistoryHandler(item.data(100),4)
        self.Tab_5_FormulaInput.setText(item.data(100).Input)
        self.Tab_5_F_Display(self.Tab_5_Active_Equation)

    def Tab_5_F_Load_Matrix_List(self):
        self.Tab_5_Matrix_List.clear()
        try:
            for Name, Variable in self.Tab_5_Active_Equation.Variables.items():
                h, w = AF.shape2(Variable)
                Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                item = QtWidgets.QListWidgetItem()
                item.setText(Text)
                item.setData(100,Name)
                item.setData(101,Variable)
                self.Tab_5_Matrix_List.addItem(item)
        except ValueError:
            AF.ExceptionOutput(sys.exc_info())
            try:
                Name, Variable = self.Tab_5_Active_Equation.Variables.items()
                h, w = AF.shape2(Variable)
                Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                item = QtWidgets.QListWidgetItem()
                item.setText(Text)
                item.setData(100,Name)
                item.setData(101,Variable)
                self.Tab_5_Matrix_List.addItem(item)
            except AF.common_exceptions:
                Error = AF.ExceptionOutput(sys.exc_info())
                self.NotifyUser(1,Error)

    def Tab_5_F_Load_Matrix(self,Name,Matrix):
        h,w = AF.shape2(Matrix)
        self.Tab_5_1_Matrix_Input.setRowCount(h)
        self.Tab_5_1_Matrix_Input.setColumnCount(w)
        self.Tab_5_1_Dimension_Input.setText(" "+str(h)+"x"+str(w))
        self.Tab_5_1_Name_Input.setText(Name)

        tolist = getattr(Matrix, "tolist", None)
        if callable(tolist):
            ValueList = Matrix.tolist()
        else:
            ValueList = [[Matrix]]
        for i,a in enumerate(ValueList):
            for j,b in enumerate(ValueList[i]):
                item = Qt.QTableWidgetItem()
                item.setText(str(b))
                self.Tab_5_1_Matrix_Input.setItem(i,j,item)

    def Tab_5_F_Config_Matrix_Dim(self):
        h,w = self.Tab_5_1_Dimension_Input.text().split("x")
        try:
            h = int(h) if int(h) > 0 else 1
            self.Tab_5_1_Matrix_Input.setRowCount(h)
        except AF.common_exceptions:
            pass
        try:
            w = int(w)
            self.Tab_5_1_Matrix_Input.setColumnCount(w)
        except AF.common_exceptions:
            pass
        for i in range(self.Tab_5_1_Matrix_Input.columnCount()):
            self.Tab_5_1_Matrix_Input.setColumnWidth(i,75)
        
    def Tab_5_F_Save_Matrix(self):
        try:
            NameInvalid=False
            Name = AF.AstusParse(self.Tab_5_1_Name_Input.text()).strip()
            if Name == "" or " " in Name: #TODO: Better checks!!!
                NameInvalid=True

            if NameInvalid:
                self.NotifyUser(1,"Matrix Name Invalid")
                return False
            
            # Read the Input and save it in a nested List
            Matrix = []
            MError = ""
            for i in range(self.Tab_5_1_Matrix_Input.rowCount()):
                Matrix.append([])
                for j in range(self.Tab_5_1_Matrix_Input.columnCount()):
                    try:
                        if self.Tab_5_1_Matrix_Input.item(i,j).text().strip() != "":
                            Matrix[i].append(AF.AstusParse(self.Tab_5_1_Matrix_Input.item(i,j).text(),False))
                        else:
                            Matrix[i].append("0")
                    except AF.common_exceptions:
                        MError += "Could not add item to Matrix at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                        #MError += AF.ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Matrix[i].append("0")
            if MError != "":
                self.NotifyUser(2,MError)
            # Convert list into Matrix and save it in the Equation
            if len(Matrix) == 1 and len(Matrix[0]) == 1:
                Matrix = parse_expr(Matrix[0][0])
            else:
                Matrix = sympy.Matrix(Matrix) # https://docs.sympy.org/latest/modules/matrices/matrices.html
            self.Tab_5_Active_Equation.AddVariable(Name,Matrix)
            
            # Preapare ListWidgetItem
            item = QtWidgets.QListWidgetItem()
            h, w = AF.shape2(Matrix)
            Text = Name + " = {}".format(str(Matrix)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
            item.setText(Text)
            item.setData(100,Name)
            item.setData(101,Matrix)
            SearchFor = Name+" "

            #Remove Duplicats
            FoundItems = self.Tab_5_Matrix_List.findItems(SearchFor,QtCore.Qt.MatchStartsWith)
            if len(FoundItems) > 0:
                for i in FoundItems:
                    index = self.Tab_5_Matrix_List.indexFromItem(i)
                    self.Tab_5_Matrix_List.takeItem(index.row())

            # Add to the Matrix List
            self.Tab_5_Matrix_List.addItem(item)
            # Display the Matrix
            self.Tab_5_F_Display_Matrix(Name,Matrix)
        except AF.common_exceptions:
            Error = AF.ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)
        
    def Tab_5_F_Update_Equation(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = False
        else:
            Eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()
        Text = self.Tab_5_FormulaInput.text()
        AMaS_Object = self.Tab_5_Active_Equation
        self.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        self.TC(lambda ID: AT.AMaS_Thread(self,AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.Tab_5_F_Display , ID))

    def Tab_5_F_Display(self, AMaS_Object): # TODO: Display the Equation in addition to the solution
        self.Tab_5_Currently_Displayed = AMaS_Object.EvaluationEquation
        self.Tab_5_Currently_Displayed_Solution = AMaS_Object.Evaluation
        returnTuple = self.Tab_5_Display.Display(AMaS_Object.LaTeX_E_L, AMaS_Object.LaTeX_E_N
                                        ,self.TopBar_Font_Size_spinBox.value(),self.BG_Colour,self.TextColour
                                        ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        if returnTuple[0] != 0:
            self.NotifyUser(returnTuple[0],returnTuple[1])
        
    def Tab_5_F_Display_Matrix(self,Name,Matrix):
        Text = sympy.latex(Matrix)
        Text += "$"
        Text1 = "$\\displaystyle"+Text
        Text2 = "$"+Text
        #Text2 = Text2.replace("\\left","")
        #Text2 = Text2.replace("\\right","")
        #Text2 = Text2.replace("\\begin","")
        #Text2 = Text2.replace("\\end","")
        Text = Name + " = "
        Text1,Text2 = Text+Text1 , Text+Text2
        self.Tab_5_Currently_Displayed = Text + str(Matrix)
        self.Tab_5_Currently_Displayed_Solution = str(Matrix)
        returnTuple = self.Tab_5_Display.Display(Text1,Text2
                                        ,self.TopBar_Font_Size_spinBox.value(),self.BG_Colour,self.TextColour
                                        ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        if returnTuple[0] != 0:
            self.NotifyUser(returnTuple[0],returnTuple[1])

# ---------------------------------- Tab_6_ ??? ----------------------------------


# ---------------------------------- Main ----------------------------------
if __name__ == "__main__":
    latex_installed, dvipng_installed = find_executable('latex'), find_executable('dvipng')
    if latex_installed and dvipng_installed: print("latex and dvipng are installed --> Using pretty LaTeX Display")
    elif latex_installed and not dvipng_installed: print("latex is installed but dvipng was not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    elif not latex_installed and dvipng_installed: print("dvipng is installed but latex was not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    else: print("latex and dvipng were not detected --> Using standard LaTeX Display (Install both to use the pretty version)")
    print("AMaDiA Startup")
    app = MainApp([])
    #app = QtWidgets.QApplication([])
    app.setStyle("fusion")
    window = AMaDiA_Main_Window(app)
    window.show()
    sys.exit(app.exec_())

