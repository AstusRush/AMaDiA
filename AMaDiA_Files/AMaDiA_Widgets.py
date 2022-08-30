# This Python file uses the following encoding: utf-8

# if__name__ == "__main__":
#     pass


import sys
sys.path.append('..')
from AGeLib import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #CLEANUP: Delete this line?
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('Qt5Agg')
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
import numpy as np
import scipy
import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
from sympy.parsing.sympy_parser import parse_expr
import time

import warnings

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART

import importlib
def ReloadModules():
    importlib.reload(AF)
    importlib.reload(AC)
    importlib.reload(ART)



# -----------------------------------------------------------------------------------------------------------------

#FEATURE: Add autocomplete for AMaDiA_TextEdit and AMaDiA_LineEdit. For Example:
#       "sq" should suggest "√(*)" with * being the cursor position
#       "int" should suggest "∫{(*)()}dx" or "∫{(*From*)(To)} f(x) dx" with "*From*" being selected or even fancier

class AMaDiA_TextEdit(AGeWidgets.TextEdit):
    def __init__(self, parent=None):
        super(AMaDiA_TextEdit, self).__init__(parent)
        self.Highlighter = LineEditHighlighter(self.document(), self)
        self.cursorPositionChanged.connect(self.CursorPositionChanged)

    def CursorPositionChanged(self):
        self.Highlighter.blockSignals(True) #block signals because rehighlight might trigger the change signal? but this blocking might also be unnecessary
        self.Highlighter.rehighlight()
        self.Highlighter.blockSignals(False)
        cursor = self.textCursor()
        curPos = cursor.position()
        self.document().contentsChange.emit(curPos,0,0)


class AMaDiA_LineEdit(AGeWidgets.LineEdit):
    def __init__(self, parent=None):
        super(AMaDiA_LineEdit, self).__init__(parent)
        self.Highlighter = LineEditHighlighter(self.document(), self)
        self.cursorPositionChanged.connect(self.CursorPositionChanged)

    def CursorPositionChanged(self):
        cursor = self.textCursor()
        curPos = cursor.position()
        self.document().contentsChange.emit(curPos,0,0)

    # TODO: Make an option that creates a vector instead of adding everything when a multiline text is pasted into a AMaDiA_LineEdit



