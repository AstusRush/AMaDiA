#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
#endregion Import


#region AWWF

class AWWF(QtWidgets.QMainWindow): # Astus Window With Frame
    """
    AWWF (Astus Window With Frame) is the face of AGeLib! This window is a full reimplementation
    of the standard window that operating systems (technically their window manager) provide. \n
    todo: Remove this line: (The regular window frames are boring and all professional applications use their own frame. This is my frame so I am a professional now!!!) \n
    TODO: Explain how the init and the top bar work! Make some simple examples!
    """
    #MAYBE: Implement borderless windowed mode as an alternative to full screen. This could be handled by adding a flag that is read in showFullScreen to decide which full screen mode to apply
    #TODO: Remove dependencies for TopBar and StatusBar to make these entirely optional
    #TODO: Add the option to handle maximized by manually adjusting size and position instead of calling the Qt method to maximize a window. QPanda3D and fruiture don't like the Qt method...
    #MAYBE: Make it possible to draw with a pen on all windows
    def __init__(self, parent = None, IncludeTopBar=True, initTopBar=True, IncludeStatusBar=True, IncludeErrorButton = False, FullscreenHidesBars = False):
        self.BarsHidden = False
        super(AWWF, self).__init__(parent)
        self.IncludeTopBar, self.IncludeStatusBar, self.FullscreenHidesBars, self.IncludeErrorButton = IncludeTopBar, IncludeStatusBar, FullscreenHidesBars, IncludeErrorButton
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint,True)
        self.AWWF_CentralWidget = Window_Frame_Widget(self)
        self.AWWF_CentralWidget_layout =  QtWidgets.QGridLayout(self.AWWF_CentralWidget)
        self.AWWF_CentralWidget_layout.setContentsMargins(0, 0, 0, 0)
        self.AWWF_CentralWidget_layout.setSpacing(0)
        self.AWWF_CentralWidget_layout.setObjectName("gridLayout")
        self.AWWF_CentralWidget.setLayout(self.AWWF_CentralWidget_layout)
        
        self.AWWF_CentralWindow = QtWidgets.QMainWindow(self)
        self.AWWF_CentralWidget_layout.addWidget(self.AWWF_CentralWindow,1,0)
        
        super(AWWF, self).setCentralWidget(self.AWWF_CentralWidget)
        self.AWWF_p_MenuBar = None
        self.AWWF_p_CentralWidget = None
        self.AWWF_p_StatusBar = None
        self.StandardSize = (900, 500)
        self.LastOpenState = self.showNormal
        self.OnTop = False

        self.installEventFilter(self)

        if IncludeTopBar:
            self.TopBar = TopBar_Widget(self, initTopBar, IncludeErrorButton = self.IncludeErrorButton)
            self.MenuBar = MMenuBar(self)
            self.setMenuBar(self.MenuBar)
            self.MenuBar.setCornerWidget(self.TopBar)
            self.MenuBar.setContentsMargins(0,0,0,0)
        if IncludeStatusBar:
            self.Statusbar = StatusBar_Widget(self)
            self.Statusbar.setObjectName("Statusbar")
            self.setStatusBar(self.Statusbar)
            self.Statusbar.setSizeGripEnabled(False)
            self.windowTitleChanged.connect(self.Statusbar.setWindowTitle)

 ##################### Layout Attempt
  #    def setMenuBar(self, MenuBar):
  #        if MenuBar == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.addWidget(QtWidgets.QWidget(self),0,0)
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
  #            except:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(MenuBar,0,0)
  #            MenuBar.setCursor(MenuBar.cursor())
  #        self.AWWF_p_MenuBar = MenuBar
  #        return True
  #
  #    def menuBar(self):
  #        return self.AWWF_p_MenuBar
  #
  #    def setCentralWidget(self, CentralWidget):
  #        if CentralWidget == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_CentralWidget)
  #            except:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(CentralWidget,1,0)
  #            CentralWidget.setCursor(CentralWidget.cursor())
  #        self.AWWF_p_CentralWidget = CentralWidget
  #        return True
  #
  #    def centralWidget(self):
  #        return self.AWWF_p_CentralWidget
  #        
  #    def setStatusBar(self, StatusBar):
  #        if StatusBar == None:
  #            try:
  #                self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_StatusBar)
  #            except:
  #                pass
  #        else:
  #            self.AWWF_CentralWidget_layout.addWidget(StatusBar,2,0)
  #            StatusBar.setCursor(StatusBar.cursor())
  #        self.AWWF_p_StatusBar = StatusBar
  #        return True
  #
  #    def statusBar(self):
  #        return self.AWWF_p_StatusBar
  #
  #
 ##################### MenuBar/CentralWidget/StatusBar/ToolBar

    def setMenuBar(self, MenuBar):
        if MenuBar == None:
            try:
                self.AWWF_CentralWindow.setMenuBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except:
                pass
        else:
            self.AWWF_CentralWindow.setMenuBar(MenuBar)
            MenuBar.setCursor(MenuBar.cursor())
        self.AWWF_p_MenuBar = MenuBar
        return True
        # TODO: The following seems to be cleaner and more efficient... Use this for all of these redirects...
        #r = self.AWWF_CentralWindow.setMenuBar(MenuBar)
        #try:
        #    MenuBar.setCursor(MenuBar.cursor())
        #except:
        #    pass
        #return r

    def menuBar(self):
        return self.AWWF_CentralWindow.menuBar()

    def setCentralWidget(self, CentralWidget):
        if CentralWidget == None:
            try:
                self.AWWF_CentralWindow.setCentralWidget(None)
            except:
                pass
        else:
            self.AWWF_CentralWindow.setCentralWidget(CentralWidget)
            CentralWidget.setCursor(CentralWidget.cursor())
        self.AWWF_p_CentralWidget = CentralWidget
        return True

    def centralWidget(self):
        return self.AWWF_CentralWindow.centralWidget()
        
    def setStatusBar(self, StatusBar):
        if StatusBar == None:
            try:
                self.AWWF_CentralWindow.setStatusBar(None)
            except:
                pass
        else:
            self.AWWF_CentralWindow.setStatusBar(StatusBar)
            StatusBar.setCursor(StatusBar.cursor())
        self.AWWF_p_StatusBar = StatusBar
        return True

    def statusBar(self):
        return self.AWWF_CentralWindow.statusBar()

    # ToolBar #TODO:Expand
    def addToolBar(self, *ToolBar):
        if ToolBar == None:
            try:
                self.AWWF_CentralWindow.addToolBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except:
                pass
        else:
            TB = self.AWWF_CentralWindow.addToolBar(*ToolBar)
        return TB

    def insertToolBar(self, *ToolBar):
        if ToolBar == None:
            try:
                self.AWWF_CentralWindow.insertToolBar(None)
                #self.AWWF_CentralWidget_layout.removeWidget(self.AWWF_p_MenuBar)
            except:
                pass
        else:
            TB = self.AWWF_CentralWindow.insertToolBar(*ToolBar)
        return TB

    def toolBarArea(self):
        return self.AWWF_CentralWindow.toolBarArea()

 ##################### show, restoreState and positionReset
    def hideBars(self,b):
        """
        If b=True  the menu, top and status bar are permanently hidden. \n
        If b=False the menu, top and status bar will be shown again. \n
        Hiding these bars is not recommended!
        """
        self.BarsHidden = b
        self.TopBar.setVisible(b)
        try:
            self.MenuBar.setVisible(b)
        except:
            pass
        try:
            self.Statusbar.setVisible(b)
        except:
            pass

    def setTopBarVisible(self,b):
        if not self.BarsHidden:
            self.TopBar.setVisible(b)
            try:
                self.MenuBar.setVisible(b)
            except:
                pass
            try:
                self.Statusbar.setVisible(b)
            except:
                pass

    def showNormal(self):
        self.setTopBarVisible(True)
        self.AWWF_CentralWidget.showFrame()
        self.TopBar.MaximizeButton.setText("🗖")
        super(AWWF, self).showNormal()

    def show(self):
        self.setTopBarVisible(True)
        super(AWWF, self).show()
        QtWidgets.QApplication.instance().processEvents()
        if self.isFullScreen() or self.isMaximized():
            self.AWWF_CentralWidget.hideFrame()
            self.TopBar.MaximizeButton.setText("🗗")
        else:
            self.AWWF_CentralWidget.showFrame()
            self.TopBar.MaximizeButton.setText("🗖")
        if self.isFullScreen() and self.FullscreenHidesBars:
            self.setTopBarVisible(False)

    def showMaximized(self):
        # Windows will not behave correctly when we try to maximize a window which does not
        # have minimize nor maximize buttons in the window frame. Windows would then ignore
        # non-available geometry, and rather maximize the widget to the full screen, minus the
        # window frame (caption).
        # Qt does a trick here, by adding a maximize button before
        # maximizing the widget, and then remove the maximize button afterwards.
        # However this trick does apparently not work when having no frame when not on the main screen.
        # Thus we need to emulate maximized on other screens when we want to distinguish between maximized and fullscreen.
        # todo: emulate maximized on other screens than the main screen
        #VALIDATE: It should work now (I simply correct the geometry after making it fullscreen) but it might cause some other problems so this needs testing...
        #try:
        #    self.window().setGeometry(
        #        QtWidgets.QStyle.alignedRect(
        #            QtCore.Qt.LeftToRight,
        #            QtCore.Qt.AlignCenter,
        #            self.size(),
        #            self.window().screen().availableGeometry()))
        #except: # For compatibility reasons try the outdated version
        #    self.window().setGeometry(
        #        QtWidgets.QStyle.alignedRect(
        #            QtCore.Qt.LeftToRight,
        #            QtCore.Qt.AlignCenter,
        #            self.size(),
        #            QtWidgets.QApplication.instance().desktop().availableGeometry(self)))
        self.setTopBarVisible(True)
        self.AWWF_CentralWidget.hideFrame()
        self.TopBar.MaximizeButton.setText("🗗")
        super(AWWF, self).showMaximized()
        if platform.system() == 'Windows': # Windows makes borderless windows too big on secondary screens (it makes them fullscreen (with everything that comes with that) instead of maximizing them)
            # This trick maximizes the window correctly but since windows still thinks the window is in fullscreen the window behaves slightly unexpected when switching between maximized and fullscreen
            #TODO: Add an extra variable that tracks the ACTUAL state of the window (basically reimplement self.isFullScreen() and self.isMaximized() ) to fix that behaviour!
            # TO BE CLEAR: This sideeffect only occurs on secondary monitors. The behaviour on the primary screen is unaffected by this trick and the window behaves exactly as expected on the primary screen!
            #self.setWindowState(QtCore.Qt.WindowMaximized) # Even calling this specifically makes the window fullscreen instead of maximized...
            try:
                self.window().setGeometry(self.window().screen().availableGeometry())
            except: # For compatibility reasons try the outdated version
                self.window().setGeometry(QtWidgets.QApplication.instance().desktop().availableGeometry(self))

    def showFullScreen(self):
        if self.FullscreenHidesBars:
            self.setTopBarVisible(False)
        else:
            self.setTopBarVisible(True)
        self.AWWF_CentralWidget.hideFrame()
        self.TopBar.MaximizeButton.setText("🗗")
        super(AWWF, self).showFullScreen()
        
    def restoreState(self,state,version=0):
        self.setTopBarVisible(True)
        super(AWWF, self).restoreState(state,version)
        QtWidgets.QApplication.instance().processEvents()
        if self.isFullScreen() or self.isMaximized():
            self.AWWF_CentralWidget.hideFrame()
            self.TopBar.MaximizeButton.setText("🗗")
        else:
            self.AWWF_CentralWidget.showFrame()
            self.TopBar.MaximizeButton.setText("🗖")
        if self.isFullScreen() and self.FullscreenHidesBars:
            self.setTopBarVisible(False)
            
    def positionReset(self):
        self.showNormal()
        QtWidgets.QApplication.instance().processEvents()
        try:
            self.resize(*self.StandardSize)#, screen = True)
        except:
            self.resize(900, 600)#, screen = True)
        #QtWidgets.QApplication.instance().processEvents()
        for _ in range(2):
            # This must be executed twice in case the window is moved between 2 screens with different scale factors:
            #   The first move moves the window to the new screen's center. 
            #   Then the OS rescales the window according to the dpi. When scaling the top left corner of the window is stationary 
            #        thus the center of the window is no longer in the center of the screen.
            #   The second move uses the new frameGeometry to correct the position.
            try:
                frameGm = self.frameGeometry()
                screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos())
                centerPoint = screen.availableGeometry().center()
                frameGm.moveCenter(centerPoint)
                self.move(frameGm.topLeft())
            except:
                try: # For compatibility reasons try the outdated version
                    frameGm = self.frameGeometry()
                    screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                    centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
                    frameGm.moveCenter(centerPoint)
                    self.move(frameGm.topLeft())
                except:
                    ExceptionOutput(sys.exc_info())
        QtWidgets.QApplication.instance().processEvents()

    def toggleFullscreen(self):
        if not self.isFullScreen():
            if self.isMaximized():
                self.LastOpenState = self.showMaximized
                self.TopBar.MaximizeButton.setText("🗖")
            else:
                self.LastOpenState = self.showNormal
                self.TopBar.MaximizeButton.setText("🗗")
            self.showFullScreen()
        else:
            if self.LastOpenState == self.showMaximized:
                self.TopBar.MaximizeButton.setText("🗗")
            else:
                self.TopBar.MaximizeButton.setText("🗖")
            self.LastOpenState()

    def resize(self, w, h=None, autoscale=True, screen = None):
        """
        w,h = width and height in pixel \n
        alternatively w = QSize and h = None \n
        if autoscale == True the size will be multiplied with the scale factor of the OS. \n
        Autoscale is only supported with versions of QT >= Qt 5.14 \n
        screen = None, True or instance of QtGui.QScreen \n
        screen is the screen whose dpi setting is used for the scaling \n
        if screen is None (default) the window's current screen is used \n
        if screen is True the screen which currently contains the mouse cursor is used
        """
        if autoscale and versionParser(QtCore.qVersion()) >= versionParser("5.14"):
            if screen is None:
                scale = self.screen().logicalDotsPerInchX()/96.0
            elif screen is True:
                scale = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).logicalDotsPerInchX()/96.0
            else:
                scale = screen.logicalDotsPerInchX()/96.0
            if h == None:
                if type(w) in [list,tuple]:
                    w, h = scale*w[0], scale*w[1]
                else:
                    w *= scale
            else:
                w, h = scale*w, scale*h
        if h == None:
            if type(w) in [list,tuple]:
                super(AWWF, self).resize(w[0],w[1])
            else:
                super(AWWF, self).resize(w)
        else:
            super(AWWF, self).resize(w,h)

 ##################### eventFilter
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == 6 and App().enableHotkeys: # QtCore.QEvent.KeyPress
            if event.modifiers() == QtCore.Qt.AltModifier:
                if event.key() == QtCore.Qt.Key_T :#and source is self: # Alt+T to toggle on top
                    if not self.OnTop:
                        print("Try OnTop")
                        self.OnTop = True
                        self.setWindowFlag(QtCore.Qt.X11BypassWindowManagerHint,True)
                        self.setWindowFlag(QtCore.Qt.BypassWindowManagerHint,True)
                        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,True)
                        QtWidgets.QApplication.instance().processEvents()
                        self.show()
                        return True
                    else:
                        print("No longer OnTop")
                        self.OnTop = False
                        self.setWindowFlag(QtCore.Qt.X11BypassWindowManagerHint,False)
                        self.setWindowFlag(QtCore.Qt.BypassWindowManagerHint,False)
                        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,False)
                        QtWidgets.QApplication.instance().processEvents()
                        self.show()
                        return True
            else:
                if event.key() == QtCore.Qt.Key_F11 : # F11 to toggle Fullscreen
                    self.toggleFullscreen()
                    return True
        #    #if event.modifiers() == QtCore.Qt.MetaModifier: # Does not work on windows as the meta key is not detected this way
        #    modifiers = QtWidgets.QApplication.keyboardModifiers() # Detects the meta key
        #    if modifiers == QtCore.Qt.MetaModifier: # Does not work on windows as windows eats all other key while the Meta Key is pressed...
        #        print("win")
        #        screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        #        screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
        #        Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
        #        Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
        #        Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
        #        Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
        #        # Left Side
        #        if event.key() == QtCore.Qt.Key_Left:
        #            self.window().resize(Full_X, Half_Y, autoscale=False)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopLeft(screen.topLeft())
        #            self.window().move(frameGm.topLeft())
        #        # Right Side
        #        elif event.key() == QtCore.Qt.Key_Right:
        #            self.window().resize(Full_X, Half_Y, autoscale=False)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopRight(screen.topRight())
        #            self.window().move(frameGm.topLeft())
        #        # Top Side
        #        elif event.key() == QtCore.Qt.Key_Up:
        #            self.window().resize(Full_X, Half_Y, autoscale=False)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveTopRight(screen.topRight())
        #            self.window().move(frameGm.topLeft())
        #        # Bottom Side
        #        elif event.key() == QtCore.Qt.Key_Down:
        #            self.window().resize(Full_X, Half_Y, autoscale=False)
        #            frameGm = self.window().frameGeometry()
        #            frameGm.moveBottomLeft(screen.bottomLeft())
        #            self.window().move(frameGm.topLeft())
        
        #if type(source) == QtWidgets.QAction and event.type() == QtCore.QEvent.Enter and source.toolTip()!="": #==10
        #    QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),source.toolTip(),source)
        return super(AWWF, self).eventFilter(source, event) # let the normal eventFilter handle the event

