#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
#endregion Import

#region first version

def init_save_lists(self):
    self.save_ignoreNames = []
    self.save_ignoreNamesStartWith = ["_","temp_","save_"]
    self.save_ignoreNamesEndWith = ["__description"]
    self.save_types = ( int, float, complex, str, bool,
                        list, tuple, dict,
                        np.ndarray,
                        )

def save(self, path="", filename="", save=True):
    """
    Save all data in an easily readable format. \n
    An explanation on how to load the data is in the saved file and printed to the console.

    Parameters
    ----------
    `path` (string) must be the path to a directory in which the file should be saved or an empty string (in which case the file will be saved in `savedData`) \n
    `filename` (string) must be the name of the file in which the data will be saved or an empty string (in which case the date and time will be used) \n
    `save` must be a bool. If True (default) the file is saved. If False the file is not saved (but the text that would have been written in the file is still returned).

    Returns
    -------
    `s`: The string that is (or would be) written to the file. \n
    `filePath`: The absolute path of the file in which the data is stored.
    """
    try:
        t   = datetime.datetime.now()
        s1  = "r\"\"\"\nThis file contains the data of an EDFA object and was saved at "+str(t.strftime('%Y.%m.%d-%H:%M:%S'))
        s1 += "\nTo load the data import `load` and call `edfa = load(EDFA.EDFA())` or `edfa = load(EDFA.EDFA)`"
        s2  = "\n\"\"\"\n\nimport numpy as np\nimport inspect\n\n"
        s2 += self.save_createDictString()
        s2 += "\n\n\n\ndef load(edfa):\n    \"\"\"Loads all the values stored in this file into the edfa object.\"\"\"\n    if inspect.isclass(edfa): edfa = edfa()\n    for name,value in TheDictionary.items():\n        setattr(edfa,name,value)\n    return edfa\n\n"
    except:
        print("Could not generate the dictionary string")
        traceback.print_exc()
        return "", ""
    if save:
        try:
            path, filename = str(path), str(filename)
            if path == "":
                normalPath = True
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"savedData")
            else:
                normalPath = False
            if filename == "":
                filename = "EDFA_Data_"+str(t.strftime("_".join(['%Y','%m','%d','%H','%M','%S'])))
            if not filename.endswith(".py"): filename += ".py"
            for i in " ,+-/\\#()[]}{?!\"\'\n~:;<>&%$=`´*@€|":
                if i in filename:
                    filename = filename.replace(i,"_")
            if filename.count(".") > 1 :
                filename = filename.replace(".","_",filename.count(".")-1)
            if filename[0].isnumeric():
                filename = "EDFA_Data_"+filename
            os.makedirs(path,exist_ok=True)
            filePath = os.path.join(path,filename)
            loadFromEverywhere = "```python\nimport EDFA # This import might need adjustment depending on where you are\nimport importlib\nspec = importlib.util.spec_from_file_location(r\"{}\", r\"{}\")\nData = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(Data)\nedfa = Data.load(EDFA.EDFA)\n```".format(str(filename[0:-3]),filePath)
            if normalPath:
                s = s1 + s2
            else:
                s = s1 + "\nTo load the file from anywhere use:\n" + loadFromEverywhere + s2
        except:
            print("Could not save the file")
            traceback.print_exc()
            return s1+s2, ""
        try:
            with open(filePath,'w',encoding="utf-8") as text_file:
                text_file.write(s)
            printString = "Data saved as\"{}\"\nTo load the data use\n".format(filePath)
            if normalPath:
                printString += "```python\nimport EDFA\nfrom savedData.{} import load\nedfa = load(EDFA.EDFA)\n```\nif you are in the EDFA folder. If you are not use\n".format(filename[0:-3])
            printString += loadFromEverywhere 
            print("\n",printString,"\n",sep="")
        except:
            print("Could not save the file as",filePath)
            traceback.print_exc()
            return s, ""
        return s, filePath
    else:
        return s1+s2, ""

def save_createDictString(self):
    """
    Returns a string with valid python code that creates a dictionary which contains all the data of this EDFA object.
    """
    d = {}
    for i in dir(self):
        try:
            exec("d[\"{}\"] = self.{}".format(i,i), globals(), {"self":self,"d":d})
        except:
            print("Could not get",i)
            traceback.print_exc()
    l = []
    for name,value in d.items():
        if ( type(value) in self.save_types and
                not name.startswith(tuple(self.save_ignoreNamesStartWith)) and
                not name.endswith(tuple(self.save_ignoreNamesEndWith)) and
                not name in self.save_ignoreNames ):
            try:
                desc = str(d[name+"__description"])
            except:
                desc = ""
            try:
                value = self._save_formatValue(value)
                l.append([name,value,desc])
            except:
                print("Could not save",name)
                traceback.print_exc()
    return self._save_format_final(l)

