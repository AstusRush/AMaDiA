#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
from ._AGeSpecialWidgets import *
from ._AGeIDE import *
#endregion Import


#region Windows

class Notification_Window(AWWF):
    def __init__(self,parent = None):
        try:
            super(Notification_Window, self).__init__(parent)
            self.setWindowTitle("Notifications")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation))
            
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            
            self.NotificationsWidget = NotificationsWidget(self)
            self.NotificationsWidget.setObjectName("NotificationsWidget")
            self.gridLayout.addWidget(self.NotificationsWidget, 0, 0)
            
            self.setCentralWidget(self.centralwidget)
            
            self.setAutoFillBackground(True)
        except:
            ExceptionOutput(sys.exc_info())

class Options_Window(AWWF):
    def __init__(self,parent = None):
        #REMINDER: Add more tabs with other option stuff...
        try:
            super(Options_Window, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Options Window")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
            
            self.centralwidget = QtWidgets.QWidget(self)
            self.centralwidget.setAutoFillBackground(True)
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
            self.gridLayout.setObjectName("gridLayout")
            self.Input_Field = OptionsWidget_1_Appearance(self) #TODO: RENAME
            self.Input_Field.setObjectName("Input_Field")
            
            self.gridLayout.addWidget(self.Input_Field, 0, 0, 0, 0)
            self.gridLayout.setContentsMargins(3,3,3,3)
            self.setCentralWidget(self.centralwidget)
            
            self.setAutoFillBackground(True)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="exec_Window.__init__")

#endregion


