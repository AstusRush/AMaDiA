# This Python file uses the following encoding: utf-8

# if__name__ == "__main__":
#     pass

from AGeLib.AGeMain import common_exceptions, ExceptionOutput, NC, MplWidget, ListWidget
from AGeLib import AGeMain

import sys
sys.path.append('..')
from PyQt5 import QtWidgets,QtCore,QtGui,Qt#,QtQuick
#QtQuick.
#from PyQt5.QtQuick import Controls as QtControls
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
from sympy.parsing.sympy_parser import parse_expr
import re
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


class AMaDiA_TextEdit(AGeMain.TextEdit):
    def __init__(self, parent=None):
        super(AMaDiA_TextEdit, self).__init__(parent)
        self.Highlighter = LineEditHighlighter(self.document(), self)
        self.cursorPositionChanged.connect(self.CursorPositionChanged)

    def CursorPositionChanged(self):
        cursor = self.textCursor()
        curPos = cursor.position()
        self.document().contentsChange.emit(curPos,0,0)
        #theformat = QtGui.QTextBlockFormat()
        #theformat.setForeground(QtGui.QColor('green'))
        #for i in range(0,self.document().blockCount()):
        #    cursor2 = QtGui.QTextCursor(self.document().findBlockByNumber(i))
        #    cursor2.setBlockFormat(theformat)
        #self.document().contentsChange.emit(curPos,0,0)


class AMaDiA_LineEdit(AGeMain.LineEdit):
    def __init__(self, parent=None):
        super(AMaDiA_LineEdit, self).__init__(parent)
        self.Highlighter = LineEditHighlighter(self.document(), self)
        self.cursorPositionChanged.connect(self.CursorPositionChanged)

    def CursorPositionChanged(self):
        cursor = self.textCursor()
        curPos = cursor.position()
        self.document().contentsChange.emit(curPos,0,0)
        #theformat = QtGui.QTextBlockFormat()
        #theformat.setForeground(QtGui.QColor('green'))
        #for i in range(0,self.document().blockCount()):
        #    cursor2 = QtGui.QTextCursor(self.document().findBlockByNumber(i))
        #    cursor2.setBlockFormat(theformat)
        #self.document().contentsChange.emit(curPos,0,0)



class LineEditHighlighter(QtGui.QSyntaxHighlighter): # TODO: Unhighlight, performance, Fix FindPair
    def __init__(self, document, Widget):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        self.Widget = Widget
        self.init_Styles()
        try:
            self.enabled = QtWidgets.QApplication.instance().optionWindow.cb_O_PairHighlighter.isChecked()
        except common_exceptions:
            self.enabled = True
        QtWidgets.QApplication.instance().S_Highlighter.connect(self.ToggleActive)

        # init the rules # Currently Unused...
        rules = [(r'%s' % b, 0, self.STYLES['brace']) for b in self.braces]
        self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def ToggleActive(self,Active):
        self.enabled = Active

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
        # TODO: Unhighlight all other blocks
        if not self.enabled:
            self.setCurrentBlockState(0)
            return
        cursor = self.Widget.textCursor()
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

class AMaDiA_TableWidget(AGeMain.TableWidget):
    def __init__(self, parent=None):
        super(AMaDiA_TableWidget, self).__init__(parent)
        self.TheDelegate = AMaDiA_TableWidget_Delegate(self)
        self.setItemDelegate(self.TheDelegate)

class AMaDiA_TableWidget_Delegate(AGeMain.TableWidget_Delegate):
    def __init__(self, parent=None):
        super(AMaDiA_TableWidget_Delegate, self).__init__(parent)

    def createEditor(self, parent, options, index):
        return AMaDiA_LineEdit(parent)


# -----------------------------------------------------------------------------------------------------------------

