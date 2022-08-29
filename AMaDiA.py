# This Python file uses the following encoding: utf-8
Version = "0.18.dev-3"
# Version should be interpreted as: (MAIN).(TOPIC).(FUNCTION).(BUGFIX)
# MAIN marks mayor milestones of the project (like the release)
# TOPIC marks the introduction of
#       a new functionality like the addition of a new tab or window that can handle a new mathematical topic
#       major internal changes like the introduction of the custom window class
#   These introductions are only that: introductions
#   Further updates complete the TOPIC. These updates may also be part of a different TOPIC version.
# FUNCTION marks the introduction of new functionality and aim to advance the current TOPIC
# BUGFIX marks very minor updates that:
#       fix bugs
#       optimize (or even add minor) functions by changing a single line
#       edit text
Author = "Robin \'Astus\' Albers"
WindowTitle = "AMaDiA v"
WindowTitle+= Version
WindowTitle+= " by "
WindowTitle+= Author
#region ---------------------------------- imports ----------------------------------
Copyright_Short =   """
                        Copyright (C) 2021  Robin Albers

                        This program is distributed in the hope that it will be useful,
                        but WITHOUT ANY WARRANTY; without even the implied warranty of
                        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                        GNU General Public License for more details.

                        You should have received a copy of the GNU General Public License
                        along with this program.  If not, see <https://www.gnu.org/licenses/>.
                    """

import datetime
import platform
if __name__ == "__main__":
    print()
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    print(WindowTitle)
    print("Loading Modules")#,end="")
    if platform.system() == 'Windows':
        try:
            import ctypes
            myAppId = u'{}{}'.format(WindowTitle , datetime.datetime.now().strftime('%H:%M:%S')) # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppId)
        except:
            pass

from AGeLib import *
import AGeLib

# import qt Modules

# import standard modules
from distutils.spawn import find_executable
import sys
import socket
import time
import errno
import os
import pathlib
import importlib
import re
import getpass
import traceback

try:
    import typing
except:
    pass

# import Maths modules
import matplotlib
import sympy
from sympy.parsing.sympy_parser import parse_expr
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Import AMaDiA Core Modules
# To Convert ui to py: (Commands for Anaconda Prompt)
# cd C:"\Users\Robin\Desktop\Projects\AMaDiA\AMaDiA_Files"
# cd /home/robin/Projects/AMaDiA/AMaDiA_Files/
# pyuic5 AMaDiAUI.ui -o AMaDiAUI.py
from AMaDiA_Files.AMaDiAUI import Ui_AMaDiA_Main_Window
from AMaDiA_Files.AMaDiA_Options_UI import Ui_AMaDiA_Options
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART
from AMaDiA_Files import AMaDiA_Threads as AT
from AMaDiA_Files import AMaDiA_Tabs
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
#from External_Libraries.python_control_master import control
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
except: #TODO The check whether Slycot is installed should not be in AMaDiA's main window but in the Control Window
    print("\nCould not import Slycot:")
    ExceptionOutput(sys.exc_info())
    print()
    slycot_Installed = False
else:
    slycot_Installed = True

if typing.TYPE_CHECKING:
    def App() -> "AMaDiA_Main_App":
        return AGeCore.App()

np.set_printoptions(threshold=100)

AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier
MetaModifier = QtCore.Qt.MetaModifier
#endregion

def AltGr_Shortcut(Symbol,shift_Symbol):
    if Keyboard_Remap_Works:
        if keyboard.is_pressed("shift"):
            AltGr_Shift_Shortcut(shift_Symbol)
        else:
            keyboard.write(Symbol)
            keyboard.release("alt")
            keyboard.release("control")
    else:
        print("Could not load External_Libraries.keyboard_master.keyboard")
def AltGr_Shift_Shortcut(Symbol):
    if Keyboard_Remap_Works:
        keyboard.write(Symbol)
        keyboard.release("alt")
        keyboard.release("control")
        keyboard.press("shift")
    else:
        print("Could not load External_Libraries.keyboard_master.keyboard")
def Superscript_Shortcut(Symbol):
    if Keyboard_Remap_Works:
        #keyboard.write("\x08")
        keyboard.write(Symbol)
        keyboard.write(" ")
        keyboard.write("\x08")
    else:
        print("Could not load External_Libraries.keyboard_master.keyboard")

#region ---------------------------------- Windows ----------------------------------
class AMaDiA_Internal_File_Display_Window(AWWF):
    def __init__(self,FileName,parent = None):
        try:
            super(AMaDiA_Internal_File_Display_Window, self).__init__(parent,True)
            self.setWindowTitle(FileName)
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogInfoView))
                
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.TextBrowser = QtWidgets.QTextBrowser(self)
            self.TextBrowser.setObjectName("TextBrowser")


            self.gridLayout.addWidget(self.TextBrowser, 0, 0, 0, 0)
            self.setCentralWidget(self.centralwidget)

            self.load(FileName)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

    def load(self,FileName):
        try:
            if "Patchlog" in FileName:
                self.setWindowTitle("Patchlog")
                #self.FolderPath = os.path.dirname(__file__)
                FileName = os.path.join(QtWidgets.QApplication.instance().FolderPath,FileName)
                with open(FileName,'r',encoding="utf-8") as text_file:
                    Text = text_file.read()
                
                List = re.split(r"\nv(0.+):(.+)", Text)
                
                NList = []
                i=1
                while i < len(List):
                    NList.append([List[i],"v"+List[i]+":"+List[i+1],List[i+2]])
                    i+=3
                text = ""
                for i in reversed(NList):
                    desc = "<ul>"+re.sub(r"^\+ (.+)$",r"\t<li>\1</li>",
                                        re.sub(r"^\+\+ (.+)$",r"\t\t\t<ul><li>\1</li></ul>",
                                                re.sub(r"^\+\+\+ (.+)$",r"\t\t\t\t<ul><ul><li>\1</li></ul></ul>",
                                                    re.sub(r"^\+\+\+\+ (.+)$",r"\t\t\t\t\t<ul><ul><ul><li>\1</li></ul></ul></ul>",i[2],
                                                            flags=re.MULTILINE),
                                                    flags=re.MULTILINE),
                                                flags=re.MULTILINE),
                                        flags=re.MULTILINE)+"</ul>"
                    text += "{}{}<br><br>".format(i[1],desc)
                self.TextBrowser.setText(text)
            else:
                self.setWindowTitle(FileName)
                #self.FolderPath = os.path.dirname(__file__)
                FileName = os.path.join(QtWidgets.QApplication.instance().FolderPath,FileName)
                with open(FileName,'r',encoding="utf-8") as text_file:
                    Text = text_file.read()
                #self.TextBrowser.setPlainText(Text)
                self.TextBrowser.setText(Text)
        except common_exceptions:
            NC(1,"Could not load {}".format(str(FileName)),exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_Internal_File_Display_Window.load",input=FileName)

    def Scroll_To_End(self):
        self.TextBrowser.verticalScrollBar().setValue(self.TextBrowser.verticalScrollBar().maximum())
        
class AMaDiA_About_Window(AWWF):
    def __init__(self,parent = None):
        try:
            super(AMaDiA_About_Window, self).__init__(parent)
            self.setWindowTitle("About AMaDiA")
            self.StandardSize = (400, 600)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogHelpButton))

            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.TextBrowser = QtWidgets.QTextBrowser(self)
            self.TextBrowser.setObjectName("TextBrowser")

            self.gridLayout.addWidget(self.TextBrowser, 0, 0, 0, 0)
            #self.layout = QtWidgets.QVBoxLayout()
            #self.layout.addWidget(self.TextBrowser)
            #self.setLayout(self.layout)
            self.setCentralWidget(self.centralwidget)

            #Text = WindowTitle+"\nWIP: More coming soon"
            #<p> Send comments, ideas and bug reports to: <a href="mailto:a011235robin@gmail.com">a011235robin@gmail.com</a></p>
            aboutText = """
            <p> <b>AMaDiA v%s</b> </p>
            <p> By Robin \"Astus\" Albers.</p>
            <p> AMaDiA aims to provide the similar functionality as matlab or mathematica while providing a GUI that is fun to work with.</p>
            <p> Furthermore the open source nature and the good documentation from SymPy (which is used for most calculations) allow for scientific work as the entire process can be analysed.</p>
            <p> License is GNU GPLv3.</p>
            <p> Repo: <a href="https://github.com/AstusRush/AMaDiA">https://github.com/AstusRush/AMaDiA</a></p>
            <p>This instance of AMaDiA runs thanks to the following external projects:</p>
            
            <ul>
                    <li><a href="https://www.python.org/">Python %s</a></li>
                    <li><a href="https://github.com/AstusRush/AGeLib">AGeLib %s</a></li>
                    <li><a href="https://www.sympy.org/en/index.html">SymPy %s</a></li>
                    <li><a href="https://numpy.org/">Numpy %s</a></li>
                    <li><a href="https://matplotlib.org/">MatplotLib %s</a></li>
                    <li><a href="https://github.com/boppreh/keyboard">keyboard</a></li>
                    <li><a href="https://github.com/python-control/python-control/">Python-Control</a></li>
            """ % (Version,
                "%d.%d" % (sys.version_info.major, sys.version_info.minor),
                AGeLib.AGeLibVersion,
                sympy.__version__,
                np.__version__,
                matplotlib.__version__)
                
            if QtVersion == "PyQt5": # type: ignore
                aboutText += """\n        <li><a href="https://riverbankcomputing.com/software/pyqt/">PyQt %s</a> <a href="https://www.qt.io/">(Qt %s)</a></li>""" % (QtCore.PYQT_VERSION_STR, QtCore.qVersion())
            elif QtVersion == "PyQt6": # type: ignore
                aboutText += """\n        <li><a href="https://riverbankcomputing.com/software/pyqt/">PyQt %s</a> <a href="https://www.qt.io/">(Qt %s)</a></li>""" % (QtCore.PYQT_VERSION_STR, QtCore.qVersion())
            elif QtVersion == "PySide6": # type: ignore
                aboutText += """\n        <li><a href="https://www.qt.io/qt-for-python">PySide6 (Qt %s)</a></li>""" % (QtCore.qVersion())
            elif QtVersion == "PySide2": # type: ignore
                aboutText += """\n        <li><a href="https://www.qt.io/qt-for-python">PySide2 (Qt %s)</a></li>""" % (QtCore.qVersion())
            
            aboutText += "\n</ul>"
            self.TextBrowser.setText(aboutText)
            self.TextBrowser.setOpenExternalLinks(True)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            ExceptionOutput(sys.exc_info())

