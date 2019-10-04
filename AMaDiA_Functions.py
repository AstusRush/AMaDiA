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


def FindPair(string, AB, start=0, end=0): # TODO: make a version that recognizes all pairs so that it returns -1 for "({)}" when searching for ["(",")"]
    # Finds the first occurence of A and the nth occurence of B with n being the amount of occurence of A between the A and the nth B
    if end == 0:
        end = len(string)+1
    Apos = string.find(AB[0], start, end)
    if Apos==-1:
        return(-1,-1)
        
    Bpos = string.find(AB[1], Apos, end)
    As = string.count(AB[0], Apos, Bpos+1)
    if As==0:
        return(Apos, Bpos)
    
    while True:
        Bpos = FindNthOccurrence(string, AB[1], As, Apos, end)
        As = string.count(AB[0], Apos, Bpos+1)
        Bs = string.count(AB[1], Apos, Bpos+1)
        if As==Bs:
            return(Apos, Bpos)
        if Bpos == -1:
            return(Apos, Bpos)
            
def Counterpart(String):
    for i in ART.LIST_l_all_pairs:
        for j in ART.LIST_l_all_pairs[i]:
            if String == ART.LIST_l_all_pairs[i][j][0]:
                return ART.LIST_l_all_pairs[i][j][1]
            elif String == ART.LIST_l_all_pairs[i][j][1]:
                return ART.LIST_l_all_pairs[i][j][0]
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
    
    
    # Getting rid of not interpreteable brackets
    for i in ART.l_pairs_brackets_not_interpreteable:
        string = string.replace(i[0],"(")
        string = string.replace(i[1],")")
        
    # Add multiplication signs where a human might leave them out
    string = string.replace(")(",")*(") # Add them between brackets
    # TODO: Add them between letters, constants and between numbers and letters and constants
    # https://docs.python.org/3/library/stdtypes.html#str.isalnum
    # 
    
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

