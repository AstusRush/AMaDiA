# -*- coding: utf-8 -*-
import sys
from codecs import decode

import re
import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy import Matrix, linsolve
common_exceptions = (TypeError , SyntaxError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError)

if __name__ =="__main__":
    sympy.init_printing()
    if len(sys.argv) == 2:
        my_str_o = decode(sys.argv[1], 'unicode_escape')
        try:
            with sympy.evaluate(False):
                my_str = parse_expr(my_str_o,evaluate=False)
                my_str = sympy.latex(my_str)
        except common_exceptions:
            # The following may look weird but it totally is!!! It does not work in any other way...
            with sympy.evaluate(True):
                my_str = parse_expr(my_str_o,evaluate=True)
                my_str = sympy.latex(my_str)
            my_str = parse_expr(my_str_o,evaluate=False)
            try:
                my_str = sympy.latex(my_str)
            except common_exceptions:
                with sympy.evaluate(True):
                    my_str = parse_expr(my_str_o,evaluate=False)
                    my_str = sympy.latex(my_str)
        # alternatively you transform it to a bytes obj and
        # then call decode with:
        # my_str = bytes(sys.argv[1], 'utf-8').decode('unicode_escape')
    elif len(sys.argv) == 3:
        my_str_o = decode(sys.argv[1], 'unicode_escape')
        local_dict = decode(sys.argv[2], 'unicode_escape')
        local_dict = eval(local_dict)
        try:
            with sympy.evaluate(False):
                my_str = parse_expr(my_str_o,evaluate=False,local_dict=local_dict)
                my_str = sympy.latex(my_str)
        except common_exceptions:
            with sympy.evaluate(True):
                my_str = parse_expr(my_str_o,evaluate=True,local_dict=local_dict)
                my_str = sympy.latex(my_str)
    else :
        my_str = 'Error'
    sympy.evaluate(True)
    print(my_str,end="")