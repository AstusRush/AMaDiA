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

l_pairs_special = [["sqrt(",")"],["√(",")"],["log(",")"],["ln(",")"],["ld(",")"],["log2(",")"],["log10(",")"]]
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
                ["η₀","376.730313412"]] #CRITICAL: Is is also only temporary and is oft rounded to 377
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


#
UNICODE_TO_LATEX_direct_replacements_symbols = [
    ["\u2000",r"\;"],
    ["\u00ac",r"\neg"],
    ["\u00b7",r"\cdot"],
    ["\u00d7",r"\times"],
    ["\u0393",r"\Gamma"],
    ["\u0394",r"\Delta"],
    ["\u0398",r"\Theta"],
    ["\u039b",r"\Lambda"],
    ["\u039e",r"\Xi"],
    ["\u03a0",r"\Pi"],
    ["\u03a3",r"\Sigma"],
    ["\u03a6",r"\Phi"],
    ["\u03a8",r"\Psi"],
    ["\u03a9",r"\Omega"],
    ["\u03b1",r"\alpha"],
    ["\u03b2",r"\beta"],
    ["\u03b3",r"\gamma"],
    ["\u03b4",r"\delta"],
    ["\u03b5",r"\varepsilon"],
    ["\u03b6",r"\zeta"],
    ["\u03b7",r"\eta"],
    ["\u03b8",r"\theta"],
    ["\u03b9",r"\iota"],
    ["\u03ba",r"\kappa"],
    ["\u03bb",r"\lambda"],
    ["\u03bc",r"\mu"],
    ["\u03bd",r"\nu"],
    ["\u03be",r"\xi"],
    ["\u03c0",r"\pi"],
    ["\u03c1",r"\rho"],
    ["\u03c2",r"\varsigma"],
    ["\u03c3",r"\sigma"],
    ["\u03c4",r"\tau"],
    ["\u03c5",r"\upsilon"],
    ["\u03c6",r"\varphi"],
    ["\u03c7",r"\chi"],
    ["\u03c8",r"\psi"],
    ["\u03c9",r"\omega"],
    ["\u2013",r"--"],
    ["\u2014",r"---"],
    ["\u2018",r"`"],
    ["\u2019",r"'"],
    ["\u201c",r"``"],
    ["\u201d",r"''"],
    ["\u2020",r"\dagger"],
    ["\u2026",r"\ldots"],
    ["\u2080",r"_0"],
    ["\u2081",r"_1"],
    ["\u2082",r"_2"],
    ["\u2083",r"_3"],
    ["\u2084",r"_4"],
    ["\u2085",r"_5"],
    ["\u2086",r"_6"],
    ["\u2087",r"_7"],
    ["\u2088",r"_8"],
    ["\u2089",r"_9"],
    ["\u2099",r"_n"],
    ["\u2070",r"^{0}"],
    ["\u00b9",r"^{1}"],
    ["\u207b",r"^{-1}"],
    ["\u00b2",r"^{2}"],
    ["\u00b3",r"^{3}"],
    ["\u2074",r"^{4}"],
    ["\u2075",r"^{5}"],
    ["\u2076",r"^{6}"],
    ["\u2077",r"^{7}"],
    ["\u2078",r"^{8}"],
    ["\u2079",r"^{9}"],
    ["\u207f",r"^{n}"],
    ["\u1d40",r"^{\text{T}}"],
    ["\u2113",r"\ell"],
    ["\u214b",r"\parr"],
    ["\u2190",r"\leftarrow"],
    ["\u2191",r"\uparrow"],
    ["\u2192",r"\rightarrow"],
    ["\u2193",r"\downarrow"],
    ["\u2194",r"\leftrightarrow"],
    ["\u21a6",r"\mapsto"],
    ["\u21aa",r"\hookrightarrow"],
    ["\u21c4",r"\rightleftarrows"],
    ["\u21c6",r"\leftrightarrows"],
    ["\u21d0",r"\Leftarrow"],
    ["\u21d1",r"\Uparrow"],
    ["\u21d2",r"\Rightarrow"],
    ["\u21d3",r"\Downarrow"],
    ["\u21d4",r"\Leftrightarrow"],
    ["\u21dd",r"\rightsquigarrow"],
    ["\u2200",r"\forall"],
    ["\u2203",r"\exists"],
    ["\u2205",r"\varnothing"],
    ["\u2208",r"\in"],
    ["\u2209",r"\notin"],
    ["\u220b",r"\ni"],
    ["\u220c",r"\not\ni"],
    ["\u2216",r"\setminus"],
    ["\u2217",r"\star"],
    ["\u2218",r"\circ"],
    ["\u221e",r"\infty"],
    ["\u2227",r"\wedge"],
    ["\u2228",r"\vee"],
    ["\u2229",r"\cap"],
    ["\u222a",r"\cup"],
    ["\u222b",r"\int"],
    ["\u2238",r"\dot -"],
    ["\u2243",r"\simeq"],
    ["\u2245",r"\cong"],
    ["\u2248",r"\approx"],
    ["\u225c",r"\triangleq"],
    ["\u2260",r"\ne"],
    ["\u2261",r"\equiv"],
    ["\u2264",r"\le"],
    ["\u2265",r"\ge"],
    ["\u2272",r"\lesssim"],
    ["\u227a",r"\prec"],
    ["\u227b",r"\succ"],
    ["\u227e",r"\precsim"],
    ["\u2282",r"\subset"],
    ["\u2283",r"\supset"],
    ["\u2284",r"\notsubset"],
    ["\u2285",r"\notsupset"],
    ["\u2286",r"\subseteq"],
    ["\u2287",r"\supseteq"],
    ["\u2288",r"\notsubseteq"],
    ["\u2289",r"\notsupseteq"],
    ["\u228a",r"\subsetneq"],
    ["\u228b",r"\supsetneq"],
    ["\u228f",r"\sqsubset"],
    ["\u2290",r"\sqsupset"],
    ["\u2291",r"\sqsubseteq"],
    ["\u2293",r"\sqcap"],
    ["\u2294",r"\sqcup"],
    ["\u2295",r"\oplus"],
    ["\u2296",r"\ominus"],
    ["\u2297",r"\otimes"],
    ["\u2298",r"\oslash"],
    ["\u2299",r"\odot"],
    ["\u229a",r"\circledcirc"],
    ["\u229b",r"\circledast"],
    ["\u229d",r"\circleddash"],
    ["\u229e",r"\boxplus"],
    ["\u229f",r"\boxminus"],
    ["\u22a0",r"\boxtimes"],
    ["\u22a1",r"\boxdot"],
    ["\u22a2",r"\vdash"],
    ["\u22a4",r"\top"],
    ["\u22a5",r"\bot"],
    ["\u22d6",r"\lessdot"],
    ["\u22d7",r"\gtrdot"],
    ["\u22ee",r"\vdots"],
    ["\u22ef",r"\cdots"],
    ["\u22f0",r"\iddots"],
    ["\u22f1",r"\ddots"],
    ["\u2610",r"\phantom{{\checkmark}}"],
    ["\u2611",r"\checkmark"],
    ["\u2713",r"\checkmark"],
    ["\u27e8",r"\langle"],
    ["\u27e9",r"\rangle"],
    ["\u27ea",r"\llangle"],
    ["\u27eb",r"\rrangle"],
    ["\u2aa8",r"\trianglelefteqslant"],
    ["\u2aa9",r"\trianglerighteqslant"],
    ["\u2aaf",r"\preceq"],
    ["\u2ab0",r"\succeq"],
    ["\u301a",r"\llbracket"],
    ["\u301b",r"\rrbracket"],
    ["\u1f329",r"\lightning"],
]
r""" # AGeIDEScript to convert from LaTeX commands to the table above
display()
out = []
for i in a.splitlines():
    if not i: continue
    try:
        x = i.strip(r"\DeclareUnicodeCharacter{")
        if r"\fbox" in x:
            x,y = x.split(r"}{\fbox{\ensuremath{")
            y = y[:-3]
        elif r"\ensuremath{" in x:
            x,y = x.split(r"}{\ensuremath{")
            y = y[:-2]
        else:
            x,y = x.split(r"}{")
            y = y[:-1]
        out.append([r"\u"+x.lower(),y])
    except:
        dpl(i)
dpl("[")
for i in out:
    dpl("    [\"",i[0].replace(r"\\","\\"),"\",r\"",i[1].replace(r"\\","\\"),"\"],",sep="")
dpl("]")
"""