class AMaDiA_exec_Window(AWWF): #CLEANUP: use the standard AGeLib exec_Window
    def __init__(self,parent = None):
        try:
            super(AMaDiA_exec_Window, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True, IncludeAdvancedCB=True)
            self.setWindowTitle("Code Execution Window")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.Input_Field = AW.AMaDiA_TextEdit(self)
            self.Input_Field.setObjectName("Input_Field")


            self.gridLayout.addWidget(self.Input_Field, 0, 0, 0, 0)
            self.setCentralWidget(self.centralwidget)

            self.Input_Field.returnCtrlPressed.connect(self.execute_code)
            
            self.setAutoFillBackground(True)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_exec_Window.__init__")

    def execute_code(self):
        input_text = self.Input_Field.toPlainText()
        try:
            exec(input_text)
        except common_exceptions:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_exec_Window.execute_code",input=input_text)

class AMaDiA_options_window(AWWF, Ui_AMaDiA_Options):
    def __init__(self,parent = None):
        try:
            super(AMaDiA_options_window, self).__init__(parent, IncludeTopBar=False, initTopBar=False, IncludeStatusBar=True)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogListView))
            self.setupUi(self)
            self.TopBar = AGeWidgets.TopBar_Widget(self,False)
            self.TabWidget.setCornerWidget(self.TopBar, QtCore.Qt.TopRightCorner)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True)
            self.setWindowTitle("Options")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.TabWidget.setCurrentIndex(0)
            
            self.setAutoFillBackground(True)
            self.ConnectSignals()
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
            
    def ConnectSignals(self):
        self.cb_O_AdvancedMode.clicked.connect(QtWidgets.QApplication.instance().toggleAdvancedMode)
        QtWidgets.QApplication.instance().S_advanced_mode_changed.connect(self.cb_O_AdvancedMode.setChecked)
        self.cb_O_Remapper_global.toggled.connect(self.ToggleGlobalRemapper)
        self.cb_O_PairHighlighter.toggled.connect(App().S_Highlighter.emit)

    def ToggleGlobalRemapper(self):
        try:
            if self.cb_O_Remapper_global.isChecked():
                self.cb_O_Remapper_local.setChecked(False)
                self.cb_O_Remapper_local.setDisabled(True)
                altgr = "altgr+"
                altgrShift = "altgr+shift+"
                #keyboard.on_press(print)
                #keyboard.add_hotkey("shift",keyboard.release, args=("altgr"),trigger_on_release=True)
                #keyboard.block_key("AltGr")
                #keyboard.add_hotkey("altgr",keyboard.release, args=("alt+control"), suppress=True)
                #keyboard.add_hotkey("control+alt+altgr+shift",keyboard.release, args=("altgr+shift"), suppress=True)
                for i in ART.KR_Map:
                    if i[0]!=" ":
                        if i[2] != " ":
                            Key = altgr + i[0]
                            keyboard.add_hotkey(Key, AltGr_Shortcut, args=(i[2],i[3]), suppress=True, trigger_on_release=True)
                            #keyboard.add_hotkey(Key, keyboard.write, args=(i[2]), suppress=True, trigger_on_release=True)
                        if i[3] != " ":
                            Key = altgrShift + i[0]
                            keyboard.add_hotkey(Key, AltGr_Shift_Shortcut, args=(i[3]), suppress=True, trigger_on_release=True)
                            #keyboard.add_hotkey(Key, keyboard.write, args=(i[3]), suppress=True, trigger_on_release=True)
                        if i[4] != " ":
                            Key = "^+"+i[0]
                            keyboard.add_hotkey(Key, Superscript_Shortcut, args=(i[4]), suppress=True, trigger_on_release=True)
                            #keyboard.add_hotkey(Key, keyboard.write, args=(i[4]), suppress=True, trigger_on_release=True)
            else:
                keyboard.clear_all_hotkeys()
                self.cb_O_Remapper_local.setEnabled(True)
                self.cb_O_Remapper_local.setChecked(True)
        except common_exceptions :
            try:
                NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_options_window.ToggleGlobalRemapper",input="Failed to map {} to {}".format(str(i),str(Key)))
            except common_exceptions :
                NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_options_window.ToggleGlobalRemapper",input="Could not determine failed remap operation.")

#endregion

# ---------------------------------- Main Application ----------------------------------
class AMaDiA_Main_App(AGeApp):
 #
    # See:
    # https://doc.qt.io/qt-5/qapplication.html
    # https://doc.qt.io/qt-5/qguiapplication.html
    # https://doc.qt.io/qt-5/qcoreapplication.html
    S_New_Notification = QtCore.pyqtSignal(NC)
    S_Highlighter = QtCore.pyqtSignal(bool)
    def __init__(self, args):
        super(AMaDiA_Main_App, self).__init__(args)
        self.installEventFilter(self)
        self.MainWindow:AMaDiA_Main_Window = None
        self.setApplicationName("AMaDiA")
        self.setApplicationVersion(Version)
        
        #CRITICAL: I found a great font: Cambria
        #       It really makes it easy to read formulas and 
        #       How common is it? Could it be a good standard font?
        
        self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        
        self._init_colourAndFont("Cambria") #TODO: This is unnecessary, isn't it? EDIT: Not if we set a font here
        
        self.AMaDiA_exec_Window_Window = None
    
    def r_generateModuleVersions(self):
        # type: () -> tuple[str,typing.Dict[str,str]]
        AppVersion = "AMaDiA {}".format(Version)
        ModuleDict = {"SymPy" : sympy.__version__}
        return AppVersion, ModuleDict
    
    def eventFilter(self, source, event):
        if event.type() == 6: # QtCore.QEvent.KeyPress
            #if event.modifiers() == ControlModifier:
            #    pass
            #if event.modifiers() == AltModifier:
            #    pass
            #    #if event.key() == QtCore.Qt.Key_O: #Already part of AGeLib
            #    #    self.showWindow_Options()
            #    #    return True
            if source == self.MainWindow: # THIS IS SPECIFIC TO AMaDiA_Main_Window #TODO: move this to the main window... Why did I even put this here in the first place?!
                if event.modifiers() == ControlModifier:
                    if event.key() == QtCore.Qt.Key_1:
                        self.MainWindow.TabWidget.setCurrentIndex(0)
                        self.MainWindow.Tab_1.InputField.setFocus()
                        return True
                    elif event.key() == QtCore.Qt.Key_2:
                        self.MainWindow.TabWidget.setCurrentIndex(1)
                        self.MainWindow.Tab_2_InputField.setFocus()
                        return True
                    elif event.key() == QtCore.Qt.Key_3:
                        self.MainWindow.TabWidget.setCurrentIndex(2)
                        if self.MainWindow.Tab_3_tabWidget.currentIndex() == 0:
                            self.MainWindow.Tab_3_1_Formula_Field.setFocus()
                        return True
                    elif event.key() == QtCore.Qt.Key_4:
                        self.MainWindow.TabWidget.setCurrentIndex(3)
                        return True
                    elif event.key() == QtCore.Qt.Key_5:
                        self.MainWindow.TabWidget.setCurrentIndex(4)
                        return True
            try:  # THIS IS SPECIFIC TO AMaDiA_Main_Window # FEATURE: Add superscript Macros
                #if self.MainWindow.Menu_Options_action_Use_Local_Keyboard_Remapper.isChecked():
                if self.optionWindow.cb_O_Remapper_local.isChecked():
                    modifiers = QtWidgets.QApplication.keyboardModifiers() # instead of event.modifiers() to be more reliable
                    if modifiers == (GroupSwitchModifier | ShiftModifier) or modifiers == (ControlModifier | AltModifier | ShiftModifier):
                        for i in ART.KR_Map:
                            if event.key() == i[5] and i[3]!=" ":
                                try:
                                    if type(source) == QtWidgets.QLineEdit or type(source) == AstusChat_Client.InputFieldClass:
                                        source.insert(i[3])
                                        return True
                                except:
                                    pass
                                try:
                                    cursor = source.textCursor()
                                    cursor.insertText(i[3])
                                    return True
                                except:
                                    break
                    elif modifiers == GroupSwitchModifier or modifiers == (ControlModifier | AltModifier):
                        for i in ART.KR_Map:
                            if event.key() == i[5] and i[2]!=" ":
                                try:
                                    if type(source) == QtWidgets.QLineEdit or type(source) == AstusChat_Client.InputFieldClass:
                                        source.insert(i[2])
                                        return True
                                except:
                                    pass
                                try:
                                    cursor = source.textCursor()
                                    cursor.insertText(i[2])
                                    return True
                                except:
                                    break
            except AttributeError:
                pass
        return super(AMaDiA_Main_App, self).eventFilter(source, event)

 # ---------------------------------- Colour and Font ----------------------------------
    #def setTheme(self, Colour = "Dark"):
    #    super(AMaDiA_Main_App, self).setTheme(Colour)
    #    if self.MainWindow != None: # THIS IS SPECIFIC TO AMaDiA_Main_Window
    #        try:
    #            self.MainWindow.init_Animations_With_Colour()
    #            brush = self.Palette.text()
    #            for i in range(self.MainWindow.Tab_3_1_History.count()):
    #                if self.MainWindow.Tab_3_1_History.item(i).data(100).current_ax == None:
    #                    self.MainWindow.Tab_3_1_History.item(i).setForeground(brush)
    #        except common_exceptions:
    #            ExceptionOutput(sys.exc_info())
                
    def r_recolour(self):
        if self.MainWindow != None:
            try:
                self.MainWindow.init_Animations_With_Colour()
                brush = self.Palette.text()
                for i in range(self.MainWindow.Tab_3_1_History.count()):
                    if self.MainWindow.Tab_3_1_History.item(i).data(100).current_ax == None:
                        self.MainWindow.Tab_3_1_History.item(i).setForeground(brush)
                self.MainWindow.Tab_1.InputField.setPalette(self.Palette2)
                self.MainWindow.Tab_2_InputField.setPalette(self.Palette2)
                self.MainWindow.Tab_3_1_Formula_Field.setPalette(self.Palette2)
                self.MainWindow.Tab_4_FormulaInput.setPalette(self.Palette2)
            except common_exceptions:
                ExceptionOutput(sys.exc_info())

 # ---------------------------------- SubWindows ----------------------------------
    def r_init_Options(self):
        self.optionWindow = AMaDiA_options_window()

 # ---------------------------------- Other ----------------------------------

    def r_createFolders(self):
        try:
            if self.AGeLibPathOK:
                # Create Plots folder to save plots
                self.PlotPath = os.path.join(os.path.join(self.AGeLibPath,"AMaDiA"),"Plots")
                os.makedirs(self.PlotPath,exist_ok=True)
                # Create Config folder to save configs
                self.ConfigFolderPath = os.path.join(os.path.join(self.AGeLibPath,"AMaDiA"),"Config")
                os.makedirs(self.ConfigFolderPath,exist_ok=True)
            self.pathOK = False
            # Find the install location of AMaDiA to load the help files
            self.selfPath = os.path.abspath(__file__)
            self.FolderPath = os.path.dirname(__file__)
            # Check if the path that was returned is correct
            filePath = os.path.join(self.FolderPath,"AMaDiA.py")
            filePath = pathlib.Path(filePath)
            if filePath.is_file():
                self.pathOK = True
        except:
            NC(1,"Could not create/validate AMaDiA folders",exc=sys.exc_info())
            



