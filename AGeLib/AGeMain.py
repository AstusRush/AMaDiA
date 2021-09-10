#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC, common_exceptions
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeSpecialWidgets import *
from ._AGeGW import *
from ._AGeAWWF import *
from ._AGeWindows import *
from ._AGeApp import *
from ._AGeQuick import *
#endregion Import
 
# ---------------------------------- Bindings for Backwards Compatibility ----------------------------------
MainApp = AGeApp
Main_App = MainApp
AButton = Button
ATextEdit = BaseTextEdit

# TODO: Move this example to its own file and change the docu of the __init__ accordingly
# ---------------------------------- Main Window ----------------------------------
class _AGe_Test_Window(AWWF):
    def __init__(self, MainApp, parent = None):
        super(_AGe_Test_Window, self).__init__(parent, initTopBar=False)
        self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True)
        self.MainApp = MainApp
        self.MainApp.setMainWindow(self)
        self.StandardSize = (906, 634)
        self.resize(*self.StandardSize)
        self.setWindowTitle("AGe Test Window")
        self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_CommandLink))

# ---------------------------------- Main ----------------------------------

if __name__ == "__main__":
    latex_installed, dvipng_installed = find_executable('latex'), find_executable('dvipng')
    if latex_installed and dvipng_installed: print("latex and dvipng are installed --> Using pretty LaTeX Display")
    else:
        if latex_installed and not dvipng_installed: print("latex is installed but dvipng was not detected")
        elif not latex_installed and dvipng_installed: print("dvipng is installed but latex was not detected")
        else: print("latex and dvipng were not detected")
        print("  --> Using standard mpl LaTeX Display (Install both to use the pretty version)")
        print("  --> Selecting MathJax Display as standard LaTeX display method")
    print("Test Window Startup")
    app = AGeApp([])
    app.setStyle("fusion")
    window = _AGe_Test_Window(app)
    app.setMainWindow(window)
    print(datetime.datetime.now().strftime('%H:%M:%S:'),"Test Window Started\n")
    window.show()
    try:
        sys.exit(app.exec())
    except:
        sys.exit(app.exec_())
