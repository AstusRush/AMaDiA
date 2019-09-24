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

common_exceptions = (TypeError , SyntaxError , sympy.SympifyError ,  AttributeError , ValueError , NotImplementedError , Exception)
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

# -----------------------------------------------------------------------------------------------------------------

def cTimeStr():
    return str(datetime.datetime.now().strftime('%H:%M'))

def cTimeSStr():
    return str(datetime.datetime.now().strftime('%H:%M:%S'))

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

def AstusParse(string):
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
    if len(List) > 0 and len(List[0]) > 0:
        if type(List[0][0]) == list:
            for i in List:
                string = Replace(string,i,a,b)
        elif type(List[0][0]) == str:
            for i in List:
                string = string.replace(i[a],i[b])
    return string
# -----------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------

def Convert_to_LaTeX(toConvert):
    # Conversion Stuff:
        #TODO: keep sympy.parsing.sympy_parser.parse_expr() in mind!!!
    # TODO : Make A file with dicts which contain a conversion scheme
    
    # TODO: Make a Loop that converts
    
    toConvert = command_to_latex(toConvert)
    return toConvert
# 11.07.2019 from http://efavdb.com/simple-python-to-latex-parser/
# Converts some numpy, math and python commands to LaTeX
# ₁₂₃₄₅₆₇₈₉₀¹²³⁴⁵⁶⁷⁸⁹⁰
# ∫ᵀ√≠≈≙
# ±ħ∈ℝΘτ̅ΨΩΠ̈∂ΣΔΦΓ↓←∞Λ@ ερθζ̲ψωπασδφγ↑→κλ⇐Ξⁿₙ‘ηº×÷—⇔ 

def parse_simple_eqn(q):
    """ Return TeX equivalent of a command 
    without parentheses. """
    # Define replacement rules.
    simple_replacements = [[' ', ''],
                           ['**', '^'], ['*', ' \\cdot '],
                           ['·', ' \\cdot '],
                           ['math.', ''], ['np.', ''],
                           ['pi', '\\pi'] , ['π', '\\pi'],
                           ['tan', '\\tan'],
                           ['cos', '\\cos'], ['sin', '\\sin'],
                           ['sec', '\\sec'], ['csc', '\\csc']]
    complex_replacements = [['^', '{{{i1}}}^{{i2}}'],
                           ['_', '{{{i1}}}_{{{i2}}}'],
                           ['/', '\\frac{{{i1}}}{{{i2}}}'],
                           ['sqrt','\\sqrt{{{i2}}}'],
                           ['√','\\sqrt{{{i2}}}']]
    # Carry out simple replacements
    for pair in simple_replacements:
        q = q.replace(pair[0], pair[1])
    # Now complex replacements
    for item in ['*', '·', '/', '+', '-', '^', '_', ',', 'sqrt', '√']:
        q = q.replace(item, ' ' + item + ' ')
    q_split = q.split()
    for index, item in enumerate(q_split):
        for pair in complex_replacements:
            if item == pair[0]:
                if item == 'sqrt' or item == '√':
                    match_str = " ".join(q_split[index:index+2])
                else:
                    match_str = " ".join(q_split[index-1:index+2])
                q = q.replace(match_str, pair[1].format(
                    i1=q_split[index-1], i2=q_split[index+1]))
    return q
 
def command_to_latex(q, index=0):
    """ Recursively eliminate parentheses. Once
    removed, apply parse_simple_eqn.        """
    open_index, close_index = -1, -1
    for q_index, i in enumerate(q):
        if i == '(':
            open_index = q_index
        elif i == ')':
            close_index = q_index
            break
    if open_index != -1:
        o = q[:open_index] + '@' + str(index) + q[close_index + 1:]
        m = q[open_index + 1:close_index]
        o_tex  = command_to_latex(o, index + 1)
        m_tex  = command_to_latex(m, index + 1)
        # Clean up redundant parentheses at recombination
        r_index = o_tex.find('@' + str(index))
        if o_tex[r_index - 1] == '{':
            return o_tex.replace('@'+str(index), m_tex)
        else:
            return o_tex.replace('@'+str(index), 
                                 ' \\left (' + m_tex + ' \\right )')
    else:
        return parse_simple_eqn(q)
    
# -----------------------------------------------------------------------------------------------------------------

