# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 12:51:32 2019

@author: Robin
"""

import sys
sys.path.append('..')
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.Qt import QApplication, QClipboard # pylint: disable=no-name-in-module
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

from External_Libraries.python_control_master import control

#import AMaDiA
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files.AMaDiA_Functions import common_exceptions, ExceptionOutput, NotificationEvent, sendNotification
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART


def ReloadModules():
    importlib.reload(AW)
    importlib.reload(AF)
    importlib.reload(AC)
    importlib.reload(ART)
#------------------------------------------------------------------------------
class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running AMaS_Creator.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (AC.AMaS , int , str , types.MethodType , int)
        (self.AMaS_Object , lvl , notifications , self.Return_Function , self.ID)
    
    result
        `tuple` (AC.AMaS , types.MethodType , int , int)
        (self.AMaS_Object , self.Return_Function , self.ID , self.Eval)

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(AC.AMaS , int , str , types.MethodType , int)
    result = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int , int)
#------------------------------------------------------------------------------
class AMaS_Creator(QtCore.QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, Text, Return_Function, Eval=None, EvalL=1, Iam = AC.Iam_Normal):
        super(AMaS_Creator, self).__init__()
        self.exiting = False
        self.Text = Text
        self.Iam = Iam
        self.EvalL = EvalL
        if Eval == None : self.Eval = -1
        elif Eval : self.Eval = 0
        else: self.Eval = 1
        self.Return_Function = Return_Function
        self.ID = -1
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        self.AMaS_Object = AC.AMaS(self.Text, self.Iam, EvalL=self.EvalL)
        if self.AMaS_Object.Exists == True:
            self.signals.result.emit(self.AMaS_Object , self.Return_Function , self.ID , self.Eval)
            lvl, notifications = self.AMaS_Object.Notifications()
            if notifications != "":
                self.signals.error.emit(self.AMaS_Object , lvl , notifications , self.Return_Function , self.ID)
        else:
            self.signals.error.emit(self.AMaS_Object , 1 , str(self.AMaS_Object.Exists) , self.Return_Function , self.ID)
        self.exiting = True
        self.signals.finished.emit()
#------------------------------------------------------------------------------

class AMaS_Worker(QtCore.QRunnable):
    def __init__(self, AMaS_Object, AMaS_Function, Return_Function):
        super(AMaS_Worker, self).__init__()
        self.ID = -1
        self.exiting = False
        self.AMaS_Object = AMaS_Object
        self.AMaS_Function = AMaS_Function
        self.Return_Function = Return_Function
        self.signals = WorkerSignals()
        
    def run(self):
        Success = self.AMaS_Function()
        if Success == True:
            self.signals.result.emit(self.AMaS_Object , self.Return_Function , self.ID, -1)
            lvl, notifications = self.AMaS_Object.Notifications()
            if notifications != "":
                self.signals.error.emit(self.AMaS_Object , lvl , notifications , self.Return_Function , self.ID)
        else:
            self.signals.error.emit(self.AMaS_Object , 1 , str(Success) , self.Return_Function , self.ID)
        self.exiting = True
        self.signals.finished.emit()
        
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Thread(self, AMaS_Object,lambda:AC.AMaS.__METHOD__(AMaS_Object, __ARGUMENTS__ ),self.__Return_to_Method__ ,ID))
"""
#------------------------------------------------------------------------------

class Timer(QtCore.QRunnable):
    def __init__(self, Time):
        super(Timer, self).__init__()
        self.Time = Time
        self.signals = WorkerSignals()
        
    def run(self):
        time.sleep(self.Time)
        self.signals.finished.emit()

#------------------------------------------------------------------------------ Threads ------------------------------------------------------------------------------
class AMaS_Creator_Thread(QtCore.QThread):
    ReturnError = QtCore.pyqtSignal(AC.AMaS , int , str , types.MethodType , int)
    Return = QtCore.pyqtSignal(AC.AMaS , types.MethodType , int , int)
    def __init__(self, Parent, Text, Return_Function, ID, Eval=None, EvalL=1, Iam = AC.Iam_Normal):
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
        if self.AMaS_Object.Exists == True:
            self.Return.emit(self.AMaS_Object , self.Return_Function , self.ID , self.Eval)
            lvl, notifications = self.AMaS_Object.Notifications()
            if notifications != "":
                self.ReturnError.emit(self.AMaS_Object , lvl , notifications , self.Return_Function , self.ID)
        else:
            self.ReturnError.emit(self.AMaS_Object , 1 , str(self.AMaS_Object.Exists) , self.Return_Function , self.ID)
        self.exiting = True
        self.exit()
        #self.quit()
        #self.deleteLater()
        
"""Usage: only replace __***__
self.TC(lambda ID: AT.AMaS_Creator(self, __Text__ , self.__Return_to_Method__ ,ID))
"""
#------------------------------------------------------------------------------

class AMaS_Thread(QtCore.QThread):
    ReturnError = QtCore.pyqtSignal(AC.AMaS , int , str , types.MethodType , int)
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
            lvl, notifications = self.AMaS_Object.Notifications()
            if notifications != "":
                self.ReturnError.emit(self.AMaS_Object , lvl , notifications , self.Return_Function , self.ID)
        else:
            self.ReturnError.emit(self.AMaS_Object , 1 , str(Success) , self.Return_Function , self.ID)
        self.exiting = True
        self.exit()
        #self.quit()
        #self.deleteLater()
        
        
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



