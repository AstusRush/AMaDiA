#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAux import ColourDict
from . import AGeToPy
#endregion Import



#region Notification Widget
class NotificationsWidget(QtWidgets.QSplitter):
    """
    This widget displays all notifications and allows (read)access to their details. \n
    The 200 most recent notifications are automatically loaded and all new notifications are automatically added. \n
    To save computer resources and keep it navigable for the user the list is limited to 200 entries.
    """
    #TODO: Limit all texts to maybe 5000 characters. 24 million characters freezes the program
    #TODO: Make text inside a listWidgetItem somehow selectable while still allowing the easy selection of an entire item and selecting multiple items to copy all of their content
    #       (or at least add a "Copy Notification" button if the "selecting individual items" part does not work)
    #       And while you're at it: Support opening links by clicking on them (maybe needs the text to be displayed as markdown which requires linebreaks to be converted and the tooltip then also needs to support this format...
    #               Therefore the formating must happen in the NC Class... The tooltip should be able to support markdown... but the NC Class needs to figure out if it is Markdown...
    #               Maybe add a bool to the init with which the markdown conversion can be turned off.
    #               It must also be ensured that only the plain text is copied when pressing ctrl+c ...
    #       This might be more work than expected... but it would be worth it
    def __init__(self, parent=None):
        super(NotificationsWidget, self).__init__(parent)
        #sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(20)
        #sizePolicy.setHeightForWidth(self.Splitter.sizePolicy().hasHeightForWidth())
        #self.Splitter.setSizePolicy(sizePolicy)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.NotificationList = NotificationListWidget(self)
        self.NotificationInfo = NotificationInfoWidget(self)
        self.NotificationList.setObjectName("NotificationList")
        self.NotificationInfo.setObjectName("NotificationInfo")
        
        App().S_New_Notification.connect(self.AddNotification)
        for i in App().Notification_List:
            self.AddNotification(i)
        
        self.NotificationList.currentItemChanged.connect(self.NotificationInfo.ShowNotificationDetails)

    def AddNotification(self,Notification):
        # type: (NC) -> None
        try:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(Notification))
            item.setData(100,Notification)
            item.setIcon(Notification.icon)
            
            self.NotificationList.addItem(item)
            self.NotificationList.scrollToBottom()
        except:
            item = QtWidgets.QListWidgetItem()
            item.setText("Could not add notification")
            item.setData(100,NC(1,"Could not add notification",exc=sys.exc_info(),func=str(self.objectName())+".(NotificationsWidget).AddNotification",win=self.window().windowTitle(),send=False))
            
            self.NotificationList.addItem(item)
            self.NotificationList.scrollToBottom()
        try:
            # Limit the list to 200 entries to save computer resources and to keep the list navigable for the user.
            while self.NotificationList.count() > 200:
                self.NotificationList.takeItem(0)
        except:
            NC(2,"Could not remove oldest notification from the list",exc=sys.exc_info(),func=str(self.objectName())+".(NotificationsWidget).AddNotification",win=self.window().windowTitle())

class NotificationListWidget(ListWidget):
    """
    This widget is used by NotificationsWidget to display all notifications.
    """
    def __init__(self, parent=None):
        super(NotificationListWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)