class LineEditHighlighter(QtGui.QSyntaxHighlighter): # TODO: performance, Fix FindPair
    def __init__(self, document, Widget):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        self.Widget = Widget
        self.init_Styles()
        try:
            self.enabled = QtWidgets.QApplication.instance().optionWindow.cb_O_PairHighlighter.isChecked()
        except common_exceptions:
            self.enabled = True
        QtWidgets.QApplication.instance().S_Highlighter.connect(self.ToggleActive)

        ## init the rules # Currently Unused...
        #rules = [(r'%s' % b, 0, self.STYLES['brace']) for b in self.braces]
        #self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules] #REMINDER: QtCore.QRegExp has been replaced by QtCore.QRegularExpression in Qt6

        App().S_ColourChanged.connect(self.UpdateFormats)

    def ToggleActive(self,Active):
        self.enabled = Active

    def UpdateFormats(self):
        self.RedFormat.setForeground(App().PenColours["Red"].color())
        self.GreenFormat.setForeground(App().PenColours["Green"].color())
        self.BlueFormat.setForeground(App().PenColours["Blue"].color())
        self.CyanFormat.setForeground(App().PenColours["Cyan"].color())
        self.MagentaFormat.setForeground(App().PenColours["Magenta"].color())

    def init_Styles(self):
        # init Lists
        self.braces = ['\{', '\}', '\(', '\)', '\[', '\]'] # pylint: disable=anomalous-backslash-in-string

        # Init Formats
        self.RedFormat = QtGui.QTextCharFormat()
        self.RedFormat.setForeground(QtGui.QColor('red'))
        self.GreenFormat = QtGui.QTextCharFormat()
        self.GreenFormat.setForeground(QtGui.QColor('green'))
        self.BlueFormat = QtGui.QTextCharFormat()
        self.BlueFormat.setForeground(QtGui.QColor('blue'))
        self.CyanFormat = QtGui.QTextCharFormat()
        self.CyanFormat.setForeground(QtGui.QColor('cyan'))
        self.MagentaFormat = QtGui.QTextCharFormat()
        self.MagentaFormat.setForeground(QtGui.QColor('magenta'))

        # Collect all Formats in a dictionary
        self.STYLES = {'brace': self.RedFormat,'pair': self.RedFormat}

    def highlightBlock(self, text):
        if not self.enabled:
            self.setCurrentBlockState(0)
            return
        cursor = self.Widget.textCursor()
        if not cursor.block() == self.currentBlock():
            #self.setCurrentBlockState(0)
            return
        curPos = cursor.positionInBlock()
        pattern = ""
        TheList = []
        for i in ART.LIST_l_normal_pairs:
            for j in i:
                if not j[0] in TheList:
                    TheList.append(j[0])
                if not j[1] in TheList:
                    TheList.append(j[1])
        TheList.sort(key=len,reverse=True)
        for i in TheList:
            pattern += re.escape(i)
            pattern += "|"
            pattern += re.escape(i)
            pattern += "|"
        pattern = pattern[:-1]
        braces_list = [[m.start(),m.end()] for m in re.finditer(pattern, text)]
        braces_list.sort(key=AF.takeFirst,reverse=False)
        for i in braces_list:
            if curPos <= i[1] and curPos >= i[0]:
                self.setFormat(i[0], i[1]-i[0], self.STYLES['pair'])
                Element = text[i[0]:i[1]]
                try:
                    Pair = AF.Counterpart(Element, ListOfLists=ART.LIST_l_normal_pairs, Both=True)
                except Exception:
                    ExceptionOutput(sys.exc_info())#break
                if Pair[0] == Element:
                    Pair = Pair.FirstResult
                    a,b = AF.FindPair(text,Pair,i[0])
                    self.setFormat(b, len(Pair[1]), self.STYLES['pair'])
                else:
                    # IMPROVE: Opening pair finder
                    
                    #---------method1----------
                    # FIXME: Does not work!!!!!!!!!!!!!! NEEDS FIX OF AF.FindPair ???
                        #k=0
                        #found = False
                        #while k < len(Pair):
                        #    a,b = AF.FindPair(text,Pair.List[k],end=i[1])
                        #    if b == i[0] and Pair.List[k][1] == Element:
                        #        c,d = a, len(Pair.List[k][0])
                        #        found = True
                        #    k+=1
                    #if found:
                    #    self.setFormat(c, d, self.STYLES['pair'])
                    
                    
                    #---------method2----------
                    found = False
                    for j in braces_list:
                        Element2 = text[j[0]:j[1]]
                        try:
                            Pair2 = AF.Counterpart(Element2, ListOfLists=ART.LIST_l_normal_pairs, Both=True)
                        except Exception:
                            ExceptionOutput(sys.exc_info())#break
                        else: #VALIDATE: This "else" was added to ensure that Pair2 exists but this code ran without problems before...
                            #               (previously the following code was always executed)
                            #               What did I think when I wrote this?
                            #               Why did I use the ExceptionOutput? Why did I want to use "break" instead of "continue"?
                            k=0
                            while k < len(Pair2):
                                a,b = AF.FindPair(text,Pair2.List[k],j[0])
                                if b == i[0] and Pair2.List[k][1] == Element:
                                    c,d = a, len(Pair2.List[k][0])
                                    found = True
                                    break
                                k+=1
                    if found:
                        self.setFormat(c, d, self.STYLES['pair'])
                
                
                break
        
        self.setCurrentBlockState(0)


# -----------------------------------------------------------------------------------------------------------------

class AMaDiA_TableWidget(AGeWidgets.TableWidget):
    def __init__(self, parent=None):
        super(AMaDiA_TableWidget, self).__init__(parent)
        self.TheDelegate = AMaDiA_TableWidget_Delegate(self)
        self.setItemDelegate(self.TheDelegate)

class AMaDiA_TableWidget_Delegate(AGeWidgets.TableWidget_Delegate):
    def __init__(self, parent=None):
        super(AMaDiA_TableWidget_Delegate, self).__init__(parent)
    
    def createEditor(self, parent, options, index):
        return AMaDiA_LineEdit(parent)