# ---------------------------------- Main Window ----------------------------------
class AMaDiA_Main_Window(AWWF, Ui_AMaDiA_Main_Window):
    S_Terminate_Threads = QtCore.pyqtSignal()
    def __init__(self, MainApp, parent = None):
        super(AMaDiA_Main_Window, self).__init__(parent,initTopBar=False)
        
        # Read all config files:
        # FEATURE: Implement config files
        
        sympy.init_printing() # doctest: +SKIP
        self.MainApp = MainApp #CLEANUP: remove self.MainApp since App() has replaced it
        App().setMainWindow(self)
        
        #FEATURE: Add Statistic Tab to easily compare numbers and check impact of variables etc
        #FEATURE: Make a subtab that makes https://www.youtube.com/watch?v=ovJcsL7vyrk and similar things plottable
        
        
       # Build the UI
        self.init_Menu()
        
        ###
        self.setObjectName("AMaDiA_Main_Window")
        self.resize(906, 634)
        self.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.TabWidget = AGeWidgets.MTabWidget(self.centralwidget)
        self.TabWidget.setAutoFillBackground(True)
        self.TabWidget.setUsesScrollButtons(False)
        self.TabWidget.setObjectName("TabWidget")
        self.Tab_1 = AMaDiA_Tabs.Tab_Calculator(self)
        self.TabWidget.addTab(self.Tab_1, "")
        self.setupUi(self)
        ###
        
        self.TopBar.init(True,True,True)
        self.TopBar.setObjectName("TopBar")
        #self.TopBarGridLayout = QtWidgets.QGridLayout(self.TopBar)
        #self.TopBarGridLayout.setContentsMargins(0, 0, 0, 0)
        #self.TopBarGridLayout.setSpacing(0)
        #self.TopBarGridLayout.setObjectName("TopBarGridLayout")
        #self.TopBar.setLayout(self.TopBarGridLayout)
        
        self.StandardSize = (906, 634)
        #self.resize(*self.StandardSize)
        
        self.TabWidget.setContentsMargins(0,0,0,0)
        #self.TabWidget.tabBar(). # Access the TabBar of the TabWidget
        self.TabWidget.tabBar().setUsesScrollButtons(True)
        self.TabWidget.tabBar().setGeometry(QtCore.QRect(0, 0, 906, 20)) # CLEANUP: Is this necessary?
        self.TabWidget.tabBar().installEventFilter(self.TopBar)
        
        #self.MenuBar.setContentsMargins(0,0,0,0)
        
        #QtWidgets.QMainWindow.setMenuBar(self,self.MenuBar) # This allows the extension functionality but has no frame...
        #self.setMenuBar(self.MenuBar) # This breaks the extension functionality but has a frame...
        
        #self.MenuBar.setCornerWidget(self.TopBar)
        
        self.Tab_3_1_Button_Plot_SymPy.setVisible(False) # CLEANUP: The Control Tab Has broken the Sympy plotter... Repairing it is not worth it... Remove this function...
        
        # MAYBE: Do something with the Statusbar
        
       # Set UI variables
        #Set starting tabs
        self.Tab_3_tabWidget.setCurrentIndex(0)
        self.Tab_3_1_TabWidget.setCurrentIndex(0)
        self.Tab_4_tabWidget.setCurrentIndex(0)
        self.TabWidget.setCurrentIndex(0)
        
        #Set Splitter Start Values
        self.Tab_2_UpperSplitter.setSizes([163,699])
        self.Tab_2_LowerSplitter.setSizes([391,70])
        self.Tab_3_1_splitter.setSizes([297,565])
        #To configure use:
        #print(self.Tab_2_UpperSplitter.sizes())
        #print(self.Tab_2_LowerSplitter.sizes())
        #print(self.Tab_3_1_splitter.sizes())
        
        
       # Initialize subwindow variables
        self.ControlWindow = None
        self.AMaDiA_About_Window_Window = None
        self.Chat = None
        self.Sever = None
        self.AMaDiA_Text_File_Window = {}
       # Initialize important variables and lists
        self.workingThreads = 0
        self.LastOpenState = lambda: self.showNormal()
        self.Bool_PreloadLaTeX = True
        self.firstrelease = False
        self.keylist = []
        try:
            self.Tab_2_Eval_checkBox.setCheckState(1)
        except:
            self.Tab_2_Eval_checkBox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        
       # Initialize Thread Related Things:
        self.ThreadList = []
        self.oldThreadpools = []
        self.threadpool = QtCore.QThreadPool()#.globalInstance()
        #self.threadpool.setMaxThreadCount(8)
        print("Multithreading with maximum %d threads (when in Threadpool mode)" % self.threadpool.maxThreadCount())
        # Thread Mode
        self.Threading = "POOL"
        #self.Threading = "LIST"
        
       # Set the Text
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AMaDiA" , WindowTitle))
        
       # EventFilter
        self.installEventFilter(self)
        # Set up context menus for the histories and other list widgets
        for i in self.findChildren(QtWidgets.QListWidget):
            i.installEventFilter(self)
        # Set up text input related Event Handlers
        for i in self.findChildren(QtWidgets.QTextEdit):
            i.installEventFilter(self)
        for i in self.findChildren(QtWidgets.QLineEdit):
            i.installEventFilter(self)
        
        # Activate Pretty-LaTeX-Mode if the Computer supports it
        if AF.LaTeX_dvipng_Installed:
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setEnabled(True)
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setChecked(True)
        
       # Run other init methods
        self.ConnectSignals()
        #self._init_colourAndFont()
        App().setTheme() #IMPROVE: This takes long but is necessary to initialize the Plots.
        #                                    This could probably be done in the init of the Canvas to reduce start time
        #       But the Signal S_ColourChanged as well as the method r_recolour are now used for other UI elements as well thus setTheme MUST be called or the other inits must be changed, too
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
        
        # VALIDATE: Check if this fixes the bug on the Laptop --> The Bug is fixed but the question remains wether this is what fixed it
        self.Tab_3_1_F_Clear()
        #One Little Bug Fix:
            #If using LaTeX Display in LaTeX Mode before using the Plotter for the first time it can happen that the plotter is not responsive until cleared.
            #Thus the plotter is now cleared on program start to **hopefully** fix this...
            #If it does not fix the problem a more elaborate method is required...
            # A new variable that checks if the plot has already been used and if the LaTeX view has been used.
            # If the first is False and the second True then clear when the plot button is pressed and change the variables to ensure that this only happens once
            #       to not accidentally erase the plots of the user as this would be really bad...
        
        self.Tab_1.InputField.setFocus()
        
       # Welcome Message and preload LaTeX
        msg = ""
        if not AF.LaTeX_dvipng_Installed:
            msg += "Please install LaTeX and dvipng to enable the LaTeX output mode"
        elif self.Bool_PreloadLaTeX:
            print("Starting LaTeX")
            self.Tab_2_Viewer.preloadLaTeX()
        if not slycot_Installed:
            if msg != "":
                msg += "\n\n"
            msg += "slycot is not installed. Some features of the Control Window will not work.\n"
            msg += "If you have conda installed use: conda install -c conda-forge slycot\n"
            msg += "Otherwise refer to: https://github.com/python-control/Slycot"
            #msg += """Otherwise refer to: <a href="https://github.com/python-control/Slycot">https://github.com/python-control/Slycot</a>""" #REMINDER: Use this when the Notification widget and the tooltip support it
            msg += "\n(The exception that was raised when importing slycot can be seen in the console.)"
        if not Keyboard_Remap_Works:
            if msg != "":
                msg += "\n\n"
            msg += "The Keyboard Remapping does not work\n"
            msg += "If you are using Linux you need to run as root to enable Keyboard Remapping"
        if msg != "":
            try:
                exc = None
                name = "Welcome " + getpass.getuser()
            except:
                exc = sys.exc_info()
                name = "Welcome Dave"
                msg += "\n\n(Could not determine user name thus Dave was chosen.\nSee the exception in this notification for more information.)"
            name += "! Click here to read a Notification."
            NC(3,msg, exc=exc, DplStr=name, win=self.windowTitle(), func="AMaDiA_Main_Window.__init__")
        else:
            try:
                msg = "Welcome " + getpass.getuser()
                #msg += ". How can I be of service?"
                NC(10,msg,win=self.windowTitle(),func="AMaDiA_Main_Window.__init__")
            except:
                NC(1,"Could not determine user name thus Dave was chosen.",DplStr="Welcome Dave",exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_Main_Window.__init__")
    
 # ---------------------------------- Init and Maintenance ----------------------------------

    def ConnectSignals(self):
        self.Menu_Options_action_ToggleCompactMenu.changed.connect(lambda: self.ToggleCompactMenu())
        #self.Menu_Options_action_Use_Global_Keyboard_Remapper.toggled.connect(self.ToggleRemapper)
        self.Menu_Options_action_Options.triggered.connect(lambda: App().showWindow_Options())
        
        self.Menu_Options_action_Advanced_Mode.toggled.connect(QtWidgets.QApplication.instance().toggleAdvancedMode)
        QtWidgets.QApplication.instance().S_advanced_mode_changed.connect(self.Menu_Options_action_Advanced_Mode.setChecked)
        
        App().optionWindow.cb_F_EvalF.toggled.connect(self.Menu_Options_action_Eval_Functions.setChecked)
        self.Menu_Options_action_Eval_Functions.toggled.connect(App().optionWindow.cb_F_EvalF.setChecked)

        App().optionWindow.cb_O_PairHighlighter.toggled.connect(self.Menu_Options_action_Highlighter.setChecked)
        self.Menu_Options_action_Highlighter.toggled.connect(App().optionWindow.cb_O_PairHighlighter.setChecked)
        self.Menu_Options_action_Highlighter.toggled.connect(App().S_Highlighter.emit)

        self.Menu_DevOptions_action_Dev_Function.triggered.connect(self.Dev_Function)
        self.Menu_DevOptions_action_Show_AMaDiA_exec_Window.triggered.connect(App().showWindow_IDE)
        self.Menu_DevOptions_action_Use_Threadpool.changed.connect(self.ToggleThreadMode)
        self.Menu_DevOptions_action_Terminate_All_Threads.triggered.connect(self.TerminateAllThreads)

        self.Menu_Chat_action_Open_Client.triggered.connect(self.OpenClient)
        self.Menu_Chat_action_Open_Server.triggered.connect(self.OpenServer)
        
        #self.Menu_Colour_action_Dark.triggered.connect(lambda: self.setTheme("Dark"))
        #self.Menu_Colour_action_Bright.triggered.connect(lambda: self.setTheme("Bright"))
        
        self.Menu_OtherWindows_action_SystemControl.triggered.connect(lambda: self.OpenControlWindow())

        self.Menu_Help_action_Examples.triggered.connect(lambda: self.Show_AMaDiA_Text_File("InputExamples.txt"))
        self.Menu_Help_action_Helpful_Commands.triggered.connect(lambda: self.Show_AMaDiA_Text_File("Helpful_Useable_Syntax.txt"))
        self.Menu_Help_action_Patchlog.triggered.connect(lambda: self.Show_AMaDiA_Text_File("Patchlog.txt"))
        self.Menu_Help_action_About.triggered.connect(lambda: self.Show_About())
        
        self.Tab_2_History.itemDoubleClicked.connect(self.Tab_2_F_Item_doubleClicked)
        self.Tab_2_LaTeXCopyButton.clicked.connect(lambda: self.Tab_2_Viewer.action_Copy_LaTeX())
        self.Tab_2_ConvertButton.clicked.connect(lambda: self.Tab_2_F_Convert())
        self.Tab_2_InputField.returnCtrlPressed.connect(lambda: self.Tab_2_F_Convert())
        
        self.Tab_3_1_History.itemDoubleClicked.connect(self.Tab_3_1_F_Item_doubleClicked)
        self.Tab_3_1_Button_Plot.clicked.connect(lambda: self.Tab_3_1_F_Plot_Button())
        self.Tab_3_1_Formula_Field.returnPressed.connect(lambda: self.Tab_3_1_F_Plot_Button())
        self.Tab_3_1_Button_Clear.clicked.connect(lambda: self.Tab_3_1_F_Clear())
        self.Tab_3_1_Button_Plot_SymPy.clicked.connect(lambda: self.Tab_3_1_F_Sympy_Plot_Button())
        self.Tab_3_1_RedrawPlot_Button.clicked.connect(lambda: self.Tab_3_1_F_RedrawPlot())
        self.Tab_3_1_Button_SavePlot.clicked.connect(lambda: self.action_tab_3_tab_1_Display_SavePlt())
        
        self.Tab_3_3_ComplexWidget.S_Plot.connect(lambda: self.Tab_3_3_F_Plot_Button())
        
        self.Tab_4_FormulaInput.returnPressed.connect(lambda: self.Tab_4_F_Update_Equation())
        self.Tab_4_1_Dimension_Input.returnPressed.connect(lambda: self.Tab_4_F_Config_Matrix_Dim())
        self.Tab_4_1_Configure_Button.clicked.connect(lambda: self.Tab_4_F_Config_Matrix_Dim())
        self.Tab_4_1_Name_Input.returnPressed.connect(lambda: self.Tab_4_F_Save_Matrix())
        self.Tab_4_1_Save_Matrix_Button.clicked.connect(lambda: self.Tab_4_F_Save_Matrix())
        self.Tab_4_2_New_Equation_Button.clicked.connect(lambda: self.Tab_4_F_New_Equation())
        self.Tab_4_2_New_Equation_Name_Input.returnPressed.connect(lambda: self.Tab_4_F_New_Equation())
        self.Tab_4_2_Load_Selected_Button.clicked.connect(lambda: self.Tab_4_F_Load_Selected_Equation())
        
        #TODO: This is temporary:
        self.Tab_4_DirectInput.returnCtrlPressed.connect(lambda: self.Tab_4_F_Text_to_Equations())
    
    def init_Menu(self,FirstTime=True):
        if FirstTime:
            self.Menu = QtWidgets.QMenu(self)
            self.Menu.setObjectName("Menu")
            #self.MenuBar = AW.MMenuBar(self)
            #self.MenuBar.setObjectName("MenuBar")
       # Create submenus
        if FirstTime:
            self.Menu_Options = QtWidgets.QMenu(self.Menu)
            self.Menu_Options.setObjectName("Menu_Options")
            self.Menu_DevOptions = QtWidgets.QMenu(self.Menu)
            self.Menu_DevOptions.setObjectName("Menu_DevOptions")
            self.Menu_Chat = QtWidgets.QMenu(self.Menu)
            self.Menu_Chat.setObjectName("Menu_Chat")
            #self.Menu_Colour = QtWidgets.QMenu(self.Menu)
            #self.Menu_Colour.setObjectName("Menu_Colour")
            self.Menu_OtherWindows = QtWidgets.QMenu(self.Menu)
            self.Menu_OtherWindows.setObjectName("Menu_OtherWindows")
            self.Menu_Help = QtWidgets.QMenu(self.Menu)
            self.Menu_Help.setObjectName("Menu_Help")
            #self.Menu_Options_MathRemap = QtWidgets.QMenu(self.Menu_Options)
            #self.Menu_Options_MathRemap.setObjectName("Menu_Options_MathRemap")
       # Create Actions
        if FirstTime:
            self.Menu_Options_action_Options = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Options.setObjectName("Menu_Options_action_Options")
            self.Menu_Options_action_ToggleCompactMenu = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_ToggleCompactMenu.setCheckable(True)
            self.Menu_Options_action_ToggleCompactMenu.setObjectName("Menu_Options_action_ToggleCompactMenu")
            self.Menu_Options_action_ToggleCompactMenu.setChecked(False)
            self.Menu_Options_action_Advanced_Mode = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Advanced_Mode.setCheckable(True)
            self.Menu_Options_action_Advanced_Mode.setObjectName("Menu_Options_action_Advanced_Mode")
            self.Menu_Options_action_Eval_Functions = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Eval_Functions.setCheckable(True)
            self.Menu_Options_action_Eval_Functions.setChecked(True)
            self.Menu_Options_action_Eval_Functions.setObjectName("Menu_Options_action_Eval_Functions")
            self.Menu_Options_action_Use_Pretty_LaTeX_Display = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setCheckable(True)
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setEnabled(False)
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setObjectName("Menu_Options_action_Use_Pretty_LaTeX_Display")
            self.Menu_Options_action_Syntax_Highlighter = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Syntax_Highlighter.setCheckable(True)
            self.Menu_Options_action_Syntax_Highlighter.setChecked(True)
            self.Menu_Options_action_Syntax_Highlighter.setObjectName("Menu_Options_action_Syntax_Highlighter")
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper = AGeWidgets.MenuAction(self)
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper.setCheckable(True)
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper.setChecked(True)
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper.setObjectName("Menu_Options_action_Use_Local_Keyboard_Remapper")
            #self.Menu_Options_action_Use_Global_Keyboard_Remapper = AGeWidgets.MenuAction(self)
            #self.Menu_Options_action_Use_Global_Keyboard_Remapper.setCheckable(True)
            #self.Menu_Options_action_Use_Global_Keyboard_Remapper.setObjectName("Menu_Options_action_Use_Global_Keyboard_Remapper")
            self.Menu_Options_action_Highlighter = AGeWidgets.MenuAction(self)
            self.Menu_Options_action_Highlighter.setCheckable(True)
            self.Menu_Options_action_Highlighter.setChecked(True)
            self.Menu_Options_action_Highlighter.setObjectName("Menu_Options_action_Highlighter")

            self.Menu_DevOptions_action_Dev_Function = AGeWidgets.MenuAction(self)
            self.Menu_DevOptions_action_Dev_Function.setObjectName("Menu_DevOptions_action_Dev_Function")
            self.Menu_DevOptions_action_Show_AMaDiA_exec_Window = AGeWidgets.MenuAction(self)
            self.Menu_DevOptions_action_Show_AMaDiA_exec_Window.setObjectName("Menu_DevOptions_action_Show_AMaDiA_exec_Window")
            self.Menu_DevOptions_action_Use_Threadpool = AGeWidgets.MenuAction(self)
            self.Menu_DevOptions_action_Use_Threadpool.setCheckable(True)
            self.Menu_DevOptions_action_Use_Threadpool.setChecked(True)
            self.Menu_DevOptions_action_Use_Threadpool.setObjectName("Menu_DevOptions_action_Use_Threadpool")
            self.Menu_DevOptions_action_Terminate_All_Threads = AGeWidgets.MenuAction(self)
            self.Menu_DevOptions_action_Terminate_All_Threads.setObjectName("Menu_DevOptions_action_Terminate_All_Threads")

            self.Menu_Chat_action_Open_Client = AGeWidgets.MenuAction(self)
            self.Menu_Chat_action_Open_Client.setObjectName("Menu_Chat_action_Open_Client")
            self.Menu_Chat_action_Open_Server = AGeWidgets.MenuAction(self)
            self.Menu_Chat_action_Open_Server.setObjectName("Menu_Chat_action_Open_Server")

            #self.Menu_Colour_action_Dark = AGeWidgets.MenuAction(self)
            #self.Menu_Colour_action_Dark.setObjectName("Menu_Colour_action_Dark")
            #self.Menu_Colour_action_Bright = AGeWidgets.MenuAction(self)
            #self.Menu_Colour_action_Bright.setObjectName("Menu_Colour_action_Bright")
            
            self.Menu_OtherWindows_action_SystemControl = AGeWidgets.MenuAction(self)
            self.Menu_OtherWindows_action_SystemControl.setObjectName("Menu_OtherWindows_action_SystemControl")

            self.Menu_Help_action_Examples = AGeWidgets.MenuAction(self)
            self.Menu_Help_action_Examples.setObjectName("Menu_Help_action_Examples")
            self.Menu_Help_action_Helpful_Commands = AGeWidgets.MenuAction(self)
            self.Menu_Help_action_Helpful_Commands.setObjectName("Menu_Help_action_Helpful_Commands")
            self.Menu_Help_action_License = AGeWidgets.MenuAction(self)
            self.Menu_Help_action_License.setObjectName("Menu_Help_action_License")
            self.Menu_Help_action_About = AGeWidgets.MenuAction(self)
            self.Menu_Help_action_About.setObjectName("Menu_Help_action_About")
            self.Menu_Help_action_Patchlog = AGeWidgets.MenuAction(self)
            self.Menu_Help_action_Patchlog.setObjectName("Menu_Help_action_Patchlog")
       # Add the Actions to the Submenus
        if FirstTime:
            self.Menu_Options.addAction(self.Menu_Options_action_Options)
            self.Menu_Options.addAction(self.Menu_Options_action_ToggleCompactMenu)
            self.Menu_Options.addAction(self.Menu_Options_action_Advanced_Mode)
            self.Menu_Options.addAction(self.Menu_Options_action_Eval_Functions)
            self.Menu_Options.addAction(self.Menu_Options_action_Use_Pretty_LaTeX_Display)
            #self.Menu_Options_MathRemap.addAction(self.Menu_Options_action_Use_Local_Keyboard_Remapper)
            #self.Menu_Options_MathRemap.addAction(self.Menu_Options_action_Use_Global_Keyboard_Remapper)
            #self.Menu_Options.addAction(self.Menu_Options_MathRemap.menuAction())
            self.Menu_Options.addAction(self.Menu_Options_action_Highlighter)
            
            self.Menu_DevOptions.addAction(self.Menu_DevOptions_action_Dev_Function)
            self.Menu_DevOptions.addAction(self.Menu_DevOptions_action_Show_AMaDiA_exec_Window)
            self.Menu_DevOptions.addAction(self.Menu_DevOptions_action_Use_Threadpool)
            self.Menu_DevOptions.addAction(self.Menu_DevOptions_action_Terminate_All_Threads)
            
            self.Menu_Chat.addAction(self.Menu_Chat_action_Open_Client)
            self.Menu_Chat.addAction(self.Menu_Chat_action_Open_Server)
            
            #self.Menu_Colour.addAction(self.Menu_Colour_action_Dark)
            #self.Menu_Colour.addAction(self.Menu_Colour_action_Bright)
            
            self.Menu_OtherWindows.addAction(self.Menu_OtherWindows_action_SystemControl)
            
            self.Menu_Help.addAction(self.Menu_Help_action_Examples)
            self.Menu_Help.addAction(self.Menu_Help_action_Helpful_Commands)
            self.Menu_Help.addAction(self.Menu_Help_action_Patchlog)
            self.Menu_Help.addAction(self.Menu_Help_action_About)
       # Add submenus to Menu
        self.Menu.addAction(self.Menu_Options.menuAction())
        self.MenuBar.addAction(self.Menu_Options.menuAction())
        self.Menu.addAction(self.Menu_DevOptions.menuAction())
        self.MenuBar.addAction(self.Menu_DevOptions.menuAction())
        #self.Menu.addAction(self.Menu_Colour.menuAction())
        #self.MenuBar.addAction(self.Menu_Colour.menuAction())
        self.Menu.addAction(self.Menu_Chat.menuAction())
        self.MenuBar.addAction(self.Menu_Chat.menuAction())
        self.Menu.addAction(self.Menu_OtherWindows.menuAction())
        self.MenuBar.addAction(self.Menu_OtherWindows.menuAction())
        self.Menu.addAction(self.Menu_Help.menuAction())
        self.MenuBar.addAction(self.Menu_Help.menuAction())
        
       # Set the text of the menus
        if FirstTime:
            _translate = QtCore.QCoreApplication.translate
            self.Menu_Options.setTitle(_translate("AMaDiA_Main_Window", "O&ptions"))
            self.Menu_DevOptions.setTitle(_translate("AMaDiA_Main_Window", "DevOptions"))
            self.Menu_Chat.setTitle(_translate("AMaDiA_Main_Window", "Chat"))
            #self.Menu_Colour.setTitle(_translate("AMaDiA_Main_Window", "Colour"))
            self.Menu_OtherWindows.setTitle(_translate("AMaDiA_Main_Window", "More Windows"))
            self.Menu_Help.setTitle(_translate("AMaDiA_Main_Window", "Help"))

            self.Menu_Options_action_Options.setText(_translate("AMaDiA_Main_Window", "&Options"))
            self.Menu_Options_action_Options.setShortcut(_translate("AMaDiA_Main_Window", "Alt+O"))
            self.Menu_Options_action_ToggleCompactMenu.setText(_translate("AMaDiA_Main_Window", "&Compact Menu"))
            self.Menu_Options_action_ToggleCompactMenu.setShortcut(_translate("AMaDiA_Main_Window", "Alt+C"))
            self.Menu_Options_action_Advanced_Mode.setText(_translate("AMaDiA_Main_Window", "&Advanced Mode"))
            self.Menu_Options_action_Advanced_Mode.setShortcut(_translate("AMaDiA_Main_Window", "Alt+A"))
            self.Menu_Options_action_Eval_Functions.setText(_translate("AMaDiA_Main_Window", "&Eval Functions"))
            self.Menu_Options_action_Eval_Functions.setToolTip(_translate("AMaDiA_Main_Window", "If unchecked functions that would return a float are not evaluated to ensure readability"))
            self.Menu_Options_action_Eval_Functions.setShortcut(_translate("AMaDiA_Main_Window", "Alt+E"))
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setText(_translate("AMaDiA_Main_Window", "Use Pretty &LaTeX Display"))
            self.Menu_Options_action_Use_Pretty_LaTeX_Display.setShortcut(_translate("AMaDiA_Main_Window", "Alt+L"))
            self.Menu_Options_action_Syntax_Highlighter.setText(_translate("AMaDiA_Main_Window", "Syntax Highlighter"))
            self.Menu_Options_action_Highlighter.setToolTip(_translate("AMaDiA_Main_Window", "Syntax Highlighter for Brackets"))
            self.Menu_Options_action_Highlighter.setText(_translate("AMaDiA_Main_Window", "Highlighter"))
            
            #self.Menu_Options_MathRemap.setTitle(_translate("AMaDiA_Main_Window", "MathKeyboard"))
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>Use (Shift+)AltGr+Key to type Mathematical Symbols.<br/>Refer to AMaDiA_ReplacementTables for mapping.<br/>For a Remapping that works on all applications use the Global Remapper in the Options.</p></body></html>"))
            #self.Menu_Options_action_Use_Local_Keyboard_Remapper.setText(_translate("AMaDiA_Main_Window", "Local Keyboard Remapper"))
            #self.Menu_Options_action_Use_Global_Keyboard_Remapper.setText(_translate("AMaDiA_Main_Window", "Global Keyboard Remapper"))
            #self.Menu_Options_action_Use_Global_Keyboard_Remapper.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>Use (Shift+)AltGr+Key to type Mathematical Symbols.<br/>Refer to AMaDiA_ReplacementTables for mapping.<br/>This works for all inputs including those in other applications!<br/>(This might cause problems with anti cheat systems in games. Use with care.)</p></body></html>"))

            self.Menu_DevOptions_action_Dev_Function.setText(_translate("AMaDiA_Main_Window", "&Dev Function"))
            self.Menu_DevOptions_action_Dev_Function.setShortcut(_translate("AMaDiA_Main_Window", "Alt+D"))
            self.Menu_DevOptions_action_Show_AMaDiA_exec_Window.setText(_translate("AMaDiA_Main_Window", "Show Debug Terminal"))
            self.Menu_DevOptions_action_Use_Threadpool.setText(_translate("AMaDiA_Main_Window", "Use Threadpool"))
            self.Menu_DevOptions_action_Terminate_All_Threads.setText(_translate("AMaDiA_Main_Window", "Terminate All Threads"))
            self.Menu_DevOptions_action_Terminate_All_Threads.setToolTip(_translate("AMaDiA_Main_Window", "Unstable, especially in Threadpool-mode"))

            self.Menu_Chat_action_Open_Client.setText(_translate("AMaDiA_Main_Window", "Open Client"))
            self.Menu_Chat_action_Open_Server.setText(_translate("AMaDiA_Main_Window", "Open Server"))

            #self.Menu_Colour_action_Dark.setText(_translate("AMaDiA_Main_Window", "Dark"))
            #self.Menu_Colour_action_Bright.setText(_translate("AMaDiA_Main_Window", "Bright"))
            
            self.Menu_OtherWindows_action_SystemControl.setText(_translate("AMaDiA_Main_Window", "System Control"))

            self.Menu_Help_action_Examples.setText(_translate("AMaDiA_Main_Window", "Examples"))
            self.Menu_Help_action_Helpful_Commands.setText(_translate("AMaDiA_Main_Window", "Helpful Commands"))
            self.Menu_Help_action_License.setText(_translate("AMaDiA_Main_Window", "License"))
            self.Menu_Help_action_About.setText(_translate("AMaDiA_Main_Window", "About"))
            self.Menu_Help_action_Patchlog.setText(_translate("AMaDiA_Main_Window", "Patchlog"))

    def setTheme(self, Colour = "Dark"):
        App().setTheme(Colour)
        
    def InstallSyntaxHighlighter(self):
        #self.Tab_1.InputField_BracesHighlighter = AW.BracesHighlighter(self.Tab_1.InputField.document())
        pass

    def INIT_Animation(self):
        self.init_Animations_With_Colour()

    def init_Animations_With_Colour(self):
        pass#self.init_Notification_Flash()
        
 # ---------------------------------- Option Toolbar Functions ----------------------------------
    def Dev_Function(self):
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
        #
        #self.ColourMain()

        NC(3,"The DevFunction is currently not assigned",win=self.windowTitle(),func="AMaDiA_Main_Window.Dev_Function")

    def ToggleCompactMenu(self):
        #TODO: The size behaves weird when compact->scaling-up->switching->scaling-down
        self.init_Menu(False)
        if self.Menu_Options_action_ToggleCompactMenu.isChecked():
            self.MenuBar.setVisible(False)
            self.MenuBar.setParent(self)
            self.TopBar.setParent(self)
            self.setMenuBar(None)
            self.MenuBar.setCornerWidget(None)
            self.TabWidget.setCornerWidget(self.TopBar, QtCore.Qt.TopRightCorner)
            self.TopBar.setVisible(True)
            #self.TabWidget.tabBar().setUsesScrollButtons(True)
            self.TopBar.setMinimumHeight(self.MenuBar.minimumHeight())
            self.TopBar.CloseButton.setMinimumHeight(self.MenuBar.minimumHeight())
        else:
            self.MenuBar.setVisible(True)
            self.setMenuBar(self.MenuBar)
            #for i in self.findChildren(QtWidgets.QMenu):
            #    i.setPalette(self.Palette)
            #for i in self.findChildren(QtWidgets.QMenu):
            #    i.setFont(self.font())
            self.TopBar.setParent(self)
            self.TabWidget.setCornerWidget(None)
            self.MenuBar.setCornerWidget(self.TopBar, QtCore.Qt.TopRightCorner)
            self.MenuBar.updateGeometry()
            self.TopBar.setVisible(True)
            #self.TabWidget.tabBar().setUsesScrollButtons(False)
            ##Palette and font need to be reset to wake up the MenuBar painter and font-setter
            ###self.setPalette(self.style().standardPalette())
            #App().setPalette(self.style().standardPalette())
            ###self.setPalette(self.Palette)
            #App().setPalette(App().Palette)
            
            # VALIDATE: are the following 6 lines necessary if self.MenuBar.updateGeometry() is called before?
            org_font = self.font()
            font = QtGui.QFont()
            font.setFamily("unifont")
            font.setPointSize(9)
            App().setFont(font)
            App().setFont(org_font)
            
            self.TopBar.setMinimumHeight(self.TabWidget.tabBar().minimumHeight())
            self.TopBar.CloseButton.setMinimumHeight(self.TabWidget.tabBar().minimumHeight())
            
    def RUNTEST(self):
        for i in Test_Input:
            self.Tab_1.InputField.setText(i)
            self.Tab_1.calculateFieldInput()
        Text = "Expected Entries after all calculations: "+str(len(Test_Input))
        print(Text)
        self.Tab_1.InputField.setText(Text)

    def ToggleThreadMode(self):
        if self.Menu_DevOptions_action_Use_Threadpool.isChecked():
            self.Threading = "POOL"
        else:
            self.Threading = "LIST"
        
 # ---------------------------------- SubWindows ----------------------------------
    def Show_AMaDiA_Text_File(self,FileName):
        if not (FileName in self.AMaDiA_Text_File_Window):
            self.AMaDiA_Text_File_Window[FileName] = AMaDiA_Internal_File_Display_Window(FileName)
        self.AMaDiA_Text_File_Window[FileName].load(FileName)
        self.AMaDiA_Text_File_Window[FileName].show()
        QtWidgets.QApplication.instance().processEvents()
        self.AMaDiA_Text_File_Window[FileName].positionReset()
        QtWidgets.QApplication.instance().processEvents()
        self.AMaDiA_Text_File_Window[FileName].activateWindow()
        
    def AMaDiA_Text_File_ScrollToEnd(self,window):
        try:
            window.Scroll_To_End()
        except common_exceptions:
            ExceptionOutput(sys.exc_info())
        
    def Show_About(self):
        if self.AMaDiA_About_Window_Window == None:
            self.AMaDiA_About_Window_Window = AMaDiA_About_Window()
        self.AMaDiA_About_Window_Window.show()
        QtWidgets.QApplication.instance().processEvents()
        self.AMaDiA_About_Window_Window.positionReset()
        QtWidgets.QApplication.instance().processEvents()
        self.AMaDiA_About_Window_Window.activateWindow()

    def OpenClient(self):
        if self.Chat == None:
            self.Chat = AstusChat_Client.MainWindow()
        self.Chat.show()
        QtWidgets.QApplication.instance().processEvents()
        self.Chat.activateWindow()

    def OpenServer(self):
        if self.Sever == None:
            self.Sever = AstusChat_Server.MainWindow()
        self.Sever.show()
        QtWidgets.QApplication.instance().processEvents()
        self.Sever.activateWindow()

    def OpenControlWindow(self):
        try:
            if self.ControlWindow == None:
                from AMaDiA_Files.AMaDiA_SystemControl import AMaDiA_Control_Window # pylint: disable=no-name-in-module
                self.ControlWindow = AMaDiA_Control_Window()
            self.ControlWindow.show()
            QtWidgets.QApplication.instance().processEvents()
            self.ControlWindow.positionReset()
            QtWidgets.QApplication.instance().processEvents()
            self.ControlWindow.activateWindow()
        except:
            NC(lvl=1,msg="Could not open Control Window",exc=sys.exc_info(),func="AMaDiA_Main_Window.OpenControlWindow",win=self.windowTitle())

 # ---------------------------------- Events and Context Menu ----------------------------------
    def OtherContextMenuSetup(self):
        try:
            self.Tab_3_1_Display.Canvas.mpl_connect('button_press_event', self.Tab_3_1_Display_Context_Menu)
        except:
            NC(lvl=4,msg="Could not update Tab_3_1_Display context menu",exc=sys.exc_info(),func="AMaDiA_Main_Window.OtherContextMenuSetup",win=self.windowTitle())
        self.Tab_4_Display.AdditionalActions['Copy Equation'] = self.action_tab_4_Display_Copy_Displayed
        self.Tab_4_Display.AdditionalActions['Copy Solution'] = self.action_tab_4_Display_Copy_Displayed_Solution
        
        
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
            menu.setPalette(self.palette())
            menu.setFont(self.font())
            menu.exec_(cursor.pos())
        
 # ---------------------------------- Event Filter ----------------------------------

    def eventFilter(self, source, event):
        # TODO: Add more mouse button functionality! See https://doc.qt.io/qt-5/qt.html#MouseButton-enum and https://doc.qt.io/qt-5/qmouseevent.html
        #print(event.type())
        #if event.type() == 6: # QtCore.QEvent.KeyPress
        if event.type() == 82: # QtCore.QEvent.ContextMenu
         # ---------------------------------- Tab_4 Matrix List Context Menu ----------------------------------
            if (source is self.Tab_4_Matrix_List) and source.itemAt(event.pos()):
                menu = QtWidgets.QMenu()
                action = menu.addAction('Load to Editor')
                action.triggered.connect(lambda: self.action_tab_4_M_Load_into_Editor(source,event))
                action = menu.addAction('Display')
                action.triggered.connect(lambda: self.action_tab_4_M_Display(source,event))
                action = menu.addAction('Copy as String')
                action.triggered.connect(lambda: self.action_tab_4_M_Copy_string(source,event))
                action = menu.addAction('Delete')
                action.triggered.connect(lambda: self.action_tab_4_M_Delete(source,event))
                menu.setPalette(self.palette())
                menu.setFont(self.font())
                menu.exec_(event.globalPos())
                return True
        #elif...
        return super(AMaDiA_Main_Window, self).eventFilter(source, event) # let the normal eventFilter handle the event
    
 # ---------------------------------- Tab_4_Matrix_List Context Menu Actions/Functions ----------------------------------
    def action_tab_4_M_Load_into_Editor(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_4_F_Load_Matrix(Name,Matrix)
    
    def action_tab_4_M_Display(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.Tab_4_F_Display_Matrix(Name,Matrix)
    
    def action_tab_4_M_Copy_string(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(str(item.data(101)))
    
    def action_tab_4_M_Delete(self,source,event):
        # FEATURE: Paperbin for matrices: If only one item was deleted save it in a temporary List item (The same as the duplicate item from the save function)
        #                             or: When items are deleted save them temporarily and add an "undo last deletion" context menu action
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            a = source.takeItem(source.row(item))
            del self.Tab_4_Active_Equation.Variables[a.data(100)]
         
 # ---------------------------------- Tab_3_1_Display_Context_Menu ----------------------------------
    def action_tab_3_tab_1_Display_SavePlt(self):
        if App().AGeLibPathOK:
            Filename = AF.cTimeFullStr("-")
            Filename += ".png"
            Filename = os.path.join(App().PlotPath,Filename)
            try:
                print(Filename)
                self.Tab_3_1_Display.Canvas.fig.savefig(Filename , facecolor=App().BG_Colour , edgecolor=App().BG_Colour )
            except:
                NC(lvl=1,msg="Could not save Plot: ",exc=sys.exc_info(),func="AMaDiA_Main_Window.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
            else:
                NC(3,"Saved plot as: {}".format(Filename),func="AMaDiA_Main_Window.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
        else:
            print("Could not save Plot: Could not validate save location")
            NC(1,"Could not save Plot: Could not validate save location",func="AMaDiA_Main_Window.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=App().AGeLibPath)
         
 # ---------------------------------- Tab_4_Display_Context_Menu ----------------------------------
    def action_tab_4_Display_Copy_Displayed(self):
        QtWidgets.QApplication.clipboard().setText(self.Tab_4_Currently_Displayed)
        
    def action_tab_4_Display_Copy_Displayed_Solution(self):
        QtWidgets.QApplication.clipboard().setText(self.Tab_4_Currently_Displayed_Solution)
 
 # ---------------------------------- HistoryHandler ----------------------------------

    def HistoryHandler(self, AMaS_Object, Tab, Subtab = None):
        

        if Tab == 1:
            if AMaS_Object.tab_1_is != True:
                item = QtWidgets.QListWidgetItem()
                item.setData(100,AMaS_Object)
                item.setText(AF.Digit_Grouping(AMaS_Object.EquationReverse))
                
                self.Tab_1.History.addItem(item)
                AMaS_Object.tab_1_is = True
                AMaS_Object.tab_1_ref = item
            else:
                self.Tab_1.History.takeItem(self.Tab_1.History.row(AMaS_Object.tab_1_ref))
                AMaS_Object.tab_1_ref.setText(AF.Digit_Grouping(AMaS_Object.EquationReverse))
                self.Tab_1.History.addItem(AMaS_Object.tab_1_ref)

            self.Tab_1.History.scrollToBottom()
        
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
            if Subtab == 1:
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
            else:
                NC(1,"Tab {} Subtab {} is unknown".format(str(Tab),str(Subtab)),input="Tab {} Subtab {}".format(str(Tab),str(Subtab)),tb=True)
        
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
        
        if Function == self.Tab_1.calculate:
            if Eval == 0 : Eval = True
            elif Eval == 1 : Eval = False
            else: Eval = None
            if Eval == None:
                Eval=App().optionWindow.cb_F_EvalF.isChecked()
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
                
                
                self.ThreadList.append(Thread) # INVESTIGATE: Check size of memory leak

                self.ThreadList[ID].Return.connect(self.TR)
                self.ThreadList[ID].ReturnError.connect(self.Error_Redirect)
                self.ThreadList[ID].finished.connect(self.ThreadFinishedSlot)
                self.ThreadList[ID].setTerminationEnabled(True)
                self.S_Terminate_Threads.connect(self.ThreadList[ID].terminate)
                self.ThreadList[ID].start()

            elif self.Threading == "POOL":
                if Kind == "NEW":
                    worker = AT.AMaS_Creator(*args,**kwargs)
                elif Kind == "WORK":
                    worker = AT.AMaS_Worker(*args) # pylint: disable=no-value-for-parameter
                worker.signals.result.connect(self.TR)
                worker.signals.error.connect(self.Error_Redirect)
                worker.signals.finished.connect(self.ThreadFinishedSlot)
                self.S_Terminate_Threads.connect(worker.terminate)
                self.threadpool.start(worker) 
        except common_exceptions:
            NC(lvl=1,msg="Could not start thread",exc=sys.exc_info(),func="AMaDiA_Main_Window.TC",win=self.windowTitle(),input="Mode = {} , Kind = {}".format(self.Threading,Kind))
        else:
            self.workingThreadsDisplay(1)
        
    def TC_old(self,Thread): # Thread Creator: All new threads are created here # CLEANUP: TC_old
        ID = -1

        # INVESTIGATE: This causes a crash due to garbagecollector deleting threads before they are properly done cleaning themselves up
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

        # INVESTIGATE: This causes a memory leak but is better than random crashes
        ID = len(self.ThreadList)
        self.ThreadList.append(Thread(ID))


        self.ThreadList[ID].Return.connect(self.TR)
        self.ThreadList[ID].ReturnError.connect(self.Error_Redirect)
        self.ThreadList[ID].start()

    def Error_Redirect(self, AMaS_Object , ReturnFunction , ID=-1):
        #IMPROVE: Improve the Error_Redirect
        AMaS_Object.sendNotifications(self.windowTitle())

    def Set_AMaS_Flags(self,AMaS_Object, f_eval = None):
        if f_eval == None:
            f_eval = App().optionWindow.cb_F_EvalF.isChecked()

        AMaS_Object.f_eval = f_eval

    def ThreadFinishedSlot(self):
        self.workingThreadsDisplay(-1)
    def workingThreadsDisplay(self,pm):
        self.workingThreads += pm
        self.Statusbar.showMessage("Currently working on {} {}".format(self.workingThreads,"equation" if self.workingThreads==1 else "equations"))
    
    def TerminateAllThreads(self):
        self.S_Terminate_Threads.emit()
        self.threadpool.clear()
        if self.threadpool.activeThreadCount() >= 1:
            self.oldThreadpools.append(self.threadpool)
            self.threadpool = QtCore.QThreadPool()
    
 # ---------------------------------- Tab_2_ LaTeX ----------------------------------
    def Tab_2_F_Convert(self, Text=None):
        EvalL = self.Tab_2_Eval_checkBox.checkState()#isChecked()
        if type(Text) != str:
            Text = self.Tab_2_InputField.toPlainText()
        #self.TC(lambda ID: AT.AMaS_Creator(Text, self.Tab_2_F_Display,ID,EvalL=EvalL))
        self.TC("NEW",Text, self.Tab_2_F_Display,EvalL=EvalL)
        
        
    def Tab_2_F_Display(self , AMaS_Object , part = "Normal", HandleHistory = True):
        if HandleHistory:
            self.HistoryHandler(AMaS_Object,2)
        Notification = NC(0,send=False)
        
        if part == "Normal":
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX)
            Notification = self.Tab_2_Viewer.display(AMaS_Object.LaTeX
                                            ,self.TopBar.Font_Size_spinBox.value()
                                            ,self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Equation":
            if AMaS_Object.LaTeX_E == r"\text{Not converted yet}":
                AMaS_Object.ConvertToLaTeX_Equation()
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX_E)
            Notification = self.Tab_2_Viewer.display(AMaS_Object.LaTeX_E
                                            ,self.TopBar.Font_Size_spinBox.value()
                                            ,self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Solution":
            if AMaS_Object.LaTeX_S == r"\text{Not converted yet}":
                AMaS_Object.ConvertToLaTeX_Solution()
            self.Tab_2_LaTeXOutput.setText(AMaS_Object.LaTeX_S)
            Notification = self.Tab_2_Viewer.display(AMaS_Object.LaTeX_S
                                            ,self.TopBar.Font_Size_spinBox.value()
                                            ,self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        #Notification.f("AMaDiA_Main_Window.Tab_2_F_Display")
        #Notification.w(self.windowTitle())
        Notification.send()
        
    def Tab_2_F_Item_doubleClicked(self,item):
        if item.data(100).LaTeX_E == r"\text{Not converted yet}" or item.data(100).LaTeX_E == r"\text{Could not convert}":
            self.Tab_2_F_Display(item.data(100),part="Normal",HandleHistory=False)
        else:
            self.Tab_2_F_Display(item.data(100),part="Equation",HandleHistory=False)
        
 # ---------------------------------- Tab_3_1_ 2D-Plot ----------------------------------
    def Tab_3_1_F_Plot_Button(self):
        #self.TC(lambda ID: AT.AMaS_Creator(self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Plot_init,ID=ID, Iam=AC.Iam_2D_plot))
        self.TC("NEW",self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Plot_init, Iam=AC.Iam_2D_plot)
         
    def Tab_3_1_F_Item_doubleClicked(self,item):
        try:
            cycle = self.Tab_3_1_Display.Canvas.ax._get_lines.prop_cycler
            item.data(100).current_ax.set_color(next(cycle)['color'])
            self.Tab_3_1_Display.Canvas.draw()
            colour = item.data(100).current_ax.get_color()
            brush = QtGui.QBrush(QtGui.QColor(colour))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)
        except common_exceptions :
            NC(lvl=2,msg="Could not cycle colour",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_3_1_F_Item_doubleClicked",win=self.windowTitle())
        
    def Tab_3_1_F_Plot_init(self , AMaS_Object): # MAYBE: get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        if not AMaS_Object.Plot_is_initialized: AMaS_Object.init_2D_plot()
        AMaS_Object.plot_ratio = self.Tab_3_1_Axis_ratio_Checkbox.isChecked()
        AMaS_Object.plot_grid = self.Tab_3_1_Draw_Grid_Checkbox.isChecked()
        AMaS_Object.plot_xmin = self.Tab_3_1_From_Spinbox.value()
        AMaS_Object.plot_xmax = self.Tab_3_1_To_Spinbox.value()
        AMaS_Object.plot_points = self.Tab_3_1_Points_Spinbox.value()
        
        if self.Tab_3_1_Points_comboBox.currentIndex() == 0:
            AMaS_Object.plot_per_unit = False
        elif self.Tab_3_1_Points_comboBox.currentIndex() == 1:
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
        
    def Tab_3_1_F_Plot(self , AMaS_Object): # FEATURE: Add an option for each axis to scale logarithmically 
        # MAYBE: Add an extra option for this in the config tab... and change everything else accordingly
        #if self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked():
        #    self.Tab_3_1_Display.useTeX(True)
        #else:
        #    self.Tab_3_1_Display.useTeX(False)
        
        self.Tab_3_1_Display.useTeX(False)

        self.HistoryHandler(AMaS_Object,3,1)
        
        try:
            if type(AMaS_Object.plot_x_vals) == int or type(AMaS_Object.plot_x_vals) == float:
                p = self.Tab_3_1_Display.Canvas.ax.axvline(x = AMaS_Object.plot_x_vals,color='red')
            else:
                p = self.Tab_3_1_Display.Canvas.ax.plot(AMaS_Object.plot_x_vals , AMaS_Object.plot_y_vals) #  (... , 'r--') for red colour and short lines
            try:
                AMaS_Object.current_ax = p[0]
            except common_exceptions:
                AMaS_Object.current_ax = p
            
            if AMaS_Object.plot_grid:
                self.Tab_3_1_Display.Canvas.ax.grid(True)
            else:
                self.Tab_3_1_Display.Canvas.ax.grid(False)
            if AMaS_Object.plot_ratio:
                self.Tab_3_1_Display.Canvas.ax.set_aspect('equal')
            else:
                self.Tab_3_1_Display.Canvas.ax.set_aspect('auto')
            
            self.Tab_3_1_Display.Canvas.ax.relim()
            self.Tab_3_1_Display.Canvas.ax.autoscale()
            if AMaS_Object.plot_xlim:
                self.Tab_3_1_Display.Canvas.ax.set_xlim(AMaS_Object.plot_xlim_vals)
            if AMaS_Object.plot_ylim:
                self.Tab_3_1_Display.Canvas.ax.set_ylim(AMaS_Object.plot_ylim_vals)
            
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
                self.Tab_3_1_Display.Canvas.draw()
            except RuntimeError:
                ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.Tab_3_1_Display.useTeX(False)
                self.Tab_3_1_Display.Canvas.draw()
        except common_exceptions :
            NC(msg="y_vals = "+str(r.repr(AMaS_Object.plot_y_vals))+str(type(AMaS_Object.plot_y_vals))+"\nYou can copy all elements in the contextmenu if advanced mode is active"
                    ,exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_3_1_F_Plot",win=self.windowTitle(), input=AMaS_Object.Input)
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
            
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
            self.Tab_3_1_Display.Canvas.ax.grid(True)
        else:
            self.Tab_3_1_Display.Canvas.ax.grid(False)
        if self.Tab_3_1_Axis_ratio_Checkbox.isChecked():
            self.Tab_3_1_Display.Canvas.ax.set_aspect('equal')
        else:
            self.Tab_3_1_Display.Canvas.ax.set_aspect('auto')
        
        self.Tab_3_1_Display.Canvas.ax.relim()
        self.Tab_3_1_Display.Canvas.ax.autoscale()
        if self.Tab_3_1_XLim_Check.isChecked():
            self.Tab_3_1_Display.Canvas.ax.set_xlim(xlims)
        if self.Tab_3_1_YLim_Check.isChecked():
            self.Tab_3_1_Display.Canvas.ax.set_ylim(ylims)
        
        try:
            self.Tab_3_1_Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_1_Display.useTeX(False)
            self.Tab_3_1_Display.Canvas.draw()
        
    def Tab_3_1_F_Clear(self):
        self.Tab_3_1_Display.useTeX(False)
        self.Tab_3_1_Display.Canvas.ax.clear()
        try:
            self.Tab_3_1_Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_3_1_Display.useTeX(False)
            self.Tab_3_1_Display.Canvas.ax.clear()
            self.Tab_3_1_Display.Canvas.draw()
        brush = self.palette().text()
        for i in range(self.Tab_3_1_History.count()):
            self.Tab_3_1_History.item(i).setForeground(brush)
            self.Tab_3_1_History.item(i).data(100).current_ax = None
            


    def Tab_3_1_F_Sympy_Plot_Button(self): # CLEANUP: DELETE SymPy Plotter
        #self.TC(lambda ID: AT.AMaS_Creator(self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Sympy_Plot,ID))
        self.TC("NEW",self.Tab_3_1_Formula_Field.text() , self.Tab_3_1_F_Sympy_Plot)
        
    def Tab_3_1_F_Sympy_Plot(self , AMaS_Object): # CLEANUP: DELETE SymPy Plotter
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
        except common_exceptions: # MAYBE: plot_implicit uses other syntax for limits. Maybe make this work
            ExceptionOutput(sys.exc_info())
            try:
                sympy.plot_implicit(temp)
            except common_exceptions:
                ExceptionOutput(sys.exc_info())
                try:
                    sympy.plot_implicit(parse_expr(AMaS_Object.string))
                except common_exceptions:
                    NC(exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_3_1_F_Sympy_Plot",win=self.windowTitle())
 
 # ---------------------------------- Tab_3_2_ 3D-Plot (Tab_3_2_3DWidget) ----------------------------------
    # FEATURE: 3D-Plot
 
 # ---------------------------------- Tab_3_3_ Complex-Plot (Tab_3_3_ComplexWidget) ----------------------------------
    # FEATURE: Complex-Plot
    def Tab_3_3_F_Plot_Button(self):
        self.TC("NEW", self.Tab_3_3_ComplexWidget.InputField.text(), self.Tab_3_3_F_Plot_init, Iam=AC.Iam_complex_plot)
         
    def Tab_3_3_F_Plot_init(self, AMaS_Object):
        #if not AMaS_Object.Plot_is_initialized_complex: AMaS_Object.init_complex_plot()
        AMaS_Object.init_complex_plot()
        AMaS_Object = self.Tab_3_3_ComplexWidget.applySettings(AMaS_Object)
        
        self.TC("WORK", AMaS_Object, lambda: AC.AMaS.Plot_Complex_Calc_Values(AMaS_Object), self.Tab_3_3_F_Plot)
        
    def Tab_3_3_F_Plot(self , AMaS_Object):
        #self.HistoryHandler(AMaS_Object,3,1)
        
        try:
            self.Tab_3_3_ComplexWidget.plot(AMaS_Object)
        except common_exceptions :
            NC(msg="Could not plot", exc=sys.exc_info(), func="AMaDiA_Main_Window.Tab_3_3_F_Plot", win=self.windowTitle(), input=AMaS_Object.Input)
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
            
 # ---------------------------------- Tab_3_4_ ND-Plot ----------------------------------
    # FEATURE: ND-Plot
 
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
        try:
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
                    NC(msg="Could not load the matrix list for this equation",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_4_F_Load_Matrix_List",
                            win=self.windowTitle(),input=self.Tab_4_Active_Equation.Input)
        except common_exceptions:
            NC(msg="Could not load the matrix list",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_4_F_Load_Matrix_List",win=self.windowTitle())

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
                item = QtCore.Qt.QTableWidgetItem()
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
            if Name == "" or " " in Name: #IMPROVE: Better checks for Matrix Names!!!
                NameInvalid=True
            
            if NameInvalid:
                NC(1,"Matrix Name Invalid",func="AMaDiA_Main_Window.Tab_4_F_Save_Matrix",win=self.windowTitle(),input=Name)
                return False
            
            # Read the Input and save it in a nested List
            Matrix = []
            MError = ""
            for i in range(self.Tab_4_1_Matrix_Input.rowCount()):
                Matrix.append([])
                for j in range(self.Tab_4_1_Matrix_Input.columnCount()):
                    try:
                        if self.Tab_4_1_Matrix_Input.item(i,j).text() != None and self.Tab_4_1_Matrix_Input.item(i,j).text().strip() != "":
                            Matrix[i].append(AF.AstusParse(self.Tab_4_1_Matrix_Input.item(i,j).text(),False))
                        else:
                            Matrix[i].append("0")
                    except common_exceptions:
                        MError += "Could not add item to Matrix at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Matrix[i].append("0")
            if MError != "":
                NC(2,MError,func="AMaDiA_Main_Window.Tab_4_F_Save_Matrix",win=self.windowTitle(),input=str(Matrix))
            # Convert list into Matrix and save it in the Equation
            if len(Matrix) == 1 and len(Matrix[0]) == 1:
                Matrix = parse_expr(Matrix[0][0])
            else:
                Matrix = sympy.Matrix(Matrix) # https://docs.sympy.org/latest/modules/matrices/matrices.html
            self.Tab_4_Active_Equation.AddVariable(Name,Matrix)
            
            # Prepare ListWidgetItem
            item = QtWidgets.QListWidgetItem()
            h, w = AF.shape2(Matrix)
            Text = Name + " = {}".format(str(Matrix)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
            item.setText(Text)
            item.setData(100,Name)
            item.setData(101,Matrix)
            SearchFor = Name+" "
            
            #Remove Duplicates
            # VALIDATE: Ensure that this works correctly in all cases!
            # FEATURE: Save the first duplicate in a temporary List item!
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
            NC(1,"Could not save matrix!",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_4_F_Save_Matrix",win=self.windowTitle())
    
    def Tab_4_F_Text_to_Equations(self): #TODO: Do this more properly. This MEthod is just a quick tool that I need right now
        #MAYBE: this could be implemented as a right-click action to the matrix list, too, but it also needs to get its own widget to be more obvious for the user.
        text:str = self.Tab_4_DirectInput.text()
        lines = text.splitlines()
        variables = [i.split("=") for i in lines]
        #
        h,w = 1,1
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
        #
        self.Tab_4_1_Matrix_Input.setItem(0,0,QtWidgets.QTableWidgetItem("="))
        for name, value in variables:
            self.Tab_4_1_Name_Input.setText(name.strip())
            self.Tab_4_1_Matrix_Input.item(0,0).setText(value.strip())
            self.Tab_4_F_Save_Matrix()
    
    def Tab_4_F_Update_Equation(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = not App().optionWindow.cb_F_EvalF.isChecked()
        else:
            Eval = App().optionWindow.cb_F_EvalF.isChecked()
        Text = self.Tab_4_FormulaInput.text()
        AMaS_Object = self.Tab_4_Active_Equation
        self.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        #self.TC(lambda ID: AT.AMaS_Worker(AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.Tab_4_F_Display , ID))
        self.TC("WORK",AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.Tab_4_F_Display)

    def Tab_4_F_Display(self, AMaS_Object): # TODO: Display the Equation in addition to the solution
        self.Tab_4_Currently_Displayed = AMaS_Object.Equation
        self.Tab_4_Currently_Displayed_Solution = AMaS_Object.Solution
        Notification = self.Tab_4_Display.display(AMaS_Object.LaTeX_ER
                                        ,self.TopBar.Font_Size_spinBox.value()
                                        ,self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        Notification.f("AMaDiA_Main_Window.Tab_4_F_Display")
        Notification.w(self.windowTitle())
        Notification.send()
        
    def Tab_4_F_Display_Matrix(self,Name,Matrix):
        #Text = sympy.latex(Matrix)
        #Text += "$"
        #Text1 = "$\\displaystyle"+Text
        #Text2 = "$"+Text
        ##Text2 = Text2.replace("\\left","")
        ##Text2 = Text2.replace("\\right","")
        ##Text2 = Text2.replace("\\begin","")
        ##Text2 = Text2.replace("\\end","")
        #Text = Name + " = "
        #Text1,Text2 = Text+Text1 , Text+Text2
        Text = r"\text{" + Name + "} = " + sympy.latex(Matrix)
        self.Tab_4_Currently_Displayed = Text + str(Matrix)
        self.Tab_4_Currently_Displayed_Solution = str(Matrix)
        Notification = self.Tab_4_Display.display(Text
                                        ,self.TopBar.Font_Size_spinBox.value()
                                        ,self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        Notification.f("AMaDiA_Main_Window.Tab_4_F_Display_Matrix")
        Notification.w(self.windowTitle())
        Notification.send()
 
 # ---------------------------------- Tab_5_ ??? ----------------------------------

 # ---------------------------------- Tab_6_ ??? ----------------------------------

# ---------------------------------- Main ----------------------------------
if __name__ == "__main__":
    latex_installed, dvipng_installed = find_executable('latex'), find_executable('dvipng')
    if latex_installed and dvipng_installed: print("latex and dvipng are installed --> Using pretty LaTeX Display")
    else:
        if latex_installed and not dvipng_installed: print("latex is installed but dvipng was not detected")
        elif not latex_installed and dvipng_installed: print("dvipng is installed but latex was not detected")
        else: print("latex and dvipng were not detected")
        print("  --> Using standard mpl LaTeX Display (Install both to use the pretty version)")
        print("  --> Selecting MathJax Display as standard LaTeX display method")
    print("AMaDiA Startup")
    app = AMaDiA_Main_App([])
    window = AMaDiA_Main_Window(app)
    print(datetime.datetime.now().strftime('%H:%M:%S:'),"AMaDiA Started\n")
    if app.AGeLibPathOK:
        lastVersion = ""
        try:
            with open(os.path.join(app.ConfigFolderPath,"Version"),'r',encoding="utf-8") as text_file:
                lastVersion = text_file.read()
        except:
            pass
        if lastVersion != Version:
            window.LastOpenState()
            window.positionReset()
            window.Tab_1.InputField.setFocus()
            window.Show_AMaDiA_Text_File("Patchlog.txt")
            #TODO: If the file did not exist before but creating it works without problems AMaDiA was probably installed for the first time and not updated. In this case the behaviour should be different.
            #       It would also be cool if the message would include what the previous installed version was
            #       And if the file could not be read and can not be created there should be no message concerning updates.
            #           AGeApp should be informing the user that the AGeLib User directory can not be created/accessed but the exception from reading/writing the version file could also be printed to the console (but only if both don't work)
            NC(3,"AMaDiA has been updated! You are now on version: "+Version,DplStr="Update complete!")
            try:
                with open(os.path.join(app.ConfigFolderPath,"Version"),'w',encoding="utf-8") as text_file:
                    text_file.write(Version)
            except:
                pass
        else:
            window.LastOpenState()
            window.positionReset()
            window.Tab_1.InputField.setFocus()
            window.activateWindow()
    else:
        window.LastOpenState()
        window.positionReset()
        window.Tab_1.InputField.setFocus()
        window.activateWindow()
    sys.exit(app.exec())