class NotificationInfoWidget(ListWidget):
    #TODO: Add a button to copy the details of the current notification to the clipboard with a tooltip that explains how to send it to the developer
    #CRITICAL: Make links clickable
    """
    This widget is used by NotificationsWidget to display the details of the currently selected notification.
    """
    def __init__(self, parent=None):
        super(NotificationInfoWidget, self).__init__(parent)
        self.setAlternatingRowColors(True)
        self.installEventFilter(self)
        
        item = QtWidgets.QListWidgetItem()
        item.setText("For more information select a notification")
        self.addItem(item)

    def keyPressEvent(self,event):
        try:
            if event == QtGui.QKeySequence.Copy:
                SelectedItems = self.selectedItems()
                if len(SelectedItems)>1:
                    string = ""
                    for i in SelectedItems:
                        string += i.text()
                        string += "\n\n"
                    QtWidgets.QApplication.clipboard().setText(string)
                    event.accept()
                    return
            super(NotificationInfoWidget, self).keyPressEvent(event)
        except:
            NC(lvl=2,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).keyPressEvent",input=str(event))
            super(NotificationInfoWidget, self).keyPressEvent(event)

    def ShowNotificationDetails(self,Notification):
        try:
            Notification = Notification.data(100)
            self.clear()
            for k,v in Notification.items():
                try:
                    if v is not None:
                        item = QtWidgets.QListWidgetItem()
                        item.setText(k+str(v))
                        self.addItem(item)
                except:
                    NC(msg="Could not display{}".format(str(k)),exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails")
        except:
            NC(exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(NotificationInfoWidget).ShowNotificationDetails")

#endregion Notification Widget

#region Appearance
class ColourPicker_OLD(QtWidgets.QToolButton): #CLEANUP
    """
    This widget is used to display and modify a single colour. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    Type: int
    Element: int
    def __init__(self, Type, Element, parent=None):
        super(ColourPicker_OLD, self).__init__(parent)
        self.Type, self.Element = Type, Element
        self.setText("")
        self.LoadCurrentPalette()
        self.clicked.connect(self.PickColour)
        self.setAutoRaise(True)
        self.setAutoFillBackground(True)
        
    def LoadCurrentPalette(self): #TODO:OVERHAUL
        try:
            if self.Type == "Pen":
                self.Colour = App().PenColours[self.Element].color()
            elif self.Type == "Notification":
                self.Colour = App().NotificationColours[self.Element].color()
            elif self.Type == "Misc":
                self.Colour = App().MiscColours[self.Element].color()
            elif self.Type == "Lexer":
                self.Colour = App().PythonLexerColours[self.Element].color()
        except:
            self.Colour = QtGui.QColor(255, 0, 255)
        self.ColourSelf()
        
    def PickColour(self):
        Colour = QtWidgets.QColorDialog.getColor(self.Colour,None,"Choose the {} colour \"{}\"".format(self.Type,self.Element))
        if Colour.isValid(): # If the QColorDialog was aborted by the user the returned colour is invalid
            self.Colour = Colour
        self.ColourSelf()
        
    def ColourSelf(self):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(self.Colour)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        # Generate readable text colour
        textColour = QtGui.QColor("black") if (0.299 * self.Colour.red() + 0.587 * self.Colour.green() + 0.114 * self.Colour.blue())/255 > 0.5 else QtGui.QColor("white")
        brush = QtGui.QBrush(textColour)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.setPalette(palette)
        # Display the HexRgb code of the colour
        #self.setText("#"+str(hex(self.Colour.rgb()))[4:]) # Does the same as the next line
        try:
            self.setText(self.Colour.name(QtGui.QColor.HexRgb))
        except:
            try:
                self.setText(self.Colour.name(0)) # 0 = HexRgb
            except:
                self.setText(self.Colour.name(QtGui.QColor.NameFormat.HexRgb))

class PaletteColourPicker_OLD(ColourPicker_OLD): #CLEANUP
    """
    This widget is used to display and modify a single colour of a QPalette. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    Mode: int
    Element: int
    ModeText: str
    ElementText: str
    Colour: QtGui.QColor
    def __init__(self, Mode, Element, ModeText, ElementText, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.Mode, self.Element = Mode, Element
        self.ModeText, self.ElementText = ModeText, ElementText
        self.setText("")
        self.LoadCurrentPalette()
        self.clicked.connect(self.PickColour)
        if self.ElementText != "Button": #MAYBE: Link the Button colour buttons to the ButtonText colour buttons
            self.setAutoRaise(True)
            self.setAutoFillBackground(True)
    
    def LoadCurrentPalette(self): #TODO:OVERHAUL
        try:
            if self.ModeText.endswith("Version 1"):
                self.Colour = App().Palette1.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
            elif self.ModeText.endswith("Version 2"):
                self.Colour = App().Palette2.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
            elif self.ModeText.endswith("Version 3"):
                self.Colour = App().Palette3.brush(self.Mode, self.Element).color()#QtGui.QColor(255, 255, 255)
            else:
                self.Colour = QtGui.QColor(255, 0, 255)
        except:
            self.Colour = QtGui.QColor(255, 0, 255)
        self.ColourSelf()
    
    def PickColour(self):
        Colour = QtWidgets.QColorDialog.getColor(self.Colour,None,"Choose colour for {} when {}".format(self.ElementText,self.ModeText))
        if Colour.isValid(): # If the QColorDialog was aborted by the user the returned colour is invalid
            self.Colour = Colour
        self.ColourSelf()


class ColourPicker(QtWidgets.QToolButton): #TODO:OVERHAUL
    """
    This widget is used to display and modify a single colour. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    
    QBRUSH_STYLES = {
        "NoBrush" : QtCore.Qt.NoBrush,
        "SolidPattern" : QtCore.Qt.SolidPattern,
        "Dense1Pattern" : QtCore.Qt.Dense1Pattern,
        "Dense2Pattern" : QtCore.Qt.Dense2Pattern,
        "Dense3Pattern" : QtCore.Qt.Dense3Pattern,
        "Dense4Pattern" : QtCore.Qt.Dense4Pattern,
        "Dense5Pattern" : QtCore.Qt.Dense5Pattern,
        "Dense6Pattern" : QtCore.Qt.Dense6Pattern,
        "Dense7Pattern" : QtCore.Qt.Dense7Pattern,
        "HorPattern" : QtCore.Qt.HorPattern,
        "VerPattern" : QtCore.Qt.VerPattern,
        "CrossPattern" : QtCore.Qt.CrossPattern,
        "BDiagPattern" : QtCore.Qt.BDiagPattern,
        "FDiagPattern" : QtCore.Qt.FDiagPattern,
        "DiagCrossPattern" : QtCore.Qt.DiagCrossPattern,
        #"LinearGradientPattern" : QtCore.Qt.LinearGradientPattern, # Not supported yet
        #"ConicalGradientPattern" : QtCore.Qt.ConicalGradientPattern, # Not supported yet
        #"RadialGradientPattern" : QtCore.Qt.RadialGradientPattern, # Not supported yet
        #"TexturePattern" : QtCore.Qt.TexturePattern, # Can not be supported
    }
    try:
        Brush: QtGui.QBrush
        Colour: QtGui.QColor
        Type: str
        Element: str
    except:
        pass
    def __init__(self, Type, Element, Brush, parent=None):
        super(ColourPicker, self).__init__(parent)
        self.Brush = Brush
        self.Colour = self.Brush.color()
        self.Type, self.Element = Type, Element
        self.setText("")
        self.ColourSelf()
        self.clicked.connect(self.PickColour)
        self.setAutoRaise(True)
        self.setAutoFillBackground(True)
        
    def getDialogTitle(self):
        return "Choose the {} colour \"{}\"".format(self.Type,self.Element)
        
    def PickColour(self):
        #TODO: Make a custom widget for this
        # See https://stackoverflow.com/questions/888646/how-could-i-use-the-qcolordialog-inside-another-widget-not-as-a-separate-dialog
        # The custom widget should then have all the tools to create a full QBrush with a colour picker, a style selection, everything to create gradients, and a bigger preview
        # The custom widget still needs to be a dialog that gets created on demand, grabs control, lets the user pick stuff, returns a value, returns control, and (most importantly) gets destroyed.
        # It would be cool to have a dialogue for every Colour button so that one can edit multiple brushes at the same time but that would be ways too many windows that would run in the background!
        # Once this new dialog exists there needs to be a way to easily copy brushes. Maybe ctrl+click to copy and shift+click to paste (but make a checkbox for this (default off) so that one can not do that accidentally)
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            style = QtWidgets.QInputDialog.getItem(None, "Choose a style", "Style", self.QBRUSH_STYLES.keys(), list(self.QBRUSH_STYLES.values()).index(self.Brush.style()), False)
            if style[1] and style[0] in self.QBRUSH_STYLES:
                if style[0] in ["LinearGradientPattern","ConicalGradientPattern","RadialGradientPattern"]:
                    raise NotImplementedError("LinearGradientPattern, ConicalGradientPattern, and RadialGradientPattern are not supported yet") #TODO: Support Gradients
                self.Brush = QtGui.QBrush(self.Colour,self.QBRUSH_STYLES[style[0]])
        else:
            Colour = QtWidgets.QColorDialog.getColor(self.Colour,None,self.getDialogTitle())
            if Colour.isValid(): # If the QColorDialog was aborted by the user the returned colour is invalid
                self.Colour = Colour
                self.Brush = QtGui.QBrush(Colour,self.Brush.style())
        self.ColourSelf()
        
    def ColourSelf(self):
        palette = QtGui.QPalette()
        brush = self.Brush
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        # Generate readable text colour
        textColour = QtGui.QColor("black") if (0.299 * self.Colour.red() + 0.587 * self.Colour.green() + 0.114 * self.Colour.blue())/255 > 0.5 else QtGui.QColor("white")
        brush = QtGui.QBrush(textColour)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.setPalette(palette)
        # Display the HexRgb code of the colour
        #self.setText("#"+str(hex(self.Colour.rgb()))[4:]) # Does the same as the next line
        try:
            self.setText(self.Colour.name(QtGui.QColor.HexRgb))
        except:
            try:
                self.setText(self.Colour.name(0)) # 0 = HexRgb
            except:
                self.setText(self.Colour.name(QtGui.QColor.NameFormat.HexRgb))

class PaletteColourPicker(ColourPicker): #TODO:OVERHAUL
    """
    This widget is used to display and modify a single colour of a QPalette. \n
    Pressing on this widget opens the standard colour dialogue of the OS. \n
    The text displays the Hex RGB code and the text colour changes automatically to ensure readability. \n
    This widget is used by OptionsWidget_1_Appearance.
    """
    try:
        Mode: int
        Element: int
        ModeText: str
        ElementText: str
    except:
        pass
    def __init__(self, Mode, Element, ModeText, ElementText, Brush, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.Brush = Brush
        self.Colour = self.Brush.color()
        self.Mode, self.Element = Mode, Element
        self.ModeText, self.ElementText = ModeText, ElementText
        self.setText("")
        self.ColourSelf()
        self.clicked.connect(self.PickColour)
        if self.ElementText != "Button": #MAYBE: Link the Button colour buttons to the ButtonText colour buttons
            self.setAutoRaise(True)
            self.setAutoFillBackground(True)
    
    def getDialogTitle(self):
        return "Choose colour for {} when {}".format(self.ElementText,self.ModeText)

class _DictTabWidget(QtWidgets.QTabWidget): #TODO
    def __init__(self, parent=None, name="THEME"):
        super(_DictTabWidget, self).__init__(parent)
        self.name = name
    
    def getDict(self,name=""):
        if not name: name = self.name
        Dict = {}
        #TODO: Generate the dict by iterating over all the tabs and collecting all their dicts and QPalettes
        for tab in range(self.count()):
            Dict.update(self.widget(tab).getDict())
        return {name:Dict}
    
    def updateTheme(self, theme):
        # type: (typing.Dict[str,typing.Union[typing.Dict[str,QtGui.QBrush],QtGui.QPalette]]) -> None
        tabs = {}
        for tab in range(self.count()):
            tabs[self.tabText(tab)] = tab
        for k,v in theme.items():
            if isinstance(v,QtGui.QPalette) and k[0:-2].strip() in tabs and k[-1].isdigit() and (k[-2].isspace() or k[-2].isalpha()):
                self.widget(tabs[k[0:-2].strip()]).updateThemeNum(v, k)
            elif k in tabs:
                self.widget(tabs[k]).updateTheme(v)
            else:
                if isinstance(v,QtGui.QPalette):
                    if k[-1].isdigit() and (k[-2].isspace() or k[-2].isalpha()):
                        w = _PaletteWidget(self, k[0:-2].strip())
                        w.updateThemeNum(v,k)
                        tabs[k[0:-2].strip()] = self.addTab(w, k[0:-2].strip())
                    else:
                        w = _PaletteWidget(self, k)
                        w.updateTheme(v)
                        tabs[k] = self.addTab(w, k)
                elif isinstance(v,dict):
                    for ik,iv in v.items():
                        if isinstance(iv,QtGui.QBrush):
                            w = _BrushDictWidget(self, k)
                            w.updateTheme(v)
                            tabs[k] = self.addTab(w, k)
                        elif isinstance(iv,(dict,QtGui.QPalette)):
                            w = _DictTabWidget(self, k)
                            w.updateTheme(v)
                            tabs[k] = self.addTab(w, k)
                        else:
                            raise NotImplementedError("{} (key: {}) of {} (key: {}) is not a supported type for entries of tabs of _DictTabWidget".format(type(v),k,type(iv),ik))
                        break
                else:
                    raise NotImplementedError("{} (key: {}) is not a supported type for tabs of _DictTabWidget".format(type(v),k))

class _PaletteWidget(QtWidgets.QTableWidget): #TODO
    PaletteRoles = {
                    #CRITICAL: Reorder these so that The text colour always comes directly after the colour of the background on which it will be displayed
                    #           This is especially important as the current order creates this huge bright area at the bottom that is way to bright! Alternating dark and bright would be way less straining for the eye!
                    "Window"            : QtGui.QPalette.Window ,
                    "Base"              : QtGui.QPalette.Base ,
                    "AlternateBase"     : QtGui.QPalette.AlternateBase ,
                    "Light"             : QtGui.QPalette.Light ,
                    "Midlight"          : QtGui.QPalette.Midlight ,
                    "Mid"               : QtGui.QPalette.Mid ,
                    "Dark"              : QtGui.QPalette.Dark ,
                    "Shadow"            : QtGui.QPalette.Shadow ,
                    "NoRole"            : QtGui.QPalette.NoRole ,
                    "Button"            : QtGui.QPalette.Button ,
                    "ButtonText"        : QtGui.QPalette.ButtonText ,
                    "Highlight"         : QtGui.QPalette.Highlight ,
                    "HighlightedText"   : QtGui.QPalette.HighlightedText ,
                    "ToolTipBase"       : QtGui.QPalette.ToolTipBase ,
                    "ToolTipText"       : QtGui.QPalette.ToolTipText ,
                    "Link"              : QtGui.QPalette.Link ,
                    "LinkVisited"       : QtGui.QPalette.LinkVisited ,
                    "Text"              : QtGui.QPalette.Text ,
                    "BrightText"        : QtGui.QPalette.BrightText ,
                    "WindowText"        : QtGui.QPalette.WindowText ,
                    }
    if versionParser(QtCore.qVersion())>=versionParser("5.12"):
        PaletteRoles["PlaceholderText"] = QtGui.QPalette.PlaceholderText # requires Qt 5.12 (see https://doc.qt.io/qt-5/qpalette.html#placeholderText)
    PaletteGroups = {
                    "Active"   : QtGui.QPalette.Active ,
                    "Inactive" : QtGui.QPalette.Inactive ,
                    "Disabled" : QtGui.QPalette.Disabled ,
                    }
    
    def __init__(self, parent, name):
        super(_PaletteWidget, self).__init__(parent)
        self.name = name
        self.nameDict = {}
        self.setNum(1)
    
    def setNum(self,num):
        self.setRowCount(len(self.PaletteRoles))
        self.setColumnCount(len(self.PaletteGroups)*num)
        self.setVerticalHeaderLabels(self.PaletteRoles.keys())
        if num == 1:
            self.setHorizontalHeaderLabels(self.PaletteGroups.keys())
        else:
            labels = []
            for i in range(num):
                for s in self.PaletteGroups.keys():
                    labels.append(s+" "+str(i+1))
            self.setHorizontalHeaderLabels(labels)
        
    
    def getDict(self,name=""):
        if not self.nameDict:
            if not name: name = self.name
            Palette = QtGui.QPalette()
            #TODO: Generate the dict
            return {name:Palette}
        else: # In case there are several palettes return them as separate entries in this dict
            Dict = {}
            for k,v in self.nameDict.items():
                Dict[v] = self.getPalette(k)
            return Dict
            
    def getPalette(self,num=1):
        palette = QtGui.QPalette()
        y = 0
        for k, v in self.PaletteRoles.items():
            x = (num-1)*len(self.PaletteGroups)
            for ki, vi in self.PaletteGroups.items():
                w = self.cellWidget(y,x) #type: PaletteColourPicker
                palette.setBrush(w.Mode, w.Element, w.Brush)
                x+=1
            y+=1
        return palette
    
    def updateTheme(self, theme):
        # type: (QtGui.QPalette) -> None
        raise NotImplementedError("_PaletteWidget.updateTheme is currently not implemented") #TODO
        self.nameDict[int(name[-1])] = name
        y = 0
        for i, v in AGeColour.PaletteElements.items():
            VLabel.append(i)
            x = 0
            for ii, vi in AGeColour.PaletteStates.items():
                widget = PaletteColourPicker(vi,v,ii,i,self.PaletteTable)
                self.PaletteColours.append(widget)
                self.PaletteTable.setCellWidget(y,x,widget)
                x+=1
            y+=1
    
    def updateThemeNum(self, theme, name):
        # type: (QtGui.QPalette, str) -> None
        #length = len(self.nameDict)
        self.nameDict[int(name[-1])] = name
        #if length != len(self.nameDict):
        #    self.setNum(len(self.nameDict))
        self.setNum(max(self.nameDict.keys()))
        y = 0
        for k, v in self.PaletteRoles.items():
            x = (int(name[-1])-1)*len(self.PaletteGroups)
            for ki, vi in self.PaletteGroups.items():
                widget = PaletteColourPicker(vi,v,ki,k,theme.brush(vi,v),self)
                self.setCellWidget(y,x,widget)
                x+=1
            y+=1

class _BrushDictWidget(QtWidgets.QTableWidget): #TODO
    def __init__(self, parent, name):
        super(_BrushDictWidget, self).__init__(parent)
        self.name = name
        self.theme = {}
        
    def getDict(self,name=""):
        if not name: name = self.name
        Dict = {}
        for i in range(self.rowCount()):
            w = self.cellWidget(i,0) #type: ColourPicker
            Dict[w.Element] = w.Brush
        return {name:Dict}
    
    def updateTheme(self, theme):
        # type: (typing.Dict[str,QtGui.QBrush]) -> None
        self.theme.update(theme)
        self.setRowCount(len(self.theme))
        self.setColumnCount(1)
        y = 0
        labels = []
        for k,v in self.theme.items():
            widget = ColourPicker(self.name,k,v,self)
            self.setCellWidget(y,0,widget)
            labels.append(k)
            y+=1
        self.setVerticalHeaderLabels(labels)

class OptionsWidget_1_Appearance(QtWidgets.QWidget): #CRITICAL: Conform to naming convention: methods camelCase, members PascalCase
    """
    This widget allows the user to change the Font and the colourpalette of the application. \n
    It furthermore allows the user to create, save and load their own colour palette. \n
    If you create your own options menu it is STRONGLY advised to include this widget! \n
    The freedome this widget provides to the user is the foundation of AGeLib. \n
    The initial reason to create this library was because I couldn't stand most applications anymore because they wouldn't allow me to change their colour.
    """
    def __init__(self, parent=None): #TODO:OVERHAUL
        super(OptionsWidget_1_Appearance, self).__init__(parent)
        self.PaletteColours = []
        self.PenColours = []
        self.NotificationColours = []
        self.MiscColours = []
        self.LexerColours = []
        
        #IMPROVE: Draw more attention to the palette selector!!! Changing the colours currently looks far too intimidating!
        #           The users first look should be drawn to the palette selector BY ANY MEANS NECESSARY!!!
        #TODO: Add this link somewhere: https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum
        #TODO: Add Tooltips that contain the info from https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum and say which colours are used for BG and FG
        #TODO: Add a checkbox somewhere to help automate the creation of Inactive and Disabled (keep tooltip behaviour in mind!!)
        #TODO: There should be a button to reload the colour list
        #       (currently only applying the Theme for editing or saving a palette are the only ways. maybe that is enough but a tiny refresh button would be neat. though it should keep the active palette's name)
        #TODO: The LoadToEditorButton needs a checkbox (default on) that makes the user confirm the loading (via a dialog) every time to prohibit accidental discarding of a lot of work.
        #TODO: Improve the behaviour of the ColourList to always display the name of the currently active Theme (or "custom" (or something like that) if the theme was loaded from the editing thingy)
        #       TIP: LoadCurrentPalette is only called when the user presses the button therefore the check whether the checkbox is checked can simply be there without the need to worry about annoying the user with automatic loading
        #MAYBE: Add Mpl/Special Colour selection
        #MAYBE: Add a button to revert ?the last? change
        
        self.setLayout(QtWidgets.QGridLayout())
        self.FontLabel = QtWidgets.QLabel(self)
        self.FontLabel.setText("Choose a font:")
        self.FontLabel.setToolTip("The displayed fonts are the fonts that are installed on your copmuter")
        self.layout().addWidget(self.FontLabel,0,0)
        self.fontComboBox = QtWidgets.QFontComboBox(self)
        self.fontComboBox.currentFontChanged.connect(self.SetFontFamily)
        self.layout().addWidget(self.fontComboBox,0,1)
        self.ColourListLabel = QtWidgets.QLabel(self) #TODO: Rename to ThemeListLabel
        self.ColourListLabel.setText("Choose a colour theme:")
        self.layout().addWidget(self.ColourListLabel,1,0)
        self.ColourList = QtWidgets.QComboBox(self) #TODO: Rename to ThemeList
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.setCurrentText("Dark")
        if versionParser(QtCore.qVersion())>=versionParser("5.14"):
            self.ColourList.textActivated.connect(App().setTheme)
        else:
            self.ColourList.currentTextChanged.connect(App().setTheme)
        self.layout().addWidget(self.ColourList,1,1)
        self.ColourTableLabel = QtWidgets.QLabel(self)
        self.ColourTableLabel.setText("Or create you own:")
        self.layout().addWidget(self.ColourTableLabel,2,0)
        self.LoadToEditorButton = QtWidgets.QPushButton(self)
        self.LoadToEditorButton.setText("Load current theme to editor")
        self.LoadToEditorButton.clicked.connect(lambda: self.LoadCurrentPalette())
        self.layout().addWidget(self.LoadToEditorButton,2,1)
        self.ThemeWidget = _DictTabWidget(self)
        self.layout().addWidget(self.ThemeWidget,3,0,1,2)
        self.ApplyPaletteButton = QtWidgets.QPushButton(self)
        self.ApplyPaletteButton.setText("Apply Theme")
        self.ApplyPaletteButton.clicked.connect(lambda: self.MakeTheme())
        self.layout().addWidget(self.ApplyPaletteButton,4,0)
        self.SavePaletteButton = QtWidgets.QPushButton(self)
        self.SavePaletteButton.setText("Save Theme")
        self.SavePaletteButton.clicked.connect(lambda: self.SavePalette())
        self.layout().addWidget(self.SavePaletteButton,4,1)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(3)
        self.ThemeWidget.updateTheme(App().Theme)
      # OLD #CLEANUP
        ## Colour Tabs #TODO: The 3 misc tabs should be combined into one tab with 3 Tables
        #self.ColourTabs = QtWidgets.QTabWidget(self)
        #self.layout().addWidget(self.ColourTabs,3,0,1,2)
        #self.PaletteTable = QtWidgets.QTableWidget(len(AGeColour.PaletteElements),len(AGeColour.PaletteStates),self)
        #self.ColourTabs.addTab(self.PaletteTable,"Palettes")
        ##self.layout().addWidget(self.PaletteTable,3,0,1,2)
        #self.PenTable_Labels = ["Red","Green","Blue","Yellow","Cyan","Magenta","Orange","Light Blue","White","Black"]
        #self.PenTable = QtWidgets.QTableWidget(len(self.PenTable_Labels),1,self)
        #self.PenTable.setVerticalHeaderLabels(self.PenTable_Labels)
        #self.ColourTabs.addTab(self.PenTable,"Pen Colours")
        #self.NotificationTable_Labels = ["Error","Warning","Notification","Message"]
        #self.NotificationTable = QtWidgets.QTableWidget(len(self.NotificationTable_Labels),1,self)
        #self.NotificationTable.setVerticalHeaderLabels(self.NotificationTable_Labels)
        #self.ColourTabs.addTab(self.NotificationTable,"Notification Colours")
        #self.MiscTable_Labels = ["Friendly","Hostile","Neutral","Ally","Self",
        #                        "Common","Uncommon","Rare","Legendary","Mythical","Artefact","Broken","Magical","Important",
        #                        "Gradient1","Gradient2","Gradient3"]
        #self.MiscTable = QtWidgets.QTableWidget(len(self.MiscTable_Labels),1,self)
        #self.MiscTable.setVerticalHeaderLabels(self.MiscTable_Labels)
        #self.ColourTabs.addTab(self.MiscTable,"Misc Colours")
        #self.LexerTable_Labels = ["Default","Comment","Number","DoubleQuotedString","SingleQuotedString","Keyword","TripleSingleQuotedString","TripleDoubleQuotedString",
        #                        "ClassName","FunctionMethodName","Operator","Identifier","CommentBlock","UnclosedString","HighlightedIdentifier","Decorator"]
        #self.LexerTable = QtWidgets.QTableWidget(len(self.LexerTable_Labels),1,self)
        #self.LexerTable.setVerticalHeaderLabels(self.LexerTable_Labels)
        #self.ColourTabs.addTab(self.LexerTable,"Lexer Colours")
        ##
        #self.ApplyPaletteButton = QtWidgets.QPushButton(self)
        #self.ApplyPaletteButton.setText("Apply Palette")
        #self.ApplyPaletteButton.clicked.connect(lambda: self.MakeTheme())
        #self.layout().addWidget(self.ApplyPaletteButton,4,0)
        #self.SavePaletteButton = QtWidgets.QPushButton(self)
        #self.SavePaletteButton.setText("Save Palette")
        #self.SavePaletteButton.clicked.connect(lambda: self.SavePalette())
        #self.layout().addWidget(self.SavePaletteButton,4,1)
        #self.layout().setContentsMargins(0,0,0,0)
        #self.layout().setSpacing(3)
        #HLabel = ["Active Version 1","Inactive Version 1","Disabled Version 1","Active Version 2","Inactive Version 2","Disabled Version 2","Active Version 3","Inactive Version 3","Disabled Version 3"]
        #VLabel = []
        #y = 0
        #for i, v in AGeColour.PaletteElements.items():
        #    VLabel.append(i)
        #    #CLEANUP
        #    #widget = PaletteColourPicker(AGeColour.PaletteStates["Active"],v,"Active",i,self.PaletteTable)
        #    #self.PaletteColours.append(widget)
        #    #self.PaletteTable.setCellWidget(y,0,widget)
        #    #widget = PaletteColourPicker(AGeColour.PaletteStates["Inactive"],v,"Inactive",i,self.PaletteTable)
        #    #self.PaletteColours.append(widget)
        #    #self.PaletteTable.setCellWidget(y,1,widget)
        #    #widget = PaletteColourPicker(AGeColour.PaletteStates["Disabled"],v,"Disabled",i,self.PaletteTable)
        #    #self.PaletteColours.append(widget)
        #    #self.PaletteTable.setCellWidget(y,2,widget)
        #    x = 0
        #    for ii, vi in AGeColour.PaletteStates.items():
        #        widget = PaletteColourPicker(vi,v,ii,i,self.PaletteTable)
        #        self.PaletteColours.append(widget)
        #        self.PaletteTable.setCellWidget(y,x,widget)
        #        x+=1
        #    y+=1
        #self.PaletteTable.setHorizontalHeaderLabels(HLabel)
        #self.PaletteTable.setVerticalHeaderLabels(VLabel)
        #y = 0
        #for i in self.PenTable_Labels:
        #    widget = ColourPicker("Pen",i,self.PenTable)
        #    self.PenColours.append(widget)
        #    self.PenTable.setCellWidget(y,0,widget)
        #    y+=1
        #y = 0
        #for i in self.NotificationTable_Labels:
        #    widget = ColourPicker("Notification",i,self.NotificationTable)
        #    self.NotificationColours.append(widget)
        #    self.NotificationTable.setCellWidget(y,0,widget)
        #    y+=1
        #y = 0
        #for i in self.MiscTable_Labels:
        #    widget = ColourPicker("Misc",i,self.MiscTable)
        #    self.MiscColours.append(widget)
        #    self.MiscTable.setCellWidget(y,0,widget)
        #    y+=1
        #y = 0
        #for i in self.LexerTable_Labels:
        #    widget = ColourPicker("Lexer",i,self.LexerTable)
        #    self.LexerColours.append(widget)
        #    self.LexerTable.setCellWidget(y,0,widget)
        #    y+=1
        
    def SetFontFamily(self,Family):
        App().setFont(Family,self.window().TopBar.Font_Size_spinBox.value(),self)
        
    def LoadCurrentPalette(self):
        """
        Loads the currently active Theme into the Editor. \n
        If the checkbox is checked the user must first confirm this action to avoid accidental loss of data. \n #TODO
        This method should not be called programmatically. It should only be called when the user clicks the LoadToEditorButton. \n
        In general the editor should never be changed by the program except if the user requests it!
        """
        self.ThemeWidget.updateTheme(App().Theme)
        #CLEANUP
        #for i in self.PaletteColours+self.PenColours+self.NotificationColours+self.MiscColours+self.LexerColours:
        #    i.LoadCurrentPalette()
        #self.PenColours = []
        #self.NotificationColours = []
        #self.MiscColours = []
        #self.LexerColours = []
    
    def LoadPaletteList(self):
        App().refreshThemeList()
        return list(App().Themes.keys())
        #CLEANUP
        ColourList = []
        try:
            try:
                importlib.reload(AGeColour)
            except:
                NC(2,"Could not reload AGeColour",exc=sys.exc_info(),func="MainApp.recolour")
            try:
                if QtWidgets.QApplication.instance().AGeLibPathOK:
                    spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(QtWidgets.QApplication.instance().AGeLibSettingsPath,"CustomColourPalettes.py"))
                    CustomColours = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(CustomColours)
                    #CustomColours.MyClass()
                else:
                    raise Exception("AGeLibPath is not OK")
            except:
                NC(4,"Could not load custom colours",exc=sys.exc_info(),func="MainApp.recolour")
            try:
                for i in AGeColour.Colours.keys():
                    ColourList.append(i)
                for i in CustomColours.Colours.keys():
                    ColourList.append(i)
            except:
                pass
        except:
            NC(1,"Exception while loading colour palette",exc=sys.exc_info(),func="MainApp.recolour")
        return ColourList
    
    def refreshThemeList(self):
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
    
    def MakeTheme(self):
        #TODO: Should this reload be here? If so: Shouldn't the list display "custom" or something like that?
        #       And if not there must be a special button for reloading the list (though there should be a button for this anyways...)
        self.ColourList.blockSignals(True)
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.blockSignals(False)
        #
        theme = self.ThemeWidget.getDict("Custom")
        theme = list(theme.values())[0]
        App()._setTheme(theme,"Custom")
        return theme
        #CLEANUP
        self.ColourList.blockSignals(True)
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.blockSignals(False)
        palette1,palette2,palette3 = QtGui.QPalette(),QtGui.QPalette(),QtGui.QPalette()
        PenColours , NotificationColours , MiscColours , LexerColours = {},{},{},{}
        for i in self.PaletteColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            if int(i.ModeText[-1]) == 1:
                palette1.setBrush(i.Mode, i.Element, brush)
            elif int(i.ModeText[-1]) == 2:
                palette2.setBrush(i.Mode, i.Element, brush)
            elif int(i.ModeText[-1]) == 3:
                palette3.setBrush(i.Mode, i.Element, brush)
        for i in self.PenColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            PenColours[i.Element] = brush
        for i in self.NotificationColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            NotificationColours[i.Element] = brush
        for i in self.MiscColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            MiscColours[i.Element] = brush
        for i in self.LexerColours:
            brush = QtGui.QBrush(i.Colour)
            brush.setStyle(QtCore.Qt.SolidPattern)
            LexerColours[i.Element] = brush
            #
        App()._recolour(palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours , LexerColours)
        return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours , LexerColours
    
    def PaletteToPython(self,Palette,FunctionName,Name): #TODO:OVERHAUL
        return
        #window.AMaDiA_About_Window_Window.TextBrowser.setText(app.optionWindow.ColourPicker.PaletteToPython(AGeColour.Colours[app.optionWindow.ColourPicker.LoadPaletteList()[0]],app.optionWindow.ColourPicker.LoadPaletteList()[0])[0])
        try:
            Palette1, Palette2, Palette3, _PenColours, _NotificationColours, _MiscColours, _LexerColours = Palette()
            if _LexerColours is None or len(_LexerColours)<5: raise Exception("_LexerColours is either None or has less than 5 Elements")
        except:
            Palette1, Palette2, Palette3, _PenColours, _NotificationColours, _MiscColours = Palette()
            _LexerColours =  {
                        "Default"                  : Palette1.brush(QtGui.QPalette.Active,QtGui.QPalette.Text) ,
                        "Comment"                  : _PenColours["Green"] ,
                        "Number"                   : _PenColours["Light Blue"] ,
                        "DoubleQuotedString"       : _PenColours["Orange"] ,
                        "SingleQuotedString"       : _PenColours["Orange"] ,
                        "Keyword"                  : _PenColours["Blue"] ,
                        "TripleSingleQuotedString" : _PenColours["Orange"] ,
                        "TripleDoubleQuotedString" : _PenColours["Orange"] ,
                        "ClassName"                : _PenColours["Red"] ,
                        "FunctionMethodName"       : _PenColours["Red"] ,
                        "Operator"                 : _PenColours["Yellow"] ,
                        "Identifier"               : Palette1.brush(QtGui.QPalette.Active,QtGui.QPalette.Text) ,
                        "CommentBlock"             : _PenColours["Green"] ,
                        "UnclosedString"           : _PenColours["Magenta"] ,
                        "HighlightedIdentifier"    : _PenColours["White"] ,
                        "Decorator"                : _PenColours["Green"]
                        }
            NC(3,"Could not Load _LexerColours. Setting defaults.",exc=sys.exc_info())
        PenColours, NotificationColours, MiscColours, LexerColours = ColourDict(),ColourDict(),ColourDict(),ColourDict()
        PenColours.copyFromDict(_PenColours)
        NotificationColours.copyFromDict(_NotificationColours)
        MiscColours.copyFromDict(_MiscColours)
        LexerColours.copyFromDict(_LexerColours)
        Text = "\ndef "+FunctionName+"():\n    palette1 = QtGui.QPalette()\n    palette2 = QtGui.QPalette()\n    palette3 = QtGui.QPalette()"
        for i, v in AGeColour.PaletteElements.items():
            for ii,iv in AGeColour.PaletteStates.items():
                if int(ii[-1]) == 1:
                    Colour = Palette1.brush(iv, v).color()
                elif int(ii[-1]) == 2:
                    Colour = Palette2.brush(iv, v).color()
                elif int(ii[-1]) == 3:
                    Colour = Palette3.brush(iv, v).color()
                Text += "\n    brush = QtGui.QBrush(QtGui.QColor({},{},{}))".format(str(Colour.red()),str(Colour.green()),str(Colour.blue()))
                Text += "\n    brush.setStyle(QtCore.Qt.SolidPattern)"
                Text += "\n    palette{}.setBrush(QtGui.QPalette.{}, QtGui.QPalette.{}, brush)".format(ii[-1],ii.split()[0],i)
        Text += "\n    PenColours = {"
        for i in self.PenTable_Labels:
            Colour = PenColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    NotificationColours = {"
        for i in self.NotificationTable_Labels:
            Colour = NotificationColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    MiscColours = {"
        for i in self.MiscTable_Labels:
            Colour = MiscColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    LexerColours = {"
        for i in self.LexerTable_Labels:
            Colour = LexerColours[i].color()
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i,str(Colour.red()),str(Colour.green()),str(Colour.blue()))
        Text = Text[:-1]+"}\n    return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours , LexerColours\n"
        return Text,FunctionName,Name
    
    def SavePalette(self,Name=None): #TODO:OVERHAUL
        if Name is None:
            Name = QtWidgets.QInputDialog.getText(self,"Palette Name","What should the palette be called?")[0].strip()
            # VALIDATE: Ensure that the names can not break the dictionary
            if Name is None or Name == "":
                NC(2,"SavePalette has been cancelled")
                return ""
        Text = AGeToPy.formatObject(self.ThemeWidget.getDict(Name))
        try:
            if not App().AGeLibPathOK: raise Exception("AGeLibPath is not OK")
            ##
            TheDict = {}
            nText = Text
            try:
                spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(App().AGeLibSettingsPath,"CustomColourPalettes.py"))
                CustomColours = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(CustomColours)
                if CustomColours.Colours:
                    for k,v in CustomColours.Colours.items():
                        if not isinstance(v,dict): # Compatibility with AGeLib v1 and v2
                            if len(v()) == 6:
                                Palette1, Palette2, Palette3, PenColours, NotificationColours, MiscColours = v()
                                PythonLexerColours = False
                            else:
                                Palette1, Palette2, Palette3, PenColours, NotificationColours, MiscColours, PythonLexerColours = v()
                            CustomColours.Colours[k] = {}
                            CustomColours.Colours[k]["Palette 1"] = Palette1
                            CustomColours.Colours[k]["Palette 2"] = Palette2
                            CustomColours.Colours[k]["Palette 3"] = Palette3
                            CustomColours.Colours[k]["Pen Colours"] = PenColours
                            CustomColours.Colours[k]["Notification Colours"] = NotificationColours
                            CustomColours.Colours[k]["Misc Colours"] = MiscColours
                            if PythonLexerColours:
                                CustomColours.Colours[k]["Python Lexer Colours"] = PythonLexerColours
                if Name in CustomColours.Colours:
                    msgBox = QtWidgets.QMessageBox(self)
                    msgBox.setText("\"{}\" already exists".format(Name))
                    msgBox.setInformativeText("Do you want to overwrite \"{}\"?".format(Name))
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                    msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                    ret = msgBox.exec()
                    if ret != QtWidgets.QMessageBox.Save:
                        return Text
                CustomColours.Colours.update(self.ThemeWidget.getDict(Name))
                nText = AGeToPy.formatObject(CustomColours.Colours, "Colours")
            except:
                NC(2,"Could not load custom colours",exc=sys.exc_info(),func="MainApp.recolour")
                msgBox = QtWidgets.QMessageBox(self)
                msgBox.setText("Could not load previous custom colours!")
                msgBox.setInformativeText("Do you want to save the colour anyways?\nWARNING: This will overwrite any previous colour palettes!!!")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                ret = msgBox.exec()
                if ret != QtWidgets.QMessageBox.Save:
                    return Text
            Text = nText
            FileName = os.path.join(App().AGeLibSettingsPath,"CustomColourPalettes.py")
            with open(FileName,'w',encoding="utf-8") as text_file:
                text_file.write(Text)
            self.ColourList.blockSignals(True)
            self.ColourList.clear()
            self.ColourList.addItems(self.LoadPaletteList())
            #TODO: The newly created Theme should be set as the active here
            self.ColourList.blockSignals(False)
        except:
            NC(1,"Could not save",exc=sys.exc_info())
        return Text
        # window.AMaDiA_About_Window_Window.TextBrowser.setText(app.optionWindow.ColourPicker.SavePalette("Test"))
        if Name is None:
            Name = QtWidgets.QInputDialog.getText(self,"Palette Name","What should the palette be called?")[0].strip()
            # VALIDATE: Ensure that the names can not break the dictionary
            if Name is None or Name == "":
                NC(2,"SavePalette has been cancelled")
                return ""
        #Text = "from PyQt5 import QtCore, QtGui\n\ndef NewColour():\n    palette1 = QtGui.QPalette()\n    palette2 = QtGui.QPalette()\n    palette3 = QtGui.QPalette()"
        Text = ("""try:\n"""+ #CRITICAL: Update PyQt6 import with compatibility stuff
                """    if QtVersion == "PySide6":\n"""+
                """        from PySide6 import QtWidgets,QtCore,QtGui\n"""+
                """    elif QtVersion == "PySide2":\n"""+
                """        from PySide2 import QtWidgets,QtCore,QtGui\n"""+
                """    elif QtVersion == "PyQt6":\n"""+
                """        from PyQt6 import QtWidgets,QtCore,QtGui\n"""+
                """    else: # QtVersion == "PyQt5":\n"""+
                """        from PyQt5 import QtWidgets,QtCore,QtGui\n"""+
                """except:\n"""+
                """    from PyQt5 import QtWidgets,QtCore,QtGui\n""")
        Text += "\n\ndef NewColour():\n    palette1 = QtGui.QPalette()\n    palette2 = QtGui.QPalette()\n    palette3 = QtGui.QPalette()"
        for i in self.PaletteColours:
            Text += "\n    brush = QtGui.QBrush(QtGui.QColor({},{},{}))".format(str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
            Text += "\n    brush.setStyle(QtCore.Qt.SolidPattern)"
            Text += "\n    palette{}.setBrush(QtGui.QPalette.{}, QtGui.QPalette.{}, brush)".format(i.ModeText.split()[2],i.ModeText.split()[0],i.ElementText)
        Text += "\n    PenColours = {"
        for i in self.PenColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        Text = Text[:-1]+"}\n    NotificationColours = {"
        for i in self.NotificationColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        Text = Text[:-1]+"}\n    MiscColours = {"
        for i in self.MiscColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        Text = Text[:-1]+"}\n    LexerColours = {"
        for i in self.LexerColours:
            Text += "\n        \"{}\":QtGui.QBrush(QtGui.QColor({},{},{})),".format(i.Element,str(i.Colour.red()),str(i.Colour.green()),str(i.Colour.blue()))
        #
        Text = Text[:-1]+"}\n    return palette1 , palette2 , palette3 , PenColours , NotificationColours , MiscColours , LexerColours\n"
        try:
            if not App().AGeLibPathOK: raise Exception("AGeLibPath is not OK")
            ##
            TheDict = {}
            try:
                nText = Text
                spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(App().AGeLibSettingsPath,"CustomColourPalettes.py"))
                CustomColours = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(CustomColours)
                i=1
                for k,v in CustomColours.Colours.items():
                    fn = "c"+str(i)
                    t,fn,n = self.PaletteToPython(v,fn,k)
                    if n == Name:
                        msgBox = QtWidgets.QMessageBox(self)
                        msgBox.setText("\"{}\" already exists".format(Name))
                        msgBox.setInformativeText("Do you want to overwrite \"{}\"?".format(Name))
                        msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                        ret = msgBox.exec()
                        if ret != QtWidgets.QMessageBox.Save:
                            return Text
                        else:
                            continue
                    nText += "\n"
                    nText += t
                    TheDict[n.replace("\\","\\\\").replace("\"","\\\"")] = fn
                    i+=1
            except:
                NC(2,"Could not load custom colours",exc=sys.exc_info(),func="MainApp.recolour")
                msgBox = QtWidgets.QMessageBox(self)
                msgBox.setText("Could not load previous custom colours!")
                msgBox.setInformativeText("Do you want to save the colour anyways?\nWARNING: This will overwrite any previous colour palettes!!!")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                ret = msgBox.exec()
                if ret != QtWidgets.QMessageBox.Save:
                    return Text
            Text = nText
            ##
            fText = Text+"\nColours = {\""+Name.replace("\\","\\\\").replace("\"","\\\"")+"\":NewColour"
            for k,v in TheDict.items():
                fText += ",\"{}\":{}".format(k,v)
            fText += "}"
            FileName = os.path.join(App().AGeLibSettingsPath,"CustomColourPalettes.py")
            with open(FileName,'w',encoding="utf-8") as text_file:
                text_file.write(fText)
        except:
            NC(1,"Could not save",exc=sys.exc_info())
        self.ColourList.blockSignals(True)
        self.ColourList.clear()
        self.ColourList.addItems(self.LoadPaletteList())
        self.ColourList.blockSignals(False)
        return Text


#
# CRITICAL: COLOUR OVERHAUL
# OVERHAUL:
# The function only returns a dict which has as values dicts or QPalette's
# This way reading is very easy, expanding is very easy, expanding for other developers for custom purposes is very easy
# This widget then reads the current colour dictionary and dynamically creates tabs and adjusts existing tabs to accommodate all colours. This way no data is lost
# The save system then does the same: read all entries from the dict and save them. there are only 3 Data Types: dict, QBrush and QPalette. The main dict only contains QPalettes or dicts with QBrush.
# There should however be a button to discard all non standard entries.
# And there should be a standard colour if an access is invalid which also notifies the user which entries must be created
#
# Furthermore no old tabs or fields should be removed when loading a different palette that does not have these tabs or fields so that the user can add them to old palettes.
# These fields should keep the colour from the previous scheme but they should be highlighted so that the user knows which fields may need adjustment
#
# New widgets for dict, brush dict, and QPalette that all work independently so that there can be several layers od dicts.
# Each widgets generates the code for itself and integrates the code for its children so that it works dynamically.
#
# AGeApp extracts some colours but mostly just saves the entire dict. All colour access then goes through that dict.
# This way it is all easily extensible.
# The dict must be its own class to be able to supply default values with special getter methods that imply what return type was expected so that a valid default type can be returned.
#
#

#class OptionsWidget_1_Appearance(QtWidgets.QWidget):
#    """
#    This widget allows the user to change the Font and the colourpalette of the application. \n
#    It furthermore allows the user to create, save and load their own colour palette. \n
#    If you create your own options menu it is STRONGLY advised to include this widget! \n
#    The freedome this widget provides to the user is the foundation of AGeLib. \n
#    The initial reason to create this library was because I couldn't stand most applications anymore because they wouldn't allow me to change their colour.
#    """
#    def __init__(self, parent=None):
#        super(OptionsWidget_1_Appearance, self).__init__(parent)


#endregion Appearance


