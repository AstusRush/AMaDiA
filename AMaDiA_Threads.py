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
import time

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
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int , int)
    def __init__(self, Parent, Text, Return_Function, ID, Eval=None, EvalL=True, Iam = AC.Iam_Normal):
        QtCore.QThread.__init__(self, Parent)
        self.exiting = False
        self.Text = Text
        self.Iam = Iam
        self.EvalL = EvalL
        if Eval == None : self.Eval = -1
        elif Eval : self.Eval = 0
        else: self.Eval = 1
        self.Return_Function = Return_Function
        self.ID = ID
        
    def run(self):
        self.AMaS_Object = AC.AMaS(self.Text, self.Iam, EvalL=self.EvalL)
        if self.AMaS_Object.Exists:
            self.Return.emit(self.AMaS_Object , self.Return_Function , self.ID , self.Eval)
        self.exiting = True
        self.exit()
        self.quit()
        self.deleteLater()
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Creator(self, __Text__ , self.__Return_to_Method__ ,ID))
"""
#------------------------------------------------------------------------------

class AMaS_Thread(QtCore.QThread):
    ReturnError = QtCore.pyqtSignal(AC.AMaS , str , types.MethodType , int) #TODO: Connect this in AMaDiA. Maybe set the string as the tooltip?
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int)
    def __init__(self, Parent, AMaS_Object, AMaS_Function, Return_Function, ID):
        QtCore.QThread.__init__(self, Parent)
        self.ID = ID
        self.exiting = False
        self.AMaS_Object = AMaS_Object
        self.AMaS_Function = AMaS_Function
        self.Return_Function = Return_Function
        
    def run(self):
        Success = self.AMaS_Function()
        if Success == True:
            self.Return.emit(self.AMaS_Object , self.Return_Function , self.ID)
        else:
            self.ReturnError.emit(self.AMaS_Object , Success , self.Return_Function , self.ID)
        self.exiting = True
        self.exit()
        self.quit()
        self.deleteLater()
        
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Thread(self, AMaS_Object,lambda:AC.AMaS.__METHOD__(AMaS_Object, __ARGUMENTS__ ),self.__Return_to_Method__ ,ID))
"""

''' Usage:
self.New_AMaS_Thread = AMaS_Calc_Thread(self, AMaS_Object , AC.Method , self.Return_Function)
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



