import sys, os
sys.path.append('..')
from AGeLib import *

import typing

import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
from sympy.parsing.sympy_parser import parse_expr
import time

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_Widgets as AW
from AMaDiA_Files import AMaDiA_ReplacementTables as ART

if typing.TYPE_CHECKING:
    from AMaDiA import App, AMaDiA_Main_Window


# To limit the length of output (Currently used to reduce the length of the y vector when an error in the plotter occurs)
import reprlib
formatArray = reprlib.Repr()
formatArray.maxlist = 20       # max elements displayed for lists
formatArray.maxarray = 20       # max elements displayed for arrays
formatArray.maxother = 500       # max elements displayed for other including np.ndarray
formatArray.maxstring = 40    # max characters displayed for strings

class Tab_Plotter(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.AMaDiA: AMaDiA_Main_Window = parent
        super().__init__(parent)
        self.setObjectName("Tab_3")
        self.gridLayout_10 = QtWidgets.QGridLayout(self)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.TabWidget = QtWidgets.QTabWidget(self)
        self.TabWidget.setObjectName("TabWidget")
        self.Tab_2D = Plot2D(self)
        self.TabWidget.addTab(self.Tab_2D, "")
        self.Tab_3D = QtWidgets.QWidget()
        self.Tab_3D.setObjectName("Tab_3D")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.Tab_3D)
        self.gridLayout_14.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_14.setSpacing(0)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.Tab_3D_3DWidget = AW.AMaDiA_3DPlotWidget(self.Tab_3D)
        self.Tab_3D_3DWidget.setObjectName("Tab_3D_3DWidget")
        self.gridLayout_14.addWidget(self.Tab_3D_3DWidget, 0, 0, 1, 1)
        self.TabWidget.addTab(self.Tab_3D, "")
        self.Tab_Complex = QtWidgets.QWidget()
        self.Tab_Complex.setObjectName("Tab_Complex")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.Tab_Complex)
        self.gridLayout_15.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_15.setSpacing(0)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.Tab_Complex_ComplexWidget = AW.AMaDiA_ComplexPlotWidget(self.Tab_Complex)
        self.Tab_Complex_ComplexWidget.setObjectName("Tab_Complex_ComplexWidget")
        self.gridLayout_15.addWidget(self.Tab_Complex_ComplexWidget, 0, 0, 1, 1)
        self.TabWidget.addTab(self.Tab_Complex, "")
        self.gridLayout_10.addWidget(self.TabWidget, 0, 0, 1, 1)
        
        self.TabWidget.setCurrentIndex(0)
        
        self.Tab_Complex_ComplexWidget.S_Plot.connect(lambda: self.Tab_Complex_F_Plot_Button())
    
 # ---------------------------------- Tab_3D_ 3D-Plot (Tab_3D_3DWidget) ----------------------------------
    # FEATURE: 3D-Plot
    
 # ---------------------------------- Tab_Complex_ Complex-Plot (Tab_Complex_ComplexWidget) ----------------------------------
    # FEATURE: Complex-Plot
    def Tab_Complex_F_Plot_Button(self):
        self.AMaDiA.TC("NEW", self.Tab_Complex_ComplexWidget.InputField.text(), self.Tab_Complex_F_Plot_init, Iam=AC.Iam_complex_plot)
    
    def Tab_Complex_F_Plot_init(self, AMaS_Object:"AC.AMaS"):
        #if not AMaS_Object.Plot_is_initialized_complex: AMaS_Object.init_complex_plot()
        AMaS_Object.init_complex_plot()
        AMaS_Object = self.Tab_Complex_ComplexWidget.applySettings(AMaS_Object)
        
        self.AMaDiA.TC("WORK", AMaS_Object, lambda: AC.AMaS.Plot_Complex_Calc_Values(AMaS_Object), self.Tab_Complex_F_Plot)
    
    def Tab_Complex_F_Plot(self , AMaS_Object:"AC.AMaS"):
        #self.AMaDiA.HistoryHandler(AMaS_Object,3,1)
        
        try:
            self.Tab_Complex_ComplexWidget.plot(AMaS_Object)
        except common_exceptions :
            NC(msg="Could not plot", exc=sys.exc_info(), func="AMaDiA_Main_Window.Tab_Complex_F_Plot", win=self.windowTitle(), input=AMaS_Object.Input)
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
    
 # ---------------------------------- Tab_3_4_ ND-Plot ----------------------------------
    # FEATURE: ND-Plot


