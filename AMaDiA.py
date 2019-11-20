# This Python file uses the following encoding: utf-8
Version = "0.14.2.7"
Author = "Robin \'Astus\' Albers"
WindowTitle = "AMaDiA v"
WindowTitle+= Version
WindowTitle+= " by "
WindowTitle+= Author

#region ---------------------------------- imports ----------------------------------

import datetime
if __name__ == "__main__":
    print()
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    print(WindowTitle)
    print("Loading Modules")#,end="")


# import qt Modules
from PyQt5.Qt import QApplication, QClipboard # pylint: disable=no-name-in-module
from PyQt5 import QtWidgets,QtCore,QtGui,Qt
#import PyQt5.Qt as Qt

# import standard modules
from distutils.spawn import find_executable
import sys
import socket
import time
import platform
import errno
import os
import pathlib
import importlib
import re
import getpass

# import Math modules
import matplotlib
import sympy
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Import AMaDiA Core Modules
# To Convert ui to py: (Commands for Anaconda Prompt)
# cd C:"\Users\Robin\Desktop\Projects\AMaDiA"
# pyuic5 AMaDiAUI.ui -o AMaDiAUI.py
from AMaDiA_Files.AMaDiAUI import Ui_AMaDiA_Main_Window
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files.AMaDiA_Functions import common_exceptions, ExceptionOutput
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART
from AMaDiA_Files import AMaDiA_Colour
from AMaDiA_Files import AMaDiA_Threads as AT
from AMaDiA_Files import AstusChat_Client
from AMaDiA_Files import AstusChat_Server
from AMaDiA_Files.Test_Input import Test_Input



# To limit the length of output (Currently used to reduce the length of the y vector when an error in the plotter occurs)
import reprlib
r = reprlib.Repr()
r.maxlist = 20       # max elements displayed for lists
r.maxarray = 20       # max elements displayed for arrays
r.maxother = 500       # max elements displayed for other including np.ndarray
r.maxstring = 40    # max characters displayed for strings

# Load External Libraries
# These are not part of the standard Anaconda package and thus are already part of AMaDiA to make installation easy
from External_Libraries.python_control_master import control
try:
    from External_Libraries.keyboard_master import keyboard
except common_exceptions :
    ExceptionOutput(sys.exc_info())
    Keyboard_Remap_Works = False
else:
    Keyboard_Remap_Works = True

# Slycot is needed for some features of control but can not be included in AMaDiA as it needs system dependent compiling
try:
    import slycot
except ModuleNotFoundError:
    slycot_Installed = False
else:
    slycot_Installed = True

np.set_printoptions(threshold=100)

AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier
#endregion

class AMaDiA_File_Display(QtWidgets.QMainWindow):
    def __init__(self,FileName,Palette,Font,parent = None):
        try:
            super(AMaDiA_File_Display, self).__init__(parent)
            self.setWindowTitle(FileName)
            self.resize(900, 500)
            self.setAutoFillBackground(True)
            self.setPalette(Palette)
            self.setFont(Font)

            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.TextBrowser = QtWidgets.QTextBrowser(self)
            self.TextBrowser.setObjectName("TopBar_Error_Label")
            self.gridLayout.addWidget(self.TextBrowser, 0, 0, 0, 0)


            self.setCentralWidget(self.centralwidget)

            self.FolderPath = os.path.dirname(__file__)
            # Check if the path that was returned is correct
            FileName = os.path.join(self.FolderPath,FileName)
            with open(FileName,'r',encoding="utf-8") as text_file:
                Text = text_file.read()
            
            #self.TextBrowser.setPlainText(Text)
            self.TextBrowser.setText(Text)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

    def Scroll_To_End(self):
        self.TextBrowser.verticalScrollBar().setValue(self.TextBrowser.verticalScrollBar().maximum())

class AMaDiA_About_Display(QtWidgets.QMainWindow):
    def __init__(self,Palette,Font,parent = None):
        try:
            super(AMaDiA_About_Display, self).__init__(parent)
            self.setWindowTitle("About AMaDiA")
            self.resize(400, 600)
            self.setAutoFillBackground(True)
            self.setPalette(Palette)
            self.setFont(Font)

            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.TextBrowser = QtWidgets.QTextBrowser(self)
            self.TextBrowser.setObjectName("TopBar_Error_Label")
            self.gridLayout.addWidget(self.TextBrowser, 0, 0, 0, 0)
            #self.layout = QtWidgets.QVBoxLayout()
            #self.layout.addWidget(self.TextBrowser)
            #self.setLayout(self.layout)
            self.setCentralWidget(self.centralwidget)

            Text = WindowTitle+"\nWIP: More coming soon"
            
            self.TextBrowser.setText(Text)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

