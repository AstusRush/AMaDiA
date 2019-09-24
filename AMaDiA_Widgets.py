# This Python file uses the following encoding: utf-8

# if__name__ == "__main__":
#     pass

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import matplotlib.pyplot as plt
import sympy

import matplotlib
from distutils.spawn import find_executable

if find_executable('latex') and find_executable('dvipng'):matplotlib.rcParams['text.usetex'] = True

import AMaDiA_Functions as AF
import AMaDiA_Classes as AC
import AMaDiA_ReplacementTables as ART

import importlib
def ReloadModules():
    importlib.reload(AF)
    importlib.reload(AC)
    importlib.reload(ART)


# 10.07.2019 from https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5?noredirect=1&lq=1
# Use MplWidget for things that have a matplot output
# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        #plt.style.use('dark_background')
        self.fig = Figure(constrained_layout =True)
        self.fig.set_facecolor((54/255, 57/255, 63/255))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor((54/255, 57/255, 63/255))
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
#        super(MplWidget, self).__init__(parent)
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

# -----------------------------------------------------------------------------------------------------------------