class Plot2D(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.PlotTab:"Tab_Plotter" = parent
        self.AMaDiA: AMaDiA_Main_Window = self.PlotTab.AMaDiA
        super().__init__(parent)
        self.setObjectName("Tab_2D")
        self.gridLayout_12 = QtWidgets.QGridLayout(self)
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_12.setSpacing(0)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(3, 0, 3, 3)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.ButtonClear = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonClear.sizePolicy().hasHeightForWidth())
        self.ButtonClear.setSizePolicy(sizePolicy)
        self.ButtonClear.setObjectName("ButtonClear")
        self.gridLayout.addWidget(self.ButtonClear, 1, 1, 1, 1)
        self.Formula_Field = AW.AMaDiA_LineEdit(self)
        self.Formula_Field.setObjectName("Formula_Field")
        self.gridLayout.addWidget(self.Formula_Field, 1, 0, 1, 1)
        self.Button_Plot = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_Plot.sizePolicy().hasHeightForWidth())
        self.Button_Plot.setSizePolicy(sizePolicy)
        self.Button_Plot.setObjectName("Button_Plot")
        self.gridLayout.addWidget(self.Button_Plot, 1, 2, 1, 1)
        self.splitter = QtWidgets.QSplitter(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_upper = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_upper.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_upper.setObjectName("gridLayout_upper")
        self.TabWidget = QtWidgets.QTabWidget(self.layoutWidget1)
        self.TabWidget.setObjectName("TabWidget")
        self.Tab_1_History = QtWidgets.QWidget()
        self.Tab_1_History.setObjectName("Tab_1_History")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.Tab_1_History)
        self.gridLayout_5.setContentsMargins(3, 3, 3, 3)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.History = AW.HistoryWidget(self.Tab_1_History)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.History.sizePolicy().hasHeightForWidth())
        self.History.setSizePolicy(sizePolicy)
        self.History.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.History.setObjectName("History")
        self.gridLayout_5.addWidget(self.History, 0, 0, 1, 1)
        self.TabWidget.addTab(self.Tab_1_History, "")
        self.ConfigWidget = Plot2DConfig(self) ###################### CONFIG TAB
        self.TabWidget.addTab(self.ConfigWidget, "")
        self.gridLayout_upper.addWidget(self.TabWidget, 0, 2, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea_Layout = QtWidgets.QWidget()
        self.scrollArea_Layout.setGeometry(QtCore.QRect(0, 0, 618, 340))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_Layout.sizePolicy().hasHeightForWidth())
        self.scrollArea_Layout.setSizePolicy(sizePolicy)
        self.scrollArea_Layout.setObjectName("scrollArea_Layout")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.scrollArea_Layout)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.Display = AGeGW.MplWidget_2D_Plot(self.scrollArea_Layout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Display.sizePolicy().hasHeightForWidth())
        self.Display.setSizePolicy(sizePolicy)
        self.Display.setObjectName("Display")
        self.gridLayout_6.addWidget(self.Display, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollArea_Layout)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 3)
        self.gridLayout_12.addLayout(self.gridLayout, 0, 0, 1, 1)
        
        self.TabWidget.setCurrentIndex(0)
        self.splitter.setSizes([297,565])
        
        self.History.itemDoubleClicked.connect(self.F_Item_doubleClicked)
        self.Button_Plot.clicked.connect(lambda: self.F_Plot_Button())
        self.Formula_Field.returnPressed.connect(lambda: self.F_Plot_Button())
        self.ButtonClear.clicked.connect(lambda: self.F_Clear())
        
        try:
            self.Display.Canvas.mpl_connect('button_press_event', self.Display_Context_Menu)
        except:
            NC(lvl=4,msg="Could not update Display context menu",exc=sys.exc_info(),func="AMaDiA_Main_Window.OtherContextMenuSetup",win=self.windowTitle())
    
    def Display_Context_Menu(self,event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            menu = QtWidgets.QMenu()
            action = menu.addAction('Save Plot')
            action.triggered.connect(self.action_tab_3_tab_1_Display_SavePlt)
            cursor = QtGui.QCursor()
            menu.setPalette(self.palette())
            menu.setFont(self.font())
            menu.exec_(cursor.pos())
    
    def action_tab_3_tab_1_Display_SavePlt(self):
        if App().AGeLibPathOK:
            Filename = AF.cTimeFullStr("-")
            Filename += ".png"
            Filename = os.path.join(App().PlotPath,Filename)
            try:
                print(Filename)
                self.Display.Canvas.fig.savefig(Filename , facecolor=App().BG_Colour , edgecolor=App().BG_Colour )
            except:
                NC(lvl=1,msg="Could not save Plot: ",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
            else:
                NC(3,"Saved plot as: {}".format(Filename),func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
        else:
            print("Could not save Plot: Could not validate save location")
            NC(1,"Could not save Plot: Could not validate save location",func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=App().AGeLibPath)
    
    def F_Plot_Button(self):
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Creator(self.Formula_Field.text() , self.F_Plot_init,ID=ID, Iam=AC.Iam_2D_plot))
        self.AMaDiA.TC("NEW",self.Formula_Field.text() , self.F_Plot_init, Iam=AC.Iam_2D_plot)
    
    def F_Item_doubleClicked(self,item): #CRITICAL: double-clicking a cleared plot results in an error. The expected behaviour would be to reload the plot
        try:
            cycle = self.Display.Canvas.ax._get_lines.prop_cycler
            item.data(100).current_ax.set_color(next(cycle)['color'])
            self.Display.Canvas.draw()
            colour = item.data(100).current_ax.get_color()
            brush = QtGui.QBrush(QtGui.QColor(colour))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)
        except common_exceptions :
            NC(lvl=2,msg="Could not cycle colour",exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Item_doubleClicked",win=self.windowTitle())
    
    def F_Plot_init(self , AMaS_Object:"AC.AMaS"): # MAYBE: get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        if not AMaS_Object.Plot_is_initialized: AMaS_Object.init_2D_plot()
        AMaS_Object.plot_ratio = self.ConfigWidget.Axis_ratio_Checkbox.isChecked()
        AMaS_Object.plot_grid = self.ConfigWidget.DrawGrid_Checkbox.isChecked()
        AMaS_Object.plot_xmin = self.ConfigWidget.From_Spinbox.value()
        AMaS_Object.plot_xmax = self.ConfigWidget.To_Spinbox.value()
        AMaS_Object.plot_points = self.ConfigWidget.Points_Spinbox.value()
        
        if self.ConfigWidget.Points_comboBox.currentIndex() == 0:
            AMaS_Object.plot_per_unit = False
        elif self.ConfigWidget.Points_comboBox.currentIndex() == 1:
            AMaS_Object.plot_per_unit = True
        
        AMaS_Object.plot_xlim = self.ConfigWidget.XLim_Check.isChecked()
        if AMaS_Object.plot_xlim:
            xmin , xmax = self.ConfigWidget.XLim_min.value(), self.ConfigWidget.XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            AMaS_Object.plot_xlim_vals = (xmin , xmax)
        AMaS_Object.plot_ylim = self.ConfigWidget.YLim_Check.isChecked()
        if AMaS_Object.plot_ylim:
            ymin , ymax = self.ConfigWidget.YLim_min.value(), self.ConfigWidget.YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            AMaS_Object.plot_ylim_vals = (ymin , ymax)
        
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Worker(AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.F_Plot ,ID))
        self.AMaDiA.TC("WORK",AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.F_Plot)
    
    def F_Plot(self , AMaS_Object:"AC.AMaS"): # FEATURE: Add an option for each axis to scale logarithmically 
        # MAYBE: Add an extra option for this in the config tab... and change everything else accordingly
        #if self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked():
        #    self.Display.useTeX(True)
        #else:
        #    self.Display.useTeX(False)
        
        self.Display.useTeX(False)
        
        self.AMaDiA.HistoryHandler(AMaS_Object,3,1)
        
        try:
            if type(AMaS_Object.plot_x_vals) == int or type(AMaS_Object.plot_x_vals) == float:
                p = self.Display.Canvas.ax.axvline(x = AMaS_Object.plot_x_vals,color='red')
            else:
                p = self.Display.Canvas.ax.plot(AMaS_Object.plot_x_vals , AMaS_Object.plot_y_vals) #  (... , 'r--') for red colour and short lines
            try:
                AMaS_Object.current_ax = p[0]
            except common_exceptions:
                AMaS_Object.current_ax = p
            
            if AMaS_Object.plot_grid:
                self.Display.Canvas.ax.grid(True)
            else:
                self.Display.Canvas.ax.grid(False)
            if AMaS_Object.plot_ratio:
                self.Display.Canvas.ax.set_aspect('equal')
            else:
                self.Display.Canvas.ax.set_aspect('auto')
            
            self.Display.Canvas.ax.relim()
            self.Display.Canvas.ax.autoscale()
            if AMaS_Object.plot_xlim:
                self.Display.Canvas.ax.set_xlim(AMaS_Object.plot_xlim_vals)
            if AMaS_Object.plot_ylim:
                self.Display.Canvas.ax.set_ylim(AMaS_Object.plot_ylim_vals)
            
            try:
                colour = p[0].get_color()
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.Tab_3_1_ref.setForeground(brush)
            except common_exceptions:
                colour = "#FF0000"
                brush = QtGui.QBrush(QtGui.QColor(colour))
                brush.setStyle(QtCore.Qt.SolidPattern)
                AMaS_Object.Tab_3_1_ref.setForeground(brush)
            
            try:
                self.Display.Canvas.draw()
            except RuntimeError:
                ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.Display.useTeX(False)
                self.Display.Canvas.draw()
        except common_exceptions :
            NC(msg="y_vals = "+str(formatArray.repr(AMaS_Object.plot_y_vals))+str(type(AMaS_Object.plot_y_vals))+"\nYou can copy all elements in the contextmenu if advanced mode is active"
                    ,exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Plot",win=self.windowTitle(), input=AMaS_Object.Input)
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
    
    def F_RedrawPlot(self):
        xmin , xmax = self.ConfigWidget.XLim_min.value(), self.ConfigWidget.XLim_max.value()
        if xmax < xmin:
            xmax , xmin = xmin , xmax
        xlims = (xmin , xmax)
        ymin , ymax = self.ConfigWidget.YLim_min.value(), self.ConfigWidget.YLim_max.value()
        if ymax < ymin:
            ymax , ymin = ymin , ymax
        ylims = (ymin , ymax)
        if self.ConfigWidget.DrawGrid_Checkbox.isChecked():
            self.Display.Canvas.ax.grid(True)
        else:
            self.Display.Canvas.ax.grid(False)
        if self.ConfigWidget.Axis_ratio_Checkbox.isChecked():
            self.Display.Canvas.ax.set_aspect('equal')
        else:
            self.Display.Canvas.ax.set_aspect('auto')
        
        self.Display.Canvas.ax.relim()
        self.Display.Canvas.ax.autoscale()
        if self.ConfigWidget.XLim_Check.isChecked():
            self.Display.Canvas.ax.set_xlim(xlims)
        if self.ConfigWidget.YLim_Check.isChecked():
            self.Display.Canvas.ax.set_ylim(ylims)
        
        try:
            self.Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Display.useTeX(False)
            self.Display.Canvas.draw()
    
    def F_Clear(self):
        self.Display.useTeX(False)
        self.Display.Canvas.ax.clear()
        try:
            self.Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Display.useTeX(False)
            self.Display.Canvas.ax.clear()
            self.Display.Canvas.draw()
        brush = self.palette().text()
        for i in range(self.History.count()):
            self.History.item(i).setForeground(brush)
            self.History.item(i).data(100).current_ax = None
    
    
    
    def F_Sympy_Plot_Button(self): # CLEANUP: DELETE SymPy Plotter
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Creator(self.Formula_Field.text() , self.F_Sympy_Plot,ID))
        self.AMaDiA.TC("NEW",self.Formula_Field.text() , self.F_Sympy_Plot)
    
    def F_Sympy_Plot(self , AMaS_Object:"AC.AMaS"): # CLEANUP: DELETE SymPy Plotter
        try:
            #self.__SPFIG = plt.figure(num="SP")
            x,y,z = sympy.symbols('x y z')  # pylint: disable=unused-variable
            
            temp = AMaS_Object.cstr
            if AMaS_Object.cstr.count("=") == 1 :
                temp1 , temp2 = AMaS_Object.cstr.split("=",1)
                temp = "Eq("+temp1
                temp += ","
                temp += temp2
                temp += ")"
            temp = parse_expr(temp)
            xmin , xmax = self.ConfigWidget.XLim_min.value(), self.ConfigWidget.XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            xlims = (xmin , xmax)
            ymin , ymax = self.ConfigWidget.YLim_min.value(), self.ConfigWidget.YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            ylims = (ymin , ymax)
            if self.ConfigWidget.XLim_Check.isChecked() and self.ConfigWidget.YLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims , ylim = ylims)
            elif self.ConfigWidget.XLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims)
            elif self.ConfigWidget.YLim_Check.isChecked():
                sympy.plot(temp , ylim = ylims)
            else:
                sympy.plot(temp)#, num="SP",backend=matplotlib.backends.backend_qt5.FigureCanvasBase)
        except common_exceptions: # MAYBE: plot_implicit uses other syntax for limits. Maybe make this work
            ExceptionOutput(sys.exc_info())
            try:
                sympy.plot_implicit(temp)
            except common_exceptions:
                ExceptionOutput(sys.exc_info())
                try:
                    sympy.plot_implicit(parse_expr(AMaS_Object.string))
                except common_exceptions:
                    NC(exc=sys.exc_info(),func="AMaDiA_Main_Window.F_Sympy_Plot",win=self.windowTitle())


