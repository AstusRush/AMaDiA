from AGeLib import *
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART
from AMaDiA_Files import AMaDiA_Threads as AT
from AMaDiA_Files.AMaDiA_Options_UI import Ui_AMaDiA_Options

# import standard modules
import datetime
import platform
from distutils.spawn import find_executable
import sys
import time
import os
import pathlib
import re
import getpass

try:
    import typing
except:
    pass

# import Maths modules
import matplotlib
import sympy
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
import numpy as np

try:
    from External_Libraries.keyboard_master import keyboard
except common_exceptions :
    ExceptionOutput(sys.exc_info())
    Keyboard_Remap_Works = False
else:
    Keyboard_Remap_Works = True

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
                self.cb_O_Remapper_local.setEnabled(True)
                keyboard.clear_all_hotkeys()
                self.cb_O_Remapper_local.setChecked(True)
        except ImportError:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_options_window.ToggleGlobalRemapper")
            self.cb_O_Remapper_global.blockSignals(True)
            self.cb_O_Remapper_global.setChecked(False)
            self.cb_O_Remapper_global.blockSignals(False)
            self.cb_O_Remapper_local.setEnabled(True)
            self.cb_O_Remapper_local.setChecked(True)
        except common_exceptions:
            try:
                NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_options_window.ToggleGlobalRemapper",input="Failed to map {} to {}".format(str(i),str(Key)))
            except common_exceptions :
                NC(exc=sys.exc_info(),win=self.windowTitle(),func="AMaDiA_options_window.ToggleGlobalRemapper",input="Could not determine failed remap operation.")
