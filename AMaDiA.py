# This Python file uses the following encoding: utf-8
Version = "0.1.0"
Author = "Robin \'Astus\' Albers"

import sys
from PyQt5 import QtWidgets,QtCore,QtGui # Maybe Needs a change of the interpreter of Qt Creator to work there
import socket
import datetime
import platform
import errno
import os
import sympy
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


WindowTitle = "AMaDiA v"
WindowTitle+= Version
WindowTitle+= " by "
WindowTitle+= Author


class MainWindow(QtWidgets.QMainWindow, Ui_AMaDiA_Main_Window):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        sympy.init_printing() # doctest: +SKIP
        self.setupUi(self)
        self.Tab_2_LaTeX_Viewer.canvas.ax.clear()
        self.Tab_2_LaTeX_Viewer.canvas.ax.axis('off')
        
        # add to UI File
        # import AMaDiA_Widgets
        # Overwrite Widgets in the UI File
        # self.Tab_2_LaTeX_Viewer = AMaDiA_Widgets.MplWidget(self.centralWidget)
        
        self.ConnectSignals()
        #self.SetColour() # TODO:Remove
        self.ColourMain()

    def ConnectSignals(self):
        self.Tab_2_LaTeX_ConvertButton.clicked.connect(self.Tab_2_F_Convert)
        self.Tab_1_Calculator_InputField.returnPressed.connect(self.Tab_1_F_Calculate)
        self.Menubar_Main_Options_action_Reload_Modules.triggered.connect(self.ReloadModules)
        self.Font_Size_spinBox.valueChanged.connect(self.ChangeFontSize)
        self.Tab_3_2D_Plot_Button_Plot.clicked.connect(self.Tab_3_F_Plot)
    
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
        
    #Options
    def ReloadModules(self):
        importlib.reload(AW)
        importlib.reload(AF)
        importlib.reload(AC)
        importlib.reload(ART)
        importlib.reload(AMaDiA_Colour)
        
        self.ColourMain()
    
    # Tab_1_
    def Tab_1_F_Calculate(self):
        Mode = "P"
        if self.Menubar_Main_Options_action_LaTeX.isChecked():
            Mode = "L"
        Input = AC.AMaS(self.Tab_1_Calculator_InputField.text(),Mode)
        # Input.EvaluateLaTeX() # TODO: left( and right) brakes it...
        Input.Evaluate(self.Menubar_Main_Options_action_Eval_Functions.isChecked())
        
        item = QtWidgets.QListWidgetItem()
        item.setData(0,Input)
        item.setText(Input.EvaluationEquation)
        self.Tab_1_Calculator_History.addItem(item) # TODO: Add the History functionality
        
    
    # Tab_2_LaTeX
    def Tab_2_F_Convert(self):
        Input = AC.AMaS(self.Tab_2_LaTeX_InputField.toPlainText())
        self.Tab_2_LaTeX_LaTeXOutput.setText(Input.LaTeX)
        item = QtWidgets.QListWidgetItem()
        item.setData(0,Input)
        item.setText(Input.Text)
        self.Tab_2_LaTeX_History.addItem(item) # TODO: Add the History functionality
        self.Tab_2_F_Display(Input)
        
    def Tab_2_F_Display(self,Item):
        # Display stuff... The way it is displayed will hopefully change as this project goes on:
        
        Text = Item.LaTeX
        
        Text += "$"
        Text = "$" + Text
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.clear() # makes Space for the new text
        
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.set_title(Text,
                      x=0.0, y=0.5, 
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size_spinBox.value()+10,
                      color = (1.0,1.0,1.0))
        
        self.Tab_2_LaTeX_Viewer.canvas.ax.axis('off')
        
        # TODO: Does not work since the text is not considered part of the graph
        # Make the Viewer big enought for the figure to not cut off the Text
        # A ScrollArea is used to fit any size
        # To set size use: setMinimumSize , setMinimumHeight , setMinimumWidth
#        self.Tab_2_LaTeX_Viewer.canvas.fig.tight_layout()
        self.Tab_2_LaTeX_Viewer.setMinimumWidth(12*len(Item.LaTeX)+100) # Below does not work! Instead using this
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
        
    def Tab_3_F_Plot(self):
        #TODO: Make the Plot thing user controlled with the input things...
        
        # Important: Use a new thread to calculate everything and probably even create the plot
        #               Then copy the output from the thread to use it here
        #               This is important to not crash the program if the user makes rediculously big Plots
        
        self.Tab_3_2D_Plot_Display.canvas.ax.plot([1,2,3,4], 'r--')
        self.Tab_3_2D_Plot_Display.canvas.draw()
        



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
