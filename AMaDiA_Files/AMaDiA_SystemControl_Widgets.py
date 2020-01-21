
from AGeLib.AGeMain import common_exceptions, NC, ExceptionOutput, MplWidget

import sys
sys.path.append('..')
from PyQt5.Qt import QApplication, QClipboard # pylint: disable=no-name-in-module
from PyQt5 import QtWidgets,QtCore,QtGui,Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('Qt5Agg')
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
import numpy as np
import scipy
import sympy
from sympy.parsing.sympy_parser import parse_expr
import re
import time

import warnings

from External_Libraries.python_control_master import control

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART
from AMaDiA_Files import AMaDiA_Widgets as AW
# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_CONTROL(Canvas):
    Titles = ['Step Response','Impulse Response','Forced Response',
                        'Bode Plot','BODE_PLOT_2',
                        'Nyquist Plot','Nichols Plot','Pole-Zero-Plot',
                        'Root-Locus-Plot','LaTeX-Display']
    def __init__(self):
        #self.fig = Figure()
        self.fig = plt.figure(num="CONTROL",constrained_layout =True)
        self.fig.set_facecolor(AF.background_Colour)

        combined = True # should Phase and Magnitude of the Bodeplot share a plot?
        if combined:
            self.gs = self.fig.add_gridspec(3, 3)
            
            self.p_step_response = self.fig.add_subplot(self.gs[0,0])
            self.p_impulse_response = self.fig.add_subplot(self.gs[0,1])
            self.p_forced_response = self.fig.add_subplot(self.gs[0,2])
            self.p_bode_plot_1 = self.fig.add_subplot(self.gs[1,0])
            self.p_bode_plot_2 = self.p_bode_plot_1.twinx()
            self.p_nyquist_plot = self.fig.add_subplot(self.gs[1,1])
            self.p_nichols_plot = self.fig.add_subplot(self.gs[1,2])
            self.p_pzmap = self.fig.add_subplot(self.gs[2:,0])
            self.p_root_locus = self.fig.add_subplot(self.gs[2:,1])
            self.p_LaTeX_Display = self.fig.add_subplot(self.gs[2:,2])
        
        else:
            self.gs = self.fig.add_gridspec(6, 3)
            
            self.p_step_response = self.fig.add_subplot(self.gs[0:2,0])
            self.p_impulse_response = self.fig.add_subplot(self.gs[0:2,1])
            self.p_TODO = self.fig.add_subplot(self.gs[0:2,2])     #TODO
            self.p_bode_plot_2 = self.fig.add_subplot(self.gs[3,0])
            self.p_bode_plot_1 = self.fig.add_subplot(self.gs[2,0],sharex=self.p_bode_plot_2)
            self.p_nyquist_plot = self.fig.add_subplot(self.gs[2:4,1])
            self.p_nichols_plot = self.fig.add_subplot(self.gs[2:4,2])
            self.p_pzmap = self.fig.add_subplot(self.gs[4:,0])
            self.p_root_locus = self.fig.add_subplot(self.gs[4:,1])
            self.p_LaTeX_Display = self.fig.add_subplot(self.gs[4:,2])

        self.p_plot_LIST = [ self.p_step_response, self.p_impulse_response, self.p_forced_response,
                            self.p_bode_plot_1, self.p_bode_plot_2,
                            self.p_nyquist_plot, self.p_nichols_plot, self.p_pzmap,
                            self.p_root_locus, self.p_LaTeX_Display]
        
        for i,p in enumerate(self.p_plot_LIST):
            p.set_facecolor(AF.background_Colour)
            if self.Titles[i] == "BODE_PLOT_2":
                p.set_title("  ")
            elif self.Titles[i] != 'LaTeX-Display':
                p.set_title(self.Titles[i])
            # set labels that control can find the axes
            if self.Titles[i] == "Bode Plot":
                p.set_label('control-bode-magnitude')
            elif self.Titles[i] == "BODE_PLOT_2":
                p.set_label('control-bode-phase')
            #elif self.Titles[i] == 'Nyquist Plot':
            #    p.set_label('control-nyquist')
        #self.fig.tight_layout()
        
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        Canvas.updateGeometry(self)

