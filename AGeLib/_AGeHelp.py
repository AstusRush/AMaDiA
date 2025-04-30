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
        self.currentItemChanged.connect(lambda item: self.HelpWindow.selectCategory(item, False))
        #self.itemDoubleClicked.connect(lambda item: self.HelpWindow.selectCategory(item, False))
        #self.itemActivated.connect(lambda item: self.HelpWindow.selectCategory(item, False)) # triggers with the enter key
        self.setHeaderHidden(True)
    
    def addHelpCategory(self, categoryName, content, overwrite=False, _topItem=None):
        # type: (str, typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget], typing.Dict[str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget],typing.Dict]]], bool, typing.Union[None,HelperTreeItem]) -> None
        subCategories = {}
        if isinstance(content, dict):
            subCategories = content
            content = subCategories["_TOP_"] if "_TOP_" in subCategories else ""
        item, is_present = self.getCategoryItem(categoryName, _topItem)
        if is_present:
            if overwrite:
                tex = f"removing\n{len(self.findCategoryItems(categoryName, _topItem)) = }"
                for i in self.findCategoryItems(categoryName, _topItem):
                    if i.parent(): i.parent().removeChild(i)
                    else: self.takeTopLevelItem(self.indexOfTopLevelItem(i))
                tex += f"\n{len(self.findCategoryItems(categoryName, _topItem)) = }"
                NC(3,tex)
            elif subCategories:
                for k,v in subCategories.items():
                    if k == "_TOP_": continue
                    self.addHelpCategory(k, v, overwrite=overwrite, _topItem=item)
                return
            else:
                return
        item = self._prepareItem(categoryName, content)
        if not _topItem: self.addTopLevelItem(item)
        else: _topItem.addChild(item)
        for k,v in subCategories.items():
            if k == "_TOP_": continue
            self.addHelpCategory(k, v, overwrite=overwrite, _topItem=item)
    
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
    
    def getCategoryItem(self, name, top=None):
        # type: (typing.Union[str,typing.List[str]], typing.Union[None,HelperTreeItem]) -> typing.Tuple[HelperTreeItem,bool]
        l = self.findCategoryItems(name, top=top)
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
    
    def findCategoryItems(self, name, top=None):
        # type: (typing.Union[str,typing.List[str]], typing.Union[None,HelperTreeItem]) -> typing.List[HelperTreeItem]
        #return self.findItems(name, QtCore.Qt.MatchFlag.MatchFixedString|QtCore.Qt.MatchFlag.MatchCaseSensitive|QtCore.Qt.MatchFlag.MatchExactly|QtCore.Qt.MatchFlag.MatchRecursive)
        if not isinstance(name, str) and len(name)==1: name = name[0]
        if isinstance(name, str):
            ret = []
            count = self.topLevelItemCount() if not top else top.childCount()
            for i in range(count):
                i = self.topLevelItem(i) if not top else top.child(i)
                if i.text(0) == name: ret.append(i)
            return ret
        else:
            ret = []
            count = self.topLevelItemCount() if not top else top.childCount()
            for i in range(count):
                i = self.topLevelItem(i) if not top else top.child(i)
                if i.text(0) == name[0]:
                    ret.extend(self.findCategoryItems(name[1:],i))
            return ret

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
            AGeLibHelpText = "This program is based upon the Astus General Library (AGeLib)." #TODO: More helptext to AGeLib
            help_text = "This is the help window.\nYou can open this window by pressing F1.\nSelect an item on the left to display the help page for it."
            if True: # Normal
                self.addHelpCategory("AGeLib",{"_TOP_":AGeLibHelpText,self.windowTitle():help_text})
            else: # Test
                self.addHelpCategory(self.windowTitle(),{"_TOP_":help_text,"Test":"Test Text Pre"})
                self.addHelpCategory(self.windowTitle(),{"_TOP_":help_text,"Test":"Test Text","Test Widget":lambda p: Button(p,"TEST")},overwrite=True)
                self.addHelpCategory("Test Category","Test Text")
                self.addHelpCategory("Test Category","Test Text2",overwrite=True)
                self.addHelpCategory("Test Category 2",{"_TOP_":"Test Text 2","Top Test":{"_TOP_":"Top Test","sub":"SubTestText"},"Other":"Other Text"})
                self.addHelpCategory("Test",{"_TOP_":"Test Text","Sub Hack":"This is cool"})
            self.installEventFilter(self)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="HelpWindow.__init__")
    
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == 6: # QtCore.QEvent.KeyPress
            if event.key() == QtCore.Qt.Key_F1:
                self.selectCategory(*self.HelpCategoryListWidget.getCategoryItem(["AGeLib",self.windowTitle()]))
                return True
        return super(HelpWindow, self).eventFilter(source, event) # let the normal eventFilter handle the event
    
    def showCategory(self, category = "", openWindow=True):
        #type: (typing.Union[str,typing.List[str]], bool) -> None
        if category=="": category = "No Category"
        if openWindow:
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
    
    def addHelpCategory(self, categoryName, content, overwrite=False):
        # type: (str, typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget], typing.Dict[str,typing.Union[str,typing.Callable[[QtWidgets.QWidget],QtWidgets.QWidget],typing.Dict]]], bool) -> None
        self.HelpCategoryListWidget.addHelpCategory(categoryName, content, overwrite=overwrite)
    
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

