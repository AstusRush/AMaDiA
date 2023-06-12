#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
#endregion Import



#region Text Widgets

class BaseTextEdit(QtWidgets.QTextEdit):
    """
    The base class for Texteditor of AGeLib. \n
    Includes the signals returnPressed, returnOnlyPressed, and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set BaseTextEdit`.setTabChangesFocus(False)`.
    """
    returnPressed = pyqtSignal()
    returnOnlyPressed = pyqtSignal()
    returnCtrlPressed = pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.installEventFilter(self)
        self.setTabChangesFocus(True)
    
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget|BaseTextEdit, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter: # Connects to returnPressed but does not accept the signal to allow linebreaks
                source.returnPressed.emit()
                if event.modifiers() == QtCore.Qt.ControlModifier:
                    source.returnCtrlPressed.emit()
                else:
                    source.returnOnlyPressed.emit()
            if event.key() == QtCore.Qt.Key_Up and source.textCursor().blockNumber() == 0: # Move to beginning if up key pressed and in first line
                cursor = source.textCursor()
                if event.modifiers() == QtCore.Qt.ShiftModifier: # If shift is pressed select the text
                    cursor.movePosition(cursor.Start,1)
                else:
                    cursor.movePosition(cursor.Start)
                source.setTextCursor(cursor)
                return True
            elif event.key() == QtCore.Qt.Key_Down and source.textCursor().blockNumber() == source.document().blockCount()-1: # Move to end if down key pressed and in last line
                cursor = source.textCursor()
                if event.modifiers() == QtCore.Qt.ShiftModifier: # If shift is pressed select the text
                    cursor.movePosition(cursor.End,1)
                else:
                    cursor.movePosition(cursor.End)
                source.setTextCursor(cursor)
                return True
        elif event.type() == QtCore.QEvent.FontChange:
            metrics = QtGui.QFontMetrics(self.font())
            try:
                self.setTabStopDistance(4 * metrics.averageCharWidth())
            except: # For old Qt Versions
                self.setTabStopWidth(4 * metrics.averageCharWidth())
        return super(BaseTextEdit, self).eventFilter(source, event)
    
    def text(self):
        return self.toPlainText()
    
    def setText(self, text: str) -> None:
        """
        Set text but do not clear the undo/redo history.
        For normal Qt behaviour use `setTextCH`
        """
        doc = self.document()
        curs = QtGui.QTextCursor(doc)
        curs.select(QtGui.QTextCursor.SelectionType.Document)
        curs.insertText(text)
    
    def setTextCH(self, text: str) -> None:
        """
        Set text and clear undo/redo history
        (This is the standard Qt implementation)
        """
        return super().setText(text)
    
    def insertFromMimeData(self, MIMEData):
        try:
            Text = MIMEData.text()
            self.textCursor().insertText(Text)
        except:
            pass

class TextEdit(BaseTextEdit):
    """
    The base multiline texteditor of AGeLib. \n
    Includes the signals returnPressed, returnOnlyPressed, and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set TextEdit`.setTabChangesFocus(False)`.
    """
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.installEventFilter(self)

        # FEATURE: Make subscript and superscript work and add an option to disable it (for small fonts)
        # See https://www.qtcentre.org/threads/38633-(SOLVED)-QTextEdit-subscripted-text for a startingpoint
        
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        #if event.type() == QtCore.QEvent.KeyPress:
        #    if (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter) and event.modifiers() == QtCore.Qt.ControlModifier:
        #        source.returnCtrlPressed.emit()
        #        return True
        return super(TextEdit, self).eventFilter(source, event)
    
