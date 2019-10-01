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
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int , bool)
    def __init__(self,Text,Return_Function,ID=-1,Eval=True):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.Text = Text
        self.Eval = Eval
        self.Return_Function = Return_Function
        self.ID = ID
        
    def run(self):
        self.AMaS_Object = AC.AMaS(self.Text)
        if self.AMaS_Object.Exists:
            self.Return.emit(self.AMaS_Object , self.Return_Function , self.ID , self.Eval)
        self.exiting = True
        self.exit()
        self.quit()
        self.deleteLater()
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Creator( __Text__ , self.__Return_to_Method__ ,ID))
"""
#------------------------------------------------------------------------------

class AMaS_Thread(QtCore.QThread):
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int)
    def __init__(self , AMaS_Object , AMaS_Function , Return_Function,ID=-1):
        QtCore.QThread.__init__(self)
        self.ID = ID
        self.exiting = False
        self.AMaS_Object = AMaS_Object
        self.AMaS_Function = AMaS_Function
        self.Return_Function = Return_Function
        
    def run(self):
        if self.AMaS_Function(): #TODO: Give error message if not successful
            self.Return.emit(self.AMaS_Object , self.Return_Function , self.ID)
        self.exiting = True
        self.exit()
        self.quit()
        self.deleteLater()
        
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Thread(AMaS_Object,lambda:AC.AMaS.__METHOD__(AMaS_Object, __ARGUMENTS__ ),self.__Return_to_Method__ ,ID))
"""

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