class Plot2DConfig(QtWidgets.QScrollArea):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget']) -> None:
        self.Plot2DTab:"Plot2D" = parent
        super().__init__(parent)
        self.setObjectName("ConfigWidget")
        self.setWidgetResizable(True)
        self.ScrollAreaWidgetContents = QtWidgets.QWidget()
        self.ScrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 221, 269))
        self.ScrollAreaWidgetContents.setObjectName("ScrollAreaWidgetContents")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.ScrollAreaWidgetContents)
        self.gridLayout_11.setContentsMargins(4, 4, 4, 4)
        self.gridLayout_11.setSpacing(3)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.YLim_Check = QtWidgets.QCheckBox(self.ScrollAreaWidgetContents)
        self.YLim_Check.setObjectName("YLim_Check")
        self.gridLayout_11.addWidget(self.YLim_Check, 8, 0, 1, 1)
        self.XLim_max = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.XLim_max.setDecimals(5)
        self.XLim_max.setMinimum(-1000000.0)
        self.XLim_max.setMaximum(1000000.0)
        self.XLim_max.setProperty("value", 5.0)
        self.XLim_max.setObjectName("XLim_max")
        self.gridLayout_11.addWidget(self.XLim_max, 7, 1, 1, 1)
        self.XLim_min = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.XLim_min.setDecimals(5)
        self.XLim_min.setMinimum(-1000000.0)
        self.XLim_min.setMaximum(1000000.0)
        self.XLim_min.setProperty("value", -5.0)
        self.XLim_min.setObjectName("XLim_min")
        self.gridLayout_11.addWidget(self.XLim_min, 7, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.ScrollAreaWidgetContents)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_11.addWidget(self.line_2, 4, 0, 1, 2)
        self.Axis_ratio_Checkbox = QtWidgets.QCheckBox(self.ScrollAreaWidgetContents)
        self.Axis_ratio_Checkbox.setObjectName("Axis_ratio_Checkbox")
        self.gridLayout_11.addWidget(self.Axis_ratio_Checkbox, 5, 1, 1, 1)
        self.To_Spinbox = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.To_Spinbox.setDecimals(5)
        self.To_Spinbox.setMinimum(-1000000.0)
        self.To_Spinbox.setMaximum(1000000.0)
        self.To_Spinbox.setProperty("value", 10.0)
        self.To_Spinbox.setObjectName("To_Spinbox")
        self.gridLayout_11.addWidget(self.To_Spinbox, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_11.addItem(spacerItem1, 12, 0, 1, 2)
        self.Points_comboBox = QtWidgets.QComboBox(self.ScrollAreaWidgetContents)
        self.Points_comboBox.setObjectName("Points_comboBox")
        self.Points_comboBox.addItem("")
        self.Points_comboBox.addItem("")
        self.gridLayout_11.addWidget(self.Points_comboBox, 2, 0, 1, 1)
        self.YLim_max = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.YLim_max.setDecimals(5)
        self.YLim_max.setMinimum(-1000000.0)
        self.YLim_max.setMaximum(1000000.0)
        self.YLim_max.setProperty("value", 50.0)
        self.YLim_max.setObjectName("YLim_max")
        self.gridLayout_11.addWidget(self.YLim_max, 9, 1, 1, 1)
        self.From_Spinbox = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.From_Spinbox.setDecimals(5)
        self.From_Spinbox.setMinimum(-1000000.0)
        self.From_Spinbox.setMaximum(1000000.0)
        self.From_Spinbox.setProperty("value", -10.0)
        self.From_Spinbox.setObjectName("From_Spinbox")
        self.gridLayout_11.addWidget(self.From_Spinbox, 0, 1, 1, 1)
        self.Label_from = QtWidgets.QLabel(self.ScrollAreaWidgetContents)
        self.Label_from.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Label_from.setObjectName("Label_from")
        self.gridLayout_11.addWidget(self.Label_from, 0, 0, 1, 1)
        self.XLim_Check = QtWidgets.QCheckBox(self.ScrollAreaWidgetContents)
        self.XLim_Check.setObjectName("XLim_Check")
        self.gridLayout_11.addWidget(self.XLim_Check, 6, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.ScrollAreaWidgetContents)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_11.addWidget(self.line, 11, 0, 1, 2)
        self.YLim_min = QtWidgets.QDoubleSpinBox(self.ScrollAreaWidgetContents)
        self.YLim_min.setDecimals(5)
        self.YLim_min.setMinimum(-1000000.0)
        self.YLim_min.setMaximum(1000000.0)
        self.YLim_min.setProperty("value", -25.0)
        self.YLim_min.setObjectName("YLim_min")
        self.gridLayout_11.addWidget(self.YLim_min, 9, 0, 1, 1)
        self.DrawGrid_Checkbox = QtWidgets.QCheckBox(self.ScrollAreaWidgetContents)
        self.DrawGrid_Checkbox.setChecked(True)
        self.DrawGrid_Checkbox.setObjectName("DrawGrid_Checkbox")
        self.gridLayout_11.addWidget(self.DrawGrid_Checkbox, 5, 0, 1, 1)
        self.Points_Spinbox = QtWidgets.QSpinBox(self.ScrollAreaWidgetContents)
        self.Points_Spinbox.setMinimum(2)
        self.Points_Spinbox.setMaximum(100000)
        self.Points_Spinbox.setProperty("value", 1000)
        self.Points_Spinbox.setObjectName("Points_Spinbox")
        self.gridLayout_11.addWidget(self.Points_Spinbox, 2, 1, 1, 1)
        self.Label_to = QtWidgets.QLabel(self.ScrollAreaWidgetContents)
        self.Label_to.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Label_to.setObjectName("Label_to")
        self.gridLayout_11.addWidget(self.Label_to, 1, 0, 1, 1)
        self.Button_Plot_SymPy = QtWidgets.QPushButton(self.ScrollAreaWidgetContents)
        self.Button_Plot_SymPy.setObjectName("Button_Plot_SymPy")
        self.gridLayout_11.addWidget(self.Button_Plot_SymPy, 13, 1, 1, 1)
        self.RedrawPlot_Button = QtWidgets.QPushButton(self.ScrollAreaWidgetContents)
        self.RedrawPlot_Button.setObjectName("RedrawPlot_Button")
        self.gridLayout_11.addWidget(self.RedrawPlot_Button, 10, 0, 1, 2)
        self.Button_SavePlot = QtWidgets.QPushButton(self.ScrollAreaWidgetContents)
        self.Button_SavePlot.setObjectName("Button_SavePlot")
        self.gridLayout_11.addWidget(self.Button_SavePlot, 13, 0, 1, 1)
        self.setWidget(self.ScrollAreaWidgetContents)
        
        self.Button_Plot_SymPy.setVisible(False) # CLEANUP: The Control Tab Has broken the Sympy plotter... Repairing it is not worth it... Remove this function...
        self.Button_Plot_SymPy.clicked.connect(lambda: self.Plot2DTab.F_Sympy_Plot_Button())
        self.RedrawPlot_Button.clicked.connect(lambda: self.Plot2DTab.F_RedrawPlot())
        self.Button_SavePlot.clicked.connect(lambda: self.Plot2DTab.action_tab_3_tab_1_Display_SavePlt())
