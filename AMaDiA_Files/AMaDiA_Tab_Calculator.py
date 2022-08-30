import sys
sys.path.append('..')
from AGeLib import *

import typing

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #CLEANUP: Delete this line?
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('Qt5Agg')
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
import numpy as np
import scipy
import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
from sympy.parsing.sympy_parser import parse_expr
import time

import warnings

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_ReplacementTables as ART

if typing.TYPE_CHECKING:
    from AMaDiA import App, AMaDiA_Main_Window

class Tab_Calculator(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.AMaDiA: AMaDiA_Main_Window = parent
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setObjectName("Tab_1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self)
        self.gridLayout_2.setContentsMargins(4, 4, 4, 4)
        self.gridLayout_2.setSpacing(3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.History = AW.HistoryWidget(self)
        self.History.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.History.setObjectName("Tab_1_History")
        self.gridLayout_2.addWidget(self.History, 0, 0, 1, 1)
        self.InputField = AW.AMaDiA_LineEdit(self)
        self.InputField.setObjectName("Tab_1_InputField")
        self.gridLayout_2.addWidget(self.InputField, 1, 0, 1, 1)
        
        self.History.itemDoubleClicked.connect(self.handleItemDoubleClicked)
        self.InputField.returnPressed.connect(lambda: self.calculateFieldInput())
    
    def calculateFieldInput(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = not App().optionWindow.cb_F_EvalF.isChecked()
        else:
            Eval = App().optionWindow.cb_F_EvalF.isChecked()
        TheInput = self.InputField.text()
        if TheInput == "RUNTEST":
            self.AMaDiA.RUNTEST()
        else:
            if self.History.count() >= 1:
                TheInput = re.sub(r"(?<!\w)ans(?!\w)","({})".format(self.History.item(self.History.count()-1).data(100).Solution),TheInput)
                TheInput = re.sub(r"(?<!\w)ans1(?!\w)","({})".format(self.History.item(self.History.count()-1).data(100).Solution),TheInput)
                if self.History.count() >= 2:
                    TheInput = re.sub(r"(?<!\w)ans2(?!\w)","({})".format(self.History.item(self.History.count()-2).data(100).Solution),TheInput)
                    if self.History.count() >= 3:
                        TheInput = re.sub(r"(?<!\w)ans3(?!\w)","({})".format(self.History.item(self.History.count()-3).data(100).Solution),TheInput)
                    else:
                        TheInput = re.sub(r"(?<!\w)ans3(?!\w)","(1)",TheInput)
                else:
                    TheInput = re.sub(r"(?<!\w)ans2(?!\w)","(1)",TheInput)
                    TheInput = re.sub(r"(?<!\w)ans3(?!\w)","(0)",TheInput)
            else:
                TheInput = re.sub(r"(?<!\w)ans(?!\w)","(1)",TheInput)
                TheInput = re.sub(r"(?<!\w)ans1(?!\w)","(1)",TheInput)
                TheInput = re.sub(r"(?<!\w)ans2(?!\w)","(0)",TheInput)
                TheInput = re.sub(r"(?<!\w)ans3(?!\w)","(0)",TheInput)
            
            if TheInput == "len()":
                TheInput = str(len(self.AMaDiA.ThreadList))
            #self.TC(lambda ID: AT.AMaS_Creator(TheInput,self.calculate,ID=ID,Eval=Eval))
            self.AMaDiA.TC("NEW",TheInput,self.calculate,Eval=Eval)
    
    def calculate(self,AMaS_Object,Eval = None):
        if Eval == None:
            Eval = App().optionWindow.cb_F_EvalF.isChecked()
        self.AMaDiA.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        #self.TC(lambda ID: AT.AMaS_Worker(AMaS_Object, lambda:AC.AMaS.Evaluate(AMaS_Object), self.calculateDisplay , ID))
        self.AMaDiA.TC("WORK", AMaS_Object, lambda:AC.AMaS.Evaluate(AMaS_Object), self.calculateDisplay)
    
    def calculateDisplay(self,AMaS_Object:"AC.AMaS"):
        self.AMaDiA.HistoryHandler(AMaS_Object,1)
    
    def handleItemDoubleClicked(self,item):
        self.InputField.selectAll()
        self.InputField.insertPlainText(item.data(100).Input)