class MainApp(QtWidgets.QApplication):
    def __init__(self, args):
        super(MainApp, self).__init__(args)
    #    self.installEventFilter(self)
    #
    #def notify(self, obj, event): # Reimplementation of notify that does nothing other than redirecting to normal implementation for now...
    #    try:
    #        return super().notify(obj, event)
    #    except:
    #        ExceptionOutput(sys.exc_info())
    #        print("Caught: ",obj,event)
    #        return False
    #
    #def eventFilter(self, source, event): #DOES NOT INTERCEPT ENOUGH to nagate all AltGr Stuff
    #    try:
    #        pass#print(event.key())
    #    except common_exceptions:
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

        self.Tab_3_1_Button_Plot_SymPy.setVisible(False) # TODO: The Control Tab Has broken the Sympy plotter... Repairing it is not worth it... Remove this function...

        self.Tab_3_tabWidget.removeTab(1)# TODO
        self.Tab_5_tabWidget.setTabEnabled(0,False)# TODO
        self.Tab_5_tabWidget.setTabToolTip(0,"Coming soon")

        # TODO: Do something with the Statusbar 

        # Create Folders if not already existing
        self.CreateFolders()
        
        # Set UI variables
        #Set starting tabs
        self.Tab_3_tabWidget.setCurrentIndex(0)
        self.Tab_3_1_TabWidget.setCurrentIndex(0)
        self.Tab_4_tabWidget.setCurrentIndex(0)
        self.Tab_5_tabWidget.setCurrentIndex(3)# TODO: 0
        self.tabWidget.setCurrentIndex(0)
        
        #Set Splitter Start Values
        self.Tab_2_UpperSplitter.setSizes([163,699])
        self.Tab_2_LowerSplitter.setSizes([391,70])
        self.Tab_3_1_splitter.setSizes([297,565])
        #To cofigure use:
        #print(self.Tab_2_UpperSplitter.sizes())
        #print(self.Tab_2_LowerSplitter.sizes())
        #print(self.Tab_3_1_splitter.sizes())
        
        
        # Initialize important variables and lists
        self.ans = "1"
        self.LastNotification = ""
        self.LastOpenState = self.showNormal
        self.Bool_PreloadLaTeX = True
        self.Tab_2_Eval_checkBox.setCheckState(1)
        #QtWidgets.QCheckBox.setCheckState(1)

        # Initialize Thread Related Things:
        self.ThreadList = []
        self.threadpool = QtCore.QThreadPool()
        #self.threadpool.setMaxThreadCount(8)
        print("Multithreading with maximum %d threads (when in Threadpool mode)" % self.threadpool.maxThreadCount())
        # Thread Mode
        self.Threading = "POOL"
        #self.Threading = "LIST"
        
        
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AMaDiA" , WindowTitle))

        Tab_5_4_Dirty_Input_Text = "#Example:\n\n"
        Tab_5_4_Dirty_Input_Text += "K_P = 5\nK_D = 0\nK_i = 0\n\nsys1 = tf([K_D,K_P,K_i],[1,1.33+K_D,1+K_P,K_i])\n\n"
        Tab_5_4_Dirty_Input_Text += "#Other example:\n#sys1 = tf([1],[1,2,3])\n\n"
        Tab_5_4_Dirty_Input_Text += "#Other example:\n#sys1 = ss([[2,8],[1,0]],[[1],[-0.5000]],[-1/8,-1],[0])\n\n"
        Tab_5_4_Dirty_Input_Text += "#Setting Input Function:\nf=\"sin(x)\"\n#f=\"1/(x+1)\""
        
        self.Tab_5_4_Dirty_Input.setPlaceholderText(Tab_5_4_Dirty_Input_Text)
        self.Tab_5_4_Dirty_Input.setText(Tab_5_4_Dirty_Input_Text)
        
        
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
        self.TopBar_Error_Label.installEventFilter(self)
        
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
        self.Tab_4_2_New_Equation_Name_Input.setText("Equation 1")
        self.Tab_4_F_New_Equation()
        self.Tab_4_2_New_Equation_Name_Input.clear()
        self.Tab_4_1_Dimension_Input.setText(" 3x3 ")
        self.Tab_4_Currently_Displayed = ""
        self.Tab_4_Currently_Displayed_Solution = ""

        # Other things:
        self.Tab_5_1_System_Set_Order()
        
        #Check if this fixes the bug on the Laptop --> The Bug is fixed but the question remains wether this is what fixed it
        self.Tab_3_1_F_Clear()
        #One Little Bug Fix:
            #If using LaTeX Display in LaTeX Mode before using the Plotter for the first time it can happen that the plotter is not responsive until cleared.
            #Thus the plotter is now leared on program start to **hopefully** fix this...
            #If it does not fix the problem a more elaborate method is required...
            # A new variable that checks if the plot has already been used and if the LaTeX view has been used.
            # If the first is False and the seccond True than clear when the plot button is pressed and cjange the variables to ensure that this only happens once
            #       to not accidentially erase the plots of the user as this would be really bad...

        self.Tab_1_InputField.setFocus()
        
        msg = ""
        if not AF.LaTeX_dvipng_Installed:
            msg += "Please install LaTeX and dvipng to enable the LaTeX output mode"
        elif self.Bool_PreloadLaTeX:
            print("Starting LaTeX")
            self.Tab_2_Viewer.PreloadLaTeX()
        if not slycot_Installed:
            if msg != "":
                msg += "\n\n"
            msg += "slycot is not installed. The Control Tab might not work correctly\n"
            msg += "If you have conda installed use: conda install -c conda-forge slycot\n"
            msg += "Otherwise refer to: https://github.com/python-control/Slycot"
        if not Keyboard_Remap_Works:
            if msg != "":
                msg += "\n\n"
            msg += "The Keyboard Remapping does not work\n"
            msg += "If you are using Linux you need to run as root to enable Keyboard Remapping"
        if msg != "":
            self.NotifyUser(3,msg)
        else:
            try:
                msg = "Welcome " + getpass.getuser()
                #msg += ". How can I be of service?"
                self.NotifyUser(10,msg)
            except common_exceptions:
                ExceptionOutput(sys.exc_info())

        
# ---------------------------------- Init and Maintanance ----------------------------------

    def ConnectSignals(self):
        self.Menubar_Main_Options_action_Dev_Function.triggered.connect(self.ReloadModules)
        self.Menubar_Main_Options_action_WindowStaysOnTop.changed.connect(self.ToggleWindowStaysOnTop)
        self.Menubar_Main_Options_action_Use_Threadpool.changed.connect(self.ToggleThreadMode)

        self.Menubar_Main_Chat_action_Open_Client.triggered.connect(self.OpenClient)
        self.Menubar_Main_Chat_action_Open_Server.triggered.connect(self.OpenServer)
        
        self.Menubar_Main_Colour_action_Dark.triggered.connect(lambda: self.Recolour("Dark"))
        self.Menubar_Main_Colour_action_Bright.triggered.connect(lambda: self.Recolour("Bright"))

        self.Menubar_Main_Help_action_Examples.triggered.connect(lambda: self.Show_AMaDiA_Text_File("InputExamples.txt"))
        self.Menubar_Main_Help_action_Helpful_Commands.triggered.connect(lambda: self.Show_AMaDiA_Text_File("Helpful_Useable_Syntax.txt"))
        self.Menubar_Main_Help_action_Patchlog.triggered.connect(lambda: self.Show_AMaDiA_Text_File("Patchlog.txt"))
        self.Menubar_Main_Help_action_About.triggered.connect(self.Show_About)

        self.TopBar_Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)
        self.TopBar_Syntax_Highlighter_checkBox.toggled.connect(self.ToggleSyntaxHighlighter)
        self.TopBar_MathRemap_checkBox.toggled.connect(self.ToggleRemapper)
        
        self.Tab_1_InputField.returnPressed.connect(self.Tab_1_F_Calculate_Field_Input)
        
        self.Tab_2_ConvertButton.clicked.connect(self.Tab_2_F_Convert)
        self.Tab_2_InputField.returnCrtlPressed.connect(self.Tab_2_F_Convert)
        
        self.Tab_3_1_Button_Plot.clicked.connect(self.Tab_3_1_F_Plot_Button)
        self.Tab_3_1_Formula_Field.returnPressed.connect(self.Tab_3_1_F_Plot_Button)
        self.Tab_3_1_Button_Clear.clicked.connect(self.Tab_3_1_F_Clear)
        self.Tab_3_1_Button_Plot_SymPy.clicked.connect(self.Tab_3_1_F_Sympy_Plot_Button)
        self.Tab_3_1_RedrawPlot_Button.clicked.connect(self.Tab_3_1_F_RedrawPlot)
        self.Tab_3_1_Button_SavePlot.clicked.connect(self.action_tab_3_tab_1_Display_SavePlt)
        
        self.Tab_4_FormulaInput.returnPressed.connect(self.Tab_4_F_Update_Equation)
        self.Tab_4_1_Dimension_Input.returnPressed.connect(self.Tab_4_F_Config_Matrix_Dim)
        self.Tab_4_1_Configure_Button.clicked.connect(self.Tab_4_F_Config_Matrix_Dim)
        self.Tab_4_1_Name_Input.returnPressed.connect(self.Tab_4_F_Save_Matrix)
        self.Tab_4_1_Save_Matrix_Button.clicked.connect(self.Tab_4_F_Save_Matrix)
        self.Tab_4_2_New_Equation_Button.clicked.connect(self.Tab_4_F_New_Equation)
        self.Tab_4_2_New_Equation_Name_Input.returnPressed.connect(self.Tab_4_F_New_Equation)
        self.Tab_4_2_Load_Selected_Button.clicked.connect(self.Tab_4_F_Load_Selected_Equation)

        self.Tab_5_1_SystemOrder_Confrim.clicked.connect(self.Tab_5_1_System_Set_Order)
        self.Tab_5_1_SaveButton.clicked.connect(self.Tab_5_1_System_Save)
        self.Tab_5_1_SavePlotButton.clicked.connect(self.Tab_5_1_System_Plot_and_Save)
        self.Tab_5_4_Dirty_Input.returnCrtlPressed.connect(self.Tab_5_4_Dirty_Display)
    
    def Colour_Font_Init(self):
        self.FontFamily = "Arial"
        self.Palette , self.BG_Colour , self.TextColour = AMaDiA_Colour.Dark()
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.setFont(font)
        self.setPalette(self.Palette)
        for i in self.findChildren(AW.MplWidget):
            i.SetColour(self.BG_Colour, self.TextColour)


        #self.Error_Palette = AMaDiA_Colour.Red_ERROR()[0] # Currently not in use

        # Always keep Statusbar Font small
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.statusbar.setFont(font)

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

        # Always keep Statusbar Font small
        font = QtGui.QFont()
        font.setFamily(Family)
        font.setPointSize(9)
        self.statusbar.setFont(font)


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
        self.init_Animations_With_Colour()
        brush = self.Palette.text()
        for i in range(self.Tab_3_1_History.count()):
            if self.Tab_3_1_History.item(i).data(100).current_ax == None:
                self.Tab_3_1_History.item(i).setForeground(brush)
        
        
    def ChangeFontSize(self):
        Size = self.TopBar_Font_Size_spinBox.value()
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(Size)
        self.setFont(newFont)
        self.centralwidget.setFont(newFont)
        self.Menubar_Main.setFont(newFont)
        self.Menubar_Main_Options.setFont(newFont)
        self.Menubar_Main_Colour.setFont(newFont)
        self.Menubar_Main_Chat.setFont(newFont)
        self.Menubar_Main_Help.setFont(newFont)

    def InstallSyntaxHighlighter(self):
        #self.Tab_1_InputField_BracesHighlighter = AW.BracesHighlighter(self.Tab_1_InputField.document())
        pass

    def INIT_Animation(self):
        self.init_Animations_With_Colour()

    def init_Animations_With_Colour(self):
        self.init_Notification_Flash()
        
    def CreateFolders(self):
        self.pathOK = False
        # Find out Path
        self.selfPath = os.path.abspath(__file__)
        self.FolderPath = os.path.dirname(__file__)
        # Check if the path that was returned is correct
        fpath = os.path.join(self.FolderPath,"AMaDiA.py")
        fpath = pathlib.Path(fpath)
        if fpath.is_file():
            self.pathOK = True
            # Create Plots folder to save plots
            self.PlotPath = os.path.join(self.FolderPath,"Plots")
            try:
                os.makedirs(self.PlotPath)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    ExceptionOutput(sys.exc_info())
                    self.pathOK = False
            # Create Config folder to save configs
            self.ConfigFolderPath = os.path.join(self.FolderPath,"Config")
            try:
                os.makedirs(self.ConfigFolderPath)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    ExceptionOutput(sys.exc_info())
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
        except common_exceptions :
            Error = ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)
            try:
                print(i,Key)
            except common_exceptions :
                pass


