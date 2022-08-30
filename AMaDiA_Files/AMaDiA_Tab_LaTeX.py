import sys
sys.path.append('..')
from AGeLib import *

import typing

import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
import time

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_ReplacementTables as ART

if typing.TYPE_CHECKING:
    from AMaDiA import App, AMaDiA_Main_Window

class Tab_LaTeX(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.AMaDiA: AMaDiA_Main_Window = parent
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setObjectName("Tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self)
        self.gridLayout_3.setContentsMargins(4, 4, 4, 4)
        self.gridLayout_3.setSpacing(3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.LowerSplitter = QtWidgets.QSplitter(self)
        self.LowerSplitter.setOrientation(QtCore.Qt.Vertical)
        self.LowerSplitter.setObjectName("LowerSplitter")
        self.UpperSplitter = QtWidgets.QSplitter(self.LowerSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.UpperSplitter.sizePolicy().hasHeightForWidth())
        self.UpperSplitter.setSizePolicy(sizePolicy)
        self.UpperSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.UpperSplitter.setObjectName("UpperSplitter")
        self.History = AW.HistoryWidget(self.UpperSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.History.sizePolicy().hasHeightForWidth())
        self.History.setSizePolicy(sizePolicy)
        self.History.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.History.setObjectName("History")
        self.layoutWidget = QtWidgets.QWidget(self.UpperSplitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_13.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_13.setSpacing(0)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.LaTeXOutput = QtWidgets.QLineEdit(self.layoutWidget)
        self.LaTeXOutput.setObjectName("LaTeXOutput")
        self.gridLayout_13.addWidget(self.LaTeXOutput, 1, 0, 1, 1)
        self.LaTeXCopyButton = QtWidgets.QPushButton(self.layoutWidget)
        self.LaTeXCopyButton.setObjectName("LaTeXCopyButton")
        self.gridLayout_13.addWidget(self.LaTeXCopyButton, 1, 1, 1, 1)
        self.Viewer = AGeGW.MplWidget_LaTeX(self.layoutWidget)
        self.Viewer.setObjectName("Viewer")
        self.gridLayout_13.addWidget(self.Viewer, 0, 0, 1, 2)
        self.InputField = AW.AMaDiA_TextEdit(self.LowerSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InputField.sizePolicy().hasHeightForWidth())
        self.InputField.setSizePolicy(sizePolicy)
        self.InputField.setObjectName("InputField")
        self.gridLayout_3.addWidget(self.LowerSplitter, 0, 0, 1, 3)
        self.ConvertButton = QtWidgets.QPushButton(self)
        self.ConvertButton.setObjectName("ConvertButton")
        self.gridLayout_3.addWidget(self.ConvertButton, 1, 2, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(780, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 1)
        self.Eval_checkBox = QtWidgets.QCheckBox(self)
        self.Eval_checkBox.setChecked(True)
        self.Eval_checkBox.setTristate(True)
        self.Eval_checkBox.setObjectName("Eval_checkBox")
        self.gridLayout_3.addWidget(self.Eval_checkBox, 1, 1, 1, 1)
        
        self.UpperSplitter.setSizes([163,699])
        self.LowerSplitter.setSizes([391,70])
        
        try:
            self.Eval_checkBox.setCheckState(1)
        except:
            self.Eval_checkBox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        
        self.History.itemDoubleClicked.connect(self.handleItemDoubleClicked)
        self.LaTeXCopyButton.clicked.connect(lambda: self.Viewer.action_Copy_LaTeX())
        self.ConvertButton.clicked.connect(lambda: self.convert())
        self.InputField.returnCtrlPressed.connect(lambda: self.convert())
    
    def convert(self, Text=None):
        EvalL = self.Eval_checkBox.checkState()#isChecked()
        if type(Text) != str:
            Text = self.InputField.toPlainText()
        #self.TC(lambda ID: AT.AMaS_Creator(Text, self.displayLaTeX,ID,EvalL=EvalL))
        self.AMaDiA.TC("NEW",Text, self.displayLaTeX,EvalL=EvalL)
    
    def displayLaTeX(self , AMaS_Object , part = "Normal", HandleHistory = True):
        if HandleHistory:
            self.AMaDiA.HistoryHandler(AMaS_Object,2)
        Notification = NC(0,send=False)
        
        if part == "Normal":
            self.LaTeXOutput.setText(AMaS_Object.LaTeX)
            Notification = self.Viewer.display(AMaS_Object.LaTeX
                                            ,self.AMaDiA.TopBar.Font_Size_spinBox.value()
                                            ,self.AMaDiA.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Equation":
            if AMaS_Object.LaTeX_E == r"\text{Not converted yet}":
                AMaS_Object.ConvertToLaTeX_Equation()
            self.LaTeXOutput.setText(AMaS_Object.LaTeX_E)
            Notification = self.Viewer.display(AMaS_Object.LaTeX_E
                                            ,self.AMaDiA.TopBar.Font_Size_spinBox.value()
                                            ,self.AMaDiA.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        elif part == "Solution":
            if AMaS_Object.LaTeX_S == r"\text{Not converted yet}":
                AMaS_Object.ConvertToLaTeX_Solution()
            self.LaTeXOutput.setText(AMaS_Object.LaTeX_S)
            Notification = self.Viewer.display(AMaS_Object.LaTeX_S
                                            ,self.AMaDiA.TopBar.Font_Size_spinBox.value()
                                            ,self.AMaDiA.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        #Notification.f("AMaDiA_Main_Window.displayLaTeX")
        #Notification.w(self.windowTitle())
        Notification.send()
    
    def handleItemDoubleClicked(self,item):
        if item.data(100).LaTeX_E == r"\text{Not converted yet}" or item.data(100).LaTeX_E == r"\text{Could not convert}":
            self.displayLaTeX(item.data(100),part="Normal",HandleHistory=False)
        else:
            self.displayLaTeX(item.data(100),part="Equation",HandleHistory=False)