# -----------------------------------------------------------------------------------------------------------------

class HistoryWidget(AGeWidgets.ListWidget):
    def __init__(self, parent=None):
        super(HistoryWidget, self).__init__(parent)
        self.installEventFilter(self)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)==1:
                    item = SelectedItems[0]
                    if QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Normal":
                        if (self == QtWidgets.QApplication.instance().MainWindow.Tab_1.History 
                                or self == QtWidgets.QApplication.instance().MainWindow.Tab_4.History) and item.data(100).Solution != "Not evaluated yet":
                            QtWidgets.QApplication.clipboard().setText(item.data(100).Equation)
                        else:
                            QtWidgets.QApplication.clipboard().setText(item.text())
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Solution"
                            and item.data(100).Solution != "Not evaluated yet"):
                        QtWidgets.QApplication.clipboard().setText(item.data(100).Solution)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Equation"
                            and item.data(100).Solution != "Not evaluated yet"):
                        QtWidgets.QApplication.clipboard().setText(item.data(100).Equation)
                    elif QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Text":
                        QtWidgets.QApplication.clipboard().setText(item.data(100).Text)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="LaTeX"
                            and item.data(100).LaTeX != r"\text{Not converted yet}"
                            and item.data(100).LaTeX != r"\text{Could not convert}"):
                        QtWidgets.QApplication.clipboard().setText(item.data(100).LaTeX)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="LaTeX Equation"
                            and item.data(100).LaTeX_E != r"\text{Not converted yet}"
                            and item.data(100).LaTeX_E != r"\text{Could not convert}"):
                        QtWidgets.QApplication.clipboard().setText(item.data(100).LaTeX_E)
                    else:
                        NC(4,QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()+" can not be copied. Using normal copy mode",win=self.window().windowTitle(),func=str(self.objectName())+".(HistoryWidget).keyPressEvent",input=item.text())
                        QtWidgets.QApplication.clipboard().setText(item.text())
                    event.accept()
                    return
                elif self == QtWidgets.QApplication.instance().MainWindow.Tab_1.History:
                    string = ""
                    for i in SelectedItems:
                        string += i.data(100).Equation
                        string += "\n"
                    QtWidgets.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(HistoryWidget, self).keyPressEvent(event)
        except common_exceptions:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(HistoryWidget).keyPressEvent",input=str(event))
            super(HistoryWidget, self).keyPressEvent(event)

    def eventFilter(self, source, event):
        #TODO: Add Tooltips for the Actions! These should also specify whether the action will be executed on all selected items or only the right-clicked-one! "Delete" should also mention "Del" as the hotkey!
        #FEATURE: When multiple items are selected the context menu should be different: instead of the usual options there should be options to format the selected items in a specific way and copy the result to the clipboard
        #FEATURE: The comma separation every 3 digits is cool! There should be a way to copy the solution or the equation including this separation
        try:
            if event.type() == 82: # QtCore.QEvent.ContextMenu
            # ---------------------------------- History Context Menu ----------------------------------
                if source.itemAt(event.pos()):
                    menu = QtWidgets.QMenu()
                    if source.itemAt(event.pos()).data(100).Solution != "Not evaluated yet":
                        action = menu.addAction('Copy Solution')
                        action.triggered.connect(lambda: self.action_H_Copy_Solution(source,event))
                        action = menu.addAction('Copy Equation')
                        action.triggered.connect(lambda: self.action_H_Copy_Equation(source,event))
                    action = menu.addAction('Copy Text')
                    action.triggered.connect(lambda: self.action_H_Copy_Text(source,event))
                    action = menu.addAction('Copy LaTeX')
                    action.triggered.connect(lambda: self.action_H_Copy_LaTeX(source,event))
                    if source.itemAt(event.pos()).data(100).LaTeX_E != r"\text{Not converted yet}" and source.itemAt(event.pos()).data(100).LaTeX_E != r"\text{Could not convert}":
                        action = menu.addAction('Copy LaTeX Equation')
                        action.triggered.connect(lambda: self.action_H_Copy_LaTeX_E(source,event))
                    if QtWidgets.QApplication.instance().advanced_mode:
                        action = menu.addAction('+ Copy Input')
                        action.triggered.connect(lambda: self.action_H_Copy_Input(source,event))
                        action = menu.addAction('+ Copy cString')
                        action.triggered.connect(lambda: self.action_H_Copy_cstr(source,event))
                    menu.addSeparator()
                    # MAYBE: Only "Calculate" if the equation has not been evaluated yet or if in Advanced Mode? Maybe? Maybe not?
                    # It currently is handy to have it always because of the EvalF thing...
                    action = menu.addAction('Calculate')
                    action.triggered.connect(lambda: self.action_H_Calculate(source,event))
                    action = menu.addAction('Display LaTeX')
                    action.triggered.connect(lambda: self.action_H_Display_LaTeX(source,event))
                    if source.itemAt(event.pos()).data(100).Solution != "Not evaluated yet":
                        action = menu.addAction('Display LaTeX Equation')
                        action.triggered.connect(lambda: self.action_H_Display_LaTeX_Equation(source,event))
                        action = menu.addAction('Display LaTeX Solution')
                        action.triggered.connect(lambda: self.action_H_Display_LaTeX_Solution(source,event))
                    menu.addSeparator()
                    if source.itemAt(event.pos()).data(100).plot_data_exists :
                        action = menu.addAction('Reload Plot') #TODO: Add tooltip
                        action.triggered.connect(lambda: self.action_H_Load_Plot(source,event))
                    if source.itemAt(event.pos()).data(100).plottable :
                        action = menu.addAction('New Plot') #TODO: Add tooltip
                        action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
                    elif QtWidgets.QApplication.instance().advanced_mode :
                        action = menu.addAction('+ New Plot') #TODO: Add tooltip
                        action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
                    if source.itemAt(event.pos()).data(100).plot_data_exists and QtWidgets.QApplication.instance().advanced_mode:
                        menu.addSeparator()
                        action = menu.addAction('+ Copy x Values')
                        action.triggered.connect(lambda: self.action_H_Copy_x_Values(source,event))
                        action = menu.addAction('+ Copy y Values')
                        action.triggered.connect(lambda: self.action_H_Copy_y_Values(source,event))
                    menu.addSeparator()
                    action = menu.addAction('Delete')
                    action.triggered.connect(lambda: self.action_H_Delete(source,event))
                    menu.setPalette(self.palette())
                    menu.setFont(self.font())
                    menu.exec_(event.globalPos())
                    return True
            elif event.type() == 6: # QtCore.QEvent.KeyPress
                if event.key() == QtCore.Qt.Key_Delete:
                    self.action_H_Delete(source,event)

            return super(HistoryWidget, self).eventFilter(source, event)
        except common_exceptions:
            NC(lvl=1,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(HistoryWidget).eventFilter",input=str(event))
            return super(HistoryWidget, self).eventFilter(source, event)
 # ---------------------------------- History Context Menu Actions/Functions ----------------------------------
  # ----------------
         
    def action_H_Copy_Solution(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).Solution)
         
    def action_H_Copy_Equation(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).Equation)
         
    def action_H_Copy_Text(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).Text)
        
    def action_H_Copy_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).LaTeX)
        
    def action_H_Copy_LaTeX_E(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).LaTeX_E)
        
    def action_H_Copy_Input(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).Input)
        
    def action_H_Copy_cstr(self,source,event):
        item = source.itemAt(event.pos())
        QtWidgets.QApplication.clipboard().setText(item.data(100).cstr)
        
  # ----------------
         
    def action_H_Calculate(self,source,event):
        item = source.itemAt(event.pos())
        self.window().TabWidget.setCurrentIndex(0)
        self.window().Tab_1.calculate(item.data(100))
        
    def action_H_Display_LaTeX(self,source,event): #TODO: Move all selected items to the LaTeX Tab History but only display LaTeX of the right-clicked-one (and update the tooltip for this action)
        item = source.itemAt(event.pos())
        self.window().TabWidget.setCurrentIndex(1)
        self.window().Tab_2.displayLaTeX(item.data(100))

    def action_H_Display_LaTeX_Equation(self,source,event):
        item = source.itemAt(event.pos())
        self.window().TabWidget.setCurrentIndex(1)
        self.window().Tab_2.displayLaTeX(item.data(100),part="Equation")

    def action_H_Display_LaTeX_Solution(self,source,event):
        item = source.itemAt(event.pos())
        self.window().TabWidget.setCurrentIndex(1)
        self.window().Tab_2.displayLaTeX(item.data(100),part="Solution")
         
  # ----------------
         
    def action_H_Load_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.window().Tab_3.Tab_2D.History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.window().TabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.window().Tab_3.Tab_2D.F_RedrawPlot()
            self.window().Tab_3.Tab_2D.F_Plot(item.data(100))
        
    def action_H_New_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.window().Tab_3.Tab_2D.History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.window().TabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.window().Tab_3.Tab_2D.F_RedrawPlot()
            self.window().Tab_3.Tab_2D.F_Plot_init(item.data(100))
         
  # ----------------
        
    def action_H_Copy_x_Values(self,source,event):
        try:
            item = source.itemAt(event.pos())
            Text = "[ "
            for i in item.data(100).plot_x_vals:
                Text += str(i)
                Text += " , "
            Text = Text[:-3]
            Text += " ]"
            QtWidgets.QApplication.clipboard().setText(Text)
        except common_exceptions:
            NC(lvl=2,msg="Could not copy x values",exc=sys.exc_info(),func="HistoryWidget.action_H_Copy_x_Values",win=self.window().windowTitle(),input=item.data(100).Input)
        
    def action_H_Copy_y_Values(self,source,event):
        try:
            item = source.itemAt(event.pos())
            Text = "[ "
            for i in item.data(100).plot_y_vals:
                Text += str(i)
                Text += " , "
            Text = Text[:-3]
            Text += " ]"
            QtWidgets.QApplication.clipboard().setText(Text)
        except common_exceptions:
            NC(lvl=2,msg="Could not copy y values",exc=sys.exc_info(),func="HistoryWidget.action_H_Copy_y_Values",win=self.window().windowTitle(),input=item.data(100).Input)
 
  # ----------------
         
    def action_H_Delete(self,source,event):
        #FEATURE: Paperbin for items: When items are deleted save them temporarily and add an "undo last deletion" context menu action
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            source.takeItem(source.row(item))
            # The cleanup below is apparently unnecessary but it is cleaner to do it anyways...
            if source is self.window().Tab_1.History:
                item.data(100).tab_1_is = False
                item.data(100).tab_1_ref = None
            elif source is self.window().Tab_2.History:
                item.data(100).tab_2_is = False
                item.data(100).tab_2_ref = None
            elif source is self.window().Tab_3.Tab_2D.History:
                item.data(100).Tab_3_1_is = False
                item.data(100).Tab_3_1_ref = None
                if item.data(100).current_ax != None:
                    item.data(100).current_ax.remove()
                    item.data(100).current_ax = None
                    self.window().Tab_3.Tab_2D.F_RedrawPlot()
            elif source is self.window().Tab_4.History:
                if item.data(100) == self.window().Tab_4.Active_Equation:
                    self.window().Tab_4.History.addItem(item)
                else:
                    item.data(100).Tab_4_is = False
                    item.data(100).Tab_4_ref = None


