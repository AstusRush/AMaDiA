# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 12:20:01 2025

@author: Robin
"""


import sys
sys.path.append('..')
from AGeLib import *
import socket
import datetime
import platform
import errno
import os
import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
import warnings

from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
import sympy.matrices.common
from sympy.core.decorators import call_highest_priority

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import scipy


from AMaDiA_Files import AMaDiA_Functions as AF


import importlib
def ReloadModules():
    importlib.reload(AF)


#class Matrix_Engineering(sympy.matrices.matrixbase.MatrixBase):
class Matrix_Engineering(sympy.Matrix):
    """
    This class is an adaptation of sympy.Matrix that behaves more like an engineer would expect,
    I.E. elementwise operations are the default and matrixmultipliaction is signalled using "@" instead of "*"
    and operations with scalars are allowed by simply casting the scalar on all elements, etc.
    
    WIP - Not functional yet!
    
    Not Working yet:
    - Exponents still use matmul
    - Extracting slices might return object of different type
    - There are actually quite a number of cases that could silently convert into a sympy.Matrix ...
    - Product(...) seems to not work correctly
    - addition of a scalar does not work...
    - multiplication with a scalar is not performed (requires a ".doit()" in the inputfield to show the result...)
    - Matmul using the "@" can not be properly displayed in LaTeX
    - I also don't quite understand the display: Usually the result should be left and the input on the right but it is often the other way round...
        This leads me to believe that even when the output looks correctly displayed it actually is not but the LaTeX of the input has been evaluated
        to be the the same as or at least similar to the correct output...
    """
    #@classmethod
    #def _new(cls, *args, **kwargs):
    #    return cls(*args, **kwargs)
    #
    #def _sympy_(self):
    #    return sympy.Matrix(self)
    
    def __matmul__(self, other):
        other = sympy.matrices.common._matrixify(other)
        if not getattr(other, 'is_Matrix', False) and not getattr(other, 'is_MatrixLike', False):
            return NotImplemented
        return super().multiply(other)
        self.__getitem__
    
    def multiply(self, other):
        return super().multiply_elementwise(other)
    
    def multiply_elementwise(self, other):
        if not isinstance(other, Iterable):
            try:
                return self._eval_scalar_mul(other)
            except TypeError:
                return NotImplemented
        if self.shape != other.shape:
            raise sympy.matrices.common.ShapeError("Matrix shapes must agree {} != {}".format(self.shape, other.shape))
        return self._eval_matrix_mul_elementwise(other)
    
    def __add__(self, other):
        if not isinstance(other, Iterable):
            return self._new(self.rows, self.cols, lambda i, j: self[i,j]+other)
        return super().__add__(other)
    
    #def pow(self, exp, method=None): #TODO