class LineEdit(BaseTextEdit):
    """
    The base single line texteditor of AGeLib. \n
    In contrast to QLineEdit, AGeLib's LineEdit supports QtGui.QSyntaxHighlighter since it is derived from QtWidgets.QTextEdit . \n
    Includes the signals returnPressed, returnOnlyPressed, and returnCtrlPressed. \n
    Includes the common behaviour of the arrow key navigation. \n
    Tab is used to focus the next widget. If you want to use tab as a symbol set TextEdit`.setTabChangesFocus(False)`. \n
    Please note that multiline text is converted to a single line in which each former line is placed in brackets and separated by plus signs.
    To change this behaviour reimplement `.insertFromMimeData(self,Data)`.
    """
    def __init__(self, parent = None, PlaceholderText = None):
        super(LineEdit, self).__init__(parent)
        self.RowHeightFactor = 1 #1.4
        self.RowHeightSpacer = 10
        self.RowHeight = QtGui.QFontMetrics(self.font()).height()*self.RowHeightFactor + self.RowHeightSpacer
        #self.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.RowHeight)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        if PlaceholderText:
            self.setPlaceholderText(PlaceholderText)
        
        self.installEventFilter(self)
        # Connect Signals
        #self.textChanged.connect(self.validateCharacters) # Turned off to fix Undo/Redo # CLEANUP: validateCharacters

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
            source.RowHeight = QtGui.QFontMetrics(source.font()).height()*self.RowHeightFactor + self.RowHeightSpacer
            source.setFixedHeight(source.RowHeight)
        elif event.type() == QtCore.QEvent.KeyPress:
            if ( event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter ) and not event.modifiers() == QtCore.Qt.ControlModifier:
                source.returnPressed.emit()
                source.returnOnlyPressed.emit()
                return True
        return super(LineEdit, self).eventFilter(source, event)

    #def validateCharacters(self): # CLEANUP: validateCharacters
     #   forbiddenChars = ['\n']
     #   cursor = self.textCursor()
     #   curPos = cursor.position()
     #   Text = self.toPlainText()
     #   found = 0
     #   for e in forbiddenChars:
     #       found += Text.count(e)
     #       Text = Text.replace(e, '')
     #   
     #   self.blockSignals(True)
     #   self.setText(Text)
     #   self.blockSignals(False)
     #   try:
     #       cursor.setPosition(curPos-found)
     #       self.setTextCursor(cursor)
     #   except:
     #       ExceptionOutput(sys.exc_info())
     #   super(LineEdit, self).validateCharacters()

    # TODO: also overwrite insertPlainText and similar methods and set...text methods to ensure that this is one line
    def insertFromMimeData(self,Data):
        # type: (QtCore.QMimeData) -> None
        if Data.hasText():
            text = Data.text()
            #text = text.replace('\n', ' + ').replace('\r', '')
            lines = []
            for i in text.splitlines():
                if i.strip() != "":
                    lines.append(i)
            if len(lines) > 1:
                text = "( "+" ) + ( ".join(lines)+" )"
            else:
                text = "".join(lines)
            self.insertPlainText(text)
            #Data.setText(text)
        else:
            super(LineEdit, self).insertFromMimeData(Data)

#endregion Text Widgets
#region List Widgets

class ListWidget(QtWidgets.QListWidget):
    """
    The base class for list widgets of AGeLib. \n
    QtGui.QKeySequence.Copy has been reimplemented to allow copying of multiple items. (Text of items is separated by linebreaks.) \n
    The scrollmode is set to ScrollPerPixel and the selectionmode is set to ExtendedSelection.
    """
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.installEventFilter(self)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)>1:
                    string = ""
                    for i in SelectedItems:
                        string += i.text()
                        string += "\n"
                    QtWidgets.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(ListWidget, self).keyPressEvent(event)
        except:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(ListWidget).keyPressEvent",input=str(event))
            super(ListWidget, self).keyPressEvent(event)

#endregion List Widgets
#region Table Widgets

class TableWidget(QtWidgets.QTableWidget):
    """
    The base class for table widgets of AGeLib. \n
    The Navigation is changed exit the widget when tab is pressed on the last item
    and AGeLib's LineEdit is used for the cell editing (which enables the use of QtGui.QSyntaxHighlighter). \n
    Includes the signal S_Focus_Next which is emitted when tab is pressed while the last item is selected.
    This can be used to automatically redirect the focus to a specific widget which can not be reached via the use of Qt's tab stops. \n
    """
    S_Focus_Next = pyqtSignal()
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        #print(type(self.itemDelegate()))
        self.TheDelegate = TableWidget_Delegate(self)
        self.setItemDelegate(self.TheDelegate)
        self.installEventFilter(self)
        
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == QtCore.QEvent.KeyPress and source in self.window().findChildren(QtWidgets.QTableWidget) and source.isEnabled() and source.tabKeyNavigation():
            index = source.currentIndex()
            if event.key() == QtCore.Qt.Key_Backtab:
                if index.row() == index.column() == 0:
                    source.setCurrentCell(0,0)
                    source.clearSelection()
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(source, False)
                    return True
            elif event.key() == QtCore.Qt.Key_Tab:
                model = source.model()
                if (index.row() == model.rowCount() - 1 and index.column() == model.columnCount() - 1):
                    source.setCurrentCell(0,0)
                    source.clearSelection()
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(source, True)
                    self.S_Focus_Next.emit()
                    return True
            elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Space:
                self.edit(index)
                return True
        return super(TableWidget, self).eventFilter(source, event)

