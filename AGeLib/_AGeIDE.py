#region General Import
from ._import_temp import *
import types
import builtins

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import typing
except:
    pass
#endregion General Import

#region AGe Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
from . import _AGeToPy
from . import AGeToPy
#endregion AGe Import

#region Special Imports
from . import _AGeIDE_SH
#endregion Special Imports


#region IDE General Widgets

#FEATURE: Make TextEdit that supports multiple cursors at the same time
#CRITICAL: Move this Widget to AGeWidgets in the Text Widgets category
#class MultiTextEdit(TextEdit): #WIP
    #"""
    #Version of TextEdit that supports multiple cursors.
    #"""
    # https://www3.sra.co.jp/qt/relation/doc-snapshot/qtgui/richtext-cursor.html -> Multiple Cursors
    # https://lost-contact.mit.edu/afs/ific.uv.es/project/atlas/software/ganga_old/external/pyqt/3.13_python234/slc3_gcc323/doc/html/qtextedit.html#setSelection
    #   void QTextEdit::setSelection ( int paraFrom, int indexFrom, int paraTo, int indexTo, int selNum = 0 )
    #   Any existing selections which have a different id (selNum) are left alone, but if an existing selection has the same id as selNum it is removed and replaced by this selection.
    #   This can be used to make different selections by giving them different IDs.
    #   Most Textinteractions must be reimplemented to handle the other selections correctly since they are ignored by default in most cases.
    #   Furthermore only the first cursor is visible thus the other cursors must be implemented as well with some graphic trickery.
    #def __init__(self, parent=None):
    #    super(MultiTextEdit, self).__init__(parent)
    #    self.installEventFilter(self)
    #    self.cursorPositionChanged.connect(lambda: self.cursorUpdate())
    #    self.previousPositions = []
    #    self.cursors = []
    #    
    #def eventFilter(self, source, event):
    #    if event.type() == self.cursorPositionChanged and App().queryKeyboardModifiers() == QtCore.Qt.AltModifier:
    #        NC(3,"Press",input=(event,App().queryKeyboardModifiers()))
    #        try:
    #            App.ev.append(event)
    #        except:
    #            App.ev = [event]
    #    return super(MultiTextEdit, self).eventFilter(source, event)
    #
    #def cursorUpdate(self):
    #    self.cursors = [self.textCursor()]
    #    if App().queryKeyboardModifiers() == QtCore.Qt.AltModifier:
    #        for i in self.previousPositions:
    #            self.cursors.append(QtGui.QTextCursor(self.document()))
    #            self.cursors[-1].setPos(i)
    #        self.previousPositions.append(self.textCursor().pos())
    #    else:
    #        self.previousPositions = [self.textCursor().pos()]


