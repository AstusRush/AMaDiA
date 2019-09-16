# This Python file uses the following encoding: utf-8
Version = "0.3.3"
Author = "Robin \'Astus\' Albers"

import sys
from PyQt5 import QtWidgets,QtCore,QtGui # Maybe Needs a change of the interpreter of Qt Creator to work there
from PyQt5.Qt import QApplication, QClipboard
import socket
import datetime
import platform
import errno
import os
import sympy
from sympy.parsing.sympy_parser import parse_expr
import importlib

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


WindowTitle = "AMaDiA v"
WindowTitle+= Version
WindowTitle+= " by "
WindowTitle+= Author


class MainWindow(QtWidgets.QMainWindow, Ui_AMaDiA_Main_Window):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        sympy.init_printing() # doctest: +SKIP
        self.setupUi(self)
        self.tabWidget.setCurrentIndex(0)
        
        self.TextColour = (215/255, 213/255, 201/255)
        
        # Setup the graphic displays:
        self.Tab_2_LaTeX_Viewer.canvas.ax.clear()
        self.Tab_2_LaTeX_Viewer.canvas.ax.axis('off')
        self.Tab_3_2D_Plot_Display.canvas.ax.spines['bottom'].set_color(self.TextColour)
        self.Tab_3_2D_Plot_Display.canvas.ax.spines['left'].set_color(self.TextColour)
        self.Tab_3_2D_Plot_Display.canvas.ax.xaxis.label.set_color(self.TextColour)
        self.Tab_3_2D_Plot_Display.canvas.ax.yaxis.label.set_color(self.TextColour)
        self.Tab_3_2D_Plot_Display.canvas.ax.tick_params(axis='x', colors=self.TextColour)
        self.Tab_3_2D_Plot_Display.canvas.ax.tick_params(axis='y', colors=self.TextColour)
        
        
        self.Tab_1_Calculator_History.installEventFilter(self)
        self.Tab_2_LaTeX_History.installEventFilter(self)
        self.Tab_3_2D_Plot_History.installEventFilter(self)
        
        
        # add to UI File
        # import AMaDiA_Widgets
        # Overwrite Widgets in the UI File
        # self.Tab_2_LaTeX_Viewer = AMaDiA_Widgets.MplWidget(self.centralWidget)
        
        self.ConnectSignals()
        #self.SetColour() # TODO:Remove
        self.ColourMain()
        
# ---------------------------------- Init and Maintanance ----------------------------------

    def ConnectSignals(self):
        self.Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)
        self.Menubar_Main_Options_action_Reload_Modules.triggered.connect(self.ReloadModules)
        
        self.Tab_1_Calculator_InputField.returnPressed.connect(self.Tab_1_F_Calculate_Field_Input)
        
        self.Tab_2_LaTeX_ConvertButton.clicked.connect(self.Tab_2_F_Convert)
        
        self.Tab_3_2D_Plot_Button_Plot.clicked.connect(self.Tab_3_F_Plot_Button)
        self.Tab_3_2D_Plot_Formula_Field.returnPressed.connect(self.Tab_3_F_Plot_Button)
        self.Tab_3_2D_Plot_Button_Clear.clicked.connect(self.Tab_3_F_Clear)
    
    def ColourMain(self):
        palette = AMaDiA_Colour.palette()
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.setFont(font)
        self.setPalette(palette)
        
        
    def SetColour(self): #TODO: Remove
        InputFieldColour = "background-color: rgb(67, 71, 78);color: rgb(215, 213, 201);"
        self.Font_Size_spinBox.setStyleSheet(InputFieldColour)
        self.centralwidget.setStyleSheet(InputFieldColour)
        self.Tab_1_Calculator_InputField.setStyleSheet(InputFieldColour)
        self.Tab_1_Calculator.setStyleSheet(InputFieldColour)
        
    def ChangeFontSize(self):
        Size = self.Font_Size_spinBox.value()
        newFont = QtGui.QFont()
        newFont.setFamily("Arial")
        newFont.setPointSize(Size)
        self.setFont(newFont)
        self.centralwidget.setFont(newFont)
        self.Menubar_Main.setFont(newFont)
        self.Menubar_Main_Options.setFont(newFont)
        
        # TODO:Remove junk-code
        
        #InputFieldColour = "background-color: rgb(67, 71, 78);color: rgb(215, 213, 201);"
        #InputFieldColour = "background-color: rgb(67, 71, 78);color: rgb(215, 213, 201); font: %ipx;"%Size
        #self.setStyleSheet(InputFieldColour)
        
        #self.setFont(newFont)
        #self.centralwidget.setFont(newFont)
        
        #self.Tab_1_Calculator_History.setFont(newFont)
        #self.Tab_1_Calculator_InputField.setFont(newFont)
        #self.Tab_2_LaTeX_History.setFont(newFont)
        #self.Tab_2_LaTeX_InputField.setFont(newFont)
        #self.Tab_2_LaTeX_LaTeXOutput.setFont(newFont)
        