class TableWidget_Delegate(QtWidgets.QStyledItemDelegate):
    """
    TableWidget delegate for AGeLib's TableWidget. \n
    This delegate uses AGeLib's LineEdit to enable the use of QtGui.QSyntaxHighlighter. \n
    The usual navigation (key press enters edit, enter closes edit, tab focuses next item, etc) is supported.
    """
    def __init__(self, parent=None):
        super(TableWidget_Delegate, self).__init__(parent)
        self.installEventFilter(self)

    def createEditor(self, parent, options, index):
        return LineEdit(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data())
        editor.selectAll()

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Tab or event.key() == QtCore.Qt.Key_Backtab)):
            # Commit Editing, end Editing mode and re-send Tab/Backtab
            self.commitData.emit(source)
            self.closeEditor.emit(source, QtWidgets.QAbstractItemDelegate.NoHint)
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers())
            QtWidgets.QApplication.instance().sendEvent(self.parent(),event)
            return True
        elif (event.type() == QtCore.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)):
            # Commit Editing and end Editing mode
            self.commitData.emit(source)
            self.closeEditor.emit(source, QtWidgets.QAbstractItemDelegate.NoHint)
            #event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,event.key(),event.modifiers())
            #QtWidgets.QApplication.instance().sendEvent(self.parent(),event)
            return True
        return super(TableWidget_Delegate, self).eventFilter(source, event)

#endregion Table Widgets
#region Stacked Widgets

class StackedWidget(QtWidgets.QStackedWidget):
    # Inspired by https://stackoverflow.com/questions/41247109/pyqt-how-to-switch-widgets-in-qstackedwidget
    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)
        self.LButton = QtWidgets.QToolButton(self)
        self.LButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowLeft))
        self.LButton.setMaximumSize(24, 24)
        self.LButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.LButton.clicked.connect(lambda: self.l())
        
        self.RButton = QtWidgets.QToolButton(self)
        self.RButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight))
        self.RButton.setMaximumSize(24, 24)
        self.RButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.RButton.clicked.connect(lambda: self.r())
        
        self.currentChanged.connect(lambda: self.checkSwitchButtons())
        self.RButton.raise_()
        self.LButton.raise_()

    def checkSwitchButtons(self):
        self.RButton.setEnabled(self.currentIndex() < self.count() - 1)
        self.LButton.setEnabled(self.currentIndex() > 0)
        self.RButton.raise_()
        self.LButton.raise_()

    def addWidget(self, widget):
        index = super(StackedWidget, self).addWidget(widget)
        self.checkSwitchButtons()
        return index

    def removeWidget(self, widget):
        index = super(StackedWidget, self).removeWidget(widget)
        self.checkSwitchButtons()
        return index
    
    def l(self):
        if self.currentIndex() > 0:
            self.setCurrentIndex(self.currentIndex() - 1)
    def r(self):
        if self.currentIndex() < self.count() - 1:
            self.setCurrentIndex(self.currentIndex() + 1)

    def resizeEvent(self, event):
        super(StackedWidget, self).resizeEvent(event)
        self.RButton.move(self.rect().right() - self.RButton.width(), 0)
        self.LButton.move(self.RButton.x() - self.LButton.width(), 0)
        self.RButton.raise_()
        self.LButton.raise_()

#endregion Stacked Widgets
#region Button/Action Widgets

class Button(QtWidgets.QPushButton):
    """
    This allows the creation and connection of a button in a single line
    """
    def __init__(self, parent = None, Text = "", Action=None):
        super(Button, self).__init__(parent)
        self.setText(Text)
        if Action is not None:
            self.clicked.connect(Action)