def _save_formatValue(self,value):
    """
    Takes `value` that may be of any (supported) type. \n
    Returns a String that contains valid python code that can be executed to create an exact copy of `value` \n
    This Method is used by `save_createDictString`
    """
    if type(value) in (int, float, complex, bool):
        return str(value)
    elif type(value) is str:
        return "\""+value+"\""
    elif type(value) in (list, tuple, np.ndarray):
        s = ""
        isnp = False
        if type(value) is np.ndarray:
            npShape = value.shape
            value = value.tolist() # let's turn it into a list so that str() doesn't cut off numbers
            isnp = True
        if isnp: s += "np.asarray( "
        s += "(" if type(value) is tuple else "["
        if len(value) == 0:
            pass
        elif len(value) == 1:
            s += " "+self._save_formatValue(value[0])+" "
        else:
            if isnp: s += "  # shape: "+str(npShape)
            s += "\n    "
            l = []
            max_len = 0
            for i in value:
                _s = self._save_formatValue(i)
                if len(_s) > max_len: max_len = len(_s)
                l.append(_s)
            if 150/2 > (max_len+3):
                groupSize = int(150/(max_len+3))
                c = 0
                sl = []
                while c < len(l):
                    ci = 0
                    sli = []
                    while ci < groupSize:
                        try:
                            si = l[c+ci]
                            sli.append(si+" "*(max_len-len(si)))
                            ci += 1
                        except: # end of list
                            break
                    sl.append(" , ".join(sli))
                    c += ci
                s += " ,\n    ".join(sl)
            else:
                s += " ,\n    ".join(l)
            s += "\n"
        s += ")" if type(value) is tuple else "]"
        if isnp: s += " )"
        return s
    elif type(value) is dict:
        raise NotImplementedError("dict is not yet supported for saving") #TODO
    else:
        raise NotImplementedError(str(type(value))+" is not supported for saving")

def _save_format_final(self,l):
    """
    Takes a list containing lists containing 3 strings `name` , `value` and `description` . \n
    Returns a string that contains valid python code that creates a dictionary containing the data from the list (the description is used for comments). \n
    This method is used by `save_createDictString`
    """
    s = "TheDictionary = {"
    for i in l:
        #if not i[2] is "":
        s += "\n    # "+i[2]
        s += "\n    \"{}\" : {} ,".format(i[0],i[1].replace("\n","\n    "))
    return s+"\n}"
#endregion first version

#region Code for Imports and Function Definitions
def formatImp(imp, indent=0, indentstr="    "):
    # type: (typing.Dict[str,str],int,str) -> str
    """
    Takes the import dict from `topy` and returns a formatted string that can be written to a file. \n
    indent and indentstr can be given for special use cases but their use should be avoided.
    """
    ret = ""
    for v in imp.values():
        if v.count("\n"): ret += "\n"+indentstr*indent
        ret += indentstr*indent + v.replace("\n","\n"+indentstr*indent) + "\n"+indentstr*indent
        if v.count("\n"): ret += "\n"+indentstr*indent
    return ret

IMP_VERSIONPARSER = [("versionParser","from packaging.version import parse as versionParser")] #CRITICAL: packaging is not a build-in module! There should be some kind of backup in case it is not installed!
IMP_TYPING = [("typing","import typing")]
IMP_NUMPY = [("numpy","import numpy")]
IMP_TEXTWRAP = [("textwrap","import textwrap")]
IMP_QT = [("Qt","""# When AGeLib is imported it automatically adds it's parent directory to the path; therefore this file does not need to \"see\" AGeLib if AGeLib has been imported before in the running program.
from AGeLib import QtCore, QtGui, QtWidgets""")]
IMP_QPALETTE = IMP_QT+IMP_VERSIONPARSER+IMP_TYPING+[("QPalette","""
def loadQPalette(l):
    # type: (typing.List[typing.Tuple[QtGui.QBrush,int,int]]) -> QtGui.QPalette
    # Takes list of tuples with (QtGui.QBrush, ColorRole, ColorGroup)
    Palette = QtGui.QPalette()
    for i in l:
        if i[1] == 20:
            if versionParser(QtCore.qVersion())>=versionParser("5.12"):
                Palette.setBrush(i[2],QtGui.QPalette.PlaceholderText,i[0])
        else:
            Palette.setBrush(i[2],i[1],i[0])
    return Palette
""")] #CRITICAL: Instead of using versionParser we should use Qt's version parser!