class CodeEditorWidget(QtWidgets.QWidget): # https://stackoverflow.com/questions/38850277/multi-cursor-editing-with-qscintilla
    """
    This widget is a code editor. It is intended for documents with less than 1000 lines (and is only thoroughly tested with less than 100 lines) and might perform poorly on longer documents. \n
    When the user presses ctrl+return (or presses a special button) the signal `S_Execute` is emitted. The idea is that something happens to the code (get the code with `.text()`). \n
    This widget is not intended to be used as a proper IDE. It is intended for interactive things like the OverloadWidget and the console in the exec_Window. \n
    The code editor offers a TextEdit (derived from QTextEdit) and (if PyQt5.Qsci (QScintilla) is installed) a QsciScintilla widget to edit code with. \n
    The constructor can be supplied with a Lexer class and additionalKeywords. The additionalKeywords are used to initialize the Lexer. \n
    Please refer to AGeLib.PythonLexer if you want to implement your own lexer. \n
    Ctrl+return triggers the `S_Execute` signal. Connect this signal to whatever method you want to do something with the code. \n
    If you have extra ways to call the method connected to `S_Execute` connect them to `sendExecute` instead as that method first saves the code and then sends `S_Execute`. \n
    """
    #TODO: Add line numbers to Editor
    #TODO: Enable auto indentation for Editor
    #TODO: Make autocomplete for EditorSc
    #TODO: Try to add the Finder to EditorSc
    returnPressed = pyqtSignal()
    returnCtrlPressed = pyqtSignal()
    S_Execute = pyqtSignal()
    #def __init__(self, parent = None, Lexer = _AGeIDE_SH.Highlighter_Python_AGeSimple, additionalKeywords=[], ExecuteButton = True, ExecuteButtonToolTip = "Execute the code"):
    def __init__(self, parent = None, Lexer = _AGeIDE_SH.Highlighter_Python_SpyderAndQSci, additionalKeywords=[],
                    ExecuteButton = True, ExecuteButtonToolTip = "Execute the code",
                    SaveButton = False, LoadButton = False, StandardFolder = "", #CRITICAL: Implement these!!! (EDFA could use these to make saving and loading templates easier.)
                    CheckBox = False, CheckBoxToolTip = "This Check Box seems to have no function",
                    ):
        self.hasFloater = False
        self._rectToMultiLast = timetime()
        super(CodeEditorWidget, self).__init__(parent)
        self.QScintilla = QSciImported
        self.hasExecuteButton = ExecuteButton
        self.hasCheckBox = CheckBox
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        #
        self.EContainer = QtWidgets.QStackedWidget(self)
        #
        self.Editor = TextEdit(self)
        self.Editor_Finder = TextAddon_Finder(self,self.Editor)
        self.Editor.setObjectName("Editor")
        self.Editor.setTabChangesFocus(False)
        self.EContainer.addWidget(self.Editor_Finder)
        self.Editor.installEventFilter(self)
        #
        if self.QScintilla:
            # Docs: https://www.riverbankcomputing.com/static/Docs/QScintilla/annotated.html
            #       https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html
            #
            #REMINDER: Look at https://github.com/forkeith/pyblime/blob/master/pyblime/view.py
            # Make own Colours for highlighting
            #       https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciStyle.html
            #TODO: Load in all active variables:
            #       https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciLexerPython.html
            #       https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciAPIs.html
            # Make selection comment/uncomment hotkeys
            #       https://stackoverflow.com/questions/50355919/how-to-implement-a-comment-feature-that-works-with-multiple-selections-in-qscint
            self.EditorSc = Qsci.QsciScintilla(self)
            self.EditorSc.setObjectName("Editor")
            self.EContainer.addWidget(self.EditorSc)
            self.EditorSc.installEventFilter(self)
            self.EContainer.setCurrentWidget(self.EditorSc)
            self.setupEditorSc()
            #self.EditorSc.QSCN_SELCHANGED.connect(lambda beenSet: self.rectToMulti(beenSet))
        else:
            NC(3,"Could not load PyQt5.Qsci (QScintilla). Coding widgets will use base Qt Widgets instead.\nPlease install PyQt5.Qsci (QScintilla) for an even better coding experience. (https://pypi.org/project/QScintilla/)",unique=True)
            self.EditorSc = None
        self.layout().addWidget(self.EContainer)
        App().S_FontChanged.connect(lambda: self._UpdateFontSize())
        App().S_ColourChanged.connect(lambda: self.recolour())
        if self.QScintilla or self.hasExecuteButton or self.hasCheckBox:
            self.Floater = QtWidgets.QWidget(self)
            self.Floater.setFocusPolicy(QtCore.Qt.NoFocus)
            self.Floater.setLayout(QtWidgets.QGridLayout(self.Floater))
            self.Floater.layout().setObjectName("gridLayout")
            self.Floater.layout().setContentsMargins(0,0,0,0)
            self.Floater.layout().setSpacing(0)
            MaxSizeFactor = 0
            if self.QScintilla:
                MaxSizeFactor += 1
                self.toggleButton = QtWidgets.QToolButton(self.Floater)
                self.toggleButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
                self.toggleButton.setMaximumSize(24, 24)
                self.toggleButton.setFocusPolicy(QtCore.Qt.NoFocus)
                self.toggleButton.setToolTip("Toggle between the QScintilla Editor and the Qt Editor")
                self.toggleButton.clicked.connect(lambda: self.toggleEditor())
                self.Floater.layout().addWidget(self.toggleButton,0,2)
            if self.hasExecuteButton:
                MaxSizeFactor += 1
                self.executeButton = QtWidgets.QToolButton(self.Floater)
                self.executeButton.setIcon(recolourIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)))
                self.executeButton.setMaximumSize(24, 24)
                self.executeButton.setFocusPolicy(QtCore.Qt.NoFocus)
                self.executeButton.setToolTip(ExecuteButtonToolTip+"\n(shortcut ctrl+return)")
                self.executeButton.clicked.connect(lambda: self.sendExecute())
                self.Floater.layout().addWidget(self.executeButton,0,1)
            if self.hasCheckBox:
                MaxSizeFactor += 1
                self.CheckBox = QtWidgets.QCheckBox(self.Floater)
                self.CheckBox.setMaximumSize(24, 24)
                self.CheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
                self.CheckBox.setToolTip(CheckBoxToolTip)
                self.CheckBox.setChecked(False)
                self.Floater.layout().addWidget(self.CheckBox,0,0)
            self.Floater.raise_()
            self.Floater.setMaximumSize(MaxSizeFactor*24, 24)
            self.hasFloater = True
        else:
            self.hasFloater = False
        try:
            #self.Input_Field_Highlighter = PythonSH(self.Editor.document())
            #self.Lexer = PythonLexerQsci(self.EditorSc, additionalKeywords)
            self.Lexer = Lexer(self.Editor, self.EditorSc, additionalKeywords)
        except:
            NC(1,exc=True)
        self.recolour()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.setFont(font)
        self.installEventFilter(self)

    def sendExecute(self):
        """
        This method saves a backup of the code and then emits the S_Execute signal. \n
        If you have extra ways to call the method connect them to this method. (Do not connect them to S_Execute.)
        """
        self.saveBackup()
        self.S_Execute.emit()

    def saveBackup(self):
        """
        This method saves the code in a file. \n
        There are 10 Files that contain the last 10 inputs. \n
        The most recently modified file's increment is always overwritten. \n
        Thus when 02 was last modified 03 will be used for the backup which then becomes the most recently modified file.
        """
        #MAYBE: move this to MainApp and give a string that serves as the file name. This way every widget __can__ have its own history and the execute and overload widget histories should be seperated
        try:
            if App().AGeLibPathOK:
                paths = sorted(pathlib.Path(App().FolderPath_CodeBackup).iterdir(), key=os.path.getmtime)
                paths.reverse()
                current = "codeBackup_00.txt"
                for i in paths:
                    if i.name.startswith("codeBackup_"):
                        try:
                            if int(i.name[11:13]) == 9:
                                current = "codeBackup_00.txt"
                            else:
                                num = str(int(i.name[11:13])+1)
                                if len(num) == 1:
                                    num = "0"+num
                                current = f"codeBackup_{num}.txt"
                        except:
                            NC(4,"Error while saving a backup of the executed code",exc=True)
                        else:
                            break
                FileName = os.path.join(App().FolderPath_CodeBackup, current)
                with open(FileName,'w',encoding="utf-8") as text_file:
                    text_file.write(self.text())
        except:
            NC(2,"Could not save a backup of the executed code",exc=True)
    
    def text(self):
        if self.EContainer.currentWidget() == self.Editor_Finder:
            text = self.Editor.toPlainText()
        elif self.QScintilla:
            text = self.EditorSc.text()
        else:
            raise Exception("Current editor is not self.Editor but self.QScintilla is false... How can this be? Which editor are you using?!")
        #CRITICAL: Instead of changing all tabs, only tabs between "\n" and the first non-space-charater should be converted (using a regular expression that searches for tabs between those but accepting tabs and space in between)
        return text.replace("\t","    ")
    
    def toPlainText(self):
        return self.text()
        
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        try:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                    self.returnPressed.emit()
                if (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter) and event.modifiers() == QtCore.Qt.ControlModifier and (source == self.Editor or source == self.EditorSc):
                    self.returnCtrlPressed.emit()
                    self.sendExecute()
                if event.key() == QtCore.Qt.Key_Backspace and self.QScintilla:
                    self.EditorSc.setScrollWidth(10) # Update the scroll width when backspace is pressed. (Can fail when holding backspace on longer documents but can be updated again by simply selecting another line)
            #if self.QScintilla and event.type() == QtCore.QEvent.KeyRelease:
            #    #if event.key() == QtCore.Qt.AltModifier or event.key() == QtCore.Qt.ShiftModifier:
            #    #    modifiers = QtWidgets.QApplication.keyboardModifiers()
            #    #    if not bool(modifiers &( QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier)): # if alt and shift are both not pressed
            #    #        self.rectToMulti()
            #    if event.key() == QtCore.Qt.ShiftModifier:
            #        modifiers = QtWidgets.QApplication.keyboardModifiers()
            #        if not bool(modifiers & QtCore.Qt.AltModifier): # if alt and shift are both not pressed
            #            self.rectToMulti()
            #    elif event.key() == QtCore.Qt.AltModifier:
            #        modifiers = QtWidgets.QApplication.keyboardModifiers()
            #        if not bool(modifiers & QtCore.Qt.ShiftModifier): # if alt and shift are both not pressed
            #            self.rectToMulti()
        except:
            pass
        return super(CodeEditorWidget, self).eventFilter(source, event)

    def resizeEvent(self, event):
        super(CodeEditorWidget, self).resizeEvent(event)
        if self.hasFloater:
            self.Floater.move(self.rect().right() - self.Floater.width(), 0)
            self.Floater.raise_()

    def toggleEditor(self):
        if self.QScintilla:
            if self.EContainer.currentWidget() == self.Editor_Finder:
                self.EContainer.setCurrentWidget(self.EditorSc)
            else:
                self.EContainer.setCurrentWidget(self.Editor_Finder)
        
    def setupEditorSc(self):
        if self.QScintilla:
            # See https://www.scintilla.org/ScintillaDoc.html#SCI_SETMULTIPLESELECTION
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETMULTIPASTE,1)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETADDITIONALSELECTIONTYPING,1)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETMULTIPLESELECTION,1)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETVIRTUALSPACEOPTIONS,1) #When problems arise set this to 5 which disables wrapping to the last line when pressing left while the caret is already in the beginning of a line
            #
            self.EditorSc.setTabWidth(4)
            self.EditorSc.setTabIndents(True)
            self.EditorSc.setAutoIndent(True)
            self.EditorSc.setIndentationsUseTabs(True)
            self.EditorSc.setUtf8(True)
            #
            self.EditorSc.setScrollWidth(10)
            self.EditorSc.setScrollWidthTracking(True)
            self.EditorSc.setMargins(1) #2
            self.EditorSc.setFolding(Qsci.QsciScintilla.CircledFoldStyle , margin=0)
            self.EditorSc.setMarginType(0, Qsci.QsciScintilla.NumberMargin)
            self.EditorSc.setMarginWidth(0, "000")
            # Following does not handle the margin colour correctly. Maybe I will try to make it work later...
            #self.EditorSc.setFolding(Qsci.QsciScintilla.CircledFoldStyle , margin=1)
            #self.EditorSc.setMarginType(1, Qsci.QsciScintilla.SymbolMargin)
            #self.EditorSc.setMarginWidth(1, "00")
            #
            self.EditorSc.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)
            self.EditorSc.setCaretLineVisible(True)
            self.EditorSc.setCaretLineFrameWidth(1)
            #
            self.EditorSc.setIndentationGuides(True) # Sets vertical lines to highlight blocks
            #
            #VALIDATE: This is probably done automatically. It is set correctly on windows. Is it set correctly on Linux, too?
            # Does "Darwin" use Unix or Mac EoL symbols? I think it might use Unix... If this is ever commented out "Darwin" should be added to one of those cases...
            #if platform.system() == "Linux":
            #    self.EditorSc.setEolMode(Qsci.QsciScintilla.EolUnix)
            #elif platform.system() == "Mac":
            #    self.EditorSc.setEolMode(Qsci.QsciScintilla.EolMac)
            #else:
            #    self.EditorSc.setEolMode(Qsci.QsciScintilla.EolWindows)
            
            # Set commands
            commands = self.EditorSc.standardCommands()
            commands.find(Qsci.QsciCommand.Redo).setKey(QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Z)
            commands.find(Qsci.QsciCommand.MoveSelectedLinesUp).setKey(QtCore.Qt.AltModifier | QtCore.Qt.Key_Up)
            commands.find(Qsci.QsciCommand.MoveSelectedLinesDown).setKey(QtCore.Qt.AltModifier | QtCore.Qt.Key_Down)
            commands.find(Qsci.QsciCommand.LineUpRectExtend).setKey(QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Up)
            commands.find(Qsci.QsciCommand.LineDownRectExtend).setKey(QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Down)
            commands.find(Qsci.QsciCommand.CharLeftRectExtend).setKey(QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Left)
            commands.find(Qsci.QsciCommand.CharRightRectExtend).setKey(QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Right)
    
    def setFont(self,font):
        font.setPointSize(App().font().pointSize())
        super(CodeEditorWidget, self).setFont(font)
        self.Editor.setFont(font)
        if self.QScintilla:
            self.EditorSc.setFont(font)
            self.Lexer.setFont(font)
            self.EditorSc.setScrollWidth(10)
            self.EditorSc.setMarginWidth(0, "000")

    def _UpdateFontSize(self):
        font = self.font()
        font.setPointSize(App().font().pointSize())
        self.setFont(font)
        #self.Editor.setFont(font)
        #if self.QScintilla:
        #    self.EditorSc.setFont(font)
        #    self.Lexer.setFont(font)
        #else:
        #    pass
    
    def recolour(self):
        if self.QScintilla:
            self.EditorSc.setPaper(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            self.EditorSc.setColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text))
            self.EditorSc.setCaretForegroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text)) #Set text cursor colour #TODO: Improve visibility
            self.Lexer.recolour()
            self.EditorSc.setMarginsBackgroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.AlternateBase))
            self.EditorSc.setMarginsForegroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text))
            #self.EditorSc.setMarginBackgroundColor(1,App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.AlternateBase))
            #
            self.EditorSc.setCaretLineBackgroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.AlternateBase)) # Sets the background of the line the cursor is in
            self.EditorSc.setMatchedBraceBackgroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.AlternateBase))
            self.EditorSc.setMatchedBraceForegroundColor(App().PythonLexerColours["Keyword"].color())
            self.EditorSc.setUnmatchedBraceBackgroundColor(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            self.EditorSc.setUnmatchedBraceForegroundColor(App().PythonLexerColours["UnclosedString"].color())
        if self.hasExecuteButton:
            try:
                self.executeButton.setIcon(recolourIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)))
            except:
                pass

    def setText(self,Text): #TODO: Turn this into "select all"+"insert" to not reset the history every time
        self.Editor.setPlainText(str(Text))
        if self.QScintilla:
            self.EditorSc.setScrollWidth(10)
            self.EditorSc.setText(str(Text))

    def rectToMulti(self, beenSet): # WHY THE BLOODY HELL CAN'T I GET THIS BLOODY HACK TO BLOODY WORK?!?!
        if beenSet and self.QScintilla and bool(QtWidgets.QApplication.keyboardModifiers()&( QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier)) and self._rectToMultiLast != timetime():
            self._rectToMultiLast = timetime()
            #if self.EditorSc.SendScintilla(self.EditorSc.SCI_GETSELECTIONMODE) == 1:
            #NC(3,self.EditorSc.SendScintilla(self.EditorSc.SCI_SELECTIONISRECTANGLE))
            #if self.EditorSc.SendScintilla(self.EditorSc.SCI_SELECTIONISRECTANGLE):
            #f,t = self.EditorSc.SendScintilla(self.EditorSc.SCI_GETRECTANGULARSELECTIONCARET), self.EditorSc.SendScintilla(self.EditorSc.SCI_SETRECTANGULARSELECTIONANCHOR)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETSELECTIONMODE,2)
            #m = self.EditorSc.SendScintilla(self.EditorSc.SCI_GETMAINSELECTION)
            n = self.EditorSc.SendScintilla(self.EditorSc.SCI_GETSELECTIONS)
            #f,t = self.EditorSc.SendScintilla(self.EditorSc.SCI_GETSELECTIONNCARET,m), self.EditorSc.SendScintilla(self.EditorSc.SCI_GETSELECTIONNANCHOR,m)
            #NC(3,[f,t,self.EditorSc.SendScintilla(self.EditorSc.SCI_ADDSELECTION,f,t),n,m])
            self.EditorSc.SendScintilla(self.EditorSc.SCI_ADDSELECTION,0,0)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_DROPSELECTIONN,n)
            self.EditorSc.SendScintilla(self.EditorSc.SCI_SETSELECTIONMODE,2)

