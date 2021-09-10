#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
from ._AGeWindows import *
from ._AGeApp import *
#endregion Import

#region quick
#TODO: Put this in its own namespace

#TODO: Make a window template that can easily turn a console app into a GUI app
#TODO: Make a function just like QuickSetup that automatically sets up this console window

class QuickWindow(AWWF):
    """
    This window has a simple vertical box layout. \n
    Simply use `addWidget` to add new widgets to the bottom of the layout. \n
    For init simply use `init` as it will be called by the real `__init__` \n
    With this you don't need to call the parents constructor which keeps your code shorter and easier to write. \n
    This window class is only intended for quick mockups. Only use this for quick test windows. \n
    It is not advised to use this for anything permanent or complex.
    """
    def __init__(self):
        super().__init__()
        self.WidgetsList = []
        self.CentralWidget = QtWidgets.QWidget(self)
        self.CentralLayout = QtWidgets.QVBoxLayout(self)
        self.CentralWidget.setLayout(self.CentralLayout)
        self.setCentralWidget(self.CentralWidget)
        self.init()

    def init(self):
        "Reimplement this as your init"
        pass

    def addWidget(self,widget):
        # type: (QtWidgets.QWidget) -> QtWidgets.QWidget
        """
        Adds widget to the bottom of the layout, saves it in a list and returns a reference. \n
        Example: `self.b = self.addWidget(Button(self,"Generate Text",self.generateText))`
        """
        self.WidgetsList.append(widget)
        self.CentralLayout.addWidget(widget)
        return widget

def QuickSetup(window_class,window_name,app_class=None):
    # type: (AWWF,str,typing.Optional[AGeApp]) -> None
    """
    This function takes a window class and automatically creates an app and the window and starts everything. \n
    TODO: Make a better documentation for this function...
    """
    print(cTimeSStr(),": ",window_name,"Window Startup")
    if app_class==None:
        app_class = AGeApp
    app = app_class([])
    #app.setStyle("fusion") #CLEANUP: Already part of the main apps init
    window = window_class()
    window.setWindowTitle(window_name)
    app.setMainWindow(window)
    app.setApplicationName(window_name+"-App")
    print(cTimeSStr(),": ",window_name,"Window Started\n")
    if hasattr(window,"LastOpenState"):
        window.LastOpenState()
    else:
        window.show()
    try: # on windows minimize the console (might work elsewhere, too)
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
    except:
        pass
    try:
        sys.exit(app.exec())
    except:
        sys.exit(app.exec_())
#endregion
