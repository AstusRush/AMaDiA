#CRITICAL: Rename this to AGeMGW for Astus' General Mathematical Graphics Widgets
#CRITICAL: Make a new Astus' General Graphics Widgets that contains more general Widgets unrelated to math
#CRITICAL: Remove the required dependency on ALL non standard libraries except for Qt and make the matplotlib colour features dependent on wheather mpl was imported successfully
#           (also import numpy, scipy and simpy to show their versions if the import was successful (and try to import them to the IDE module so that they can be used easily))
#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
#endregion Import

#region Special Imports

from distutils.spawn import find_executable
if find_executable('latex') and find_executable('dvipng'): LaTeX_dvipng_Installed = True
else : LaTeX_dvipng_Installed = False

import typing

#endregion Special Imports

#CRITICAL: Use matplotlibImported and numpyImported

#CRITICAL: ALL __init__'s of classes derived from QtWidgets.QWidget should have a try-except around everything except `super(MplWidget, self).__init__(parent)` in case something goes wrong with matplotlib

#region MplWidget (Matplotlib Widgets)


class MplWidget(QtWidgets.QWidget):
    """
    Baseclass for all matplotlib widgets. \n
    This class only provides basic recolouring support. \n
    This class does not initialize a canvas. This must be done in derived classes.
    """
    Canvas: FigureCanvasQTAgg
    def __init__(self, parent=None):
        super(MplWidget, self).__init__(parent)
        self.background_Colour = App().BG_Colour
        self.TextColour = App().TextColour
        self.Cycler = App().mplCycler
    
    def setColour(self,BG=None,FG=None,Cycler=None):
        if BG is not None:
            self.background_Colour = BG
        if FG is not None:
            self.TextColour = FG
        if Cycler is not None:
            self.Cycler = Cycler
        self.HexcolourText = '#%02x%02x%02x' % (int(self.TextColour[0]*255),int(self.TextColour[1]*255),int(self.TextColour[2]*255))
        try:
            self.Canvas.figure.set_facecolor(self.background_Colour)
            self.Canvas.figure.set_edgecolor(self.background_Colour)
            for i in self.Canvas.figure.axes:
                try:
                    i.set_facecolor(self.background_Colour)
                    i.set_prop_cycle(self.Cycler)
                except:
                    pass
        except:
            pass #ExceptionOutput(sys.exc_info())
        try:
            self.Canvas.draw()
        except:
            ExceptionOutput(sys.exc_info())
    
    #def eventFilter(self, source, event):
    #    if event.type() == QtCore.QEvent.PaletteChange:
    #        try:
    #            source.setColour(QtWidgets.QApplication.instance().BG_Colour , QtWidgets.QApplication.instance().TextColour)
    #        except:
    #            ExceptionOutput(sys.exc_info())
    #    return super(MplWidget, self).eventFilter(source, event)

# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_2D_Plot(FigureCanvasQTAgg):
    fig: Figure
    figure: Figure
    ax: mplAxes
    def __init__(self):
        #plt.style.use('dark_background')
        if versionParser(matplotlib.__version__) >= versionParser("2.2"):
            self.fig = Figure(constrained_layout = True)
        else:
            self.fig = Figure(tight_layout = True)
        self.fig.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        FigureCanvasQTAgg.updateGeometry(self)

