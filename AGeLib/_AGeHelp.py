#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
from ._AGeWindows import *
#endregion Import

#region Help Widgets

class HelperTreeItem(QtWidgets.QTreeWidgetItem):
    def setExpanded(self, b = True):
        if self.parent():
            self.parent().setExpanded(b)
        super(HelperTreeItem, self).setExpanded(b)

class HelpTreeWidget(QtWidgets.QTreeWidget):
    """
    This widget is used by the HelpWindow to display an overview of all help pages.
    """
    def __init__(self, parent, helpWindow):
        super(HelpTreeWidget, self).__init__(parent)
        self.HelpWindow = helpWindow #type: HelpWindow
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.itemDoubleClicked.connect(lambda item: self.HelpWindow.selectCategory(item, False))
        self.itemActivated.connect(lambda item: self.HelpWindow.selectCategory(item, False)) # triggers with the enter key
        self.setHeaderHidden(True)
    
    def addHelpCategory(self, categoryName, content, subCategories=None, overwrite=False):
        # type: (str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]],typing.Dict[str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]]],bool) -> None
        if self.getCategoryItem(categoryName)[1]:
            if overwrite:
                for i in self.findCategoryItems(categoryName):
                    if i.parent(): i.parent().removeChild(i)
                    else: self.takeTopLevelItem(self.indexOfTopLevelItem(i))
            elif subCategories:
                self.addSubCategories(categoryName, subCategories, overwrite)
                return
            else:
                return
        item = self._prepareItem(categoryName, content)
        self.addTopLevelItem(item)
        if subCategories:
            self.addSubCategories(categoryName, subCategories, overwrite)
    
    def addSubCategories(self, categoryName, subCategories, overwrite=False):
        # type: (str,typing.Dict[str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]]],bool) -> None
        parent_item = self.getCategoryItem(categoryName)
        if not parent_item[1]:
            NC(1,f"Could not find \"{categoryName}\" and can therefore not add subcategories.",win=self.windowTitle(),func="HelpTreeWidget.addSubCategories")
            return
        for k,v in subCategories.items():
            if self.getCategoryItem(k)[1]:
                if overwrite:
                    for i in self.findCategoryItems(categoryName):
                        if i.parent(): i.parent().removeChild(i)
                        else: self.takeTopLevelItem(self.indexOfTopLevelItem(i))
                else:
                    continue
            item = self._prepareItem(k,v)
            parent_item[0].addChild(item)
    
    def _prepareItem(self, categoryName, content):
        # type: (str,str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]]) -> HelperTreeItem
        item = HelperTreeItem()
        item.setText(0,categoryName)
        if callable(content):
            item.setData(0,100, "widget")
            item.setData(0,101, content)
        elif isinstance(content, str):
            item.setData(0,100, "string")
            item.setData(0,101, content)
        else:
            errMsg = f"Could not register help category \"{categoryName}\" with content of type \"{type(content)}\""
            NC(2,errMsg,win=self.windowTitle(),func="HelpTreeWidget.addHelpCategory")
            item.setData(0,100, "string")
            item.setData(0,101, errMsg)
        return item
    
    def getCategoryItem(self, name):
        # type: (str) -> typing.Tuple[HelperTreeItem,bool]
        l = self.findCategoryItems(name)
        if l:
            if len(l) > 1:
                NC(2,f"Found multiple categories for the term \"{name}\". Returning only the first.",win=self.windowTitle(),func="HelpTreeWidget.getCategoryItem")
            return l[0], True
        else:
            item = HelperTreeItem()
            item.setText(0,"Category Not Found")
            item.setData(0,100, "string")
            item.setData(0,101, f"Could not find help category \"{name}\"")
            return item, False
    
    def findCategoryItems(self, name):
        # type: (str) -> typing.List[HelperTreeItem]
        return self.findItems(name, QtCore.Qt.MatchFlag.MatchFixedString|QtCore.Qt.MatchFlag.MatchCaseSensitive|QtCore.Qt.MatchFlag.MatchExactly|QtCore.Qt.MatchFlag.MatchRecursive)

class HelpTextDisplay(QtWidgets.QPlainTextEdit): pass

