#!/usr/bin/env python3
# Client Version
ClientVersion = "5.6"
# Compatible with Server Version (Or Newer)
ServerVersion = "4.5"
Author = "Robin \'Astus\' Albers"

WindowTitle = "Client v"
WindowTitle+= ClientVersion
WindowTitle+= " by "
WindowTitle+= Author

import sys
sys.path.append('..')
from PyQt5 import QtWidgets,QtCore,QtGui
import socket
import platform
import errno
import os
from AMaDiA_Files.AMaDiA_Functions import common_exceptions, ExceptionOutput
from AMaDiA_Files.AstusChat_Client_UI import Ui_ClientInterface
from AMaDiA_Files import AMaDiA_Colour


bConnected = False


class InputFieldClass(QtWidgets.QLineEdit):
    def __init__(self, type, parent=None):
        super(InputFieldClass, self).__init__(parent)
        #self.setIconSize(QtCore.QSize(124, 124))
        #self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        #self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(InputFieldClass, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            super(InputFieldClass, self).dragMoveEvent(event)

    def dropEvent(self, event):
        global bConnected
        try:
            if bConnected:
                if event.mimeData().hasUrls():
                    url = event.mimeData().text()
                    filename = url[url.rfind("/")+1:]
                    myFile = "S/f/"
                    myFile += filename
                    myFile += "/"
                    
                    if platform.system() == 'Linux':
                        with open(str(os.path.join(event.mimeData().text()[7:])),'r') as text_file:
                            myFile += text_file.read()
                    elif "rt.e-technik.tu-dortmund.de" in url:
                        with open(event.mimeData().text()[5:],'r') as text_file:
                            myFile += text_file.read()
                    else:
                        with open(event.mimeData().text()[8:],'r') as text_file:
                            myFile += text_file.read()
                    
                    sockclient.send(myFile.encode('utf8'))
        except Exception as inst:
            inst
            pass


