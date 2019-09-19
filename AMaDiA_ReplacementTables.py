# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:22:05 2019

@author: Robin
"""




# ₁₂₃₄₅₆₇₈₉₀¹²³⁴⁵⁶⁷⁸⁹⁰ # DONE singular
# ∫ᵀ√≠≈≙
# ±ħ∈ℝΘτ̅ΨΩΠ̈∂ΣΔΦΓ↓←∞Λ@ ερθζ̲ψωπασδφγ↑→κλ⇐Ξⁿₙ‘ηº×÷—⇔ 


# ---------------------------------- Lists l_ ----------------------------------

l_beginning_symbols = ['=','(','{','[']
l_pairs_brackets = [['(',')'],['[',']'],['{','}']]
l_pairs_brackets_special = [['<','>']]
l_pairs_quotation = [["\"","\""],["\'","\'"]]
l_seperators = [',']

LIST_l_all_pairs = [l_pairs_brackets , l_pairs_brackets_special , l_pairs_quotation]


# ---------------------------------- Normal Replacements n_ ----------------------------------

n_standard = [["integral","Integral"],["Integrate","Integral"],["integrate","Integral"],["int ","Integral"],["Int ","Integral"]]
n_greek_letters = [["π"," pi "],["λ"," lamda "]]
n_constants = [["π"," pi "]]
n_operators = [["^","**"],["·","*"]]
n_operators_notinv = [["—","-"],["×","*"],["÷","/"]]
n_space = [[" "," "]]

LIST_n_all = [n_standard , n_greek_letters , n_constants , n_operators , n_operators_notinv , n_space]

n_greek_letters_nospace = [["π","pi"],["λ","lamda"]]
n_constants_nospace = [["π"," pi "]]
LIST_n_invertable = [n_greek_letters_nospace , n_constants_nospace , n_operators]
# ---------------------------------- Special Replacements s_ ----------------------------------

s_constants_math = [["i"," I "],["e"," E "]]
s_constants_engineering = [["j"," I "],["e"," E "]]

# ---------------------------------- Replacements Simple to Python r_s_ ----------------------------------

r_s_superscript_numbers = [["¹","**(1)"],["²","**(2)"],["³","**(3)"],["⁴","**(4)"],["⁵","**(5)"],["⁶","**(6)"],["⁷","**(7)"],["⁸","**(8)"],["⁹","**(9)"],["⁰","**(0)"]]
r_s_subscript_numbers = [["₁","_1"],["₂","_2"],["₃","_3"],["₄","_4"],["₅","_5"],["₆","_6"],["₇","_7"],["₈","_8"],["₉","_9"],["₀","_0"]]
r_s_superscript_letters = [["ⁿ","**(n)"]]
r_s_subscript_letters = [["ₙ","_n"]]

LIST_r_s_scripts = [r_s_superscript_numbers , r_s_subscript_numbers , r_s_superscript_letters , r_s_subscript_letters]

r_s_operators = [["√","sqrt"],["∫","Integral"]]

# ---------------------------------- Replacements Complex to Python r_c_ ----------------------------------

# number refferences number of parts in addition to symbol replacement
r_c_operators_1 = [["√",""]]
r_c_operators_2 = [[]]
r_c_operators_3 = [["Σ",""],["Π",""]]
r_c_operators_4 = [
                    ["∫",""], # 1: from 2: to 3: f(x) 4: dx
                    []]


# ---------------------------------- PYTHON_TO_LATEX_ ----------------------------------

PYTHON_TO_LATEX_simple_replacements = [
                        ['**', '^'],
                        ['*', ' \\cdot '], ['·', ' \\cdot '],
                        ['math.', ''], ['np.', ''],
                        ['pi', '\\pi'] , ['π', '\\pi'],
                        ['tan', '\\tan'], ['cos', '\\cos'], ['sin', '\\sin'], ['sec', '\\sec'], ['csc', '\\csc']]
PYTHON_TO_LATEX_complex_replacements =[
                        ['^', '{{{i1}}}^{{{i2}}}'],
                        ['_', '{{{i1}}}_{{{i2}}}'],
                        ['/', '\\frac{{{i1}}}{{{i2}}}'],
                        ['sqrt','\\sqrt{{{i2}}}'], ['√','\\sqrt{{{i2}}}']]