#endregion Help Widgets
#region Help Window
class HelpWindow(AWWF):
    def __init__(self,parent = None):
        try:
            # Init
            super(HelpWindow, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Help Window")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogHelpButton))
            
            self.Splitter = QtWidgets.QSplitter(self)
            self.HelpCategoryListWidget = HelpTreeWidget(self.Splitter, self)
            self.HelpDisplay = HelpTextDisplay(self.Splitter)
            self.setCentralWidget(self.Splitter)
            help_text = "This is the help window.\nYou can open this window by pressing F1.\nDouble-click an item on the left to display the help page for it."
            if True: # Normal
                self.addHelpCategory(self.windowTitle(),help_text)
            else: # Test
                self.addHelpCategory(self.windowTitle(),help_text,{"Test":"Test Text Pre"})
                self.addHelpCategory(self.windowTitle(),help_text,{"Test":"Test Text","Test Widget":lambda p: Button(p,"TEST")},overwrite=True)
                self.addHelpCategory("Test Category","Test Text")
                self.addHelpCategory("Test Category","Test Text2",overwrite=True)
            self.installEventFilter(self)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="HelpWindow.__init__")
    
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == 6: # QtCore.QEvent.KeyPress
            if event.key() == QtCore.Qt.Key_F1:
                self.selectCategory(*self.HelpCategoryListWidget.getCategoryItem(self.windowTitle()))
                return True
        return super(HelpWindow, self).eventFilter(source, event) # let the normal eventFilter handle the event
    
    def showCategory(self, category = ""):
        if category=="": category = "No Category"
        self.show()
        App().processEvents()
        self.positionReset()
        App().processEvents()
        self.activateWindow()
        self.selectCategory(*self.HelpCategoryListWidget.getCategoryItem(category))
    
    def selectCategory(self, item, select=True):
        # type: (HelperTreeItem,bool) -> None
        #IMPROVE: This currently flickers when item.data(0,100) is or was "widget"
        if not isinstance(self.HelpDisplay, HelpTextDisplay):
            self.clearWidgets()
        if item.data(0,100).lower() == "string":
            if not isinstance(self.HelpDisplay, HelpTextDisplay):
                self.HelpDisplay = HelpTextDisplay(self.Splitter)
            self.HelpDisplay.setPlainText(item.data(0,101))
            if select:
                self.HelpCategoryListWidget.collapseAll()
                self.HelpCategoryListWidget.setFocus()
                self.HelpCategoryListWidget.clearSelection()
                App().processEvents()
                item.setSelected(True)
                item.setExpanded(True)
                self.HelpCategoryListWidget.setCurrentItem(item)
        elif item.data(0,100).lower() == "widget":
            self.clearWidgets()
            self.HelpDisplay = item.data(0,101)(self.Splitter) #type: QtWidgets.QWidget
            if select:
                self.HelpCategoryListWidget.collapseAll()
                self.HelpCategoryListWidget.setFocus()
                self.HelpCategoryListWidget.clearSelection()
                App().processEvents()
                item.setSelected(True)
                item.setExpanded(True)
                self.HelpCategoryListWidget.setCurrentItem(item)
        else:
            if not isinstance(self.HelpDisplay, HelpTextDisplay):
                self.HelpDisplay = HelpTextDisplay(self.Splitter)
            self.HelpDisplay.setPlainText(f"ERROR\nData of type \"{item.data(100)}\" is not supported yet.")
    
    def addHelpCategory(self, categoryName, content, subCategories=None, overwrite=False):
        # type: (str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]],typing.Dict[str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget]]],bool) -> None
        self.HelpCategoryListWidget.addHelpCategory(categoryName, content, subCategories, overwrite)
    
    def clearWidgets(self):
        self.HelpDisplay = None
        for i in range(self.Splitter.count()):
            widget = self.Splitter.widget(i)
            if widget != self.HelpCategoryListWidget:
                #VALIDATE: This should not cause a memory leak but the hide() is required so the splitter behaves odd...
                #IMPROVE: There should be a cleaner way...
                widget.hide()
                widget.destroy()

#endregion Help Window