class HistoryWidget(ListWidget):
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
                        if (self == QtWidgets.QApplication.instance().MainWindow.Tab_1_History 
                                or self == QtWidgets.QApplication.instance().MainWindow.Tab_4_History) and item.data(100).Solution != "Not evaluated yet":
                            Qt.QApplication.clipboard().setText(item.data(100).Equation)
                        else:
                            Qt.QApplication.clipboard().setText(item.text())
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Solution"
                            and item.data(100).Solution != "Not evaluated yet"):
                        Qt.QApplication.clipboard().setText(item.data(100).Solution)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Equation"
                            and item.data(100).Solution != "Not evaluated yet"):
                        Qt.QApplication.clipboard().setText(item.data(100).Equation)
                    elif QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="Text":
                        Qt.QApplication.clipboard().setText(item.data(100).Text)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="LaTeX"
                            and item.data(100).LaTeX != "Not converted yet"
                            and item.data(100).LaTeX != "Could not convert"):
                        Qt.QApplication.clipboard().setText(item.data(100).LaTeX)
                    elif (QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()=="LaTeX Equation"
                            and item.data(100).LaTeX_E != "Not converted yet"
                            and item.data(100).LaTeX_E != "Could not convert"):
                        Qt.QApplication.clipboard().setText(item.data(100).LaTeX_E)
                    else:
                        NC(4,QtWidgets.QApplication.instance().optionWindow.comb_O_HCopyStandard.currentText()+" can not be copied. Using normal copy mode",win=self.window().windowTitle(),func=str(self.objectName())+".(HistoryWidget).keyPressEvent",input=item.text()).send()
                        Qt.QApplication.clipboard().setText(item.text())
                    event.accept()
                    return
                elif self == QtWidgets.QApplication.instance().MainWindow.Tab_1_History:
                    string = ""
                    for i in SelectedItems:
                        string += i.data(100).Equation
                        string += "\n"
                    Qt.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(HistoryWidget, self).keyPressEvent(event)
        except common_exceptions:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(HistoryWidget).keyPressEvent",input=str(event)).send()
            super(HistoryWidget, self).keyPressEvent(event)

    def eventFilter(self, source, event):
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
                if source.itemAt(event.pos()).data(100).LaTeX_E != "Not converted yet" and source.itemAt(event.pos()).data(100).LaTeX_E != "Could not convert":
                    action = menu.addAction('Copy LaTeX Equation')
                    action.triggered.connect(lambda: self.action_H_Copy_LaTeX_E(source,event))
                if QtWidgets.QApplication.instance().optionWindow.cb_O_AdvancedMode.isChecked():
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
                    action = menu.addAction('Load Plot')
                    action.triggered.connect(lambda: self.action_H_Load_Plot(source,event))
                if source.itemAt(event.pos()).data(100).plottable :
                    action = menu.addAction('New Plot')
                    action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
                elif QtWidgets.QApplication.instance().optionWindow.cb_O_AdvancedMode.isChecked() :
                    action = menu.addAction('+ New Plot')
                    action.triggered.connect(lambda: self.action_H_New_Plot(source,event))
                if source.itemAt(event.pos()).data(100).plot_data_exists and QtWidgets.QApplication.instance().optionWindow.cb_O_AdvancedMode.isChecked():
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

        return super(HistoryWidget, self).eventFilter(source, event)
 # ---------------------------------- History Context Menu Actions/Functions ----------------------------------
  # ----------------
         
    def action_H_Copy_Solution(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).Solution)
         
    def action_H_Copy_Equation(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).Equation)
         
    def action_H_Copy_Text(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).Text)
        
    def action_H_Copy_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).LaTeX)
        
    def action_H_Copy_LaTeX_E(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).LaTeX_E)
        
    def action_H_Copy_Input(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).Input)
        
    def action_H_Copy_cstr(self,source,event):
        item = source.itemAt(event.pos())
        Qt.QApplication.clipboard().setText(item.data(100).cstr)
        
  # ----------------
         
    def action_H_Calculate(self,source,event):
        item = source.itemAt(event.pos())
        self.window().tabWidget.setCurrentIndex(0)
        self.window().Tab_1_F_Calculate(item.data(100))
        
    def action_H_Display_LaTeX(self,source,event):
        item = source.itemAt(event.pos())
        self.window().tabWidget.setCurrentIndex(1)
        self.window().Tab_2_F_Display(item.data(100))

    def action_H_Display_LaTeX_Equation(self,source,event):
        item = source.itemAt(event.pos())
        self.window().tabWidget.setCurrentIndex(1)
        self.window().Tab_2_F_Display(item.data(100),part="Equation")

    def action_H_Display_LaTeX_Solution(self,source,event):
        item = source.itemAt(event.pos())
        self.window().tabWidget.setCurrentIndex(1)
        self.window().Tab_2_F_Display(item.data(100),part="Solution")
         
  # ----------------
         
    def action_H_Load_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.window().Tab_3_1_History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.window().tabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.window().Tab_3_1_F_RedrawPlot()
            self.window().Tab_3_1_F_Plot(item.data(100))
        
    def action_H_New_Plot(self,source,event):
        TheItem = source.itemAt(event.pos())
        if source is self.window().Tab_3_1_History:
            listItems=source.selectedItems()
            if not listItems: return
        else:
            listItems = [TheItem]
        for item in listItems:
            self.window().tabWidget.setCurrentIndex(2)
            if not item.data(100).Plot_is_initialized:
                item.data(100).init_2D_plot()
            if item.data(100).current_ax != None:
                item.data(100).current_ax.remove()
                item.data(100).current_ax = None
                self.window().Tab_3_1_F_RedrawPlot()
            self.window().Tab_3_1_F_Plot_init(item.data(100))
         
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
            Qt.QApplication.clipboard().setText(Text)
        except common_exceptions:
            NC(lvl=2,msg="Could not copy x values",exc=sys.exc_info(),func="HistoryWidget.action_H_Copy_x_Values",win=self.window().windowTitle(),input=item.data(100).Input).send()
        
    def action_H_Copy_y_Values(self,source,event):
        try:
            item = source.itemAt(event.pos())
            Text = "[ "
            for i in item.data(100).plot_y_vals:
                Text += str(i)
                Text += " , "
            Text = Text[:-3]
            Text += " ]"
            Qt.QApplication.clipboard().setText(Text)
        except common_exceptions:
            NC(lvl=2,msg="Could not copy y values",exc=sys.exc_info(),func="HistoryWidget.action_H_Copy_y_Values",win=self.window().windowTitle(),input=item.data(100).Input).send()
 
  # ----------------
         
    def action_H_Delete(self,source,event):
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            source.takeItem(source.row(item))
            # The cleanup below is apparently unnecessary but it is cleaner to do it anyways...
            if source is self.window().Tab_1_History:
                item.data(100).tab_1_is = False
                item.data(100).tab_1_ref = None
            elif source is self.window().Tab_2_History:
                item.data(100).tab_2_is = False
                item.data(100).tab_2_ref = None
            elif source is self.window().Tab_3_1_History:
                item.data(100).Tab_3_1_is = False
                item.data(100).Tab_3_1_ref = None
                if item.data(100).current_ax != None:
                    item.data(100).current_ax.remove()
                    item.data(100).current_ax = None
                    self.window().Tab_3_1_F_RedrawPlot()
            elif source is self.window().Tab_4_History:
                if item.data(100) == self.window().Tab_4_Active_Equation:
                    self.window().Tab_4_History.addItem(item)
                else:
                    item.data(100).Tab_4_is = False
                    item.data(100).Tab_4_ref = None
