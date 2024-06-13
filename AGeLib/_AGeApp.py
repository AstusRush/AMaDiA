#region General Import
from ._import_temp import *

import matplotlib # required to get the version

#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeAux import ColourDict
from ._AGeWidgets import *
from ._AGeAWWF import *
from ._AGeWindows import *
from . import _AGeWindows
from ._AGeSpecialWidgets import *
from ._AGeGW import *
from ._AGeIDE import *
from ._AGeHelp import *
from . import _AGeIDE
#endregion Import





#region Application
# ---------------------------------- Main Application ----------------------------------
AltModifier = QtCore.Qt.AltModifier
ControlModifier = QtCore.Qt.ControlModifier
GroupSwitchModifier = QtCore.Qt.GroupSwitchModifier
ShiftModifier = QtCore.Qt.ShiftModifier
MetaModifier = QtCore.Qt.MetaModifier

class AGeApp(QtWidgets.QApplication):
    """
    This class is the core of AGeLib.   \n
    Methods beginning with `r_` are virtual templates that can be reimplemented.   \n
    TODO: MORE INFO
    """
    #MAYBE: Make standard hotkeys optional (in case a dev wants to use these hotkeys) but write a warning that changing these is not recommended as it might confuse users that are used to the standard AGeLib Hotkeys
 #
    # See:
    # https://doc.qt.io/qt-5/qapplication.html
    # https://doc.qt.io/qt-5/qguiapplication.html
    # https://doc.qt.io/qt-5/qcoreapplication.html
    S_New_Notification = pyqtSignal(NC)
    S_FontChanged = pyqtSignal()
    S_ColourChanged = pyqtSignal()
    S_advanced_mode_changed = pyqtSignal(bool)
    
    
    try:
        MainWindow: AWWF
        MW: AWWF
        Notification_Window: _AGeWindows.Notification_Window
        exec_Window: _AGeIDE.exec_Window
        optionWindow: Options_Window
        
        advanced_mode: bool
        Notification_List: list
        uniqueNotificationList: list
        ModuleVersions: str
        
        Theme: typing.Dict[str,typing.Union[typing.Dict[str,QtGui.QBrush],QtGui.QPalette]]
        ThemeName: str
        Themes: typing.Dict[str,typing.Dict[str,typing.Union[typing.Dict[str,QtGui.QBrush],QtGui.QPalette]]]
        
        Palette1: QtGui.QPalette
        Palette2: QtGui.QPalette
        Palette3: QtGui.QPalette
        
        AppSpecificThemes: typing.Dict[str,function]
        PenColours: typing.Dict[str,QtGui.QBrush]
        NotificationColours: typing.Dict[str,QtGui.QBrush]
        MiscColours: typing.Dict[str,QtGui.QBrush]
        PythonLexerColours: typing.Dict[str,QtGui.QBrush]
        
        BG_Colour: QtGui.QColor
        TextColour: QtGui.QColor
    except:
        pass
        
    def __init__(self, args = None, useExcepthook = True):
        if args is None:
            args = []
        print("Starting App")
        self.enableHotkeys = True
        super(AGeApp, self).__init__(args)
        self.setStyle("fusion")
        self.setAttribute(QtCore.Qt.AA_DontUseNativeMenuBar) #Fixes to bar widget on MacOS/OSX/darwin/Apples OS
        try:
            msg = "Welcome " + getpass.getuser()
        except:
            msg = "Welcome"
        self.LastNotificationText = msg
        self.LastNotificationToolTip = msg
        self.LastNotificationIcon = QtGui.QIcon()
        
        self._LastCopiedBrush = QtGui.QBrush(QtGui.QColor(0))
        
        self.MainWindow = None
        self.MW = None
        self.Notification_Window = None
        self.exec_Window = None
        self.optionWindow = None
        self.HelpWindow = None
        self.Theme = {}
        self.ThemeName = ""
        self.Themes = {}
        self.AppSpecificThemes = {}
        
        self.installEventFilter(self)
        self.aboutToQuit.connect(lambda: self._saveClipboard())
        
        self.advanced_mode = False
        
        self.setOrganizationName("Robin Albers")
        self.setOrganizationDomain("https://github.com/AstusRush")
        
        self.Notification_List = []
        self.uniqueNotificationList = []
        self._init_NCF()
        self._makeAGeLibPath()
        ###########################
        #TODO: Load Settings like standard palette and font
        #self.Palette , self.BG_Colour , self.TextColour = AGeColour.Dark()
        #self.colour_Pack = (self.Palette , self.BG_Colour , self.TextColour)
        self._init_colourAndFont()
        self._generateModuleVersions()
        
        self.HelpWindow = HelpWindow()
        
        self.r_init_Options()
        if useExcepthook:
            sys.excepthook = trap_exc_during_debug
    
    def setMainWindow(self, TheWindow):
        # type: (AWWF) -> None
        """
        This method allows you to declare the primary window of your application.   \n
        You can use `self.MainWindow` (or `self.MW`) to access it.   \n
        Setting a main window is not obligatory and does nothing on its own.   \n
        The intention behind declaring a main window is to make the code more readable
        and to provide a convenient way to refer to it.   \n
        This can also be useful if a function needs to access the main window in an application where the main window changes.
        """
        self.MainWindow = TheWindow
        self.MW = TheWindow
    
    #def notify(self, obj, event): # Reimplementation of notify that does nothing other than redirecting to normal implementation for now...
        #try:
        #    return super().notify(obj, event)
        #except:
        #    ExceptionOutput(sys.exc_info())
        #    print("Caught: ",obj,event)
        #    return False
        
    def _generateModuleVersions(self):
        AppName, ModuleDict = self.r_generateModuleVersions()
        
        self.ModuleVersions = AppName
        self.ModuleVersions += "\nPython %d.%d\nAGeLib %s" % (sys.version_info.major, sys.version_info.minor, version)
        
        if numpyImported:
            self.ModuleVersions += "\nNumpy %s" % numpy_version
        else:
            self.ModuleVersions += "\nNumpy COULD NOT BE IMPORTED"
        if matplotlibImported:
            self.ModuleVersions += "\nMatplotLib %s" % matplotlib.__version__
        else:
            self.ModuleVersions += "\nMatplotLib COULD NOT BE IMPORTED"
        
        if QtVersion == "PyQt5": # type: ignore
            self.ModuleVersions += "\nPyQt %s (Qt %s)" % (QtCore.PYQT_VERSION_STR, QtCore.qVersion())
        elif QtVersion == "PyQt6": # type: ignore
            self.ModuleVersions += "\nPyQt %s (Qt %s)" % (QtCore.PYQT_VERSION_STR, QtCore.qVersion())
        elif QtVersion == "PySide6": # type: ignore
            self.ModuleVersions += "\nPySide6 Qt %s" % (QtCore.qVersion())
        elif QtVersion == "PySide2": # type: ignore
            self.ModuleVersions += "\nPySide2 Qt %s" % (QtCore.qVersion())
            
        try:
            for k,v in ModuleDict.items():
                self.ModuleVersions += "\n{} {}".format(k,v)
        except:
            print("Could not add the custom module versions to the list:")
            ExceptionOutput(sys.exc_info())
        
        #try:
        #    self.ModuleVersions = "Python %s\nAGeLib %s\nNumpy %s\nMatplotLib %s\nPyQt %s (Qt %s)" % ("%d.%d" % (sys.version_info.major, sys.version_info.minor),
        #            version,
        #            numpy_version,
        #            matplotlib.__version__,
        #            QtCore.PYQT_VERSION_STR, QtCore.qVersion())
        #except:
        #    self.ModuleVersions = "Python %s\nAGeLib %s\nNumpy %s\nMatplotLib %s\nPySide Qt %s" % ("%d.%d" % (sys.version_info.major, sys.version_info.minor),
        #            version,
        #            numpy_version,
        #            matplotlib.__version__,
        #            QtCore.qVersion())
    
    def r_generateModuleVersions(self):
        # type: () -> tuple[str,typing.Dict[str,str]]
        """
        Reimplement this method to add to the module version string. \n
        It must return a string that contains the App name and version (like "MyApp 1.5.3")
        and a dictionary that has the names of the modules you use (as strings) as keys and the version of the module (as strings) as Values. \n
        (The module Version must of course be read directly from the used module at users PC and can not be hardcoded as this would defeat the purpose.) \n
        The main purpose of the module version string is to allow users to file detailed bug reports as the module version string is part of every notification. \n
        The versions of Python, AGeLib, Numpy, MatplotLib, and Qt are listed automatically and must not be added. \n
        (This method is automatically called by `_generateModuleVersions` which is called by the `__init__`.)
        """
        return "",{}
    
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == 6 and self.enableHotkeys: # QtCore.QEvent.KeyPress
            #FEATURE: self.setWindowOpacity(0.5) (with self being a QMainWindow) Is really cool and could be quite useful...
            #       Does it make sense to add a global hotkey to open a dialogue to set the opacity of the current widget (with a confirmation for setting the value below 0.25 (initially selected option should be Abort to avoid accidents))
            if event.modifiers() == ControlModifier:
                if event.key() == QtCore.Qt.Key_T:
                    self.showWindow_IDE()
                    return True
            if event.modifiers() == AltModifier:
                if event.key() == QtCore.Qt.Key_A:
                    self.toggleAdvancedMode(not self.advanced_mode)
                    return True
                elif event.key() == QtCore.Qt.Key_O:
                    self.showWindow_Options()
                    return True
            if True: #Any Modifier
                if event.key() == QtCore.Qt.Key_F9: # FEATURE: HelpWindow: Inform the User that this feature exists. Make Help window that is opened with F1
                    for w in self.topLevelWidgets():
                        if w.isVisible():
                            try:
                                w.positionReset()
                            except:
                                pass
                    return True
                if event.key() == QtCore.Qt.Key_F12:
                    try:
                        _ , _ = source.window().winId(), source.window().screen() # Check if this exists #MAYBE: Use hasattr? Would probably be more readable... And then use if/else instead of try/except
                        self.makeScreenshot(source.window())
                    except:
                        self.makeScreenshot(source)
                    return True
        elif event.type() == NotificationEvent.EVENT_ID:
            self._notifyUser(event.N)
            return True
        return super(AGeApp, self).eventFilter(source, event)
    
    def makeScreenshot(self,window):
        # type: (QtWidgets.QWidget) -> None
        if self.AGeLibPathOK:
            name = self.applicationName()
            nameValid = ""
            ValidChars = string.ascii_letters + string.digits + "~ -_."
            for i in name:
                if i in ValidChars:
                    nameValid += i
            nameValid = nameValid.replace(" ","_")
            Filename = nameValid + "-" + cTimeFullStr("-") + ".png"
            Filename = os.path.join(self.ScreenshotFolderPath,Filename)
            try:
                WID = window.winId()
                screen = window.screen()
                screen.grabWindow(WID).save(Filename)
                print(Filename)
            except:
                NC(msg="Could not save Screenshot",exc=sys.exc_info(),func="AGeApp.eventFilter",input=Filename)
            else:
                NC(3,"Screenshot of currently active window saved as:\n"+Filename,func="AGeApp.eventFilter",input=Filename)
        else:
            print("Could not save Screenshot: Could not validate save location")
            NC(1,"Could not save Screenshot: Could not validate save location",func="AGeApp.eventFilter",input=self.AGeLibPath)
    
    def _saveClipboard(self):
        """
        On MS Windows this method ensures that the clipboard is kept:\n
        The contents of the clipboard are only stored as references.
        When you copy text from an application it can be pasted in all other applications
        but as soon as you close the application the reference is no longer valid and the clipboard is empty.  \n
        Note: This is not a problem if the user has a clipboard manager as they don't use references but instead copy the data.  \n
        On MS Windows this method writes the text into the clipboard.
        On other platforms it gives the clipboard manager an additional chance to copy the data.  \n
        This method is called automatically when the application exits and does not need to be called manually
        except if you expect your program to crash regularly and want to ensure that the clipboard is not lost
        on systems that have no active clipboard manager.
        """
        clipboard = QtWidgets.QApplication.clipboard()
        if platform.system() == 'Windows':
            try:
                import win32clipboard
                text = clipboard.text()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()
            except:
                print("Could not save clipboard data:")
                ExceptionOutput(sys.exc_info())
        else: #FEATURE: Find a linux version of win32clipboard
            print("Clipboard is only saved if a clipboard manager is installed due to OS limitations.")
            event = QtCore.QEvent(QtCore.QEvent.Clipboard)
            QtWidgets.QApplication.sendEvent(clipboard, event)
            self.processEvents()
    
    def toggleAdvancedMode(self, checked):
        # type: (bool) -> None
        """
        This function changes the state of the advanced mode to `checked`.   \n
        `S_advanced_mode_changed` is emitted and the checkbox `AdvancedCB` of all `TopBar_Widget`'s is updated. \n
        Do not change `advanced_mode` manually!!! Always use this function!
        """
        try:
            self.advanced_mode = checked
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeAdvancedCB:
                        i.AdvancedCB.setChecked(self.advanced_mode)
            self.S_advanced_mode_changed.emit(self.advanced_mode)
        except:
            NC(1,"Exception while toggling advanced mode",exc=sys.exc_info(),func="AGeApp.toggleAdvancedMode",input="{}: {}".format(str(type(checked)),str(checked)))
    
 # ---------------------------------- Colour and Font ----------------------------------
    # CRITICAL: Make a bool with which to force a font and palette change not only on the application level but on every single widget of every window
    def setTheme(self, Name = "Dark"):
        # type: (str) -> None
        """
        #TODO: This information is slightly outdated and needs to be updated
        Applies a colour scheme:   \n
        This method takes the name (string) of a colour scheme. \n
        First AGeColour (standard AGeLib colours) and CustomColourPalettes (user created colours) are (re-)imported and their dictionaries are loaded. \n
        Then the AGeColour dict is searched for the name. If it is not found the dict of CustomColourPalettes is searched. AppSpecificThemes is searched last.  \n
        As soon as the name is found the colourpalette is applied (by calling _setTheme). \n
        Please note: \n
        If you have code that needs to run after the palette has changed (like applying colours to specific widgets) reimplement `r_setTheme`. \n
        `r_setTheme` is called by `_setTheme` after the new palette has been applied. \n
        Furthermore the signal `S_ColourChanged` is emitted after `_setTheme`. \n
        To add custom colour palettes for your application use the method `addTheme`. \n \n
        COLOURS
        ===========
        + `Palette1`, `Palette2` and `Palette3` and full QPalettes that can be used to colour different ports of the UI. Use `r_setTheme` to apply these Palettes to widgets.
        `Palette` is deprecated and only accessible for compatibility reasons! It will be removed in future versions!
        + `BG_Colour` and `TextColour` can be used to colour different parts that are incompatible with QPalettes.
        These are tuples with 3 floats between 0 and 1 that specify RGB values and are taken from the Base and Text colours from Palette1.
        + `PenColours` is a dict containing QBrushes. Use `.color()` to access the QColor.
        The colours in this dict are visually distinct from the background (and don't necessarily correspond to their name).
        These colours should be used for graphs (and are automatically set as the MatPlotLib colour cycle), pen colours for editors,
        player colours for games and all other cases where visually distinct colours are needed.
        + `NotificationColours` is a dict that contains the colours for the notification flashes but can also be used for similar purposes like highlighting text.
        + `MiscColours` is a dict for all other colour needs. It contains some basic colours that are labelled for games but I encourage creative interpretation!
        The colours that are labelled for rarity for example could also be used to colourcode a dataset regarding the importance of the values:
        Common values are coloured as common and rare values that need attention are coloured as rare. \n
        
        These dicts are subclassed to ensure that a bracket access (dict["key"]) on an invalid key returns a random colour instead of raising an exception to allow expansion.
        However it is not advisable to expand these dicts at the moment. This colour system is still WIP and might change in the future. \n
        Only `__getitem__` is overwritten in the class thus `.get` can still be used to detect missing colours and provide replacements.
        """
        self.refreshThemeList()
        try:
            self._setTheme(self.Themes[Name], Name)
        except:
            NC(1,"Exception while loading colour theme",exc=sys.exc_info(),func="AGeApp.setTheme",input=str(Name))
    
    def addTheme(self, name, theme):
        # type: (str,typing.Dict[str,typing.Union[typing.Dict[str,QtGui.QBrush],QtGui.QPalette]]) -> None
        """
        Use this method to add custom themes. (They are saved in the dict `AppSpecificThemes`.) \n
        `name` should be a string and `theme` must be a dictionary containing the palettes and brush-dictionaries. \n
        Please note that the users custom colours take priority over application palettes
        thus you need to add a tag in front of your names that no user would ever use
        (for example your application name in square brackets (like `[AMaDiA] Dark`)). \n
        The tag must be unique enough to ensure that no user would ever use it in a custom name! (TODO:Changes regarding the requirement for uniqueness are planned)
        """
        self.AppSpecificThemes[name] = theme
        self.refreshThemeList()
        self.optionWindow.Input_Field.refreshThemeList() #TODO: This is not pretty. And that widget should really really really get renamed!!
    
    def refreshThemeList(self):
        #TODO: stop overwriting by appending the source in brackets and reversing the load order so that AGeColour.Colours always has priority (And then update doc of `addTheme`)
        self.Themes = {}
        try:
            # Load AppSpecificThemes
            self.Themes.update(self.AppSpecificThemes)
            # Load CustomColours
            try:
                spec = importlib.util.spec_from_file_location("CustomColourPalettes", os.path.join(self.AGeLibSettingsPath,"CustomColourPalettes.py"))
                CustomColours = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(CustomColours)
                #CustomColours.MyClass()
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
                self.Themes.update(CustomColours.Colours)
            except:
                NC(4,"Could not load custom colours",exc=sys.exc_info(),func="AGeApp.refreshThemeList")
            # Load AGeColour
            try:
                importlib.reload(AGeColour)
            except:
                NC(2,"Could not reload AGeColour",exc=sys.exc_info(),func="AGeApp.refreshThemeList")
            self.Themes.update(AGeColour.Colours)
        except:
            NC(1,"Exception while loading refreshing the themes dictionary",exc=sys.exc_info(),func="AGeApp.refreshThemeList")
    
    def _setTheme(self, Theme, Name):
        # type: (typing.Dict[str,typing.Union[typing.Dict[str,QtGui.QBrush],QtGui.QPalette]], str) -> None
        """
        This method is called by `setTheme` to apply the theme. \n
        For all theme changes `setTheme` should be used. \n
        If you have code that needs to run after the theme has changed (like applying colours to specific widgets) reimplement `r_setTheme`.
        """
        self.Theme.update(Theme)
        self.ThemeName = Name
        Theme = self.Theme
        Palette1 = Theme["Palette 1"] # type: QtGui.QPalette
        Palette2 = Theme["Palette 2"] # type: QtGui.QPalette
        Palette3 = Theme["Palette 3"] # type: QtGui.QPalette
        PenColours = Theme["Pen Colours"] # type: typing.Dict[str,QtGui.QBrush]
        NotificationColours = Theme["Notification Colours"] # type: typing.Dict[str,QtGui.QBrush]
        MiscColours = Theme["Misc Colours"] # type: typing.Dict[str,QtGui.QBrush]
        self.Palette = Palette1 #TODO: Remove self.Palette
        self.Palette1 = Palette1
        self.Palette1Active = QtGui.QPalette(self.Palette1)
        self.Palette2 = Palette2
        self.Palette3 = Palette3
        self.PenColours = ColourDict()
        self.PenColours.copyFromDict(PenColours)
        self.NotificationColours = ColourDict()
        self.NotificationColours.copyFromDict(NotificationColours)
        self.MiscColours = ColourDict()
        self.MiscColours.copyFromDict(MiscColours)
        self.PythonLexerColours = Theme["Python Lexer Colours"]
        Colour = self.Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base)
        self.BG_Colour = (Colour.red()/255,Colour.green()/255,Colour.blue()/255)
        Colour = self.Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text)
        self.TextColour = (Colour.red()/255,Colour.green()/255,Colour.blue()/255)
        self.colour_Pack = (self.Palette1 , self.BG_Colour , self.TextColour) #TODO: remove self.colour_Pack
        self.setPalette(self.Palette1Active)
        QtWidgets.QToolTip.setPalette(self.Palette1Active)
        self._update_NCF()
        
        c=[]
        for v in self.PenColours.values():
            #c.append(v.color().name(0))
            try:
                c.append(v.color().name(0)) # 0 = HexRgb
            except:
                c.append(v.color().name(QtGui.QColor.NameFormat.HexRgb))
        if matplotlibImported:
            self.mplCycler = matplotlib.cycler(color=c)
            matplotlib.rcParams['axes.prop_cycle'] = self.mplCycler
        
        #self.HandPixmap = self.handIcon.pixmap(self.handIcon.actualSize(QtCore.QSize(self.FontPixelSize,self.FontPixelSize)))
        #mask = self.HandPixmap.createMaskFromColor(QtGui.QColor('transparent'), QtCore.Qt.MaskInColor)
        #self.HandPixmap.fill(self.palette().color(QtGui.QPalette.Active,QtGui.QPalette.Text))
        #self.HandPixmap.setMask(mask)
        for w in self.topLevelWidgets():
            if matplotlibImported:
                for i in w.findChildren(MplWidget):
                    i.setColour(self.BG_Colour, self.TextColour, self.mplCycler)
            #for i in w.findChildren(Window_Frame_Widget):
            #    i.setPalette(FramePalette)
            #if versionParser(QtCore.qVersion()) >= versionParser("5.10"):
            #    for i in w.findChildren(TopBar_Widget):
            #        i.MoveMe.setPixmap(self.HandPixmap)
        self.r_setTheme()
        self.S_ColourChanged.emit()
    
    def r_setTheme(self):
        """
        This method is called after the colour palette has changed.   \n
        All GUI elements usually use the palette of the application but if the method `setPalette` is called
        the element looses the ability to inherit from the Application and needs special treatment.   \n
        Reimplement this method to provide such special treatment. \n
        For example `Palette2` and `Palette3` should only be applied to widgets in this method! \n
        Furthermore everything that uses `PenColours`, `NotificationColours` or `MiscColours` should be updated here or by connecting a custom function to `S_ColourChanged`.
        """
        pass
    
    def _init_colourAndFont(self, FontFamily = "Arial"):
        # type: (str) -> None
        #TODO: Accept more arguments for FontFamily, PointSize and colour Palette Name and use defaults if none were given or if something went wrong while applying them
        #TODO: Choose a different standard font since Arial is apparently very disliked in the font-community. Maybe use Lucida or Calibri. Or Comic Sans MS ;)
        self.FontFamily = FontFamily
        font = QtGui.QFont()
        font.setFamily(self.FontFamily)
        font.setPointSize(9)
        self.setFont(font)
        self.setTheme()
        
        # Always keep Statusbar Font small
        font = QtGui.QFont()
        font.setFamily(self.FontFamily)
        font.setPointSize(9)
        for w in self.topLevelWidgets():
            for i in w.findChildren(QtWidgets.QStatusBar):
                try:
                    i.setFont(font)
                except:
                    ExceptionOutput(sys.exc_info())
    
    def setFont(self, Family=None, PointSize=0, source=None, emitSignal=True):
        # type: (str|QtGui.QFont|None,int,AWWF|None,bool) -> None
        """
        Changes the font to `Family` and the font size to `PointSize` for the entire application.  \n
        `Family`: QFont, string or None (None keeps old family and only changes font size)  \n
        `PointSize`: int, if 0 ans `Family` is QFont the pointsize of QFont is used. \n
        `source` : The window from which the font was changed  \n
        If `PointSize` is less than 5 the value from the Font_Size_spinBox of `source` will be taken. If this fails it defaults to 9. \n
        `emitSignal`: If True (default) `S_FontChanged` is emitted after the new font is applied. \n\n
        Furthermore the Font_Size_spinBox of all windows is updated with the new value (the signals of Font_Size_spinBox are blocked during the update).\n
        All `TopBar_Widget`s are resized. \n
        The fontsize of all statusbars is always kept at 9 but the font family is updated.
        """
        if type(Family) == QtGui.QFont:
            if PointSize==0:
                PointSize = Family.pointSize()
            Family = Family.family()
            self.FontFamily = Family
        elif Family is None:
            Family = self.FontFamily
        else:
            self.FontFamily = Family
        if type(PointSize) == str:
            PointSize = int(PointSize)
        try:
            if PointSize < 5:
                try:
                    PointSize = source.TopBar.Font_Size_spinBox.value()
                except:
                    try:
                        NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="AGeApp.setFont",win=source.windowTitle())
                    except:
                        NC(msg="Could not read Font_Size_spinBox.value()",exc=sys.exc_info(),func="AGeApp.setFont")
                    PointSize = 9
        except:
            pass
        if type(PointSize) != int:
            print(type(PointSize)," is an invalid type for font size (",PointSize,")")
            try:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="AGeApp.setFont",win=source.windowTitle())
            except:
                NC(msg="{} is an invalid type for font size ({})".format(str(type(PointSize)),str(PointSize)),exc=sys.exc_info(),func="AGeApp.setFont")
            PointSize = 9
                
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                try:
                    if i.IncludeFontSpinBox:
                        # setValue emits ValueChanged and thus calls changeFontSize if the new Value is different from the old one.
                        # If the new Value is the same it is NOT emitted.
                        # To ensure that this behaves correctly either way the signals are blocked while changing the Value.
                        i.Font_Size_spinBox.blockSignals(True)
                        i.Font_Size_spinBox.setValue(PointSize)
                        i.Font_Size_spinBox.blockSignals(False)
                except:
                    ExceptionOutput(sys.exc_info())
        
        font = QtGui.QFont()
        font.setFamily(Family)
        font.setPointSize(PointSize)
        super(AGeApp, self).setFont(font)
        StatusbarFont = QtGui.QFont()
        StatusbarFont.setFamily(Family)
        StatusbarFont.setPointSize(9)
        self.FontPixelSize = self.font().pointSize()/72*self.primaryScreen().physicalDotsPerInch()
        #self.HandPixmap = self.handIcon.pixmap(self.handIcon.actualSize(QtCore.QSize(self.FontPixelSize,self.FontPixelSize)))
        #mask = self.HandPixmap.createMaskFromColor(QtGui.QColor('transparent'), QtCore.Qt.MaskInColor)
        #self.HandPixmap.fill((self.palette().color(QtGui.QPalette.Active,QtGui.QPalette.Text)))
        #self.HandPixmap.setMask(mask)
        
        matplotlib.rcParams.update({'font.size': PointSize*1.5})
        
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                try:
                    if type(i.parentWidget()) == MMenuBar:
                        i.setMinimumHeight(i.parentWidget().minimumHeight())
                    elif type(i.parentWidget()) == QtWidgets.QTabWidget:
                        i.setMinimumHeight(i.parentWidget().tabBar().minimumHeight())
                except:
                    ExceptionOutput(sys.exc_info())
                #if versionParser(QtCore.qVersion()) >= versionParser("5.10"):
                #    i.MoveMe.setPixmap(self.HandPixmap)
            # Always keep Statusbar Font small
            for i in w.findChildren(QtWidgets.QStatusBar):
                try:
                    i.setFont(StatusbarFont)
                except:
                    ExceptionOutput(sys.exc_info())
        
        if emitSignal:
            self.S_FontChanged.emit()
    
 # ---------------------------------- Notifications ----------------------------------
    def _init_NCF(self): # Notification_Flash
        """
        NO INTERACTION NEEDED \n
        Initiates the notification flash animations. This method is called automatically.
        """
        # CRITICAL: There should only be one Animation and NC should only contain the properties instead of the animation! ( colourNAME and duration )
        #           This also makes _update_NCF superfluous
        #           This would not only make multi threading saver but also make the flashing more stable when many notifications trigger at the same time!
        self.NCF_NONE = QtCore.QPropertyAnimation(self)
        
        self.NCF_r = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_r.setDuration(1000)
        self.NCF_r.setLoopCount(1)
        self.NCF_r.finished.connect(self._NCF_Finished)
        
        self.NCF_y = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_y.setDuration(1000)
        self.NCF_y.setLoopCount(1)
        self.NCF_y.finished.connect(self._NCF_Finished)
        
        self.NCF_g = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_g.setDuration(1000)
        self.NCF_g.setLoopCount(1)
        self.NCF_g.finished.connect(self._NCF_Finished)
        
        self.NCF_b = QtCore.QPropertyAnimation(self,b'FLASH_colour')
        self.NCF_b.setDuration(1000)
        self.NCF_b.setLoopCount(1)
        self.NCF_b.finished.connect(self._NCF_Finished)
    
    def _update_NCF(self):
        """
        NO INTERACTION NEEDED \n
        Updates the notification flash animations. This method is called automatically.
        """
        
        self.NCF_r.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_r.setKeyValueAt(0.5, self.NotificationColours["Error"].color())
        
        self.NCF_y.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_y.setKeyValueAt(0.5, self.NotificationColours["Warning"].color())
        
        self.NCF_g.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_g.setKeyValueAt(0.5, self.NotificationColours["Message"].color())
        
        self.NCF_b.setStartValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setEndValue(self.Palette.color(QtGui.QPalette.Window))
        self.NCF_b.setKeyValueAt(0.5, self.NotificationColours["Notification"].color())
    
    def _set_FLASH_colour(self, col): # Handles changes to the Property FLASH_colour
        """
        NO INTERACTION NEEDED \n
        Helpfunction that handles changes to the Property FLASH_colour.
        """
        palette = QtGui.QPalette(self.Palette1Active)
        for i in [QtGui.QPalette.Active, QtGui.QPalette.Inactive, QtGui.QPalette.Disabled]:
            palette.setBrush(i, QtGui.QPalette.Window, QtGui.QBrush(col,self.Palette1.brush(i, QtGui.QPalette.Window).style()))
        self.setPalette(palette)
    FLASH_colour = pyqtProperty(QtGui.QColor, fset=_set_FLASH_colour) # Defines the Property FLASH_colour
    
    def _NCF_Finished(self):
        """
        NO INTERACTION NEEDED \n
        This method is called when a notification flash animation is finished and resets the palette.
        """
        self.Palette1Active = QtGui.QPalette(self.Palette1)
        self.setPalette(self.Palette1Active)
        pass#self.TopBar_Error_Label.setFrameShape(QtWidgets.QFrame.NoFrame)
    
    def _notifyUser(self, N):
        # type: (NC) -> None
        """
        NO INTERACTION NEEDED \n
        Displays the notification `N` to the user. \n
        This method should not be called manually!
        """
        if N.unique:
            if N.m() in self.uniqueNotificationList:
                return
            else:
                self.uniqueNotificationList.append(N.m())
        if N.l() == 0:
            return
        elif N.l()!=4 or self.advanced_mode:
            Error_Text_TT,icon = self._listVeryRecentNotifications(N)
            self.LastNotificationText = N.DPS()
            self.LastNotificationToolTip = Error_Text_TT
            self.LastNotificationIcon = icon
            Lines = N.DPS().splitlines()
            Lines = Lines[:8] if len(Lines) > 8 else Lines
            for i in range(len(Lines)):
                Lines[i] = (Lines[i][:90] + '..') if len(Lines[i]) > 60 else Lines[i]
            Text = "\n".join(Lines)
            for w in self.topLevelWidgets():
                for i in w.findChildren(TopBar_Widget):
                    if i.IncludeErrorButton:
                        i.Error_Label.setText(Text)
                        i.Error_Label.setToolTip(Error_Text_TT)
                        i.Error_Label.setIcon(icon)
        
        if N.log:
            self.Notification_List.append(N)
            # Limit the list to 200 entries to save computer resources.
            # (This list is not meant to store information.
            #  It only holds some recent notifications in case the user missed one.
            #  If this list was longer it would only make it harder for the user to find anything)
            while len(self.Notification_List) > 200:
                self.Notification_List.pop(0)
            self.S_New_Notification.emit(N)
        # Allow the button to adjust to the new text:
        for w in self.topLevelWidgets():
            for i in w.findChildren(TopBar_Widget):
                if i.IncludeErrorButton:
                    i.parentWidget().adjustSize()
        if (N.l()!=4 or self.advanced_mode) and (not N.Flash == self.NCF_NONE) and (not N.Flash is None):
            N.Flash.start()
        # REMINDER: Somewhere you need to make the error message "Sorry Dave, I can't let you do this."
    
    def _listVeryRecentNotifications(self, N):
        # type: (NC) -> tuple[str,QtGui.QIcon]
        """
        NO INTERACTION NEEDED \n
        This helpfunction is used by _notifyUser to generate the tooltip for the notification button.
        """
        cTime = time.time()
        Error_Text_TT = N.TTS()
        level = N.l()
        icon = N.icon
        for i in range(len(self.Notification_List)):
            if i< 10 and cTime - self.Notification_List[-i-1]._time_time < 2 and len(Error_Text_TT.splitlines())<40:
                if self.Notification_List[-i-1].l()!=0 and (self.Notification_List[-i-1].l()!=4 or self.advanced_mode):
                    Error_Text_TT += "\n\n"
                    Error_Text_TT += str(self.Notification_List[-i-1])
                    cTime = self.Notification_List[-i-1]._time_time
                    if level > self.Notification_List[-i-1].l():
                        level = self.Notification_List[-i-1].l()
                        icon = self.Notification_List[-i-1].icon
            else:
                break
        return (Error_Text_TT,icon)
    
 # ---------------------------------- SubWindows ----------------------------------
    
    def r_init_Options(self):
        """
        This method initializes the standard options window and is called automatically. \n
        If you want a custom options window reimplement this method with the following code:\n
        ```python
        self.optionWindow = Custom_Options_Window()
        ```
        and replace `Custom_Options_Window` with your own class that is derived from AWWF. \n
        Your custom options window should include the widget `OptionsWidget_1_Appearance`!!!
        """
        self.optionWindow = Options_Window()
    
    def showWindow_Notifications(self): #TODO: This should not reset the position but merely show the window in the position it used to be but take it to the foreground and activate it.
        """
        Shows a window that lists all notifications and displays their details. \n
        Default access: pressing the notification button
        """
        if self.Notification_Window is None:
            self.Notification_Window = Notification_Window()
        self.Notification_Window.show()
        self.processEvents()
        self.Notification_Window.positionReset()
        self.processEvents()
        self.Notification_Window.activateWindow()
    
    def showWindow_IDE(self):
        """
        Shows a window that can execute code within the program. (This window is very useful for debugging) \n
        Default shortcut (applicationwide): ctrl+T
        """
        if self.exec_Window is None:
            self.exec_Window = exec_Window()
        self.exec_Window.show()
        self.processEvents()
        self.exec_Window.positionReset()
        self.processEvents()
        self.exec_Window.activateWindow()
    
    def showWindow_Options(self):
        """
        Shows the options window. \n
        Default shortcut (applicationwide): alt+O
        """
        self.optionWindow.show()
        self.processEvents()
        self.optionWindow.activateWindow()
        self.processEvents()
    
    def showWindow_Help(self, category=""):
        """
        Shows the help window. \n
        Default shortcut (applicationwide): F1
        """
        self.HelpWindow.showCategory(category)
        self.processEvents()
    
 # ---------------------------------- Files and Folders ----------------------------------
    
    def _makeAGeLibPath(self): #CRITICAL: Reamen all FolderPath members to FolderPath_{name of folder} to be easily accessible
        """
        NO INTERACTION NEEDED \n
        This method creates/finds/validates the path to the AGeLib config directory.
        """
        self.AGeLibPathOK = False
        self.AGeLibPath = False
        self.AGeLibSettingsPath = False
        self.ScreenshotFolderPath = False
        self.PictureFolderPath = False
        self.FolderPath_CodeBackup = False
        try:
            self.AGeLibPath = os.path.join(os.path.expanduser("~"),"AGeLib")
            os.makedirs(self.AGeLibPath,exist_ok=True)
            # Create Settings folder
            self.AGeLibSettingsPath = os.path.join(self.AGeLibPath,"Settings")
            os.makedirs(self.AGeLibSettingsPath,exist_ok=True)
            FileName = os.path.join(self.AGeLibSettingsPath,"CustomColourPalettes.py")
            with open(FileName,'a',encoding="utf-8") as text_file:
                pass # We just ensure that the file exists here.
            if os.stat(FileName).st_size == 0: # Now we ensure that it contains the Colours dictionary
                with open(FileName,'w',encoding="utf-8") as text_file:
                    text_file.write(r"Colours={}")
            # Create Screenshots folder
            self.ScreenshotFolderPath = os.path.join(self.AGeLibPath,"Screenshots")
            os.makedirs(self.ScreenshotFolderPath,exist_ok=True)
            # Create Pictures folder
            self.PictureFolderPath = os.path.join(self.AGeLibPath,"Pictures")
            os.makedirs(self.PictureFolderPath,exist_ok=True)
            # Create ProgramFiles folder
            self.ProgramFilesFolderPath = os.path.join(self.AGeLibPath,"ProgramFiles")
            os.makedirs(self.ProgramFilesFolderPath,exist_ok=True)
            # Create CodeBackup folder
            self.FolderPath_CodeBackup = os.path.join(self.AGeLibPath,"CodeBackup")
            os.makedirs(self.FolderPath_CodeBackup,exist_ok=True)
            #
            self.AGeLibPathOK = True
        except:
            NC(1,"Could not create/validate AGeLib folder",exc=sys.exc_info())
        try:
            self.r_createFolders()
        except:
            NC(1,"Could not create/validate program specific folders",exc=sys.exc_info())
        #try:
        #    self.handIcon = QtGui.QIcon(r"C:\Users\Robin\Desktop\Projects\AGeLib\Icons\Hand.png")#MAYBE: SET PATH!!!!!!
        #except:
        #    self.handIcon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        #self.FontPixelSize = 9/72*self.primaryScreen().physicalDotsPerInch()
        #self.HandPixmap = self.handIcon.pixmap(self.handIcon.actualSize(QtCore.QSize(self.FontPixelSize,self.FontPixelSize)))
        #mask = self.HandPixmap.createMaskFromColor(QtGui.QColor('transparent'), QtCore.Qt.MaskInColor)
        #self.HandPixmap.fill(self.palette().color(QtGui.QPalette.Active,QtGui.QPalette.Text))
        #self.HandPixmap.setMask(mask)
    
    def r_createFolders(self):
        """
        This Function is called automatically at the end of `_makeAGeLibPath` which is called by the `__init__`. \n
        Reimplement this function to create folders. \n
        It is recommended to create a program specific folder in `self.AGeLibPath`. \n
        Example:\n
        ```python
        self.Folder = os.path.join(self.AGeLibPath,"PROGRAM_NAME")
        os.makedirs(self.Folder,exist_ok=True)
        ```
        """
        pass
    
    def pyFileSave(self, name, content, version = None, lastCompatibleVersion = None, message="", saveUpdate=False, dataloss=False, forceUp=False, forceAll=False): #CRITICAL: implement this
        """
        Saves a python file but puts the current AGeLib version (or given `version` string) as a variable in the beginning of the file. \n
        `name` is the target's full path including the name of the file and the file extension (should be `.py`) and `content` is the string containing the new content of the file. \n
        If the file already exists it is checked with which version it was written and asks the User whether it should proceed if the version differs from the current version. \n
        If the string `lastCompatibleVersion` is given the user is only asked if the version of the file is older than this last compatible version. \n
        The string `message` will be displayed to the user in case of a version difference. It should contain the purpose of the file, some information about forewards and backwards compatibility, and potentially lost data when overwriting.
        Maybe even a list of all saved items. In short: It should help the User make an informed decision! (The user is only given the path of the file by default.) \n
        If `saveUpdate` is True the user will be informed that the program is aware of the version difference and has taken it into consideration so that no data will be lost when updating. \n
        If `dataloss` is True the user will be informed that the program is aware of the version difference but is incapeable of keeping all saved data. \n
        If `forceUp` is True the File will only be overwritten if the version of the file is older. This should only be used for small files which will ALWAYS be backwards compatibel. \n
        If `forceAll` is True the Version is not checked. This should only be used for small files whose structure will NEVER change and which will ALWAYS be compatible to ALL versions. \n
        TO BE CLEAR: If compatibility is not guaranteed the User should decide if they want to overwrite the file!
        """
        pass
    
    def pyFileCheck(self, name): #CRITICAL: implement this
        # type: (str) -> tuple[bool,str]
        """
        Checks if a file (created with pyFileSave) exists and with which version it was written. \n
        returns bool, string \n
        bool is True if the file exists or False if it does not. \n
        string is the version of the file. If the file does not contain a version string the string is empty
        """
        pass
    
 # ---------------------------------- Other ----------------------------------
    #def
    
 # ---------------------------------- Static Methods ----------------------------------
    @staticmethod
    def instance():
        # type: () -> AGeApp
        """
        This static method returns the instance of the main application. \n
        This is basically the same as `QtWidgets.QApplication.instance()`. \n
        This method is only overwritten for type hinting purposes (so that the returned type is acknowledged as AGeApp rather than QtWidgets.QApplication).
        """
        return QtWidgets.QApplication.instance()
    
#endregion

