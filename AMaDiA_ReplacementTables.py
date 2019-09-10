# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:22:05 2019

@author: Robin
"""




# ₁₂₃₄₅₆₇₈₉₀¹²³⁴⁵⁶⁷⁸⁹⁰
# ∫ᵀ√≠≈≙
# ±ħ∈ℝΘτ̅ΨΩΠ̈∂ΣΔΦΓ↓←∞Λ@ ερθζ̲ψωπασδφγ↑→κλ⇐Ξⁿₙ‘ηº×÷—⇔ 


beginning_symbols = ['=','(','{','[']
pairs_brackets = [['(',')'],['[',']'],['{','}']]
pairs_brackets_special = [['<','>']]
pairs_quotation = [["\"","\""],["\'","\'"]]
seperators = [',']

pair_LIST_LIST = [pairs_brackets , pairs_brackets_special , pairs_quotation]

simple_replacements = [
                        ['**', '^'],
                        ['*', ' \\cdot '], ['·', ' \\cdot '],
                        ['math.', ''], ['np.', ''],
                        ['pi', '\\pi'] , ['π', '\\pi'],
                        ['tan', '\\tan'], ['cos', '\\cos'], ['sin', '\\sin'], ['sec', '\\sec'], ['csc', '\\csc']]
complex_replacements =[
                        ['^', '{{{i1}}}^{{{i2}}}'],
                        ['_', '{{{i1}}}_{{{i2}}}'],
                        ['/', '\\frac{{{i1}}}{{{i2}}}'],
                        ['sqrt','\\sqrt{{{i2}}}'], ['√','\\sqrt{{{i2}}}']]