#endregion IDE General Widgets
#region IDE Helper Widgets
class _InspectWidget_memberItem(QtWidgets.QWidget):
    def __init__(self,item,InspectWidget,parent=None):
        super(_InspectWidget_memberItem, self).__init__(parent)
        self.string, self.item = item
        self.RowHeightFactor = 1
        self.RowHeightSpacer = 10
        self.InspectWidget = InspectWidget
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        #
        self._t_ret = None
        self.buttons = []
        self.RowHeight = QtGui.QFontMetrics(self.font()).height()*self.RowHeightFactor + self.RowHeightSpacer
        self.setFixedHeight(self.RowHeight)
        #
        self.label = QtWidgets.QLabel(self.string,self)
        self.label.setFixedHeight(self.RowHeight)
        self.layout().addWidget(self.label,0,0)
        #
        #self.Button_Info = Button(self,"I",lambda: self.showInfo())
        self.Button_Info = QtWidgets.QToolButton(self)
        self.buttons.append(self.Button_Info)
        self.Button_Info.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation))
        self.Button_Info.setFixedSize(self.RowHeight,self.RowHeight)
        self.Button_Info.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Button_Info.setToolTip("Show Info")
        self.Button_Info.clicked.connect(lambda: self.showInfo())
        self.layout().addWidget(self.Button_Info,0,100)
        #
        self.Button_Zoom = QtWidgets.QToolButton(self)
        self.buttons.append(self.Button_Zoom)
        self.Button_Zoom.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))
        self.Button_Zoom.setFixedSize(self.RowHeight,self.RowHeight)
        self.Button_Zoom.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Button_Zoom.setToolTip("Add this to the name input")
        self.Button_Zoom.clicked.connect(lambda: self.zoom())
        self.layout().addWidget(self.Button_Zoom,0,99)
        #
        # Dynamic Buttons
        #TODO: Button_Code if applicable
        #self.Button_Code = QtWidgets.QToolButton(self)
        #
        #TODO: Button_Help if applicable (Validate: This is already be part of info, isn't it?)
        #self.Button_Help = QtWidgets.QToolButton(self)
        #
        try:
            if hasattr(self.item,"__call__"):
                self.Button_Call = QtWidgets.QToolButton(self)
                self.buttons.append(self.Button_Call)
                self.Button_Call.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight))
                self.Button_Call.setFixedSize(self.RowHeight,self.RowHeight)
                self.Button_Call.setFocusPolicy(QtCore.Qt.NoFocus)
                self.Button_Call.setToolTip("Call this method and display the return value")
                self.Button_Call.clicked.connect(lambda: self.callMethod())
                self.layout().addWidget(self.Button_Call,0,96)
        except:
            pass
        #
        self.installEventFilter(self)

    def showInfo(self):
        try:
            text = f"{self.string}\nType: {type(self.item)}\n{self.stringRep(Format = True)}"
            try:
                if self.item.__doc__ != "":
                    text += f"\nDoc:\n{self.item.__doc__}"
            except:
                pass
            self.InspectWidget.DisplayWidget.setPlainText(text)
        except:
            NC(1,"Could not show info",exc=True)

    def stringRep(self, item = "no strItem given", Format = True): #TODO: Improve Formatting
        try:
            if item == "no strItem given":
                item = self.item
            strItem = str(item)
            if len(strItem) >= 4e6:
                # if the String is too big we don't bother processing it
                # since processing the string with python for loops would take too long
                #MAYBE: ask the user if the processing is worth the time with a pop up dialogue
                string = "\n"+strItem+"\n\n\n"
            elif type(item) in [tuple,list]:
                if len(strItem) <= 40:
                    string = strItem
                else:
                    if type(item) == list: s = ("[","]")
                    elif type(item) == tuple: s = ("(",")")
                    else: s = ("[","]")
                    string = f"\n{s[0]}\n"+" ,\n".join([str(i) for i in item])+f"\n{s[1]}\n\n\n"
                #TODO: If numpy array display everything! QPlainTextEdit can handle it!
                #TODO: If List, Dict, etc split it in lines for readability and display the Length
                #REMINDER: You have already written something like that for EDFA
            else:
                string = strItem
                if Format and (len(string)>=40 or len(string.splitlines())>1): string = "\n"+string+"\n\n\n"
        except:
            NC(2,"Error while extracting string",exc=True)
            string = str(self.item)
            if Format: string = "\n"+string+"\n\n\n"
        if Format: string = "\nString Representation: "+string
        return string

    def showCode(self):
        pass

    def showHelp(self):
        pass

    def zoom(self):
        self.InspectWidget.zoom(self.string)

    def callMethod(self):
        proceed = False#QtWidgets.QMessageBox.question(None,"Are you sure",f"Do you really want to call the method \"{self.string}\"?") == QtWidgets.QMessageBox.Yes
        args, proceed = QtWidgets.QInputDialog.getText(self,"Are you sure?",f"Do you really want to call the method \"{self.string}\"?\nIf so, do you want to call it with arguments?")
        if not proceed: return
        try:
            exec(f"_self_self._t_ret = _self_self.item({args})", self.InspectWidget.Globals, {"self":self.InspectWidget.window(),"_self_self":self})
            #self._t_ret = self.item()
        except:
            self._t_ret = sys.exc_info()
        try:
            text = f"{self.string}\nReturn Type: {type(self._t_ret)}\n{self.stringRep(item = self._t_ret, Format = True)}"
            self.InspectWidget.DisplayWidget.setPlainText(text)
        except:
            NC(1,"Could not show return value",exc=True)

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
            self.RowHeight = QtGui.QFontMetrics(self.font()).height()*self.RowHeightFactor + self.RowHeightSpacer
            self.setFixedHeight(self.RowHeight)
            self.label.setFixedHeight(self.RowHeight)
            for i in self.buttons:
                i.setFixedSize(self.RowHeight,self.RowHeight)
        return super(_InspectWidget_memberItem, self).eventFilter(source, event)