class MplWidget_2D_Plot(MplWidget):
    # Inspired by https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5?noredirect=1&lq=1 from 10.07.2019
    #CRITICAL: Test if the NavBar behaves as intended and still allows for rightclick interaction
    
    Canvas: MplCanvas_2D_Plot
    Layout: QtWidgets.QVBoxLayout
    NavBar: NavigationToolbar2QT
    
    def __init__(self, parent=None, includeNavBar=False):
        super(MplWidget_2D_Plot, self).__init__(parent)
        self.Canvas = MplCanvas_2D_Plot()
        self.Layout = QtWidgets.QVBoxLayout()
        if includeNavBar:
            self.NavBar = NavigationToolbar2QT(self.Canvas, self) #mpl control
            self.Layout.addWidget(self.NavBar) #mpl control
            #self.Canvas.mpl_connect('key_press_event', self.on_key_press) #mpl control
        self.Layout.addWidget(self.Canvas)
        self.setLayout(self.Layout)
        self.layout().setContentsMargins(0,0,0,0)
        if typing.TYPE_CHECKING:
            self.plot = self.Canvas.ax.plot
        else:
            self.plot = lambda *args, **kwargs: self.Canvas.ax.plot(*args, **kwargs)
    
    #def on_key_press(self, event): #mpl control
    #    # implement the default mpl key press events described at
    #    # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
    #    mpl_key_press_handler(event, self.Canvas, self.NavBar)
    
    def setColour(self,BG=None,FG=None,Cycler=None):
        """
        Sets all colours for the plot and redraws it. \n
        #TODO: Improve this documentation
        """
        #CRITICAL: Apply these updates to AMaDiA's Control Window's plots
        super(MplWidget_2D_Plot, self).setColour(BG,FG,Cycler)
        for i in self.Canvas.figure.axes:
            try:
                i.spines['bottom'].set_color(self.TextColour)
                i.spines['left'].set_color(self.TextColour)
                i.xaxis.label.set_color(self.TextColour)
                i.yaxis.label.set_color(self.TextColour)
                i.tick_params(axis='x', colors=self.TextColour)
                i.tick_params(axis='y', colors=self.TextColour)
                try:
                    i.title.set_color(self.TextColour)
                except:
                    pass
                try:
                    legend = i.get_legend()#(facecolor="w",edgecolor="w",frameon=False)
                    if not legend is None:
                        legend.set_frame_on(False)
                        for j in legend.get_texts():
                            j.set_color(self.TextColour)
                except:
                    pass
            except:
                pass
        self.Canvas.draw()
    
    def draw(self, recolour = True):
        """
        Recolours and redraws the canvas. This also resets the colour wheel. \n
        If you do not want this (eg because you use the colours of the plots in an external Legend) call `.draw(recolour=False)`
        """
        if recolour:
            self.setColour()
        else:
            self.Canvas.draw()
    
    def clear(self, re_init_ax = False):
        """
        Clears all axes. \n
        If `re_init_axis` set to `True`: Deletes all axes and reinitializes `ax` as a subplot.
        """
        for i in self.Canvas.figure.axes:
            i.clear()
            if re_init_ax:
                self.Canvas.figure.delaxes(i)
        if re_init_ax:
            self.Canvas.ax = self.Canvas.fig.add_subplot(111)
            self.Canvas.figure.set_tight_layout(tight=True)
        self.Canvas.draw()
    
    # CRITICAL: Add more convenience functions
    #def plot(self,x,y): #CLEANUP: This redirect is now done in the __init__ and even gives the method annotation from mpl in the ide
    #    #CRITICAL: I am pretty sure that plot can take more arguments... (To be clear: That is sarcasm. Add support for all arguments.)
    #    #CRITICAL: Try Except Block
    #    self.Canvas.ax.plot(x,y)
    #    self.Canvas.draw()
    
    def useTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the seperation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']
    
    def plotThings(self,things): #CRITICAL: OVERHAUL THIS CONCEPT AND CHANGE THE ORDER OF THE VALUES IN THE TUPLE AND WRITE DOCUMENTATION
        if len(things) == 0:
            return
        self.clear(True)
        for i in things:
            try:
                #TODO: if any dimension has the length 1 it should be ignored so that [[[1],[2],[3]]] (which has the shape (1,3,1)) can be plotted
                if isinstance(i,(list,tuple)):
                    if len(i) == 2:
                        if isinstance(i[1],str):
                            name = i[1]
                            y = i[0] if isinstance(i[0],np.ndarray) else np.asarray(i[0])
                            x = np.asarray(range(y.shape[0]))
                        else:
                            y = i[1] if isinstance(i[1],np.ndarray) else np.asarray(i[1])
                            x = i[0] if isinstance(i[0],np.ndarray) else np.asarray(i[0])
                            name = ""
                    elif len(i) == 3:
                        y = i[1] if isinstance(i[1],np.ndarray) else np.asarray(i[1])
                        x = i[0] if isinstance(i[0],np.ndarray) else np.asarray(i[0])
                        name = str(i[2])
                else:
                    y = i if isinstance(i,np.ndarray) else np.asarray(i)
                    x = range(y.shape[0])
                    name = ""
                
                #self.ConsoleWidget.dpl()
                if len(y.shape) == 1:
                    if name == "": name = "Unnamed with {} values".format(str(y.shape[0]))
                    self.Canvas.ax.plot(x,y,label=name)
                elif len(y.shape) == 2:
                    if name == "": name = "Unnamed with shape {}".format(str(y.shape))
                    self.Canvas.ax.imshow(y.T,label=name)
                else:
                    NC(2,"MplWidget_2D_Plot can not plot {}-dimensional arrays.".format(str(len(y.shape))))
            except:
                NC(2,"Could not create plot",exc=True)
        
        self.Canvas.ax.legend()
        self.draw()

# -----------------------------------------------------------------------------------------------------------------

class MplCanvas_LaTeX(FigureCanvasQTAgg):
    fig: Figure
    ax: plt.Axes
    def __init__(self,w,h):
        #plt.style.use('dark_background')
        #self.fig = Figure(constrained_layout =True)
        self.fig = Figure(figsize = (w,h),dpi=90)
        self.fig.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        
        #h = [Size.Fixed(1.0), Size.Fixed(4.5)]
        #v = [Size.Fixed(0.7), Size.Fixed(5.)]
        #divider = Divider(self.fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
        
        self.ax = self.fig.add_subplot(111)
        #self.ax = Axes(self.fig, divider.get_position())
        
        self.ax.set_facecolor(QtWidgets.QApplication.instance().BG_Colour)
        self.ax.set_anchor('W')
        self.fig.subplots_adjust(left=0.01)
        self.ax.axis('off')
        
        #self.ax.set_axes_locator(divider.new_locator(nx=1, ny=1))
        #self.fig.add_axes(self.ax)
        
        FigureCanvasQTAgg.__init__(self, self.fig)
        #FigureCanvasQTAgg.setSizePolicy(self, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        #FigureCanvasQTAgg.updateGeometry(self)

