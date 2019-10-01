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




class AMaS: # Astus' Mathematical Structure
    def __init__(self, string):
        try:
            self.Input = string
            self.TimeStamp = AF.cTimeSStr()
            #string = string.split("\n")
            string = string.splitlines()
            if type(string) == list :
                self.stringList = string
                self.string = string[0]
            else:
                self.stringList = [string]
                self.string = string
            self.init()
            self.init_plot()
            self.init_history()
        except AF.common_exceptions :
            self.Exists = False
        else:
            self.Exists = True
    
    def init(self):
        self.Text = AF.AstusParseInverse(self.string)
        #print(self.Text)
        self.Evaluation = "Not evaluated yet."
        self.EvaluationEquation = "? = " + self.Text
        self.cstr = AF.AstusParse(self.string) # the converted string that is interpreteable
        self.cstrList = []
        for i in self.stringList:
            self.cstrList.append(AF.AstusParse(i,False))
        self.LaTeX = "Not converted yet"
        self.LaTeX_L = "Not converted yet" #For display if in LaTeX-Mode
        self.LaTeX_N = "Not converted yet" #For display if in Not-LaTeX-Mode
        self.ConvertToLaTeX()
                
                
    def init_history(self):
        self.tab_1_is = False
        self.tab_1_ref = None
        self.tab_2_is = False
        self.tab_2_ref = None
        self.tab_3_is = False
        self.tab_3_ref = None
                
    def init_plot(self):
        # TODO: Improve this
        #if self.cstr.count("=")==0 and self.cstr.count("x")>=1: #TODO: use: if substr in string:
        if self.cstr.count("=")==0 and "x" in self.cstr:
            self.plottable = True
        else:
            self.plottable = False
        self.current_ax = None
        self.plot_data_exists = False
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
        
    def ConvertToLaTeX(self):
        try:
            #if self.cstr.count("=") >= 1 : #TODO: use: if substr in string:
            if "=" in self.cstr:
                parts = self.cstr.split("=")
                self.LaTeX = ""
                for i in parts:
                    if len(i)>0:
                        self.LaTeX += sympy.latex( sympy.S(i,evaluate=False))
                    self.LaTeX += " = "
                self.LaTeX = self.LaTeX[:-3]
            else:
                self.LaTeX = sympy.latex( sympy.S(self.cstr,evaluate=False))
        except AF.common_exceptions: #as inst:
            AF.ExceptionOutput(sys.exc_info())
            self.LaTeX = "Could not convert"
            
        self.LaTeX_L = ""
        self.LaTeX_N = ""
        n = len(self.cstrList)
        for i,e in enumerate(self.cstrList):
            n -= 1
            LineText = ""
            try:
                #if e.count("=") >= 1 : #TODO: use: if substr in string:
                if "=" in e :
                    parts = self.cstrList[i].split("=")
                    conv = ""
                    for j in parts:
                        if len(j)>0:
                            conv += sympy.latex( sympy.S(j,evaluate=False))
                        conv += " = "
                    LineText += conv[:-3]
                else:
                    LineText += sympy.latex( sympy.S(e,evaluate=False))
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
        
    
    def Analyse(self): #TODO: Make it work or delete it
        #TODO: keep parse_expr() in mind!!!
        # https://docs.sympy.org/latest/modules/parsing.html
        i_first = -1
        for i in ART.beginning_symbols:
            i_curr = self.cstr.find(ART.beginning_symbols[i])
            if i_curr != -1:
                if i_first == -1:
                    i_first = i_curr
                elif i_curr < i_first:
                    i_first = i_curr
    
    def Evaluate(self,EvalF = True): # TODOMode: Not happy with the EvalF thing...
        #TODO:CALCULATE MORE STUFF
        # https://docs.sympy.org/latest/modules/evalf.html
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        if self.cstr.count("=") == 1 :
            try:
                temp = self.cstr
                #if EvalF:
                #    temp.replace("Integral","integrate")
                temp = "(" + temp
                temp = temp.replace("=" , ") - (")
                temp = temp + ")"
                ans = parse_expr(temp)
                ans = ans.doit()
                ans = sympy.solve(ans)
                self.Evaluation = "{ "
                for i in ans:
                    if EvalF and not type(i) == dict: # TODOMode: Not happy with the EvalF thing... BUT happy with i.evalf()!!!!!!
                        i = i.evalf()
                    i_temp = str(i)
                    i_temp = i_temp.rstrip('0').rstrip('.') if '.' in i_temp else i_temp #TODO: make this work for complex numbers
                    self.Evaluation += i_temp
                    self.Evaluation += " , "
                self.Evaluation = self.Evaluation[:-3]
                if len(self.Evaluation) > 0:
                    self.Evaluation += " }"
                else:
                    ans = parse_expr(temp)
                    ans = ans.evalf()
                    self.Evaluation = "True" if ans == 0 else "False: right side deviates by "+str(ans)
                    
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + "   <==   "
            self.EvaluationEquation += self.Text
        else:
            try:
                ans = parse_expr(self.cstr)
                try: # A problem was introduced with version 0.7.0 which necessitates this when inputting integrate(sqrt(sin(x))/(sqrt(sin(x))+sqrt(cos(x))))
                    # The Problem seems to be gone at least since version 0.8.0.3 but Keep this anyways in case other problems occure here...
                    ans = ans.doit()
                except ValueError:
                    print("Could not simplify "+str(ans))
                    AF.ExceptionOutput(sys.exc_info())
                if EvalF: # TODOMode: Not happy with the EvalF thing... BUT happy with ans.evalf()!!!!!!
                    ans = ans.evalf()
                self.Evaluation = str(ans)
                self.Evaluation = self.Evaluation.rstrip('0').rstrip('.') if '.' in self.Evaluation else self.Evaluation #TODO: make this work for complex numbers
            except AF.common_exceptions: #as inst:
                AF.ExceptionOutput(sys.exc_info())
                #print(inst.args)
                #if callable(inst.args):
                #    print(inst.args())
                self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + " = "
            self.EvaluationEquation += self.Text
        if self.Evaluation == "Fail":
            return False
        else:
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
            
            
    def Plot_Calc_Values(self):
        if self.cstr.count("=")>=1:
            try:
                temp_line_split = self.cstr.split("=",1)
                temp_line_split[0] = temp_line_split[0].strip()
                if temp_line_split[0] == "x":
                    temp_line_x_val = parse_expr(temp_line_split[1])
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
                Function = parse_expr(self.cstr)
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