# ---------------------------------- Error Handling ----------------------------------
    def init_Notification_Flash(self):
        self.Notification_Flash_Red = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.Notification_Flash_Red.setDuration(1000)
        self.Notification_Flash_Red.setLoopCount(1)
        self.Notification_Flash_Red.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Red.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Red.setKeyValueAt(0.5, QtGui.QColor(255, 0, 0))
        self.Notification_Flash_Red.finished.connect(self.Notification_Flash_Finished)
        
        self.Notification_Flash_Yellow = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.Notification_Flash_Yellow.setDuration(1000)
        self.Notification_Flash_Yellow.setLoopCount(1)
        self.Notification_Flash_Yellow.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Yellow.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Yellow.setKeyValueAt(0.5, QtGui.QColor(255, 255, 0))
        self.Notification_Flash_Yellow.finished.connect(self.Notification_Flash_Finished)

        self.Notification_Flash_Green = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.Notification_Flash_Green.setDuration(1000)
        self.Notification_Flash_Green.setLoopCount(1)
        self.Notification_Flash_Green.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Green.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Green.setKeyValueAt(0.5, QtGui.QColor(0, 255, 0))
        self.Notification_Flash_Green.finished.connect(self.Notification_Flash_Finished)

        self.Notification_Flash_Blue = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.Notification_Flash_Blue.setDuration(1000)
        self.Notification_Flash_Blue.setLoopCount(1)
        self.Notification_Flash_Blue.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Blue.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.Notification_Flash_Blue.setKeyValueAt(0.5, QtGui.QColor(0, 0, 255))
        self.Notification_Flash_Blue.finished.connect(self.Notification_Flash_Finished)

    def _set_FLASH_colour(self, col): # Handles chnges to the Property FLASH_colour
        palette = self.Palette
        palette.setColor(QtGui.QPalette.Window, col)
        self.setPalette(palette)
    FLASH_colour = QtCore.pyqtProperty(QtGui.QColor, fset=_set_FLASH_colour) # Defines the Property FLASH_colour

    def NotifyUser(self,Type,Text="Not Given",Time=None):
        """0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification"""
        if Text=="Not Given" and type(Type) == tuple:
            Type, Text = Type[0], Type[1]
        self.LastNotification = Text
        if Type == 0:
            pass
        elif Type == 1:
            self.NotifyUser_Error(Text,Time)
        elif Type == 2:
            self.NotifyUser_Warning(Text,Time)
        elif Type == 3:
            self.NotifyUser_Notification(Text,Time)
        elif Type == 4:
            if self.Menubar_Main_Options_action_Advanced_Mode.isChecked():
                self.NotifyUser_Notification(Text,Time)
        elif Type == 10:
            self.NotifyUser_Direct(Text,Time)
        else:
            nText = "Notification of type "+str(Type)
            nText += " (Type unknown):\n"
            nText += Text
            self.NotifyUser_Warning(nText,Time)

    def NotifyUser_Error(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Error at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        #self.TopBar_Error_Label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Notification_Flash_Red.start()

    def NotifyUser_Warning(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Warning at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.Notification_Flash_Yellow.start()

    def NotifyUser_Notification(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        Text = "Notification at " + Time
        self.TopBar_Error_Label.setText(Text)
        self.TopBar_Error_Label.setToolTip(Error_Text)

        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.Notification_Flash_Blue.start()

    def NotifyUser_Direct(self,Error_Text,Time=None):
        if Time==None:
            Time = AF.cTimeSStr()
        self.TopBar_Error_Label.setText(Error_Text)
        self.TopBar_Error_Label.setToolTip("Start at "+Time)

        #self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.WinPanel)
        #self.Notification_Flash_Blue.start()

    def Notification_Flash_Finished(self):
        self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.NoFrame)


# ---------------------------------- Option Toolbar Funtions ----------------------------------
    def ReloadModules(self):
        #AC.ReloadModules()
        #AF.ReloadModules()
        #AC.ReloadModules()
        #AT.ReloadModules()
        #AW.ReloadModules()
        #importlib.reload(AW)
        #importlib.reload(AF)
        #importlib.reload(AC)
        #importlib.reload(ART)
        #importlib.reload(AT)
        #importlib.reload(AMaDiA_Colour)
        #
        #self.ColourMain()

        self.Tab_5_tabWidget.setTabEnabled(0,True)# TODO

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
        Text = "Expected Entries after all calulations: "+str(len(Test_Input))
        print(Text)
        self.Tab_1_InputField.setText(Text)

    def ToggleThreadMode(self):
        if self.Menubar_Main_Options_action_Use_Threadpool.isChecked():
            self.Threading = "POOL"
        else:
            self.Threading = "LIST"

    def Show_AMaDiA_Text_File(self,FileName):
        self.AMaDiA_Text_File_Window = AMaDiA_File_Display(FileName,self.Palette,self.font())
        self.AMaDiA_Text_File_Window.show()
        if FileName == "Patchlog.txt":
            worker = AT.Timer(0.1) # pylint: disable=no-value-for-parameter
            worker.signals.finished.connect(self.AMaDiA_Text_File_SCROLLTOEND)
            self.threadpool.start(worker)
        
    def AMaDiA_Text_File_SCROLLTOEND(self):
        self.AMaDiA_Text_File_Window.Scroll_To_End()

    def Show_About(self):
        self.AMaDiA_About_Display_Window = AMaDiA_About_Display(self.Palette,self.font())
        self.AMaDiA_About_Display_Window.show()

# ---------------------------------- Chat Toolbar Funtions ----------------------------------

    def OpenClient(self):
        self.Chat = AstusChat_Client.MainWindow(self.Palette,self.FontFamily)
        self.Chat.show()

    def OpenServer(self):
        self.Sever = AstusChat_Server.MainWindow(self.Palette,self.FontFamily)
        self.Sever.show()


# ---------------------------------- Events and Context Menu ----------------------------------
    def OtherContextMenuSetup(self):
        self.Tab_3_1_Display.canvas.mpl_connect('button_press_event', self.Tab_3_1_Display_Context_Menu)
        self.Tab_4_Display.canvas.mpl_connect('button_press_event', self.Tab_4_Display_Context_Menu)
        self.Tab_5_2_Display.canvas.mpl_connect('button_press_event', self.Tab_5_2_Maximize_Axes)
        
        
 # ---------------------------------- 2D Plot Context Menu ---------------------------------- 
    def Tab_3_1_Display_Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            action = menu.addAction('Save Plot')
            action.triggered.connect(self.action_tab_3_tab_1_Display_SavePlt)
            cursor = QtGui.QCursor()
            menu.exec_(cursor.pos())
            
 # ---------------------------------- Multi-Dim Display Context Menu ---------------------------------- 
    def Tab_4_Display_Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            action = menu.addAction('Copy Text')
            action.triggered.connect(self.action_tab_5_Display_Copy_Displayed)
            action = menu.addAction('Copy Solution')
            action.triggered.connect(self.action_tab_5_Display_Copy_Displayed_Solution)
            cursor = QtGui.QCursor()
            menu.exec_(cursor.pos())

 # ---------------------------------- Control Plot Interaction ---------------------------------- 
    def Tab_5_2_Maximize_Axes(self,event):
        try:
            if event.button == 1 and event.dblclick:
                message = self.Tab_5_3_SingleDisplay.Plot(self.Tab_5_2_Display.Curr_Sys, event.inaxes.title.get_text())
                if message[0] == 0:
                    self.Tab_5_tabWidget.setCurrentIndex(2)
                else:
                    self.NotifyUser(message)
        except common_exceptions as inst:
            if type(inst) != AttributeError:
                self.NotifyUser(1,ExceptionOutput(sys.exc_info()))
            self.Tab_5_tabWidget.setCurrentIndex(1)
        self.Tab_5_tabWidget.setFocus()
    

# ---------------------------------- Event Filter ----------------------------------
    def eventFilter(self, source, event): # TODO: Add more
        #print(event.type())
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_F11 and source is self: # F11 to toggle Fullscreen
            if not self.isFullScreen():
                self.LastOpenState = self.showMaximized if self.isMaximized() else self.showNormal
                self.showFullScreen()
            else:
                self.LastOpenState()
     # ---------------------------------- History Context Menu ----------------------------------
        elif (event.type() == QtCore.QEvent.ContextMenu and
            (source is self.Tab_1_History 
                or source is self.Tab_2_History 
                or source is self.Tab_3_1_History 
                or source is self.Tab_4_History #TODO: This is temporary. Implement this context menu properly
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
     # ---------------------------------- Tab_4 Matrix List Context Menu ----------------------------------
        elif (event.type() == QtCore.QEvent.ContextMenu and
            (source is self.Tab_4_Matrix_List)and source.itemAt(event.pos())):
            menu = QtWidgets.QMenu()
            action = menu.addAction('Load to Editor')
            action.triggered.connect(lambda: self.action_tab_5_M_Load_into_Editor(source,event))
            action = menu.addAction('Display')
            action.triggered.connect(lambda: self.action_tab_5_M_Display(source,event))
            action = menu.addAction('Copy as String')
            action.triggered.connect(lambda: self.action_tab_5_M_Copy_string(source,event))
            action = menu.addAction('Delete')
            action.triggered.connect(lambda: self.action_tab_5_M_Delete(source,event))
            menu.exec_(event.globalPos())
            return True
     # ---------------------------------- LineEdit Events ---------------------------------- #TODO:DELETE THIS (Already implemented in the class)
        #elif type(source) == AW.LineEdit:
        #    if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
        #        QTextEdFontMetrics =  QtGui.QFontMetrics(source.font())
        #        source.QTextEdRowHeight = QTextEdFontMetrics.lineSpacing()+9
        #        source.setFixedHeight(source.QTextEdRowHeight)
        #    if (event.type() == QtCore.QEvent.KeyPress # Connects to returnPressed
        #    and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
        #        source.returnPressed.emit()
        #        return True
        #    if (event.type() == QtCore.QEvent.KeyPress # Move to beginning if up key pressed
        #    and event.key() == QtCore.Qt.Key_Up):
        #        cursor = source.textCursor()
        #        cursor.movePosition(cursor.Start)
        #        source.setTextCursor(cursor)
        #        return True
        #    if (event.type() == QtCore.QEvent.KeyPress # Move to end if down key pressed
        #    and event.key() == QtCore.Qt.Key_Down):
        #        cursor = source.textCursor()
        #        cursor.movePosition(cursor.End)
        #        source.setTextCursor(cursor)
        #        return True
     # ---------------------------------- Tab_2_InputField ---------------------------------- #TODO:DELETE THIS (Already implemented in the class)
        #elif (event.type() == QtCore.QEvent.KeyPress  # Tab_2_InputField: use crtl+return to convert
        #      and source is self.Tab_2_InputField
        #      and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
        #      and event.modifiers() == QtCore.Qt.ControlModifier):
        #    self.Tab_2_F_Convert()
        #    return True
     # ---------------------------------- Remap Keys to allow for Math Unicode Symbol input ---------------------------------- #TODO:DELETE THIS
        
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
     # ---------------------------------- Other Events ----------------------------------
        elif (event.type() == 4 and source is self.TopBar_Error_Label): # Copy last Notification on Doubleclick on the Top Bar Label
              QApplication.clipboard().setText(self.LastNotification)
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
        if source is self.Tab_3_1_History:
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
                self.Tab_3_1_F_RedrawPlot()
            self.Tab_3_1_F_Plot(item.data(100))
        
    def action_H_New_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.Tab_3_1_History:
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
                self.Tab_3_1_F_RedrawPlot()
            self.Tab_3_1_F_Plot_init(item.data(100))
        
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
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
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
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
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
            elif source is self.Tab_3_1_History:
                item.data(100).Tab_3_1_is = False
                item.data(100).Tab_3_1_ref = None
                if item.data(100).current_ax != None:
                    item.data(100).current_ax.remove()
                    item.data(100).current_ax = None
                    self.Tab_3_1_F_RedrawPlot()
            elif source is self.Tab_4_History:
                if item.data(100) == self.Tab_4_Active_Equation:
                    self.Tab_4_History.addItem(item)
                else:
                    item.data(100).Tab_4_is = False
                    item.data(100).Tab_4_ref = None


# ---------------------------------- Tab_4_Matrix_List Context Menu Actions/Functions ----------------------------------
    def action_tab_5_M_Load_into_Editor(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_4_F_Load_Matrix(Name,Matrix)
    
    def action_tab_5_M_Display(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_4_F_Display_Matrix(Name,Matrix)
    
    def action_tab_5_M_Copy_string(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(str(item.data(101)))
    
    def action_tab_5_M_Delete(self,source,event):
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            a = source.takeItem(source.row(item))
            del self.Tab_4_Active_Equation.Variables[a.data(100)]
        

# ---------------------------------- Tab_3_1_Display_Context_Menu ----------------------------------
    def action_tab_3_tab_1_Display_SavePlt(self):
        if self.pathOK:
            Filename = AF.cTimeFullStr("-")
            Filename += ".png"
            Filename = os.path.join(self.PlotPath,Filename)
            try:
                print(Filename)
                self.Tab_3_1_Display.canvas.fig.savefig(Filename , facecolor=self.BG_Colour , edgecolor=self.BG_Colour )
            except:
                Error = "Could not save Plot: "
                Error += ExceptionOutput(sys.exc_info())
                self.NotifyUser(1,Error)
            else:
                self.NotifyUser(3,Filename)
        else:
            print("Could not save Plot: Could not validate save location")
            self.NotifyUser(1,"Could not save Plot: Could not validate save location")
        

# ---------------------------------- Tab_4_Display_Context_Menu ----------------------------------
    def action_tab_5_Display_Copy_Displayed(self):
        QApplication.clipboard().setText(self.Tab_4_Currently_Displayed)
        
    def action_tab_5_Display_Copy_Displayed_Solution(self):
        QApplication.clipboard().setText(self.Tab_4_Currently_Displayed_Solution)


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
            if AMaS_Object.Tab_3_1_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.Text)
                
                self.Tab_3_1_History.addItem(item)
                AMaS_Object.Tab_3_1_is = True
                AMaS_Object.Tab_3_1_ref = item
            else:
                self.Tab_3_1_History.takeItem(self.Tab_3_1_History.row(AMaS_Object.Tab_3_1_ref))
                AMaS_Object.Tab_3_1_ref.setText(AMaS_Object.Text)
                self.Tab_3_1_History.addItem(AMaS_Object.Tab_3_1_ref)
            
            self.Tab_3_1_History.scrollToBottom()
        
        elif Tab == 4:
            if AMaS_Object.Tab_4_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AMaS_Object.Name)
                
                self.Tab_4_History.addItem(item)
                AMaS_Object.Tab_4_is = True
                AMaS_Object.Tab_4_ref = item
            else:
                self.Tab_4_History.takeItem(self.Tab_4_History.row(AMaS_Object.Tab_4_ref))
                AMaS_Object.Tab_4_ref.setText(AMaS_Object.Name)
                self.Tab_4_History.addItem(AMaS_Object.Tab_4_ref)

            self.Tab_4_Active_Equation = AMaS_Object
            self.Tab_4_F_Load_Matrix_List()
            self.Tab_4_History.scrollToBottom()

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

    def TC(self, Kind, *args, **kwargs):
        try:
            if self.Threading == "LIST":
                ID = len(self.ThreadList)
                
                if Kind == "NEW":
                    Thread = AT.AMaS_Creator_Thread(self,*args,ID=ID,**kwargs)
                elif Kind == "WORK":
                    Thread = AT.AMaS_Thread(self,*args,ID=ID) # pylint: disable=no-value-for-parameter
                
                self.ThreadList.append(Thread)

                self.ThreadList[ID].Return.connect(self.TR)
                self.ThreadList[ID].ReturnError.connect(self.Error_Redirect)
                self.ThreadList[ID].start()

            elif self.Threading == "POOL":
                if Kind == "NEW":
                    worker = AT.AMaS_Creator(*args,**kwargs)
                elif Kind == "WORK":
                    worker = AT.AMaS_Worker(*args) # pylint: disable=no-value-for-parameter
                worker.signals.result.connect(self.TR)
                worker.signals.error.connect(self.Error_Redirect)
                #worker.signals.finished.connect(self.NONE)
                self.threadpool.start(worker) 
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)
        
    def TC_old(self,Thread): # Thread Creator: All new threads are created here
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

    def Error_Redirect(self, AMaS_Object , ErrorType , Error_Text , ReturnFunction , ID=-1):
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
            #self.TC(lambda ID: AT.AMaS_Creator(TheInput,self.Tab_1_F_Calculate,ID=ID,Eval=Eval))
            self.TC("NEW",TheInput,self.Tab_1_F_Calculate,Eval=Eval)
        
        
        
    def Tab_1_F_Calculate(self,AMaS_Object,Eval = None):
        if Eval == None:
            Eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()
        self.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        #self.TC(lambda ID: AT.AMaS_Worker(AMaS_Object, lambda:AC.AMaS.Evaluate(AMaS_Object), self.Tab_1_F_Calculate_Display , ID))
        self.TC("WORK", AMaS_Object, lambda:AC.AMaS.Evaluate(AMaS_Object), self.Tab_1_F_Calculate_Display)
        
    def Tab_1_F_Calculate_Display(self,AMaS_Object):
        self.HistoryHandler(AMaS_Object,1)
        self.ans = AMaS_Object.Evaluation
        

# ---------------------------------- Tab_2_ LaTeX ----------------------------------
    def Tab_2_F_Convert(self, Text=None):
        EvalL = self.Tab_2_Eval_checkBox.isChecked()
        if type(Text) != str:
            Text = self.Tab_2_InputField.toPlainText()
        #self.TC(lambda ID: AT.AMaS_Creator(Text, self.Tab_2_F_Display,ID,EvalL=EvalL))
        self.TC("NEW",Text, self.Tab_2_F_Display,EvalL=EvalL)
        
        
    def Tab_2_F_Display(self , AMaS_Object , part = "Normal"):
        
        self.HistoryHandler(AMaS_Object,2)
        
        if part == "Normal":
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX)
            returnTuple = self.Tab_2_Viewer.Display(AMaS_Object.LaTeX_L, AMaS_Object.LaTeX_N
                                            ,self.TopBar_Font_Size_spinBox.value()
                                            ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Evaluation":
            if AMaS_Object.LaTeX_E == "Not converted yet":
                AMaS_Object.Convert_Evaluation_to_LaTeX()
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX_E)
            returnTuple = self.Tab_2_Viewer.Display(AMaS_Object.LaTeX_E_L, AMaS_Object.LaTeX_E_N
                                            ,self.TopBar_Font_Size_spinBox.value()
                                            ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        self.NotifyUser(returnTuple)#[0],returnTuple[1])
        

# ---------------------------------- Tab_3_1_ 2D-Plot ----------------------------------
    def Tab_3_1_F_Plot_Button(self):
        #self.TC(lambda ID: AT.AMaS_Creator(self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Plot_init,ID=ID, Iam=AC.Iam_2D_plot))
        self.TC("NEW",self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Plot_init, Iam=AC.Iam_2D_plot)
        
        
    def Tab_3_1_F_Plot_init(self , AMaS_Object): #TODO: Maybe get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        if not AMaS_Object.Plot_is_initialized: AMaS_Object.init_2D_plot()
        AMaS_Object.plot_ratio = self.Tab_3_1_Axis_ratio_Checkbox.isChecked()
        AMaS_Object.plot_grid = self.Tab_3_1_Draw_Grid_Checkbox.isChecked()
        AMaS_Object.plot_xmin = self.Tab_3_1_From_Spinbox.value()
        AMaS_Object.plot_xmax = self.Tab_3_1_To_Spinbox.value()
        AMaS_Object.plot_steps = self.Tab_3_1_Steps_Spinbox.value()
        
        if self.Tab_3_1_Steps_comboBox.currentIndex() == 0:
            AMaS_Object.plot_per_unit = False
        elif self.Tab_3_1_Steps_comboBox.currentIndex() == 1:
            AMaS_Object.plot_per_unit = True
        
        AMaS_Object.plot_xlim = self.Tab_3_1_XLim_Check.isChecked()
        if AMaS_Object.plot_xlim:
            xmin , xmax = self.Tab_3_1_XLim_min.value(), self.Tab_3_1_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            AMaS_Object.plot_xlim_vals = (xmin , xmax)
        AMaS_Object.plot_ylim = self.Tab_3_1_YLim_Check.isChecked()
        if AMaS_Object.plot_ylim:
            ymin , ymax = self.Tab_3_1_YLim_min.value(), self.Tab_3_1_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            AMaS_Object.plot_ylim_vals = (ymin , ymax)
        
        #self.TC(lambda ID: AT.AMaS_Worker(AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.Tab_3_1_F_Plot ,ID))
        self.TC("WORK",AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.Tab_3_1_F_Plot)
        
        
        
        
    def Tab_3_1_F_Plot(self , AMaS_Object):
        #TODO: MAYBE Add an extra option for this in the config tab... and change everything else accordingly
        #if self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked():
        #    self.Tab_3_1_Display.UseTeX(True)
        #else:
        #    self.Tab_3_1_Display.UseTeX(False)
        
        self.Tab_3_1_Display.UseTeX(False)

        self.HistoryHandler(AMaS_Object,3)
        
        try:
            if type(AMaS_Object.plot_x_vals) == int or type(AMaS_Object.plot_x_vals) == float:
                p = self.Tab_3_1_Display.canvas.ax.axvline(x = AMaS_Object.plot_x_vals,color='red')
            else:
                p = self.Tab_3_1_Display.canvas.ax.plot(AMaS_Object.plot_x_vals , AMaS_Object.plot_y_vals) #  (... , 'r--') for red colour and short lines
            try:
                AMaS_Object.current_ax = p[0]
            except common_exceptions:
                AMaS_Object.current_ax = p
            
            if AMaS_Object.plot_grid:
                self.Tab_3_1_Display.canvas.ax.grid(True)
            else:
                self.Tab_3_1_Display.canvas.ax.grid(False)
            if AMaS_Object.plot_ratio:
                self.Tab_3_1_Display.canvas.ax.set_aspect('equal')
            else:
                self.Tab_3_1_Display.canvas.ax.set_aspect('auto')
            
            self.Tab_3_1_Display.canvas.ax.relim()
            self.Tab_3_1_Display.canvas.ax.autoscale()
            if AMaS_Object.plot_xlim:
                self.Tab_3_1_Display.canvas.ax.set_xlim(AMaS_Object.plot_xlim_vals)
            if AMaS_Object.plot_ylim:
                self.Tab_3_1_Display.canvas.ax.set_ylim(AMaS_Object.plot_ylim_vals)
            
            try:
                colour = p[0].get_color()
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.Tab_3_1_ref.setForeground(brush)
            except common_exceptions:
                colour = "#FF0000"
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.Tab_3_1_ref.setForeground(brush)
            
            try:
                self.Tab_3_1_Display.canvas.draw()
            except RuntimeError:
                ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.Tab_3_1_Display.UseTeX(False)
                self.Tab_3_1_Display.canvas.draw()
        except common_exceptions :
            Error = ExceptionOutput(sys.exc_info(),False)
            print("y_vals = ",r.repr(AMaS_Object.plot_y_vals),type(AMaS_Object.plot_y_vals),"\nYou can copy all elements in advanced mode in the contextmenu")
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
            self.NotifyUser(1,Error)
            
    def Tab_3_1_F_RedrawPlot(self):
        xmin , xmax = self.Tab_3_1_XLim_min.value(), self.Tab_3_1_XLim_max.value()
        if xmax < xmin:
            xmax , xmin = xmin , xmax
        xlims = (xmin , xmax)
        ymin , ymax = self.Tab_3_1_YLim_min.value(), self.Tab_3_1_YLim_max.value()
        if ymax < ymin:
            ymax , ymin = ymin , ymax
        ylims = (ymin , ymax)
        if self.Tab_3_1_Draw_Grid_Checkbox.isChecked():
            self.Tab_3_1_Display.canvas.ax.grid(True)
        else:
            self.Tab_3_1_Display.canvas.ax.grid(False)
        if self.Tab_3_1_Axis_ratio_Checkbox.isChecked():
            self.Tab_3_1_Display.canvas.ax.set_aspect('equal')
        else:
            self.Tab_3_1_Display.canvas.ax.set_aspect('auto')
        
        self.Tab_3_1_Display.canvas.ax.relim()
        self.Tab_3_1_Display.canvas.ax.autoscale()
        if self.Tab_3_1_XLim_Check.isChecked():
            self.Tab_3_1_Display.canvas.ax.set_xlim(xlims)
        if self.Tab_3_1_YLim_Check.isChecked():
            self.Tab_3_1_Display.canvas.ax.set_ylim(ylims)
        
        try:
            self.Tab_3_1_Display.canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_1_Display.UseTeX(False)
            self.Tab_3_1_Display.canvas.draw()
        
        
    def Tab_3_1_F_Clear(self):
        self.Tab_3_1_Display.UseTeX(False)
        self.Tab_3_1_Display.canvas.ax.clear()
        try:
            self.Tab_3_1_Display.canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_1_Display.UseTeX(False)
            self.Tab_3_1_Display.canvas.ax.clear()
            self.Tab_3_1_Display.canvas.draw()
        brush = self.Palette.text()
        for i in range(self.Tab_3_1_History.count()):
            self.Tab_3_1_History.item(i).setForeground(brush)
            self.Tab_3_1_History.item(i).data(100).current_ax = None
            
    def Tab_3_1_F_Sympy_Plot_Button(self): # TODO: DELETE
        #self.TC(lambda ID: AT.AMaS_Creator(self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Sympy_Plot,ID))
        self.TC("NEW",self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Sympy_Plot)
        
    def Tab_3_1_F_Sympy_Plot(self , AMaS_Object): # TODO: DELETE
        try:
            #self.__SPFIG = plt.figure(num="SP")
            x,y,z = sympy.symbols('x y z')  # pylint: disable=unused-variable
            
            temp = AMaS_Object.cstr
            if AMaS_Object.cstr.count("=") == 1 :
                temp1 , temp2 = AMaS_Object.cstr.split("=",1)
                temp = "Eq("+temp1
                temp += ","
                temp += temp2
                temp += ")"
            temp = parse_expr(temp)
            xmin , xmax = self.Tab_3_1_XLim_min.value(), self.Tab_3_1_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            xlims = (xmin , xmax)
            ymin , ymax = self.Tab_3_1_YLim_min.value(), self.Tab_3_1_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            ylims = (ymin , ymax)
            if self.Tab_3_1_XLim_Check.isChecked() and self.Tab_3_1_YLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims , ylim = ylims)
            elif self.Tab_3_1_XLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims)
            elif self.Tab_3_1_YLim_Check.isChecked():
                sympy.plot(temp , ylim = ylims)
            else:
                sympy.plot(temp)#, num="SP",backend=matplotlib.backends.backend_qt5.FigureCanvasBase)
        except common_exceptions: # TODO: plot_implicit uses other syntax for limits
            Error = ExceptionOutput(sys.exc_info())
            try:
                sympy.plot_implicit(temp)
            except common_exceptions:
                Error = ExceptionOutput(sys.exc_info())
                try:
                    sympy.plot_implicit(parse_expr(AMaS_Object.string))
                except common_exceptions:
                    Error = ExceptionOutput(sys.exc_info())
                    self.NotifyUser(1,Error)


# ---------------------------------- Tab_4_ Multi-Dim ----------------------------------
    def Tab_4_F_New_Equation(self):
        Name = ""+self.Tab_4_2_New_Equation_Name_Input.text().strip()
        if Name == "":
            Name="Unnamed Equation"
        #self.TC(lambda ID: AT.AMaS_Creator(Name,self.Tab_4_F_New_Equation_Done,ID=ID,Iam=AC.Iam_Multi_Dim))
        self.TC("NEW",Name,self.Tab_4_F_New_Equation_Done,Iam=AC.Iam_Multi_Dim)
    def Tab_4_F_New_Equation_Done(self,AMaS_Object):
        self.HistoryHandler(AMaS_Object,4)

    def Tab_4_F_Load_Selected_Equation(self):
        item = self.Tab_4_History.selectedItems()
        if len(item) == 1:
            item = item[0]
            self.HistoryHandler(item.data(100),4)
        self.Tab_4_FormulaInput.setText(item.data(100).Input)
        self.Tab_4_F_Display(self.Tab_4_Active_Equation)

    def Tab_4_F_Load_Matrix_List(self):
        self.Tab_4_Matrix_List.clear()
        try:
            for Name, Variable in self.Tab_4_Active_Equation.Variables.items():
                h, w = AF.shape2(Variable)
                Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                item = QtWidgets.QListWidgetItem()
                item.setText(Text)
                item.setData(100,Name)
                item.setData(101,Variable)
                self.Tab_4_Matrix_List.addItem(item)
        except ValueError:
            ExceptionOutput(sys.exc_info())
            try:
                Name, Variable = self.Tab_4_Active_Equation.Variables.items()
                h, w = AF.shape2(Variable)
                Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                item = QtWidgets.QListWidgetItem()
                item.setText(Text)
                item.setData(100,Name)
                item.setData(101,Variable)
                self.Tab_4_Matrix_List.addItem(item)
            except common_exceptions:
                Error = ExceptionOutput(sys.exc_info())
                self.NotifyUser(1,Error)

    def Tab_4_F_Load_Matrix(self,Name,Matrix):
        h,w = AF.shape2(Matrix)
        self.Tab_4_1_Matrix_Input.setRowCount(h)
        self.Tab_4_1_Matrix_Input.setColumnCount(w)
        self.Tab_4_1_Dimension_Input.setText(" "+str(h)+"x"+str(w))
        self.Tab_4_1_Name_Input.setText(Name)

        tolist = getattr(Matrix, "tolist", None)
        if callable(tolist):
            ValueList = Matrix.tolist()
        else:
            ValueList = [[Matrix]]
        for i,a in enumerate(ValueList): # pylint: disable=unused-variable
            for j,b in enumerate(ValueList[i]):
                item = Qt.QTableWidgetItem()
                item.setText(str(b))
                self.Tab_4_1_Matrix_Input.setItem(i,j,item)

    def Tab_4_F_Config_Matrix_Dim(self):
        h,w = self.Tab_4_1_Dimension_Input.text().split("x")
        try:
            h = int(h) if int(h) > 0 else 1
            self.Tab_4_1_Matrix_Input.setRowCount(h)
        except common_exceptions:
            pass
        try:
            w = int(w)
            self.Tab_4_1_Matrix_Input.setColumnCount(w)
        except common_exceptions:
            pass
        for i in range(self.Tab_4_1_Matrix_Input.columnCount()):
            self.Tab_4_1_Matrix_Input.setColumnWidth(i,75)
        
    def Tab_4_F_Save_Matrix(self):
        try:
            NameInvalid=False
            Name = AF.AstusParse(self.Tab_4_1_Name_Input.text()).strip()
            if Name == "" or " " in Name: #TODO: Better checks!!!
                NameInvalid=True

            if NameInvalid:
                self.NotifyUser(1,"Matrix Name Invalid")
                return False
            
            # Read the Input and save it in a nested List
            Matrix = []
            MError = ""
            for i in range(self.Tab_4_1_Matrix_Input.rowCount()):
                Matrix.append([])
                for j in range(self.Tab_4_1_Matrix_Input.columnCount()):
                    try:
                        if self.Tab_4_1_Matrix_Input.item(i,j).text().strip() != "":
                            Matrix[i].append(AF.AstusParse(self.Tab_4_1_Matrix_Input.item(i,j).text(),False))
                        else:
                            Matrix[i].append("0")
                    except common_exceptions:
                        MError += "Could not add item to Matrix at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Matrix[i].append("0")
            if MError != "":
                self.NotifyUser(2,MError)
            # Convert list into Matrix and save it in the Equation
            if len(Matrix) == 1 and len(Matrix[0]) == 1:
                Matrix = parse_expr(Matrix[0][0])
            else:
                Matrix = sympy.Matrix(Matrix) # https://docs.sympy.org/latest/modules/matrices/matrices.html
            self.Tab_4_Active_Equation.AddVariable(Name,Matrix)
            
            # Preapare ListWidgetItem
            item = QtWidgets.QListWidgetItem()
            h, w = AF.shape2(Matrix)
            Text = Name + " = {}".format(str(Matrix)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
            item.setText(Text)
            item.setData(100,Name)
            item.setData(101,Matrix)
            SearchFor = Name+" "

            #Remove Duplicats
            FoundItems = self.Tab_4_Matrix_List.findItems(SearchFor,QtCore.Qt.MatchStartsWith)
            if len(FoundItems) > 0:
                for i in FoundItems:
                    index = self.Tab_4_Matrix_List.indexFromItem(i)
                    self.Tab_4_Matrix_List.takeItem(index.row())

            # Add to the Matrix List
            self.Tab_4_Matrix_List.addItem(item)
            # Display the Matrix
            self.Tab_4_F_Display_Matrix(Name,Matrix)
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)
        
    def Tab_4_F_Update_Equation(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = False
        else:
            Eval = self.Menubar_Main_Options_action_Eval_Functions.isChecked()
        Text = self.Tab_4_FormulaInput.text()
        AMaS_Object = self.Tab_4_Active_Equation
        self.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        #self.TC(lambda ID: AT.AMaS_Worker(AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.Tab_4_F_Display , ID))
        self.TC("WORK",AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.Tab_4_F_Display)

    def Tab_4_F_Display(self, AMaS_Object): # TODO: Display the Equation in addition to the solution
        self.Tab_4_Currently_Displayed = AMaS_Object.EvaluationEquation
        self.Tab_4_Currently_Displayed_Solution = AMaS_Object.Evaluation
        returnTuple = self.Tab_4_Display.Display(AMaS_Object.LaTeX_E_L, AMaS_Object.LaTeX_E_N
                                        ,self.TopBar_Font_Size_spinBox.value()
                                        ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        if returnTuple[0] != 0:
            self.NotifyUser(returnTuple[0],returnTuple[1])
        
    def Tab_4_F_Display_Matrix(self,Name,Matrix):
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
        self.Tab_4_Currently_Displayed = Text + str(Matrix)
        self.Tab_4_Currently_Displayed_Solution = str(Matrix)
        returnTuple = self.Tab_4_Display.Display(Text1,Text2
                                        ,self.TopBar_Font_Size_spinBox.value()
                                        ,self.Menubar_Main_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        if returnTuple[0] != 0:
            self.NotifyUser(returnTuple[0],returnTuple[1])


# ---------------------------------- Tab_5_ (Mind-)Control ----------------------------------
    def Tab_5_1_System_Set_Order(self,Order=None):
        if type(Order) != int:
            Order = self.Tab_5_1_SystemOrder_Spinbox.value()
        
        # Transfer
        ## Add/Remove Columns
        shift = Order+1-self.Tab_5_1_System_1TF_tableWidget.columnCount()
        if shift > 0:
            for i in range(abs(shift)):
                self.Tab_5_1_System_1TF_tableWidget.insertColumn(0)
        elif shift < 0:
            for i in range(abs(shift)):
                self.Tab_5_1_System_1TF_tableWidget.removeColumn(0)

        ## Set Header Labels
        HeaderLabel = []
        i=Order
        while i >=0:
            s="s{}".format(i)
            HeaderLabel.append(u''.join(dict(zip(u"0123456789", u"⁰¹²³⁴⁵⁶⁷⁸⁹")).get(c, c) for c in s))
            i-=1
        self.Tab_5_1_System_1TF_tableWidget.setHorizontalHeaderLabels(HeaderLabel)

        # State System
        #TODO: Adjust other input methods
        #TODO: For SS set the HeaderLabels to x₁,x₂,...

        # ODE
        #TODO: Adjust other input methods

    def Tab_5_1_System_Save(self):
        Tab = self.Tab_5_1_Input_tabWidget.currentIndex()
        try:
            NameInvalid=False
            Name = AF.AstusParse(self.Tab_5_1_NameInput.text()).strip()
            if Name == "" or " " in Name: #TODO: Better checks!!!
                NameInvalid=True

            if NameInvalid:
                self.NotifyUser(1,"System Name Invalid")
                return False



            if Tab == 0: #Autoarrange Transfer Function
                # Parse the input and find out the coefficients of the powers of s
                s = sympy.symbols("s")
                try:
                    Ys_r = sympy.poly(sympy.expand(parse_expr(AF.AstusParse(self.Tab_5_1_System_4ATF_Ys.text())).doit().evalf()),s)
                    #a = list(reversed(Ys_r.collect(s).as_ordered_terms()))
                    #Ys = [a[p].coeff(s**p) for p in range(len(a)-1,0,-1)] # 0 is not included on purpose
                    #Ys.append(a[0]) # get the coefficient of s^0
                    #for i,v in enumerate(Ys): # Make sure that the type is correct
                    #    val = str(v)
                    #    if "s" in val: # If coefficient = 1, s is returned.
                    #        val = "1"  # This is handeled here.
                    #    Ys[i] = float(val)
                    terms = Ys_r.all_terms()
                    Ys = []
                    for i in terms:
                        Ys.append(float(i[1]))
                    print(Ys)
                except common_exceptions:
                    Error = "Error in Y(s)"
                    Error += ExceptionOutput(sys.exc_info())
                    self.NotifyUser(1,Error)
                    return False
                try:
                    Xs_r = sympy.poly(sympy.expand(parse_expr(AF.AstusParse(self.Tab_5_1_System_4ATF_Xs.text())).doit().evalf()),s)
                    #a = list(reversed(Xs_r.collect(s).as_ordered_terms()))
                    #Xs = [a[p].coeff(s**p) for p in range(len(a)-1,0,-1)] # 0 is not included on purpose
                    #Xs.append(a[0]) # get the coefficient of s^0
                    #for i,v in enumerate(Xs): # Make sure that the type is correct
                    #    val = str(v)
                    #    if "s" in val: # If coefficient = 1, s is returned.
                    #        val = "1"  # This is handeled here.
                    #    Xs[i] = float(val)
                    terms = Xs_r.all_terms()
                    Xs = []
                    for i in terms:
                        Xs.append(float(i[1]))
                    print(Xs)
                except common_exceptions:
                    Error = "Error in X(s)"
                    Error += ExceptionOutput(sys.exc_info())
                    self.NotifyUser(1,Error)
                    return False
                sys1 = control.tf(Ys,Xs)
            elif Tab == 1: #Transfer
                Ys = []
                Xs = []
                MError = ""
                for j in range(self.Tab_5_1_System_1TF_tableWidget.columnCount()):
                    try:
                        if self.Tab_5_1_System_1TF_tableWidget.item(0,j).text().strip() != "":
                            Ys.append(float(parse_expr(AF.AstusParse(self.Tab_5_1_System_1TF_tableWidget.item(0,j).text(),True)).doit().evalf()))
                        else:
                            Ys.append(0)
                    except common_exceptions:
                        MError += "Could not add item to System at ({},{}). Inserting a Zero instead. ".format(1,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Ys.append(0)
                    try:
                        if self.Tab_5_1_System_1TF_tableWidget.item(1,j).text().strip() != "":
                            Xs.append(float(parse_expr(AF.AstusParse(self.Tab_5_1_System_1TF_tableWidget.item(1,j).text(),True)).doit().evalf()))
                        else:
                            Xs.append(0)
                    except common_exceptions:
                        MError += "Could not add item to System at ({},{}). Inserting a Zero instead. ".format(2,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Xs.append(0)
                if MError != "":
                    self.NotifyUser(2,MError)
                # Remove epmty leading entries
                for i,y in enumerate(Ys):
                    if y == 0:
                        Ys.pop(i)
                    else:
                        break
                for i,y in enumerate(Xs):
                    if y == 0:
                        Xs.pop(i)
                    else:
                        break
                print(Ys,r"/",Xs)
                sys1 = control.tf(Ys,Xs)
            elif Tab == 2: #State System
                pass
            elif Tab == 3: #ODE
                pass
            else: # Can not occur...
                raise Exception("Tab {} in Control->Input Tab is unknown".format(Tab))
            # TODO: Save
            print(sys1)
            return sys1
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)

    def Tab_5_1_System_Plot_and_Save(self):
        sys1 = self.Tab_5_1_System_Save()
        if sys1 == False:
            pass
        else:
            self.Tab_5_1_System_Plot(sys1)

    def Tab_5_1_System_Plot(self,sys1):
        try:
            self.NotifyUser(self.Tab_5_2_Display.Display(sys1))
            self.Tab_5_tabWidget.setFocus()
            self.Tab_5_3_SingleDisplay.clear()
            self.Tab_5_tabWidget.setCurrentIndex(1)
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            self.NotifyUser(1,Error)

    def Tab_5_4_Dirty_Display(self):
        if not self.Menubar_Main_Options_action_Advanced_Mode.isChecked():
            self.NotifyUser(3,"This is the danger zone!\nPlease activate Advanced Mode to confirm that you know what you are doing!")
        else:
            self.Tab_5_tabWidget.setCurrentIndex(1)
            input_text = "from External_Libraries.python_control_master.control import * \nglobal sys1\nglobal f\nf=\"\"\n" + self.Tab_5_4_Dirty_Input.toPlainText()
            #K_D,K_P,K_i = 0,1,0
            try:
                g,l = dict(),dict()
                exec(input_text,g,l)
                print(g["sys1"])
                self.NotifyUser(self.Tab_5_2_Display.Display(g["sys1"],Ufunc=g["f"]))
                self.Tab_5_tabWidget.setFocus()
                self.Tab_5_3_SingleDisplay.clear()
            except common_exceptions:
                Error = ExceptionOutput(sys.exc_info())
                self.Tab_5_tabWidget.setCurrentIndex(3)
                self.NotifyUser(1,Error)

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
    print(datetime.datetime.now().strftime('%H:%M:%S:'),"AMaDiA Started\n")
    window.LastOpenState()
    sys.exit(app.exec_())