class MplWidget_LaTeX(MplWidget): #CRITICAL: Verify (should already be in): Make QWebEngineView optional (determined by whether the import was successful (requires import overhaul))!!! Use NC(unique=True) if QtWebEngineWidgets not importable
    if QtWebEngineWidgetsImported:
        WebCanvas: QtWebEngineWidgets.QWebEngineView
    def __init__(self, parent=None):
        self.QtWebEngineWidgetsImported = QtWebEngineWidgetsImported
        super(MplWidget_LaTeX, self).__init__(parent)
        self.Canvas = MplCanvas_LaTeX(1,1)
        if self.QtWebEngineWidgetsImported:
            self.WebCanvas = QtWebEngineWidgets.QWebEngineView(self)
            self.WebCanvas.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
            #if versionParser(QtCore.qVersion()) < versionParser("5.8"): #Would disable scrolling
            #    self.WebCanvas.setEnabled(False)
            if versionParser(QtCore.qVersion()) >= versionParser("5.8"):
                self.WebCanvas.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.FocusOnNavigationEnabled, False)
        else:
            ncStr  = "Could not load QtWebEngineWidgets.\n"
            ncStr += "If QtWebEngineWidgets is installed the LaTeX widgets offer to display using MathJax which is less resource intensive than MatPlotLib\n"
            ncStr += "and it does not require a LaTeX installation for full LaTeX support (but therefore requires an internet connection).\n"
            ncStr += "If you experience long loading times to display LaTeX or do not want to install LaTeX consider installing QtWebEngineWidgets."
            NC(3,ncStr,exc=QtWebEngineWidgets,unique=True)
        self.StackedWidget = QtWidgets.QStackedWidget(self)
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self.Scroll = QtWidgets.QScrollArea(self)
        self.Scroll.setWidget(self.Canvas)
        
        self.layout().addWidget(self.StackedWidget)
        self.layout().setContentsMargins(0,0,0,0)
        self.StackedWidget.addWidget(self.Scroll)
        if self.QtWebEngineWidgetsImported:
            self.StackedWidget.addWidget(self.WebCanvas)
            
            self.ToggleButton = QtWidgets.QToolButton(self)
            self.ToggleButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
            self.ToggleButton.setMaximumSize(24, 24)
            self.ToggleButton.setFocusPolicy(QtCore.Qt.NoFocus)
            self.ToggleButton.clicked.connect(lambda: self.toggle())
        self.ModeToolTip = "{} is currently used to display LaTeX.\n"+\
                           "Click here to use {} instead.\n"+\
                           "If you have LaTeX installed MatPlotLib is prettier but MathJax is faster.\n"+\
                           "If you don't have LaTeX installed it is recommended to use MathJax.\n"+\
                           "Please note that MathJax requires an internet connection to load the script.\n"+\
                           "(Every time you start AMaDiA the script is loaded when using MathJax for the first time.\n"+\
                           " After this initial loading the internet connection is no longer required while AMaDiA is running.)"
        if LaTeX_dvipng_Installed or not self.QtWebEngineWidgetsImported:
            self.StackedWidget.setCurrentWidget(self.Scroll)
            if self.QtWebEngineWidgetsImported:
                self.ToggleButton.setToolTip(self.ModeToolTip.format("MatPlotLib","MathJax"))
        else:
            self.StackedWidget.setCurrentWidget(self.WebCanvas)
            self.ToggleButton.setToolTip(self.ModeToolTip.format("MathJax","MatPlotLib"))
        
        if self.QtWebEngineWidgetsImported:
            self.WebCanvas.installEventFilter(self)
        self.Canvas.installEventFilter(self)
        self.Scroll.installEventFilter(self)
        self.StackedWidget.installEventFilter(self)
        if self.QtWebEngineWidgetsImported:
            self.ToggleButton.installEventFilter(self)
        
        self.LastCall = False
        self.LaTeX = ""
        self.LaTeX_L = ""
        self.AdditionalActions = {}
        self.StackedWidget.currentChanged.connect(lambda: self._modeSwitched())
        
        pageSource = r"""
                    <html>
                    <body bgcolor=" """+str(App().Palette1.base().color().name(QtGui.QColor.HexRgb))+r""" ">
                    </body></html>
                    """
        if self.QtWebEngineWidgetsImported:
            try:
                self.WebCanvas.setHtml(pageSource)
            except:
                NC(4,"Could not set background colour",exc=sys.exc_info(),input=pageSource,win=self.window().windowTitle(),func=str(self.objectName())+".__init__")
            webEnginePage = self.WebCanvas.page()
            webEnginePage.setBackgroundColor(App().Palette1.base().color())

    def resizeEvent(self, event):
        super(MplWidget_LaTeX, self).resizeEvent(event)
        if self.QtWebEngineWidgetsImported:
            self.ToggleButton.move(self.rect().right() - self.ToggleButton.width(), 0)
            self.ToggleButton.raise_()

    def toggle(self):
        if self.QtWebEngineWidgetsImported:
            if self.StackedWidget.currentWidget() == self.Scroll:
                self.StackedWidget.setCurrentWidget(self.WebCanvas)
            elif self.StackedWidget.currentWidget() == self.WebCanvas:
                self.StackedWidget.setCurrentWidget(self.Scroll)
    
    def _modeSwitched(self):
        if self.QtWebEngineWidgetsImported:
            if self.StackedWidget.currentWidget() == self.Scroll:
                #self.ToggleButton.setText("mpl")
                self.ToggleButton.setToolTip(self.ModeToolTip.format("MatPlotLib","MathJax"))
            elif self.StackedWidget.currentWidget() == self.WebCanvas:
                #self.ToggleButton.setText("MathJax")
                self.ToggleButton.setToolTip(self.ModeToolTip.format("MathJax","MatPlotLib"))
            self.ToggleButton.raise_()
        if self.LastCall != False:
            self.displayRaw(*self.LastCall)
            
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        try:
            if event.type() == 82 and self.LaTeX != "": # QtCore.QEvent.ContextMenu
                menu = self._init_context_actions(QtWidgets.QMenu())
                cursor = QtGui.QCursor()
                menu.setPalette(self.palette())
                menu.setFont(self.font())
                menu.exec_(cursor.pos())
                return True
            return super(MplWidget_LaTeX, self).eventFilter(source, event)
        except:
            NC(lvl=1,exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".(MplWidget_LaTeX).eventFilter",input=str(event))
            return super(MplWidget_LaTeX, self).eventFilter(source, event)
    
    def _init_context_actions(self,menu):
        # type: (QtWidgets.QMenu) -> QtWidgets.QMenu
        """Adds self.AdditionalActions and standard actions to menu and returns it"""
        for t,a in self.AdditionalActions.items():
            action = menu.addAction(t)
            action.triggered.connect(a)
        if self.LaTeX != self.LaTeX_L:
            action = menu.addAction('Copy LaTeX (without format)')
            action.triggered.connect(self.action_Copy_LaTeX)
        action = menu.addAction('Copy LaTeX')
        action.triggered.connect(self.action_Copy_LaTeX_L)
        if self.StackedWidget.currentWidget() == self.Scroll and App().AGeLibPathOK:
            action = menu.addAction('Save LaTeX as png')
            action.triggered.connect(self.action_Save_Picture)
        return menu
    
    def action_Copy_LaTeX(self):
        try:
            QtWidgets.QApplication.clipboard().setText(self.LaTeX)
        except:
            NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX")
    
    def action_Copy_LaTeX_L(self):
        try:
            QtWidgets.QApplication.clipboard().setText(self.LaTeX_L)
        except:
            NC(2,"Could not copy LaTeX",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Copy_LaTeX_L")

    def action_Save_Picture(self):
        try:
            Filename = cTimeFullStr("-")
            Filename += ".png"
            Filename = os.path.join(App().PictureFolderPath,Filename)
            try:
                print(Filename)
                self.Canvas.fig.savefig(Filename , facecolor=App().BG_Colour , edgecolor=App().BG_Colour )
            except:
                NC(lvl=1,msg="Could not save LaTeX: ",exc=sys.exc_info(),func=str(self.objectName())+".action_Save_Picture",win=self.window().windowTitle(),input=Filename)
            else:
                NC(3,"Saved LaTeX as: {}".format(Filename),func=str(self.objectName())+".action_Save_Picture",win=self.window().windowTitle(),input=Filename)
        except:
            NC(2,"Could not save LaTeX as png",exc=sys.exc_info(),win=self.window().windowTitle(),func=str(self.objectName())+".action_Save_Picture")

    def setColour(self,BG=None,FG=None,Cycler=None):
        super(MplWidget_LaTeX, self).setColour(BG,FG,Cycler)
        if self.QtWebEngineWidgetsImported:
            webEnginePage = self.WebCanvas.page()
            webEnginePage.setBackgroundColor(App().Palette1.base().color())
        if self.LastCall != False:
            #self.displayRaw(self.LastCall[0],self.LastCall[1],self.LastCall[2],self.LastCall[3])
            self.displayRaw(*self.LastCall)
        else:
            try:
                self.Canvas.draw()
            except:
                pass
            if self.QtWebEngineWidgetsImported:
                try:
                    pageSource = r"""
                                <html>
                                <body bgcolor=" """+str(App().Palette1.base().color().name(QtGui.QColor.HexRgb))+r""" ">
                                </body></html>
                                """
                    self.WebCanvas.setHtml(pageSource)
                except:
                    pass
    
    def useTeX(self,TheBool):
        # This Method changes the settings for not only one but all widgets...
        # This makes the clear function of the plotter slow if the LaTeX display has been used in LaTeX mode directly before
        # It could help to separate the two widgets into two files...
        # ... but it is also possible that this setting is global not only for the file but the program which would make the separation a massive waste of time...
        # Maybe test this in a little testprogram to not waste that much time...
        
        matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        #Both seem to do the same:
        matplotlib.rcParams['text.usetex'] = TheBool
        matplotlib.rcParams['text.latex.preamble'] = r"\usepackage[utf8]{inputenc} \usepackage{amsmath}"
        plt.rc('text', usetex=TheBool)
        return matplotlib.rcParams['text.usetex']

    def preloadLaTeX(self):
        try:
            self.useTeX(True)
            self.Canvas.ax.clear()
            self.Canvas.ax.set_title(r"$\frac{2 \cdot 3 \int \left(x + 2 x\right)\, dx}{6}$",
                        loc = "left",
                        y=(1.15-(20/5000)),
                        horizontalalignment='left',
                        verticalalignment='top',
                        fontsize=20,
                        color = "white"
                        ,bbox=dict(boxstyle="round", facecolor="black",
                        ec="0.1", pad=0.1, alpha=0)
                        )
            self.Canvas.ax.axis('off')
            self.Canvas.draw()
            time.sleep(0.1)
            self.Canvas.ax.clear()
            self.Canvas.ax.axis('off')
            self.Canvas.draw()
            self.useTeX(False)
        except:
            try:
                self.useTeX(False)
            except:
                ExceptionOutput(sys.exc_info())
            ExceptionOutput(sys.exc_info())
    
    def display(self, Text, Font_Size = None, Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        # Reminder: You can set Usetex for each individual text object. Example:
        # plt.xlabel('$x$', usetex=True)
        umlautList = [["Ä","A"],["ä","a"],["Ö","O"],["ö","o"],["Ü","U"],["ü","u"]]
        Text_L = Text
        for i in umlautList:
            Text_L = Text_L.replace(i[0],r"\text{\""+i[1]+r"}")
        Lines_L = Text_L.splitlines()
        Lines_N = Text.splitlines()
        Text_L = r" \begin{alignat*}{2} & " + r" \\ & ".join(Lines_L) + r" \end{alignat*}  "
        Text_N = "$" + "$\n$".join(Lines_N) + "$"
        rtn = self.displayRaw(Text_L, Text_N, Font_Size=Font_Size,Use_LaTeX=Use_LaTeX)
        self.LaTeX = Text
        return rtn
        
    def displayRaw(self, Text_L, Text_N, Font_Size = None, Use_LaTeX = False):
        """Returns a notification with all relevant information"""
        if Font_Size is None:
            Font_Size = App().font().pointSize()
        self.LaTeX_L = Text_L
        self.LaTeX_N = Text_N
        self.Font_Size = Font_Size * 2
        if self.LastCall != [Text_L, Text_N, Font_Size, Use_LaTeX]:
            self.LastCall = [Text_L, Text_N, Font_Size, Use_LaTeX]
            self.LaTeX = self.LaTeX_L #Ensures that self.LaTeX is set when DisplayRaw is called directly but is overwritten if DisplayRaw was called by Display
        Notification = NC(lvl=0,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
        if self.StackedWidget.currentIndex() == 0:
            try:
                success = False
                if Use_LaTeX:
                    self.useTeX(True)
                    self.Text = self.LaTeX_L
                else:
                    self.useTeX(False)
                    try:
                        self.Text = self.LaTeX_N.replace(r"\limits","")
                    except:
                        self.Text = self.LaTeX_N
                
                if Use_LaTeX:
                    try:
                        self._display(self.Text)
                    except:
                        Notification = NC(4,"Could not display in Mathmode",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
                    else:
                        success = True
                if Use_LaTeX and not success:
                    self.Text = self.LaTeX_N
                    try:
                        self._display(self.Text)
                    except:
                        Notification = NC(2,"Could not display with LaTeX. Displaying with matplotlib instead.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
                    else:
                        success = True
                if not success:
                    try:
                        self.Text = self.LaTeX_N.replace(r"\limits","")
                    except:
                        self.Text = self.LaTeX_N
                    self.useTeX(False)
                    try:
                        self._display(self.Text)
                    except:
                        Notification = NC(1,"Could not display at all.",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
                        self.useTeX(False)
                        if Use_LaTeX:
                            ErrorText = "The text can't be displayed. Please send your input and a description of your problem to the developer"
                        else:
                            ErrorText = "The text can't be displayed. Please note that many things can't be displayed without LaTeX Mode."
                            if not LaTeX_dvipng_Installed:
                                ErrorText += "\n Please install LaTeX (and dvipng if it is not already included in your LaTeX distribution) or use the MathJax display mode"
                        try:
                            self._display(ErrorText)
                        except:
                            Notification = NC(1,"Critical Error: MatPlotLib Display seems broken. Could not display anything",exc=sys.exc_info(),input=ErrorText,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
            except:
                Notification = NC(1,"Critical Error",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
            finally:
                self.useTeX(False)
                return Notification
        elif self.StackedWidget.currentIndex() == 1 and self.QtWebEngineWidgetsImported:
            pageSource = r"""
                        <html><head>
                        <script>
                        MathJax = {
                            options: {
                                renderActions: {
                                    addMenu: [0, '', '']
                                }
                            }
                        };
                        </script>
                        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
                        </script></head>
                        <style type="text/css">
                        ::-webkit-scrollbar {width: 6px; height: 4px; background: """+str(App().Palette1.base().color().name(QtGui.QColor.HexRgb))+r"""; }
                        ::-webkit-scrollbar-thumb { background-color: """+str(App().Palette1.alternateBase().color().name(QtGui.QColor.HexRgb))+r"""; -webkit-border-radius: 1ex; }
                        </style>
                        <body bgcolor=" """+str(App().Palette1.base().color().name(QtGui.QColor.HexRgb))+r""" ">
                        <p><mathjax style="font-size:2.3em; color: """+str(App().palette().text().color().name(QtGui.QColor.HexRgb))+\
                        r""";">"""+Text_L+r"""</mathjax></p>
                        </body></html>
                        """ #MAYBE: Make the script offline if possible...
                        #<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
            try:
                self.WebCanvas.setHtml(pageSource)
            except:
                Notification = NC(4,"Could not display LaTeX with mathjax",exc=sys.exc_info(),input=self.Text,win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)
            return Notification
        else:
            return NC(4,"Mode {} is not implemented or supported".format(str(self.StackedWidget.currentIndex())),input="Mode: {}".format(str(self.StackedWidget.currentIndex())),win=self.window().windowTitle(),func=str(self.objectName())+".DisplayRaw",send=False)

    def _display(self,text):
        """
        This is a help function used by DisplayRaw to draw on the mpl canvas.
        """
        self.Canvas.ax.clear() # makes Space for the new text
        y = 1.15-(self.Font_Size/5000) # For Figure(figsize = (100,100),dpi=90)
        #y = 1.195-(self.Font_Size/180) # For Figure(figsize = (100,10),dpi=90)
        t = self.Canvas.ax.set_title(text,
                                    loc = "left",
                                    #x=-0.12,
                                    y=y,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    fontsize=self.Font_Size,
                                    color = self.TextColour
                                    ,bbox=dict(boxstyle="round", facecolor=self.background_Colour,ec="0.1", pad=0.1, alpha=0)
                                    )
        #
        r = self.Canvas.get_renderer()
        #t = self.Canvas.ax.get_title()
        bb = t.get_window_extent(renderer=r)
        
        x,y = self.Canvas.fig.dpi_scale_trans.inverted().transform((bb.width,bb.height))+self.Canvas.fig.dpi_scale_trans.inverted().transform((0,y))
        self.Canvas.fig.set_size_inches(x+0.4,y+1, forward=True)
        self.Canvas.ax.clear()
        t = self.Canvas.ax.set_title(text,
                                    loc = "left",
                                    x=0.1,
                                    y=y+0.5,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    fontsize=self.Font_Size,
                                    color = self.TextColour,
                                    #bbox=dict(boxstyle="round", facecolor=self.background_Colour,ec="0.1", pad=0.1, alpha=0),
                                    transform = self.Canvas.fig.dpi_scale_trans#.inverted()
                                    )
        #
        self.Canvas.ax.axis('off')
        self.Canvas.draw()
        self.Canvas.adjustSize()
        #self.Scroll.adjustSize()
        #self.adjustSize()

#endregion MplWidget

#region GWidget (Graphic Widgets)
#FEATURE: Make a more performant Plotter Widget using pyqtgraph. This boost in performance should allow plot interactions. See https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/
#FEATURE: All plot widgets should be able to give the coordinates of the mouse cursor to make them easier to read. (This should be toggleable to not interfere with other interactions.)
#MAYBE: Make a plotting widget that can take in any lists and make a plot. This specifically means detecting the dimensions and making a 2D or 3D plot depending on the input

#Web/LaTeX Widget:
 #import sys
 #from PyQt5.QtWebEngineWidgets import QtWebEngineWidgets.QWebEngineView
 #
 #pageSource = r"""
 #             <html><head>
 #             <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
 #             </script></head>
 #             <body bgcolor=" """+str(App().palette().base().color().name(QtGui.QColor.HexRgb))+r""" ">
 #             <p><mathjax style="font-size:2.3em; color: """+str(App().palette().text().color().name(QtGui.QColor.HexRgb))+r"""">$$\displaystyle \frac{2 \cdot 3 \int \left(x + 2 x\right)\, dx}{6} $$</mathjax></p>
 #             </body></html>
 #             """
 #self.webWindow = AWWF()
 #self.webView = QtWebEngineWidgets.QWebEngineView()
 #self.webView.setHtml(pageSource)
 ##self.webView.setUrl(QtCore.QUrl("https://www.google.com"))
 #self.webWindow.setCentralWidget(self.webView)
 #self.webWindow.show()

class GCanvas(QtWidgets.QWidget): # TODO
    def __init__(self, parent=None):
        super(GCanvas, self).__init__(parent)

class GWidget(QtWidgets.QWidget): # TODO
    def __init__(self, parent=None, Canvas=GCanvas):
        super(GWidget, self).__init__(parent)
        
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(3)
        
        self.Canvas = Canvas(self)
        self.layout().addWidget(self.Canvas,0,0)

# -----------------------------------------------------------------------------------------------------------------

        
class GCanvas_Label(GCanvas): # TODO
    def __init__(self, parent=None):
        super(GCanvas_Label, self).__init__(parent)
        
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(3)
        
        self.Canvas = QtWidgets.QLabel(self) # TODO: See https://doc.qt.io/qt-5/qpixmap.html#details and evaluate  QImage, QPixmap, QBitmap and QPicture
        self.Scroll = QtWidgets.QScrollArea(self)
        self.Scroll.setWidget(self.Canvas)
        self.Scroll.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        self.Scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.Scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.Scroll.setWidgetResizable(True)
        self.Scroll.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(self.Scroll,0,0)

    def setPixmap(self, pixmap):
        self.Canvas.setPixmap(pixmap)

class GCanvas_RGB(GCanvas_Label): # TODO
    # Idea: Make a plot with x and y axis for input and a colourmap with r and b values for the output (and make it possible to swap in and output)
    # r and b need a legend telling what r=0 and r=255 means (same for b). Even better: a scale showing this with all the colours and the numbers
    colourDict = {"red":0,"green":1,"blue":2,"none":-1}
    def __init__(self, parent=None):
        super(GCanvas_RGB, self).__init__(parent)
        self.legendSize = 200
        # LegendBoxWidget
        self.LegendBoxWidget = QtWidgets.QWidget(self)
        self.LegendBoxWidget.setLayout(QtWidgets.QGridLayout())
        self.LegendBoxWidget.layout().setContentsMargins(0,0,0,0)
        self.LegendBoxWidget.layout().setSpacing(3)
        self.LegendBoxL1Max = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL1Max,0,1,QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.LegendBoxL1Mid = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL1Mid,1,1,QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.LegendBoxL1Min = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL1Min,2,1,QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.LegendBoxL2Min = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL2Min,3,2,QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.LegendBoxL2Mid = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL2Mid,3,3,QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.LegendBoxL2Max = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxL2Max,3,4,QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.LegendBoxLabel = QtWidgets.QLabel(self)
        self.LegendBoxWidget.layout().addWidget(self.LegendBoxLabel,0,2,3,3,QtCore.Qt.AlignCenter)
        LegendBoxSpacer1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.LegendBoxWidget.layout().addItem(LegendBoxSpacer1,4,0,1,4)
        LegendBoxSpacer2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.LegendBoxWidget.layout().addItem(LegendBoxSpacer2,0,0,4,1)
        self.LegendBoxScroll = QtWidgets.QScrollArea(self)
        self.LegendBoxScroll.setWidget(self.LegendBoxWidget)
        self.LegendBoxScroll.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        self.LegendBoxScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.LegendBoxScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.LegendBoxScroll.setWidgetResizable(True)
        self.LegendBoxScroll.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # LegendBarWidget
        self.LegendBarWidget = QtWidgets.QWidget(self)
        self.LegendBarWidget.setLayout(QtWidgets.QGridLayout())
        self.LegendBarWidget.layout().setContentsMargins(0,0,0,0)
        self.LegendBarWidget.layout().setSpacing(3)
        #
        self.layout().addWidget(self.LegendBoxScroll,0,1)
        self.layout().addWidget(self.LegendBarWidget,0,2)
        #
        self.LegendBoxScroll.setMaximumWidth(max(self.LegendBoxL1Min.width(),self.LegendBoxL1Mid.width(),self.LegendBoxL1Max.width())+max(self.LegendBoxLabel.width(),self.LegendBoxL2Min.width()+self.LegendBoxL2Mid.width()+self.LegendBoxL2Max.width()+12)+10)


    def plot(self,a1=None,a2=None,a3=None,a1c="red",a2c="green",a3c="blue",a1m=None,a2m=None,a3m=None,xyl=None,a1l=None,a2l=None,a3l=None,link1and2=False):
        """
        Plots up to three matrices in the same plot by converting them into colour intensities. \n
        a1, a2 and a3 must have the same dimensions \n
         a1  : numpy Array : One of the arrays \n
         a1c : "red" or "green" or "blue" : colour of a1 \n
         a1m : [float,float] : [min,max] : min and max of a1 \n
         a1l : [float,float,bool] : [min,max,log] : min and max displayed in the legend (in case a1 was modified before) and wether the scaling is logarithmically \n
           or  [str,str,str] : [min,mid,max] : Strings that are displayed in the legend (strings may be empty) \n
         xyl : [float,float,bool,float,float,bool] : [xMin,xMax,xLog,yMin,yMax,yLog] : For x and y axes labels \n
         link1and2 : bool : If True 1 and 2 will be linked. This means for example that 1 is for positive values and 2 is for negative values
        """
        # TODO: xyl=None,a1l=None,a2l=None,a3l=None
        if type(a1) != type(None):
            array = np.zeros(a1.shape+(3,))
        elif type(a2) != type(None):
            array = np.zeros(a2.shape+(3,))
        elif type(a3) != type(None):
            array = np.zeros(a3.shape+(3,))
        else:
            array = np.zeros((400,400,3))
        if type(a1) != type(None):
            if a1m is None:
                a1m = [a1.min(),a1.max()]
            else:
                a1m = np.minimum(a1m, np.full_like(a1m,a1m[1]))
                a1m = np.maximum(a1m, np.full_like(a1m,a1m[0]))
            a1 = (a1-a1m[0])/(a1m[1]-a1m[0])*255
            if self.colourDict[a1c] != -1: array[:,:,self.colourDict[a1c.lower()]] = a1
        if type(a2) != type(None):
            if a2m is None:
                a2m = [a2.min(),a2.max()]
            else:
                a2m = np.minimum(a2m, np.full_like(a2m,a2m[1]))
                a2m = np.maximum(a2m, np.full_like(a2m,a2m[0]))
            a2 = (a2-a2m[0])/(a2m[1]-a2m[0])*255
            if self.colourDict[a2c] != -1: array[:,:,self.colourDict[a2c.lower()]] = a2
        if type(a3) != type(None):
            if a3m is None:
                a3m = [a3.min(),a3.max()]
            else:
                a3m = np.minimum(a3m, np.full_like(a3m,a3m[1]))
                a3m = np.maximum(a3m, np.full_like(a3m,a3m[0]))
            a3 = (a3-a3m[0])/(a3m[1]-a3m[0])*255
            if self.colourDict[a3c] != -1: array[:,:,self.colourDict[a3c.lower()]] = a3
        self.display(array)
        self._makeLegend(a1=a1,a2=a2,a3=a3,a1c=a1c,a2c=a2c,a3c=a3c,a1m=a1m,a2m=a2m,a3m=a3m,a1l=a1l,a2l=a2l,a3l=a3l,link1and2=link1and2)

    def display(self,array): #TODO: Add https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.pyplot.imshow.html as alternative to QLabel
        """
        Displays the array as a picture \n
         array : numpy array : NxMx3 : The array that is converted to a picture that is then displays \n
        The length of the first 2 dimensions should not be much larger then the pixels of the screen \n
        The 3rd dimension must have a length of 3. These 3 values coorespond to the red, green and blue intensity of the pixel \n
        All values should be in the closed interval [0,255]. Values outside this interval will be regarded as 0 \n
        Note: The array is automatically converted to only contain entries of the type np.uint8
        """
        #self.colour = np.transpose(array, (1,0,2)).copy().astype(np.uint8)
        #self.image = QtGui.QImage(self.colour, self.colour.shape[1], self.colour.shape[0], QtGui.QImage.Format_RGB888)
        self.colour = array.astype(np.uint8)
        self.image = QtGui.QImage(self.colour, self.colour.shape[1], self.colour.shape[0], 3*self.colour.shape[1], QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap(self.image)
        #self.pixmap = self.pixmap.scaled(640,400, QtCore.Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap)

    def _makeLegend(self,a1=None,a2=None,a3=None,a1c="red",a2c="green",a3c="blue",a1m=None,a2m=None,a3m=None,a1l=None,a2l=None,a3l=None,link1and2=False):
        b1 = ( type(a1) != type(None) )
        b2 = ( type(a2) != type(None) )
        b3 = ( type(a3) != type(None) )
        if b1+b2+b3 == 0: # No Input
            self._makeLegend_clear()
        elif b1+b2+b3 == 1 + link1and2 :
            if link1and2: self._makeLegend_bar(a1=a1,a2=a2,a1c=a1c,a2c=a2c,a1m=a1m,a2m=a2m,a1l=a1l,a2l=a2l,link1and2=link1and2)
            elif b1: self._makeLegend_bar(a1=a1,a1c=a1c,a1m=a1m,a1l=a1l)
            elif b2: self._makeLegend_bar(a1=a2,a1c=a2c,a1m=a2m,a1l=a2l)
            elif b3: self._makeLegend_bar(a1=a3,a1c=a3c,a1m=a3m,a1l=a3l)
        elif b1+b2+b3 == 2 + link1and2 :
            if link1and2: self._makeLegend_box(a1=a1,a2=a2,a3=a3,a1c=a1c,a2c=a2c,a3c=a3c,a1m=a1m,a2m=a2m,a3m=a3m,a1l=a1l,a2l=a2l,a3l=a3l,link1and2=link1and2)
            elif b1 and b2: self._makeLegend_box(a1=a1,a2=a2,a1c=a1c,a2c=a2c,a1m=a1m,a2m=a2m,a1l=a1l,a2l=a2l)
            elif b2 and b3: self._makeLegend_box(a1=a2,a2=a3,a1c=a2c,a2c=a3c,a1m=a2m,a2m=a3m,a1l=a2l,a2l=a3l)
            elif b3 and b1: self._makeLegend_box(a1=a1,a2=a3,a1c=a1c,a2c=a3c,a1m=a1m,a2m=a3m,a1l=a1l,a2l=a3l)
        elif b1+b2+b3 == 3:
            self._makeLegend_both(a1=a1,a2=a2,a3=a3,a1c=a1c,a2c=a2c,a3c=a3c,a1m=a1m,a2m=a2m,a3m=a3m,a1l=a1l,a2l=a2l,a3l=a3l)

    def _makeLegend_clear(self):
        pass #TODO

    def _makeLegend_bar(self,a1=None,a2=None,a1c="red",a2c="green",a1m=None,a2m=None,a1l=None,a2l=None,link1and2=False):
        pass #TODO

    def _makeLegend_box(self,a1=None,a2=None,a3=None,a1c="red",a2c="green",a3c="blue",a1m=None,a2m=None,a3m=None,a1l=None,a2l=None,a3l=None,link1and2=False):
        def _round(x,l=5):
            if x == 0: return "0"
            return np.format_float_positional(x,l,fractional=True,trim="-") if 1 < abs(x) < 10000 else np.format_float_scientific(x,l,trim="-")
        if not link1and2:
            array = np.zeros((self.legendSize,self.legendSize,3),dtype=np.uint8)
            if self.colourDict[a1c] != -1: array[:,:,self.colourDict[a1c.lower()]] = np.linspace(np.linspace(0,255,self.legendSize),np.linspace(0,255,self.legendSize),self.legendSize,dtype=np.uint8)
            if self.colourDict[a2c] != -1: array[:,:,self.colourDict[a2c.lower()]] = np.linspace(np.linspace(255,255,self.legendSize),np.linspace(0,0,self.legendSize),self.legendSize,dtype=np.uint8)
            if type(a1l) != list:
                self.LegendBoxL1Min.setText(_round(a1m[0]))
                self.LegendBoxL1Mid.setText(_round(a1m[0]+(a1m[1]-a1m[0])/2))
                self.LegendBoxL1Max.setText(_round(a1m[1]))
            elif len(a1l) == 2 or type(a1l[2]) == bool and a1l[2] == False:
                self.LegendBoxL1Min.setText(_round(a1l[0]))
                self.LegendBoxL1Mid.setText(_round(a1l[0]+(a1l[1]-a1l[0])/2))
                self.LegendBoxL1Max.setText(_round(a1l[1]))
            elif len(a1l) == 3 and type(a1l[2]) == bool and a1l[2] == True:
                self.LegendBoxL1Min.setText("")
                self.LegendBoxL1Mid.setText("")
                self.LegendBoxL1Max.setText("")
                #TODO: DO LOG
                NC(2,"Log for limits is not supported for the legend yet")
            else:
                self.LegendBoxL1Min.setText(str(a1l[0]))
                self.LegendBoxL1Mid.setText(str(a1l[1]))
                self.LegendBoxL1Max.setText(str(a1l[2]))
            if type(a2l) != list:
                self.LegendBoxL2Min.setText(_round(a2m[0]))
                self.LegendBoxL2Mid.setText(_round(a2m[0]+(a2m[1]-a2m[0])/2))
                self.LegendBoxL2Max.setText(_round(a2m[1]))
            elif len(a2l) == 2 or type(a2l[2]) == bool and a2l[2] == False:
                self.LegendBoxL2Min.setText(_round(a2l[0]))
                self.LegendBoxL2Mid.setText(_round(a2l[0]+(a2l[1]-a2l[0])/2))
                self.LegendBoxL2Max.setText(_round(a2l[1]))
            elif len(a2l) == 3 and type(a2l[2]) == bool and a2l[2] == True:
                self.LegendBoxL2Min.setText("")
                self.LegendBoxL2Mid.setText("")
                self.LegendBoxL2Max.setText("")
                #TODO: DO LOG
                NC(2,"Log for limits is not supported for the legend yet")
            else:
                self.LegendBoxL2Min.setText(str(a2l[0]))
                self.LegendBoxL2Mid.setText(str(a2l[1]))
                self.LegendBoxL2Max.setText(str(a2l[2]))
        else:
            pass #TODO: Link
        self.legendImage = QtGui.QImage(array, array.shape[0], array.shape[1], QtGui.QImage.Format_RGB888)
        self.legendPixmap = QtGui.QPixmap(self.legendImage)
        self.LegendBoxLabel.setPixmap(self.legendPixmap)
        QtWidgets.QApplication.instance().processEvents()
        QtWidgets.QApplication.instance().processEvents() # Needs to be called twice for the labels to adjust their size
        self.LegendBoxScroll.setMaximumWidth(max(self.LegendBoxL1Min.width(),self.LegendBoxL1Mid.width(),self.LegendBoxL1Max.width())+max(self.LegendBoxLabel.width(),self.LegendBoxL2Min.width()+self.LegendBoxL2Mid.width()+self.LegendBoxL2Max.width()+12)+10)

    def _makeLegend_both(self,a1=None,a2=None,a3=None,a1c="red",a2c="green",a3c="blue",a1m=None,a2m=None,a3m=None,a1l=None,a2l=None,a3l=None):
        pass #TODO: Make colour rectangle and colour bar and make them swappable

# -----------------------------------------------------------------------------------------------------------------

class GWidget_ComplexPlot(GWidget): # TODO
    def __init__(self, parent=None):
        super(GWidget_ComplexPlot, self).__init__(parent, GCanvas_RGB)

    def plot(self, array, limits): # TODO
        """
        `array` must be 2d numpy array containing complex numbers\n
        `limits` must be list: [real min, real max, imag min, imag max]\n
        The numbers in the `array` are then converted to colours and then display as a rectangle.\n
        A coordinate system will be displayed using the `limits`.
        """
        self.inLimits = limits
        if True:
            i = np.imag(array)
            r = np.real(array)
        else:
            li_max = 3
            li_min = -li_max
            i = np.minimum(np.imag(array),np.full_like(array,li_max))
            i = np.maximum(i             ,np.full_like(array,li_min))
            r = np.minimum(np.real(array),np.full_like(array,li_max))
            r = np.maximum(r             ,np.full_like(array,li_min))
        self.outLimits = [r.min(),r.max(),i.min(),i.max()]
        # TODO: get the average of the matrices and make sure that the extrema don't deviate from them too much. This is important to filter out infinities
        # TODO: Draw inspiration form https://reference.wolfram.com/language/ref/ComplexPlot.html
        # TODO: Add option to only display real or imag and add option to display only real or imag but using red for positive and blue for negative
        # TODO: Add option to show "Betrag und Phase" instead of real and imag
        # TODO: Add option to switch the colours (red green blue)
        # TODO: Add option to highlight 0 with green (or whatever colour is unused)
        #               Add option to only colour in real = 0 or imag = 0 or r+i = 0
        #               It would be cool to have a green line where real and/or imag are/is 0
        self.Canvas.plot(a1=r,a2=i,a1c="red",a2c="blue")
        #self.Canvas.Plot(a1=r,a2=i,c=[0,2],a1l=[r.min(),r.max()],a2l=[i.min(),i.max()])
        NC("array has shape {}.\nThe in limits are {}\nThe out limits are {}".format(array.shape,self.inLimits,self.outLimits))

# -----------------------------------------------------------------------------------------------------------------

#endregion GWidget

