# This Python file uses the following encoding: utf-8

# if__name__ == "__main__":
#     pass

import sys
import subprocess
from PyQt5 import QtWidgets,QtCore,QtGui # Maybe Needs a change of the interpreter of Qt Creator to work there
import socket
import datetime
import time
import platform
import errno
import os
import sympy
import re


from sympy.parsing.sympy_parser import parse_expr

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors


import AMaDiA_Classes as AC
import AMaDiA_ReplacementTables as ART

import importlib

from distutils.spawn import find_executable
if find_executable('latex') and find_executable('dvipng'): LaTeX_dvipng_Installed = True
else : LaTeX_dvipng_Installed = False

def ReloadModules():
    importlib.reload(AC)
    importlib.reload(ART)


# -----------------------------------------------------------------------------------------------------------------

common_exceptions = (TypeError , SyntaxError , sympy.SympifyError ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError)
def ExceptionOutput(exc_info,extraInfo = True):
    try:
        print(cTimeSStr(),":")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        if extraInfo:
            print(exc_type, " in", fname, " line", exc_tb.tb_lineno ,": ", exc_obj)
        else:
            print(exc_type, " in", fname, " line", exc_tb.tb_lineno)
        return str(exc_type)+": "+str(exc_obj)
    except common_exceptions:
        print("An exception occured while trying to print an exception!")

background_Colour = (54/255, 57/255, 63/255)
# -----------------------------------------------------------------------------------------------------------------

def cTimeStr():
    return str(datetime.datetime.now().strftime('%H:%M'))

def cTimeSStr():
    return str(datetime.datetime.now().strftime('%H:%M:%S'))

def cTimeFullStr(seperator = None):
    if seperator == None:
        return str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    else:
        TheFormat = seperator.join(['%Y','%m','%d','%H','%M','%S'])
        return str(datetime.datetime.now().strftime(TheFormat))

def takeFirst(elem):
    return elem[0]
def takeSecond(elem):
    return elem[1]

def FindNthOccurrence(string, tofind, n=1, start=0, end=0):
    # Finds nth occurence of tofind in string between start and end, else returns -1
    if end == 0:
        end = len(string)
    val = start - 1
    for i in range(0, n): 
        val = string.find(tofind, val + 1, end)
        if val == -1:
            return val
    return val


def FindPair(string, AB, start=0, end=0, listlist=ART.LIST_l_normal_pairs): # Version that recognizes all pairs so that it returns -1 for "({)}" when searching for ["(",")"]
    # Finds the first occurence of A and the nth occurence of B with n being the amount of occurence of A between the A and the nth B
    # TODO: DOES NOT WORK IF AT LEAST 2 OPENING TOO MANY
    if end == 0:
        end = len(string)+1
    if start >= end-1 or start<0 or end > len(string)+1 or start<0 or start >= end:
        return(-1,-1)
    Apos = string.find(AB[0], start, end)
    if Apos==-1:
        return(-1,-1)
    if end < 0 or string.find(AB[1], Apos, end) == -1:
        return(Apos,-1)
    tApos = -1
    for k in listlist:
        for o in k:
            index = string.find(o[0], Apos+len(AB[0]), end)
            if not index == -1 and ( tApos == -1 or index < tApos ):
                tApos = index
    if tApos == -1:
        #return FindPair_simple(string,AB,start,end)
        Bpos = string.find(AB[1], Apos+len(AB[0]), end)
        return(Apos, Bpos)
    
    BlockEnd = FindEndOfBlock(string, AB[1], listlist, Apos+len(AB[0]), end)
    if BlockEnd <= start or BlockEnd <= 0 or BlockEnd >= end or BlockEnd==-1:
        return(Apos, -1)
    Bpos = string.find(AB[1], BlockEnd, end)
    return(Apos, Bpos)