#endregion Code for Imports and Function Definitions
#region Constants and Lookups
LIMIT_CHAR_ROW = 150
QBRUSH_STYLES = {
    0  : ("QtCore.Qt.NoBrush" , QtCore.Qt.NoBrush),
    1  : ("QtCore.Qt.SolidPattern" , QtCore.Qt.SolidPattern),
    2  : ("QtCore.Qt.Dense1Pattern" , QtCore.Qt.Dense1Pattern),
    3  : ("QtCore.Qt.Dense2Pattern" , QtCore.Qt.Dense2Pattern),
    4  : ("QtCore.Qt.Dense3Pattern" , QtCore.Qt.Dense3Pattern),
    5  : ("QtCore.Qt.Dense4Pattern" , QtCore.Qt.Dense4Pattern),
    6  : ("QtCore.Qt.Dense5Pattern" , QtCore.Qt.Dense5Pattern),
    7  : ("QtCore.Qt.Dense6Pattern" , QtCore.Qt.Dense6Pattern),
    8  : ("QtCore.Qt.Dense7Pattern" , QtCore.Qt.Dense7Pattern),
    9  : ("QtCore.Qt.HorPattern" , QtCore.Qt.HorPattern),
    10 : ("QtCore.Qt.VerPattern" , QtCore.Qt.VerPattern),
    11 : ("QtCore.Qt.CrossPattern" , QtCore.Qt.CrossPattern),
    12 : ("QtCore.Qt.BDiagPattern" , QtCore.Qt.BDiagPattern),
    13 : ("QtCore.Qt.FDiagPattern" , QtCore.Qt.FDiagPattern),
    14 : ("QtCore.Qt.DiagCrossPattern" , QtCore.Qt.DiagCrossPattern),
    15 : ("QtCore.Qt.LinearGradientPattern" , QtCore.Qt.LinearGradientPattern),
    17 : ("QtCore.Qt.ConicalGradientPattern" , QtCore.Qt.ConicalGradientPattern),
    16 : ("QtCore.Qt.RadialGradientPattern" , QtCore.Qt.RadialGradientPattern),
    24 : ("QtCore.Qt.TexturePattern" , QtCore.Qt.TexturePattern),
}
QPALETTE_COLORROLE = {
    0  : ("QtGui.QPalette.WindowText" , QtGui.QPalette.WindowText) ,
    1  : ("QtGui.QPalette.Button" , QtGui.QPalette.Button) ,
    2  : ("QtGui.QPalette.Light" , QtGui.QPalette.Light) ,
    3  : ("QtGui.QPalette.Midlight" , QtGui.QPalette.Midlight) ,
    4  : ("QtGui.QPalette.Dark" , QtGui.QPalette.Dark) ,
    5  : ("QtGui.QPalette.Mid" , QtGui.QPalette.Mid) ,
    6  : ("QtGui.QPalette.Text" , QtGui.QPalette.Text) ,
    7  : ("QtGui.QPalette.BrightText" , QtGui.QPalette.BrightText) ,
    8  : ("QtGui.QPalette.ButtonText" , QtGui.QPalette.ButtonText) ,
    9  : ("QtGui.QPalette.Base" , QtGui.QPalette.Base) ,
    10 : ("QtGui.QPalette.Window" , QtGui.QPalette.Window) ,
    11 : ("QtGui.QPalette.Shadow" , QtGui.QPalette.Shadow) ,
    12 : ("QtGui.QPalette.Highlight" , QtGui.QPalette.Highlight) ,
    13 : ("QtGui.QPalette.HighlightedText" , QtGui.QPalette.HighlightedText) ,
    14 : ("QtGui.QPalette.Link" , QtGui.QPalette.Link) ,
    15 : ("QtGui.QPalette.LinkVisited" , QtGui.QPalette.LinkVisited) ,
    16 : ("QtGui.QPalette.AlternateBase" , QtGui.QPalette.AlternateBase) ,
    17 : ("QtGui.QPalette.NoRole" , QtGui.QPalette.NoRole) ,
    18 : ("QtGui.QPalette.ToolTipBase" , QtGui.QPalette.ToolTipBase) ,
    19 : ("QtGui.QPalette.ToolTipText" , QtGui.QPalette.ToolTipText) ,
}
if versionParser(QtCore.qVersion())>=versionParser("5.12"):
    QPALETTE_COLORROLE[20] = ("20" , QtGui.QPalette.PlaceholderText)