class MainWindow(QtWidgets.QMainWindow, Ui_ClientInterface): 

    def __init__(self, Palette, TheFontFamily, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.FontFamily = TheFontFamily
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(9)
        self.setFont(newFont)
        (self.Palette , self.BG_Colour , self.TextColour) = Palette
        self.setPalette(self.Palette)

        self.InputField = InputFieldClass(self.centralwidget)
        self.InputField.setAutoFillBackground(True)
        self.InputField.setObjectName("InputField")
        self.gridLayout.addWidget(self.InputField, 3, 2, 1, 11)
        
        #self.retranslateUi(self)
        
        global sockclient
        sockclient = socket.socket()
        #sockclient.settimeout(5)
        
        
        self.RequestChatHistoryBox.setToolTip("Request Chat History on Login")
        self.OnlineList.setPlainText("No Server Connected")
        
        try:
            self.PortField.setText("32005")
            myIP = str(socket.gethostbyname(socket.gethostname()))
        
            if platform.system() == 'Linux':
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                myIP =  str(s.getsockname()[0])
                del s
                
            if platform.system() == 'Linux':
                self.IPField.setText(myIP)
        except:
            pass
            
        #sockclient.bind((myIP,0))
        self.ConnectCheckBox.clicked.connect(self.on_ConnectBoxChanged) 
        self.SendButton.clicked.connect(self.on_sendButtonClicked)
        self.InputField.returnPressed.connect(self.on_sendButtonClicked)
        self.FontSizeBox.valueChanged.connect(self.ChangeFontSize)

    def SetFont(self,Family = None, PointSize = 0):
        pass # TODO: How to handle this? who should be in control?
        #if type(Family) == QtGui.QFont:
        #    self.setFont(Family)
        #else:
        #    if Family == None:
        #        Family = self.font().family()
        #    if type(PointSize) == str:
        #        PointSize = int(PointSize)
        #    if PointSize <= 5:
        #        PointSize = self.font().pointSize()
        #    
        #    font = QtGui.QFont()
        #    font.setFamily(Family)
        #    font.setPointSize(PointSize)
        #    self.setFont(font)

    def Recolour(self, palette, BG_Colour, TextColour):
        self.Palette , self.BG_Colour , self.TextColour = palette, BG_Colour, TextColour
        self.setPalette(self.Palette)
        

    def on_sendButtonClicked(self):
        if self.ConnectCheckBox.isChecked():
            msg = "S"
            msg += self.InputField.text()
            if len(msg)>= 3 and msg[1] == "/":
                if msg[2]=="u" or msg[2]=="f":
                    msg = "S" + msg[3:]
            self.InputField.clear()
            sockclient.send(msg.encode('utf8'))
        else:
            msg = self.InputField.text()
            self.InputField.clear()
            self.ChatDisplay.append(msg)

    def SendFile(self , MyFile):
        if self.ConnectCheckBox.isChecked() :
            sockclient.send(MyFile.encode('utf8'))
    
    
    def on_ConnectBoxChanged(self):
        global sockclient
        global bConnected
        if self.ConnectCheckBox.isChecked() :
            self.ChatDisplay.append("Trying to connect...")
            IP = self.IPField.text()
            Port = int(self.PortField.text())
            try:
                sockclient.connect((IP,Port))
                if self.RequestChatHistoryBox.isChecked() :
                    msg = "requHist"
                    sockclient.send(msg.encode('utf8'))        
                self.ChatDisplay.append("... Connected ...")
                self.NewListener = listener()
                self.NewListener.start()
                self.NewListener.receiver.connect(self.print_message)
                self.NewListener.ConnectCheckBoxUnset.connect(self.ConnectCheckBoxUnset)
                self.NewListener.UserListUpdater.connect(self.UpdateUserList)
            except Exception as inst:
                self.ChatDisplay.append("Could not connect to Server. Maybe IP and Port are wrong")
                #self.ChatDisplay.append(str(inst.args))
                sockclient.close()
                sockclient = socket.socket()
                self.ConnectCheckBox.setChecked(False)
                inst
            finally:
                bConnected = self.ConnectCheckBox.isChecked()
        else:
            msg = "S/d"
            sockclient.send(msg.encode('utf8'))
            sockclient.close()
            self.ChatDisplay.append("... Disconnecting ...")
            self.OnlineList.clear()
            sockclient = socket.socket()
            #sockclient.settimeout(5)
            bConnected = self.ConnectCheckBox.isChecked()


    def ConnectCheckBoxUnset(self):
        global sockclient
        global bConnected
        sockclient.close()
        sockclient = socket.socket()
        #sockclient.settimeout(5)
        self.ConnectCheckBox.setChecked(False)
        bConnected = self.ConnectCheckBox.isChecked()
        

    def print_message(self,msg):
        self.ChatDisplay.append(msg)
        
    def retranslateUi(self, ClientInterface):
        global WindowTitle
        _translate = QtCore.QCoreApplication.translate
        ClientInterface.setWindowTitle(_translate("ClientInterface", WindowTitle))
        self.SendButton.setText(_translate("ClientInterface", "Send"))
        self.ConnectCheckBox.setText(_translate("ClientInterface", "Connect"))
        self.IPField.setPlaceholderText(_translate("ClientInterface", "IP"))
        self.InputField.setPlaceholderText(_translate("ClientInterface", "Message"))
        self.FontText.setText(_translate("ClientInterface", "Set Font Size"))
        self.PortField.setPlaceholderText(_translate("ClientInterface", "Port"))
        self.RequestChatHistoryBox.setToolTip("Request Chat History on Login")
        
    def UpdateUserList(self, msg):
        self.OnlineList.setPlainText(msg)
        
    def ChangeFontSize(self):
        Size = self.FontSizeBox.value()
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(Size)
        self.setFont(newFont)
        self.centralwidget.setFont(newFont)
        
    def wheelEvent(self, QWheelEvent):
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        numDegrees = QWheelEvent.angleDelta().y() / 8
        numSteps = numDegrees / 15
        #self.print_message(str(numSteps))
        if modifiers == QtCore.Qt.ControlModifier:
            #self.print_message(str(modifiers))
            if self.FontSizeBox.value() + numSteps <= self.FontSizeBox.maximum() and self.FontSizeBox.value() + numSteps >= self.FontSizeBox.minimum() :
                self.FontSizeBox.setValue(self.FontSizeBox.value() + numSteps)
                self.ChangeFontSize()
                #self.print_message(str(self.FontSizeBox.value() + numSteps))

 
class listener(QtCore.QThread):
    receiver = QtCore.pyqtSignal(str)
    ConnectCheckBoxUnset = QtCore.pyqtSignal()
    UserListUpdater = QtCore.pyqtSignal(str)
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.exiting = False

    def run(self):
        self.receiver.emit("... Receiving ...")
        try:
            while True:
                Message = sockclient.recv(32767).decode('utf8')
                if len(Message) == 0:
                    raise socket.error()
                elif len(Message) >= 3 and Message[0]=="/" and Message[1]=="u":
                    self.UserListUpdater.emit(Message[3:])
                elif len(Message) >= 3 and Message[0]=="/" and Message[1]=="f":
                    if platform.system() == 'Linux':
                        filename = "Downloads/"
                    else:
                        filename = "Downloads\\"
                    filename += Message.split('/',4)[2]
                    try:
                        os.makedirs("Downloads")
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            pass
                    fliecount = 1
                    brakets = False
                    if "." in filename:
                        #extension = (filename + '.')[:-1]
                        #bareName = (filename + '.')[:-1]
                        extension = filename[filename.rfind("."):]
                        bareName = filename[:filename.rfind(".")]
                    else:
                        bareName = filename
                        extension = ""
                    
                    # This "if" case is usefull if a file is passed back and forth
                    #     between people who change it and you want to track the iteration.
                    # It is however annoying if the file is, for examplce, marked
                    #     with a year in brackets.
                    if bareName.endswith(")"):
                        try:
                            fliecount = int(bareName[bareName.rfind("(")+1:bareName.rfind(")")])
                            bareName = bareName[:bareName.rfind("(")]
                            brakets = True
                        except:
                            pass
                    while True:
                        exists = os.path.isfile(filename)
                        if exists:
                            if brakets:
                                filename = bareName
                                filename += "("
                                filename += str(fliecount)
                                filename += ")"
                                filename += extension
                            else:
                                filename = bareName
                                filename += "(1)"
                                filename += extension
                                brakets = True
                            fliecount += 1
                        else:
                            break
                    with open(filename,'w') as text_file:
                        text_file.write(Message.split('/',4)[3])
                else:
                    self.receiver.emit(Message)
        except:
            self.receiver.emit("... Connection to server lost")
            self.ConnectCheckBoxUnset.emit()
            self.UserListUpdater.emit("No Server Connected")
            self.exiting = True

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")

    form = MainWindow(AMaDiA_Colour.Dark()[0],"Arial")
    form.show()
    sys.exit(app.exec_())
 
if __name__=="__main__":
    main()