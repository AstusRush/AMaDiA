# This Python file uses the following encoding: utf-8

# if__name__ == "__main__":
#     pass

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
import sympy
import sys


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
class MplCanvas_2D_Plot(Canvas):
    def __init__(self):
        #plt.style.use('dark_background')
        self.fig = Figure(constrained_layout =True)
        self.fig.set_facecolor(AF.background_Colour)
        
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_facecolor(AF.background_Colour)
        
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget_2D_Plot(QtWidgets.QWidget):
    def __init__(self, parent=None):
#        super(MplWidget, self).__init__(parent)
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas_2D_Plot()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to seperate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']

# -----------------------------------------------------------------------------------------------------------------
class MplCanvas_LaTeX(Canvas):
    def __init__(self,w,h):
        #plt.style.use('dark_background')
        #self.fig = Figure(constrained_layout =True)
        self.fig = Figure(figsize = (w,h),dpi=90)
        self.fig.set_facecolor(AF.background_Colour)
        
        #h = [Size.Fixed(1.0), Size.Fixed(4.5)]
        #v = [Size.Fixed(0.7), Size.Fixed(5.)]
        #divider = Divider(self.fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
        
        self.ax = self.fig.add_subplot(111)
        #self.ax = Axes(self.fig, divider.get_position())
        
        self.ax.set_facecolor(AF.background_Colour)
        self.ax.set_anchor('W')
        self.fig.subplots_adjust(left=0.01)
        self.ax.axis('off')
        
        #self.ax.set_axes_locator(divider.new_locator(nx=1, ny=1))
        #self.fig.add_axes(self.ax)
        
        Canvas.__init__(self, self.fig)
        #Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        #Canvas.updateGeometry(self)

class MplWidget_LaTeX(QtWidgets.QWidget):
    def __init__(self, parent=None):
#        super(MplWidget, self).__init__(parent)
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas_LaTeX(100,100)                  # Create canvas object
        #self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        #self.vbl.addWidget(self.canvas)
        #self.setLayout(self.vbl)
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidget(self.canvas)

        #self.Tab_2_LaTeX_LaTeXOutput.nav = NavigationToolbar(self.Tab_2_LaTeX_LaTeXOutput.canvas, self.Tab_2_LaTeX_LaTeXOutput)
        #self.Tab_2_LaTeX_LaTeXOutput.layout().addWidget(self.Tab_2_LaTeX_LaTeXOutput.nav)
        self.layout().addWidget(self.scroll)
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to seperate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']
    
    def Display(self,Text_L,Text_N,Font_Size,TextColour,Use_LaTeX = False):
        self.Text = Text_L
        self.Font_Size = Font_Size * 2
        self.TextColour = TextColour
        #-----------IMPORTANT-----------
        if Use_LaTeX:
            self.Text = Text_L
            self.UseTeX(True)
        else:
            self.UseTeX(False)
            Text_N = Text_N.replace("\limits","")
            self.Text = Text_N
        #-----------IMPORTANT-----------
        self.w=9
        self.h=9
        #self.canvas = MplCanvas_LaTeX(self.w+1, self.h+1) 
        #self.scroll.setWidget(self.canvas)
        #self.layout().addWidget(self.scroll)
        #self.canvas.resize(self.w+1, self.h+1)
        #self.canvas.__init__(self.w+1, self.h+1)
        self.canvas.ax.clear() # makes Space for the new text
        
        
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
                      
        """ For Figure(figsize = (100,100),dpi=90)
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
        """
        """ For Figure(figsize = (100,10),dpi=90)
        self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.195-(self.Font_Size/180)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
        """
        
        self.canvas.ax.axis('off')
        # Show the "graph"
        try:
            self.canvas.draw()
        except AF.common_exceptions:
            self.Text = Text_N
            if Use_LaTeX:
                self.UseTeX(True)
            else:
                self.UseTeX(False)
            self.canvas.ax.clear()
            self.canvas.ax.set_title(self.Text,
                      loc = "left",
                      #x=-0.12,
                      y=(1.15-(self.Font_Size/5000)),
                      horizontalalignment='left',
                      verticalalignment='top',
                      fontsize=self.Font_Size,
                      color = self.TextColour
                      ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                      ec="0.1", pad=0.1, alpha=0)
                      )
            self.canvas.ax.axis('off')
            #--------------------------
            
            try:
                self.canvas.draw()
            except AF.common_exceptions:
                AF.ExceptionOutput(sys.exc_info())
                print("Trying to output without LaTeX")
                self.Text = Text_N.replace("\limits","")
                self.UseTeX(False)
                self.canvas.ax.clear()
                self.canvas.ax.set_title(self.Text,
                          loc = "left",
                          #x=-0.12,
                          y=(1.15-(self.Font_Size/5000)),
                          horizontalalignment='left',
                          verticalalignment='top',
                          fontsize=self.Font_Size,
                          color = self.TextColour
                          ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                          ec="0.1", pad=0.1, alpha=0)
                          )
                self.canvas.ax.axis('off')
                #--------------------------
                try:
                    self.canvas.draw()
                except AF.common_exceptions:
                    AF.ExceptionOutput(sys.exc_info())
                    self.UseTeX(False)
                    self.canvas.ax.clear()
                    if Use_LaTeX:
                        ErrorText = "The text can't be displayed. Please send your input and a description of your problem to the developer"
                    else:
                        ErrorText = "The text can't be displayed. Please note that many things can't be displayed without LaTeX Mode."
                        if not AF.LaTeX_dvipng_Installed:
                            ErrorText += "\n Please install LaTeX (and dvipng if it is not already included in your LaTeX distribution) and restart AMaDiA"
                    self.canvas.ax.set_title(ErrorText,
                            loc = "left",
                            #x=-0.12,
                            y=(1.15-(self.Font_Size/5000)),
                            horizontalalignment='left',
                            verticalalignment='top',
                            fontsize=self.Font_Size,
                            color = self.TextColour
                            ,bbox=dict(boxstyle="round", facecolor=AF.background_Colour,
                            ec="0.1", pad=0.1, alpha=0)
                            )
                    self.canvas.ax.axis('off')
                    try:
                        self.canvas.draw()
                    except AF.common_exceptions:
                        AF.ExceptionOutput(sys.exc_info())
                        print("Can not display anything")
                
        finally:
            self.UseTeX(False)