# ---------------------------------- Options ----------------------------------
    def ReloadModules(self):
        importlib.reload(AW)
        importlib.reload(AF)
        importlib.reload(AC)
        importlib.reload(ART)
        importlib.reload(AT)
        importlib.reload(AMaDiA_Colour)
        
        self.ColourMain()
        
        
        
# ---------------------------------- History Context Menu ----------------------------------
    
        
    def HistoryContextMenu(self, QPos): #TODO:Remove
        self.listMenu= QtWidgets.QMenu()
        menu_item = self.listMenu.addAction("Remove Item")
        self.connect(menu_item, QtCore.SIGNAL("triggered()"), self.menuItemClicked) 
        parentPosition = self.Tab_1_Calculator_History.mapToGlobal(QtCore.QPoint(0, 0))        
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show() 


    def eventFilter(self, source, event): # TODO: Add more
        if (event.type() == QtCore.QEvent.ContextMenu and
            (source is self.Tab_1_Calculator_History or source is self.Tab_2_LaTeX_History or source is self.Tab_3_2D_Plot_History )and
            source.itemAt(event.pos())):
            menu = QtWidgets.QMenu()
            action = menu.addAction('Copy Text')
            action.triggered.connect(lambda: self.action_H_Copy_Text(source,event))
            action = menu.addAction('Copy LaTeX')
            action.triggered.connect(lambda: self.action_H_Copy_LaTeX(source,event))
            if source.itemAt(event.pos()).data(100).Evaluation != "Not evaluated yet.":
                action = menu.addAction('Copy Solution')
                action.triggered.connect(lambda: self.action_H_Copy_Solution(source,event))
            menu.addSeparator()
            # TODO: Only "Calculate" if the equation has not been evaluated yet or if in Dev Mode? Maybe? Maybe not?
            # It currently is handy to have it always because of the EvalF thing...
            action = menu.addAction('Calculate')
            action.triggered.connect(lambda: self.action_H_Calculate(source,event))
            action = menu.addAction('Display LaTeX')
            action.triggered.connect(lambda: self.action_H_Display_LaTeX(source,event))
            menu.addSeparator()
            action = menu.addAction('Delete')
            action.triggered.connect(lambda: self.action_H_Delete(source,event))
            if menu.exec_(event.globalPos()):
                pass #TODO: This if-case seems rather pointless but without something in the in it's condition it doesn't work...
                #item = source.itemAt(event.pos())
                #QApplication.clipboard().setText(item.data(100).Text)
            return True
        return super(MainWindow, self).eventFilter(source, event)
    
    def action_H_Copy_Text(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).Text)
        
    def action_H_Copy_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).LaTeX)
        
    def action_H_Copy_Solution(self,source,event):
        item = source.itemAt(event.pos())
        QApplication.clipboard().setText(item.data(100).Evaluation)
        
    def action_H_Calculate(self,source,event):
        item = source.itemAt(event.pos())
        self.tabWidget.setCurrentIndex(0)
        self.Tab_1_F_Calculate(item.data(100))
        
    def action_H_Display_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        self.tabWidget.setCurrentIndex(1)
        self.Tab_2_F_Display(item.data(100))
        
    def action_H_Delete(self,source,event):
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
           source.takeItem(source.row(item))
        
        
