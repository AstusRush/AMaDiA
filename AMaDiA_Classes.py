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
    def __init__(self, string, Type = "Python"):
        self.TimeStamp = AF.cTimeSStr()
        self.Type = Type # LaTeX = L , Python = P , Complex = C
        self.string = string
        self.init()
    
    def init(self):
        self.Text = self.string
        self.Evaluation = "Not evaluated yet."
        self.EvaluationEquation = "? = " + self.Text
        #self.Analyse() #TODO
        try:
            self.simpleConversion = AF.Convert_to_LaTeX(self.string) #TODO: Remove or change
        except ... :
            self.simpleConversion = "Fail"
        self.LaTeX = self.simpleConversion
        if self.Type == "C" or self.Type == "Complex":
            self.LaTeX = self.simpleConversion # TODO
            
        elif self.Type == "L" or self.Type == "Latex":
            self.LaTeX = self.simpleConversion
            
        elif self.Type == "P" or self.Type == "Python":
            try:
                if self.string.count("=") >= 1 :
                    parts = self.string.split("=")
                    self.LaTeX = ""
                    for i in parts:
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
    
    def Evaluate(self,EvalF):
        #TODO:CALCULATE MORE STUFF
        # https://docs.sympy.org/latest/modules/evalf.html
        # https://docs.sympy.org/latest/modules/solvers/solvers.html
        if self.string.count("=") == 1 :
            if self.Type == "P" or self.Type == "Python":
                try:
                    temp = self.string
                    temp = temp.replace("=" , " - (")
                    temp = temp + ")"
                    ans = sympy.parsing.sympy_parser.parse_expr(temp)
                    ans = sympy.solve(ans)
                    self.Evaluation = "[ "
                    for i in ans:
                        if EvalF:
                            i = i.evalf()
                        self.Evaluation += str(i)
                        self.Evaluation += " , "
                    self.Evaluation = self.Evaluation[:-3]
                    self.Evaluation += " ]"
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            if self.Type == "L" or self.Type == "Latex":
                #TODO
                try:
                    ans = parse_latex(temp)
                    ans = sympy.solve(ans)
                    self.Evaluation = str(ans)
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            self.EvaluationEquation = self.Evaluation + "   <==   "
            self.EvaluationEquation += self.Text
        else:
            if self.Type == "P" or self.Type == "Python":
                try:
                    ans = sympy.parsing.sympy_parser.parse_expr(self.string)
                    if EvalF:
                        ans = ans.evalf()
                    self.Evaluation = str(ans)
                except sympy.SympifyError :
                    self.Evaluation = "Fail"
            if self.Type == "L" or self.Type == "Latex":
                try:
                    ans = parse_latex(self.string)
                    if EvalF:
                        ans = ans.evalf()
                    self.Evaluation = str(ans)
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
