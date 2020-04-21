# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:55:31 2019

@author: Robin
"""

# if__name__ == "__main__":
#     pass

from AGeLib.exc import *

import sys
sys.path.append('..')
from PyQt5 import QtWidgets,QtCore,QtGui # Maybe Needs a change of the interpreter of Qt Creator to work there
import socket
import datetime
import platform
import errno
import os
import sympy
import re
import warnings

from PyQt5 import QtCore

from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import scipy


from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_ReplacementTables as ART


import importlib
def ReloadModules():
    importlib.reload(AF)
    importlib.reload(ART)



Iam_Lost = "Lost"
Iam_Normal = "Normal"
Iam_2D_plot = "2D-plot"
Iam_ODE = "ODE"
Iam_Multi_Dim = "Multi-Dim"
IamList = [Iam_Lost, Iam_Normal, Iam_2D_plot, Iam_ODE, Iam_Multi_Dim]


#parse_expr\((.*),evaluate=False,local_dict=self.Variables,global_dict=self.global_dict()\)
#

class AMaS: # Astus' Mathematical Structure
    warningMutex = QtCore.QMutex()
 # ---------------------------------- INIT ----------------------------------
    def __init__(self, string, Iam, EvalL = 1):
        self.Input = string
        self.TimeStamp = AF.cTimeSStr()
        self.TimeStampFull = AF.cTimeFullStr()
        self.mutex = QtCore.QMutex()
        self.NotificationMutex = QtCore.QMutex()
        self.Name = "No Name Given"
        self.init_bools()
        self.init_Flags()
        self.f_eval_LaTeX = EvalL
        self.Iam = Iam
        self.Variables = {}
        self.VariablesUnev = {}
        with QtCore.QMutexLocker(self.NotificationMutex):
            self.NotificationList = []
        
        if string == "":
            N = NC(1,"ERROR: No input",func="AMaS.__init__",DplStr="Please give an input",send=False)
            self.Notify(N)
            self.Exists = False
        else:
            try:
                self.INIT_WhatAmI(string)
            except common_exceptions :
                self.Notify(NC(1,"Could not create AMaS object",func="AMaS.__init__",exc=sys.exc_info(),send=False))
                self.Exists = False
            else:
                self.Exists = True
    
    def init_bools(self):
        self.multiline = False
        self.Plot_is_initialized = False
        self.plot_data_exists = False
        self.disable_units = False
        self.init_history()

    def INIT_WhatAmI(self,string):
        if self.Iam == Iam_Normal:
            self.INIT_Normal(string)
        elif self.Iam == Iam_2D_plot:
            self.INIT_2D_plot(string)
        elif self.Iam == Iam_ODE:
            self.INIT_ODE(string)
        elif self.Iam == Iam_Multi_Dim:
            self.INIT_Multi_Dim(string)
        else:
            print("AMaS Object: I am Lost! I don't know who I am! "+self.Iam+" is not known to me! I'm gonna pretend I am normal!")
            self.Iam = Iam_Lost
            self.INIT_Normal(string)


    def INIT_Normal(self,string):
        string = string.splitlines()
        if type(string) == list :
            if len(string) > 1 :
                self.stringList = string
                self.string = string[0]
                self.multiline = True
            else:
                self.string = string[0]
        else:
            self.string = string
        self.init_Critical()

    def INIT_2D_plot(self,string):
        self.string = string
        self.init_Critical()
        self.init_2D_plot()

    def INIT_ODE(self,string):
        #FEATURE: INIT_ODE
        # https://docs.sympy.org/latest/modules/solvers/ode.html
        print("Iam_ODE IS NOT IMPLEMENTED YET!")
        self.INIT_Normal(string)

    def INIT_Multi_Dim(self,string):
        self.Name = string
        self.string = "0"
        self.init_Critical()

    def init_Critical(self):
        self.Separator = " = "
        self.Text = AF.AstusParseInverse(self.string)
        self.Solution = "Not evaluated yet"
        self.EquationReverse = "? = " + self.Text
        self.Equation = self.Text + " = ?"
        self.cstr = AF.AstusParse(self.string) # the converted string that is interpretable
        if self.multiline:
            self.cstrList = []
            for i in self.stringList:
                self.cstrList.append(AF.AstusParse(i,False))
        self.LaTeX    = r"\text{Not converted yet}" # LaTeX of the input
        self.LaTeX_S  = r"\text{Not converted yet}" # LaTeX of the Solution
        self.LaTeX_E  = r"\text{Not converted yet}" # LaTeX of the Equation
        self.LaTeX_ER = r"\text{Not converted yet}" # LaTeX of the Equation in Reverse order
        self.Am_I_Plottable()
        self.ConvertToLaTeX()
        

    def Am_I_Plottable(self):
        # IMPROVE: Improve the criteria for "plottable"
        if "x" in self.cstr and not "=" in self.cstr:
            self.plottable = True
        else:
            self.plottable = False
                
                
    def init_history(self):
        self.tab_1_is = False
        self.tab_1_ref = None
        self.tab_2_is = False
        self.tab_2_ref = None
        self.Tab_3_1_is = False
        self.Tab_3_1_ref = None
        self.Tab_4_is = False
        self.Tab_4_ref = None
                
    def init_2D_plot(self):
        self.Plot_is_initialized = True
        self.current_ax = None
        self.plot_ratio = False
        self.plot_grid = True
        self.plot_xmin = -5
        self.plot_xmax = 5
        self.plot_xlim = False
        self.plot_xlim_vals = (-5, 5)
        self.plot_ylim = False
        self.plot_ylim_vals = (-5, 5)
        self.plot_points = 1000
        self.plot_per_unit = False
        self.plot_x_vals = np.arange(10)
        self.plot_y_vals = np.zeros_like(self.plot_x_vals)
        

    
 # ---------------------------------- Update, Rename, etc ----------------------------------
    def Update(self,string=None):
        if string != None:
            self.string = string
        self.init_Critical()
        return True

    def Rename(self,Name):
        self.Name = Name
        return True

 # ---------------------------------- Flags ----------------------------------
    def init_Flags(self):
        self.f_eval = True         # converted to floating-point approximations (decimal numbers)
        self.f_eval_LaTeX = 1      # If 0 prohibits all evaluation when converting to LaTeX
                                   # If 2 Allows most Solution
        
        
        
        # REMINDER : FOLLOWING ARE NOT SET BUT READ DIRECTLY:
        self.f_simplify = None     # Simplifies
        self.f_powsimp = None      # Simplifies/Collects exponents
        self.f_expand = None       # Solve all * and **
        self.f_factor = None       # takes a polynomial and factors it into irreducible factors (Inverse of expand)
        self.f_collect = None      # collects common powers of a term in an expression
        self.f_collect_arg = ""
        self.f_cancel = None       # will take any rational function and put it into the standard canonical form p/q
        self.f_apart = None        # performs a partial fraction decomposition on a rational function
        self.f_expand_trig = None  # To expand trigonometric functions, that is, apply the sum or double angle identities
        
        
        
        # REMINDER : FOLLOWING NEED IMPLEMENTATION:
        
        
        # Simplify: https://docs.sympy.org/latest/tutorial/simplification.html
        self.f_rewrite = None      # A common way to deal with special functions is to rewrite them in terms of one another
        self.f_rewrite_arg = ""       # For example: tan(x).rewrite(sin)

        #self.f_ = False

    def ExecuteFlags(self,expr):
        if type(expr) == dict:
            temp_dict = {}
            for k,v in expr.items():
                try:
                    if type(k) in [int,str,float,bool]:
                        temp_dict[k] = self.ExecuteFlags(v)
                    else:
                        temp_dict[self.ExecuteFlags(k)] = self.ExecuteFlags(v)
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
                    temp_dict[k] = v
            expr = temp_dict
        else:
            try:
                if self.f_eval:
                    expr = expr.evalf()
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_simplify == True or self.f_simplify == None and QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked():
                    expr = sympy.simplify(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_powsimp == True or self.f_powsimp == None and QtWidgets.QApplication.instance().optionWindow.cb_F_powsimp.isChecked():
                    if type(expr) == sympy.Equality:
                        expr = sympy.Eq(sympy.powsimp(expr.lhs),sympy.powsimp(expr.rhs))
                    else:
                        expr = sympy.powsimp(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_expand == True or self.f_expand == None and QtWidgets.QApplication.instance().optionWindow.cb_F_expand.isChecked():
                    expr = sympy.expand(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_factor == True or self.f_factor == None and QtWidgets.QApplication.instance().optionWindow.cb_F_factor.isChecked():
                    expr = sympy.factor(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_collect == True:
                    expr = sympy.collect(expr,AF.parse(self.f_collect_arg))
                elif self.f_collect == None and QtWidgets.QApplication.instance().optionWindow.cb_F_collect.isChecked():
                    expr = sympy.collect(expr,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_collect.text()))
            except common_exceptions :
                self.Notify(NC(2,"Could not collect term",exc=sys.exc_info(),func="AMaS.ExecuteFlags",send=False))
            try:
                if self.f_cancel == True or self.f_cancel == None and QtWidgets.QApplication.instance().optionWindow.cb_F_cancel.isChecked():
                    expr = sympy.cancel(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_apart == True or self.f_apart == None and QtWidgets.QApplication.instance().optionWindow.cb_F_apart.isChecked():
                    expr = sympy.apart(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            try:
                if self.f_expand_trig == True or self.f_expand_trig == None and QtWidgets.QApplication.instance().optionWindow.cb_F_expand_trig.isChecked():
                    expr = sympy.expand_trig(expr)
            except common_exceptions :
                ExceptionOutput(sys.exc_info())
            # TODO : Add the others
        return expr
        """
        try:
            if self.f_? == True or self.f_? == None and QtWidgets.QApplication.instance().optionWindow.cb_F_?.isChecked():
                expr = sympy.?(expr)
        except common_exceptions :
            ExceptionOutput(sys.exc_info())
        """ # pylint: disable=unreachable

    def global_dict(self):
        if QtWidgets.QApplication.instance().optionWindow.cb_U_EnableUnits.isChecked() and not self.disable_units:
            global_dict = {}
            exec('from sympy import *', global_dict)
            exec('from sympy.physics.units import *', global_dict)
            return global_dict
        else:
            return None
 # ---------------------------------- Notifications ----------------------------------

    def sendNotifications(self,win=None):
        """
        Sends all Notifications and clears them   \n
        Optionally sets the window of all notifications to win
        """
        with QtCore.QMutexLocker(self.NotificationMutex):
            if win != None:
                for i in self.NotificationList:
                    i.w(win)
            for i in self.NotificationList:
                i.send()
                QtWidgets.QApplication.instance().processEvents()
            self.NotificationList = []

    def Notify(self,Notification):
        """Used to add Notifications"""
        with QtCore.QMutexLocker(self.NotificationMutex):
            In = ""
            if Notification.i()!=self.Input:
                In += "Specific Input:\n"
                try:
                    In += Notification.i()
                except:
                    In += "ERROR: ATTRIBUTE DOES NOT EXIST"
                In += "\n\n"
            In += "The state of the object while the notification was triggered (not final state):\nself.Input:\n"
            try:
                In += self.Input
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.cstr:\n"
            try:
                In += self.cstr
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.TimeStampFull (time of creation of the AMaS object):\n"
            try:
                In += self.TimeStampFull
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.Name (Usually: No Name Given):\n"
            try:
                In += self.Name
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.Iam:\n"
            try:
                In += self.Iam
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.LaTeX:\n"
            try:
                In += self.LaTeX
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            In += "\n\nself.Solution:\n"
            try:
                In += self.Solution
            except:
                In += "ERROR: ATTRIBUTE DOES NOT EXIST"
            Notification.i(In)
            #Notification.i("    self.Input: "+self.Input+"\nSpecific Input: "+In)
            self.NotificationList.append(Notification)

    def NotifyFromNumpy(self,text,flag=""):
        """Used to add Notifications from Numpy and scipy"""
        print(text,flag)
        text += flag
        self.Notify(NC(3,text,send=False))

    def NotifyWarning(self, message, category, filename, lineno, file=None, line=None):
        TheWarning = warnings.formatwarning(message, category, filename, lineno, line)
        print("Warning in AMaS for",self.Input,"\n",TheWarning)
        self.Notify(NC(2,TheWarning,err=message,tb="filename: {}\nlineno: {}".format(str(filename),str(lineno)),send=False))

 # ---------------------------------- LaTeX Converter ----------------------------------
    # MAYBE: set a time limit for conversions that can be disabled in the options (if this is even possible)
    
    def ConvertToLaTeX(self):
        """
        Converts the Input into LaTeX.
        """
        if self.multiline:
            self.LaTeX = ""
            n = len(self.cstrList)
            for i,e in enumerate(self.cstrList):
                n -= 1
                LineText = ""
                try:
                    #if e.strip() == "":
                    #    #LineText += "-"
                    #    if n > 0:
                    #        LineText += "\n"
                    #        #self.LaTeX_L += "$\displaystyle"
                    #        #self.LaTeX_N += "$"
                    #    self.LaTeX += LineText
                    #    continue
                    #if "=" in e:
                    #    parts = self.cstrList[i].split("=")
                    #    conv = ""
                    #    for j in parts:
                    #        if len(j)>0:
                    #            conv += AF.LaTeX(j,local_dict=self.VariablesUnev,evalf=self.f_eval_LaTeX)
                    #        conv += " = "
                    #    LineText += conv[:-3]
                    #else:
                    LineText = AF.LaTeX(e,local_dict=self.VariablesUnev,evalf=self.f_eval_LaTeX)
                except common_exceptions: #as inst:
                    ExceptionOutput(sys.exc_info())
                    # LineText += AF.AstusParseInverse(e) #MAYBE: Unicodesymbols seem to brake LaTeX Output... Maybe there is a way to fix it?
                    LineText += e
                    LineText = r" \text{ " + LineText.replace("\t",r" \qquad ") + " } "
                    if n > 0:
                        LineText += "\n"
                    self.LaTeX += LineText
                else:
                    #LineText += "$"
                    if "#" in e:
                        LineText += r" \qquad \text{ " + e.split("#",1)[1] + " } "
                    if n > 0:
                        LineText += "\n"
                    #self.LaTeX_L += r"$\displaystyle "
                    #self.LaTeX_N += "$"
                    #self.LaTeX_L += LineText
                    self.LaTeX += r" \qquad "*e.count("\t") + LineText
        else:
            try:
                #if "=" in self.cstr:
                #    parts = self.cstr.split("=")
                #    self.LaTeX = ""
                #    for i in parts:
                #        if len(i)>0:
                #            self.LaTeX += AF.LaTeX(i,local_dict=self.VariablesUnev,evalf=self.f_eval_LaTeX)
                #        self.LaTeX += " = "
                #    self.LaTeX = self.LaTeX[:-3]
                #else:
                self.LaTeX = AF.LaTeX(self.cstr,local_dict=self.VariablesUnev,evalf=self.f_eval_LaTeX)
                if "#" in self.cstr:
                    self.LaTeX += r" \qquad \text{ " + self.cstr.split("#",1)[1] + " } "
            except common_exceptions:
                self.Notify(NC(exc=sys.exc_info(),lvl=2,msg="Could not convert input to LaTeX",func="AMaS.ConvertToLaTeX",send=False))
                self.LaTeX = r"\text{Could not convert}"
    
    def ConvertToLaTeX_Solution(self, expr=None):
        """
        Converts the solution into LaTeX and creates a LaTeX version of the equation. \n
        Handles ``self.LaTeX_S``, ``self.LaTeX_E`` and ``self.LaTeX_ER``. \n
        expr must be a Sympy Expression (NOT A STRING!)   \n
        If not given or not convertable try to convert self.Solution
        """
        try:
            if expr != None:
                try:
                    self.LaTeX_S = sympy.latex(expr)
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
                    self.LaTeX_S = r"\text{Could not convert}"
                    self.LaTeX_E = r"\text{Could not convert}"
                    self.LaTeX_ER = r"\text{Could not convert}"
                    expr = None
            if expr == None:
                try:
                    if self.Solution == "Not evaluated yet":
                        raise Exception("Equation has not been evaluated yet")
                    #if "=" in self.Solution:
                    #    parts = self.Solution.split("=")
                    #    self.LaTeX_S = ""
                    #    for i in parts:
                    #        if len(i)>0:
                    #            #self.LaTeX_S += sympy.latex( sympy.S(i,evaluate=False))
                    #            expr = parse_expr(i,evaluate=False,local_dict=self.Variables,global_dict=self.global_dict())
                    #            self.LaTeX_S += sympy.latex(expr)
                    #        self.LaTeX_S += " = "
                    #    self.LaTeX_S = self.LaTeX_S[:-3]
                    #else:
                    #    #self.LaTeX_S = sympy.latex( sympy.S(self.Solution,evaluate=False))
                    #    expr = parse_expr(self.Solution,evaluate=False,local_dict=self.Variables,global_dict=self.global_dict())
                    #    self.LaTeX_S = sympy.latex(expr)
                    self.LaTeX_S = AF.LaTeX(self.Solution,local_dict=self.VariablesUnev,evalf=1)
                except common_exceptions:
                    if expr==None: expr=self.Solution
                    self.Notify(NC(exc=sys.exc_info(),lvl=2,msg="Could not convert Solution to LaTeX",input=expr,func="AMaS.ConvertToLaTeX_Solution",send=False))
                    return False
        except common_exceptions:
            self.LaTeX_S = r"\text{Could not convert}"
            self.LaTeX_E = r"\text{Could not convert}"
            self.LaTeX_ER = r"\text{Could not convert}"
            self.Notify(NC(exc=sys.exc_info(),lvl=2,msg="Could not convert Solution to LaTeX",input=expr,func="AMaS.ConvertToLaTeX_Solution",send=False))
            return False
        else:
            try:
                LaTeX = self.LaTeX
                if LaTeX == r"\text{Could not convert}":
                    LaTeX = r"\text{" + self.Text + "}"
                self.LaTeX_S = AF.number_shaver(self.LaTeX_S)
                if self.Separator == " = ":
                    self.LaTeX_E  = LaTeX + " = " + self.LaTeX_S
                    self.LaTeX_ER = self.LaTeX_S + " = " + LaTeX
                elif self.Separator == "   ==>   ":
                    self.LaTeX_E  = LaTeX + r" \Longrightarrow " + self.LaTeX_S
                    self.LaTeX_ER = self.LaTeX_S + r" \Longleftarrow " + LaTeX
                else:
                    self.LaTeX_E  = LaTeX + r" \Longrightarrow " + self.LaTeX_S
                    self.LaTeX_ER = self.LaTeX_S + r" \Longleftarrow " + LaTeX
            except common_exceptions:
                self.LaTeX_E = r"\text{Could not convert}"
                self.LaTeX_ER = r"\text{Could not convert}"
                self.Notify(NC(exc=sys.exc_info(),lvl=2,msg="Could not convert Equation to LaTeX",input=expr,func="AMaS.ConvertToLaTeX_Solution",send=False))
                return False
            else:
                return True
    
 # ---------------------------------- Calculator Methods ----------------------------------
    # MAYBE: set a time limit for evaluations that can be disabled in the options (if this is even possible)


    def Evaluate(self, Method=1):
        """
        This method redirects to the various solver methods
        """
        if QtWidgets.QApplication.instance().optionWindow.cb_D_NewSolver.isChecked():
            return self.Evaluate_SymPy()
        elif Method==0:
            return self.Evaluate_SymPy()
        elif Method==1:
            return self.Evaluate_SymPy_old()
        else:
            self.Notify(NC(2,"Invalid evaluate method number. Using standard method instead.",func="AMaS.Evaluate",send=False))
            return self.Evaluate_SymPy_old()
        
    def CheckForNonesense(self,expr): #REMINDER: check for more dangerous things
        """
        This method searches for mathematical "nonesense" and warns the user. \n
        It currently searches for: \n
        Sums that don't converge.
        """
        try:
            if type(expr) in [str,int,float,complex,bool]:
                return
            elif type(expr) == dict:
                for k,i in expr.items():
                    self.CheckForNonesense(k)
                    self.CheckForNonesense(i)
            elif type(expr) == list:
                for i in expr:
                    self.CheckForNonesense(i)
            else:
                if expr.func in [sympy.Sum, sympy.Product]:
                    if expr.func == sympy.Sum:
                        f_s = "Sum"
                    elif expr.func == sympy.Product:
                        f_s = "Product"
                    try:
                        if not expr.is_convergent():
                            self.Notify(NC(2,"The input contains a {} that does NOT converge! The result is not to be trusted!".format(f_s),func="AMaS.Evaluate",input="{}:\n{}".format(f_s,str(expr)),send=False))
                    except NotImplementedError:
                        self.Notify(NC(2,"The input contains a {} that can not be checked for convergence! The result is not to be trusted!".format(f_s),func="AMaS.Evaluate",input="{}:\n{}".format(f_s,str(expr)),send=False))
                # CHECK HERE
                for arg in expr.args:
                    self.CheckForNonesense(arg)
        except AttributeError:
            pass
        except:
            self.Notify(NC(2,"The input could not be completely scanned for \"nonesense\"",func="AMaS.Evaluate",input="Expression: "+str(expr),exc=sys.exc_info(),send=False))

    def Evaluate_SymPy(self):
        Notification = NC(0,send=False)
        
        try:
            if self.Input.count("=") >= 1 and self.Input.count(",") >= 1:
                try:
                    if self.Solve_ODE_Version_1():
                        self.init_Flags()
                        return True
                except common_exceptions:
                    ExceptionOutput(sys.exc_info())
            try:
                pass #TODO: Try to solve it
            except common_exceptions:
                Notification = NC(1,"Could not solve",func="AMaS.Evaluate_SymPy",exc=sys.exc_info(),send=False)
            # TODO: reimplement the two solvers from the old one (one equalsign or none) but make the code less redundant and cleaner and handle dicts even better
        except common_exceptions:
            Notification = NC(1,"Could not solve",func="AMaS.Evaluate_SymPy",exc=sys.exc_info(),send=False)
            self.Solution = "Fail"
        
        self.Equation = self.Solution + self.Separator
        self.Equation += self.Text
        
        self.init_Flags() # Reset All Flags
        
        self.Equation = AF.number_shaver(self.Equation)
        self.Solution = AF.number_shaver(self.Solution)
        
        if self.Solution == "Fail":
            self.Notify(Notification)
            return False
        else:
            return True
        return True

    def Evaluate_SymPy_old(self):
        #TODO: CALCULATE EVEN MORE STUFF (how can solveset be used?)
        #TODO: Dirac does not work... what does the sympy documentation say to dirac...?
        #TODO: If a Sum is involved it should be checked for convergence with https://docs.sympy.org/latest/modules/concrete.html#sympy.concrete.summations.Sum.is_convergent
        #      If it is not convergent the user should be notified that the solution can not be trusted!
        # https://docs.sympy.org/latest/modules/evalf.html
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        
        Notification = NC(0,send=False)
        ODE = False
        if self.Input.count("=") >= 1 and self.Input.count(",") >= 1:
            try:
                ODE = self.Solve_ODE_Version_1()
            except common_exceptions:
                ExceptionOutput(sys.exc_info())
                ODE = False
        if ODE == True:
            self.init_Flags() # Reset All Flags
            return ODE
        
        if self.cstr.count("=") == 1 and self.cstr.split("=")[0].count("(")==self.cstr.split("=")[0].count(")"):
            try:
                temp = self.cstr
                #if Eval:
                #    temp.replace("Integral","integrate")
                temp = "(" + temp
                temp = temp.replace("=" , ") - (")
                temp = temp + ")"
                temp = AF.UnpackDualOperators(temp,Brackets=("[","]"))
                print(temp)
                ans = parse_expr(temp,local_dict=self.Variables,global_dict=self.global_dict())
                self.CheckForNonesense(ans)
                ParsedInput = ans
                try:
                    ans = ans.doit()
                except common_exceptions:
                    pass
                try:
                    if self.f_simplify==None:
                        ans = sympy.dsolve(ans,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                    else:
                        ans = sympy.dsolve(ans,simplify=self.f_simplify)
                    try:
                        classification = sympy.classify_ode(ParsedInput)
                        self.Notify(NC(3,"ODE Classification:\n"+str.join("\n",classification),func="AMaS.Evaluate_SymPy_old",send=False))
                    except common_exceptions:
                        Notification = NC(1,"Could not classify ODE",func="AMaS.Evaluate_SymPy_old",exc=sys.exc_info(),send=False)
                    try:
                        ansF = self.ExecuteFlags(ans)
                        self.Solution = str(ansF.lhs) + " = "
                        self.Solution += str(ansF.rhs)
                        self.ConvertToLaTeX_Solution(ansF)
                    except common_exceptions:
                        ansF = self.ExecuteFlags(ans)
                        self.Solution = str(ansF)
                        self.ConvertToLaTeX_Solution(ansF)
                except common_exceptions:
                    Notification = NC(1,"Could not solve as ODE",func="AMaS.Evaluate_SymPy_old",exc=sys.exc_info(),send=False)
                    if type(ans)==list:
                        self.Solution = "[ " if len(ans)>1 else ""
                        for ji in ans:
                            if QtWidgets.QApplication.instance().optionWindow.cb_F_solveFor.isChecked():
                                try:
                                    if self.f_simplify==None:
                                        j = sympy.solve(ji,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                    else:
                                        j = sympy.solve(ji,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=self.f_simplify)
                                except common_exceptions:
                                    self.Notify(NC(2,"Could not solve for "+QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text(),exc=sys.exc_info(),func="AMaS.Evaluate_SymPy_old",send=False))
                                    if self.f_simplify==None:
                                        j = sympy.solve(ji,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                    else:
                                        j = sympy.solve(ji,dict=True,simplify=self.f_simplify)
                            else:
                                if self.f_simplify==None:
                                    j = sympy.solve(ji,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                else:
                                    j = sympy.solve(ji,dict=True,simplify=self.f_simplify)
                            self.Solution += "[ " if len(ji)>1 else ""
                            le = len(self.Solution)
                            for i in j:
                                i = self.ExecuteFlags(i)
                                i_temp = str(i)
                                #i_temp = i_temp.rstrip('0').rstrip('.') if '.' in i_temp else i_temp #CLEANUP: Delete this, Already implemented
                                self.Solution += i_temp
                                self.Solution += " , "
                            if len(self.Solution) > le:
                                self.Solution = self.Solution[:-3]
                                self.Solution += " ]" if len(ji)>1 else ""
                            else:
                                self.Solution = self.Solution[:-2]
                                j = parse_expr(str(ji),local_dict=self.Variables,global_dict=self.global_dict())
                                try:
                                    j = j.doit()
                                except common_exceptions:
                                    ExceptionOutput(sys.exc_info())
                                try: # MAYBE: get rid of this evalf()
                                    if self.f_eval: j = j.evalf()
                                except common_exceptions:
                                    ExceptionOutput(sys.exc_info())
                                #j = self.ExecuteFlags(j) #MAYBE: Should this be done?
                                #self.Solution = "True" if j == 0 else "False: right side deviates by "+str(j)
                                try:
                                    if j == 0 or str(j) == "0":
                                        self.Solution = "True"
                                    elif sympy.cancel(j) == 0 or str(sympy.cancel(j)) == "0":
                                        self.Solution = "True"
                                        self.Notify(NC(3,"True in the sense that the terms cancel. Without cancling the right side deviates by "+str(j),func="AMaS.Evaluate_SymPy_old",send=False))
                                    else:
                                        self.Solution = "False: right side deviates by "+str(j)
                                except common_exceptions:
                                    self.Solution = "True" if j == 0 or str(j) == "0" else "False: right side deviates by "+str(j)
                            self.Solution += " , "
                        self.Solution = self.Solution[:-3]
                        self.Solution += " ]" if len(ans)>1 else ""
                    else:
                        if QtWidgets.QApplication.instance().optionWindow.cb_F_solveFor.isChecked():
                            try:
                                if self.f_simplify==None:
                                    ans = sympy.solve(ans,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                else:
                                    ans = sympy.solve(ans,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=self.f_simplify)
                            except common_exceptions:
                                self.Notify(NC(2,"Could not solve for "+QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text(),exc=sys.exc_info(),func="AMaS.Evaluate_SymPy_old",send=False))
                                if self.f_simplify==None:
                                    ans = sympy.solve(ans,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                else:
                                    ans = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                        else:
                            if self.f_simplify==None:
                                ans = sympy.solve(ans,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                            else:
                                ans = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                        self.Solution = "[ " if len(ans)>1 else ""
                        for i in ans:
                            i = self.ExecuteFlags(i)
                            i_temp = str(i)
                            #i_temp = i_temp.rstrip('0').rstrip('.') if '.' in i_temp else i_temp #CLEANUP: Delete this, Already implemented
                            self.Solution += i_temp
                            self.Solution += " , "
                        self.Solution = self.Solution[:-3]
                        if len(self.Solution) > 0:
                            self.Solution += " ]" if len(ans)>1 else ""
                        else:
                            ans = parse_expr(temp,local_dict=self.Variables,global_dict=self.global_dict())
                            try:
                                ans = ans.doit()
                            except common_exceptions:
                                ExceptionOutput(sys.exc_info())
                            try: # MAYBE: get rid of this evalf()
                                if self.f_eval: ans = ans.evalf()
                            except common_exceptions:
                                ExceptionOutput(sys.exc_info())
                            #ans = self.ExecuteFlags(ans) #MAYBE: Should this be done?
                            #self.Solution = "True" if ans == 0 else "False: right side deviates by "+str(ans)
                            try:
                                if ans == 0 or str(ans) == "0":
                                    self.Solution = "True"
                                elif sympy.cancel(ans) == 0 or str(sympy.cancel(ans)) == "0":
                                    self.Solution = "True"
                                    self.Notify(NC(3,"True in the sense that the terms cancel. Without cancling the right side deviates by "+str(ans),func="AMaS.Evaluate_SymPy_old",send=False))
                                else:
                                    self.Solution = "False: right side deviates by "+str(ans)
                            except common_exceptions:
                                self.Solution = "True" if ans == 0 or str(ans) == "0" else "False: right side deviates by "+str(ans)
                    self.ConvertToLaTeX_Solution()
                    
            except common_exceptions: #as inst:
                Notification = NC(1,"Could not solve",func="AMaS.Evaluate_SymPy_old",exc=sys.exc_info(),send=False)
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Solution = "Fail"
            self.Separator = "   ==>   "
            self.EquationReverse = AF.AstusParseInverse(self.Solution, True) + "   <==   "
            self.EquationReverse += self.Text
            self.Equation = self.Text + "   ==>   "
            self.Equation += AF.AstusParseInverse(self.Solution, True)
        else:
            try:
                temp = AF.UnpackDualOperators(self.cstr,Brackets=("{","}"))
                ans = parse_expr(temp,local_dict=self.Variables,global_dict=self.global_dict())
                self.CheckForNonesense(ans)
                separator = "   <==   "
                self.Separator = "   ==>   "
                ParsedInput = ans
                if type(ans) == bool:
                    self.Solution = str(ans)
                else:
                    try: # A problem was introduced with version 0.7.0 which necessitates this when inputting integrate(sqrt(sin(x))/(sqrt(sin(x))+sqrt(cos(x))))
                        # The Problem seems to be gone at least since version 0.8.0.3 but Keep this anyways in case other problems occur here...
                        ans = ans.doit()
                    except common_exceptions:
                        print("Could not simplify "+str(ans))
                        ExceptionOutput(sys.exc_info())
                    try:
                        if self.f_simplify==None:
                            ans = sympy.dsolve(ans,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                        else:
                            ans = sympy.dsolve(ans,simplify=self.f_simplify)
                        try:
                            classification = sympy.classify_ode(ParsedInput)
                            self.Notify(NC(3,"ODE Classification:\n"+str.join("\n",classification),func="AMaS.Evaluate_SymPy_old",send=False))
                        except common_exceptions:
                            Notification = NC(1,"Could not classify ODE",func="AMaS.Evaluate_SymPy_old",exc=sys.exc_info(),send=False)
                        ansF = self.ExecuteFlags(ans)
                        try:
                            self.Solution = str(ansF.lhs) + " = "
                            self.Solution += str(ansF.rhs)
                            self.ConvertToLaTeX_Solution(ansF)
                        except common_exceptions:
                            self.Solution = str(ansF)
                            self.ConvertToLaTeX_Solution(ansF)
                    except common_exceptions:
                        separator = " = " #TODO: inequalities should use the other separator
                        self.Separator = " = "
                        if self.f_eval:
                            try:
                                ans = ans.evalf()
                            except common_exceptions:
                                try:
                                    if QtWidgets.QApplication.instance().optionWindow.cb_F_solveFor.isChecked():
                                        try:
                                            if self.f_simplify==None:
                                                ans_S = sympy.solve(ans,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                            else:
                                                ans_S = sympy.solve(ans,AF.parse(QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text()),dict=True,simplify=self.f_simplify)
                                        except common_exceptions:
                                            self.Notify(NC(2,"Could not solve for "+QtWidgets.QApplication.instance().optionWindow.tf_F_solveFor.text(),exc=sys.exc_info(),func="AMaS.Evaluate_SymPy_old",send=False))
                                            if self.f_simplify==None:
                                                ans_S = sympy.solve(ans,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                            else:
                                                ans_S = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                                    else:
                                        if self.f_simplify==None:
                                            ans_S = sympy.solve(ans,dict=True,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
                                        else:
                                            ans_S = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                                    try:
                                        if not (type(ans_S)==list and len(ans_S)==0):
                                            ans = ans_S
                                    except common_exceptions:
                                        ans = ans_S
                                except common_exceptions:
                                    pass
                        ansF = self.ExecuteFlags(ans)
                        self.Solution = str(ansF)
                        self.ConvertToLaTeX_Solution(ansF)
                    #self.Solution = self.Solution.rstrip('0').rstrip('.') if '.' in self.Solution else self.Solution #CLEANUP: Delete this, Already implemented
            except common_exceptions: #as inst:
                Notification = NC(1,"Could not solve",func="AMaS.Evaluate_SymPy_old",exc=sys.exc_info(),send=False)
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Solution = "Fail"
                separator = "   <==   "
                self.Separator = "   ==>   "
            self.EquationReverse = AF.AstusParseInverse(self.Solution, True) + separator
            self.EquationReverse += self.Text
            if separator == "   <==   ":
                separator = "   ==>   "
            self.Equation = self.Text + separator
            self.Equation += AF.AstusParseInverse(self.Solution, True)
        
        self.init_Flags() # Reset All Flags
        
        self.Equation = AF.number_shaver(self.Equation)
        self.EquationReverse = AF.number_shaver(self.EquationReverse)
        self.Solution = AF.number_shaver(self.Solution)
        #self.ConvertToLaTeX_Equation()

        #self.Solution = AF.AstusParseInverse(self.Solution, True) # TODO: Inverse Parse the solution.
                                        # This currently breaks everything with E notation and probably much more when working with "ans".
                                        # The current way of only converting the displayed Equation works and does not have this problem.
                                        # The reason the Solution should be inverse-parsed is to give the user a prettier solution to copy.
        
        
        if self.Solution == "Fail":
            if QtWidgets.QApplication.instance().optionWindow.cb_U_EnableUnits.isChecked() and not self.disable_units:
                self.disable_units = True
                Notification.m("Could not solve. Trying to solve without units...\n(Units can be turned off in the options.)")
                Notification.l(3)
                self.Notify(Notification)
                return self.Evaluate(1)
            else:
                self.Notify(Notification)
                return False
        else:
            return True
        
    def EvaluateEquation_1(self): # This is currently being used
        temp = self.cstr
        #if Eval:
        #    temp.replace("Integral","integrate")
        temp = "(" + temp
        temp = temp.replace("=" , ") - (")
        temp = temp + ")"
        return True
        
    def EvaluateEquation_2(self): #IMPROVE: This might be better BUT: This is weird and does not always work and needs a lot of reprogramming and testing...
        temp = self.cstr
        temp1 , temp2 = self.cstr.split("=",1)
        temp = "Eq("+temp1
        temp += ","
        temp += temp2
        temp += ")"
        return True
                
    def EvaluateLaTeX(self):
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        try:
            ans = parse_latex(self.LaTeX)
            ans = ans.evalf()
            self.Solution = str(ans)
        except common_exceptions: #as inst:
            self.Notify(NC(1,"Could not solve",func="AMaS.EvaluateLaTeX",exc=sys.exc_info(),send=False))
            self.Solution = "Fail"
            return False
        return True

    def Solve_ODE_Version_1(self):
        Notification = NC(0,send=False)
        try:
            Input = self.Input
            Input = Input.split(",")
            func = Input[1].strip()[0]
            equation = AF.AstusParse(Input.pop(0))
            if equation.count("=") == 1 :
                equation = "(" + equation
                equation = equation.replace("=" , ") - (")
                equation = equation + ")"
            var = equation.split(func,1)[1].split("(",1)[1].split(")",1)[0].strip()
            print("Function:",func)
            print("Variable:",var)
            var_Parsed = parse_expr(var)
            equation = parse_expr(equation,local_dict=self.Variables,global_dict=self.global_dict())
            classification = sympy.classify_ode(equation)
            print("ODE Classification:\n",classification)
            self.Notify(NC(3,"ODE Classification:\n"+str.join("\n",classification),func="AMaS.Solve_ODE_Version_1",send=False))
            ics = {}
            for i in Input:
                f,y=i.split("=")
                f,x = f.split("(",1)
                x = x.split(")",1)[0].strip()
                f+="("
                f+=var
                f+=")"
                f,x,y = parse_expr(AF.AstusParse(f,False)),parse_expr(AF.AstusParse(x,False),local_dict=self.Variables,global_dict=self.global_dict()),parse_expr(AF.AstusParse(y,False),local_dict=self.Variables,global_dict=self.global_dict())
                f = f.subs(var_Parsed,x)
                ics[f] = y
            #ics = {f1.subs(x,x1):y1,f2.subs(x,x2):y2}
            func += "("
            func += var
            func += ")"
            func = parse_expr(func)
            if self.f_simplify==None:
                equation = sympy.dsolve(equation,func=func,ics=ics,simplify=QtWidgets.QApplication.instance().optionWindow.cb_F_simplify.isChecked())
            else:
                equation = sympy.dsolve(equation,func=func,ics=ics,simplify=self.f_simplify)
            equation = self.ExecuteFlags(equation)
            try:
                self.Solution = str(equation.lhs) + " = "
                self.Solution += str(equation.rhs)
                self.ConvertToLaTeX_Solution(equation)
            except common_exceptions:
                self.Solution = str(equation)
                self.ConvertToLaTeX_Solution(equation)

        except common_exceptions:
            Notification = NC(1,"Could not solve ODE",func="AMaS.Solve_ODE_Version_1",exc=sys.exc_info(),send=False)
            self.Solution = "Fail"
        
        self.Separator = "   ==>   "
        self.EquationReverse = AF.AstusParseInverse(self.Solution, True) + "   <==   "
        self.EquationReverse += self.Text
        self.Equation = self.Text + "   ==>   "
        self.Equation += AF.AstusParseInverse(self.Solution, True)
        #self.ConvertToLaTeX_Equation()
            
        if self.Solution == "Fail":
            return Notification
        else:
            return True
            
    def Solve_PDE_Version_1(self):
        #FEATURE: Add support for Partial Differential Equations
        # https://docs.sympy.org/latest/modules/solvers/pde.html
        # PDEs are currently solveable with:
        # pdsolve(1 + (2*(d(u(x,y))/dx)) + (3*(d(u(x,y))/dy)))
        pass

            
 # ---------------------------------- 2D Plotter Methods ----------------------------------
            
    def Plot_2D_Calc_Values(self):
        oldErrCall = np.seterrcall(self.NotifyFromNumpy)
        oldErrCall_sp = scipy.seterrcall(self.NotifyFromNumpy)
        if self.cstr.count("=")>=1:
            try:
                temp_line_split = self.cstr.split("=",1)
                temp_line_split[0] = temp_line_split[0].strip()
                if temp_line_split[0] == "x":
                    temp_line_x_val = parse_expr(temp_line_split[1],local_dict=self.Variables,global_dict=self.global_dict())
                    temp_line_x_val = float(temp_line_x_val.evalf())
                    if type(temp_line_x_val) == int or type(temp_line_x_val) == float :
                        self.plot_x_vals = temp_line_x_val
                        self.plot_data_exists = True
                        np.seterrcall(oldErrCall)
                        scipy.seterrcall(oldErrCall_sp)
                        return True
            except common_exceptions:
                pass
        
        
        if True : #self.plottable: #IMPROVE: The "plottable" thing is not exact. Try to plot it even if not "plottable" and handle the exceptions
            x = sympy.symbols('x')
            n = sympy.symbols('n') # pylint: disable=unused-variable
            try:
                Function = parse_expr(self.cstr,local_dict=self.Variables,global_dict=self.global_dict())
            except common_exceptions: #as inst:
                self.Notify(NC(1,"Could not calculate values for plot",func="AMaS.Plot_2D_Calc_Values",exc=sys.exc_info(),send=False))
                self.plottable = False
                np.seterrcall(oldErrCall)
                scipy.seterrcall(oldErrCall_sp)
                return False
            try:
                Function = Function.doit()
            except common_exceptions: #as inst:
                ExceptionOutput(sys.exc_info())
                
            if self.plot_xmax < self.plot_xmin:
                self.plot_xmax , self.plot_xmin = self.plot_xmin , self.plot_xmax
            
            if self.plot_per_unit:
                step_size = 1/(self.plot_points-1)
            else:
                step_size = (self.plot_xmax - self.plot_xmin)/(self.plot_points-1)
                
            #                                 from     up to (excluding the last!) step size
            self.plot_x_vals = np.arange(self.plot_xmin, self.plot_xmax+step_size, step_size)

            try:
                evalfunc = sympy.lambdify(x, Function, modules=['numpy','sympy'])
                print(self.plot_x_vals,type(self.plot_x_vals))
                self.plot_y_vals = evalfunc(self.plot_x_vals)
                
                
                if type(self.plot_y_vals) == int or type(self.plot_y_vals) == float or self.plot_y_vals.shape == (): #This also catches the case exp(x)
                    self.plot_y_vals = np.full_like(self.plot_x_vals , self.plot_y_vals)
                if self.plot_y_vals.shape != self.plot_x_vals.shape:
                    raise Exception("Dimensions do not match")
                
            except common_exceptions: #as inst:
                TheException = sys.exc_info()
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                # To Catch AttributeError 'ImmutableDenseNDimArray' object has no attribute 'could_extract_minus_sign'
                # This occurs, for example, when trying to plot integrate(sqrt(sin(x))/(sqrt(sin(x))+sqrt(cos(x))))
                # This is a known Sympy bug since ~2011 and is yet to be fixed...  See https://github.com/sympy/sympy/issues/5721
                try:
                    self.warningMutex.lock()
                    oldNPWarn = np.warnings.showwarning
                    oldWarn = warnings.showwarning
                    np.warnings.showwarning = self.NotifyWarning
                    warnings.showwarning = self.NotifyWarning
                    if self.cstr.count("Integral") == 0:
                        evalfunc = sympy.lambdify(x, self.cstr, modules='numpy')
                        self.plot_y_vals = evalfunc(self.plot_x_vals)
                        self.plot_y_vals = np.asarray(self.plot_y_vals)
                        
                        if type(self.plot_y_vals) == int or type(self.plot_y_vals) == float or self.plot_y_vals.shape == ():
                            self.plot_y_vals = np.full_like(self.plot_x_vals , self.plot_y_vals)
                        if self.plot_y_vals.shape != self.plot_x_vals.shape:
                            print(self.plot_y_vals.shape)
                            raise Exception("Dimensions do not match")
                        self.Notify(NC(3,msg="Could not calculate plot with sympy.\nUsing numpy instead.",exc=TheException,func="AMaS.Plot_2D_Calc_Values",send=False))
                    elif self.cstr.count("Integral") == 1 and( ( re.fullmatch(r"Integral\((.(?<!Integral))+,x\)",self.cstr) and self.cstr.count(",x)") == 1 ) or ( re.fullmatch(r"Integral\((.(?<!Integral))+\)",self.cstr) and self.cstr.count(",x)") == 0 )):
                        temp_Text = self.cstr
                        temp_Text = temp_Text.replace("Integral","")
                        temp_Text = re.sub(r",x\)$",")",temp_Text)
                        evalfunc = sympy.lambdify(x, temp_Text, modules='numpy')
                        
                        def F(X):
                            try:
                                return [scipy.integrate.quad(evalfunc, 0, y) for y in X]
                            except TypeError:
                                return scipy.integrate.quad(evalfunc, 0, X)
                        
                        self.plot_y_vals = evalfunc(self.plot_x_vals)
                        self.plot_y_vals = [F(X)[0] for X in self.plot_x_vals]
                        self.plot_y_vals = np.asarray(self.plot_y_vals)
                        
                        if type(self.plot_y_vals) == int or type(self.plot_y_vals) == float or self.plot_y_vals.shape == 1:
                            self.plot_y_vals = np.full_like(self.plot_x_vals , self.plot_y_vals)
                        if self.plot_y_vals.shape != self.plot_x_vals.shape:
                            raise Exception("Dimensions do not match")
                        self.Notify(NC(2,msg="Could not calculate plot with sympy.\nInstead using numpy to generate the data for the function and scipy to generate the integral of this data."
                                                +"\nWARNING: The displayed plot is not the plot of the input integral but of the integral of the plot of the function.",exc=TheException,func="AMaS.Plot_2D_Calc_Values",send=False))
                    else:
                        raise Exception("Can not calculate plot data")
                except common_exceptions: #as inst:
                    self.Notify(NC(1,"Could not calculate values for plot",func="AMaS.Plot_2D_Calc_Values",exc=sys.exc_info(),send=False))
                    np.seterrcall(oldErrCall)
                    scipy.seterrcall(oldErrCall_sp)
                    return False
                finally:
                    np.warnings.showwarning = oldNPWarn
                    warnings.showwarning = oldWarn
                    self.warningMutex.unlock()
                    
            self.plot_data_exists = True
            np.seterrcall(oldErrCall)
            scipy.seterrcall(oldErrCall_sp)
            return True
        else:
            np.seterrcall(oldErrCall)
            scipy.seterrcall(oldErrCall_sp)
            return False


 # ---------------------------------- Variable (and Multi-Dim) Methods ----------------------------------

    def AddVariable(self, Name, Value):
        self.Variables[Name] = Value
        self.VariablesUnev[Name] = sympy.UnevaluatedExpr(Value)
        return True

    def UpdateEquation(self, Text = None):
        try:
            if Text == None:
                Text = self.Input
            else:
                self.Input = Text
            self.string = Text
            self.init_Critical()
            
            temp = self.Text
            for i,v in self.Variables.items():
                temp = re.sub("((?<!\w)|(?<=\d))"+str(i)+"(?!\w)",str(v),temp) # pylint: disable=anomalous-backslash-in-string
            self.Text = temp
            
            self.Evaluate()
            #self.cstr = self.Solution
            self.ConvertToLaTeX()
            return True
        except common_exceptions:
            self.Notify(NC(lvl=1,msg="Could not update Equation",exc=sys.exc_info(),func="AMaS.UpdateEquation",send=False))
            return False


 # ---------------------------------- ... ----------------------------------