class TopBar_Widget(QtWidgets.QWidget): # CRITICAL: there should be a flag to merely hide the 3 control buttons in fullscreen instead of hiding top and status bar completely
    def __init__(self, parent=None, DoInit=False, IncludeMenu = False, IncludeFontSpinBox = True, IncludeErrorButton = False, IncludeAdvancedCB = False):
        # type: (QtWidgets.QWidget, bool,bool,bool,bool,bool) -> None
        super(TopBar_Widget, self).__init__(parent)
        self.moving = False
        self.offset = 0
        self.IncludeMenu, self.IncludeFontSpinBox = IncludeMenu, IncludeFontSpinBox
        self.IncludeErrorButton, self.IncludeAdvancedCB = IncludeErrorButton, IncludeAdvancedCB
        if DoInit:
            self.init(IncludeMenu, IncludeFontSpinBox, IncludeErrorButton, IncludeAdvancedCB)

    def init(self, IncludeMenu = False, IncludeFontSpinBox = False, IncludeErrorButton = False, IncludeAdvancedCB = False):
        # type: (bool,bool,bool,bool) -> None
        # TODO: restrict the height and add the Option for a QtWidgets.QSpacerItem to make the horizontal spacing work if not corner widget
        self.IncludeMenu, self.IncludeFontSpinBox = IncludeMenu, IncludeFontSpinBox
        self.IncludeErrorButton, self.IncludeAdvancedCB = IncludeErrorButton, IncludeAdvancedCB
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setObjectName("TopBar")
        if self.layout() == None:
            self.gridLayout = QtWidgets.QGridLayout(self)
            self.gridLayout.setContentsMargins(0, 0, 0, 0)
            self.gridLayout.setSpacing(0)
            self.gridLayout.setObjectName("gridLayout")
            #self.gridLayout.setSizeConstraint(QtWidgets.QGridLayout.SetNoConstraint)
            self.setLayout(self.gridLayout)
        
        self.ButtonSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.CloseButton = QtWidgets.QToolButton(self)
        self.CloseButton.setObjectName("CloseButton")
        self.layout().addWidget(self.CloseButton, 0, 108, 1, 1,QtCore.Qt.AlignRight)
        self.CloseButton.setText("🗙") # TODO: Apple does not support these...
        
        self.RedHighlightPalette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(155, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.RedHighlightPalette.setBrush(QtGui.QPalette.All, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.RedHighlightPalette.setBrush(QtGui.QPalette.All, QtGui.QPalette.ButtonText, brush)
        self.CloseButton.installEventFilter(self)
        self.CloseButton.setAutoRaise(True)
        self.CloseButton.setSizePolicy(self.ButtonSizePolicy)
        self.CloseButton.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.MaximizeButton = QtWidgets.QToolButton(self)
        self.MaximizeButton.setObjectName("MaximizeButton")
        self.layout().addWidget(self.MaximizeButton, 0, 107, 1, 1,QtCore.Qt.AlignRight)
        self.MaximizeButton.setText("🗖") # TODO: Apple does not support these...
        self.MaximizeButton.installEventFilter(self)
        self.MaximizeButton.setAutoRaise(True)
        self.MaximizeButton.setSizePolicy(self.ButtonSizePolicy)
        
        self.MinimizeButton = QtWidgets.QToolButton(self)
        self.MinimizeButton.setObjectName("MinimizeButton")
        self.layout().addWidget(self.MinimizeButton, 0, 106, 1, 1,QtCore.Qt.AlignRight)
        self.MinimizeButton.setText("🗕") # TODO: Apple does not support these...
        self.MinimizeButton.installEventFilter(self)
        self.MinimizeButton.setAutoRaise(True)
        self.MinimizeButton.setSizePolicy(self.ButtonSizePolicy)
        
        self.OptionsButton = QtWidgets.QToolButton(self)
        self.OptionsButton.setObjectName("OptionsButton")
        self.layout().addWidget(self.OptionsButton, 0, 105, 1, 1,QtCore.Qt.AlignRight)
        self.OptionsButton.setText("⚙") # TODO: Apple does not support these...
        self.OptionsButton.setToolTip("Show the options window")
        self.OptionsButton.installEventFilter(self)
        self.OptionsButton.setAutoRaise(True)
        self.OptionsButton.setSizePolicy(self.ButtonSizePolicy)
        
        self.MoveMe = QtWidgets.QLabel(self)
        self.MoveMe.setObjectName("MoveMe")
        self.layout().addWidget(self.MoveMe, 0, 104, 1, 1,QtCore.Qt.AlignRight)
        #self.MoveMe.
        #if versionParser(QtCore.qVersion()) < versionParser("5.10"):
        self.MoveMe.setText("   ⬤   ") # TODO: Apple probably doesn't support this either...
            # ⬤ ✥ 🖐 
            #self.MoveMe.setText("  🖐  ")#▨#🖐
            #self.MoveMe.setText("<p style=\"color:transparent;\">  🖐  </p>")#▨#🖐
            #self.MoveMe.setText("  🖐\uEF0E  ")#▨#🖐
            #self.MoveMe.setText("<p>&#128528;&#65038;&#128542;&#65038;&#128512;&#65038; each followed by VS15</p>")#▨#🖐
            #self.MoveMe.setText("<p style=\"font-family: Helvetica, Arial;\">  🖐  </p>")#▨#🖐
        #else:
        #    self.MoveMe.setPixmap(App().HandPixmap)
        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        
        self.CloseButton.clicked.connect(lambda: self.exit())
        self.MaximizeButton.clicked.connect(lambda: self.toggleMinMax())
        self.MinimizeButton.clicked.connect(lambda: self.minimize())
        self.OptionsButton.clicked.connect(lambda: App().showWindow_Options())
        
        try:
            #self.window().menuBar().installEventFilter(self)
            if IncludeMenu:
                self.Menu = QtWidgets.QToolButton(self)
                self.Menu.setObjectName("Menu")
                self.layout().addWidget(self.Menu, 0, 103, 1, 1,QtCore.Qt.AlignRight)
                self.Menu.setText("\u2630")#☰ #("≡")
                self.Menu.setAutoRaise(True)
                self.Menu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
                self.Menu.setMenu(self.window().Menu)
                self.Menu.setSizePolicy(self.ButtonSizePolicy)
        except:
            ExceptionOutput(sys.exc_info())
        
        if IncludeAdvancedCB:
            self.AdvancedCB = QtWidgets.QCheckBox(self)
            self.AdvancedCB.setText("")
            self.AdvancedCB.setToolTip("Advanced Mode (alt+A)")
            self.AdvancedCB.setChecked(QtWidgets.QApplication.instance().advanced_mode)
            self.AdvancedCB.setObjectName("AdvancedCB")
            self.layout().addWidget(self.AdvancedCB, 0, 102, 1, 1,QtCore.Qt.AlignRight)
            self.AdvancedCB.clicked.connect(lambda checked: QtWidgets.QApplication.instance().toggleAdvancedMode(checked))
        
        if IncludeFontSpinBox:
            self.Font_Size_spinBox = QtWidgets.QSpinBox(self)
            self.Font_Size_spinBox.setMinimum(5)
            self.Font_Size_spinBox.setMaximum(25)
            self.Font_Size_spinBox.setProperty("value", self.font().pointSize())
            self.Font_Size_spinBox.setObjectName("Font_Size_spinBox")
            self.layout().addWidget(self.Font_Size_spinBox, 0, 101, 1, 1,QtCore.Qt.AlignRight)
            self.Font_Size_spinBox.valueChanged.connect(lambda: self.changeFontSize())
        
        if IncludeErrorButton:
            self.Error_Label = QtWidgets.QPushButton(self)
            self.Error_Label.setObjectName("Error_Label")
            self.Error_Label.setText(QtWidgets.QApplication.instance().LastNotificationText)
            self.Error_Label.setToolTip(QtWidgets.QApplication.instance().LastNotificationToolTip)
            self.Error_Label.setIcon(QtWidgets.QApplication.instance().LastNotificationIcon)
            self.layout().addWidget(self.Error_Label, 0, 100, 1, 1,QtCore.Qt.AlignRight)
            self.Error_Label.installEventFilter(self)
            self.Error_Label.clicked.connect(lambda: QtWidgets.QApplication.instance().showWindow_Notifications())

    def minimize(self):
        self.window().showMinimized()

    def toggleMinMax(self):
        if not self.window().isFullScreen():
            if self.window().isMaximized():
                self.window().showNormal()
            else:
                self.window().showMaximized()
        else:
            try:
                self.window().LastOpenState()
            except AttributeError:
                self.window().showMaximized()

    def exit(self):
        self.window().close()

    def changeFontSize(self):
        try:
            QtWidgets.QApplication.instance().setFont(PointSize = self.Font_Size_spinBox.value(), source=self.window())
        except:
            ExceptionOutput(sys.exc_info())
        
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        #if event.type() == 5: # QtCore.QEvent.MouseMove
        #    if self.moving: self.window().move(event.globalPos()-self.offset)
        #elif event.type() == 2: # QtCore.QEvent.MouseButtonPress
        #    if event.button() == QtCore.Qt.LeftButton:
        #        self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #        self.MaximizeButton.setText("🗖")
        #        self.moving = True; self.offset = event.globalPos()-self.window().geometry().topLeft()
        #elif event.type() == 3: # QtCore.QEvent.MouseButtonRelease
        #    self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #    self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        #    self.moving = False
        #    if event.button() == QtCore.Qt.LeftButton:
        #        pos = self.window().pos()
        #        #if (pos.x() < 0):
        #        #    pos.setX(0)
        #        #    self.window().move(pos)
        #        if (pos.y() < 0):
        #            pos.setY(0)
        #            self.window().move(pos)
        if event.type() == 10 or event.type() == 11:# QtCore.QEvent.Enter or QtCore.QEvent.Leave
            if source == self.CloseButton:
                if event.type() == QtCore.QEvent.Enter:#HoverMove
                    self.CloseButton.setPalette(self.RedHighlightPalette)
                elif event.type() == QtCore.QEvent.Leave:#HoverLeave
                    self.CloseButton.setPalette(self.palette())
            elif source == self.MaximizeButton:
                if event.type() == QtCore.QEvent.Enter:
                    self.MaximizeButton.setAutoRaise(False)
                elif event.type() == QtCore.QEvent.Leave:
                    self.MaximizeButton.setAutoRaise(True)
            elif source == self.MinimizeButton:
                if event.type() == QtCore.QEvent.Enter:
                    self.MinimizeButton.setAutoRaise(False)
                elif event.type() == QtCore.QEvent.Leave:
                    self.MinimizeButton.setAutoRaise(True)
        elif self.IncludeErrorButton and source is self.Error_Label and event.type() == QtCore.QEvent.Enter: #==10
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),self.Error_Label.toolTip(),self.Error_Label)
        return super(TopBar_Widget, self).eventFilter(source, event)

    def mousePressEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            #if self.window().isMaximized() or self.window().isFullScreen(): # If moving the window while in fullscreen or maximized make it normal first
            #    corPos = self.window().geometry().topRight()
            #    self.window().showNormal()
            #    self.window().AWWF_CentralWidget.showFrame()
            #    QtWidgets.QApplication.instance().processEvents()
            #    self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
            self.moving = True
            self.offset = event.globalPos()-self.window().geometry().topLeft()

    def mouseReleaseEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.MoveMe.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                try:
                    screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry()
                except: #For backwards compatibility
                    screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                    screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode(): # MAYBE: Make this behaviour for advanced mode toggable in the options if a user never wants this
                        self.window().resize(Full_X, Half_Y, autoscale=False)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="TopBar_Widget.mouseReleaseEvent")

    def mouseMoveEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if self.moving:
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                # TODO: Make normalizing the window relative to the previous and current window width to keep the cursor on the window regardless wether clicking right or left
                self.MaximizeButton.setText("🗖")
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)