QPALETTE_COLORGROUP = {
    0  : ("QtGui.QPalette.Active" , QtGui.QPalette.Active) ,
    1  : ("QtGui.QPalette.Disabled" , QtGui.QPalette.Disabled) ,
    2  : ("QtGui.QPalette.Inactive" , QtGui.QPalette.Inactive) ,
}
#endregion Constants and Lookups

#region Base Functions
def format_(code, imp):
    # type: (str,typing.Dict[str,str]) -> str
    """
    Takes code and imp as returned by topy and returns them combined as a string.
    """
    ret = formatImp(imp)
    ret += "\n"+code+"\n"
    return ret
    
def formatObject(value, name="", ignoreNotImplemented = False):
    # type: (typing.Any,str,bool) -> str
    """
    This is the same as `format_(*_topy(value,name, ignoreNotImplemented = ignoreNotImplemented))`
    """
    return format_(*_topy(value,name, ignoreNotImplemented = ignoreNotImplemented))

def writeToFile(code, imp, path):
    # type: (str,typing.Dict[str,str],str) -> None
    """
    Takes the return values from `topy` and saves everything as a file at the given path. \n
    (There are no checks for the path. These must be performed before calling this function.)
    """
    raise NotImplementedError() #CRITICAL: TODO

#NOTE: Not all these types are supported yet but they are at least planned!
SUPPORTED_TYPES = (
    int, float, complex, str, bool,
    list, tuple, dict,
    np.ndarray,
    QtGui.QColor,QtGui.QBrush,QtGui.QPalette,
    plt.Axes )