def FindEndOfBlock(string, Target, listlist, start=0, end=0):
    if end == 0:
        end = len(string)+1
    if start >= end:
        return start
    tApos = string.find(Target, start, end)
    isEnd = True
    for k in listlist:
        for o in k:
            index = string.find(o[0], start, end)
            if not index == -1 and index <= tApos:
                tApos = index
                isEnd = False
                CurrentPair = o
    if isEnd:
        return start
    nstart = FindPair(string, CurrentPair, start, end, listlist)[1] + len(CurrentPair[1])
    if nstart == -1 or nstart <= start:
        return start
    else:
        return FindEndOfBlock(string, Target, listlist, nstart, end)


def FindPair_simple(string, AB, start=0, end=0):
    # Finds the first occurence of A and the nth occurence of B with n being the amount of occurence of A between the A and the nth B
    if end == 0:
        end = len(string)+1
    Apos = string.find(AB[0], start, end)
    if Apos==-1:
        return(-1,-1)
        
    Bpos = string.find(AB[1], Apos, end)
    As = string.count(AB[0], Apos, Bpos+len(AB[1]))
    if As==0:
        return(Apos, Bpos)
    
    while True:
        Bpos = FindNthOccurrence(string, AB[1], As, Apos, end)
        As = string.count(AB[0], Apos, Bpos+len(AB[1]))
        Bs = string.count(AB[1], Apos, Bpos+len(AB[1]))
        if As==Bs:
            return(Apos, Bpos)
        if Bpos == -1:
            return(Apos, Bpos)

class Counterpart_Result_List:
    def __init__(self,Both):
        self.List = []
        self.Both = Both
        self.FirstResult = None

    def append(self , x):
        self.List.append(x)
        return self
        
    def __getitem__(self, key):
        if self.Both and type(self.FirstResult) == list:
            return self.FirstResult[key]
        else:
            return self.List[key]
    
    def __len__(self):
        return len(self.List)

    def __iadd__(self,value):
        if len(self.List) == 0:
            self.FirstResult = value
        self.List.append(value)
        return self

    def __call__(self):
        return self.FirstResult

    def __repr__(self):
        return self.FirstResult

    def __str__(self):
        return str(self.FirstResult)

    def __contains__(self,keyword): # TODO: Does not work as it opens all internal lists as well...
        return keyword in self.List

    def HalfList(self,Column):
        if self.Both:
            t = []
            for i in self.List:
                t.append(i[Column])
            return t
        else:
            return self.FirstResult
            
def Counterpart(String,ListOfLists=ART.LIST_l_all_pairs,Both=False):
    result = Counterpart_Result_List(Both)
    for i in ListOfLists:
        for j in i:
            if String == j[0]:
                result += j[1] if not Both else j
            elif String == j[1]:
                result += j[0] if not Both else j
    if len(result)>=1:
        return result
    ErrMsg = String+" has no couterpart"
    raise Exception(ErrMsg)
    

# -----------------------------------------------------------------------------------------------------------------

def LaTeX(expr,local_dict=None,evalf=1):
    # This function parses a string into a sympy construct withou evaluating anything!
    
    try:
        expr = Matrix_Encaser(expr)
    except common_exceptions:
        ExceptionOutput(sys.exc_info())

    try:
        if evalf == 2:
            expr = expr.replace("evalf","",1)
            rtnexpr = parse_expr(expr,evaluate=True,local_dict=local_dict)
            rtnexpr = sympy.latex(rtnexpr)
        elif evalf == 1:
            rtnexpr = parse_expr(expr,evaluate=False,local_dict=local_dict)
            rtnexpr = sympy.latex(rtnexpr)

        else:
            try:
                Path = os.path.dirname(__file__)
                if platform.system() == 'Windows':
                    Path += r"\NoEvalParse.py"
                elif platform.system() == 'Linux':
                    Path += r"/NoEvalParse.py"
                rtnexpr = subprocess.check_output([sys.executable, Path, expr])#, local_dict]) # TODO: Make local_dict work
                rtnexpr = rtnexpr.decode("utf8")
            except common_exceptions:
                ExceptionOutput(sys.exc_info())
                rtnexpr = parse_expr(expr,evaluate=False,local_dict=local_dict)
                rtnexpr = sympy.latex(rtnexpr)
    except common_exceptions:
        ExceptionOutput(sys.exc_info())
        rtnexpr = parse_expr(expr,evaluate=True,local_dict=local_dict)
        rtnexpr = sympy.latex(rtnexpr)
    
    return rtnexpr