class MplWidget_CONTROL(MplWidget):
    def __init__(self, parent=None):
        super(MplWidget_CONTROL, self).__init__(parent)
        QtWidgets.QWidget.__init__(self)           # Inherit from QWidget
        self.canvas = MplCanvas_CONTROL()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.layout().setContentsMargins(0,0,0,0)
        
        
        #self.setLayout(QtWidgets.QVBoxLayout())
        #self.scroll = QtWidgets.QScrollArea(self)
        #self.scroll.setWidget(self.canvas)

        self.Curr_Sys = (None, None, 0.0, 0.0, "", "")
        self.LastCall = False
        self.Curr_Sys_LaTeX = ""
        
    def SetColour(self,BG=None,FG=None):
        try:
            if BG != None and FG != None:
                self.background_Colour = BG
                self.TextColour = FG
                self.HexcolourText = '#%02x%02x%02x' % (int(self.TextColour[0]*255),int(self.TextColour[1]*255),int(self.TextColour[2]*255))
            self.canvas.fig.set_facecolor(self.background_Colour)
            self.canvas.fig.set_edgecolor(self.background_Colour)
            for i,p in enumerate(self.canvas.p_plot_LIST):
                p.set_facecolor(self.background_Colour)
                if p.get_title() == "N/A":
                    p.axis('off')
                    p.text(0.5,0.5,"N/A", horizontalalignment='center', verticalalignment='center',color=self.TextColour)
                    p.set_title(self.canvas.Titles[i],color=self.TextColour)
                    continue
                if self.canvas.Titles[i] == "BODE_PLOT_2":
                    p.set_title("  ",color=self.TextColour)
                elif self.canvas.Titles[i] != 'LaTeX-Display':
                    p.set_title(self.canvas.Titles[i],color=self.TextColour)
                if self.canvas.Titles[i] == "BODE_PLOT_2" or self.canvas.Titles[i] == 'Bode Plot':
                    p.spines['right'].set_color(self.TextColour)
                else:
                    p.yaxis.label.set_color(self.TextColour)
                p.xaxis.label.set_color(self.TextColour)
                p.spines['bottom'].set_color(self.TextColour)
                p.spines['left'].set_color(self.TextColour)
                p.tick_params(axis='x', colors=self.TextColour)
                p.tick_params(axis='y', colors=self.TextColour)
                if self.canvas.Titles[i] == 'LaTeX-Display':
                    p.axis('off')
            self.canvas.p_LaTeX_Display.text(0.5,0.5,self.Curr_Sys_LaTeX, horizontalalignment='center', verticalalignment='center',color=self.TextColour)#,usetex=True)
            if self.Curr_Sys[4] != "" and False: # Disabled since the Legend covers the entire axes when Window not fullscreen
                self.canvas.p_forced_response.legend(["Input Function: "+self.Curr_Sys[4]])#,color=self.TextColour)
        except common_exceptions:
            NC(2,"Could not set all colours for the system plots",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".SetColour").send()
        try:
            self.canvas.draw()
        except common_exceptions:
            NC(1,"Could not draw system plots",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".SetColour").send()
        
        #if self.LastCall != False:
        #    self.Display(self.LastCall[0],self.LastCall[1],self.LastCall[2],self.LastCall[3])
        #else:
        #    try:
        #        self.canvas.draw()
        #    except common_exceptions:
        #        pass
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']
    
    def Display(self,sys1,Use_LaTeX = False, T=None, X0 = 0.0, U=0.0, Ufunc = ""):
        """
        Retrun value compatible as argument to init NC   \n
        sys1 = System   \n
        Use_LaTeX = bool   \n
        T = Time steps at which the input is defined; values must be evenly spaced.   \n
        X0 = Initial condition   \n
        U = Input array giving input at each time T used for "Forced Response"-plot   \n
        Ufunc = string (Name of the function that created U)
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for i in self.canvas.p_plot_LIST:
                    i.clear()
            Torig = T
            Uorig = U
            try:
                if T == None:
                    syst = control.timeresp._get_ss_simo(sys1)
                    T = scipy.signal.ltisys._default_response_times(syst.A, 500)

                # If U not given try to create using Ufunc. If Ufunc not given or creation failed set U and Ufunc to 0
                if U == 0.0:
                    if Ufunc != "":
                        try:
                            Function = parse_expr(AF.AstusParse(Ufunc))
                            s = sympy.symbols('s')
                            evalfunc = sympy.lambdify(s, Function, modules=['numpy','sympy'])
                            U = evalfunc(T)
                            U = np.asarray(U)
                            if type(U) == int or type(U) == float or U.shape == (): #This also catches the case exp(x)
                                U = np.full_like(T, U)
                            if U.shape != T.shape:
                                raise Exception("Dimensions do not match")
                        except common_exceptions:
                            NC(2,"Could not interpret u(s)",exc=sys.exc_info(),input=Ufunc,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
                            Ufunc = ""
                    if Ufunc == "":
                        Ufunc = "0"
            except common_exceptions:
                NC(1,"Could not calculate time steps",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()


            self.Curr_Sys_LaTeX = str(sys1) #TODO: MAKE PROPER LaTeX
            self.Curr_Sys = (sys1, Torig, X0, Uorig, Ufunc, self.Curr_Sys_LaTeX)


            self.canvas.p_bode_plot_1.set_label('control-bode-magnitude')
            self.canvas.p_bode_plot_2.set_label('control-bode-phase')
            
        except common_exceptions:
            NC(1,"Could not prepare the control display",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.UseTeX(False)
            return
        
        try: # 0
            oT,y = control.step_response(sys1, number_of_samples=500, T=T, X0 = X0)
            self.canvas.p_step_response.plot(oT,y)
        except common_exceptions:
            NC(1,"Could not plot step response",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_step_response.set_title("N/A")

        try: # 1
            oT,y = control.impulse_response(sys1, number_of_samples=500, T=T, X0 = X0)
            self.canvas.p_impulse_response.plot(oT,y)
        except common_exceptions:
            NC(1,"Could not plot impulse response",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_impulse_response.set_title("N/A")

        try: # 2
            oT,y, xout = control.forced_response(sys1, T=T, X0 = X0, U=U) # pylint: disable=unused-variable
            self.canvas.p_forced_response.plot(oT,y)
        except common_exceptions:
            NC(1,"Could not plot forced response",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_forced_response.set_title("N/A")

        try: # 3+4
            plt.figure(self.canvas.fig.number) # set figure to current that .gfc() in control.bode_plot can find it
            control.bode_plot(sys1, dB=True, omega_num=500)
        except common_exceptions:
            NC(1,"Could not generate Bode plot",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_bode_plot_1.set_title("N/A")

        try: # 5
            plt.sca(self.canvas.p_nyquist_plot)
            control.nyquist_plot(sys1,number_of_samples=500)
        except common_exceptions:
            NC(1,"Could not generate Nyquist plot",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_nyquist_plot.set_title("N/A")

        try: # 6
            plt.sca(self.canvas.p_nichols_plot)
            control.nichols_plot(sys1, number_of_samples=500)
        except common_exceptions:
            NC(1,"Could not generate Nichols plot",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_nichols_plot.set_title("N/A")

        try: # 7
            poles,zeros = control.pzmap(sys1,Plot=False)
            if len(poles) > 0:
                self.canvas.p_pzmap.scatter(np.real(poles), np.imag(poles), s=50, marker='x', c="red")
            if len(zeros) > 0:
                self.canvas.p_pzmap.scatter(np.real(zeros), np.imag(zeros), s=25, marker='o', c="orange")
            self.canvas.p_pzmap.grid(True)
        except common_exceptions:
            NC(1,"Could not generate pole-zero-map",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_pzmap.set_title("N/A")

        try: # 8
            #plt.sca(self.canvas.p_root_locus)
            #control.rlocus(sys1)
            control.root_locus_AMaDiA(sys1,self.canvas.p_root_locus)
            self.canvas.p_root_locus.grid(True)
        except common_exceptions:
            NC(1,"Could not generate root locus plot",exc=sys.exc_info(),input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Display").send()
            self.canvas.p_root_locus.set_title("N/A")

        # 9 + Plot
        self.SetColour() # Set Colour, Titles, etc... and the Display
        self.UseTeX(False)

# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_CONTROL_single_plot(Canvas):
    def __init__(self):
        #self.fig = Figure()
        self.fig = plt.figure(constrained_layout =True)
        self.fig.set_facecolor(AF.background_Colour)
        
        self.ax = self.fig.add_subplot(111)
        self.ax1 = self.ax.twinx()
        self.ax1.axis('off')
        
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        Canvas.updateGeometry(self)

class MplWidget_CONTROL_single_plot(MplWidget):
    def __init__(self, parent=None):
        super(MplWidget_CONTROL_single_plot, self).__init__(parent)
        self.Bode = False
        self.FuncLabel = ""
        self.Title = "Doubleclick on a control plot to display it here"

        self.Grid = QtWidgets.QGridLayout(self)
        self.Grid.setContentsMargins(0, 0, 0, 0)
        self.Grid.setSpacing(0)
        self.Grid.setObjectName("Grid")

        ##self.ScrollWidgetC = QtWidgets.QWidget(self)
        ##self.ScrollWidgetCGrid = QtWidgets.QGridLayout(self.ScrollWidgetC)
        ##self.ScrollWidgetCGrid.setContentsMargins(0, 0, 0, 0)
        ##self.ScrollWidgetCGrid.setSpacing(0)
        ##self.ScrollWidgetCGrid.setObjectName("ScrollWidgetCGrid")
        #self.ScrollWidget = QtWidgets.QScrollArea(self)#.ScrollWidgetC)
        #self.ScrollWidget.setWidgetResizable(True)
        #self.ScrollWidget.setObjectName("ScrollWidget")
        self.ScrollWidgetContents = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        #sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.ScrollWidgetContents.sizePolicy().hasHeightForWidth())
        self.ScrollWidgetContents.setSizePolicy(sizePolicy)
        ##self.ScrollWidgetContents.setGeometry(QtCore.QRect(0, 0, 221, 264))
        self.ScrollWidgetContents.setObjectName("ScrollWidgetContents")
        self.ScrollGrid = QtWidgets.QGridLayout(self.ScrollWidgetContents)
        self.ScrollGrid.setContentsMargins(0, 0, 0, 0)
        self.ScrollGrid.setSpacing(0)
        self.ScrollGrid.setObjectName("ScrollGrid")

        self.canvas = MplCanvas_CONTROL_single_plot()
        self.x_from_input = QtWidgets.QDoubleSpinBox(self.ScrollWidgetContents)
        self.x_to_input = QtWidgets.QDoubleSpinBox(self.ScrollWidgetContents)
        self.x_checkbox = QtWidgets.QCheckBox(self.ScrollWidgetContents)
        self.y_from_input = QtWidgets.QDoubleSpinBox(self.ScrollWidgetContents)
        self.y_to_input = QtWidgets.QDoubleSpinBox(self.ScrollWidgetContents)
        self.y_checkbox = QtWidgets.QCheckBox(self.ScrollWidgetContents)
        self.apply_zoom_button = QtWidgets.QPushButton(self.ScrollWidgetContents)

        self.x_from_input.setDecimals(5)
        self.x_from_input.setMinimum(-1000000.0)
        self.x_from_input.setMaximum(1000000.0)
        self.x_from_input.setProperty("value", -10.0)
        self.x_to_input.setDecimals(5)
        self.x_to_input.setMinimum(-1000000.0)
        self.x_to_input.setMaximum(1000000.0)
        self.x_to_input.setProperty("value", 10.0)
        self.x_checkbox.setText("Limit x")
        self.y_from_input.setDecimals(5)
        self.y_from_input.setMinimum(-1000000.0)
        self.y_from_input.setMaximum(1000000.0)
        self.y_from_input.setProperty("value", 0.0)
        self.y_to_input.setDecimals(5)
        self.y_to_input.setMinimum(-1000000.0)
        self.y_to_input.setMaximum(1000000.0)
        self.y_to_input.setProperty("value", 5.0)
        self.y_checkbox.setText("Limit y")
        self.apply_zoom_button.setText("Apply Limits")
        
        #self.ScrollWidget.setWidget(self.ScrollWidgetContents)

        self.ScrollGrid.addWidget(self.x_from_input,1,0)
        self.ScrollGrid.addWidget(self.x_to_input,1,1)
        self.ScrollGrid.addWidget(self.x_checkbox,1,2)
        self.ScrollGrid.addWidget(self.y_from_input,1,3)
        self.ScrollGrid.addWidget(self.y_to_input,1,4)
        self.ScrollGrid.addWidget(self.y_checkbox,1,5)
        self.ScrollGrid.addWidget(self.apply_zoom_button,1,6)

        ##self.ScrollWidgetCGrid.addWidget(self.ScrollWidget,1,0)

        self.Grid.addWidget(self.canvas,0,0)
        self.Grid.addWidget(self.ScrollWidgetContents,1,0)#self.Grid.addWidget(self.ScrollWidget,1,0)#C
        
        self.setLayout(self.Grid)

        # TODO: Reimplement these to let them fit the height to the contents automatically
        #self.ScrollWidgetContents.setMaximumHeight(50)
        #self.ScrollWidget.setMaximumHeight(70)
        
        self.apply_zoom_button.clicked.connect(self.ApplyZoom)
        
    def ApplyZoom(self):
        try:
            xmin , xmax = self.x_from_input.value(), self.x_to_input.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            xlims = (xmin , xmax)
            ymin , ymax = self.y_from_input.value(), self.y_to_input.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            ylims = (ymin , ymax)
            
            self.canvas.ax.relim()
            self.canvas.ax1.relim()
            self.canvas.ax.autoscale()
            self.canvas.ax1.autoscale()
            if self.x_checkbox.isChecked():
                self.canvas.ax.set_xlim(xlims)
                self.canvas.ax1.set_xlim(xlims)
            if self.y_checkbox.isChecked():
                self.canvas.ax.set_ylim(ylims)
                self.canvas.ax1.set_ylim(ylims)
            
            try:
                self.canvas.draw()
            except RuntimeError: #This is only a failsave
                ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.UseTeX(False)
                self.canvas.draw()
        except common_exceptions:
            Error = ExceptionOutput(sys.exc_info())
            self.window().NotifyUser(1,Error)
        
    def SetColour(self,BG=None,FG=None):
        if BG != None and FG != None:
            super(MplWidget_CONTROL_single_plot, self).SetColour(BG,FG)
        try:
            self.canvas.ax.set_facecolor(self.background_Colour)
            self.canvas.ax.spines['bottom'].set_color(self.TextColour)
            self.canvas.ax.spines['left'].set_color(self.TextColour)
            if not self.Bode:
                self.canvas.ax.yaxis.label.set_color(self.TextColour)
            self.canvas.ax.xaxis.label.set_color(self.TextColour)
            self.canvas.ax.tick_params(axis='x', colors=self.TextColour)
            self.canvas.ax.tick_params(axis='y', colors=self.TextColour)
            self.canvas.ax.set_title(self.Title, color=self.TextColour)
            if self.Bode:
                self.canvas.ax1.set_facecolor(self.background_Colour)
                self.canvas.ax1.spines['bottom'].set_color(self.TextColour)
                self.canvas.ax1.spines['left'].set_color(self.TextColour)
                self.canvas.ax1.tick_params(axis='x', colors=self.TextColour)
                self.canvas.ax1.tick_params(axis='y', colors=self.TextColour)
                self.canvas.ax.grid( c='C0',ls=(0, (4, 6)), linewidth=1  ,which='major')
                self.canvas.ax.grid( c='C0',ls=(0, (2, 8)), linewidth=0.5,which='minor',axis='x')
                self.canvas.ax1.grid(c='C1',ls=(0, (2, 8)), linewidth=1)
                self.canvas.ax.spines['right'].set_color(self.TextColour)
                self.canvas.ax1.spines['right'].set_color(self.TextColour)
            if self.FuncLabel != "":
                self.canvas.ax.legend()
        except common_exceptions:
            NC(2,"Could not set all colours for the single system plot",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".SetColour").send()
        try:
            self.canvas.draw()
            return True
        except common_exceptions:
            NC(1,"Could not draw the single system plot",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".SetColour").send()
            return False
    
    def UseTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']

    def clear(self):
        self.Title = "Doubleclick on a control plot to display it here"
        try:
            self.canvas.ax.remove()
        except common_exceptions:
            pass
        try:
            self.canvas.ax1.remove()
        except common_exceptions:
            pass
        try:
            self.canvas.fig.clear()
        except common_exceptions:
            pass
        try:
            self.canvas.ax = self.canvas.fig.add_subplot(111)
            self.canvas.ax1 = self.canvas.ax.twinx()
            self.canvas.ax1.axis('off')
        except common_exceptions:
            pass
        self.Bode = False
        try: # CLEANUP: Clean up clear function
            self.canvas.ax.set_facecolor(self.background_Colour)
            self.canvas.ax.spines['bottom'].set_color(self.TextColour)
            self.canvas.ax.spines['left'].set_color(self.TextColour)
            #if not self.Bode:
            self.canvas.ax.yaxis.label.set_color(self.TextColour)
            self.canvas.ax.xaxis.label.set_color(self.TextColour)
            self.canvas.ax.tick_params(axis='both',which='both', colors=self.TextColour)
            #self.canvas.ax.tick_params(axis='y', colors=self.TextColour)
            self.canvas.ax.set_title(self.Title, color=self.TextColour)
            #if self.Bode:
            #    self.canvas.ax1.set_facecolor(self.background_Colour)
            #    self.canvas.ax1.spines['bottom'].set_color(self.TextColour)
            #    self.canvas.ax1.spines['left'].set_color(self.TextColour)
            #    self.canvas.ax1.tick_params(axis='both',which='both', colors=self.TextColour)
            #    #self.canvas.ax1.tick_params(axis='y', colors=self.TextColour)
            #if self.Bode:
            #    self.canvas.ax1.grid(c='orange',ls='--')
            #    self.canvas.ax.spines['right'].set_color(self.TextColour)
            #    self.canvas.ax1.spines['right'].set_color(self.TextColour)
        except common_exceptions:
            pass
        try:
            self.canvas.draw()
        except common_exceptions:
            pass

    def Plot(self,system,PlotName):
        """
        Plot the plot "Plotname"
        """
        ret = False
        self.FuncLabel = ""
        Titles = MplCanvas_CONTROL.Titles
        (sys1, T, X0 , U, Ufunc, Curr_Sys_LaTeX) = system # pylint: disable=unused-variable
        try:
            if T == None:
                syst = control.timeresp._get_ss_simo(sys1)
                T = scipy.signal.ltisys._default_response_times(syst.A, 5000)
        except common_exceptions:
            pass
        self.clear()

        # Plot the Plot
        try:
            if PlotName == Titles[0]:
                oT,y = control.step_response(sys1, number_of_samples=5000, T=T, X0 = X0)
                self.canvas.ax.plot(oT,y)
            elif PlotName == Titles[1]:
                oT,y = control.impulse_response(sys1, number_of_samples=5000, T=T, X0 = X0)
                self.canvas.ax.plot(oT,y)
            elif PlotName == Titles[2]:
                # If U not given try to create using Ufunc. If Ufunc not given or creation failed set U and Ufunc to 0
                if U == 0.0:
                    if Ufunc != "":
                        try:
                            Function = parse_expr(AF.AstusParse(Ufunc))
                            s = sympy.symbols('s')
                            evalfunc = sympy.lambdify(s, Function, modules=['numpy','sympy'])
                            U = evalfunc(T)
                            U = np.asarray(U)
                            if type(U) == int or type(U) == float or U.shape == (): #This also catches the case exp(s)
                                U = np.full_like(T, U)
                            if U.shape != T.shape:
                                raise Exception("Dimensions do not match")
                        except common_exceptions:
                            NC(2,"Could not interpret u(s)",exc=sys.exc_info(),input=Ufunc,win=self.window().windowTitle(),func=str(self.objectName())+".Plot").send()
                            Ufunc = ""
                    if Ufunc == "":
                        Ufunc = "0"
                
                self.FuncLabel = "u(s) = "+Ufunc
                oT,y,xout = control.forced_response(sys1, T=T, X0 = X0, U=U) # pylint: disable=unused-variable
                self.canvas.ax.plot(oT,y,label="Response")
                self.canvas.ax.plot(T,U,label="Input Function: u(s) = "+Ufunc)
            elif PlotName == Titles[3] or PlotName == Titles[4] or PlotName == "  ":
                self.Bode = True
                self.canvas.ax1.axis('on')
                self.canvas.ax.set_label('control-bode-magnitude')
                self.canvas.ax1.set_label('control-bode-phase')
                plt.figure(self.canvas.fig.number)
                control.bode_plot(sys1, dB=True, omega_num=5000,Dense_Phase_Major_Ticks=True, margins=True)
            elif PlotName == Titles[5]:
                plt.sca(self.canvas.ax)
                control.nyquist_plot(sys1, number_of_samples=5000)
                self.FuncLabel = "Nyquist"
            elif PlotName == Titles[6]:
                plt.sca(self.canvas.ax)
                control.nichols_plot(sys1, number_of_samples=5000)
            elif PlotName == Titles[7]:
                poles,zeros = control.pzmap(sys1,Plot=False)
                if len(poles) > 0:
                    self.canvas.ax.scatter(np.real(poles), np.imag(poles), s=50, marker='x', c="red")
                if len(zeros) > 0:
                    self.canvas.ax.scatter(np.real(zeros), np.imag(zeros), s=25, marker='o', c="orange")
                self.canvas.ax.grid(True)
            elif PlotName == Titles[8]:
                control.root_locus_AMaDiA(sys1,self.canvas.ax)
                self.canvas.ax.grid(True)
                self.canvas.ax.legend()
            else: # LaTeX Display (Uses Title as display string) # This can currently not occur
                #NC(2,"The system display can not be magnified yet",input=sys1,win=self.window().windowTitle(),func=str(self.objectName())+".Plot").send()
                return False
            


            # Get Plotname
            if PlotName == Titles[3] or PlotName == Titles[4] or PlotName == "  ":
                self.Title = Titles[3]
            else:
                self.Title = PlotName

            #Colour everything and draw it
            ret = self.SetColour()
        except common_exceptions:
            NC(1,"Could not plot {}".format(str(PlotName)),exc=sys.exc_info(),input="System:\n{}\n\nPlot: {}".format(str(sys1),str(PlotName)),win=self.window().windowTitle(),func=str(self.objectName())+".Plot").send()
            self.UseTeX(False)
            return False
        self.UseTeX(False)
        return ret



# ----------------------
class SystemClass():
    def __init__(self,sysIn,Name,Tab=None,systemInput=None):
        self.sys = sysIn
        self.Name = Name
        self.Tab = Tab
        self.systemInput = systemInput
        # Generate LaTeX of tf:
        Ys,Xs = control.tfdata(self.sys)
        Ys,Xs = Ys[0][0],Xs[0][0]
        Gs = "Eq(G(s),("
        YStr = []
        i = len(Ys)-1
        while i >= 0:
            if Ys[len(Ys)-i-1] != 0:
                if i == 0:
                    s = "{}".format(Ys[len(Ys)-i-1])
                else:
                    s = "{}*s**({})".format(Ys[len(Ys)-i-1],i)
                YStr.append(s)
            i-=1
        Gs += "+".join(YStr)
        Gs += ")/("
        XStr = []
        i = len(Xs)-1
        while i >= 0:
            if Xs[len(Xs)-i-1] != 0:
                if i == 0:
                    s = "{}".format(Xs[len(Xs)-i-1])
                else:
                    s = "{}*s**({})".format(Xs[len(Xs)-i-1],i)
                XStr.append(s)
            i-=1
        Gs += "+".join(XStr)
        Gs += "))"
        Gs = AF.number_shaver(Gs)
        Sys_Gs = parse_expr(Gs,evaluate=False)
        Sys_Gs_LaTeX = sympy.latex(Sys_Gs)
        self.Sys_Gs_LaTeX_L = r"$\displaystyle "
        self.Sys_Gs_LaTeX_N = "$"
        self.Sys_Gs_LaTeX_L += Sys_Gs_LaTeX
        self.Sys_Gs_LaTeX_N += Sys_Gs_LaTeX
        self.Sys_Gs_LaTeX_L += "$"
        self.Sys_Gs_LaTeX_N += "$"
        
        # Generate LaTeX of ss:
        A,B,C,D = control.ssdata(self.sys)
        self.Order = A.shape[0]
        x_vec = []
        x_vec_diff = []
        i=1
        while i <= self.Order:
            x_vec.append("x_{}(t)".format(i))
            x_vec_diff.append("diff(x_{}(t),t)".format(i))
            i+=1
        x_vec = str(sympy.Matrix(x_vec))
        x_vec_diff = str(sympy.Matrix(x_vec_diff))
        A,B = AF.number_shaver(str(sympy.Matrix(A))) , AF.number_shaver(str(sympy.Matrix(B)))
        C,D = AF.number_shaver(str(sympy.Matrix(C))) , AF.number_shaver(str(sympy.Matrix(D)))
        self.SSx_LaTeX = AF.LaTeX("Eq("+x_vec_diff+","+A+"*"+x_vec+"+"+B+"*u(t))")
        self.SSy_LaTeX = AF.LaTeX("Eq(y(t),"+C+"*"+x_vec+"+"+D+"*u(t))")
        self.Sys_SS_LaTeX_L = r"$\displaystyle " + self.SSx_LaTeX + "$\n" + r"$\displaystyle " + self.SSy_LaTeX + "$"
        self.Sys_SS_LaTeX_N = "$" + self.SSx_LaTeX + "$\n$" + self.SSy_LaTeX + "$"
        
        
        # Combine LaTeX of ss and tf:
        self.CheckStability()
        try:
            self.Sys_LaTeX_L = "System: ${}$ \nBIBO-Stable: ${}$\nTransfer Function:\n".format(AF.LaTeX(AF.AstusParse(self.Name)),self.BIBOStabel) + self.Sys_Gs_LaTeX_L + "\nState Space:\n" + self.Sys_SS_LaTeX_L
            self.Sys_LaTeX_N = "System: ${}$ \nBIBO-Stable: ${}$\nTransfer Function:\n".format(AF.LaTeX(AF.AstusParse(self.Name)),self.BIBOStabel) + self.Sys_Gs_LaTeX_N + "\nState Space:\n" + self.Sys_SS_LaTeX_N
        except common_exceptions:
            NC(1,"Invalid Name (Could not convert name to LaTeX)",exc=sys.exc_info(),func="SystemClass.__init__",input=self.Name,win="System Control Window").send()
            raise Exception("Invalid Name (Could not convert name to LaTeX)")

    def Item(self):
        item = QtWidgets.QListWidgetItem()
        item.setText(self.Name)
        item.setData(100,self)
        return item

    def Close(self):
        SystemObject = SystemClass(control.feedback(self.sys),self.Name+"_closed",self.Tab,self.systemInput)
        item = QtWidgets.QListWidgetItem()
        item.setText(SystemObject.Name)
        item.setData(100,SystemObject)
        return item

    def CheckStability(self):
        self.BIBOStabel = True
        #A = sympy.Matrix(control.ssdata(self.sys)[0])
        #eigenvals = A.eigenvals()
        poles = self.sys.pole()
        for i in poles:
            if np.real(i) >= 0:
                self.BIBOStabel = False
                break