class _MemberListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(_MemberListWidget, self).__init__(parent)
        self.installEventFilter(self)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)==1:
                    item = SelectedItems[0]
                    QtWidgets.QApplication.clipboard().setText(self.itemWidget(item).string)
                    event.accept()
                    return
            super(_MemberListWidget, self).keyPressEvent(event)
        except:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(_MemberListWidget).keyPressEvent",input=str(event))
            super(_MemberListWidget, self).keyPressEvent(event)

#endregion IDE Helper Widgets
#region IDE Widgets
#CRITICAL: Validate (should already be in) self should refer to the window instead of the widget for easier navigation

class ConsoleWidget(QtWidgets.QSplitter):
    def __init__(self, parent = None, additionalKeywords=[]):
        """
        TODO: Write Documentation
        """
        super(ConsoleWidget, self).__init__(parent)
        self.setOrientation(QtCore.Qt.Horizontal)
        #
        self.Globals = globals()
        self.Locals = {}
        self.LocalsExternal = {}
        self.updateLocals = None
        #
        
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.Console = CodeEditorWidget(self,additionalKeywords=self.additionalKeywords()+additionalKeywords,
                                        ExecuteButton=True, ExecuteButtonToolTip="Execute the code",
                                        CheckBox = True, CheckBoxToolTip = "If checked the locals will be persistend between executions.\nThus if not checked the locals will be cleared before and after execution."
                                        )
        self.Console.setFont(font)
        self.Console.setText("# TODO: Write some introductory text here.\n")
        
        #TODO: Load the and the class members to the auto complete of self.Console
        
        self.DisplayWidget = QtWidgets.QPlainTextEdit(self)
        self.DisplayWidget.setObjectName("DisplayWidget")
        self.DisplayWidget.setPlainText("Use 'display(\"text\")' to display text.\nAlternatively use `dpl` to append text. It works like `print`. Use display(\"\") to clear the display.\n")
        metrics = QtGui.QFontMetrics(self.DisplayWidget.font())
        try:
            self.DisplayWidget.setTabStopDistance(4 * metrics.averageCharWidth())
        except: # For old Qt Versions
            self.DisplayWidget.setTabStopWidth(4 * metrics.averageCharWidth())
        self.DisplayWidget.installEventFilter(self)
        self.DisplayWidget_Finder = TextAddon_Finder(self,self.DisplayWidget)
        self.Console.S_Execute.connect(lambda: self.executeCode())
        
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == QtCore.QEvent.FontChange:
            metrics = QtGui.QFontMetrics(self.DisplayWidget.font())
            try:
                self.DisplayWidget.setTabStopDistance(4 * metrics.averageCharWidth())
            except: # For old Qt Versions
                self.DisplayWidget.setTabStopWidth(4 * metrics.averageCharWidth())
        return super(ConsoleWidget, self).eventFilter(source, event)
        
    def additionalKeywords(self):
        return ["App","NC",
                "app","window","mw","self","display","dpl","dir","code","help","getPath"
                ]

    def setGlobals(self, Globals = None):
        # type: (dict) -> None
        """
        Set the globals used in executeCode. If None the globals of this method are loaded.
        """
        # , self.Globals, {"self":self}
        if Globals == None:
            self.Globals = globals()
        else:
            self.Globals = Globals
        #TODO: Update autocomplete

    def setLocals(self, Locals = {}):
        """
        Set the locals used in executeCode.
        """
        self.LocalsExternal = Locals

    def setLocalsUpdateFunction(self, function = None):
        """
        Set a function that is called before executing code. This function must return a dictionary containing additional locals that are used when executing the code.
        """
        self.updateLocals = function

    def executeCode(self):
        if self.updateLocals: self.setLocals(self.updateLocals())
        input_text = self.Console.text()
        try:
            if not self.Console.CheckBox.checkState():
                self.Locals = {}
            # Set app and window for the local dictionary so that they can be used in the execution
            self.Locals.update({
                "app"     : App() ,
                "window"  : App().MainWindow ,
                "mw"      : App().MainWindow ,
                "self"    : self.window() ,
                "display" : self.display ,
                "dpl"     : self.dpl ,
                "dir"     : self.dir ,
                "code"    : self.code ,
                "help"    : self.help ,
                "getPath" : lambda mustExist=False: getPath(mustExist) ,
                })
            self.Locals.update(self.LocalsExternal)
            exec(input_text, self.Globals, self.Locals)
            if not self.Console.CheckBox.checkState():
                self.Locals = {}
        except:
            NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="ConsoleWidget.executeCode",input=input_text)

    def display(self, *args, sep=" ", end="\n"):
        # type: (*object,str,str) -> None
        l = []
        for i in args:
            l.append(str(i))
        self.DisplayWidget.setPlainText(str(sep).join(l)+str(end))
        
    def dpl(self, *args, sep=" ", end="\n"):
        # type: (*object,str,str) -> None
        l = []
        for i in args:
            l.append(str(i))
        self.DisplayWidget.setPlainText(self.DisplayWidget.toPlainText()+str(sep).join(l)+str(end))

    def dir(self,thing,filterItem=None):
        # type: (typing.Any,list[str]|None) -> list[str]
        if type(filterItem) == type(None):
            self.DisplayWidget.setPlainText("\n".join(filter(filterItem, dir(thing))))
        elif type(filterItem) in [list,tuple]:
            self.DisplayWidget.setPlainText("\n".join(filter(lambda x: self._filterHelper(x,filterItem), dir(thing))))
        else:
            self.DisplayWidget.setPlainText("\n".join(filter(lambda x: str(filterItem).lower() in x.lower(), dir(thing))))
        return dir(thing)

    def code(self,item):
        # type: (types.MethodType|types.FunctionType) -> None
        self.DisplayWidget.setPlainText(inspect.getsource(item))

    def help(self,item):
        self.DisplayWidget.setPlainText(inspect.getdoc(item))
        
    def _filterHelper(self,x,filterItem):
        # type: (str, list[str]) -> bool
        for i in filterItem:
            if str(i).lower() in x.lower(): return True
        return False

    def setText(self,Text): #TODO: Turn this into "select all"+"insert" to not reset the history every time
        self.Console.setText(Text)

    def text(self):
        return self.Console.text()

    def toPlainText(self):
        return self.Console.toPlainText()