class ToolButton(QtWidgets.QToolButton):
    """
    This tool button scales its size correctly depending on the dpi of the current screen. \n
    The standard behaviour of QToolButton is to scale according to the dpi of the main screen which looks horrible. \n
    ( The corrected scaling is only supported with versions of QT >= Qt 5.14 )
    """
    #CRITICAL: Add other set...Size methods and add detection of change of current screen and make the button autoscale when it detects this
    #CRITICAL: Use this ToolButton instead of the usual QToolButton in all places where it makes sense (thus everywhere the size is set but not where the layout handles the size)
    def __init__(self, parent = None):
        super(ToolButton, self).__init__(parent)
        self._last_setMinimumSize = (None,None)
        self._last_setIconSize = (None,None)
        self._connectScreenChangedSignal()
        
    def _connectScreenChangedSignal(self):
        try:
            self.window().windowHandle().screenChanged.connect(self.updateToDPI) # May not be a lambda function as those do not get disconnected after the object is deleted
            QtCore.QTimer.singleShot(100,self.updateToDPI())
        except:
            QtCore.QTimer.singleShot(5000,self._connectScreenChangedSignal)
    
    def scaleToDPI(self, f):
        """
        Scales f from the DPI of the primary screen to the DPI of the current screen. \n
        scaleToDPI is only supported with versions of QT >= Qt 5.14
        """
        if versionParser(QtCore.qVersion()) >= versionParser("5.14"):
            scale = self.window().screen().logicalDotsPerInchX()/App().primaryScreen().logicalDotsPerInchX()
            if type(f) in [list,tuple]:
                f = (scale*f[0], scale*f[1])
            else:
                f *= scale
        return f
    
    def updateToDPI(self):
        """
        Calls all set...Size methods with the previous values to adjust their DPI scaling.
        """
        if self._last_setMinimumSize != (None,None):
            self.setMinimumSize(*self._last_setMinimumSize)
        if self._last_setIconSize != (None,None):
            self.setIconSize(*self._last_setIconSize)
    
    def setMinimumSize(self, w,h = None):
        self._last_setMinimumSize = (w,h)
        if h is None:
            t = w
        else:
            t = (w,h)
        t = self.scaleToDPI(t)
        w,h = t
        super(ToolButton, self).setMinimumSize(int(w),int(h))
    
    def setIconSize(self, w,h = None):
        self._last_setIconSize = (w,h)
        if h is None:
            t = w
        else:
            t = (w,h)
        t = self.scaleToDPI(t)
        w,h = t
        super(ToolButton, self).setIconSize(QtCore.QSize(int(w),int(h)))

class MenuAction(QtWidgets.QAction):
    def __init__(self, parent=None, text=None, tooltip=None, action=None, add=False, icon=None):
        if text is not None:
            if icon is not None:
                super(MenuAction, self).__init__(icon,text,parent)
            else:
                super(MenuAction, self).__init__(text,parent)
        else:
            super(MenuAction, self).__init__(parent)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if action is not None:
            if type(action) != list:
                action = [action]
            for i in action:
                self.triggered.connect(i)
        if add:
            parent.addAction(self)
        self.hovered.connect(self.showToolTip)
    
    def showToolTip(self):
        #if self.toolTip() != "" and self.toolTip() is not None and self.toolTip() != self.text():
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),self.toolTip())#,self)

