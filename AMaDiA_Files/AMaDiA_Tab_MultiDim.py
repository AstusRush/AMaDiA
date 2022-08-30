import sys, os
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


import reprlib
formatArray = reprlib.Repr()
formatArray.maxlist = 20       # max elements displayed for lists
formatArray.maxarray = 20       # max elements displayed for arrays
formatArray.maxother = 500       # max elements displayed for other including np.ndarray
formatArray.maxstring = 40    # max characters displayed for strings

class Tab_MultiDim(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.AMaDiA: AMaDiA_Main_Window = parent
        super().__init__(parent)
        self.setObjectName("Tab_4")
        self.gridLayout_7 = QtWidgets.QGridLayout(self)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.Splitter_Main = QtWidgets.QSplitter(self)
        self.Splitter_Main.setOrientation(QtCore.Qt.Horizontal)
        self.Splitter_Main.setObjectName("Splitter_Main")
        self.Splitter_Left = QtWidgets.QSplitter(self.Splitter_Main)
        self.Splitter_Left.setOrientation(QtCore.Qt.Vertical)
        self.Splitter_Left.setObjectName("Splitter_Left")
        self.tabWidget = QtWidgets.QTabWidget(self.Splitter_Left)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.tab_1)
        self.gridLayout_9.setContentsMargins(4, 0, 0, 4)
        self.gridLayout_9.setSpacing(3)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.InputTab_Dimension_Input = QtWidgets.QLineEdit(self.tab_1)
        self.InputTab_Dimension_Input.setMaxLength(5)
        self.InputTab_Dimension_Input.setCursorPosition(0)
        self.InputTab_Dimension_Input.setObjectName("1_Dimension_Input")
        self.gridLayout_9.addWidget(self.InputTab_Dimension_Input, 1, 0, 1, 1)
        self.InputTab_Matrix_Input = AW.AMaDiA_TableWidget(self.tab_1)
        self.InputTab_Matrix_Input.setRowCount(3)
        self.InputTab_Matrix_Input.setColumnCount(3)
        self.InputTab_Matrix_Input.setObjectName("1_Matrix_Input")
        self.InputTab_Matrix_Input.horizontalHeader().setDefaultSectionSize(75)
        self.gridLayout_9.addWidget(self.InputTab_Matrix_Input, 0, 0, 1, 4)
        self.InputTab_Save_Matrix_Button = QtWidgets.QPushButton(self.tab_1)
        self.InputTab_Save_Matrix_Button.setObjectName("1_Save_Matrix_Button")
        self.gridLayout_9.addWidget(self.InputTab_Save_Matrix_Button, 1, 3, 1, 1)
        self.InputTab_Configure_Button = QtWidgets.QPushButton(self.tab_1)
        self.InputTab_Configure_Button.setObjectName("1_Configure_Button")
        self.gridLayout_9.addWidget(self.InputTab_Configure_Button, 1, 1, 1, 1)
        self.InputTab_Name_Input = QtWidgets.QLineEdit(self.tab_1)
        self.InputTab_Name_Input.setObjectName("1_Name_Input")
        self.gridLayout_9.addWidget(self.InputTab_Name_Input, 1, 2, 1, 1)
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_4.setContentsMargins(4, 4, 4, 4)
        self.gridLayout_4.setSpacing(3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.EquationTab_New_Equation_Button = QtWidgets.QPushButton(self.tab_2)
        self.EquationTab_New_Equation_Button.setObjectName("2_New_Equation_Button")
        self.gridLayout_4.addWidget(self.EquationTab_New_Equation_Button, 1, 3, 1, 1)
        self.History = AW.HistoryWidget(self.tab_2)
        self.History.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.History.setObjectName("History")
        self.gridLayout_4.addWidget(self.History, 0, 0, 1, 4)
        self.EquationTab_Load_Selected_Button = QtWidgets.QPushButton(self.tab_2)
        self.EquationTab_Load_Selected_Button.setObjectName("2_Load_Selected_Button")
        self.gridLayout_4.addWidget(self.EquationTab_Load_Selected_Button, 1, 2, 1, 1)
        self.EquationTab_New_Equation_Name_Input = QtWidgets.QLineEdit(self.tab_2)
        self.EquationTab_New_Equation_Name_Input.setObjectName("2_New_Equation_Name_Input")
        self.gridLayout_4.addWidget(self.EquationTab_New_Equation_Name_Input, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.Matrix_List = AGeWidgets.ListWidget(self.Splitter_Left)
        self.Matrix_List.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Matrix_List.setObjectName("Matrix_List")
        self.Splitter_Right = QtWidgets.QSplitter(self.Splitter_Main)
        self.Splitter_Right.setOrientation(QtCore.Qt.Vertical)
        self.Splitter_Right.setObjectName("Splitter_Right")
        self.layoutWidget2 = QtWidgets.QWidget(self.Splitter_Right)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.Display_gridLayout = QtWidgets.QGridLayout(self.layoutWidget2)
        self.Display_gridLayout.setContentsMargins(0, 0, 0, 0)
        self.Display_gridLayout.setSpacing(0)
        self.Display_gridLayout.setObjectName("Display_gridLayout")
        self.Display = AGeGW.MplWidget_LaTeX(self.layoutWidget2)
        self.Display.setObjectName("Display")
        self.Display_gridLayout.addWidget(self.Display, 0, 0, 1, 1)
        self.FormulaInput = AW.AMaDiA_LineEdit(self.layoutWidget2)
        self.FormulaInput.setObjectName("FormulaInput")
        self.Display_gridLayout.addWidget(self.FormulaInput, 1, 0, 1, 1)
        self.DirectInput = AW.AMaDiA_TextEdit(self.Splitter_Right)
        self.DirectInput.setObjectName("DirectInput")
        self.gridLayout_7.addWidget(self.Splitter_Main, 0, 0, 1, 1)
        
        self.tabWidget.setCurrentIndex(0)
        
        self.Active_Equation:"AC.AMaS" = None
        
       # Signals and Slots
        self.FormulaInput.returnPressed.connect(lambda: self.F_Update_Equation())
        self.InputTab_Dimension_Input.returnPressed.connect(lambda: self.F_Config_Matrix_Dim())
        self.InputTab_Configure_Button.clicked.connect(lambda: self.F_Config_Matrix_Dim())
        self.InputTab_Name_Input.returnPressed.connect(lambda: self.F_Save_Matrix())
        self.InputTab_Save_Matrix_Button.clicked.connect(lambda: self.F_Save_Matrix())
        self.EquationTab_New_Equation_Button.clicked.connect(lambda: self.F_New_Equation())
        self.EquationTab_New_Equation_Name_Input.returnPressed.connect(lambda: self.F_New_Equation())
        self.EquationTab_Load_Selected_Button.clicked.connect(lambda: self.F_Load_Selected_Equation())
        
        #TODO: This is temporary:
        self.DirectInput.returnCtrlPressed.connect(lambda: self.F_Text_to_Equations())
        
        
        
        self.Display.AdditionalActions['Copy Equation'] = self.action_tab_4_Display_Copy_Displayed
        self.Display.AdditionalActions['Copy Solution'] = self.action_tab_4_Display_Copy_Displayed_Solution
        
        self.installEventFilter(self)
    
    def init_Equation(self):
        self.EquationTab_New_Equation_Name_Input.setText("Equation 1")
        self.F_New_Equation()
        self.EquationTab_New_Equation_Name_Input.clear()
        self.InputTab_Dimension_Input.setText(" 3x3 ")
        self.Currently_Displayed = ""
        self.Currently_Displayed_Solution = ""
    
    def eventFilter(self, source, event):
        # TODO: Add more mouse button functionality! See https://doc.qt.io/qt-5/qt.html#MouseButton-enum and https://doc.qt.io/qt-5/qmouseevent.html
        #print(event.type())
        #if event.type() == 6: # QtCore.QEvent.KeyPress
        if event.type() == 82: # QtCore.QEvent.ContextMenu
            if (source is self.Matrix_List) and source.itemAt(event.pos()):
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
        return super().eventFilter(source, event) # let the normal eventFilter handle the event
    
    def action_tab_4_M_Load_into_Editor(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.F_Load_Matrix(Name,Matrix)
    
    def action_tab_4_M_Display(self,source,event):
        item = source.itemAt(event.pos())
        Name = item.data(100)
        Matrix = item.data(101)
        self.F_Display_Matrix(Name,Matrix)
    
    def action_tab_4_M_Copy_string(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(str(item.data(101)))
    
    def action_tab_4_M_Delete(self,source,event):
        # FEATURE: Paperbin for matrices: If only one item was deleted save it in a temporary List item (The same as the duplicate item from the save function)
        #                             or: When items are deleted save them temporarily and add an "undo last deletion" context menu action
        listItems = source.selectedItems()
        if not listItems: return        
        for item in listItems:
            a = source.takeItem(source.row(item))
            del self.Active_Equation.Variables[a.data(100)]
    
    def action_tab_4_Display_Copy_Displayed(self):
        QtWidgets.QApplication.clipboard().setText(self.Currently_Displayed)
    
    def action_tab_4_Display_Copy_Displayed_Solution(self):
        QtWidgets.QApplication.clipboard().setText(self.Currently_Displayed_Solution)
    
    
    def F_New_Equation(self):
        Name = ""+self.EquationTab_New_Equation_Name_Input.text().strip()
        if Name == "":
            Name="Unnamed Equation"
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Creator(Name,self.F_New_Equation_Done,ID=ID,Iam=AC.Iam_Multi_Dim))
        self.AMaDiA.TC("NEW",Name,self.F_New_Equation_Done,Iam=AC.Iam_Multi_Dim)
    def F_New_Equation_Done(self,AMaS_Object:"AC.AMaS"):
        self.AMaDiA.HistoryHandler(AMaS_Object,4)
    
    def F_Load_Selected_Equation(self):
        item = self.History.selectedItems()
        if len(item) == 1:
            item = item[0]
            self.AMaDiA.HistoryHandler(item.data(100),4)
        self.FormulaInput.setText(item.data(100).Input)
        self.F_Display(self.Active_Equation)
    
    def F_Load_Matrix_List(self):
        try:
            self.Matrix_List.clear()
            try:
                for Name, Variable in self.Active_Equation.Variables.items():
                    h, w = AF.shape2(Variable)
                    Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                    item = QtWidgets.QListWidgetItem()
                    item.setText(Text)
                    item.setData(100,Name)
                    item.setData(101,Variable)
                    self.Matrix_List.addItem(item)
            except ValueError:
                ExceptionOutput(sys.exc_info())
                try:
                    Name, Variable = self.Active_Equation.Variables.items()
                    h, w = AF.shape2(Variable)
                    Text = Name + " = {}".format(str(Variable)) if h==1 and w==1 else Name + " : {}x{}".format(h,w)
                    item = QtWidgets.QListWidgetItem()
                    item.setText(Text)
                    item.setData(100,Name)
                    item.setData(101,Variable)
                    self.Matrix_List.addItem(item)
                except common_exceptions:
                    NC(msg="Could not load the matrix list for this equation",exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Load_Matrix_List",
                            win=self.windowTitle(),input=self.Active_Equation.Input)
        except common_exceptions:
            NC(msg="Could not load the matrix list",exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Load_Matrix_List",win=self.windowTitle())
    
    def F_Load_Matrix(self,Name,Matrix):
        h,w = AF.shape2(Matrix)
        self.InputTab_Matrix_Input.setRowCount(h)
        self.InputTab_Matrix_Input.setColumnCount(w)
        self.InputTab_Dimension_Input.setText(" "+str(h)+"x"+str(w))
        self.InputTab_Name_Input.setText(Name)
        
        tolist = getattr(Matrix, "tolist", None)
        if callable(tolist):
            ValueList = Matrix.tolist()
        else:
            ValueList = [[Matrix]]
        for i,a in enumerate(ValueList): # pylint: disable=unused-variable
            for j,b in enumerate(ValueList[i]):
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(b))
                self.InputTab_Matrix_Input.setItem(i,j,item)
    
    def F_Config_Matrix_Dim(self):
        h,w = self.InputTab_Dimension_Input.text().split("x")
        try:
            h = int(h) if int(h) > 0 else 1
            self.InputTab_Matrix_Input.setRowCount(h)
        except common_exceptions:
            pass
        try:
            w = int(w)
            self.InputTab_Matrix_Input.setColumnCount(w)
        except common_exceptions:
            pass
        for i in range(self.InputTab_Matrix_Input.columnCount()):
            self.InputTab_Matrix_Input.setColumnWidth(i,75)
    
    def F_Save_Matrix(self):
        try:
            NameInvalid=False
            Name = AF.AstusParse(self.InputTab_Name_Input.text()).strip()
            if Name == "" or " " in Name: #IMPROVE: Better checks for Matrix Names!!!
                NameInvalid=True
            
            if NameInvalid:
                NC(1,"Matrix Name Invalid",func="AMaDiA_Main_Window.F_Save_Matrix",win=self.windowTitle(),input=Name)
                return False
            
            # Read the Input and save it in a nested List
            Matrix = []
            MError = ""
            for i in range(self.InputTab_Matrix_Input.rowCount()):
                Matrix.append([])
                for j in range(self.InputTab_Matrix_Input.columnCount()):
                    try:
                        if self.InputTab_Matrix_Input.item(i,j).text() != None and self.InputTab_Matrix_Input.item(i,j).text().strip() != "":
                            Matrix[i].append(AF.AstusParse(self.InputTab_Matrix_Input.item(i,j).text(),False))
                        else:
                            Matrix[i].append("0")
                    except common_exceptions:
                        MError += "Could not add item to Matrix at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Matrix[i].append("0")
            if MError != "":
                NC(2,MError,func="AMaDiA_Main_Window.F_Save_Matrix",win=self.windowTitle(),input=str(Matrix))
            # Convert list into Matrix and save it in the Equation
            if len(Matrix) == 1 and len(Matrix[0]) == 1:
                Matrix = parse_expr(Matrix[0][0])
            else:
                Matrix = sympy.Matrix(Matrix) # https://docs.sympy.org/latest/modules/matrices/matrices.html
            self.Active_Equation.AddVariable(Name,Matrix)
            
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
            FoundItems = self.Matrix_List.findItems(SearchFor,QtCore.Qt.MatchStartsWith)
            if len(FoundItems) > 0:
                for i in FoundItems:
                    index = self.Matrix_List.indexFromItem(i)
                    self.Matrix_List.takeItem(index.row())
            
            # Add to the Matrix List
            self.Matrix_List.addItem(item)
            # Display the Matrix
            self.F_Display_Matrix(Name,Matrix)
        except common_exceptions:
            NC(1,"Could not save matrix!",exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Save_Matrix",win=self.windowTitle())
    
    def F_Text_to_Equations(self): #TODO: Do this more properly. This MEthod is just a quick tool that I need right now
        #MAYBE: this could be implemented as a right-click action to the matrix list, too, but it also needs to get its own widget to be more obvious for the user.
        text:str = self.DirectInput.text()
        lines = text.splitlines()
        variables = [i.split("=") for i in lines]
        #
        h,w = 1,1
        try:
            h = int(h) if int(h) > 0 else 1
            self.InputTab_Matrix_Input.setRowCount(h)
        except common_exceptions:
            pass
        try:
            w = int(w)
            self.InputTab_Matrix_Input.setColumnCount(w)
        except common_exceptions:
            pass
        for i in range(self.InputTab_Matrix_Input.columnCount()):
            self.InputTab_Matrix_Input.setColumnWidth(i,75)
        #
        self.InputTab_Matrix_Input.setItem(0,0,QtWidgets.QTableWidgetItem("="))
        for name, value in variables:
            self.InputTab_Name_Input.setText(name.strip())
            self.InputTab_Matrix_Input.item(0,0).setText(value.strip())
            self.F_Save_Matrix()
    
    def F_Update_Equation(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            Eval = not App().optionWindow.cb_F_EvalF.isChecked()
        else:
            Eval = App().optionWindow.cb_F_EvalF.isChecked()
        Text = self.FormulaInput.text()
        AMaS_Object = self.Active_Equation
        self.AMaDiA.Set_AMaS_Flags(AMaS_Object,f_eval = Eval)
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Worker(AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.F_Display , ID))
        self.AMaDiA.TC("WORK",AMaS_Object, lambda:AC.AMaS.UpdateEquation(AMaS_Object ,Text=Text), self.F_Display)
    
    def F_Display(self, AMaS_Object:"AC.AMaS"): # TODO: Display the Equation in addition to the solution
        self.Currently_Displayed = AMaS_Object.Equation
        self.Currently_Displayed_Solution = AMaS_Object.Solution
        Notification:"NC" = self.Display.display(AMaS_Object.LaTeX_ER
                                        ,self.AMaDiA.TopBar.Font_Size_spinBox.value()
                                        ,self.AMaDiA.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        Notification.f("AMaDiA_Main_Window.F_Display")
        Notification.w(self.windowTitle())
        Notification.send()
    
    def F_Display_Matrix(self,Name,Matrix):
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
        self.Currently_Displayed = Text + str(Matrix)
        self.Currently_Displayed_Solution = str(Matrix)
        Notification:"NC" = self.Display.display(Text
                                        ,self.AMaDiA.TopBar.Font_Size_spinBox.value()
                                        ,self.AMaDiA.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                        )
        Notification.f("AMaDiA_Main_Window.F_Display_Matrix")
        Notification.w(self.windowTitle())
        Notification.send()
