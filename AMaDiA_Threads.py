# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 12:51:32 2019

@author: Robin
"""

import sys
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.Qt import QApplication, QClipboard
import socket
import datetime
import platform
import errno
import os
import sympy
from sympy.parsing.sympy_parser import parse_expr
import importlib
import types

import numpy as np
import scipy.integrate

import AMaDiA
import AMaDiA_Widgets as AW
import AMaDiA_Functions as AF
import AMaDiA_Classes as AC
import AMaDiA_ReplacementTables as ART


def ReloadModules():
    importlib.reload(AW)
    importlib.reload(AF)
    importlib.reload(AC)
    importlib.reload(ART)
#------------------------------------------------------------------------------

class AMaS_Creator(QtCore.QThread):
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType)
    def __init__(self,Text,Return_Function):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.Text = Text
        self.Return_Function = Return_Function
        
    def run(self):
        self.AMaS_Object = AC.AMaS(self.Text)
        self.Return.emit(self.AMaS_Object , self.Return_Function)
        self.exiting = True
        #self.exit()
        
#------------------------------------------------------------------------------

class AMaS_Calc_Thread(QtCore.QThread): #TODO: Outdated. Use AMaS_Thread instead
    Calculator_Return = QtCore.pyqtSignal(AC.AMaS)
#    LaTeX_Return = QtCore.pyqtSignal(AC.AMaS)
    def __init__(self, AMaS_Object, Function): # TODOMode: Not happy with the EvalF thing...
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.AMaS_Object = AMaS_Object
        self.Function = Function
        
    def run(self):
        self.Function(self)
        
    def Evaluate(self):
        self.AMaS_Object.Evaluate()
        self.Calculator_Return.emit(self.AMaS_Object)
        self.exiting = True
        #self.exit()
        
    def Evaluate_NOT(self): # TODOMode: Not happy with the EvalF thing...
        self.AMaS_Object.Evaluate(False)
        self.Calculator_Return.emit(self.AMaS_Object)
        self.exiting = True
        #self.exit()
            
            
""" Usage
self.New_AMaS_Thread = AMaS_Calc_Thread()
self.New_AMaS_Thread.Calculator_Return.connect(self.Tab_1_F_Calculate_Display)
self.New_AMaS_Thread.start()
"""

#------------------------------------------------------------------------------

class AMaS_Thread(QtCore.QThread):
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType)
    def __init__(self , AMaS_Object , AMaS_Function , Return_Function):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.AMaS_Object = AMaS_Object
        self.AMaS_Function = AMaS_Function
        self.Return_Function = Return_Function
        
    def run(self):
        if self.AMaS_Function(self.AMaS_Object): #TODO: Give error message if not successful
            self.Return.emit(self.AMaS_Object , self.Return_Function)
        self.exiting = True
        #self.exit()

''' Usage:
self.New_AMaS_Thread = AMaS_Calc_Thread(AMaS_Object , AC.Method , self.Return_Function)
self.New_AMaS_Thread.Calculator_Return.connect(self.RT)
self.New_AMaS_Thread.start()


also use

def Perform(f):
    f()

Perform(lambda: Action1())
Perform(lambda: Action2(p))
Perform(lambda: Action3(p, r))

'''

#------------------------------------------------------------------------------