def Matrix_Encaser(string):
    if "Matrix(" in string:
        Before,Matrix = string.split("Matrix(",1)
        Before = Before + "UnevaluatedExpr(Matrix"
        Matrix = "("+Matrix
        Matrix = Matrix_Encaser(Matrix)
        Close = FindPair(Matrix,["(",")"])[1]
        M,A = Matrix[:Close],Matrix[Close:]
        A = ")"+A
        string = Before+M+A
    return string
    

# -----------------------------------------------------------------------------------------------------------------
# Useful links:
    # https://pypi.org/project/parse/  # New library not in anacona so probably not good to use...
    # https://pyformat.info/
    # https://docs.python.org/3.4/library/string.html

def AstusParse(string,ConsoleOutput = True, Iam = AC.Iam_Normal ,LocalVars = None):
    # TODO:
    # If Iam_Multi_Dim replace everything except multiplication signs
    # Then search with re for the LocalVars
    # Then Parse the multiplication signs in accordance to the position of the LocalVars
    
    string = re.sub(r"√(\w)",r"sqrt(\1)",string)
    string = re.sub(r"(\w*)\'\'\'\'\'\((\w)\)",r"diff(diff(diff(diff(diff(\1(\2),\2),\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\"\"\'\((\w)\)"  ,  r"diff(diff(diff(diff(diff(\1(\2),\2),\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\'\'\'\'\((\w)\)",r"diff(diff(diff(diff(\1(\2),\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\"\"\((\w)\)"  ,  r"diff(diff(diff(diff(\1(\2),\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\'\'\'\((\w)\)",r"diff(diff(diff(\1(\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\"\'\((\w)\)" , r"diff(diff(diff(\1(\2),\2),\2),\2)",string)
    string = re.sub(r"(\w*)\'\'\((\w)\)",r"diff(diff(\1(\2),\2),\2)",string)
    string = re.sub(r"(\w*)\"\((\w)\)" , r"diff(diff(\1(\2),\2),\2)",string)
    string = re.sub(r"(\w*)\'\((\w)\)",r"diff(\1(\2),\2)",string)
    string = re.sub(r"(\w*)\'\'\'\'",r"diff(diff(diff(diff(\1(x),x),x),x),x)",string)
    string = re.sub(r"(\w*)\"\""  ,  r"diff(diff(diff(diff(\1(x),x),x),x),x)",string)
    string = re.sub(r"(\w*)\'\'\'",r"diff(diff(diff(\1(x),x),x),x)",string)
    string = re.sub(r"(\w*)\"\'" , r"diff(diff(diff(\1(x),x),x),x)",string)
    string = re.sub(r"(\w*)\'\'",r"diff(diff(\1(x),x),x)",string)
    string = re.sub(r"(\w*)\"",r"diff(diff(\1(x),x),x)",string)
    string = re.sub(r"(\w*)\'",r"diff(\1(x),x)",string)
    string = re.sub(r"(\w*)\u0308\((\w)\)",r"diff(diff(\1(\2),\2),\2)",string)
    string = re.sub(r"(\w*)\u0307\((\w)\)",r"diff(\1(\2),\2)",string)
    string = re.sub(r"(\w*)\u0308",r"diff(diff(\1(t),t),t)",string)
    string = re.sub(r"(\w*)\u0307",r"diff(\1(t),t)",string)
    string = Replace(string,ART.LIST_n_all)
    string = Replace(string,ART.LIST_r_s_scripts)
    #----
    #---- Temporary Integral Handling for Astus's Integral Syntax
    string = IntegralParser_Astus(string)
    #----
    string = IntegralParser(string)
    string = Derivative_and_IndefiniteIntegral_Parser(string) # Do this after all other integral parsers
    
    
    # Getting rid of not interpreteable brackets
    # string = NonIterpreteableBracketReplace(string)
    
    
    # Add multiplication signs where a human might leave them out
    string = string.replace(")(",")*(") # Add them between brackets
    string = re.sub(r"((?:\d+)|(?:[a-zA-Z]\w*\(\w+\)))((?:[a-zA-Z]\w*)|\()", r"\1*\2", string)

    if ConsoleOutput:
        print("Input parsed: ",string)
    return string