UNICODE_TO_LATEX_direct_replacements_letters = [
    ["\u1d538",r"\mathbb{A}"],
    ["\u1d539",r"\mathbb{B}"],
    ["\u2102",r"\mathbb{C}"],
    ["\u1d53b",r"\mathbb{D}"],
    ["\u1d53c",r"\mathbb{E}"],
    ["\u1d53d",r"\mathbb{F}"],
    ["\u1d53e",r"\mathbb{G}"],
    ["\u210d",r"\mathbb{H}"],
    ["\u1d540",r"\mathbb{I}"],
    ["\u1d541",r"\mathbb{J}"],
    ["\u1d542",r"\mathbb{K}"],
    ["\u1d543",r"\mathbb{L}"],
    ["\u1d544",r"\mathbb{M}"],
    ["\u2115",r"\mathbb{N}"],
    ["\u1d546",r"\mathbb{O}"],
    ["\u2119",r"\mathbb{P}"],
    ["\u211a",r"\mathbb{Q}"],
    ["\u211d",r"\mathbb{R}"],
    ["\u1d54a",r"\mathbb{S}"],
    ["\u1d54b",r"\mathbb{T}"],
    ["\u1d54c",r"\mathbb{U}"],
    ["\u1d54d",r"\mathbb{V}"],
    ["\u1d54e",r"\mathbb{W}"],
    ["\u1d54f",r"\mathbb{X}"],
    ["\u1d550",r"\mathbb{Y}"],
    ["\u2124",r"\mathbb{Z}"],
    ["\u1d400",r"\mathbf{A}"],
    ["\u1d41a",r"\mathbf{a}"],
    ["\u1d401",r"\mathbf{B}"],
    ["\u1d41b",r"\mathbf{b}"],
    ["\u1d402",r"\mathbf{C}"],
    ["\u1d41c",r"\mathbf{c}"],
    ["\u1d403",r"\mathbf{D}"],
    ["\u1d41d",r"\mathbf{d}"],
    ["\u1d404",r"\mathbf{E}"],
    ["\u1d41e",r"\mathbf{e}"],
    ["\u1d405",r"\mathbf{F}"],
    ["\u1d41f",r"\mathbf{f}"],
    ["\u1d406",r"\mathbf{G}"],
    ["\u1d420",r"\mathbf{g}"],
    ["\u1d407",r"\mathbf{H}"],
    ["\u1d421",r"\mathbf{h}"],
    ["\u1d408",r"\mathbf{I}"],
    ["\u1d422",r"\mathbf{i}"],
    ["\u1d409",r"\mathbf{J}"],
    ["\u1d423",r"\mathbf{j}"],
    ["\u1d40a",r"\mathbf{K}"],
    ["\u1d424",r"\mathbf{k}"],
    ["\u1d40b",r"\mathbf{L}"],
    ["\u1d425",r"\mathbf{l}"],
    ["\u1d40c",r"\mathbf{M}"],
    ["\u1d426",r"\mathbf{m}"],
    ["\u1d40d",r"\mathbf{N}"],
    ["\u1d427",r"\mathbf{n}"],
    ["\u1d40e",r"\mathbf{O}"],
    ["\u1d428",r"\mathbf{o}"],
    ["\u1d40f",r"\mathbf{P}"],
    ["\u1d429",r"\mathbf{p}"],
    ["\u1d410",r"\mathbf{Q}"],
    ["\u1d42a",r"\mathbf{q}"],
    ["\u1d411",r"\mathbf{R}"],
    ["\u1d42b",r"\mathbf{r}"],
    ["\u1d412",r"\mathbf{S}"],
    ["\u1d42c",r"\mathbf{s}"],
    ["\u1d413",r"\mathbf{T}"],
    ["\u1d42d",r"\mathbf{t}"],
    ["\u1d414",r"\mathbf{U}"],
    ["\u1d42e",r"\mathbf{u}"],
    ["\u1d415",r"\mathbf{V}"],
    ["\u1d42f",r"\mathbf{v}"],
    ["\u1d416",r"\mathbf{W}"],
    ["\u1d430",r"\mathbf{w}"],
    ["\u1d417",r"\mathbf{X}"],
    ["\u1d431",r"\mathbf{x}"],
    ["\u1d418",r"\mathbf{Y}"],
    ["\u1d432",r"\mathbf{y}"],
    ["\u1d419",r"\mathbf{Z}"],
    ["\u1d433",r"\mathbf{z}"],
    ["\u1d4d0",r"\mathcal{A}"],
    ["\u1d4d1",r"\mathcal{B}"],
    ["\u1d4d2",r"\mathcal{C}"],
    ["\u1d4d3",r"\mathcal{D}"],
    ["\u1d4d4",r"\mathcal{E}"],
    ["\u1d4d5",r"\mathcal{F}"],
    ["\u1d4d6",r"\mathcal{G}"],
    ["\u1d4d7",r"\mathcal{H}"],
    ["\u1d4d8",r"\mathcal{I}"],
    ["\u1d4d9",r"\mathcal{J}"],
    ["\u1d4da",r"\mathcal{K}"],
    ["\u1d4db",r"\mathcal{L}"],
    ["\u1d4dc",r"\mathcal{M}"],
    ["\u1d4dd",r"\mathcal{N}"],
    ["\u1d4de",r"\mathcal{O}"],
    ["\u1d4df",r"\mathcal{P}"],
    ["\u1d4e0",r"\mathcal{Q}"],
    ["\u1d4e1",r"\mathcal{R}"],
    ["\u1d4e2",r"\mathcal{S}"],
    ["\u1d4e3",r"\mathcal{T}"],
    ["\u1d4e4",r"\mathcal{U}"],
    ["\u1d4e5",r"\mathcal{V}"],
    ["\u1d4e6",r"\mathcal{W}"],
    ["\u1d4e7",r"\mathcal{X}"],
    ["\u1d4e8",r"\mathcal{Y}"],
    ["\u1d4e9",r"\mathcal{Z}"],
    ["\u1d434",r"\mathit{A}"],
    ["\u1d44e",r"\mathit{a}"],
    ["\u1d435",r"\mathit{B}"],
    ["\u1d44f",r"\mathit{b}"],
    ["\u1d436",r"\mathit{C}"],
    ["\u1d450",r"\mathit{c}"],
    ["\u1d437",r"\mathit{D}"],
    ["\u1d451",r"\mathit{d}"],
    ["\u1d438",r"\mathit{E}"],
    ["\u1d452",r"\mathit{e}"],
    ["\u1d439",r"\mathit{F}"],
    ["\u1d453",r"\mathit{f}"],
    ["\u1d43a",r"\mathit{G}"],
    ["\u1d454",r"\mathit{g}"],
    ["\u1d43b",r"\mathit{H}"],
    ["\u210e",r"\mathit{h}"],
    ["\u1d43c",r"\mathit{I}"],
    ["\u1d456",r"\mathit{i}"],
    ["\u1d43d",r"\mathit{J}"],
    ["\u1d457",r"\mathit{j}"],
    ["\u1d43e",r"\mathit{K}"],
    ["\u1d458",r"\mathit{k}"],
    ["\u1d43f",r"\mathit{L}"],
    ["\u1d459",r"\mathit{l}"],
    ["\u1d440",r"\mathit{M}"],
    ["\u1d45a",r"\mathit{m}"],
    ["\u1d441",r"\mathit{N}"],
    ["\u1d45b",r"\mathit{n}"],
    ["\u1d442",r"\mathit{O}"],
    ["\u1d45c",r"\mathit{o}"],
    ["\u1d443",r"\mathit{P}"],
    ["\u1d45d",r"\mathit{p}"],
    ["\u1d444",r"\mathit{Q}"],
    ["\u1d45e",r"\mathit{q}"],
    ["\u1d445",r"\mathit{R}"],
    ["\u1d45f",r"\mathit{r}"],
    ["\u1d446",r"\mathit{S}"],
    ["\u1d460",r"\mathit{s}"],
    ["\u1d447",r"\mathit{T}"],
    ["\u1d461",r"\mathit{t}"],
    ["\u1d448",r"\mathit{U}"],
    ["\u1d462",r"\mathit{u}"],
    ["\u1d449",r"\mathit{V}"],
    ["\u1d463",r"\mathit{v}"],
    ["\u1d44a",r"\mathit{W}"],
    ["\u1d464",r"\mathit{w}"],
    ["\u1d44b",r"\mathit{X}"],
    ["\u1d465",r"\mathit{x}"],
    ["\u1d44c",r"\mathit{Y}"],
    ["\u1d466",r"\mathit{y}"],
    ["\u1d44d",r"\mathit{Z}"],
    ["\u1d467",r"\mathit{z}"],
    ["\u1d49c",r"\mathscr{A}"],
    ["\u212c",r"\mathscr{B}"],
    ["\u1d49e",r"\mathscr{C}"],
    ["\u1d49f",r"\mathscr{D}"],
    ["\u2130",r"\mathscr{E}"],
    ["\u2131",r"\mathscr{F}"],
    ["\u1d4a2",r"\mathscr{G}"],
    ["\u210b",r"\mathscr{H}"],
    ["\u2110",r"\mathscr{I}"],
    ["\u1d4a5",r"\mathscr{J}"],
    ["\u1d4a6",r"\mathscr{K}"],
    ["\u2112",r"\mathscr{L}"],
    ["\u2133",r"\mathscr{M}"],
    ["\u1d4a9",r"\mathscr{N}"],
    ["\u1d4aa",r"\mathscr{O}"],
    ["\u1d4ab",r"\mathscr{P}"],
    ["\u1d4ac",r"\mathscr{Q}"],
    ["\u211b",r"\mathscr{R}"],
    ["\u1d4ae",r"\mathscr{S}"],
    ["\u1d4af",r"\mathscr{T}"],
    ["\u1d4b0",r"\mathscr{U}"],
    ["\u1d4b1",r"\mathscr{V}"],
    ["\u1d4b2",r"\mathscr{W}"],
    ["\u1d4b3",r"\mathscr{X}"],
    ["\u1d4b4",r"\mathscr{Y}"],
    ["\u1d4b5",r"\mathscr{Z}"],
    ["\u1d504",r"\mathfrak{A}"],
    ["\u1d51e",r"\mathfrak{a}"],
    ["\u1d505",r"\mathfrak{B}"],
    ["\u1d51f",r"\mathfrak{b}"],
    ["\u1d520",r"\mathfrak{c}"],
    ["\u1d507",r"\mathfrak{D}"],
    ["\u1d521",r"\mathfrak{d}"],
    ["\u1d508",r"\mathfrak{E}"],
    ["\u1d522",r"\mathfrak{e}"],
    ["\u1d509",r"\mathfrak{F}"],
    ["\u1d523",r"\mathfrak{f}"],
    ["\u1d50a",r"\mathfrak{G}"],
    ["\u1d524",r"\mathfrak{g}"],
    ["\u1d525",r"\mathfrak{h}"],
    ["\u1d526",r"\mathfrak{i}"],
    ["\u1d50d",r"\mathfrak{J}"],
    ["\u1d527",r"\mathfrak{j}"],
    ["\u1d50e",r"\mathfrak{K}"],
    ["\u1d528",r"\mathfrak{k}"],
    ["\u1d50f",r"\mathfrak{L}"],
    ["\u1d529",r"\mathfrak{l}"],
    ["\u1d510",r"\mathfrak{M}"],
    ["\u1d52a",r"\mathfrak{m}"],
    ["\u1d511",r"\mathfrak{N}"],
    ["\u1d52b",r"\mathfrak{n}"],
    ["\u1d512",r"\mathfrak{O}"],
    ["\u1d52c",r"\mathfrak{o}"],
    ["\u1d513",r"\mathfrak{P}"],
    ["\u1d52d",r"\mathfrak{p}"],
    ["\u1d514",r"\mathfrak{Q}"],
    ["\u1d52e",r"\mathfrak{q}"],
    ["\u1d52f",r"\mathfrak{r}"],
    ["\u1d516",r"\mathfrak{S}"],
    ["\u1d530",r"\mathfrak{s}"],
    ["\u1d517",r"\mathfrak{T}"],
    ["\u1d531",r"\mathfrak{t}"],
    ["\u1d518",r"\mathfrak{U}"],
    ["\u1d532",r"\mathfrak{u}"],
    ["\u1d519",r"\mathfrak{V}"],
    ["\u1d533",r"\mathfrak{v}"],
    ["\u1d51a",r"\mathfrak{W}"],
    ["\u1d534",r"\mathfrak{w}"],
    ["\u1d51b",r"\mathfrak{X}"],
    ["\u1d535",r"\mathfrak{x}"],
    ["\u1d51c",r"\mathfrak{Y}"],
    ["\u1d536",r"\mathfrak{y}"],
    ["\u1d537",r"\mathfrak{z}"],
]
r""" # AGeIDEScript to convert from LaTeX commands to the table above
display()
out = []
for i in a.splitlines():
    if not i: continue
    try:
        x = i.replace(r"\DeclareUnicodeInv{\ensuremath{","")
        x,y = x.split(r"}}{")
        y = y[:-1]
        out.append([r"\u"+y.lower(),x])
    except:
        dpl(i)
dpl("[")
for i in out:
    dpl("    [\"",i[0].replace(r"\\","\\"),"\",r\"",i[1].replace(r"\\","\\"),"\"],",sep="")
dpl("]")
"""

UNICODE_TO_LATEX_direct_replacements = [UNICODE_TO_LATEX_direct_replacements_symbols, UNICODE_TO_LATEX_direct_replacements_letters]


# ---------------------------------- MASTERLISTS M_ ----------------------------------

M_pair_LIST_LIST_LIST = [LIST_l_all_pairs]



# ---------------------------------- _ ----------------------------------