def topy(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (typing.Any, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    """
    Takes `value` that may be of any (supported) type. \n
    Returns a String that contains valid python code that can be executed to create an exact copy of `value`
    and a dictionary that uses the names of the required modules as keys and code to import these modules as values
    (if Qt is a required module AGeLib must have been imported before executing/importing the code as the import relies on it). \n
    Raises `NotImplementedError` if the datatype is not supported. \n
    If `ignoreNotImplemented` is True, not supported datatypes will be ignored. \n
    If `name` is given the returned code will begin with `name = `, otherwise the code will not assign the value to a variable. \n
    `indent` is the indentationlevel at which the code should be and `indentstr` is the string that is used for each indentationlevel (should be either 4 spaces (default) or `\\t`). \n
    NOTE: matplotlib.pyplot.Axes will be saved as a function that takes an axes as an argument and plots the stored content on the axes. (It does not clear the Axes.) \n
    NOTE: The returned string always ends with a new line. If you don't want the new line use `_topy` instead. \n
    NOTE: The code in the returned module dict does not end with a new line. \n
    If an object has the method `tocode_AGeLib` it will be called to generate the code.
    This method must take the arguments name, indent, and indentstr and return a str and a dict (just like this function).
    """
    ret, imp = _topy(value,name,indent,indentstr)
    return ret+"\n", imp

def _topy(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (typing.Any, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    """
    This function is the same as `topy` but it does not append a new line at the end.
    """
    try:
        # Custom
        if hasattr(value,"tocode_AGeLib"):
            ret, imp = value.tocode_AGeLib(name,indent,indentstr)
        # Basic
        elif isinstance(value, (int, float, complex, bool)):
            ret, imp = _topy_num(value,name,indent,indentstr) #return str(value)
        elif isinstance(value, str):
            ret, imp = _topy_str(value,name,indent,indentstr) #return "\""+value+"\""
        # Iterables
        elif isinstance(value, (list, tuple)) or (numpyImported and isinstance(value, np.ndarray)):
            ret, imp = _topy_iter(value,name,indent,indentstr)
        elif isinstance(value, dict):
            ret, imp = _topy_dict(value,name,indent,indentstr)
        # Qt Colours
        elif isinstance(value, QtGui.QColor):
            ret, imp = _topy_QColor(value,name,indent,indentstr)
        elif isinstance(value, QtGui.QBrush):
            ret, imp = _topy_QBrush(value,name,indent,indentstr)
        elif isinstance(value, QtGui.QGradient):
            ret, imp = _topy_QGradient(value,name,indent,indentstr)
        elif isinstance(value, QtGui.QPalette):
            ret, imp = _topy_QPalette(value,name,indent,indentstr)
        # Other
        elif matplotlibImported and isinstance(value, plt.Axes):
            raise NotImplementedError("matplotlib.pyplot.Axes is not yet supported for saving") #TODO: _topy_mplAxes
        #
        else:
            raise NotImplementedError(str(type(value))+" is not supported for saving")
        #
        return ret, imp
    except NotImplementedError as inst:
        if ignoreNotImplemented: return "", {}
        else: raise inst
        

def _topy_num(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (typing.Union[int, float, complex, bool], str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += str(value)
    return ret, {}

def _topy_str(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (str, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    ret = indentstr*indent
    if name:
        ret += name + " = "
    if value.count("\n"):
        imp.update(IMP_TEXTWRAP)
        lines = value.splitlines()
        ret += "textwrap.dedent(\"\"\"\\\n"
        for i in lines:
            ret += indentstr*(indent+1) + i.replace("\\","\\\\").replace("\"","\\\"") + "\n"
        ret += indentstr*indent+"\"\"\")"
        if value[-1]!="\n": ret+="[0:-1]"
    else:
        ret += "\""+value.replace("\\","\\\\").replace("\"","\\\"")+"\""
    return ret, imp

def _topy_dict(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (dict, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += "{\n"
    for k,v in value.items():
        rk, ik = _topy(k,"",indent+1,indentstr)
        rv, iv = _topy(v,"",indent+2,indentstr)
        # The indentation is there in case of multiline strings and strip removes tabs and spaces from the beginning (and end) of the value string.
        ret += rk + " : " + rv.strip(" ").strip("\t") + " ,\n"
        imp.update(ik)
        imp.update(iv)
    ret += indentstr*indent + "}"
    return ret, imp

def _topy_iter(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (typing.Union[list,tuple,np.ndarray], str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    ret = indentstr*indent
    if name:
        ret += name + " = "
    if numpyImported and type(value) is np.ndarray:
        npShape = value.shape
        value = value.tolist() # let's turn it into a list so that str() doesn't cut off numbers
        ret += "numpy.asarray( "
        imp.update(IMP_NUMPY)
        isnp = True
    else:
        isnp = False
    ret += "(" if type(value) is tuple else "["
    if len(value) == 0:
        pass
    elif len(value) == 1:
        r, i = _topy(value[0],"",0,indentstr)
        if r.count("\n"):
            r = r.replace("\n",("\n"+indentstr*(indent+1)))
            ret += "\n"+r+" ,\n"+indentstr*indent
        else:
            ret += " "+r+", "
        imp.update(i)
    else:
        if isnp: ret += "  # shape: "+str(npShape)
        ret += "\n" + indentstr*(indent+1)
        l = []
        max_len = 0
        for v in value:
            r, i = _topy(v,"",0,indentstr)
            if r.count("\n"):
                r = r.replace("\n",("\n"+indentstr*(indent+1)))
                max_len = -1
            elif  max_len >= 0 and len(r) > max_len:
                max_len = len(r)
            l.append(r)
            imp.update(i)
        if max_len > 0 and LIMIT_CHAR_ROW/2 > (max_len+3):
            groupSize = int(150/(max_len+3))
            c = 0
            sl = []
            while c < len(l):
                ci = 0
                sli = []
                while ci < groupSize:
                    try:
                        si = l[c+ci]
                        sli.append(si+" "*(max_len-len(si)))
                        ci += 1
                    except: # end of list
                        break
                sl.append(" , ".join(sli))
                c += ci
            ret += (" ,\n"+indentstr*(indent+1)).join(sl)
        else:
            ret += (" ,\n"+indentstr*(indent+1)).join(l)
        ret += " ,\n"+indentstr*indent
    ret += ")" if type(value) is tuple else "]"
    if isnp: ret += " )"
    return ret, imp

def _topy_QColor(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (QtGui.QColor, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    imp.update(IMP_QT)
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += "QtGui.QColor({},{},{},{})".format(value.red(),value.green(),value.blue(),value.alpha())
    return ret, imp
    
def _topy_QBrush(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (QtGui.QBrush, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    #NOTE: texture is currently not supported and can not be (at least not easily...)
    imp = {}
    imp.update(IMP_QT)
    ret = indentstr*indent
    if name:
        ret += name + " = "
    if int(value.style()) not in QBRUSH_STYLES.keys():
        if ignoreNotImplemented: return "", {}
        raise NotImplementedError("The QBrush Style {} is not supported for saving".format(int(value.style())))
    if int(value.style()) not in (15,16,17):
        ret += "QtGui.QBrush({},{})".format(_topy_QColor(value.color())[0],QBRUSH_STYLES[int(value.style())][0]) # casting value.style() to int is required because of PyQt6 and possible thanks to AGeQt
    else: # gradient
        #TODO: gradient is currently not supported but should be
        # https://doc.qt.io/qt-5/qbrush.html
        # Qt provides three different gradients: QLinearGradient, QConicalGradient, and QRadialGradient - all of which inherit QGradient.
        r,i = _topy_QGradient(value.gradient())
        ret += "QtGui.QBrush({})".format(r)
        imp.update(i)
    if int(value.style()) == 24 :
        if ignoreNotImplemented: return "", {}
        raise NotImplementedError("QtCore.Qt.TexturePattern for QtGui.QBrush is not supported for saving")
    return ret, imp
    
def _topy_QGradient(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False): #TODO: _topy_QGradient
    # type: (QtGui.QGradient|QtGui.QLinearGradient|QtGui.QConicalGradient|QtGui.QRadialGradient, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    #TODO: QGradient has NO getter function for the colours. There are still some ways to implement this:
    #   1- When saving, make a QPixmap with the gradient and read all the colours from that in some reasonable interval
    #       https://stackoverflow.com/questions/3306786/get-intermediate-color-from-a-gradient/29280443
    #       https://www.qtcentre.org/threads/14307-How-to-get-the-specified-position-s-QColor-in-QLinearGradient
    #           and https://www.qtcentre.org/threads/49693-How-to-get-color-of-pixel-or-point
    #   2- QVariantAnimation.keyValueAt might be able to extreact the information if QGradient can get loaded into it.
    #       https://stackoverflow.com/questions/3306786/get-intermediate-color-from-a-gradient/29280443
    #   3- The colours could be saved separately for every gradient but this would mean that saving only works with the information but not with an actual QGradient.
    #           So one would probably make an AGeGradient that stores the information and only AGeGradients could be saved. This in turn would require an AGeBrush and AGePalette to store the AGeGradients explicitley...
    #               Or one is lucky and QBrush and QPalette actually return the AGeGradient... But I doubt it somehow...
    # 
    # 1 is the most versatile but not the most runtime-efficient
    # 2 might be more runtime-efficient which is of some importance but I am not certain of this and it is still questionable if this approach even works
    # 3 would be the most runtime-efficient and the most precise and accurate but is less compatible and requires more infrastructure
    # 3 is the best for the palette saving but 1/2 is the best for AGeToPy
    # -> 3 is the best approach since it is the best option for saving several colour themes with multiple gradients as it has no precision loss and the fastest runtime
    #
    #
    #REMINDER: These object must be created using a lot of method calls which can not be done inside a dict.
    #           Therefore a dict with strings of all necessary values should be given to a constructor of a custom function for code.
    #           The import dict should contain one entry for the Qt import and one entry with a function that takes a dict and turns it into the required datatype.
    #           NOTE: if a function uses a module that is imported after the function is defined there is no problem as long as the function is called after the module is imported.
    #               Therefore the order of imports and function definitions does not matter as long as it all comes before the code part.
    if ignoreNotImplemented: return "", {}
    raise NotImplementedError("QtGui.QGradient is not yet supported for saving")
    imp = {}
    imp.update(IMP_QT)
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += str(value) ####
    return ret, imp
    
def _topy_QPalette(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (QtGui.QPalette, str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    imp.update(IMP_QPALETTE)
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += "loadQPalette([\n"
    for kr,vr in QPALETTE_COLORROLE.items():
        for kg,vg in QPALETTE_COLORGROUP.items():
            r,i = _topy_QBrush(value.brush(vg[1],vr[1]))
            imp.update(i)
            ret += "{}( {} , {} , {} ),\n".format(indentstr*(indent+1), r, vr[0], vg[0])
    ret += indentstr*indent + "])"
    return ret, imp
#region Base Functions

def _topy_(value, name="", indent=0, indentstr="    ", ignoreNotImplemented = False):
    # type: (typing.Union[int, float, complex, bool], str, int, str, bool) -> tuple[str, typing.Dict[str,str]]
    imp = {}
    ret = indentstr*indent
    if name:
        ret += name + " = "
    ret += str(value) ####
    return ret, imp