#endregion Button/Action Widgets
#region Text Addons
class TextAddon_Finder(QtWidgets.QWidget):
    """
    This widget provides search functionality for QTextEdit, QPlainTextEdit, and all derived classes.\n
    The search field appears when pressing ctrl+F.\n
    Usage:\n
    Create the text widget you want to have search functionality. Then create a TextAddon_Finder. \n
    The constructor must be given a parent widget (or `None`) and the text widget. \n
    When you want to move the text widget or add it to a layout perform these actions on the TextAddon_Finder instead as the text widget is now a part of it. \n
    (Meaning: the text widget is added to the layout of the TextAddon_Finder. This is necessary to handle events and the search field's position and visibility.) \n
    All other interactions can still be performed with the text widget as usual.
    """
    try:
        textWidget: typing.Union[QtWidgets.QTextEdit,QtWidgets.QPlainTextEdit]
    except:
        pass
    def __init__(self, parent, textWidget):
        super(TextAddon_Finder, self).__init__(parent)
        self.textWidget = textWidget
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.textWidget,0,0)
        #
        self.occurrencesTimeout = 1000 * 10
        #
        self.Floater = _TextAddon_Finder_Floater(self)
        self.Floater.setVisible(False)
        self.installEventFilter(self)
        self.textWidget.installEventFilter(self)
        
    def resizeEvent(self, event):
        super(TextAddon_Finder, self).resizeEvent(event)
        self.Floater.setMinimumWidth(self.Floater.cWidth())
        self.Floater.move(self.rect().right() - self.Floater.cWidth(), self.rect().bottom() - self.Floater.RowHeight)
        self.Floater.raise_()

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_F and event.modifiers() == QtCore.Qt.ControlModifier:
                self.Floater.setVisible(True)
                try:
                    selectedText = self.textWidget.textCursor().selectedText()
                    if selectedText != "" and not len(selectedText.splitlines()) > 1:
                        self.Floater.inputField.selectAll()
                        self.Floater.inputField.insertPlainText(selectedText.splitlines()[0])
                except:
                    pass
                self.Floater.inputField.setFocus()
                return True
        return super(TextAddon_Finder, self).eventFilter(source, event)

    def find(self, flag = 0):
        """
        Search for and select the text currently displayed in the inputField. \n
        Flags can be one of the four QtGui.QTextDocument.FindFlags .\n
        Also display the number of occurrences in the Statusbar of the window.
        """
        # If you want more control you can implement this yourself as shown here: https://github.com/goldsborough/Writer-Tutorial/blob/master/PyQt5/Part-4/ext/find.py
        if flag == 0:
            flag = QtGui.QTextDocument.FindFlags()
        query = self.Floater.inputField.text()
        if query == "":
            return
        try:
            try:
                text = self.textWidget.text()
            except:
                text = self.textWidget.toPlainText()
            occurrences = text.lower().count(query.lower())
            try:
                self.window().Statusbar.showMessage("Found {} occurrence".format(occurrences)+("s" if occurrences != 1 else ""),self.occurrencesTimeout)
            except:
                pass
        except:
            pass
        if not self.textWidget.find(query,flag): # if we don't find anything we start from the beginning (or the end)
            lastCursorPosition = self.textWidget.textCursor() # store the cursor position in case we find nothing
            if int(flag)%2: # if flag contains QtGui.QTextDocument.FindBackward:
                self.textWidget.moveCursor(QtGui.QTextCursor.End)
            else:
                self.textWidget.moveCursor(QtGui.QTextCursor.Start)
            if not self.textWidget.find(query,flag):
                self.textWidget.setTextCursor(lastCursorPosition) # if nothing was found we don't want to have moved the cursor

class _TextAddon_Finder_Floater(QtWidgets.QWidget):
    """
    NO INTERACTION RECOMMENDED\n
    This is the searchbar for the TextAddon_Finder and depends on many of its methods and attributes.\n
    As such this class should not be used by anything other than the TextAddon_Finder.
    """
    def __init__(self, parent):
        super(_TextAddon_Finder_Floater, self).__init__(parent)
        self.visibleCharacters = 12 # Not exact but close enough
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        #
        self.inputField = LineEdit(self)
        self.inputField.returnOnlyPressed.connect(lambda: self.parent().find())
        self.inputField.returnCtrlPressed.connect(lambda: self.parent().find(QtGui.QTextDocument.FindBackward))
        self.layout().addWidget(self.inputField,0,0)
        self.inputField.setFixedWidth(QtGui.QFontMetrics(self.font()).averageCharWidth()*self.visibleCharacters)
        self.RowHeight = QtGui.QFontMetrics(self.font()).height()*self.inputField.RowHeightFactor + self.inputField.RowHeightSpacer
        self.setFixedHeight(self.RowHeight)
        #
        self.upButton = QtWidgets.QToolButton(self)
        self.upButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))
        self.upButton.setFixedSize(self.RowHeight,self.RowHeight)
        self.upButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.upButton.setToolTip("Select previous occurrence\nShortcut: Hit ctrl+return in the search field.")
        self.upButton.clicked.connect(lambda: self.parent().find(QtGui.QTextDocument.FindBackward))
        self.layout().addWidget(self.upButton,0,1)
        #
        self.downButton = QtWidgets.QToolButton(self)
        self.downButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown))
        self.downButton.setFixedSize(self.RowHeight,self.RowHeight)
        self.downButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.downButton.setToolTip("Select next occurrence\nShortcut: Hit return in the search field.")
        self.downButton.clicked.connect(lambda: self.parent().find())
        self.layout().addWidget(self.downButton,0,2)
        #
        self.hideButton = QtWidgets.QToolButton(self)
        self.hideButton.setText("🗙")
        self.hideButton.setFixedSize(self.RowHeight,self.RowHeight)
        self.hideButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.hideButton.setToolTip("Close the search.\nShortcut: Hit ctrl+F in the search field.")
        self.hideButton.clicked.connect(lambda: self.hideSelf())
        self.layout().addWidget(self.hideButton,0,3)
        #
        #self.setWi
        self.installEventFilter(self)
        App().S_ColourChanged.connect(lambda: self.updateColour())
        self.updateColour()
        self.setFixedWidth(QtGui.QFontMetrics(self.font()).averageCharWidth()*self.visibleCharacters+self.hideButton.width() +self.upButton.width()+self.downButton.width() )

    def cWidth(self):
        return self.inputField.width()+self.hideButton.width() +self.upButton.width()+self.downButton.width()

    def hideSelf(self):
        self.setVisible(False)
        self.parent().textWidget.setFocus()
    
    def updateColour(self):
        pal = QtGui.QPalette(self.palette())
        brush = pal.brush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase)
        pal.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = pal.brush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase)
        pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = pal.brush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase)
        pal.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.inputField.setPalette(pal)

    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if (event.type() == QtCore.QEvent.FontChange): # Rescale if font size changes
            self.RowHeight = QtGui.QFontMetrics(self.font()).height()*self.inputField.RowHeightFactor + self.inputField.RowHeightSpacer
            self.setFixedHeight(self.RowHeight)
            self.upButton.setFixedSize(self.RowHeight,self.RowHeight)
            self.downButton.setFixedSize(self.RowHeight,self.RowHeight)
            self.hideButton.setFixedSize(self.RowHeight,self.RowHeight)
            self.inputField.setFixedWidth(QtGui.QFontMetrics(self.font()).averageCharWidth()*self.visibleCharacters)
            self.setFixedWidth(QtGui.QFontMetrics(self.font()).averageCharWidth()*self.visibleCharacters+self.hideButton.width() +self.upButton.width()+self.downButton.width() )
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_F and event.modifiers() == QtCore.Qt.ControlModifier:
                self.hideSelf()
                return True
        return super(_TextAddon_Finder_Floater, self).eventFilter(source, event)