class StatusBar_Widget(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar_Widget, self).__init__(parent)
        self.WindowNameLabel = QtWidgets.QLabel(self)
        self.addPermanentWidget(self.WindowNameLabel)

    def setWindowTitle(self, WindowTitle):
        # type: (str) -> None
        WindowTitle += " "
        self.WindowNameLabel.setText(WindowTitle)

class Window_Frame_Widget(QtWidgets.QFrame): #IMPROVE: Maybe the resizing and moving could be made more elegant than that elif block by using matrices? Also the code is currently duplicated in some places. That should be made more elegant as well.
    mPos: QtCore.QPoint
    global_mPos: QtCore.QPoint
    offset: QtCore.QPoint
    storeWidth: int
    storeHeight: int
    adjXFac: int
    adjYFac: int
    transXFac: int
    transYFac: int
    FrameEnabled: bool
    moving: bool
    Direction: str
    def __init__(self, parent = None):
        super(Window_Frame_Widget, self).__init__(parent)
        self.FrameEnabled = False
        self.moving = False
        self.setMouseTracking(True)
        
        
        # Resizing was inspired by an answer to https://stackoverflow.com/questions/37047236/qt-resizable-and-movable-main-window-without-title-bar (16.12.2019)
        self.offset = None
        self.mPos = None # For dragging, relative mouse position to upper left
        self.global_mPos = None # For resizing, global mouse position at mouse click
        #self.rs_mPos = None # for resizing #CLEANUP: Remove this as it is not needed
        self.storeWidth = 0 # fix window size at mouseclick for resizing
        self.storeHeight = 0
        self.adjXFac = 0
        self.adjYFac = 0
        self.transXFac = 0
        self.transYFac = 0
        self.Direction = "D"
    
    def showFrame(self):
        self.FrameEnabled = True
        self.setFrameStyle(self.Box | self.Sunken)
        self.setLineWidth(2)
        #self.setMidLineWidth(3)

    def hideFrame(self):
        self.FrameEnabled = False
        self.setFrameStyle(self.NoFrame)
        #self.setLineWidth(1)
        #self.setMidLineWidth(3)

    def mousePressEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if (event.button() == QtCore.Qt.LeftButton):
            # Coordinates have been mapped such that the mouse position is relative to the upper left of the main window
            self.mPos = event.globalPos() - self.window().frameGeometry().topLeft()

            # At the moment of mouse click, capture global position and lock the size of window for resizing
            self.global_mPos = event.globalPos()
            self.storeWidth = self.width()
            self.storeHeight= self.height()
            self.offset = event.globalPos()-self.window().geometry().topLeft() # event.globalPos()-frameGeometry().topLeft()
            rs_size = 20
            # Big if statement checks if the mouse is near the frame and if the frame is enabled
            if ( ((abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size) or
                    (abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size)or
                    (abs(self.offset.y()) < rs_size) or
                    (abs(self.offset.y()) <rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size))
                    and self.FrameEnabled):
                # Use 2x2 matrix to adjust how much you are resizing and how much you
                # are moving. Since the default coordinates are relative to upper left
                # You cannot just have one way of resizing and moving the window.
                # It will depend on which corner you are referring to
                # 
                # self.adjXFac and self.adjYFac are for calculating the difference between your
                # current mouse position and where your mouse was when you clicked.
                # With respect to the upper left corner, moving your mouse to the right
                # is an increase in coordinates, moving mouse to the bottom is increase etc.
                # However, with other corners this is not so and since I chose to subtract
                # This difference at the end for resizing, self.adjXFac and self.adjYFac should be
                # 1 or -1 depending on whether moving the mouse in the x or y directions
                # increases or decreases the coordinates respectively. 
                # 
                # self.transXFac self.transYFac is to move the window over. Resizing the window does not
                # automatically pull the window back toward your mouse. This is what
                # transfac is for (translate window in some direction). It will be either
                # 0 or 1 depending on whether you need to translate in that direction.
                #
                # Initialize Matrix:
                # Upper left corner section
                if ( (abs(self.offset.x()) < rs_size and abs(self.offset.y()) < rs_size)):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                    # Upper left. No flipping of axis, no translating window
                    self.adjXFac=1
                    self.adjYFac=1
                    self.transXFac=0
                    self.transYFac=0
                    self.Direction = "D"
                    self.moving = True
                # Upper right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y()) <rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    # upper right. Flip displacements in mouse movement across x axis
                    # and translate window left toward the mouse
                    self.adjXFac=-1
                    self.adjYFac=1
                    self.transXFac=1
                    self.transYFac=0
                    self.Direction = "D"
                    self.moving = True
                # Lower left corner section
                elif(abs(self.offset.x()) < rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    # lower left. Flip displacements in mouse movement across y axis
                    # and translate window up toward mouse
                    self.adjXFac=1
                    self.adjYFac=-1
                    self.transXFac=0
                    self.transYFac=1
                    self.Direction = "D"
                    self.moving = True
                # Lower right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                    # lower right. Flip mouse displacements on both axis and
                    # translate in both x and y direction left and up toward mouse.
                    self.adjXFac=-1
                    self.adjYFac=-1
                    self.transXFac=1
                    self.transYFac=1
                    self.Direction = "D"
                    self.moving = True
                
                
                # Upper Side
                elif abs(self.offset.y()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                    self.adjXFac=-1#1
                    self.adjYFac=1
                    self.transXFac=1#0
                    self.transYFac=0
                    self.Direction = "y"
                    self.moving = True
                # Lower side
                elif abs(self.offset.y()) > self.height()-rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                    self.adjXFac=-1
                    self.adjYFac=-1
                    self.transXFac=1
                    self.transYFac=1
                    self.Direction = "y"
                    self.moving = True
                # Right Side
                elif abs(self.offset.x()) > self.width()-rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    self.adjXFac=-1
                    self.adjYFac=-1#1
                    self.transXFac=1
                    self.transYFac=1#0
                    self.Direction = "x"
                    self.moving = True
                # Left Side
                elif abs(self.offset.x()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    self.adjXFac=1
                    self.adjYFac=-1
                    self.transXFac=0
                    self.transYFac=1
                    self.Direction = "x"
                    self.moving = True
            
            event.accept()

    def mouseReleaseEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        self.moving = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def mouseMoveEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if self.moving:
            #if (event.buttons()==QtCore.Qt.LeftButton ):
            if self.Direction == "D":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth-adjXDiff, self.storeHeight-adjYDiff, autoscale=False)
            elif self.Direction == "y":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth, self.storeHeight-adjYDiff, autoscale=False)
            elif self.Direction == "x":
                # Calculation of displacement. self.adjXFac=1 means normal displacement
                # self.adjXFac=-1 means flip over axis     
                adjXDiff = self.adjXFac*(event.globalPos().x() - self.global_mPos.x())
                adjYDiff = self.adjYFac*(event.globalPos().y() - self.global_mPos.y())
                # if transfac is 1 then movepoint of mouse is translated     
                movePoint = QtCore.QPoint(self.mPos.x() - self.transXFac*adjXDiff, self.mPos.y()-self.transYFac*adjYDiff)
                self.window().move(event.globalPos()-movePoint)
                self.window().resize(self.storeWidth-adjXDiff, self.storeHeight, autoscale=False)
            event.accept()
        else:
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            rs_size = 20
            if ( ((abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size) or
                    (abs(self.offset.x()) < rs_size) or
                    (abs(self.offset.x()) > self.width()-rs_size)or
                    (abs(self.offset.y()) < rs_size) or
                    (abs(self.offset.y()) <rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size) or
                    (abs(self.offset.y())> self.height()-rs_size))
                    and self.FrameEnabled):
                # Upper left corner section
                if ( (abs(self.offset.x()) < rs_size and abs(self.offset.y()) < rs_size)):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                # Upper right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y()) <rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                    self.Direction = "D"
                # Lower left corner section
                elif(abs(self.offset.x()) < rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeBDiagCursor)
                # Lower right corner section
                elif(abs(self.offset.x()) > self.width()-rs_size and abs(self.offset.y())> self.height()-rs_size):
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                
                
                # Upper Side
                elif abs(self.offset.y()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                # Lower side
                elif abs(self.offset.y()) > self.height()-rs_size:
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                # Right Side
                elif abs(self.offset.x()) > self.width()-rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                # Left Side
                elif abs(self.offset.x()) < rs_size:
                    self.setCursor(QtCore.Qt.SizeHorCursor)
                    
            # In any move event if it is not in a resize region use the default cursor
            else:
                self.setCursor(QtCore.Qt.ArrowCursor)

    def leaveEvent(self,event):
        self.setCursor(QtCore.Qt.ArrowCursor)

class MMenuBar(QtWidgets.QMenuBar): # Moveable Menu Bar
    def __init__(self, parent=None):
        super(MMenuBar, self).__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.moving = False
        self.offset = 0
        self.setMouseTracking(True)

    def mousePressEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if event.button() == QtCore.Qt.LeftButton and self.actionAt(event.pos())==None and self.moving == False and self.activeAction()==None:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.moving = True
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().AWWF_CentralWidget.moving = False
            event.accept()
        else:
            self.moving = False
        super(MMenuBar, self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.window().AWWF_CentralWidget.moving = False
        if event.button() == QtCore.Qt.LeftButton and self.moving:
            self.moving = False
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                try:
                    screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry()
                except: #For backwards compatibility
                    screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                    screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode():
                        self.window().resize(Full_X, Half_Y, autoscale=False)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MMenuBar.mouseReleaseEvent")
        else:
            self.moving = False
            super(MMenuBar, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if self.moving:
            event.accept()
            self.window().AWWF_CentralWidget.moving = False
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                try:
                    self.window().TopBar.MaximizeButton.setText("🗖")
                except:
                    pass
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)
        else:
            if self.actionAt(event.pos())!=None:
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            super(MMenuBar, self).mouseMoveEvent(event)

class MTabWidget(QtWidgets.QTabWidget): # Moveable Tab Widget
    def __init__(self, parent=None):
        super(MTabWidget, self).__init__(parent)
        #self.TabBar = MTabBar(self)
        #self.setTabBar(self.TabBar)
        ####self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabBar().setUsesScrollButtons(True)
        self.moving = False
        self.offset = 0
        self.setMouseTracking(True)

    def mousePressEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        if event.button() == QtCore.Qt.LeftButton and self.moving == False and self.childAt(event.pos())==None:
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.moving = True
            self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().AWWF_CentralWidget.moving = False
        else:
            self.moving = False
        super(MTabWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.window().AWWF_CentralWidget.moving = False
        if event.button() == QtCore.Qt.LeftButton and self.moving:
            self.moving = False
            pos = self.window().pos()
            #if (pos.x() < 0):
            #    pos.setX(0)
            #    self.window().move(pos)
            if (pos.y() < 0):
                pos.setY(0)
                self.window().move(pos)
            # If the mouse is in a corner or on a side let the window fill this corner or side of the screen
            try:
                Tolerance = 5
                eventPos = event.globalPos()
                try:
                    screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry()
                except: #For backwards compatibility
                    screenNumber = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
                    screen = QtWidgets.QApplication.desktop().availableGeometry(screenNumber)
                Half_X = (screen.bottomRight().x()-screen.topLeft().x())/2+1
                Full_X = (screen.bottomRight().x()-screen.topLeft().x())+1
                Half_Y = (screen.bottomRight().y()-screen.topLeft().y())/2+1
                Full_Y = (screen.bottomRight().y()-screen.topLeft().y())+1
                BottomMax = screen.bottomLeft().y()
                RightMax = screen.bottomRight().x()
                TopMax = screen.topLeft().y()
                LeftMax = screen.topLeft().x()
                #if (pos.y() > BottomMax): # If Bottom Side gets removed this must be turned on to make it impossible for the window to get lost behind the task bar
                #    pos.setY(BottomMax-50)
                #    self.window().move(pos)
                # Top Left
                if eventPos.x() <= Tolerance + LeftMax and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Bottom Left
                elif eventPos.x() <= Tolerance + LeftMax and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
                # Top Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() <= Tolerance + TopMax:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Bottom Right
                elif eventPos.x() >= RightMax-Tolerance and eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Half_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomRight(screen.bottomRight())
                    self.window().move(frameGm.topLeft())
                # Left Side
                elif eventPos.x() <= Tolerance + LeftMax:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopLeft(screen.topLeft())
                    self.window().move(frameGm.topLeft())
                # Right Side
                elif eventPos.x() >= RightMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveTopRight(screen.topRight())
                    self.window().move(frameGm.topLeft())
                # Top Side
                elif eventPos.y() <= Tolerance + TopMax:
                    if advancedMode():
                        self.window().resize(Full_X, Half_Y, autoscale=False)
                        frameGm = self.window().frameGeometry()
                        frameGm.moveTopRight(screen.topRight())
                        self.window().move(frameGm.topLeft())
                    else:
                        self.window().showMaximized()
                # Bottom Side
                elif eventPos.y() >= BottomMax-Tolerance:
                    self.window().resize(Full_X, Half_Y, autoscale=False)
                    frameGm = self.window().frameGeometry()
                    frameGm.moveBottomLeft(screen.bottomLeft())
                    self.window().move(frameGm.topLeft())
            except:
                NC(exc=sys.exc_info(),win=self.window().windowTitle(),func="MTabWidget.mouseReleaseEvent")
        else:
            self.moving = False
            super(MTabWidget, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self,event):
        # type: (QtGui.QMouseEvent) -> None # Only registers if mouse is pressed...
        if self.moving:
            event.accept()
            self.window().AWWF_CentralWidget.moving = False
            if (self.window().isMaximized() or self.window().isFullScreen()): # If moving the window while in fullscreen or maximized make it normal first
                try:
                    self.window().TopBar.MaximizeButton.setText("🗖")
                except:
                    pass
                corPos = self.window().geometry().topRight()
                self.window().showNormal()
                self.window().AWWF_CentralWidget.showFrame()
                QtWidgets.QApplication.instance().processEvents()
                self.window().move(corPos-self.window().geometry().topRight()+self.window().geometry().topLeft())
                self.offset = event.globalPos()-self.window().geometry().topLeft()
            self.window().move(event.globalPos()-self.offset)
        else:
            #if self.childAt(event.pos())==None:
            #    self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            #else: # Does not work... Maybe all widgets need self.setMouseTracking(True) ?
            #    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            super(MTabWidget, self).mouseMoveEvent(event)


# class MTabBar(QtWidgets.QTabBar): # Moveable Tab Bar # Does not work since the TabBar is only the space of the tab names but not the free space next to the names...
 #    def __init__(self, parent=None):
 #        super(MTabBar, self).__init__(parent)
 #        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #        self.moving = False
 #        self.setMouseTracking(True)
 #        self.offset = 0
 #
 #    def mousePressEvent(self,event):
 #        if event.button() == QtCore.Qt.LeftButton and self.tabAt(event.pos())==None and self.moving == False:
 #            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
 #            self.moving = True
 #            self.offset = event.globalPos()-self.window().geometry().topLeft()
 #        else:
 #            self.moving = False
 #        super(MTabBar, self).mousePressEvent(event)
 #
 #    def mouseReleaseEvent(self,event):
 #        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #        if event.button() == QtCore.Qt.LeftButton and self.moving:
 #            self.moving = False
 #            pos = self.window().pos()
 #            #if (pos.x() < 0):
 #            #    pos.setX(0)
 #            #    self.window().move(pos)
 #            if (pos.y() < 0):
 #                pos.setY(0)
 #                self.window().move(pos)
 #        else:
 #            self.moving = False
 #            super(MTabBar, self).mouseReleaseEvent(event)
 #
 #    def mouseMoveEvent(self,event):
 #        if self.moving:
 #            self.window().move(event.globalPos()-self.offset)
 #        else:
 #            if self.tabAt(event.pos())!=None:
 #                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
 #            else:
 #                self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 #            super(MTabBar, self).mouseMoveEvent(event)


#endregion