# ---------------------------------- Thread Redirector ----------------------------------

    def TR(self,AMaS_Object,Function): 
        self.Function = Function
        self.Function(AMaS_Object)

# ---------------------------------- Tab_1_Calculator_ ----------------------------------
    def Tab_1_F_Calculate_Field_Input(self):
        Mode = "P" # TODO:Mode Not happy with the Mode thing...
        if self.Menubar_Main_Options_action_LaTeX.isChecked():
            Mode = "L" # TODO:Mode Not happy with the Mode thing...
        
        # Input.EvaluateLaTeX() # TODO: left( and right) brakes it...
        self.New_AMaST_Creator = AT.AMaS_Creator(self.Tab_1_Calculator_InputField.text(), self.Tab_1_F_Calculate, Mode) # TODO:Mode Not happy with the Mode thing...
        self.New_AMaST_Creator.Return.connect(self.TR)
        self.New_AMaST_Creator.start()
        
    def Tab_1_F_Calculate(self,AMaS_Object):
        if self.Menubar_Main_Options_action_Eval_Functions.isChecked(): # TODOMode: Not happy with the EvalF thing...
            self.New_AMaST_Evaluater = AT.AMaS_Calc_Thread(AMaS_Object , AT.AMaS_Calc_Thread.Evaluate) # TODOMode: Not happy with the EvalF thing... #TODO: Outdated. Use AMaS_Thread instead
        else:
            self.New_AMaST_Evaluater = AT.AMaS_Calc_Thread(AMaS_Object , AT.AMaS_Calc_Thread.Evaluate_NOT) # TODOMode: Not happy with the EvalF thing... #TODO: Outdated. Use AMaS_Thread instead
        self.New_AMaST_Evaluater.Calculator_Return.connect(self.Tab_1_F_Calculate_Display)
        self.New_AMaST_Evaluater.start()
        
    def Tab_1_F_Calculate_Display(self,AMaS_Object):
        
        item = QtWidgets.QListWidgetItem()
        item.setData(100,AMaS_Object)
        item.setText(AMaS_Object.EvaluationEquation)
        
        self.Tab_1_Calculator_History.addItem(item)
        
    
# ---------------------------------- Tab_2_LaTeX_ ----------------------------------
    def Tab_2_F_Convert(self):
        self.New_AMaST_Creator = AT.AMaS_Creator(self.Tab_2_LaTeX_InputField.toPlainText(), self.Tab_2_F_Display)
        self.New_AMaST_Creator.Return.connect(self.TR)
        self.New_AMaST_Creator.start()
        
    def Tab_2_F_Display(self,Input):
        # Display stuff... The way it is displayed will hopefully change as this project goes on:
        
        
        self.Tab_2_LaTeX_LaTeXOutput.setText(Input.LaTeX)
        item = QtWidgets.QListWidgetItem()
        item.setData(100,Input)
        item.setText(Input.Text)
        self.Tab_2_LaTeX_History.addItem(item)
        
        Text = Input.LaTeX
        
        Text += "$"
        Text = "$" + Text
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.clear() # makes Space for the new text
        
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.set_title(Text,
                      x=0.0, y=0.5, 
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size_spinBox.value()+10,
                      color = self.TextColour)
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.axis('off')
        
        # TODO: Does not work since the text is not considered part of the graph
        # Make the Viewer big enought for the figure to not cut off the Text
        # A ScrollArea is used to fit any size
        # To set size use: setMinimumSize , setMinimumHeight , setMinimumWidth
#        self.Tab_2_LaTeX_Viewer.canvas.fig.tight_layout()
        self.Tab_2_LaTeX_Viewer.setMinimumWidth(12*len(Input.LaTeX)+100) # Below does not work! Instead using this
        size = self.Tab_2_LaTeX_Viewer.canvas.fig.get_size_inches()*self.Tab_2_LaTeX_Viewer.canvas.fig.dpi # Gets the size in pixels
        size += np.sum(self.Tab_2_LaTeX_Viewer.canvas.fig.get_constrained_layout_pads())
