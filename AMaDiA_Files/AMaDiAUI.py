# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AMaDiAUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from AGeLib import QtCore, QtGui, QtWidgets


class Ui_AMaDiA_Main_Window(object):
    def setupUi(self, AMaDiA_Main_Window):
        self.retranslateUi(AMaDiA_Main_Window)
        self.TabWidget.setCurrentIndex(0)
        self.Tab_3.TabWidget.setCurrentIndex(0)
        self.Tab_3.Tab_2D.TabWidget.setCurrentIndex(0)
        self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.setCurrentIndex(0)
        self.Tab_4.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AMaDiA_Main_Window)
        AMaDiA_Main_Window.setTabOrder(self.TabWidget, self.Tab_1.History)
        AMaDiA_Main_Window.setTabOrder(self.Tab_1.History, self.Tab_1.InputField)
        AMaDiA_Main_Window.setTabOrder(self.Tab_1.InputField, self.Tab_2.InputField)
        AMaDiA_Main_Window.setTabOrder(self.Tab_2.InputField, self.Tab_2.ConvertButton)
        AMaDiA_Main_Window.setTabOrder(self.Tab_2.ConvertButton, self.Tab_2.LaTeXOutput)
        AMaDiA_Main_Window.setTabOrder(self.Tab_2.LaTeXOutput, self.Tab_2.History)
        AMaDiA_Main_Window.setTabOrder(self.Tab_2.History, self.Tab_3.Tab_2D.scrollArea)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.scrollArea, self.Tab_3.Tab_2D.TabWidget)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.TabWidget, self.Tab_3.Tab_2D.History)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.History, self.Tab_3.Tab_2D.ConfigWidget)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget, self.Tab_3.Tab_2D.ConfigWidget.From_Spinbox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.From_Spinbox, self.Tab_3.Tab_2D.ConfigWidget.To_Spinbox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.To_Spinbox, self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox, self.Tab_3.Tab_2D.ConfigWidget.Points_Spinbox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.Points_Spinbox, self.Tab_3.Tab_2D.ConfigWidget.DrawGrid_Checkbox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.DrawGrid_Checkbox, self.Tab_3.Tab_2D.ConfigWidget.Axis_ratio_Checkbox)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.Axis_ratio_Checkbox, self.Tab_3.Tab_2D.ConfigWidget.XLim_Check)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.XLim_Check, self.Tab_3.Tab_2D.ConfigWidget.XLim_min)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.XLim_min, self.Tab_3.Tab_2D.ConfigWidget.XLim_max)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.XLim_max, self.Tab_3.Tab_2D.ConfigWidget.YLim_Check)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.YLim_Check, self.Tab_3.Tab_2D.ConfigWidget.YLim_min)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.YLim_min, self.Tab_3.Tab_2D.ConfigWidget.YLim_max)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.YLim_max, self.Tab_3.Tab_2D.ConfigWidget.RedrawPlot_Button)
        AMaDiA_Main_Window.setTabOrder(self.Tab_3.Tab_2D.ConfigWidget.RedrawPlot_Button, self.Tab_3.Tab_2D.ConfigWidget.Button_Plot_SymPy)

    def retranslateUi(self, AMaDiA_Main_Window):
        _translate = QtCore.QCoreApplication.translate
        AMaDiA_Main_Window.setWindowTitle(_translate("AMaDiA_Main_Window", "AMaDiA"))
        self.Tab_1.InputField.setPlaceholderText(_translate("AMaDiA_Main_Window", "Enter something and hit return to calculate. Use ctrl+return to not solve divisions, roots, etc."))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Tab_1), _translate("AMaDiA_Main_Window", "Calculator"))
        self.Tab_2.LaTeXOutput.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>This is only a preview! All linebreaks are removed!</p><p>Rightklick on the <span style=\" text-decoration: underline;\">formula</span> in the display above or cklick the button to the right to copy the LaTeX!</p></body></html>"))
        self.Tab_2.LaTeXCopyButton.setText(_translate("AMaDiA_Main_Window", "Copy LaTeX"))
        self.Tab_2.InputField.setPlaceholderText(_translate("AMaDiA_Main_Window", "Add Mathematical Expression to be Converted to LaTeX. Use ctrl+return or the Convert button to display. Please give Feedback if return should convert and shift+return adds a new line instead!"))
        self.Tab_2.ConvertButton.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>Shortcut: ctrl+return while having the Input field selected</p></body></html>"))
        self.Tab_2.ConvertButton.setText(_translate("AMaDiA_Main_Window", "Convert"))
        self.Tab_2.Eval_checkBox.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>Evaluate Function:<br/>Controls if functions in the input should be evaluated.<br/>If unchecked some things (like Derivatives) might look weird.<br/>If half-checked only basic functions will be evaluated and only if they return integers<br/>If checked most things will be evaluated</p><p>Example:<br/>Input: sin(pi)<br/>Output if half-checked: 0<br/>Output if unchecked: sin(pi)</p><p>Input: exp(ln(x))<br/>Output if half-checked: x<br/>Output if unchecked: exp(ln(x))</p></body></html>"))
        self.Tab_2.Eval_checkBox.setText(_translate("AMaDiA_Main_Window", "Eval"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Tab_2), _translate("AMaDiA_Main_Window", "LaTeX"))
        self.Tab_3.Tab_2D.ButtonClear.setText(_translate("AMaDiA_Main_Window", "Clear"))
        self.Tab_3.Tab_2D.Formula_Field.setPlaceholderText(_translate("AMaDiA_Main_Window", "Enter a function f(x) (eg. \"x^2\") or a constant (eg. \"23+4\" for a horizontal line or \"x=23+4\" for a vertical line at 27) and hit return."))
        self.Tab_3.Tab_2D.Button_Plot.setText(_translate("AMaDiA_Main_Window", "Plot"))
        self.Tab_3.Tab_2D.TabWidget.setTabText(self.Tab_3.Tab_2D.TabWidget.indexOf(self.Tab_3.Tab_2D.Tab_1_History), _translate("AMaDiA_Main_Window", "History"))
        self.Tab_3.Tab_2D.ConfigWidget.YLim_Check.setToolTip(_translate("AMaDiA_Main_Window", "Limit the part of the y axis that is shown"))
        self.Tab_3.Tab_2D.ConfigWidget.YLim_Check.setText(_translate("AMaDiA_Main_Window", "Limit Y"))
        self.Tab_3.Tab_2D.ConfigWidget.Axis_ratio_Checkbox.setText(_translate("AMaDiA_Main_Window", "1:1 axis ratio"))
        self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.setCurrentText(_translate("AMaDiA_Main_Window", "Points total"))
        self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.setItemText(0, _translate("AMaDiA_Main_Window", "Points total"))
        self.Tab_3.Tab_2D.ConfigWidget.Points_comboBox.setItemText(1, _translate("AMaDiA_Main_Window", "Points per Unit"))
        self.Tab_3.Tab_2D.ConfigWidget.Label_from.setText(_translate("AMaDiA_Main_Window", "From"))
        self.Tab_3.Tab_2D.ConfigWidget.XLim_Check.setToolTip(_translate("AMaDiA_Main_Window", "Limit the part of the x axis that is shown"))
        self.Tab_3.Tab_2D.ConfigWidget.XLim_Check.setText(_translate("AMaDiA_Main_Window", "Limit X"))
        self.Tab_3.Tab_2D.ConfigWidget.DrawGrid_Checkbox.setText(_translate("AMaDiA_Main_Window", "Draw Grid"))
        self.Tab_3.Tab_2D.ConfigWidget.Label_to.setText(_translate("AMaDiA_Main_Window", "To"))
        self.Tab_3.Tab_2D.ConfigWidget.Button_Plot_SymPy.setToolTip(_translate("AMaDiA_Main_Window", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">It is advised to use the normal Plot.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Note:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- Control the Plotted area with Limit X and Limit Y</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">    (Don\'t forget to enable these with the checkboxes)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- Opens new window</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Advantages of SymPy Plotting:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- Easier zomming</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- More options when saving the Plot</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Disadvantages:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- Plots are not saved in the History</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- (Currently) Only one graph per plot</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- (Currently) Limited configuration via the main window</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">- Can not plot as many functions as the main plotter</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">  (The main plotter has several methods of plotting which are used</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">   if the normal method fails while the SymPy plotter only has the normal method)</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p></body></html>"))
        self.Tab_3.Tab_2D.ConfigWidget.Button_Plot_SymPy.setText(_translate("AMaDiA_Main_Window", "Plot with SymPy"))
        self.Tab_3.Tab_2D.ConfigWidget.RedrawPlot_Button.setToolTip(_translate("AMaDiA_Main_Window", "Apply settings"))
        self.Tab_3.Tab_2D.ConfigWidget.RedrawPlot_Button.setText(_translate("AMaDiA_Main_Window", "Redraw Plot"))
        self.Tab_3.Tab_2D.ConfigWidget.Button_SavePlot.setToolTip(_translate("AMaDiA_Main_Window", "<html><head/><body><p>Save the current Plot (exactly as displayed including size and resoltuion)</p><p>as a .png in the Plots folder where the AMaDiA.py is located.</p><p>Tip: This option is also accessible in the right klick menu of the Plot.</p></body></html>"))
        self.Tab_3.Tab_2D.ConfigWidget.Button_SavePlot.setText(_translate("AMaDiA_Main_Window", "Save Plot"))
        self.Tab_3.Tab_2D.TabWidget.setTabText(self.Tab_3.Tab_2D.TabWidget.indexOf(self.Tab_3.Tab_2D.ConfigWidget), _translate("AMaDiA_Main_Window", "Config"))
        self.Tab_3.TabWidget.setTabText(self.Tab_3.TabWidget.indexOf(self.Tab_3.Tab_2D), _translate("AMaDiA_Main_Window", "2D"))
        self.Tab_3.TabWidget.setTabText(self.Tab_3.TabWidget.indexOf(self.Tab_3.Tab_3D), _translate("AMaDiA_Main_Window", "3D"))
        self.Tab_3.TabWidget.setTabText(self.Tab_3.TabWidget.indexOf(self.Tab_3.Tab_Complex), _translate("AMaDiA_Main_Window", "Complex"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Tab_3), _translate("AMaDiA_Main_Window", "Plotter"))
        self.Tab_4.InputTab_Dimension_Input.setInputMask(_translate("AMaDiA_Main_Window", "00\\xD0"))
        self.Tab_4.InputTab_Dimension_Input.setText(_translate("AMaDiA_Main_Window", "3x3"))
        self.Tab_4.InputTab_Save_Matrix_Button.setText(_translate("AMaDiA_Main_Window", "Save"))
        self.Tab_4.InputTab_Configure_Button.setText(_translate("AMaDiA_Main_Window", "Configure"))
        self.Tab_4.InputTab_Name_Input.setPlaceholderText(_translate("AMaDiA_Main_Window", "Name"))
        self.Tab_4.tabWidget.setTabText(self.Tab_4.tabWidget.indexOf(self.Tab_4.tab_1), _translate("AMaDiA_Main_Window", "Matrix Input"))
        self.Tab_4.EquationTab_New_Equation_Button.setText(_translate("AMaDiA_Main_Window", "New Equation"))
        self.Tab_4.EquationTab_Load_Selected_Button.setText(_translate("AMaDiA_Main_Window", "Load Selected"))
        self.Tab_4.EquationTab_New_Equation_Name_Input.setToolTip(_translate("AMaDiA_Main_Window", "Enter the equation name"))
        self.Tab_4.EquationTab_New_Equation_Name_Input.setPlaceholderText(_translate("AMaDiA_Main_Window", "Enter the equation name"))
        self.Tab_4.tabWidget.setTabText(self.Tab_4.tabWidget.indexOf(self.Tab_4.tab_2), _translate("AMaDiA_Main_Window", "History"))
        self.Tab_4.FormulaInput.setPlaceholderText(_translate("AMaDiA_Main_Window", "WIP: Input a formula (using the names of the matrices) and hit return"))
        self.Tab_4.DirectInput.setPlaceholderText(_translate("AMaDiA_Main_Window", "WIP: This Widget is currently a placeholder but if you insert 'name = value' and hit ctrl+enter those variables (one per line if you want multiple) will be loaded into the current equation."))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Tab_4), _translate("AMaDiA_Main_Window", "Multi-Dim"))
from AGeLib.AGeGW import MplWidget_2D_Plot, MplWidget_LaTeX
from AGeLib.AGeWidgets import ListWidget, MTabWidget
from AMaDiA_Files.AMaDiA_Widgets import AMaDiA_3DPlotWidget, AMaDiA_ComplexPlotWidget, AMaDiA_LineEdit, AMaDiA_TableWidget, AMaDiA_TextEdit, HistoryWidget