class InspectWidget(QtWidgets.QWidget):
    #TODO: Add new tab for inspection of items with a gui for self.help, self.dir and self.code
    #TODO: Make Documentation that is accessible in the Window (MAYBE: New tab with explanations)
    # ### InspectWidget ###
    # Inspection should contain:
    # o = base().terrain
    # #o = base().terrain.get_root()
    # 
    # self.dir(o,"")
    # #self.help(o)
    # #self.code(o)
    # #display(o)
    # #display(type(o))
    # #display(o.__module__)
    # #display(o.__name__) # Improve
    # #display(str(o))
    # #display(len(o))
    #
    # Some fun stuff from the inspect module
    #
    # Sketch: Input | (dir) List of methods and attributes with buttons for type, help, code, string representation directly on the items as applicable | Area to display stuff when a button is pressed
    def __init__(self, parent = None):
        """
        TODO: Write Documentation
        """
        super(InspectWidget, self).__init__(parent)
        #
        self.Globals = globals()
        #
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        #
        self.Splitter = QtWidgets.QSplitter(self)
        self.Splitter.setObjectName("Splitter")
        self.Splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout().addWidget(self.Splitter,0,0)
        #
        self.MemberWidget = QtWidgets.QWidget(self.Splitter)
        self.MemberWidget.setLayout(QtWidgets.QGridLayout(self.MemberWidget))
        self.MemberWidget.layout().setObjectName("gridLayout")
        self.MemberWidget.layout().setContentsMargins(0,0,0,0)
        #
        #TODO: Reduce the width of the buttons to a minimum
        self.NameInput = LineEdit(self)
        self.NameInput.setPlaceholderText("Input Object and press return")
        self.MemberWidget.layout().addWidget(self.NameInput,0,0)
        self.NameInput.returnPressed.connect(lambda: self.loadMembers())
        self.ButtonLoadBuiltins = Button(self,"B",lambda: self.loadBuiltins())
        self.ButtonLoadBuiltins.setToolTip("Load the Builtins")
        #self.ButtonLoadBuiltins.setFocusPolicy(QtCore.Qt.NoFocus)
        self.MemberWidget.layout().addWidget(self.ButtonLoadBuiltins,0,1)
        self.ButtonLoadGlobals = Button(self,"G",lambda: self.loadGlobals())
        self.ButtonLoadGlobals.setToolTip("Load the Globals")
        #self.ButtonLoadGlobals.setFocusPolicy(QtCore.Qt.NoFocus)
        self.MemberWidget.layout().addWidget(self.ButtonLoadGlobals,0,2)
        #
        self.FilterInput = LineEdit(self)
        self.FilterInput.setPlaceholderText("Input Filter word and press return")
        self.FilterInput.setToolTip("Multiple filter words may be seperated by comma or space.\nThe filter words are combined with or. This means that\nif you want to get everything related to colour you should try \"paint,colour,color,palette\" as your filter.")
        self.MemberWidget.layout().addWidget(self.FilterInput,1,0,1,3)
        self.FilterInput.returnPressed.connect(lambda: self.loadMembers())
        #
        self.MemberList = _MemberListWidget(self)
        self.MemberList.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.MemberList.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.MemberList.itemDoubleClicked.connect(lambda item: self.MemberList.itemWidget(item).showInfo())
        self.MemberList.installEventFilter(self)
        self.MemberWidget.layout().addWidget(self.MemberList,2,0,1,3)
        #
        #MAYBE: Make this a QStackedWidget (without buttons) that toggles between QPlainTextEdit for text display and CodeWidget for code display
        #TODO: At the very least this should get its own QFontComboBox for better readability (maybe with a checkbox that quickly toggles between global font and QFontComboBox font)
        self.DisplayWidget = QtWidgets.QPlainTextEdit(self)
        self.DisplayWidget.setObjectName("displayWidget")
        #self.DisplayWidget.setPlainText("Use 'display(\"text\")' to display text.\nAlternatively use `dpl` to append text. It works like `print`. Use display(\"\") to clear the display.\n")
        metrics = QtGui.QFontMetrics(self.DisplayWidget.font())
        try:
            self.DisplayWidget.setTabStopDistance(4 * metrics.averageCharWidth())
        except: # For old Qt Versions
            self.DisplayWidget.setTabStopWidth(4 * metrics.averageCharWidth())
        self.displayWidget_Finder = TextAddon_Finder(self.Splitter,self.DisplayWidget)
        self.DisplayWidget.setTabChangesFocus(True) #MAYBE: Is that good? I can't imagine a situation in which you would want to write a tab in this widget... It is for display, not for editing...
        #
        App().S_FontChanged.connect(lambda: self.updateListUnitGeometry())
        #
        self.setTabOrder(self.ButtonLoadGlobals, self.ButtonLoadBuiltins)
        self.setTabOrder(self.ButtonLoadBuiltins, self.NameInput)
        self.setTabOrder(self.NameInput, self.FilterInput)
        self.setTabOrder(self.FilterInput, self.MemberList)
        self.setTabOrder(self.MemberList, self.DisplayWidget)

    def setGlobals(self, Globals = None):
        # type: (dict) -> None
        """
        Set the globals used in loadMembers. If None the globals of this method are loaded.
        """
        # , self.Globals, {"self":self}
        if Globals == None:
            self.Globals = globals()
        else:
            self.Globals = Globals
        #TODO: Update autocomplete

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget|_MemberListWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        try:
            if event.type() == 6: # QtCore.QEvent.KeyPress
                if source == self.MemberList:
                    if event.key() == QtCore.Qt.Key_Space or event.key() == QtCore.Qt.Key_Return:
                        listItems = source.selectedItems()
                        if not listItems: pass
                        elif len(listItems) != 1: pass
                        else: source.itemWidget(listItems[0]).showInfo()
        except:
            NC(lvl=1,exc=sys.exc_info())
        return super(InspectWidget, self).eventFilter(source, event)

    def loadMembers(self): # self.window().InspectWidget.loadMembers
        self.MemberList.clear()
        if self.NameInput.text().strip() == "": # If the field is empty self.Globals and buildins are displayed
            return
        self.dir()
        self._temp_members_dict = {}
        for i in self._temp_members:
            try:
                self._temp_members_dict[i] = self._objectGetter(i)
            except:
                ExceptionOutput()
        self.displayMembers()
        
    def loadBuiltins(self):
        self.MemberList.clear()
        self.dir(builtins)
        self._temp_members_dict = {}
        for i in self._temp_members:
            try:
                self._temp_members_dict[i] = self._objectGetter_Builtins(i)
            except:
                ExceptionOutput()
        self.displayMembers()

    def loadGlobals(self):
        self.MemberList.clear()
        self.filter(self.Globals.keys())
        self._temp_members_dict = {}
        for i in self._temp_members:
            try:
                self._temp_members_dict[i] = self.Globals[i]
            except:
                ExceptionOutput()
        self.displayMembers()

    def displayMembers(self):
        for member in self._temp_members_dict.items():
            itemN = QtWidgets.QListWidgetItem()
            widget = _InspectWidget_memberItem(member,self,self.MemberList)
            itemN.setSizeHint(widget.sizeHint())
            self.MemberList.addItem(itemN)
            self.MemberList.setItemWidget(itemN, widget)
        self.updateListUnitGeometry()

    def _objectGetter(self,string):
        self._temp_member = None
        exec("_self_self._temp_member = "+self.NameInput.text()+"."+string, self.Globals, {"self":self.window(),"_self_self":self})
        return self._temp_member

    def _objectGetter_Builtins(self,string):
        self._temp_member = None
        exec("_self_self._temp_member = "+string, vars(builtins), {"self":self.window(),"_self_self":self})
        return self._temp_member

    def dir(self, thing=None):
        # type: (typing.Any) -> list[str]
        self._temp_members = []
        if thing == None:
            exec("_self_self._temp_thing = dir("+self.NameInput.text()+")", self.Globals, {"self":self.window(),"_self_self":self})
        else:
            self._temp_thing = dir(thing)
        #if type(filterItem) == type(None) or filterItem == "":
        #    self._temp_members = filter(filterItem, self._temp_thing)
        return self.filter(self._temp_thing)

    def filter(self,listToFilter):
        # type: (list[str]) -> list[str]
        self._temp_thing = listToFilter
        filterItem = self.FilterInput.text().strip()
        if "," in filterItem or " " in filterItem:
            filterItem = filterItem.split(",")
            filterItem_temp = [i.strip() for i in filterItem]
            filterItem = []
            for i in filterItem_temp:
                filterItem += [x for x in i.split(" ")]
            #filterItem = [x for x in i.split(" ") for i in filterItem]
            self._temp_members = list(filter(lambda x: self._filterHelper(x,filterItem), self._temp_thing))
        else:
            self._temp_members = list(filter(lambda x: str(filterItem).lower() in x.lower(), self._temp_thing))
        return self._temp_members
        
    def _filterHelper(self,x,filterItem):
        for i in filterItem:
            if str(i).lower() in x.lower(): return True
        return False

    def zoom(self,text):
        """Add `.text` to the NameInput"""
        self.NameInput.moveCursor(QtGui.QTextCursor.End)
        if self.NameInput.text() == "":
            self.NameInput.textCursor().insertText(text)
            self.NameInput.selectAll()
        else:
            self.NameInput.textCursor().insertText("."+text)
            self.NameInput.find("."+text, QtGui.QTextDocument.FindBackward)
        self.NameInput.setFocus()
            
    def updateListUnitGeometry(self):
        items = [self.MemberList.item(i) for i in range(self.MemberList.count())]
        for i in items:
            self.MemberList.itemWidget(i).adjustSize()
            i.setSizeHint(self.MemberList.itemWidget(i).sizeHint())


