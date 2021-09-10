


import sys
sys.path.append('..')
from AGeLib import *

import sympy
import re
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError , sympy.SympifyError , sympy.parsing.sympy_parser.TokenError)
from sympy.parsing.sympy_parser import parse_expr

from External_Libraries.python_control_master import control

from AMaDiA_Files import AMaDiA_Functions as AF
from AMaDiA_Files import AMaDiA_Classes as AC
from AMaDiA_Files import AMaDiA_ReplacementTables as ART
from AMaDiA_Files.AMaDiA_SystemControl_UI import Ui_SystemControlWindow
from AMaDiA_Files.AMaDiA_SystemControl_Widgets import MplCanvas_CONTROL
from AMaDiA_Files.AMaDiA_SystemControl_Widgets import SystemClass


# ---------------------------------- Main Window ----------------------------------
class AMaDiA_Control_Window(AWWF, Ui_SystemControlWindow):
    #FEATURE: Totzeit. Formel ist hier: https://de.wikipedia.org/wiki/Totzeit_(Regelungstechnik)#Ann%C3%A4herung_an_das_Verhalten_eines_Totzeitgliedes_durch_Allpass-Glieder_als_Ersatztotzeit
    #       Simply make 2 fields to input delay (T_t) and steps for the approximation (n). Then multiply Y(s) with (1-T_t/(2*n)*s)^n and X(s) with (1+T_t/(2*n)*s)^n
    #FEATURE: Timedescrete systems. Should be straight foreward. Simply replace the control calls with the time descrete ones. The detection could be based on whether the variable is s or z
    #FEATURE: Allow the user to set plot parameters
    #TODO: Doubleclicking on an item in the history should display it in the LaTeX display
    def __init__(self, parent = None):
        super(AMaDiA_Control_Window, self).__init__(parent, IncludeTopBar=False, initTopBar=False, IncludeStatusBar=True)
        self.setupUi(self)
        self.TopBar = AGeWidgets.TopBar_Widget(self,False)
        self.ControlSystems_tabWidget.setCornerWidget(self.TopBar, QtCore.Qt.TopRightCorner)
        self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
        
        self.StandardSize = (906, 634)
        self.resize(*self.StandardSize)
        
        self.ControlSystems_tabWidget.setCurrentIndex(0)
        self.ControlSystems_1_Output_tabWidget.removeTab(1)
        
        ControlSystems_4_Dirty_Input_Text = "#Example:\n\n"
        ControlSystems_4_Dirty_Input_Text += "K_P = 5\nK_D = 0\nK_i = 0\n\nsys1 = tf([K_D,K_P,K_i],[1,1.33+K_D,1+K_P,K_i])\n\n"
        ControlSystems_4_Dirty_Input_Text += "#Other example:\n#sys1 = tf([1],[1,2,3])\n\n"
        ControlSystems_4_Dirty_Input_Text += "#Other example:\n#sys1 = ss([[2,8],[1,0]],[[1],[-0.5000]],[-1/8,-1],[0])\n\n"
        ControlSystems_4_Dirty_Input_Text += "#Setting Input Function u(s):\nu=\"sin(s)\"\n#u=\"1/(s+1)\""
        
        self.ControlSystems_4_Dirty_Input.setPlaceholderText(ControlSystems_4_Dirty_Input_Text)
        self.ControlSystems_4_Dirty_Input.setText(ControlSystems_4_Dirty_Input_Text)
        
        # EventFilter
        self.installEventFilter(self)
        # Set up context menus for the histories and other list widgets
        for i in self.findChildren(QtWidgets.QListWidget):
            i.installEventFilter(self)
        # Set up text input related Event Handlers
        for i in self.findChildren(QtWidgets.QTextEdit):
            i.installEventFilter(self)
        for i in self.findChildren(QtWidgets.QLineEdit):
            i.installEventFilter(self)
        
        # Run other init methods
        self.ConnectSignals()
        
        # Other things:
        self.ControlSystems_1_System_Set_Order()
        
        for i in self.findChildren(AGeGW.MplWidget):
            i.setColour()
        NC(10,"Welcome to CONTROL (WIP)",win=self.windowTitle(),func="{}.__init__".format(str(self.objectName())))
    
 # ---------------------------------- Init and Maintenance ----------------------------------
    
    def ConnectSignals(self):
        self.ControlSystems_1_SystemOrder_Confrim.clicked.connect(self.ControlSystems_1_System_Set_Order)
        self.ControlSystems_1_SaveButton.clicked.connect(self.ControlSystems_1_System_Save)
        self.ControlSystems_1_SavePlotButton.clicked.connect(self.ControlSystems_1_System_Plot_and_Save)
        
        self.ControlSystems_1_System_4ATF_Ys.returnPressed.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_System_4ATF_Xs))
        self.ControlSystems_1_System_4ATF_Xs.returnPressed.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_NameInput))
        self.ControlSystems_1_System_1TF_tableWidget.S_Focus_Next.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_NameInput))
        self.ControlSystems_1_System_2SS_A_tableWidget.S_Focus_Next.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_System_2SS_B_tableWidget))
        self.ControlSystems_1_System_2SS_B_tableWidget.S_Focus_Next.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_System_2SS_C_tableWidget))
        self.ControlSystems_1_System_2SS_C_tableWidget.S_Focus_Next.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_System_2SS_D_tableWidget))
        self.ControlSystems_1_System_2SS_D_tableWidget.S_Focus_Next.connect(lambda: self.ControlSystems_1_SetFocus_on(self.ControlSystems_1_NameInput))
        self.ControlSystems_1_NameInput.returnPressed.connect(self.ControlSystems_1_System_Plot_and_Save)
        
        
        self.ControlSystems_2_Display.Canvas.mpl_connect('button_press_event', self.ControlSystems_2_Maximize_Axes)
        
        self.ControlSystems_4_Dirty_Input.returnCtrlPressed.connect(self.ControlSystems_4_Dirty_Display)
    
 # ---------------------------------- Event Filter ----------------------------------
    
    def eventFilter(self, source, event):
        #print(event.type())
        #if event.type() == 6: # QtCore.QEvent.KeyPress
        # # ---------------------------------- Full Screen ----------------------------------
        #    if event.key() == QtCore.Qt.Key_F11 and source is self: # F11 to toggle Fullscreen
        #        if not self.isFullScreen():
        #            if self.isMaximized():
        #                self.LastOpenState = self.showMaximized
        #                self.TopBar.MaximizeButton.setText("🗖")
        #            else:
        #                self.LastOpenState = self.showNormal
        #                self.TopBar.MaximizeButton.setText("🗗")
        #            self.showFullScreen()
        #        else:
        #            if self.LastOpenState == self.showMaximized:
        #                self.TopBar.MaximizeButton.setText("🗗")
        #            else:
        #                self.TopBar.MaximizeButton.setText("🗖")
        #            self.LastOpenState()
        if event.type() == 82: # QtCore.QEvent.ContextMenu
         # ---------------------------------- List Context Menu ----------------------------------
            if (source is self.ControlSystems_1_SystemList) and source.itemAt(event.pos()):
                menu = QtWidgets.QMenu()
                action = menu.addAction('Load to Editor')
                action.triggered.connect(lambda: self.action_SystemList_Load_into_Editor(source,event))
                action = menu.addAction('Copy as String')
                action.triggered.connect(lambda: self.action_SystemList_Copy_string(source,event))
                action = menu.addAction('Display')
                action.triggered.connect(lambda: self.action_SystemList_Display(source,event))
                action = menu.addAction('Plot')
                action.triggered.connect(lambda: self.action_SystemList_Plot(source,event))
                action = menu.addAction('Plot Closed-Loop System')
                action.triggered.connect(lambda: self.action_SystemList_Plot_Closed(source,event))
                action = menu.addAction('Delete')
                action.triggered.connect(lambda: self.action_SystemList_Delete(source,event))
                menu.setPalette(self.palette())
                menu.setFont(self.font())
                menu.exec_(event.globalPos())
                return True
        #elif...
        return super(AMaDiA_Control_Window, self).eventFilter(source, event) # let the normal eventFilter handle the event
 # ---------------------------------- List Context Menu Actions/Functions ----------------------------------
    def action_SystemList_Load_into_Editor(self,source,event):
        item = source.itemAt(event.pos())
        system = item.data(100)
        self.ControlSystems_1_System_tabWidget.setCurrentIndex(system.Tab)
        self.ControlSystems_1_SystemOrder_Spinbox.setValue(system.Order)
        self.ControlSystems_1_System_Set_Order(system.Order)
        if system.Tab == 0:
            Ys, Xs = system.systemInput
            self.ControlSystems_1_System_4ATF_Ys.setText(Ys)
            self.ControlSystems_1_System_4ATF_Xs.setText(Xs)
        elif system.Tab == 1:
            Ys, Xs, Order = system.systemInput
            self.ControlSystems_1_System_Set_Order(Order)
            for j in range(self.ControlSystems_1_System_1TF_tableWidget.columnCount()):
                item = QtCore.Qt.QTableWidgetItem()
                t = AF.number_shaver(str(Ys[j])) if AF.number_shaver(str(Ys[j])) != "0" else ""
                item.setText(t)
                self.ControlSystems_1_System_1TF_tableWidget.setItem(0,j,item)
                item = QtCore.Qt.QTableWidgetItem()
                t = AF.number_shaver(str(Xs[j])) if AF.number_shaver(str(Xs[j])) != "0" else ""
                item.setText(t)
                self.ControlSystems_1_System_1TF_tableWidget.setItem(1,j,item)
        elif system.Tab == 2:
            A,B,C,D = system.systemInput
            for i in range(system.Order):
                for j in range(system.Order):
                    item = QtCore.Qt.QTableWidgetItem()
                    item.setText(AF.number_shaver(str(A[i][j])))
                    self.ControlSystems_1_System_2SS_A_tableWidget.setItem(i,j,item)
                item = QtCore.Qt.QTableWidgetItem()
                item.setText(AF.number_shaver(str(B[i][0])))
                self.ControlSystems_1_System_2SS_B_tableWidget.setItem(i,0,item)
                item = QtCore.Qt.QTableWidgetItem()
                item.setText(AF.number_shaver(str(C[i])))
                self.ControlSystems_1_System_2SS_C_tableWidget.setItem(0,i,item)
            item = QtCore.Qt.QTableWidgetItem()
            t = AF.number_shaver(str(D[0][0])) if AF.number_shaver(str(D[0][0])) != "0" else ""
            item.setText(t)
            self.ControlSystems_1_System_2SS_D_tableWidget.setItem(0,0,item)
    
    def action_SystemList_Copy_string(self,source,event):
        item = source.itemAt(event.pos())
        system = item.data(100)
        QtWidgets.QApplication.clipboard().setText(str(system.sys))
    
    def action_SystemList_Display(self,source,event):
        item = source.itemAt(event.pos())
        system = item.data(100)
        self.ControlSystems_1_System_Display_LaTeX(system)
    
    def action_SystemList_Plot(self,source,event):
        item = source.itemAt(event.pos())
        system = item.data(100)
        self.ControlSystems_1_System_Display_LaTeX(system)
        self.ControlSystems_1_System_Plot(system)
    
    def action_SystemList_Plot_Closed(self,source,event):
        open_system = source.itemAt(event.pos()).data(100)
        item = open_system.Close()
        closed_system = item.data(100)
        self.ControlSystems_1_SystemList.addItem(item)
        self.ControlSystems_1_System_Display_LaTeX(closed_system)
        self.ControlSystems_1_System_Plot(closed_system)
    
    def action_SystemList_Delete(self,source,event):
        # FEATURE: Paperbin for Systems: When items are deleted save them temporarily and add an "undo last deletion" context menu action
        listItems=source.selectedItems()
        if not listItems: return        
        for item in listItems:
            source.takeItem(source.row(item))
    
  # ---------------------------------- Control Plot Interaction ---------------------------------- 
    def ControlSystems_2_Maximize_Axes(self,event):
        try:
            if event.button == 1 and event.dblclick and event.inaxes.title.get_text() in MplCanvas_CONTROL.Titles[:9]+["  "]:
                if self.ControlSystems_3_SingleDisplay.Plot(self.ControlSystems_2_Display.Curr_Sys, event.inaxes.title.get_text()):
                    self.ControlSystems_tabWidget.setCurrentIndex(2)
        except common_exceptions as inst:
            if type(inst) != AttributeError:
                NC(exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_2_Maximize_Axes",win=self.windowTitle())
            self.ControlSystems_tabWidget.setCurrentIndex(1)
        self.ControlSystems_tabWidget.setFocus()
    
 # ---------------------------------- ControlSystems_ (Mind-)Control ----------------------------------
    def ControlSystems_1_System_Set_Order(self,Order=None):
        if type(Order) != int:
            Order = self.ControlSystems_1_SystemOrder_Spinbox.value()
        
        # Transfer
        ## Add/Remove Columns
        shift = Order+1-self.ControlSystems_1_System_1TF_tableWidget.columnCount()
        if shift > 0:
            for i in range(abs(shift)):
                self.ControlSystems_1_System_1TF_tableWidget.insertColumn(0)
        elif shift < 0:
            for i in range(abs(shift)):
                self.ControlSystems_1_System_1TF_tableWidget.removeColumn(0)
        
        ## Set Header Labels
        HeaderLabel = []
        i=Order
        while i >= 0:
            s="s{}".format(i)
            HeaderLabel.append(u''.join(dict(zip(u"0123456789", u"⁰¹²³⁴⁵⁶⁷⁸⁹")).get(c, c) for c in s))
            i-=1
        self.ControlSystems_1_System_1TF_tableWidget.setHorizontalHeaderLabels(HeaderLabel)
        
        # State System
        q,p = 1,1 # Future use for multi dimensional input and output (See https://en.wikipedia.org/wiki/State-space_representation)
        self.ControlSystems_1_System_2SS_A_tableWidget.setRowCount(Order)
        self.ControlSystems_1_System_2SS_A_tableWidget.setColumnCount(Order)
        
        self.ControlSystems_1_System_2SS_B_tableWidget.setRowCount(Order)
        self.ControlSystems_1_System_2SS_B_tableWidget.setColumnCount(p)
        
        self.ControlSystems_1_System_2SS_C_tableWidget.setRowCount(q)
        self.ControlSystems_1_System_2SS_C_tableWidget.setColumnCount(Order)
        
        self.ControlSystems_1_System_2SS_D_tableWidget.setRowCount(q)
        self.ControlSystems_1_System_2SS_D_tableWidget.setColumnCount(p)
        
        ## Set Header Labels
        HeaderLabelX = []
        i=1
        while i <= Order:
            s="x{}·".format(i)
            HeaderLabelX.append(u''.join(dict(zip(u"0123456789", u"₀₁₂₃₄₅₆₇₈₉")).get(c, c) for c in s))
            i+=1
        HeaderLabelXDiff = []
        i=1
        while i <= Order:
            s="ẋ{}=".format(i)
            HeaderLabelXDiff.append(u''.join(dict(zip(u"0123456789", u"₀₁₂₃₄₅₆₇₈₉")).get(c, c) for c in s))
            i+=1
        HeaderLabelU = ["u·"]
        HeaderLabelY = ["y="]
        self.ControlSystems_1_System_2SS_A_tableWidget.setHorizontalHeaderLabels(HeaderLabelX)
        self.ControlSystems_1_System_2SS_A_tableWidget.setVerticalHeaderLabels(HeaderLabelXDiff)
        self.ControlSystems_1_System_2SS_B_tableWidget.setHorizontalHeaderLabels(HeaderLabelU)
        self.ControlSystems_1_System_2SS_B_tableWidget.setVerticalHeaderLabels(HeaderLabelXDiff)
        self.ControlSystems_1_System_2SS_C_tableWidget.setHorizontalHeaderLabels(HeaderLabelX)
        self.ControlSystems_1_System_2SS_C_tableWidget.setVerticalHeaderLabels(HeaderLabelY)
        self.ControlSystems_1_System_2SS_D_tableWidget.setHorizontalHeaderLabels(HeaderLabelU)
        self.ControlSystems_1_System_2SS_D_tableWidget.setVerticalHeaderLabels(HeaderLabelY)
    
    def ControlSystems_1_SetFocus_on(self,item):
        if item == self.ControlSystems_1_System_4ATF_Xs:
            self.ControlSystems_1_System_4ATF_Xs.setFocus()
            self.ControlSystems_1_System_4ATF_Xs.selectAll()
        elif item == self.ControlSystems_1_NameInput:
            self.ControlSystems_1_System_2SS_tabWidget.setCurrentIndex(0)
            self.ControlSystems_1_NameInput.setFocus()
            self.ControlSystems_1_NameInput.selectAll()
        elif item == self.ControlSystems_1_System_2SS_B_tableWidget:
            self.ControlSystems_1_System_2SS_tabWidget.setCurrentIndex(1)
            self.ControlSystems_1_System_2SS_B_tableWidget.setFocus()
        elif item == self.ControlSystems_1_System_2SS_C_tableWidget:
            self.ControlSystems_1_System_2SS_tabWidget.setCurrentIndex(2)
            self.ControlSystems_1_System_2SS_C_tableWidget.setFocus()
        elif item == self.ControlSystems_1_System_2SS_D_tableWidget:
            self.ControlSystems_1_System_2SS_tabWidget.setCurrentIndex(3)
            self.ControlSystems_1_System_2SS_D_tableWidget.setFocus()
    
    def ControlSystems_1_System_Save(self):
        Tab = self.ControlSystems_1_System_tabWidget.currentIndex()
        sys1 = None
        try:
            NameInvalid=False
            Name = AF.AstusParse(self.ControlSystems_1_NameInput.text()).strip()
            if Name == "" or " " in Name: #IMPROVE: Better checks for System Name!!!
                NameInvalid=True
            
            if NameInvalid:
                NC(1,"System Name Invalid",func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input=Name)
                return False
            
            
            
            if Tab == 0: #Autoarrange Transfer Function
                # Parse the input and find out the coefficients of the powers of s
                systemInput = (self.ControlSystems_1_System_4ATF_Ys.text(),self.ControlSystems_1_System_4ATF_Xs.text())
                s = sympy.symbols("s")
                # FEATURE: check if s or z is in systemInput and create a time discrete system if it is z and add a field to THIS TAB to set the Abtastzeit
                try:
                    success = False
                    mult = 0
                    Yt = "("+self.ControlSystems_1_System_4ATF_Ys.text()+")"
                    Xt = "("+self.ControlSystems_1_System_4ATF_Xs.text()+")"
                    termsY,termsX = "Fail","Fail"
                    while not success:
                        try:
                            Ys_s = sympy.expand(parse_expr(AF.AstusParse(Yt)).doit().evalf())
                            print(type(Ys_s),Ys_s)
                            if type(Ys_s) == type(parse_expr("1/s")):
                                pass
                            Ys_r = sympy.poly(Ys_s,s)
                            termsY = Ys_r.all_terms()
                            Xs_s = sympy.expand(parse_expr(AF.AstusParse(Xt)).doit().evalf())
                            Xs_r = sympy.poly(Xs_s,s)
                            termsX = Xs_r.all_terms()
                            success = True
                        except:
                            Yt+="*s"
                            Xt+="*s"
                            mult+=1
                            if mult>20:
                                NC(msg="Could not normalize",exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input="Input:{}\nX:{}\nY:{}".format(self.ControlSystems_1_System_4ATF_Ys.text(),str(termsY),str(termsX)))
                                return False
                    temp_list_y = []
                    temp_list_x = []
                    for i in termsY:
                        temp_list_y.append(int(i[0][0]))
                    for i in termsX:
                        temp_list_x.append(int(i[0][0]))
                    while min(temp_list_y)<0 or min(temp_list_x)<0:
                        Yt+="*s"
                        Xt+="*s"
                        Ys_r = sympy.poly(sympy.expand(parse_expr(AF.AstusParse(Yt)).doit().evalf()),s)
                        termsY = Ys_r.all_terms()
                        Xs_r = sympy.poly(sympy.expand(parse_expr(AF.AstusParse(Xt)).doit().evalf()),s)
                        termsX = Xs_r.all_terms()
                        temp_list_y = []
                        temp_list_x = []
                        for i in termsY:
                            temp_list_y.append(int(i[0][0]))
                        for i in termsX:
                            temp_list_x.append(int(i[0][0]))
                        mult+=1
                        if mult>20:
                            raise Exception("Could not normalize\nX:{}\nY:{}".format(str(termsY),str(termsX)))
                    Ys = []
                    for i in termsY:
                        Ys.append(float(i[1]))
                    print(Ys)
                except common_exceptions:
                    NC(msg="Error in Y(s)",exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input=self.ControlSystems_1_System_4ATF_Ys.text())
                    return False
                try:
                    Xs = []
                    for i in termsX:
                        Xs.append(float(i[1]))
                    print(Xs)
                except common_exceptions:
                    NC(msg="Error in X(s)",exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input=self.ControlSystems_1_System_4ATF_Xs.text())
                    return False
                sys1 = control.tf(Ys,Xs)
            elif Tab == 1: #Transfer
                Ys,YsI = [],[]
                Xs,XsI = [],[]
                MError = ""
                for j in range(self.ControlSystems_1_System_1TF_tableWidget.columnCount()):
                    try:
                        if self.ControlSystems_1_System_1TF_tableWidget.item(0,j) != None and self.ControlSystems_1_System_1TF_tableWidget.item(0,j).text().strip() != "":
                            Ys.append(float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_1TF_tableWidget.item(0,j).text(),True)).doit().evalf()))
                        else:
                            Ys.append(0)
                    except common_exceptions:
                        MError += "Could not add item to System at ({},{}). Inserting a Zero instead. ".format(1,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Ys.append(0)
                    try:
                        if self.ControlSystems_1_System_1TF_tableWidget.item(1,j) != None and self.ControlSystems_1_System_1TF_tableWidget.item(1,j).text().strip() != "":
                            Xs.append(float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_1TF_tableWidget.item(1,j).text(),True)).doit().evalf()))
                        else:
                            Xs.append(0)
                    except common_exceptions:
                        MError += "Could not add item to System at ({},{}). Inserting a Zero instead. ".format(2,j+1)
                        #MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        Xs.append(0)
                    YsI.append(Ys[j])
                    XsI.append(Xs[j])
                systemInput = (YsI,XsI,self.ControlSystems_1_System_1TF_tableWidget.columnCount()-1)
                if MError != "":
                    NC(2,MError,func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input="X(s) = {}\nY(s) = {}".format(str(Xs),str(Ys)))
                # Remove empty leading entries
                while Ys[0]==0:
                    Ys.pop(0)
                while Xs[0]==0:
                    Xs.pop(0)
                #print(Ys,r"/",Xs)
                sys1 = control.tf(Ys,Xs)
            elif Tab == 2: #State System
                A,B,C,D = [],[],[],[]
                # Loading A
                MError = ""
                for i in range(self.ControlSystems_1_System_2SS_A_tableWidget.rowCount()):
                    A.append([])
                    for j in range(self.ControlSystems_1_System_2SS_A_tableWidget.columnCount()):
                        try:
                            if self.ControlSystems_1_System_2SS_A_tableWidget.item(i,j) != None and self.ControlSystems_1_System_2SS_A_tableWidget.item(i,j).text().strip() != "":
                                A[i].append(float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_2SS_A_tableWidget.item(i,j).text(),False)).doit().evalf()))
                            else:
                                A[i].append(0)
                        except common_exceptions:
                            MError += "Could not add item to A at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                            MError += ExceptionOutput(sys.exc_info())
                            MError += "\n"
                            A[i].append(0)
                # Loading B
                for j in range(self.ControlSystems_1_System_2SS_B_tableWidget.rowCount()):
                    try:
                        if self.ControlSystems_1_System_2SS_B_tableWidget.item(j,0) != None and self.ControlSystems_1_System_2SS_B_tableWidget.item(j,0).text().strip() != "":
                            B.append([float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_2SS_B_tableWidget.item(j,0).text(),False)).doit().evalf())])
                        else:
                            B.append([0])
                    except common_exceptions:
                        MError += "Could not add item to B at ({},{}). Inserting a Zero instead. ".format(j+1,1)
                        MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        B.append([0])
                # Loading C
                for j in range(self.ControlSystems_1_System_2SS_C_tableWidget.columnCount()):
                    try:
                        if self.ControlSystems_1_System_2SS_C_tableWidget.item(0,j) != None and self.ControlSystems_1_System_2SS_C_tableWidget.item(0,j).text().strip() != "":
                            C.append(float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_2SS_C_tableWidget.item(0,j).text(),False)).doit().evalf()))
                        else:
                            C.append(0)
                    except common_exceptions:
                        MError += "Could not add item to C at ({},{}). Inserting a Zero instead. ".format(1,j+1)
                        MError += ExceptionOutput(sys.exc_info())
                        MError += "\n"
                        C.append(0)
                # Loading D
                for i in range(self.ControlSystems_1_System_2SS_D_tableWidget.rowCount()):
                    D.append([])
                    for j in range(self.ControlSystems_1_System_2SS_D_tableWidget.columnCount()):
                        try:
                            if self.ControlSystems_1_System_2SS_D_tableWidget.item(i,j) != None and self.ControlSystems_1_System_2SS_D_tableWidget.item(i,j).text().strip() != "":
                                D[i].append(float(parse_expr(AF.AstusParse(self.ControlSystems_1_System_2SS_D_tableWidget.item(i,j).text(),False)).doit().evalf()))
                            else:
                                D[i].append(0)
                        except common_exceptions:
                            MError += "Could not add item to D at ({},{}). Inserting a Zero instead. ".format(i+1,j+1)
                            MError += ExceptionOutput(sys.exc_info())
                            MError += "\n"
                            D[i].append(0)
                # Send Errors
                if MError != "":
                    NC(2,MError,func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input="A:\n{}\n\nB:\n{}\n\nC:\n{}\n\nD:\n{}".format(str(A),str(B),str(C),str(D)))
                # Creating System
                systemInput = (A,B,C,D)
                sys1 = control.ss(A,B,C,D)
            elif Tab == 3: #ODE
                raise Exception("ODE Input is not implemented yet")
            else: # Can not occur...
                raise Exception("Tab {} in Control->Input Tab is unknown".format(str(Tab)))
            
            sysObject = SystemClass(sys1,Name,Tab,systemInput)
            self.ControlSystems_1_System_Display_LaTeX(sysObject)
            self.ControlSystems_1_SystemList.addItem(sysObject.Item())
            # TODO: Deal with duplicated names
            # REMINDER: Save duplicate in other list item to prevent accidental overwrites
            # REMINDER: Save deleted items in other list item to prevent accidental deletions
            
            print(sys1)
            return sysObject
        except common_exceptions:
            NC(exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Save",win=self.windowTitle(),input="Control->Input Tab Number = {}\nSystem: {}".format(str(Tab),str(sys1)))
            return False
    
    def ControlSystems_1_System_Plot_and_Save(self):
        sysObject = self.ControlSystems_1_System_Save()
        if sysObject == False:
            pass
        else:
            self.ControlSystems_1_System_Plot(sysObject)
    
    def ControlSystems_1_System_Plot(self,sysObject):
        try:
            self.ControlSystems_2_Display.display(sysObject.sys, Ufunc=self.ControlSystems_1_Input_InputFunction.text())
            self.ControlSystems_tabWidget.setFocus()
            self.ControlSystems_3_SingleDisplay.clear()
            self.ControlSystems_tabWidget.setCurrentIndex(1)
        except common_exceptions:
            NC(exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Plot",win=self.windowTitle(),input=str(sysObject.sys))
    
    def ControlSystems_1_System_Display_LaTeX(self,sysObject):
        try:
            self.ControlSystems_1_Output_2L_LaTeXDisplay.displayRaw(sysObject.Sys_LaTeX_L,sysObject.Sys_LaTeX_N
                                            ,self.TopBar.Font_Size_spinBox.value()
                                            ,QtWidgets.QApplication.instance().MainWindow.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                            )
        except common_exceptions:
            NC(exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_1_System_Display_LaTeX",win=self.windowTitle(),input=str(sysObject.sys))
    
    def ControlSystems_4_Dirty_Display(self):
        if not QtWidgets.QApplication.instance().advanced_mode:
            NC(3,"This is the \"danger zone\"!\nPlease activate Advanced Mode to confirm that you know what you are doing!",func="AMaDiA_Control_Window.ControlSystems_4_Dirty_Display",win=str(self.windowTitle()),input="Advanced Mode: {}".format(str(QtWidgets.QApplication.instance().advanced_mode)))
        else:
            self.ControlSystems_tabWidget.setCurrentIndex(1)
            input_text = "from External_Libraries.python_control_master.control import * \nglobal sys1\nglobal u\nu=\"\"\n" + self.ControlSystems_4_Dirty_Input.toPlainText()
            #K_D,K_P,K_i = 0,1,0
            try:
                g,l = dict(),dict()
                exec(input_text,g,l)
                print(g["sys1"])
                self.ControlSystems_2_Display.display(g["sys1"],Ufunc=g["u"])
                self.ControlSystems_tabWidget.setFocus()
                self.ControlSystems_3_SingleDisplay.clear()
                # Generate LaTeX of tf:
                sys1 = g["sys1"]
                Ys,Xs = control.tfdata(sys1)
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
                Sys_Gs_LaTeX_L = r"$\displaystyle "
                Sys_Gs_LaTeX_N = "$"
                Sys_Gs_LaTeX_L += Sys_Gs_LaTeX
                Sys_Gs_LaTeX_N += Sys_Gs_LaTeX
                Sys_Gs_LaTeX_L += "$"
                Sys_Gs_LaTeX_N += "$"
                
                # Generate LaTeX of ss:
                A,B,C,D = control.ssdata(sys1)
                Order = A.shape[0]
                x_vec = []
                x_vec_diff = []
                i=1
                while i <= Order:
                    x_vec.append("x_{}(t)".format(i))
                    x_vec_diff.append("diff(x_{}(t),t)".format(i))
                    i+=1
                x_vec = str(sympy.Matrix(x_vec))
                x_vec_diff = str(sympy.Matrix(x_vec_diff))
                A,B = AF.number_shaver(str(sympy.Matrix(A))) , AF.number_shaver(str(sympy.Matrix(B)))
                C,D = AF.number_shaver(str(sympy.Matrix(C))) , AF.number_shaver(str(sympy.Matrix(D)))
                SSx_LaTeX = AF.LaTeX("Eq("+x_vec_diff+","+A+"*"+x_vec+"+"+B+"*u(t))")
                SSy_LaTeX = AF.LaTeX("Eq(y(t),"+C+"*"+x_vec+"+"+D+"*u(t))")
                Sys_SS_LaTeX_L = r"$\displaystyle " + SSx_LaTeX + "$\n" + r"$\displaystyle " + SSy_LaTeX + "$"
                Sys_SS_LaTeX_N = "$" + SSx_LaTeX + "$\n$" + SSy_LaTeX + "$"
                
                
                # Display LaTeX:
                Sys_LaTeX_L = "From Code Input:\nTransfer Function:\n" + Sys_Gs_LaTeX_L + "\nState Space:\n" + Sys_SS_LaTeX_L
                Sys_LaTeX_N = "From Code Input:\nTransfer Function:\n" + Sys_Gs_LaTeX_N + "\nState Space:\n" + Sys_SS_LaTeX_N
                self.ControlSystems_1_Output_2L_LaTeXDisplay.displayRaw(Sys_LaTeX_L,Sys_LaTeX_N
                                                ,self.TopBar.Font_Size_spinBox.value()
                                                ,QtWidgets.QApplication.instance().MainWindow.Menu_Options_action_Use_Pretty_LaTeX_Display.isChecked()
                                                )
            except common_exceptions:
                NC(1,"Could not execute code to generate the system",exc=sys.exc_info(),func="AMaDiA_Control_Window.ControlSystems_4_Dirty_Display",win=self.windowTitle(),input=input_text)
                self.ControlSystems_tabWidget.setCurrentIndex(3)