#        self.Tab_2_LaTeX_Viewer.setMinimumSize(size[0],size[1]) # Seems to do nothing
#        self.Tab_2_LaTeX_Viewer.setMaximumSize(size[0]+10,size[1]+10) # Seems to do nothing
        
        # I think the problem is, that the figure uses all space it can get and thus resizeing does not work correctly
        # makeing the min bigger makes the figure bigger and makeing the max smaller makes the figure smaller (or if too small crashes everything)
        # making the min smaller does not change the figures size (or it dcreses it a bit with each drawing untill it hits the min...)
        
        # Does not work! Instead using
#        self.Tab_2_LaTeX_Viewer.setMinimumWidth(12*len(LaTeX)+100)
        
        # Show the "graph"
        self.Tab_2_LaTeX_Viewer.canvas.draw()
        
        
# ---------------------------------- Tab_3_2D_Plot_ ----------------------------------
    def Tab_3_F_Plot_Button(self):
        Mode = "P"
        if self.Menubar_Main_Options_action_LaTeX.isChecked():
            Mode = "L"
            
        self.New_AMaST_Creator = AT.AMaS_Creator(self.Tab_3_2D_Plot_Formula_Field.text() , self.Tab_3_F_Plot_init , Mode) # TODO:Mode Not happy with the Mode thing...
        self.New_AMaST_Creator.Return.connect(self.TR)
        self.New_AMaST_Creator.start()
        
        
    def Tab_3_F_Plot_init(self , AMaS_object): #TODO: Maybe get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        AMaS_object.plot_ratio = self.Tab_3_2D_Plot_Axis_ratio_Checkbox.isChecked()
        AMaS_object.plot_grid = self.Tab_3_2D_Plot_Draw_Grid_Checkbox.isChecked()
        AMaS_object.plot_xmin = self.Tab_3_2D_Plot_From_Spinbox.value()
        AMaS_object.plot_xmax = self.Tab_3_2D_Plot_To_Spinbox.value()
        AMaS_object.plot_steps = self.Tab_3_2D_Plot_Steps_Spinbox.value()
        AMaS_object.plot_per_unit = self.Tab_3_2D_Plot_Steps_Checkbox.isChecked()
        self.New_AMaST_Plotter = AT.AMaS_Thread(AMaS_object , AC.AMaS.Plot_Calc_Values , self.Tab_3_F_Plot) # TODO:Mode Not happy with the Mode thing...
        self.New_AMaST_Plotter.Return.connect(self.TR)
        self.New_AMaST_Plotter.start()
        
        
    def Tab_3_F_Plot(self , AMaS_object):
        
        # TODO: Colour the text and the Graph in the same colour
        item = QtWidgets.QListWidgetItem()
        item.setData(100,AMaS_object)
        item.setText(AMaS_object.Text)
        self.Tab_3_2D_Plot_History.addItem(item)
        
        self.Tab_3_2D_Plot_Display.canvas.ax.plot(AMaS_object.plot_x_vals , AMaS_object.plot_y_vals) #  (... , 'r--') für rot
        
        if AMaS_object.plot_grid:
            self.Tab_3_2D_Plot_Display.canvas.ax.grid(True)
        else:
            self.Tab_3_2D_Plot_Display.canvas.ax.grid(False)
        if AMaS_object.plot_ratio:
            self.Tab_3_2D_Plot_Display.canvas.ax.set_aspect('equal')
        else:
            self.Tab_3_2D_Plot_Display.canvas.ax.set_aspect('auto')
        
        #self.Tab_3_2D_Plot_Display.canvas.ax = sympy.plot(Input,x_min,x_max) #TODO: Maybe make this work or even better: Implement sympy.plot instead of pyplot
        self.Tab_3_2D_Plot_Display.canvas.draw()
        
        
    def Tab_3_F_Clear(self):
        # TODO: Uncoulor all coloured text in the history
        self.Tab_3_2D_Plot_Display.canvas.ax.clear()
        self.Tab_3_2D_Plot_Display.canvas.draw()
        
        
# ---------------------------------- Tab_4_??? ----------------------------------


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