class OverloadWidget(QtWidgets.QWidget): #CRITICAL: Add ability to overload and add functions
    method: types.MethodType
    target: types.MethodType
    targetObject: object
    Static: bool
    Static_ClassOverwrite: bool
    def __init__(self, parent = None, method = None, name = "", _class = None):
        # type: (QtWidgets.QWidget|None, types.MethodType|None, str, type|None) -> None
        """
        This widget allows the user to change methods while the program is running. \n
        If you supply a method the widget will only be able to change this one method. \n
        Otherwise the user can enter the methods and happily edit all the methods of the entire application. \n
        If you supply a method you can additionally supply a string that will be displayed as the title. If not the methods name will be displayed. \n
        You should only add this widget to your program if all your users can program. \n
        This widget is part of the exec_Window (thus you don't need to add this widget to your application just for debug purposes).
        """
        super(OverloadWidget, self).__init__(parent)
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        self._TempCode = ""
        self.lastHighlightColour = "Red"
        self.Static = not method is None
        self.Static_ClassOverwrite = not _class is None
        self.MethodGlobals = globals()
        self.Globals = globals()
        if self.Static:
            if name == "":
                try:
                    name = method.__name__
                except:
                    NC(2,"Could not load name",exc=sys.exc_info(),input=method)
            self.Label = QtWidgets.QLabel(name,self)
            self.layout().addWidget(self.Label,0,0)
            self.method = method
            self.target = method
            if _class is None:
                self.targetObject = self.target.__self__
            else:
                self.targetObject = _class
        else:
            self.NameInput = LineEdit(self)
            #TODO: Add tooltip that BRIEFLY explains how to input methods.
            # The tooltip should NOT mention that the code code is executed in this widget and not in the window.
            # However the HELP tab of the code execution window SHOULD mention this and SHOULD give a more complete explanation.
            self.layout().addWidget(self.NameInput,0,0)
            self.NameInput.returnPressed.connect(lambda: self.loadCode())
            self.method = None
            self.target = None
            self.targetObject = None
        self.loadButton = Button(self,"Load Code",lambda: self.loadCode())
        self.layout().addWidget(self.loadButton,0,1)
        self.applyButton = Button(self,"Apply Code")
        self.applyButton.setToolTip(self.applyCode.__doc__)
        self.applyButton.setToolTipDuration(0)
        self.layout().addWidget(self.applyButton,0,2)
        self.Console = CodeEditorWidget(self,additionalKeywords=["self","NC"],ExecuteButton=False)
        self.layout().addWidget(self.Console, 1, 0, 1, 3)
        self.applyButton.clicked.connect(lambda: self.Console.sendExecute())
        self.Console.S_Execute.connect(lambda: self.applyCode())
        if self.Static:
            self.loadCode()
        else:
            self.highlightInput("Red")
            self.NameInput.textChanged.connect(lambda: self.highlightInput("Yellow"))
            App().S_ColourChanged.connect(lambda: self.highlightInput(self.lastHighlightColour))

    def highlightInput(self,c="Red"):
        # type: (str) -> None
        """
        Changes the border of the input field to green when code is loaded successfully and changes it red whenever the text of input field changes. \n
        This makes it easy to see if it is save to apply the code. \n
        The code can be applied regardless of the colour to not hinder creativity.
        """
        self.lastHighlightColour = c
        if not self.Static:
            pal = QtGui.QPalette(self.palette())
            brush = App().PenColours[c]
            pal.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
            pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
            pal.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
            self.NameInput.setPalette(pal)

    def setGlobals(self, Globals = None):
        # type: (dict) -> None
        """
        Set the globals used in loadCode. If None the globals of this method are loaded.
        """
        # , self.Globals, {"self":self}
        if Globals == None:
            self.Globals = globals()
        else:
            self.Globals = Globals
        #TODO: Update autocomplete

    def loadCode(self):
        """
        Loads the code of the method that is named in the NameInput and displays it. \n
        Also loads the globals that are connected to this method. \n
        If this was successful the outline of the NameInput turns green.
        """
        try:
            if not self.Static:
                exec("_self_self.method = "+self.NameInput.text(), self.Globals, {"self":self.window(),"_self_self":self})
            try:
                if not self.Static_ClassOverwrite:
                    exec("_self_self._TempCode = \"\\n\"+_self_self.method.__self__._Code_Overwrite_"+self.method.__name__ , self.Globals, {"self":self.window(),"_self_self":self})
                else:
                    exec("_self_self._TempCode = \"\\n\"+_self_self.targetObject._Code_Overwrite_"+self.method.__name__ , self.Globals, {"self":self.window(),"_self_self":self})
                code = self._TempCode
            except:
                code = "\n"+inspect.getsource(self.method)
            for _ in range(0,5):
                # Filter out leading tabs and spaces.
                # Do several passes in case a class definition is indented but not infinite passes to avoid endless loops.
                # (I can conceive of many ways that could lead to one or both if cases evaluating to True while replace does not actually perform any changes.
                #   All of these are far too uncommon to warrent handling and most make the code invalid anyways.)
                # textwrap.dedent is not used because empty lines should not be normalized to just a newline character but instead be dedented like all other lines
                if "    def" in code and not True in [s.startswith("def") for s in code.splitlines()]:
                    code = code.replace("\n    ","\n")
                if "\tdef" in code and not True in [s.startswith("def") for s in code.splitlines()]: # Not using elif in case strings containing "def" with leading spaces/tabs are used
                    code = code.replace("\n\t","\n")
            self.Console.setText("# Use ctrl+return to confirm your code changes"+code)
            self.MethodGlobals = self.method.__globals__ #TODO: Load these globals and the class members to the auto complete of self.Console
            self.highlightInput("Green")
        except:
            method = str(self.method) if self.Static else self.NameInput.text()
            NC(1,"Could not load code",exc=sys.exc_info(),input=method)
            self.highlightInput("Red")

    def applyCode(self):
        """
        Overwrites the method currently named in the NameInput with the method currently entered in the Console using the globals that where loaded when loadCode was last called. \n
        Alternatively adds a new method to the object or class if the method does not currently exist.
        (Before adding a new method it is recommended to first load a method of that class to load the relevant globals. (Loading the __init__ is often the easiest way.))\n
        It is supported to add/modify methods to/of classes and objects.
        If adding a method to a class all (current and future) objects of that class (that do not have an attribute with the same name of the new method) gain this method.
        If modifying a method of a class the change is applied to all objects of the class IN WHICH THE METHOD IS DEFINED AND ALL DERIVED CLASSES! Thus be careful where a method was defined!\n
        Overwriting a method that is connected to signals does not change the method that is connected to the signals as they store a separate version of the method :(
        But connecting signals to lambda functions that call the method circumvents this problem. (This is the reason why most signals in AGeLib are connected via lambda functions.)
        """
        # Further reading: https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
        # Further reading: https://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object-instance
        code = "CODE NOT ASSEMBLED YET"
        ovw,new,cow,cnw = code,code,code,code
        try:
            if not self.Static:
                exec(f"try:\n\t_self_self.target = {self.NameInput.text()}\nexcept:\n\t_self_self.target = None\ntry:\n\t_self_self.targetObject = "+self.NameInput.text().rsplit(".",1)[0]+"\nexcept:\n\t_self_self.targetObject = None", self.Globals, {"self":self.window(),"_self_self":self})
            ovw,new,cow,cnw = self.assembleMethod()
            ovwExc,newExc,cowExc,cnwExc = None,None,None,None
            #MAYBE: try reloading the globals here? and load the globals of __init__ in case it is a new method?
            if not inspect.isclass(self.targetObject):
                try:
                    exec(ovw,self.MethodGlobals,{"self":self.window(),"_self_self":self,"types":types,"sys":sys})
                except:
                    ovwExc = sys.exc_info()
                    NC(4,"Could not overwrite method of method",exc=ovwExc,input=ovw)
                    try:
                        exec(new,self.MethodGlobals,{"self":self.window(),"_self_self":self,"types":types,"sys":sys})
                    except:
                        newExc = sys.exc_info()
                        NC(4,"Could not add new method to object",exc=newExc,input=new)
                        NC(1,"Could not overwrite or add method of/to object.\nPlease refer to the last 2 level 4 notifications for more information.")
            else:
                try:
                    exec(cow,self.MethodGlobals,{"self":self.window(),"_self_self":self,"types":types,"sys":sys})
                except:
                    cowExc = sys.exc_info()
                    NC(4,"Could not overwrite method of class",exc=cowExc,input=cow)
                    try:
                        exec(cnw,self.MethodGlobals,{"self":self.window(),"_self_self":self,"types":types,"sys":sys})
                    except:
                        cnwExc = sys.exc_info()
                        NC(4,"Could not add new method to class",exc=cnwExc,input=cnw)
                        NC(1,"Could not overwrite or add method of/to class.\nPlease refer to the last 2 level 4 notifications for more information.")
        except:
            NC(1,"Could not apply code",exc=sys.exc_info(),input=ovw)

    def assembleMethod(self):
        """
        This is a helper function for applyCode that puts together the code necessary for overwriting the method with (or adding) the new one.
        """
        methodName1 = self.Console.text().split("def ",1)[1].split("(",1)[0].strip()
        if not self.Static_ClassOverwrite:
            className1 = "vars(sys.modules[_self_self.target.__module__])[_self_self.target.__qualname__.rsplit(\".\",1)[0]]"
        else:
            className1 = "_self_self.targetObject"
        if not self.Static:
            methodName2 = self.NameInput.text().rsplit(".",1)[1]
            #className2  = self.NameInput.text().rsplit(".",1)[0]
            className2  = "_self_self.targetObject"
        else:
            methodName2 = self.target.__name__
            className2  = className1 # This would cause an error but this case should not be possible anyways... maybe investigate this case but it should be impossible that we use this.
        try:
            # OVerWrite
            ovw = self.Console.text()+f"\nfunctype=type(_self_self.target)\n_self_self.target.__self__.{self.target.__name__} = functype({methodName1}, _self_self.target.__self__)"
            ovw+= "\nsetattr(_self_self.target.__self__,\"_Code_Overwrite_\"+_self_self.target.__name__, \"\"\""+ ( self.Console.text().split("\n",1)[1] if self.Console.text().startswith("#") else self.Console.text() ).replace("\\","\\\\").replace("\n","\\n").replace("\"","\\\"").replace("\'","\\\'")+"\"\"\")"
        except:
            ovw = "raise Exception(\"The object does not have this method yet.\")" # This exception will lead to the new-case.
        # NEW
        new = self.Console.text()+f"\nfunctype=types.MethodType\n_self_self.targetObject.{methodName1} = functype({methodName1}, _self_self.targetObject)"
        new+= f"\nsetattr(_self_self.targetObject,\"_Code_Overwrite_{methodName1}\", \"\"\""+ ( self.Console.text().split("\n",1)[1] if self.Console.text().startswith("#") else self.Console.text() ).replace("\\","\\\\").replace("\n","\\n").replace("\"","\\\"").replace("\'","\\\'")+"\"\"\")"
        # Class OverWrite
        cow = self.Console.text()+f"\nqualname_temp = _self_self.target.__qualname__\n{className1}.{methodName2} = {methodName1}" # className1 will cause an exception if it does not have the method. This then leads to the cnw-case.
        cow+= f"\n{className1}.{methodName2}.__qualname__ = qualname_temp" # The __qualname__ of a function that is bound to a class does not include the class name because it is still a function. But since we need it to include the class name we ensure that it is added.
        cow+= f"\n{className1}._Code_Overwrite_{methodName2} = \"\"\""+ ( self.Console.text().split("\n",1)[1] if self.Console.text().startswith("#") else self.Console.text() ).replace("\\","\\\\").replace("\n","\\n").replace("\"","\\\"").replace("\'","\\\'")+"\"\"\""
        # Class NeW
        cnw = self.Console.text()+f"\n{className2}.{methodName2} = {methodName1}\n{className2}.{methodName2}.__self__ = {className2}\n{className2}.{methodName2}.__name__ = \"{methodName2}\"\n{className2}.{methodName2}.__qualname__ = {className2}.__name__+\".{methodName2}\""
        cnw+= f"\n{className2}._Code_Overwrite_{methodName2} = \"\"\""+ ( self.Console.text().split("\n",1)[1] if self.Console.text().startswith("#") else self.Console.text() ).replace("\\","\\\\").replace("\n","\\n").replace("\"","\\\"").replace("\'","\\\'")+"\"\"\""
        return ovw,new,cow,cnw

    def applyCode_old(self): #CLEANUP: Remove
        #Further reading: https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
        # Overwriting a method that is connected to signals does not change the method that is connected to the signals as they store a separate version of the method :(
        # But connecting signals to lambda functions that call the method works to circumvent this
        try:
            code = "Not Evaluated yet"
            if self.Static:
                code = self.assembleMethod_old(self.target)
            else:
                code = self.assembleMethod_old(self.NameInput.text())
            exec(code,self.MethodGlobals,{"self":self})
        except:
            NC(2,"Could not apply code",exc=sys.exc_info(),input=code)

    def assembleMethod_old(self,target): #CLEANUP: Remove
        r = self.Console.text()+"\nfunctype=type("+target+")\n"+target+" = functype("+self.Console.text().split("def ",1)[1].split("(",1)[0]+", "+target+".__self__)"
        r+= "\nsetattr("+target+".__self__,\"_Code_Overwrite_\"+"+target+".__name__, \"\"\""+ ( self.Console.text().split("\n",1)[1] if self.Console.text().startswith("#") else self.Console.text() ).replace("\\","\\\\").replace("\n","\\n").replace("\"","\\\"").replace("\'","\\\'")+"\"\"\")"
        return r

