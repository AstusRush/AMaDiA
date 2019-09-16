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

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors

import AMaDiA_Functions as AF
import AMaDiA_ReplacementTables as ART


##### SEE https://github.com/sympy/sympy_gamma/


class AMaS: # Astus' Mathematical Structure
    def __init__(self, string, Type = "Python"): # TODOMode: Not happy with the Mode thing...
        self.TimeStamp = AF.cTimeSStr()
        self.Type = Type # LaTeX = L , Python = P , Complex = C # TODOMode: Not happy with the Mode thing...
        self.string = string
        self.init()
    
    def init(self):
        self.string = self.string.replace("integrate","Integral") # integrate takes 6 seconds to evaluate while Integral takes "no" time but both do the same
        self.string = self.string.replace("integral","Integral") # also doing this in case of capitalization stuff
        self.Text = self.string
        self.Evaluation = "Not evaluated yet."
        self.EvaluationEquation = "? = " + self.Text
        #self.Analyse() #TODO
        try:
            self.simpleConversion = AF.Convert_to_LaTeX(self.string) #TODO: Remove or change
        except ... :
            self.simpleConversion = "Fail"
        self.LaTeX = self.simpleConversion
        if self.Type == "C" or self.Type == "Complex": # TODOMode: Not happy with the Mode thing...
            self.LaTeX = self.simpleConversion # TODO
            
        elif self.Type == "L" or self.Type == "Latex": # TODOMode: Not happy with the Mode thing...
            self.LaTeX = self.simpleConversion
            
        elif self.Type == "P" or self.Type == "Python": # TODOMode: Not happy with the Mode thing...
            try:
                if self.string.count("=") >= 1 :
                    parts = self.string.split("=")
                    self.LaTeX = ""
                    for i in parts:
                        if len(i)>0:
                            self.LaTeX += sympy.latex( sympy.S(i,evaluate=False))
                        self.LaTeX += " = "
                    self.LaTeX = self.LaTeX[:-3]
                else:
                    self.LaTeX = sympy.latex( sympy.S(self.string,evaluate=False))
            except sympy.SympifyError :
                self.LaTeX = "Fail"
        
    
    def Analyse(self): #TODO: Make it work
        #TODO: keep sympy.parsing.sympy_parser.parse_expr() in mind!!!
        # https://docs.sympy.org/latest/modules/parsing.html
        i_first = -1
        for i in ART.beginning_symbols:
            i_curr = self.string.find(ART.beginning_symbols[i])
            if i_curr != -1:
                if i_first == -1:
                    i_first = i_curr
                elif i_curr < i_first:
                    i_first = i_curr
    
    def Evaluate(self,EvalF = True): # TODOMode: Not happy with the EvalF thing...
        #TODO:CALCULATE MORE STUFF
        # https://docs.sympy.org/latest/modules/evalf.html
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        if self.string.count("=") == 1 :
            if self.Type == "P" or self.Type == "Python": # TODOMode: Not happy with the Mode thing...
                try:
                    temp = self.string
                    temp = "(" + temp
                    temp = temp.replace("=" , ") - (")
                    temp = temp + ")"
                    ans = sympy.parsing.sympy_parser.parse_expr(temp)
                    ans = sympy.solve(ans)
                    self.Evaluation = "[ "
                    for i in ans:
                        if EvalF: # TODOMode: Not happy with the EvalF thing... BUT happy with i.evalf()!!!!!!
                            i = i.evalf()
                        i_temp = str(i)
                        i_temp = i_temp.rstrip('0').rstrip('.') if '.' in i_temp else i_temp
                        self.Evaluation += str(i)
                        self.Evaluation += " , "
                    self.Evaluation = self.Evaluation[:-3]
                    if len(self.Evaluation) > 0:
                        self.Evaluation += " ]"
                    else:
                        ans = sympy.parsing.sympy_parser.parse_expr(temp)
                        ans = ans.evalf()
                        self.Evaluation = "True" if ans == 0 else "False: "+str(ans)
                        
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            if self.Type == "L" or self.Type == "Latex": # TODOMode: Not happy with the Mode thing...
                #TODO
                try:
                    ans = parse_latex(temp)
                    ans = sympy.solve(ans)
                    self.Evaluation = str(ans)
                    self.Evaluation = self.Evaluation.rstrip('0').rstrip('.') if '.' in self.Evaluation else self.Evaluation
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + "   <==   "
            self.EvaluationEquation += self.Text
        else:
            if self.Type == "P" or self.Type == "Python": # TODOMode: Not happy with the Mode thing...
                try:
                    ans = sympy.parsing.sympy_parser.parse_expr(self.string)
                    if EvalF: # TODOMode: Not happy with the EvalF thing...
                        ans = ans.evalf()
                    self.Evaluation = str(ans)
                    self.Evaluation = self.Evaluation.rstrip('0').rstrip('.') if '.' in self.Evaluation else self.Evaluation
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            if self.Type == "L" or self.Type == "Latex": # TODOMode: Not happy with the Mode thing...
                try:
                    ans = parse_latex(self.string)
                    if EvalF: # TODOMode: Not happy with the EvalF thing...
                        ans = ans.evalf()
                    self.Evaluation = str(ans)
                    self.Evaluation = self.Evaluation.rstrip('0').rstrip('.') if '.' in self.Evaluation else self.Evaluation
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + " = "
            self.EvaluationEquation += self.Text
                
    def EvaluateLaTeX(self):
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        try:
            ans = parse_latex(self.LaTeX)
            ans = ans.evalf()
            self.Evaluation = str(ans)
        except sympy.SympifyError :
            self.Evaluation = "Fail"
