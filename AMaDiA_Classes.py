# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:55:31 2019

@author: Robin
"""

# if__name__ == "__main__":
#     pass

import sys
from PyQt5 import QtWidgets,QtCore,QtGui # Maybe Needs a change of the interpreter of Qt Creator to work there
import socket
import datetime
import platform
import errno
import os
import sympy
import re

from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import scipy

import AMaDiA_Functions as AF
import AMaDiA_ReplacementTables as ART



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

class AMaS: # Astus' Mathematical Structure

 # ---------------------------------- INIT ----------------------------------
    def __init__(self, string, Iam):
        self.Input = string
        self.TimeStamp = AF.cTimeSStr()
        self.TimeStampFull = AF.cTimeFullStr()
        self.Name = "No Name Given"
        self.init_bools()
        self.init_Flags()
        self.Iam = Iam
        self.Variables = {}
        try:
            self.INIT_WhatAmI(string)
        except AF.common_exceptions :
            AF.ExceptionOutput(sys.exc_info())
            self.Exists = False
        else:
            self.Exists = True
    
    def init_bools(self):
        self.multiline = False
        self.Plot_is_initialized = False
        self.plot_data_exists = False
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
        #TODO
        # https://docs.sympy.org/latest/modules/solvers/ode.html
        print("Iam_ODE IS NOT IMPLEMENTED YET!")
        self.INIT_Normal(string)

    def INIT_Multi_Dim(self,string):
        self.Name = string
        self.string = "0"
        self.init_Critical()

    def init_Critical(self):
        self.Text = AF.AstusParseInverse(self.string)
        self.Evaluation = "Not evaluated yet."
        self.EvaluationEquation = "? = " + self.Text
        self.cstr = AF.AstusParse(self.string) # the converted string that is interpreteable
        if self.multiline:
            self.cstrList = []
            for i in self.stringList:
                self.cstrList.append(AF.AstusParse(i,False))
        self.LaTeX = "Not converted yet"
        self.LaTeX_L = "Not converted yet" #For display if in LaTeX-Mode
        self.LaTeX_N = "Not converted yet" #For display if in Not-LaTeX-Mode
        self.LaTeX_E = "Not converted yet" #For display of the Solution
        self.LaTeX_E_L = "Not converted yet" #For display if in LaTeX-Mode
        self.LaTeX_E_N = "Not converted yet" #For display if in Not-LaTeX-Mode
        self.Am_I_Plottable()
        self.ConvertToLaTeX()
        

    def Am_I_Plottable(self):
        # TODO: Improve the criteria for "plottable"
        if "x" in self.cstr and not "=" in self.cstr:
            self.plottable = True
        else:
            self.plottable = False
                
                
    def init_history(self):
        self.tab_1_is = False
        self.tab_1_ref = None
        self.tab_2_is = False
        self.tab_2_ref = None
        self.tab_3_is = False
        self.tab_3_ref = None
        self.Tab_5_is = False
        self.Tab_5_ref = None
                
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
        self.plot_steps = 1000
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

        # TODO : FOLLOWING NEED IMPLEMENTATION:

        # Simplify: https://docs.sympy.org/latest/tutorial/simplification.html
        self.f_simplify = True      # Simplifies
        self.f_expand = False       # Solve all * and **
        self.f_factor = False       # takes a polynomial and factors it into irreducible factors (Inverse of expand)
        self.f_collect = False      # collects common powers of a term in an expression
        self.f_cancel = False       # will take any rational function and put it into the standard canonical form p/q
        self.f_apart = False        # performs a partial fraction decomposition on a rational function
        self.f_expand_trig = False  # To expand trigonometric functions, that is, apply the sum or double angle identities
        self.f_powsimp = True      # Simplifies/Collects exponents

        self.f_rewrite = False      # A common way to deal with special functions is to rewrite them in terms of one another
        self.f_rewritefunc = None   # For example: tan(x).rewrite(sin)

        #self.f_ = False

    def ExecuteFlags(self,expr):
        try:
            if self.f_eval:
                expr = expr.evalf()
        except AF.common_exceptions :
            AF.ExceptionOutput(sys.exc_info())
        try:
            if self.f_powsimp:
                if type(expr) == sympy.Equality:
                    expr = sympy.Eq(sympy.powsimp(expr.lhs),sympy.powsimp(expr.rhs))
                else:
                    expr = sympy.powsimp(expr)
        except AF.common_exceptions :
            AF.ExceptionOutput(sys.exc_info())
        try:
            if self.f_simplify:
                expr = sympy.simplify(expr)
        except AF.common_exceptions :
            AF.ExceptionOutput(sys.exc_info())
        # TODO : Add the others
        return expr

 # ---------------------------------- LaTeX Converter ----------------------------------

    def ConvertToLaTeX(self):
        # Create the string that the user can copy
        try:
            if "=" in self.cstr:
                parts = self.cstr.split("=")
                self.LaTeX = ""
                for i in parts:
                    if len(i)>0:
                        #self.LaTeX += sympy.latex( sympy.S(i,evaluate=False))
                        expr = parse_expr(i,evaluate=False,local_dict=self.Variables)
                        self.LaTeX += sympy.latex(expr)
                    self.LaTeX += " = "
                self.LaTeX = self.LaTeX[:-3]
            else:
                #self.LaTeX = sympy.latex( sympy.S(self.cstr,evaluate=False))
                expr = parse_expr(self.cstr,evaluate=False,local_dict=self.Variables)
                self.LaTeX = sympy.latex(expr)
        except AF.common_exceptions:
            AF.ExceptionOutput(sys.exc_info())
            self.LaTeX = "Could not convert"
        
        # Set up the strings that are used in the LaTeX Displays
        if self.multiline:
            self.ConvertToLaTeX_Multiline()
        elif self.LaTeX == "Could not convert":
            self.LaTeX_L = self.cstr
            self.LaTeX_N = self.cstr
        else:
            self.LaTeX_L = "$\displaystyle"
            self.LaTeX_N = "$"
            self.LaTeX_L += self.LaTeX
            self.LaTeX_N += self.LaTeX
            self.LaTeX_L += "$"
            self.LaTeX_N += "$"

            
        
    def ConvertToLaTeX_Multiline(self):
        self.LaTeX_L = ""
        self.LaTeX_N = ""
        n = len(self.cstrList)
        for i,e in enumerate(self.cstrList):
            n -= 1
            LineText = ""
            try:
                if e.strip() == "":
                    LineText += "-"
                    if n > 0:
                        LineText += "\n"
                        #self.LaTeX_L += "$\displaystyle"
                        #self.LaTeX_N += "$"
                    self.LaTeX_L += LineText
                    self.LaTeX_N += LineText
                    continue
                if "=" in e :
                    parts = self.cstrList[i].split("=")
                    conv = ""
                    for j in parts:
                        if len(j)>0:
                            #conv += sympy.latex( sympy.S(j,evaluate=False))
                            expr = parse_expr(j,evaluate=False,local_dict=self.Variables)
                            conv += sympy.latex(expr)
                        conv += " = "
                    LineText += conv[:-3]
                else:
                    #LineText += sympy.latex( sympy.S(e,evaluate=False))
                    expr = parse_expr(e,evaluate=False,local_dict=self.Variables)
                    LineText = sympy.latex(expr)
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                # LineText += AF.AstusParseInverse(e) #TODO: Unicodesymbols seem to brake LaTeX Output... Maybe there is a way to fix it?
                LineText += e
                if n > 0:
                    LineText += "\n"
                self.LaTeX_L += LineText
                self.LaTeX_N += LineText
            else:
                LineText += "$"
                if n > 0:
                    LineText += "\n"
                self.LaTeX_L += "$\displaystyle"
                self.LaTeX_N += "$"
                self.LaTeX_L += LineText
                self.LaTeX_N += LineText


    def Convert_Evaluation_to_LaTeX(self, expr=None):
        # expr must be a Sympy Expression (NOT A STRING!)
        # If not given or not convertable try to convert self.Evaluation
        try:
            if expr != None:
                try:
                    self.LaTeX_E = sympy.latex(expr)
                except AF.common_exceptions:
                    AF.ExceptionOutput(sys.exc_info())
                    self.LaTeX_E = "Could not convert"
                    expr = None
            if expr == None:
                try:
                    if self.Evaluation == "Not evaluated yet.":
                        raise Exception("Not evaluated yet.")
                    if "=" in self.Evaluation:
                        parts = self.Evaluation.split("=")
                        self.LaTeX_E = ""
                        for i in parts:
                            if len(i)>0:
                                #self.LaTeX_E += sympy.latex( sympy.S(i,evaluate=False))
                                expr = parse_expr(i,evaluate=False,local_dict=self.Variables)
                                self.LaTeX_E += sympy.latex(expr)
                            self.LaTeX_E += " = "
                        self.LaTeX_E = self.LaTeX_E[:-3]
                    else:
                        #self.LaTeX_E = sympy.latex( sympy.S(self.Evaluation,evaluate=False))
                        expr = parse_expr(self.Evaluation,evaluate=False,local_dict=self.Variables)
                        self.LaTeX_E = sympy.latex(expr)
                except AF.common_exceptions:
                    AF.ExceptionOutput(sys.exc_info())
                    self.LaTeX_E = "Could not convert"
                    self.LaTeX_E_L += self.LaTeX_E
                    self.LaTeX_E_N += self.LaTeX_E
                    return False
            self.LaTeX_E_L = "$\displaystyle"
            self.LaTeX_E_N = "$"
            self.LaTeX_E_L += self.LaTeX_E
            self.LaTeX_E_N += self.LaTeX_E
            self.LaTeX_E_L += "$"
            self.LaTeX_E_N += "$"
        except AF.common_exceptions: #as inst:
            AF.ExceptionOutput(sys.exc_info())
            return False
        return True
        
    
    def Analyse(self): #TODO: Make it work or delete it
        #TODO: keep parse_expr() in mind!!!
        # https://docs.sympy.org/latest/modules/parsing.html
        i_first = -1
        for i in ART.l_beginning_symbols:
            i_curr = self.cstr.find(ART.l_beginning_symbols[i])
            if i_curr != -1:
                if i_first == -1:
                    i_first = i_curr
                elif i_curr < i_first:
                    i_first = i_curr


 # ---------------------------------- Calculator Methods ----------------------------------


    def Evaluate(self):
        #TODO:CALCULATE MORE STUFF
        # https://docs.sympy.org/latest/modules/evalf.html
        # https://docs.sympy.org/latest/modules/solvers/solvers.html

        ODE = False
        if self.Input.count("=") >= 1 and self.Input.count(",") >= 1:
            try:
                ODE = self.Solve_ODE_Version_1()
            except AF.common_exceptions:
                AF.ExceptionOutput(sys.exc_info())
                ODE = False
        if ODE == True:
            self.init_Flags() # Reset All Flags
            return ODE

        Error = "None"
        if self.cstr.count("=") == 1 :
            try:
                temp = self.cstr
                #if Eval:
                #    temp.replace("Integral","integrate")
                temp = "(" + temp
                temp = temp.replace("=" , ") - (")
                temp = temp + ")"
                ans = parse_expr(temp,local_dict=self.Variables)
                ParsedInput = ans
                try:
                    ans = ans.doit()
                except AF.common_exceptions:
                    pass
                try:
                    ans = sympy.dsolve(ans,simplify=self.f_simplify)
                    try:
                        print("ODE Class:",sympy.classify_ode(ParsedInput))
                    except AF.common_exceptions:
                        Error = AF.ExceptionOutput(sys.exc_info())
                    try:
                        ansF = self.ExecuteFlags(ans)
                        self.Evaluation = str(ansF.lhs) + " = "
                        self.Evaluation += str(ansF.rhs)
                        self.Convert_Evaluation_to_LaTeX(ansF)
                    except AF.common_exceptions:
                        ansF = self.ExecuteFlags(ans)
                        self.Evaluation = str(ansF)
                        self.Convert_Evaluation_to_LaTeX(ansF)
                except AF.common_exceptions:
                    ans = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                    self.Evaluation = "{ "
                    for i in ans:
                        if not type(i) == dict:
                            i = self.ExecuteFlags(i)
                        i_temp = str(i)
                        i_temp = i_temp.rstrip('0').rstrip('.') if '.' in i_temp else i_temp #TODO: make this work for complex numbers. Use re
                        self.Evaluation += i_temp
                        self.Evaluation += " , "
                    self.Evaluation = self.Evaluation[:-3]
                    if len(self.Evaluation) > 0:
                        self.Evaluation += " }"
                    else:
                        ans = parse_expr(temp,local_dict=self.Variables)
                        ans = ans.doit()
                        try: # TODO Maybe get rid of this evalf()
                            if self.f_eval: ans = ans.evalf()
                        except AF.common_exceptions:
                            AF.ExceptionOutput(sys.exc_info())
                        self.Evaluation = "True" if ans == 0 else "False: right side deviates by "+str(ans)
                    self.Convert_Evaluation_to_LaTeX()
                    
            except AF.common_exceptions: #as inst:
                Error = AF.ExceptionOutput(sys.exc_info())
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + "   <==   "
            self.EvaluationEquation += self.Text
        else:
            try:
                ans = parse_expr(self.cstr,local_dict=self.Variables)
                ParsedInput = ans
                try: # A problem was introduced with version 0.7.0 which necessitates this when inputting integrate(sqrt(sin(x))/(sqrt(sin(x))+sqrt(cos(x))))
                    # The Problem seems to be gone at least since version 0.8.0.3 but Keep this anyways in case other problems occure here...
                    ans = ans.doit()
                except AF.common_exceptions:
                    print("Could not simplify "+str(ans))
                    AF.ExceptionOutput(sys.exc_info())
                try:
                    ans = sympy.dsolve(ans,simplify=self.f_simplify)
                    try:
                        print("ODE Class:",sympy.classify_ode(ParsedInput))
                    except AF.common_exceptions:
                        Error = AF.ExceptionOutput(sys.exc_info())
                    ansF = self.ExecuteFlags(ans)
                    try:
                        self.Evaluation = str(ansF.lhs) + " = "
                        self.Evaluation += str(ansF.rhs)
                        self.Convert_Evaluation_to_LaTeX(ansF)
                    except AF.common_exceptions:
                        self.Evaluation = str(ansF)
                        self.Convert_Evaluation_to_LaTeX(ansF)
                    separator = "   <==   "
                except AF.common_exceptions:
                    separator = " = "
                    if self.f_eval:
                        try:
                            ans = ans.evalf()
                        except AF.common_exceptions:
                            ans = sympy.solve(ans,dict=True,simplify=self.f_simplify)
                    ansF = self.ExecuteFlags(ans)
                    self.Evaluation = str(ansF)
                    self.Convert_Evaluation_to_LaTeX(ansF)
                self.Evaluation = self.Evaluation.rstrip('0').rstrip('.') if '.' in self.Evaluation else self.Evaluation #TODO: make this work for complex numbers. Use re
            except AF.common_exceptions: #as inst:
                Error = AF.ExceptionOutput(sys.exc_info())
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Evaluation = "Fail"
                separator = "   <==   "
            self.EvaluationEquation = self.Evaluation + separator
            self.EvaluationEquation += self.Text
        
        self.init_Flags() # Reset All Flags
        
        
        
        if self.Evaluation == "Fail":
            return Error
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
        
    def EvaluateEquation_2(self): #TODO: This might be better BUT: This is weired and does not always work and needs a lot of reprogramming and testing...
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
            self.Evaluation = str(ans)
        except AF.common_exceptions: #as inst:
            AF.ExceptionOutput(sys.exc_info())
            #print(inst.args)
            #if callable(inst.args):
            #    print(inst.args())
            self.Evaluation = "Fail"
            return False
        return True

    def Solve_ODE_Version_1(self):
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
            equation = parse_expr(equation,local_dict=self.Variables)
            print("ODE Class:",sympy.classify_ode(equation))
            ics = {}
            for i in Input:
                f,y=i.split("=")
                f,x = f.split("(",1)
                x = x.split(")",1)[0].strip()
                f+="("
                f+=var
                f+=")"
                f,x,y = parse_expr(AF.AstusParse(f,False)),parse_expr(AF.AstusParse(x,False),local_dict=self.Variables),parse_expr(AF.AstusParse(y,False),local_dict=self.Variables)
                f = f.subs(var_Parsed,x)
                ics[f] = y
            #ics = {f1.subs(x,x1):y1,f2.subs(x,x2):y2}
            func += "("
            func += var
            func += ")"
            func = parse_expr(func)
            equation = sympy.dsolve(equation,func=func,ics=ics,simplify=self.f_simplify)
            equation = self.ExecuteFlags(equation)
            try:
                self.Evaluation = str(equation.lhs) + " = "
                self.Evaluation += str(equation.rhs)
                self.Convert_Evaluation_to_LaTeX(equation)
            except AF.common_exceptions:
                self.Evaluation = str(equation)
                self.Convert_Evaluation_to_LaTeX(equation)

        except AF.common_exceptions:
            Error = AF.ExceptionOutput(sys.exc_info())
            self.Evaluation = "Fail"
        
        self.EvaluationEquation = self.Evaluation + "   <==   "
        self.EvaluationEquation += self.Text
            
        if self.Evaluation == "Fail":
            return Error
        else:
            return True
            
            
 # ---------------------------------- 2D Plotter Methods ----------------------------------
            
    def Plot_2D_Calc_Values(self):
        if self.cstr.count("=")>=1:
            try:
                temp_line_split = self.cstr.split("=",1)
                temp_line_split[0] = temp_line_split[0].strip()
                if temp_line_split[0] == "x":
                    temp_line_x_val = parse_expr(temp_line_split[1],local_dict=self.Variables)
                    temp_line_x_val = float(temp_line_x_val.evalf())
                    if type(temp_line_x_val) == int or type(temp_line_x_val) == float :
                        self.plot_x_vals = temp_line_x_val
                        self.plot_data_exists = True
                        return True
            except AF.common_exceptions:
                pass
        
        
        if True : #self.plottable: #TODO: The "plottable" thing is not exact. Try to plot it even if not "plottable" and handle the exceptions
            x = sympy.symbols('x')
            n = sympy.symbols('n')
            try:
                Function = parse_expr(self.cstr,local_dict=self.Variables)
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                self.plottable = False
                return False
            try:
                Function = Function.doit()
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                
            if self.plot_xmax < self.plot_xmin:
                self.plot_xmax , self.plot_xmin = self.plot_xmin , self.plot_xmax
            
            if self.plot_per_unit:
                steps = 1/self.plot_steps
            else:
                steps = (self.plot_xmax - self.plot_xmin)/self.plot_steps
                
            self.plot_x_vals = np.arange(self.plot_xmin, self.plot_xmax+steps, steps)
            try:
                #e = sympy.numbers.E
                evalfunc = sympy.lambdify(x, Function, modules='sympy') # Can not handle exp(x) and cos(),etc ... Maybe try the loop to go through every value...
                self.plot_y_vals = evalfunc(self.plot_x_vals)
                
                
                if type(self.plot_y_vals) == int or type(self.plot_y_vals) == float or self.plot_y_vals.shape == (): #This also catches the case exp(x)
                    self.plot_y_vals = np.full_like(self.plot_x_vals , self.plot_y_vals)
                if self.plot_y_vals.shape != self.plot_x_vals.shape:
                    raise Exception("Dimensions do not match")
                
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                # To Catch AttributeError 'ImmutableDenseNDimArray' object has no attribute 'could_extract_minus_sign'
                # This occures, for example, when trying to plot integrate(sqrt(sin(x))/(sqrt(sin(x))+sqrt(cos(x))))
                # This is a known Sympy bug since ~2011 and is yet to be fixed...  See https://github.com/sympy/sympy/issues/5721
                
                # To Catch ValueError Invalid limits given
                # This occures, for example, when trying to plot integrate(x**2)
                # This is a weird bug #TODO: Investigate this bug...
                
                try:
                    if self.cstr.count("Integral") != 1:
                        evalfunc = sympy.lambdify(x, self.cstr, modules='numpy')
                        self.plot_y_vals = evalfunc(self.plot_x_vals)
                        self.plot_y_vals = np.asarray(self.plot_y_vals)
                        
                        if type(self.plot_y_vals) == int or type(self.plot_y_vals) == float or self.plot_y_vals.shape == ():
                            self.plot_y_vals = np.full_like(self.plot_x_vals , self.plot_y_vals)
                        if self.plot_y_vals.shape != self.plot_x_vals.shape:
                            print(self.plot_y_vals.shape)
                            raise Exception("Dimensions do not match")
                    else:
                        temp_Text = self.cstr
                        temp_Text = temp_Text.replace("Integral","")
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
                except AF.common_exceptions: #as inst:
                    AF.ExceptionOutput(sys.exc_info())
                    return False
                    
            self.plot_data_exists = True
            return True
        else:
            return False


 # ---------------------------------- Variable (and Multi-Dim) Methods ----------------------------------

    def AddVariable(self, Name, Value):
        self.Variables[Name] = Value
        return True

    def UpdateEquation(self, Text = None):
        if Text == None:
            Text = self.Input
        self.Input = Text
        self.string = Text
        self.init_Critical()
        self.Evaluate()
        #self.cstr = self.Evaluation
        self.ConvertToLaTeX()
        return True


# ---------------------------------- ... ----------------------------------