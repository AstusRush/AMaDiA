
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
    S_ValueChanged:pyqtSignal = None
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
        self.S_ValueChanged = self.SpinBox.valueChanged
    
    def get(self) -> int:
        return self.SpinBox.value()
    
    def __call__(self) -> int:
        return self.get()
    
    def set(self, value:int):
        self.SpinBox.setValue(value)
    
    def copyFrom(self, other:'Int'):
        self.SpinBox.setValue(other.SpinBox.value())

class IntSlider(_TypeWidget):
    S_ValueChanged:'pyqtSignal' = pyqtSignal(int)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:int, min_:int=-10, max_:int=10, unit="") -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.SpinBox = self.addWidget(QtWidgets.QSpinBox(self),0,1)
        self.Slider = self.addWidget(QtWidgets.QSlider(self),1,0,1,2)
        self.Slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        if unit:
            self.SpinBox.setSuffix(f" {unit}")
        if min_:
            self.SpinBox.setMinimum(min_)
            self.Slider.setMinimum(min_)
        if max_:
            self.SpinBox.setMaximum(max_)
            self.Slider.setMaximum(max_)
        self.SpinBox.setValue(default)
        self.Slider.setValue(default)
        self.Slider.setSingleStep(1)
        self.Slider.setPageStep(1)
        
        self.SpinBox.valueChanged.connect(lambda val: self._changed(val))
        self.Slider.valueChanged.connect(lambda val: self._changed(val))
    
    def _changed(self, val:int):
        self.SpinBox.blockSignals(True)
        self.Slider.blockSignals(True)
        self.SpinBox.setValue(val)
        self.Slider.setValue(val)
        self.SpinBox.blockSignals(False)
        self.Slider.blockSignals(False)
        self.S_ValueChanged.emit(val)
    
    def get(self) -> int:
        return self.SpinBox.value()
    
    def __call__(self) -> int:
        return self.get()
    
    def set(self, value:int):
        self.SpinBox.setValue(value)
        #NOTE: This sends a signal, triggering _changed and thus updating the slider
    
    def copyFrom(self, other:'Int'):
        self.SpinBox.setValue(other.SpinBox.value())
        #NOTE: This sends a signal, triggering _changed and thus updating the slider

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
        self.S_ValueChanged = self.SpinBox.valueChanged
    
    def get(self) -> float:
        return self.SpinBox.value()
    
    def __call__(self) -> float:
        return self.get()
    
    def set(self, value:float):
        self.SpinBox.setValue(value)
    
    def copyFrom(self, other:'Float'):
        self.SpinBox.setValue(other.SpinBox.value())

class FloatSlider(_TypeWidget):
    S_ValueChanged:'pyqtSignal' = pyqtSignal(float)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:float, min_:float=-10, max_:float=10, unit="",sliderPrecision:int=1) -> None:
        super().__init__(parent)
        self.SliderPrecision = sliderPrecision
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.SpinBox = self.addWidget(DoubleSpinBox(self),0,1)
        self.SpinBox.setDecimals(10)
        try:
            try:
                self.SpinBox.setStepType(self.SpinBox.AdaptiveDecimalStepType)
            except:
                self.SpinBox.setStepType(self.SpinBox.StepType.AdaptiveDecimalStepType)
        except:
            ExceptionOutput()
        self.Slider = self.addWidget(QtWidgets.QSlider(self),1,0,1,2)
        self.Slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        if unit:
            self.SpinBox.setSuffix(f" {unit}")
        if min_:
            self.SpinBox.setMinimum(min_)
            self.Slider.setMinimum(math.ceil(min_*10**self.SliderPrecision))
        if max_:
            self.SpinBox.setMaximum(max_)
            self.Slider.setMaximum(math.floor(max_*10**self.SliderPrecision))
        self.SpinBox.setValue(default)
        self.Slider.setValue(int(default))
        self.Slider.setSingleStep(1)
        self.Slider.setPageStep(1)
        
        self.SpinBox.valueChanged.connect(lambda val: self._changed(val))
        self.Slider.valueChanged.connect(lambda val: self._changed(val/(10**self.SliderPrecision)))
    
    def _changed(self, val:float):
        self.SpinBox.blockSignals(True)
        self.Slider.blockSignals(True)
        self.SpinBox.setValue(val)
        self.Slider.setValue(int(val*10**self.SliderPrecision))
        self.SpinBox.blockSignals(False)
        self.Slider.blockSignals(False)
        self.S_ValueChanged.emit(val)
    
    def get(self) -> float:
        return self.SpinBox.value()
    
    def __call__(self) -> float:
        return self.get()
    
    def set(self, value:float):
        self.SpinBox.setValue(value)
        #NOTE: This sends a signal, triggering _changed and thus updating the slider
    
    def copyFrom(self, other:'Float'):
        self.SpinBox.setValue(other.SpinBox.value())
        #NOTE: This sends a signal, triggering _changed and thus updating the slider

class Bool(_TypeWidget):
    S_ValueChanged:pyqtSignal = pyqtSignal(bool)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:bool) -> None:
        super().__init__(parent)
        self.Checkbox = self.addWidget(QtWidgets.QCheckBox(f"{displayname}", self))
        self.Checkbox.setChecked(default)
        self.Checkbox.stateChanged.connect(lambda: self.S_ValueChanged.emit(self.Checkbox.isChecked()))
    
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
    S_ValueChanged:pyqtSignal = pyqtSignal(str)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str, defaultDir:str="", filter:str="", initialFilter:str="") -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.Button = self.addWidget(AGeWidgets.Button(self,"Set Path",lambda: self.setPath()),0,1)
        self.Path = default
        self.Button.setToolTip(default)
        self.DefaultDir = defaultDir
        self.Filter = filter
        self.InitialFilter = initialFilter
    
    def setPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName(directory=self.DefaultDir, filter=self.Filter, initialFilter=self.InitialFilter)[0]
        if path:
            self.Path = path
            self.Button.setToolTip(path)
            self.S_ValueChanged.emit(path)
    
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
    S_ValueChanged:pyqtSignal = pyqtSignal(str)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:list, type_:type=int) -> None:
        super().__init__(parent)
        self.Type = type_
        self.NameLabel = self.addWidget(QtWidgets.QLabel(displayname, self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input = self.addWidget(QtWidgets.QLineEdit(self),0,1)
        self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(", ".join([str(i) for i in default]))
        self.Input.returnPressed.connect(lambda: self.S_ValueChanged.emit(self.Input.text()))
    
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
    S_ValueChanged:pyqtSignal = pyqtSignal(str)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str) -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(displayname, self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        #self.Input = self.addWidget(QtWidgets.QLineEdit(self),0,1)
        self.Input = self.addWidget(AGeWidgets.LineEdit(self),0,1)
        #self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(default)
        self.Input.textChanged.connect(lambda: self.S_ValueChanged.emit(self.Input.text()))
    
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
    S_ValueChanged:pyqtSignal = pyqtSignal(str)
    def __init__(self, parent: 'QtWidgets.QWidget', displayname:str, default:str) -> None:
        super().__init__(parent)
        self.NameLabel = self.addWidget(QtWidgets.QLabel(f"{displayname}", self),0,0)
        self.NameLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input = self.addWidget(AGeWidgets.LineEdit(self),0,1)
        self.Input.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.Input.setText(default)
        self.Input.returnPressed.connect(lambda: self.S_ValueChanged.emit(self.Input.text()))
    
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

