
#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, NC
from ._AGeFunctions import *
#from ._AGeWidgets import *
from . import _AGeWidgets as AGeWidgets
#endregion Import

import math
import typing
import weakref

#region Helper Functions
def roundToN(x,n):
    return x if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))
#endregion Helper Functions

#region Typewidgets
class _TypeWidget(AGeWidgets.TightGridWidget):
    def __init__(self, parent: 'QtWidgets.QWidget') -> None:
        super().__init__(parent=parent)
    
    def get(self):
        raise NotImplementedError(f"{type(self)} has not implemented `get`, yet!")
    
    def set(self):
        raise NotImplementedError(f"{type(self)} has not implemented `set`, yet!")
    
    def copyFrom(self, other):
        raise NotImplementedError(f"{type(self)} has not implemented `copyFrom`, yet!")
    
    def __call__(self):
        return self.get()

class Int(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:int, min_:int=None, max_:int=None, unit="") -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.SpinBox = self.addWidget(QtWidgets.QSpinBox(self),0,1)
        if unit:
            self.SpinBox.setSuffix(f" {unit}")
        if min_:
            self.SpinBox.setMinimum(min_)
        if max_:
            self.SpinBox.setMaximum(max_)
        self.SpinBox.setValue(default)
    
    def get(self) -> int:
        return self.SpinBox.value()
    
    def __call__(self) -> int:
        return self.get()
    
    def set(self, value:int):
        self.SpinBox.setValue(value)
    
    def copyFrom(self, other:'Int'):
        self.SpinBox.setValue(other.SpinBox.value())

class Float(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:float, min_:float=None, max_:float=None, unit="", precise=False) -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        if precise:
            self.SpinBox = self.addWidget(QtWidgets.QDoubleSpinBox(self),0,1)
            self.SpinBox.setDecimals(15)
        else:
            self.SpinBox = self.addWidget(DoubleSpinBox(self),0,1)
            self.SpinBox.setDecimals(10)
            try:
                try:
                    self.SpinBox.setStepType(self.SpinBox.AdaptiveDecimalStepType)
                except:
                    self.SpinBox.setStepType(self.SpinBox.StepType.AdaptiveDecimalStepType)
            except:
                ExceptionOutput()
        if unit:
            self.SpinBox.setSuffix(f" {unit}")
        if min_:
            self.SpinBox.setMinimum(min_)
        if max_:
            self.SpinBox.setMaximum(max_)
        self.SpinBox.setValue(default)
    
    def get(self) -> float:
        return self.SpinBox.value()
    
    def __call__(self) -> float:
        return self.get()
    
    def set(self, value:float):
        self.SpinBox.setValue(value)
    
    def copyFrom(self, other:'Float'):
        self.SpinBox.setValue(other.SpinBox.value())

class Bool(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:bool) -> None:
        super().__init__(parent)
        self.Checkbox = self.addWidget(QtWidgets.QCheckBox(f"{displayname}", self))
        self.Checkbox.setChecked(default)
    
    def get(self) -> bool:
        return self.Checkbox.isChecked()
    
    def __call__(self) -> bool:
        return self.get()
    
    def set(self, value:bool):
        self.Checkbox.setChecked(value)
    
    def copyFrom(self, other:'Bool'):
        self.Checkbox.setChecked(other.Checkbox.isChecked())

class Array(_TypeWidget): #TODO: Make a thingy to input arrays. This should probably be a button that opens a window with all the necessary stuff like a QTbale and a field to support numpy programming
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default: np.ndarray, dimMin=[None,None,None], dimMax=[None,None,None], unit="") -> None:
        super().__init__(parent)

class Path(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str, defaultDir:str="") -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.Button = self.addWidget(AGeWidgets.Button(self,"Set Path",lambda: self.setPath()),0,1)
        self.Path = default
        self.Button.setToolTip(default)
        self.DefaultDir = defaultDir
    
    def setPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName(directory=self.DefaultDir)[0]
        if path:
            self.Path = path
            self.Button.setToolTip(path)
    
    def get(self) -> str:
        return self.Path
    
    def __call__(self) -> str:
        return self.get()
    
    def set(self, value:str):
        self.Path = value
        self.Button.setToolTip(value)
    
    def copyFrom(self, other:'Path'):
        path = other.path
        self.Path = path
        self.Button.setToolTip(path)

class List(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:list, type_:type=int) -> None:
        super().__init__(parent)
        self.Type = type_
        self.NameLabel = self.addWidget(QtWidgets.QLabel(displayname, self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input = self.addWidget(QtWidgets.QLineEdit(self),0,1)
        self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(", ".join([str(i) for i in default]))
    
    def get(self) -> list: #TODO: validate input in some way
        return [self.Type(i) for i in self.Input.text().split(",")]
    
    def __call__(self) -> list:
        return self.get()
    
    #def set(self, value:str): #TODO
    #    self.Path = value
    #    self.Button.setToolTip(value)
    
    def copyFrom(self, other:'Str'):
        self.Input.setText(other.Input.text())

class Str(_TypeWidget):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str) -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(displayname, self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        #self.Input = self.addWidget(QtWidgets.QLineEdit(self),0,1)
        self.Input = self.addWidget(AGeWidgets.LineEdit(self),0,1)
        #self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(default)
    
    def get(self) -> str:
        return self.Input.text()
    
    def __call__(self) -> str:
        return self.get()
    
    def set(self, value:str):
        self.Input.setText(value)
    
    def copyFrom(self, other:'Str'):
        self.Input.setText(other.Input.text())

class Name(Str):
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, object_:'object', attribute:'str') -> None:
        self.objectRef:'weakref.ref[object]' = weakref.ref(object_)
        self.AttributeName = attribute
        super().__init__(parent, displayname=displayname, default=getattr(object_,attribute))
        self.Input.textChanged.connect(lambda: self.updateName())
    
    def updateName(self):
        setattr(self.objectRef(), self.AttributeName, self.get())

class Wildcard(_TypeWidget): #MAYBE: Multiline support?
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str) -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input = self.addWidget(AGeWidgets.LineEdit(self),0,1)
        self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(default)
    
    def get(self):
        locals_ = self.getLocals()
        exec("value = "+self.Input.text(), self.getGlobals(), locals_)
        return locals_["value"]
    
    def getLocals(self):
        return {}
    
    def getGlobals(self):
        return globals()
    
    def __call__(self):
        return self.get()
    
    def set(self, value:str): #MAYBE: One could also support AGeToPy if value is not a string or when a flag is set. But linebreaks may not appear...
        self.Input.setText(value)
    
    def copyFrom(self, other:'Wildcard'):
        self.Input.setText(other.Input.text())

#endregion Typewidgets

#region Type Helpers
class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def textFromValue(self, value):
        try:
            return QtCore.QLocale().toString(roundToN(value,5), 'g', QtCore.QLocale.FloatingPointPrecisionOption.FloatingPointShortest)
        except:
            return QtCore.QLocale().toString(roundToN(value,5), 'g', QtCore.QLocale.FloatingPointShortest)
#endregion Type Helpers

