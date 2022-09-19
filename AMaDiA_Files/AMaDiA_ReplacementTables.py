# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:22:05 2019

@author: Robin
"""
import sys
sys.path.append('..')
from AGeLib import *
Qt = QtCore.Qt

# ---------------------------------- Keyboard Remapper KR_ ----------------------------------

KR_Map = [
    # Sorted for German Keyboard but mostly compatible with all Keyboards
    # Note that not all Symbols are currently supported
    # This is my custom Layout for my Linux Laptop
    #Normal
        #Shift
            #AltGr
                #AltGr+Shift
                    # ^
                        # Qt Key
    # Line 1 (Numbers)
    ["^","°","′","″"," ",Qt.Key_Dead_Circumflex],
    ["1","!","∫","₁","¹",Qt.Key_1],         [" ","!"," ","₁"," ",Qt.Key_Exclam],
    ["2","\"","ᵀ","₂","²",Qt.Key_2],       [" ","\""," ","₂"," ",Qt.Key_QuoteDbl],     [" ","\"","ᵀ","₂","²",Qt.Key_twosuperior],
    ["3","§","√","₃","³",Qt.Key_3],         [" ","§"," ","₃"," ",Qt.Key_paragraph],     [" ","§","√","₃","³",Qt.Key_threesuperior],
    ["4","$","\u2260","₄","⁴",Qt.Key_4],    [" ","$"," ","₄"," ",Qt.Key_Dollar],
    ["5","%","≈","₅","⁵",Qt.Key_5],         [" ","%"," ","₅"," ",Qt.Key_Percent],
    ["6","&","≙","₆","⁶",Qt.Key_6],         [" ","&"," ","₆"," ",Qt.Key_Ampersand],
    ["7","/","{","₇","⁷",Qt.Key_7],         [" ","/"," ","₇"," ",Qt.Key_Slash],
    ["8","(","[","₈","⁸",Qt.Key_8],         [" ","("," ","₈"," ",Qt.Key_ParenLeft],
    ["9",")","]","₉","⁹",Qt.Key_9],         [" ",")"," ","₉"," ",Qt.Key_ParenRight],
    ["0","=","}","₀","⁰",Qt.Key_0],         [" ","="," ","₀"," ",Qt.Key_Equal],
    ["ß","?","\\","¿"," ",Qt.Key_ssharp],
    ["´","`","≤","≥"," ",Qt.Key_acute],
    # Line 2 (QWERTZ...)
    ["q","Q","@","±"," ",Qt.Key_Q],
    ["w","W",r" ",r"ħ","ʷ",Qt.Key_W],
    ["e","E","ε","∈","ᵉ",Qt.Key_E],
    ["r","R","ρ","ℝ","ʳ",Qt.Key_R],
    ["t","T","θ","Θ","ᵗ",Qt.Key_T],
    ["z","Z","ζ","τ","ᶻ",Qt.Key_Z],
    ["u","U","\u0332","\u0305","ᵘ",Qt.Key_U],
    ["i","I","ψ","Ψ","ⁱ",Qt.Key_I],
    ["o","O","ω","Ω","ᵒ",Qt.Key_O],
    ["p","P","π","Π","ᵖ",Qt.Key_P],
    ["ü","Ü","\u0307","\u0308","ᵞ",Qt.Key_Udiaeresis],
    ["plus","*"," "," ","⁺",Qt.Key_Plus],
    # Line 3 (ASD...)
    ["a","A","α","∂","ᵃ",Qt.Key_A],
    ["s","S","σ","Σ","ˢ",Qt.Key_S],
    ["d","D","δ","Δ","ᵈ",Qt.Key_D],
    ["f","F","φ","Φ","ᶠ",Qt.Key_F],
    ["g","G","γ","Γ","ᵍ",Qt.Key_G],
    ["h","H","↑","↓","ʰ",Qt.Key_H],
    ["j","J","→","←","ʲ",Qt.Key_J],
    ["k","K","κ","∞","ᵏ",Qt.Key_K],
    ["l","L","λ","Λ","ˡ",Qt.Key_L],
    ["ö","Ö","\u005E"," ","ᵝ",Qt.Key_Odiaeresis],
    ["ä","Ä","↳","\u0303","ᵅ",Qt.Key_Adiaeresis],
    ["#",r"'","’"," ","ᵟ",Qt.Key_NumberSign],
    # Line 4 (YXC...)
    ["<",">","|","⇔"," ",Qt.Key_Less],                  [" ",">","|","⇔"," ",Qt.Key_Greater],
    ["y","Y","⇒","⇐","ʸ",Qt.Key_Y],
    ["x","X","ξ","Ξ","ˣ",Qt.Key_X],
    ["c","C","ℂ","ⁿ","ᶜ",Qt.Key_C],
    ["v","V","\u20D7","ₙ","ᵛ",Qt.Key_V],
    ["b","B","β"," ","ᵇ",Qt.Key_B],
    ["n","N","ν","η","ⁿ",Qt.Key_N],
    ["m","M","\u03bc"," ","ᵐ",Qt.Key_M],                [" ","M","\u03bc"," "," ",Qt.Key_mu],
    ["comma",";","\u22C5","\u00D7","⁽",Qt.Key_Comma],   [" ",";","\u22C5","\u00D7","⁽",Qt.Key_Semicolon],
    [".",":","…","÷","⁾",Qt.Key_Period],                [" ",":","…","÷","⁾",Qt.Key_Colon],
    ["-","_","–","—","⁻",Qt.Key_Minus],                 [" ","_","–","—","⁻",Qt.Key_Underscore]]

# ---------------------------------- Lists l_ ----------------------------------

l_beginning_symbols = ['=','(','{','[']
l_pairs_brackets = [['(',')'],['[',']'],['{','}']]
l_pairs_brackets_special = [['<','>']]
l_pairs_brackets_not_interpretable = [['{','}'],['[',']']]
l_pairs_quotation = [["\"","\""],["\'","\'"]]
#CLEANUP: Clean this up...:
l_pairs_special_I_D = [["Integral","d","Integral("],["d(",")/d","diff("],["∂(",")/∂","diff("]]
l_pairs_special_I_D_all_Integrals = [["Integral","d","Integral("],["d(",")/d","diff("],["∂(",")/∂","diff("],["integral","d","Integral("],
                                ["Integrate","d","Integral("],["integrate","d","Integral("],["int ","d","Integral("],["Int ","d","Integral("],["∫","d","Integral("]]
l_pairs_special_I_D_Unicode = [["∫","d","Integral("],["d(",")/d","diff("],["∂(",")/∂","diff("]]

l_pairs_special = [["sqrt(",")"],["√(",")"]]
l_separators = [',']

LIST_l_normal_pairs = [l_pairs_brackets , l_pairs_special_I_D_all_Integrals , l_pairs_special]
LIST_l_normal_pairs_Unicode = [l_pairs_brackets , l_pairs_special_I_D_Unicode , l_pairs_special]
LIST_l_all_pairs = [l_pairs_brackets , l_pairs_brackets_special , l_pairs_quotation , l_pairs_special_I_D , l_pairs_special]


# ---------------------------------- Normal Replacements n_ ----------------------------------

n_standard = [["",""]]
n_standard_integrals = [["integral","Integral"],["Integrate","Integral"],["integrate","Integral"],["int ","Integral"],["Int ","Integral"],["∫","Integral"]]
n_greek_letters = [["\u0391"," Alpha "],["\u03b1"," alpha "],
                   ["\u0392"," Beta "],["\u03b2"," beta "],
                   ["\u0393"," Gamma "],["\u03b3"," gamma "],
                   ["\u0394"," Delta "],["\u03b4"," delta "],
                   ["\u0395"," Epsilon "],["\u03b5"," epsilon "],
                   ["\u0396"," Zeta "],["\u03b6"," zeta "],
                   ["\u0397"," Eta "],["\u03b7"," eta "],
                   ["\u0398"," Theta "],["\u03b8"," theta "],
                   ["\u0399"," Iota "],["\u03b9"," iota "],
                   ["\u039a"," Kappa "],["\u03ba"," kappa "],
                   ["\u039b"," Lamda "],["\u03bb"," lamda "], # Lambda is a function in sympy so they spell the letter lamda
                   ["\u039c"," Mu "],["\u03bc"," mu "],["µ"," mu "],
                   ["\u039d"," Nu "],["\u03bd"," nu "],
                   ["\u039e"," Xi "],["\u03be"," xi "],
                   ["\u039f"," Omicron "],["\u03bf"," omicron "],
                   ["\u03a0"," Pi "],["\u03c0"," pi "],
                   ["\u03a1"," Rho "],["\u03c1"," rho "],
                   ["\u03a3"," Sigma "],["\u03c3"," sigma "],
                   ["\u03a4"," Tau "],["\u03c4"," tau "],
                   ["\u03a5"," Upsilon "],["\u03c5"," upsilon "],
                   ["\u03a6"," Phi "],["\u03c6"," phi "],
                   ["\u03a7"," chi "],["\u03c7"," chi "], #Capital Chi is a function in sympy!!! Converting into lower case chi instead
                   ["\u03a8"," Psi "],["\u03c8"," psi "],
                   ["\u03a9"," Omega "],["\u03c9"," omega "]
                   ]
n_greek_letters_nospace = [["\u0391","Alpha"],["\u03b1","alpha"],
                   ["\u0392","Beta"],["\u03b2","beta"],
                   ["\u0393","Gamma"],["\u03b3","gamma"],
                   ["\u0394","Delta"],["\u03b4","delta"],
                   ["\u0395","Epsilon"],["\u03b5","epsilon"],
                   ["\u0396","Zeta"],["\u03b6","zeta"],
                   ["\u0397","Eta"],["\u03b7","eta"],
                   ["\u0398","Theta"],["\u03b8","theta"],
                   ["\u0399","Iota"],["\u03b9","iota"],
                   ["\u039a","Kappa"],["\u03ba","kappa"],
                   ["\u039b","Lamda"],["\u03bb","lamda"], # Lambda is a function in sympy so they spell the letter lamda
                   ["\u039c","Mu"],["\u03bc","mu"],["µ"," mu "],
                   ["\u039d","Nu"],["\u03bd","nu"],
                   ["\u039e","Xi"],["\u03be","xi"],
                   ["\u039f","Omicron"],["\u03bf","omicron"],
                   ["\u03a0","Pi"],["\u03c0","pi"],
                   ["\u03a1","Rho"],["\u03c1","rho"],
                   ["\u03a3","Sigma"],["\u03c3","sigma"],
                   ["\u03a4","Tau"],["\u03c4","tau"],
                   ["\u03a5","Upsilon"],["\u03c5","upsilon"],
                   ["\u03a6","Phi"],["\u03c6","phi"],
                   ["\u03a7","chi"],["\u03c7","chi"], #Capital Chi is a function in sympy!!! Converting into lower case chi instead
                   ["\u03a8","Psi"],["\u03c8","psi"],
                   ["\u03a9","Omega"],["\u03c9","omega"]
                   ]
n_constants = [["\u03c0"," pi "],["∞"," oo "], #]
                ["c₀","299792458"],["ε₀","(8.8541878128*10**(-12))"],["µ₀","(1.25663706212*10**(-6))"], #CRITICAL: This is only temporary but should be implemented in a more permanent but toggleable way with optional units
                ["η₀","377"]] #CRITICAL: Is is also only temporary but this is also not as precise as the other ones (this is the value so that my solutions match the official solutions of my uni)
n_operators = [["^","**"],["\u22C5","*"]]
n_operators_special = [["√","sqrt"],["∫","Integral"]]
n_operators_notinv = [["–","-"],["—","-"],["\u00B7","*"],["×","*"],["÷","/"],["°C","degC"],["°F","*5/9*degC-32*5/9*degC"],["/°","*(360/pi/2)"],["°","/(360/pi/2)"]]
n_operators_dual = [["±","+","-"],["∓","-","+"]]
n_space = [[" "," "]]

n_priority_Invertable = [["°C","*degC"],["°C","degC"],["°F","*5/9*degC-32*5/9*degC"],["/°","*(360/pi/2)"],["°","/(360/pi/2)"]]

LIST_n_all = [n_standard_integrals , n_constants , n_greek_letters_nospace , n_operators , n_operators_special , n_operators_notinv , n_space]

n_constants_nospace = [["π"," pi "]]
LIST_n_invertable = [n_priority_Invertable , n_operators , n_operators_special]
# ---------------------------------- Special Replacements s_ ----------------------------------

s_constants_math = [["i","I"],["e","E"]]
s_constants_engineering = [["j","I"],["e","E"]]

# ---------------------------------- Replacements Simple to Python r_s_ ----------------------------------

r_s_superscript_numbers_neg = [["⁻¹","**(-1)"],["⁻²","**(-2)"],["⁻³","**(-3)"],["⁻⁴","**(-4)"],["⁻⁵","**(-5)"],["⁻⁶","**(-6)"],["⁻⁷","**(-7)"],["⁻⁸","**(-8)"],["⁻⁹","**(-9)"],["⁻⁰","**(-0)"]]
r_s_superscript_numbers = [["¹","**(1)"],["²","**(2)"],["³","**(3)"],["⁴","**(4)"],["⁵","**(5)"],["⁶","**(6)"],["⁷","**(7)"],["⁸","**(8)"],["⁹","**(9)"],["⁰","**(0)"]]
r_s_subscript_numbers = [["₁","_1"],["₂","_2"],["₃","_3"],["₄","_4"],["₅","_5"],["₆","_6"],["₇","_7"],["₈","_8"],["₉","_9"],["₀","_0"]]
r_s_superscript_letters = [["ⁿ","**(n)"],["ᵀ",".T"]]
r_s_subscript_letters = [["ₙ","_n"]]

LIST_r_s_scripts = [r_s_superscript_numbers_neg, r_s_superscript_numbers , r_s_subscript_numbers , r_s_superscript_letters , r_s_subscript_letters]



# ---------------------------------- Replacements Complex to Python r_c_ ----------------------------------

# number references number of parts in addition to symbol replacement
r_c_operators_1 = [["√",""]]
r_c_operators_2 = [[]]
r_c_operators_3 = [["Σ",""],["Π",""]]
r_c_operators_4 = [
                    ["∫",""], # 1: from 2: to 3: f(x) 4: dx
                    []]


# ---------------------------------- PYTHON_TO_LATEX_ ----------------------------------

PYTHON_TO_LATEX_simple_replacements = [
                        ['**', '^'],
                        ['*', ' \\cdot '], ['·', ' \\cdot '], ['\u22C5', ' \\cdot '],
                        ['math.', ''], ['np.', ''],
                        ['pi', '\\pi'] , ['π', '\\pi'],
                        ['tan', '\\tan'], ['cos', '\\cos'], ['sin', '\\sin'], ['sec', '\\sec'], ['csc', '\\csc']]
PYTHON_TO_LATEX_complex_replacements =[
                        ['^', '{{{i1}}}^{{{i2}}}'],
                        ['_', '{{{i1}}}_{{{i2}}}'],
                        ['/', '\\frac{{{i1}}}{{{i2}}}'],
                        ['sqrt','\\sqrt{{{i2}}}'], ['√','\\sqrt{{{i2}}}']]

# ---------------------------------- MASTERLISTS M_ ----------------------------------

M_pair_LIST_LIST_LIST = [LIST_l_all_pairs]



# ---------------------------------- _ ----------------------------------