#region 3DPlotWidget ----------------------------------------------------------------------------------------------

class AMaDiA_3DPlotWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AMaDiA_3DPlotWidget, self).__init__(parent)

#endregion 3DPlotWidget -------------------------------------------------------------------------------------------
#region ComplexPlotWidget -----------------------------------------------------------------------------------------

class AMaDiA_ComplexPlotWidget(QtWidgets.QWidget):
    S_Plot = QtCore.pyqtSignal() # The Plot Signal
    def __init__(self, parent=None):
        super(AMaDiA_ComplexPlotWidget, self).__init__(parent)
        
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(3)
        
        self.Display = AGeGW.GWidget_ComplexPlot(self)
        self.layout().addWidget(self.Display,0,0)
        #
        self.SettingsArea = QtWidgets.QWidget(self)
        self.SettingsArea.setLayout(QtWidgets.QHBoxLayout())
        self.SettingsArea.layout().setContentsMargins(0,0,0,0)
        self.SBFromR = QtWidgets.QDoubleSpinBox(self)
        self.SBFromI = QtWidgets.QDoubleSpinBox(self)
        self.SBToR = QtWidgets.QDoubleSpinBox(self)
        self.SBToI = QtWidgets.QDoubleSpinBox(self)
        self.SBFromRLabel = QtWidgets.QLabel("From",self)
        self.SBFromILabel = QtWidgets.QLabel("+ i ·",self)
        self.SBToRLabel = QtWidgets.QLabel("to",self)
        self.SBToILabel = QtWidgets.QLabel("+ i ·",self)
        for i in [self.SBFromR,self.SBFromI,self.SBToR,self.SBToI]:
            i.setRange(-10000,10000)
            i.setStepType(QtWidgets.QDoubleSpinBox.AdaptiveDecimalStepType)
        self.SBFromR.setValue(-5)
        self.SBFromI.setValue(-5)
        self.SBToR.setValue(5)
        self.SBToI.setValue(5)
        for i in [self.SBFromRLabel,self.SBFromR,self.SBFromILabel,self.SBFromI,self.SBToRLabel,self.SBToR,self.SBToILabel,self.SBToI]:
            self.SettingsArea.layout().addWidget(i)
        self.SettingsArea.layout().insertStretch(-1)
        self.layout().addWidget(self.SettingsArea,1,0)
        #
        self.InputField = AMaDiA_LineEdit(self)
        self.InputField.returnPressed.connect(self.S_Plot.emit)
        self.InputField.returnCtrlPressed.connect(self.S_Plot.emit)
        self.layout().addWidget(self.InputField,2,0)

    def plot(self, AMaS_Object:"AC.AMaS"):
        self.lastInput = AMaS_Object
        self.Display.plot(AMaS_Object.plotC_vals, (AMaS_Object.plotC_r_min, AMaS_Object.plotC_r_max, AMaS_Object.plotC_i_min, AMaS_Object.plotC_i_max))

    def applySettings(self, AMaS_Object:"AC.AMaS"):
        AMaS_Object.plotC_r_min = self.SBFromR.value()
        AMaS_Object.plotC_i_min = self.SBFromI.value()
        AMaS_Object.plotC_r_max = self.SBToR.value()
        AMaS_Object.plotC_i_max = self.SBToI.value()
        return AMaS_Object
        ##
        #AMaS_Object.plot_ratio = self.Tab_3.Tab_2D.ConfigWidget.Axis_ratio_Checkbox.isChecked()
        #AMaS_Object.plot_grid = self.Tab_3.Tab_2D.ConfigWidget.DrawGrid_Checkbox.isChecked()
        #AMaS_Object.plot_xmin = self.Tab_3.Tab_2D.ConfigWidget.From_Spinbox.value()
        #AMaS_Object.plot_xmax = self.Tab_3.Tab_2D.ConfigWidget.To_Spinbox.value()
        #AMaS_Object.plot_points = self.Tab_3.Tab_2D.ConfigWidget.Points_Spinbox.value()
        
        #if self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.currentIndex() == 0:
        #    AMaS_Object.plot_per_unit = False
        #elif self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.currentIndex() == 1:
        #    AMaS_Object.plot_per_unit = True
        
        #AMaS_Object.plot_xlim = self.Tab_3.Tab_2D.ConfigWidget.XLim_Check.isChecked()
        #if AMaS_Object.plot_xlim:
        #    xmin , xmax = self.Tab_3.Tab_2D.ConfigWidget.XLim_min.value(), self.Tab_3.Tab_2D.ConfigWidget.XLim_max.value()
        #    if xmax < xmin:
        #        xmax , xmin = xmin , xmax
        #    AMaS_Object.plot_xlim_vals = (xmin , xmax)
        #AMaS_Object.plot_ylim = self.Tab_3.Tab_2D.ConfigWidget.YLim_Check.isChecked()
        #if AMaS_Object.plot_ylim:
        #    ymin , ymax = self.Tab_3.Tab_2D.ConfigWidget.YLim_min.value(), self.Tab_3.Tab_2D.ConfigWidget.YLim_max.value()
        #    if ymax < ymin:
        #        ymax , ymin = ymin , ymax
        #    AMaS_Object.plot_ylim_vals = (ymin , ymax)

        
#endregion ComplexPlotWidget --------------------------------------------------------------------------------------

