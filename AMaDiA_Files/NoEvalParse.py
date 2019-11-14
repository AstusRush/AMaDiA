# -*- coding: utf-8 -*-
import sys
from codecs import decode

import re
import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy import Matrix, linsolve

if __name__ =="__main__":

    if len(sys.argv) == 2:
        my_str = decode(sys.argv[1], 'unicode_escape')
        with sympy.evaluate(False):
            my_str = parse_expr(my_str,evaluate=False)
        # alternatively you transform it to a bytes obj and
        # then call decode with:
        # my_str = bytes(sys.argv[1], 'utf-8').decode('unicode_escape')
    elif len(sys.argv) == 3:
        my_str = decode(sys.argv[1], 'unicode_escape')
        local_dict = decode(sys.argv[2], 'unicode_escape')
        local_dict = eval(local_dict)
        with sympy.evaluate(False):
            my_str = parse_expr(my_str,evaluate=False,local_dict=local_dict)
    else :
        my_str = 'Error'
    my_str = sympy.latex(my_str)
    print(my_str,end="")