def IntegralParser_Astus(string):
    if "Integral{(" in string:
        Before,From = string.split("Integral{(",1)
        From,To = From.split(")(",1)
        To,Func = To.split(")}",1)
        Func = IntegralParser_Astus(Func) # Find other integrals if there are any and handle them
        Func,After = Func.split("d",1)
        if Func[-1]=="*":
            Func = Func[:-1]
        x = After[0]
        After = After[1:]
        string = Before + " Integral(" + Func + ",("+x+","+From+","+To+"))" + After
    return string
    
def IntegralParser(string):
    #TODO: Make this work for user-defined Syntax
    return string

def Derivative_and_IndefiniteIntegral_Parser(string):
    for i in ART.l_pairs_special_I_D:
        amount = string.count(i[0])
        counter = 0
        if amount > 0:
            start = 0
            while counter < amount:
                Pair = FindPair(string, i,start=start)
                if not Pair[0] == -1 and not Pair[1] == -1:
                    A,B,C = string[:Pair[0]] , string[Pair[0]:Pair[1]] , string[Pair[1]:]
                    B = B.replace(i[0],i[2],1)
                    x,C = C[len(i[1]):len(i[1])+1],C[len(i[1])+1:]
                    B += "," 
                    B += x
                    B += ")"
                    string = A+B
                    string += C
                    counter+=1
                    start = Pair[0]+len(i[0])
                else:
                    break
    return string

def NonIterpreteableBracketReplace(string):
    for i in ART.l_pairs_brackets_not_interpreteable:
        string = string.replace(i[0],"(")
        string = string.replace(i[1],")")
    return string

"""

    for i in ART:
        string.replace(i[0],i[1])
    
"""
"""

    for i in ART:
        for j in i:
            string.replace(j[0],j[1])
    
"""

def AstusParseInverse(string):
    string = Replace(string,ART.n_operators)
    string = Replace(string,ART.n_standard_integrals)
    string = Replace(string,ART.LIST_r_s_scripts,1,0)
    string = Replace(string,ART.LIST_n_invertable,1,0)
        
    #string = string.replace(" * "," · ")
    
    
    
    return string


def Replace(string,List,a=0,b=1):
    # Replaces everything in string that is in List[][a] with List[][b]
    # The List must only contain lists with that all contain at least two strings or Lists that contain such lists
    # Alternatively takes a dictionary and replaces all keys in the string with their Value
    if type(List) == dict:
        for Key, Value in List.items():
            string = string.replace(Key,str(Value))
    elif len(List) > 0 and len(List[0]) > 0:
        if type(List[0][0]) == list:
            for i in List:
                string = Replace(string,i,a,b)
        elif type(List[0][0]) == str:
            for i in List:
                string = string.replace(i[a],i[b])
    return string
# -----------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------

def shape2(Item):
    shape = getattr(Item, "tolist", None)
    if callable(shape):
        try:
            i,j = Item.shape()
        except common_exceptions:
            i,j = Item.shape
    elif shape != None:
        i,j = Item.shape
    else:
        i,j = 1,1
    return i,j

def shape3(Item):
    shape = getattr(Item, "tolist", None)
    if callable(shape):
        try:
            i,j,k = Item.shape()
        except common_exceptions:
            i,j,k = Item.shape
    elif shape != None:
        i,j,k = Item.shape
    else:
        i,j,k = 1,1,1
    return i,j,k
    
# -----------------------------------------------------------------------------------------------------------------