#endregion find

#region layout
class TightGridWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget'] = None, makeCompact:bool=True) -> None:
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        self.layout().setContentsMargins(0,0,0,0)
        if makeCompact: self.makeCompact()
    
    def makeCompact(self):
        self.layout().setRowStretch(1000, 1)
    
    def addWidget(self, widget, *args, **kwargs):
        """
        Allows creating a widget and adding it to the grid layout in one line. \n
        (This is just a wrapper for `layout().addWidget` that returns the widget.) \n
        This can make it much more readable when adding several spin boxes or labels to a layout.
        """
        #NOTE: widget must be a QWidget or a subclass but type-hinting this actually stops the linter from working correctly
        #       as it then only sees a QWidget returned instead of what you actually gave it.
        self.layout().addWidget(widget, *args, **kwargs)
        return widget
        #if typing.TYPE_CHECKING:
        #    return widget
        #else:
        #    if isinstance(widget, QtWidgets.QWidget):
        #        return widget
        #    else:
        #        NC(1,f"{widget} is not a subclass of QtWidgets.QWidget!", input=args, func=f"{type(self)}.addWidget")
        #        return None

class TightGridFrame(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional['QtWidgets.QWidget'] = None, makeCompact:bool=True) -> None:
        super().__init__(parent=parent)
        self.setFrameStyle(self.Box | self.Sunken)
        self.setLayout(QtWidgets.QGridLayout(self))
        self.layout().setObjectName("gridLayout")
        #self.layout().setContentsMargins(0,0,0,0)
        if makeCompact: self.makeCompact()
    
    def makeCompact(self):
        self.layout().setRowStretch(1000, 1)
    
    def addWidget(self, widget, *args, **kwargs):
        """
        Allows creating a widget and adding it to the grid layout in one line. \n
        (This is just a wrapper for `layout().addWidget` that returns the widget.) \n
        This can make it much more readable when adding several spin boxes or labels to a layout.
        """
        #NOTE: widget must be a QWidget or a subclass but type-hinting this actually stops the linter from working correctly
        #       as it then only sees a QWidget returned instead of what you actually gave it.
        self.layout().addWidget(widget, *args, **kwargs)
        return widget
        #if typing.TYPE_CHECKING:
        #    return widget
        #else:
        #    if isinstance(widget, QtWidgets.QWidget):
        #        return widget
        #    else:
        #        NC(1,f"{widget} is not a subclass of QtWidgets.QWidget!", input=args, func=f"{type(self)}.addWidget")
        #        return None
#endregion layout
