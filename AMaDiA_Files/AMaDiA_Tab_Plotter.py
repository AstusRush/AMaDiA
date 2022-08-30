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
        self.Tab_2D = QtWidgets.QWidget()
        self.Tab_2D.setObjectName("Tab_2D")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.Tab_2D)
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_12.setSpacing(0)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.Tab_2D_gridLayout = QtWidgets.QGridLayout()
        self.Tab_2D_gridLayout.setContentsMargins(3, 0, 3, 3)
        self.Tab_2D_gridLayout.setSpacing(3)
        self.Tab_2D_gridLayout.setObjectName("Tab_2D_gridLayout")
        self.Tab_2D_ButtonClear = QtWidgets.QPushButton(self.Tab_2D)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_ButtonClear.sizePolicy().hasHeightForWidth())
        self.Tab_2D_ButtonClear.setSizePolicy(sizePolicy)
        self.Tab_2D_ButtonClear.setObjectName("Tab_2D_ButtonClear")
        self.Tab_2D_gridLayout.addWidget(self.Tab_2D_ButtonClear, 1, 1, 1, 1)
        self.Tab_2D_Formula_Field = AW.AMaDiA_LineEdit(self.Tab_2D)
        self.Tab_2D_Formula_Field.setObjectName("Tab_2D_Formula_Field")
        self.Tab_2D_gridLayout.addWidget(self.Tab_2D_Formula_Field, 1, 0, 1, 1)
        self.Tab_2D_Button_Plot = QtWidgets.QPushButton(self.Tab_2D)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_Button_Plot.sizePolicy().hasHeightForWidth())
        self.Tab_2D_Button_Plot.setSizePolicy(sizePolicy)
        self.Tab_2D_Button_Plot.setObjectName("Tab_2D_Button_Plot")
        self.Tab_2D_gridLayout.addWidget(self.Tab_2D_Button_Plot, 1, 2, 1, 1)
        self.Tab_2D_splitter = QtWidgets.QSplitter(self.Tab_2D)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_splitter.sizePolicy().hasHeightForWidth())
        self.Tab_2D_splitter.setSizePolicy(sizePolicy)
        self.Tab_2D_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.Tab_2D_splitter.setObjectName("Tab_2D_splitter")
        self.layoutWidget1 = QtWidgets.QWidget(self.Tab_2D_splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.Tab_2D_gridLayout_upper = QtWidgets.QGridLayout(self.layoutWidget1)
        self.Tab_2D_gridLayout_upper.setContentsMargins(0, 0, 0, 0)
        self.Tab_2D_gridLayout_upper.setObjectName("Tab_2D_gridLayout_upper")
        self.Tab_2D_TabWidget = QtWidgets.QTabWidget(self.layoutWidget1)
        self.Tab_2D_TabWidget.setObjectName("Tab_2D_TabWidget")
        self.Tab_2D_Tab_1_History = QtWidgets.QWidget()
        self.Tab_2D_Tab_1_History.setObjectName("Tab_2D_Tab_1_History")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.Tab_2D_Tab_1_History)
        self.gridLayout_5.setContentsMargins(3, 3, 3, 3)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.Tab_2D_History = AW.HistoryWidget(self.Tab_2D_Tab_1_History)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_History.sizePolicy().hasHeightForWidth())
        self.Tab_2D_History.setSizePolicy(sizePolicy)
        self.Tab_2D_History.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Tab_2D_History.setObjectName("Tab_2D_History")
        self.gridLayout_5.addWidget(self.Tab_2D_History, 0, 0, 1, 1)
        self.Tab_2D_TabWidget.addTab(self.Tab_2D_Tab_1_History, "")
        self.Tab_2D_Tab_2_Config = QtWidgets.QWidget()
        self.Tab_2D_Tab_2_Config.setObjectName("Tab_2D_Tab_2_Config")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.Tab_2D_Tab_2_Config)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.Tab_2D_Tab_2_Config_scrollArea = QtWidgets.QScrollArea(self.Tab_2D_Tab_2_Config)
        self.Tab_2D_Tab_2_Config_scrollArea.setWidgetResizable(True)
        self.Tab_2D_Tab_2_Config_scrollArea.setObjectName("Tab_2D_Tab_2_Config_scrollArea")
        self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 221, 269))
        self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents.setObjectName("Tab_2D_Tab_2_Config_scrollAreaWidgetContents")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.gridLayout_11.setContentsMargins(4, 4, 4, 4)
        self.gridLayout_11.setSpacing(3)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.Tab_2D_YLim_Check = QtWidgets.QCheckBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_YLim_Check.setObjectName("Tab_2D_YLim_Check")
        self.gridLayout_11.addWidget(self.Tab_2D_YLim_Check, 8, 0, 1, 1)
        self.Tab_2D_XLim_max = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_XLim_max.setDecimals(5)
        self.Tab_2D_XLim_max.setMinimum(-1000000.0)
        self.Tab_2D_XLim_max.setMaximum(1000000.0)
        self.Tab_2D_XLim_max.setProperty("value", 5.0)
        self.Tab_2D_XLim_max.setObjectName("Tab_2D_XLim_max")
        self.gridLayout_11.addWidget(self.Tab_2D_XLim_max, 7, 1, 1, 1)
        self.Tab_2D_XLim_min = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_XLim_min.setDecimals(5)
        self.Tab_2D_XLim_min.setMinimum(-1000000.0)
        self.Tab_2D_XLim_min.setMaximum(1000000.0)
        self.Tab_2D_XLim_min.setProperty("value", -5.0)
        self.Tab_2D_XLim_min.setObjectName("Tab_2D_XLim_min")
        self.gridLayout_11.addWidget(self.Tab_2D_XLim_min, 7, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_11.addWidget(self.line_2, 4, 0, 1, 2)
        self.Tab_2D_Axis_ratio_Checkbox = QtWidgets.QCheckBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Axis_ratio_Checkbox.setObjectName("Tab_2D_Axis_ratio_Checkbox")
        self.gridLayout_11.addWidget(self.Tab_2D_Axis_ratio_Checkbox, 5, 1, 1, 1)
        self.Tab_2D_To_Spinbox = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_To_Spinbox.setDecimals(5)
        self.Tab_2D_To_Spinbox.setMinimum(-1000000.0)
        self.Tab_2D_To_Spinbox.setMaximum(1000000.0)
        self.Tab_2D_To_Spinbox.setProperty("value", 10.0)
        self.Tab_2D_To_Spinbox.setObjectName("Tab_2D_To_Spinbox")
        self.gridLayout_11.addWidget(self.Tab_2D_To_Spinbox, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_11.addItem(spacerItem1, 12, 0, 1, 2)
        self.Tab_2D_Points_comboBox = QtWidgets.QComboBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Points_comboBox.setObjectName("Tab_2D_Points_comboBox")
        self.Tab_2D_Points_comboBox.addItem("")
        self.Tab_2D_Points_comboBox.addItem("")
        self.gridLayout_11.addWidget(self.Tab_2D_Points_comboBox, 2, 0, 1, 1)
        self.Tab_2D_YLim_max = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_YLim_max.setDecimals(5)
        self.Tab_2D_YLim_max.setMinimum(-1000000.0)
        self.Tab_2D_YLim_max.setMaximum(1000000.0)
        self.Tab_2D_YLim_max.setProperty("value", 50.0)
        self.Tab_2D_YLim_max.setObjectName("Tab_2D_YLim_max")
        self.gridLayout_11.addWidget(self.Tab_2D_YLim_max, 9, 1, 1, 1)
        self.Tab_2D_From_Spinbox = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_From_Spinbox.setDecimals(5)
        self.Tab_2D_From_Spinbox.setMinimum(-1000000.0)
        self.Tab_2D_From_Spinbox.setMaximum(1000000.0)
        self.Tab_2D_From_Spinbox.setProperty("value", -10.0)
        self.Tab_2D_From_Spinbox.setObjectName("Tab_2D_From_Spinbox")
        self.gridLayout_11.addWidget(self.Tab_2D_From_Spinbox, 0, 1, 1, 1)
        self.Tab_2D_Label_from = QtWidgets.QLabel(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Label_from.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Tab_2D_Label_from.setObjectName("Tab_2D_Label_from")
        self.gridLayout_11.addWidget(self.Tab_2D_Label_from, 0, 0, 1, 1)
        self.Tab_2D_XLim_Check = QtWidgets.QCheckBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_XLim_Check.setObjectName("Tab_2D_XLim_Check")
        self.gridLayout_11.addWidget(self.Tab_2D_XLim_Check, 6, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_11.addWidget(self.line, 11, 0, 1, 2)
        self.Tab_2D_YLim_min = QtWidgets.QDoubleSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_YLim_min.setDecimals(5)
        self.Tab_2D_YLim_min.setMinimum(-1000000.0)
        self.Tab_2D_YLim_min.setMaximum(1000000.0)
        self.Tab_2D_YLim_min.setProperty("value", -25.0)
        self.Tab_2D_YLim_min.setObjectName("Tab_2D_YLim_min")
        self.gridLayout_11.addWidget(self.Tab_2D_YLim_min, 9, 0, 1, 1)
        self.Tab_2D_Draw_Grid_Checkbox = QtWidgets.QCheckBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Draw_Grid_Checkbox.setChecked(True)
        self.Tab_2D_Draw_Grid_Checkbox.setObjectName("Tab_2D_Draw_Grid_Checkbox")
        self.gridLayout_11.addWidget(self.Tab_2D_Draw_Grid_Checkbox, 5, 0, 1, 1)
        self.Tab_2D_Points_Spinbox = QtWidgets.QSpinBox(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Points_Spinbox.setMinimum(2)
        self.Tab_2D_Points_Spinbox.setMaximum(100000)
        self.Tab_2D_Points_Spinbox.setProperty("value", 1000)
        self.Tab_2D_Points_Spinbox.setObjectName("Tab_2D_Points_Spinbox")
        self.gridLayout_11.addWidget(self.Tab_2D_Points_Spinbox, 2, 1, 1, 1)
        self.Tab_2D_Label_to = QtWidgets.QLabel(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Label_to.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Tab_2D_Label_to.setObjectName("Tab_2D_Label_to")
        self.gridLayout_11.addWidget(self.Tab_2D_Label_to, 1, 0, 1, 1)
        self.Tab_2D_Button_Plot_SymPy = QtWidgets.QPushButton(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Button_Plot_SymPy.setObjectName("Tab_2D_Button_Plot_SymPy")
        self.gridLayout_11.addWidget(self.Tab_2D_Button_Plot_SymPy, 13, 1, 1, 1)
        self.Tab_2D_RedrawPlot_Button = QtWidgets.QPushButton(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_RedrawPlot_Button.setObjectName("Tab_2D_RedrawPlot_Button")
        self.gridLayout_11.addWidget(self.Tab_2D_RedrawPlot_Button, 10, 0, 1, 2)
        self.Tab_2D_Button_SavePlot = QtWidgets.QPushButton(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.Tab_2D_Button_SavePlot.setObjectName("Tab_2D_Button_SavePlot")
        self.gridLayout_11.addWidget(self.Tab_2D_Button_SavePlot, 13, 0, 1, 1)
        self.Tab_2D_Tab_2_Config_scrollArea.setWidget(self.Tab_2D_Tab_2_Config_scrollAreaWidgetContents)
        self.gridLayout_8.addWidget(self.Tab_2D_Tab_2_Config_scrollArea, 12, 0, 1, 1)
        self.Tab_2D_TabWidget.addTab(self.Tab_2D_Tab_2_Config, "")
        self.Tab_2D_gridLayout_upper.addWidget(self.Tab_2D_TabWidget, 0, 2, 1, 1)
        self.Tab_2D_scrollArea = QtWidgets.QScrollArea(self.Tab_2D_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_scrollArea.sizePolicy().hasHeightForWidth())
        self.Tab_2D_scrollArea.setSizePolicy(sizePolicy)
        self.Tab_2D_scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Tab_2D_scrollArea.setWidgetResizable(True)
        self.Tab_2D_scrollArea.setObjectName("Tab_2D_scrollArea")
        self.Tab_2D_scrollArea_Layout = QtWidgets.QWidget()
        self.Tab_2D_scrollArea_Layout.setGeometry(QtCore.QRect(0, 0, 618, 340))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_scrollArea_Layout.sizePolicy().hasHeightForWidth())
        self.Tab_2D_scrollArea_Layout.setSizePolicy(sizePolicy)
        self.Tab_2D_scrollArea_Layout.setObjectName("Tab_2D_scrollArea_Layout")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.Tab_2D_scrollArea_Layout)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.Tab_2D_Display = AGeGW.MplWidget_2D_Plot(self.Tab_2D_scrollArea_Layout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tab_2D_Display.sizePolicy().hasHeightForWidth())
        self.Tab_2D_Display.setSizePolicy(sizePolicy)
        self.Tab_2D_Display.setObjectName("Tab_2D_Display")
        self.gridLayout_6.addWidget(self.Tab_2D_Display, 0, 0, 1, 1)
        self.Tab_2D_scrollArea.setWidget(self.Tab_2D_scrollArea_Layout)
        self.Tab_2D_gridLayout.addWidget(self.Tab_2D_splitter, 0, 0, 1, 3)
        self.gridLayout_12.addLayout(self.Tab_2D_gridLayout, 0, 0, 1, 1)
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
        
        self.Tab_2D_Button_Plot_SymPy.setVisible(False) # CLEANUP: The Control Tab Has broken the Sympy plotter... Repairing it is not worth it... Remove this function...
        
        self.TabWidget.setCurrentIndex(0)
        self.Tab_2D_TabWidget.setCurrentIndex(0)
        self.Tab_2D_splitter.setSizes([297,565])
        
        self.Tab_2D_History.itemDoubleClicked.connect(self.Tab_2D_F_Item_doubleClicked)
        self.Tab_2D_Button_Plot.clicked.connect(lambda: self.Tab_2D_F_Plot_Button())
        self.Tab_2D_Formula_Field.returnPressed.connect(lambda: self.Tab_2D_F_Plot_Button())
        self.Tab_2D_ButtonClear.clicked.connect(lambda: self.Tab_2D_F_Clear())
        self.Tab_2D_Button_Plot_SymPy.clicked.connect(lambda: self.Tab_2D_F_Sympy_Plot_Button())
        self.Tab_2D_RedrawPlot_Button.clicked.connect(lambda: self.Tab_2D_F_RedrawPlot())
        self.Tab_2D_Button_SavePlot.clicked.connect(lambda: self.action_tab_3_tab_1_Display_SavePlt())
        
        self.Tab_Complex_ComplexWidget.S_Plot.connect(lambda: self.Tab_Complex_F_Plot_Button())
        
        try:
            self.Tab_2D_Display.Canvas.mpl_connect('button_press_event', self.Tab_2D_Display_Context_Menu)
        except:
            NC(lvl=4,msg="Could not update Tab_2D_Display context menu",exc=sys.exc_info(),func="AMaDiA_Main_Window.OtherContextMenuSetup",win=self.windowTitle())
    
    def Tab_2D_Display_Context_Menu(self,event):
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
                self.Tab_2D_Display.Canvas.fig.savefig(Filename , facecolor=App().BG_Colour , edgecolor=App().BG_Colour )
            except:
                NC(lvl=1,msg="Could not save Plot: ",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
            else:
                NC(3,"Saved plot as: {}".format(Filename),func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=Filename)
        else:
            print("Could not save Plot: Could not validate save location")
            NC(1,"Could not save Plot: Could not validate save location",func="AMaDiA_Main_Window.Tab_3.action_tab_3_tab_1_Display_SavePlt",win=self.windowTitle(),input=App().AGeLibPath)
    
 # ---------------------------------- Tab_3_1_ 2D-Plot ----------------------------------
    def Tab_2D_F_Plot_Button(self):
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Creator(self.Tab_2D_Formula_Field.text() , self.Tab_2D_F_Plot_init,ID=ID, Iam=AC.Iam_2D_plot))
        self.AMaDiA.TC("NEW",self.Tab_2D_Formula_Field.text() , self.Tab_2D_F_Plot_init, Iam=AC.Iam_2D_plot)
    
    def Tab_2D_F_Item_doubleClicked(self,item):
        try:
            cycle = self.Tab_2D_Display.Canvas.ax._get_lines.prop_cycler
            item.data(100).current_ax.set_color(next(cycle)['color'])
            self.Tab_2D_Display.Canvas.draw()
            colour = item.data(100).current_ax.get_color()
            brush = QtGui.QBrush(QtGui.QColor(colour))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)
        except common_exceptions :
            NC(lvl=2,msg="Could not cycle colour",exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_2D_F_Item_doubleClicked",win=self.windowTitle())
    
    def Tab_2D_F_Plot_init(self , AMaS_Object:"AC.AMaS"): # MAYBE: get these values upon creation in case the User acts before the LaTeX conversion finishes? (Not very important)
        if not AMaS_Object.Plot_is_initialized: AMaS_Object.init_2D_plot()
        AMaS_Object.plot_ratio = self.Tab_2D_Axis_ratio_Checkbox.isChecked()
        AMaS_Object.plot_grid = self.Tab_2D_Draw_Grid_Checkbox.isChecked()
        AMaS_Object.plot_xmin = self.Tab_2D_From_Spinbox.value()
        AMaS_Object.plot_xmax = self.Tab_2D_To_Spinbox.value()
        AMaS_Object.plot_points = self.Tab_2D_Points_Spinbox.value()
        
        if self.Tab_2D_Points_comboBox.currentIndex() == 0:
            AMaS_Object.plot_per_unit = False
        elif self.Tab_2D_Points_comboBox.currentIndex() == 1:
            AMaS_Object.plot_per_unit = True
        
        AMaS_Object.plot_xlim = self.Tab_2D_XLim_Check.isChecked()
        if AMaS_Object.plot_xlim:
            xmin , xmax = self.Tab_2D_XLim_min.value(), self.Tab_2D_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            AMaS_Object.plot_xlim_vals = (xmin , xmax)
        AMaS_Object.plot_ylim = self.Tab_2D_YLim_Check.isChecked()
        if AMaS_Object.plot_ylim:
            ymin , ymax = self.Tab_2D_YLim_min.value(), self.Tab_2D_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            AMaS_Object.plot_ylim_vals = (ymin , ymax)
        
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Worker(AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.Tab_2D_F_Plot ,ID))
        self.AMaDiA.TC("WORK",AMaS_Object,lambda:AC.AMaS.Plot_2D_Calc_Values(AMaS_Object),self.Tab_2D_F_Plot)
    
    def Tab_2D_F_Plot(self , AMaS_Object:"AC.AMaS"): # FEATURE: Add an option for each axis to scale logarithmically 
        # MAYBE: Add an extra option for this in the config tab... and change everything else accordingly
        #if self.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked():
        #    self.Tab_2D_Display.useTeX(True)
        #else:
        #    self.Tab_2D_Display.useTeX(False)
        
        self.Tab_2D_Display.useTeX(False)
        
        self.AMaDiA.HistoryHandler(AMaS_Object,3,1)
        
        try:
            if type(AMaS_Object.plot_x_vals) == int or type(AMaS_Object.plot_x_vals) == float:
                p = self.Tab_2D_Display.Canvas.ax.axvline(x = AMaS_Object.plot_x_vals,color='red')
            else:
                p = self.Tab_2D_Display.Canvas.ax.plot(AMaS_Object.plot_x_vals , AMaS_Object.plot_y_vals) #  (... , 'r--') for red colour and short lines
            try:
                AMaS_Object.current_ax = p[0]
            except common_exceptions:
                AMaS_Object.current_ax = p
            
            if AMaS_Object.plot_grid:
                self.Tab_2D_Display.Canvas.ax.grid(True)
            else:
                self.Tab_2D_Display.Canvas.ax.grid(False)
            if AMaS_Object.plot_ratio:
                self.Tab_2D_Display.Canvas.ax.set_aspect('equal')
            else:
                self.Tab_2D_Display.Canvas.ax.set_aspect('auto')
            
            self.Tab_2D_Display.Canvas.ax.relim()
            self.Tab_2D_Display.Canvas.ax.autoscale()
            if AMaS_Object.plot_xlim:
                self.Tab_2D_Display.Canvas.ax.set_xlim(AMaS_Object.plot_xlim_vals)
            if AMaS_Object.plot_ylim:
                self.Tab_2D_Display.Canvas.ax.set_ylim(AMaS_Object.plot_ylim_vals)
            
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
                self.Tab_2D_Display.Canvas.draw()
            except RuntimeError:
                ExceptionOutput(sys.exc_info(),False)
                print("Trying to output without LaTeX")
                self.Tab_2D_Display.useTeX(False)
                self.Tab_2D_Display.Canvas.draw()
        except common_exceptions :
            NC(msg="y_vals = "+str(formatArray.repr(AMaS_Object.plot_y_vals))+str(type(AMaS_Object.plot_y_vals))+"\nYou can copy all elements in the contextmenu if advanced mode is active"
                    ,exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_2D_F_Plot",win=self.windowTitle(), input=AMaS_Object.Input)
            #print("y_vals = ")
            #print(AMaS_Object.plot_y_vals)
            #print(type(AMaS_Object.plot_y_vals))
            AMaS_Object.plottable = False
    
    def Tab_2D_F_RedrawPlot(self):
        xmin , xmax = self.Tab_2D_XLim_min.value(), self.Tab_2D_XLim_max.value()
        if xmax < xmin:
            xmax , xmin = xmin , xmax
        xlims = (xmin , xmax)
        ymin , ymax = self.Tab_2D_YLim_min.value(), self.Tab_2D_YLim_max.value()
        if ymax < ymin:
            ymax , ymin = ymin , ymax
        ylims = (ymin , ymax)
        if self.Tab_2D_Draw_Grid_Checkbox.isChecked():
            self.Tab_2D_Display.Canvas.ax.grid(True)
        else:
            self.Tab_2D_Display.Canvas.ax.grid(False)
        if self.Tab_2D_Axis_ratio_Checkbox.isChecked():
            self.Tab_2D_Display.Canvas.ax.set_aspect('equal')
        else:
            self.Tab_2D_Display.Canvas.ax.set_aspect('auto')
        
        self.Tab_2D_Display.Canvas.ax.relim()
        self.Tab_2D_Display.Canvas.ax.autoscale()
        if self.Tab_2D_XLim_Check.isChecked():
            self.Tab_2D_Display.Canvas.ax.set_xlim(xlims)
        if self.Tab_2D_YLim_Check.isChecked():
            self.Tab_2D_Display.Canvas.ax.set_ylim(ylims)
        
        try:
            self.Tab_2D_Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_2D_Display.useTeX(False)
            self.Tab_2D_Display.Canvas.draw()
    
    def Tab_2D_F_Clear(self):
        self.Tab_2D_Display.useTeX(False)
        self.Tab_2D_Display.Canvas.ax.clear()
        try:
            self.Tab_2D_Display.Canvas.draw()
        except RuntimeError:
            ExceptionOutput(sys.exc_info(),False)
            print("Trying to output without LaTeX")
            self.Tab_2D_Display.useTeX(False)
            self.Tab_2D_Display.Canvas.ax.clear()
            self.Tab_2D_Display.Canvas.draw()
        brush = self.palette().text()
        for i in range(self.Tab_2D_History.count()):
            self.Tab_2D_History.item(i).setForeground(brush)
            self.Tab_2D_History.item(i).data(100).current_ax = None
    
    
    
    def Tab_2D_F_Sympy_Plot_Button(self): # CLEANUP: DELETE SymPy Plotter
        #self.AMaDiA.TC(lambda ID: AT.AMaS_Creator(self.Tab_2D_Formula_Field.text() , self.Tab_2D_F_Sympy_Plot,ID))
        self.AMaDiA.TC("NEW",self.Tab_2D_Formula_Field.text() , self.Tab_2D_F_Sympy_Plot)
    
    def Tab_2D_F_Sympy_Plot(self , AMaS_Object:"AC.AMaS"): # CLEANUP: DELETE SymPy Plotter
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
            xmin , xmax = self.Tab_2D_XLim_min.value(), self.Tab_2D_XLim_max.value()
            if xmax < xmin:
                xmax , xmin = xmin , xmax
            xlims = (xmin , xmax)
            ymin , ymax = self.Tab_2D_YLim_min.value(), self.Tab_2D_YLim_max.value()
            if ymax < ymin:
                ymax , ymin = ymin , ymax
            ylims = (ymin , ymax)
            if self.Tab_2D_XLim_Check.isChecked() and self.Tab_2D_YLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims , ylim = ylims)
            elif self.Tab_2D_XLim_Check.isChecked():
                sympy.plot(temp , xlim = xlims)
            elif self.Tab_2D_YLim_Check.isChecked():
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
                    NC(exc=sys.exc_info(),func="AMaDiA_Main_Window.Tab_2D_F_Sympy_Plot",win=self.windowTitle())
 
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
 