#endregion IDE Widgets
#region IDE Window
class exec_Window(AWWF):
    def __init__(self,parent = None):
        try:
            # Init
            super(exec_Window, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Code Execution Window")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
            
            self.Globals = globals()
            font = QtGui.QFont()
            font.setFamily("Consolas")
            
            self.TabWidget = MTabWidget(self)
            self.setCentralWidget(self.TabWidget)
            
            self.TabWidget.setCornerWidget(self.TopBar, QtCore.Qt.TopRightCorner)
            self.TopBar.setVisible(True)
            #self.TabWidget.tabBar().setUsesScrollButtons(True)
            self.TopBar.setMinimumHeight(self.MenuBar.minimumHeight())
            self.TopBar.CloseButton.setMinimumHeight(self.MenuBar.minimumHeight())
            self.MenuBar.setVisible(False)
            self.setMenuBar(None)
            
            self.GlobalsCheckBox = QtWidgets.QCheckBox(self.TopBar)
            self.GlobalsCheckBox.setText("globs")
            self.GlobalsCheckBox.setToolTip("Checked: Use the globals of the main file\nUnchecked: Use the globals of AGeIDE")
            self.GlobalsCheckBox.setChecked(False)
            self.GlobalsCheckBox.setObjectName("GlobalsCheckBox")
            self.TopBar.layout().addWidget(self.GlobalsCheckBox, 0, 50, 1, 1,QtCore.Qt.AlignRight)
            self.GlobalsCheckBox.clicked.connect(lambda: self.toggleGlobals())
            
            # Overload
            self.OverloadWidget = OverloadWidget(self)
            self.OverloadWidget.setObjectName("OverloadWidget")
            self.TabWidget.addTab(self.OverloadWidget,"Overload")
            self.OverloadWidget.Console.setFont(font)
            
            # Console #REM#
            self.ConsoleWidget = ConsoleWidget(self)
            self.TabWidget.addTab(self.ConsoleWidget,"Console")
            
            # Inspect #TODO
            self.InspectWidget = InspectWidget(self)
            self.InspectWidget.setObjectName("InspectWidget")
            self.TabWidget.addTab(self.InspectWidget,"Inspect")
            
            # Options #TODO: Improve and add more.
            #TODO: It would probably be best to fuse this with Help since there aren't to many options...
            #TODO: Turn this into its own widget class that is in _AGeIDE but NOT imported in AGeIDE
            self.OptionsWidget = QtWidgets.QWidget(self)
            self.OptionsWidget.setAutoFillBackground(True)
            self.OptionsWidget.setObjectName("OptionsWidget")
            self.OptionsLayout = QtWidgets.QGridLayout(self.OptionsWidget)
            self.OptionsLayout.setObjectName("OptionsLayout")
            self.TabWidget.addTab(self.OptionsWidget,"Options")
            
            self.fontComboBox = QtWidgets.QFontComboBox(self)
            self.fontComboBox.setCurrentFont(font)
            self.fontComboBox.currentFontChanged.connect(self.updateFonts)
            self.OptionsLayout.addWidget(self.fontComboBox,0,1)
            #self.TopBar.layout().addWidget(self.fontComboBox, 0, 99, 1, 1,QtCore.Qt.AlignRight)
            
            ## Help #TODO: It would probably be best to fuse this with Options since there aren't to many options...
            #self.HelpWidget = QtWidgets.QWidget(self)
            #self.HelpWidget.setAutoFillBackground(True)
            #self.HelpWidget.setObjectName("HelpWidget")
            #self.HelpLayout = QtWidgets.QGridLayout(self.HelpWidget)
            #self.HelpLayout.setObjectName("HelpLayout")
            #self.TabWidget.addTab(self.HelpWidget,"Help")
            
            # Other
            self.TabWidget.setCurrentWidget(self.ConsoleWidget)
            
            self.setAutoFillBackground(True)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.__init__")

    def setGlobals(self, Globals = None):
        """
        Set the globals used in execute_code and the widgets. If None the globals of this method are loaded.
        """
        # , self.Globals, {"self":self}
        if Globals == None:
            self.Globals = globals()
        else:
            self.Globals = Globals
        self.OverloadWidget.setGlobals(self.Globals)
        self.InspectWidget.setGlobals(self.Globals)
        self.ConsoleWidget.setGlobals(self.Globals)

    def toggleGlobals(self):
        if self.GlobalsCheckBox.checkState():
            self.setGlobals(vars(sys.modules['__main__']))
        else:
            self.setGlobals(None)

    def updateFonts(self, font):
        self.ConsoleWidget.Console.setFont(font)
        self.OverloadWidget.Console.setFont(font)

#endregion IDE Window

