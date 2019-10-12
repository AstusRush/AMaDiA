# This Python file uses the following encoding: utf-8

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

common_exceptions = (TypeError , SyntaxError , sympy.SympifyError ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError)
def ExceptionOutput(exc_info,extraInfo = True):
    try:
        print(cTimeSStr(),":")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        if extraInfo:
            print(exc_type, " in", fname, " line", exc_tb.tb_lineno ,": ", exc_obj)
        else:
            print(exc_type, " in", fname, " line", exc_tb.tb_lineno)
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
    if end == 0:
        end = len(string)+1
    Apos = string.find(AB[0], start, end)
    if Apos==-1:
        return(-1,-1)
    tApos = -1
    for k in listlist:
        for o in k:
            index = string.find(o[0], start, end)
            if not index == -1 and ( tApos == -1 or index < tApos ):
                tApos = index
    if tApos == -1:
        return FindPair_simple(string,AB,start,end)
    
    BlockEnd = FindEndOfBlock(string, AB[1], listlist, Apos+len(AB[0]), end)
    Bpos = string.find(AB[1], BlockEnd, end)
    return(Apos, Bpos)

def FindEndOfBlock(string, Target, listlist, start=0, end=0):
    if end == 0:
        end = len(string)+1
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
    start = FindPair(string, CurrentPair, start, end, listlist)[1] + len(CurrentPair[1])
    return FindEndOfBlock(string, Target, listlist, start, end)

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
            
def Counterpart(String,ListOfLists=ART.LIST_l_all_pairs,Both=False):
    for i in ListOfLists:
        for j in i:
            if String == j[0]:
                return j[1] if not Both else j
            elif String == j[1]:
                return j[0] if not Both else j
    ErrMsg = String+" has no couterpart"
    raise Exception(ErrMsg)
    

# -----------------------------------------------------------------------------------------------------------------
# Useful links:
    # https://pypi.org/project/parse/  # New library not in anacona so probably not good to use...
    # https://pyformat.info/
    # https://docs.python.org/3.4/library/string.html

def AstusParse(string,ConsoleOutput = True):
    string = Replace(string,ART.LIST_n_all)
    string = Replace(string,ART.LIST_r_s_scripts)
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
        if i[0] in string:
            Pair = FindPair(string, i)
            if not Pair[0] == -1 and not Pair[1] == -1:
                A,B,C = string[:Pair[0]] , string[Pair[0]:Pair[1]] , string[Pair[1]:]
                B = B.replace(i[0],i[2],1)
                x,C = C[len(i[1]):len(i[1])+1],C[len(i[1])+1:]
                B += "," 
                B += x
                B += ")"
                string = A+B
                string += C
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

