#!/usr/bin/env python3
#Server Version
ServerVersion = "5.6"
#Compatible with Client Version (Or Newer)
ClientVersion = "4.3"
Author = "Robin \'Astus\' Albers"

ServerVersionAuthor = "Server v"
ServerVersionAuthor+= ServerVersion
ServerVersionAuthor+= " by "
ServerVersionAuthor+= Author


import sys
sys.path.append('..')
from PyQt5 import QtWidgets, QtCore, QtGui
import socket
import time
import platform
import datetime
from AMaDiA_Files.AMaDiA_Functions import common_exceptions, ExceptionOutput
from AMaDiA_Files.AstusChat_Server_UI import Ui_ServerInterface
from AMaDiA_Files import AMaDiA_Colour

WindowTitle = ServerVersionAuthor

global bConnected
bConnected = False

MakeHistory = False


#--------------------------------------------------------------------------------------------------------------------------
def cTimeStr():
    return str(datetime.datetime.now().strftime('%H:%M : '))

def cTimeSStr():
    return str(datetime.datetime.now().strftime('%H:%M:%S : '))

class NameTaken(Exception):
    def __init__(self, Message):
        self.Message = Message
    def __str__(self):
        return repr(self.Message)
class ExcBanned(Exception):
    def __init__(self, Message):
        self.Message = Message
    def __str__(self):
        return repr(self.Message)

class ConnectionList(QtCore.QThread):
    # Do not do "List = []" here as it would be shared by all objects of
    # this class (even thoough it would probably not matter in this programm
    printer = QtCore.pyqtSignal(str)
    ServerUserListUpdater = QtCore.pyqtSignal()
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.List = []  # creates a new List for each object of this class
        self.Banned = [] # List of Banned IP for current session
        
    def append(self , x):
        self.List.append(x)
        
    def __getitem__(self, key):
        return self.List[key]
    
    def __len__(self):
        return len(self.List)
    
    def CloseAll(self):
        self.SendToAll("THE SERVER IS CLOSING NOW")
        formmsg = cTimeSStr() + "THE SERVER IS CLOSING NOW"
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(formmsg+'\n')
            except:
                pass
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn:
                try:
                    self[i].client_socket.close()
                except Exception as inst:
                    msg = cTimeSStr()+" Exception when Closing connection to ID "
                    msg += str(i)
                    self.printer.emit(msg)
                    self.printer.emit(str(inst.args))
            i+=1

    
    def SendToAll(self,Message):
        # Encode the massage here once to save the time to encode it for every user
        Message = cTimeStr() + Message
        if MakeHistory:
            try:
                with open('ClientChatHistory.txt','a') as text_file:
                    text_file.write(Message+"\n")
            except:
                pass
        Message = Message.encode("utf8")
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn:
                try:
                    self[i].client_socket.send(Message)
                except Exception as inst:
                    self.printer.emit(cTimeSStr()+'user logged off while A message was send. This is nigh impossible')
                    self.printer.emit(str(inst.args))
            i+=1
    
    def SendToAllButOne(self,MyID,Message):
        # Encode the massage here once to save the time to encode it for every user
        Message = cTimeStr() + Message
        if MakeHistory:
            try:
                with open('ClientChatHistory.txt','a') as text_file:
                    text_file.write(Message+"\n")
            except:
                pass
        Message = Message.encode("utf8")
        i=0
        while i < len(self) :
            if i != MyID and self[i].IsLoggedIn:
                try:
                    self[i].client_socket.send(Message)
                except Exception as inst:
                    formmsg = cTimeSStr() + 'user logged off while A message was send. This is nigh impossible'
                    self.printer.emit(formmsg)
                    formmsg = str(inst.args)
                    self.printer.emit(formmsg)
            i+=1
            
    def SendToName(self, Recipient, Message):
        i=0
        bFound = False
        while i < len(self) :
            if self[i].IsLoggedIn and str(self[i].Username) == Recipient:
                self[i].send(Message)
                bFound = True
            i+=1
        if not bFound:
            ErrorMessage = "Could not send Message to User "
            ErrorMessage += str(Recipient)
            ErrorMessage += " as this Name is not logged in"
            formmsg = cTimeSStr() + ErrorMessage
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+ErrorMessage+"\n")
                except:
                    pass
            raise Exception(ErrorMessage)
        
    def SendToIP(self, RecipientIP, Message):
        Message = str(datetime.datetime.now().strftime('%H:%M')) + Message
        Message = Message.encode("utf8")
        i=0
        bFound = False
        while i < len(self) :
            if self[i].IsLoggedIn and str(self[i].IP) == RecipientIP:
                self[i].client_socket.send(Message)
                bFound = True
            i+=1
        if not bFound:
            ErrorMessage = "Could not send Message to IP "
            ErrorMessage += str(RecipientIP)
            ErrorMessage += " as this IP is not logged in"
            formmsg = cTimeSStr() + ErrorMessage
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+ErrorMessage+"\n")
                except:
                    pass
            raise Exception(ErrorMessage)
            
        
    def SendToIPPort(self, RecipientIP , RecipientPort , Message):
        i=0
        bFound = False
        while i < len(self) :
            if self[i].IsLoggedIn and str(self[i].IP) == RecipientIP and str(self[i].Port) == RecipientPort:
                self[i].send(Message)
                bFound = True
            i+=1
        if not bFound:
            ErrorMessage = "Could not send Message to "
            ErrorMessage += str(RecipientIP)
            ErrorMessage += ":"
            ErrorMessage += str(RecipientPort)
            ErrorMessage += " as it is not logged in"
            formmsg = cTimeSStr() + ErrorMessage
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+ErrorMessage+"\n")
                except:
                    pass
            raise Exception(ErrorMessage)
            
    def SendToID(self, RecipientID, Message):
        if RecipientID in range(0,len(self)) and self[RecipientID].IsLoggedIn:
            self[RecipientID].send(Message)
        else:
            ErrorMessage = "Could not send Message to ID "
            ErrorMessage += str(RecipientID)
            ErrorMessage += " as this ID is not logged in"
            formmsg = cTimeSStr() + ErrorMessage
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+ErrorMessage+"\n")
                except:
                    pass
            raise Exception(ErrorMessage)
            
    def CheckUsername(self, Username):
        if len(Username) == 0:
            raise NameTaken("Please actually ENTER SOMETHING instead of bashing return!")
        Username = Username.replace('"','')
        Username = Username.replace('/','')
        Username = Username.replace('>','')
        if len(Username) == 0:
            raise NameTaken("> , \" and / are invalid")
        Username = Username.strip()
        if len(Username) == 0:
            raise NameTaken("Spaces are obviously invalid")
        if len(Username) > 20:
            raise NameTaken("Username too long")
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn and self[i].Username == Username:
                raise NameTaken("Username already taken")
            i+=1
        return Username
    
    def SendToAll_Updated_Client_List(self):
        self.ServerUserListUpdater.emit()
        time.sleep(0.1)
        Message = "/u Users Online:\n\n"
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn:
                Message += self[i]()
                Message += "\n"
            i+=1
        Message = Message.encode("utf8")
        formmsg = cTimeSStr() + "Sending updated User list"
        self.printer.emit(formmsg)
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn:
                try:
                    self[i].client_socket.send(Message)
                except Exception as inst:
                    formmsg = cTimeSStr() + 'user logged off while A message was send. This is nigh impossible'
                    self.printer.emit(formmsg)
                    formmsg = str(inst.args)
                    self.printer.emit(formmsg)
            i+=1
            
    def SendFileToAllButOne(self,ID,MyFile):
        Message = self[ID].Username
        Message += " has send the file \""
        Message += MyFile.split('/',4)[2]
        Message += "\""
        formmsg = cTimeSStr() + Message
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(cTimeSStr()+Message+'\n')
            except:
                pass
        self.SendToAll(Message)
        time.sleep(0.1)
        i=0
        while i < len(self) :
            if self[i].IsLoggedIn and i != ID:
                try:
                    self[i].client_socket.send(MyFile.encode("utf8"))
                except Exception as inst:
                    formmsg = cTimeSStr() + 'user logged off while A message was send. This is nigh impossible'
                    self.printer.emit(formmsg)
                    formmsg = str(inst.args)
                    self.printer.emit(formmsg)
            i+=1
        

    def HandleMessage(self,ID,rawMessage):
        global ServerVersionAuthor
        Commands = LookForCommands(rawMessage)
        if not self[ID].CommandRights:
            Message = self[ID].Username
            Message += ": "
            Message += rawMessage
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            self.SendToAll(Message)
            
        elif Commands[0] == "none":
            Message = self[ID].Username
            Message += ": "
            Message += Commands[2]
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            self.SendToAll(Message)
            
        elif len(Commands[0]) >= 2 and Commands[0][1]=="w":
            try:
                Message = self[ID].Username
                Message += " whispers to "
                if len(Commands[0]) >= 3 and Commands[0] == "/wd":
                    sMessage = "user with ID "
                    sMessage += Commands[1]
                elif len(Commands[0]) >= 3 and Commands[0] == "/wp":
                    sMessage = Commands[1]
                    sMessage += ":"
                    sMessage += Commands[3]
                else:
                    sMessage = Commands[1]
                sMessage += ":"
                sMessage += Commands[2]
                bMessage = "You whisper to "
                bMessage += sMessage
                sMessage = Message + sMessage
                formmsg = cTimeSStr() + sMessage
                self.printer.emit(formmsg)
                if MakeHistory:
                    try:
                        with open('ChatHistory.txt','a') as text_file:
                            text_file.write(cTimeSStr()+sMessage+'\n')
                    except:
                        pass
                Message += "you:"
                Message += Commands[2]
                if Commands[0] == "/w":
                    self.SendToName(Commands[1],Message)
                elif len(Commands[0]) >= 3 and Commands[0] == "/wp":
                    self.SendToIPPort(Commands[1],Commands[3],Message)
                elif len(Commands[0]) >= 3 and Commands[0] == "/wi":
                    self.SendToIP(Commands[1],Message)
                elif len(Commands[0]) >= 3 and Commands[0] == "/wd":
                    self.SendToID(int(Commands[1]),Message)
                self.SendToID(ID,bMessage)
            except Exception as inst:
                try:
                    Message = str(inst.args)
                    self.SendToID(ID,Message)
                except Exception:
                    formmsg = cTimeSStr() + 'user logged off after request'
                    self.printer.emit(formmsg)
            
            
        elif Commands[0]=="l":
            Message = "All logged in Clients are \n"
            i=0
            while i < len(self) :
                if self[i].IsLoggedIn:
                    Message += str(self[i].IP)
                    Message += ":"
                    Message += str(self[i].Port)
                    Message += " as "
                    Message += self[i].Username
                    Message += " with ID "
                    Message += str(self[i].MyID)
                    Message += "\n"
                i+=1
            formmsg = cTimeSStr() + self[ID].Username
            formmsg += " has requested the list of all clients"
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+self[ID].Username+" has requested the list of all clients\n")
                except:
                    pass
            try:
                self.SendToID(ID,Message)
            except Exception:
                formmsg = cTimeSStr() + 'user logged off after request'
                self.printer.emit(formmsg)
            
        elif Commands[0]=="n":
            try:
                NewName = Connections.CheckUsername(Commands[1])
                Message = self[ID].Username
                Message += " has changed their username to "
                Message += NewName
                self[ID].Username = NewName
                formmsg = cTimeSStr() + Message
                self.printer.emit(formmsg)
                if MakeHistory:
                    try:
                        with open('ChatHistory.txt','a') as text_file:
                            text_file.write(cTimeSStr()+Message+'\n')
                    except:
                        pass
                self.SendToAll(Message)
                self.SendToAll_Updated_Client_List()
            except NameTaken as inst:
                try:
                    self.SendToID(ID,inst.Message)
                except Exception:
                    formmsg = cTimeSStr() + 'user logged off after request'
                    self.printer.emit(formmsg)
            
        elif Commands[0]=="d":
            self[ID].IsLoggedIn = False
            self[ID].client_socket.close()
        
        
            
        elif Commands[0]=="f":
            self.SendFileToAllButOne(ID,Commands[2])
            
        elif Commands[0] == "panic":
            Message = "<b>DON'T PANIC </b>" 
            Message += self[ID].Username
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            self.SendToAll(Message)
            
        elif Commands[0] == "scream":
            Message = "<i>" 
            Message += self[ID].Username
            Message += " runs around in circles, screaming!</i>"
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            self.SendToAll(Message)
            
        elif Commands[0] == "me":
            Message = "<i>" 
            Message += self[ID].Username
            Message += Commands[2]
            Message += "</i>"
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            self.SendToAll(Message)
            
            
        else: # elif Commands[0]=="?":
            Message = ServerVersionAuthor
            Message += "\n          Commands are: \n"
            Message += "            /w \"<username>\" <Message> to whisper to a user \n"
            Message += "            /wp \"<IP:Port>\" <Message> to whisper to a user \n"
            Message += "            /wi \"<IP>\" <Message> to whisper to a user \n"
            Message += "            /wd \"<ID>\" <Message> to whisper to a user \n"
            Message += "            /l to display all currently logged in Clients \n"
            Message += "            /n <username> change the username \n"
            Message += "            /d to disconnect \n"
            Message += "            /me \n"
            Message += "            /panic to show your panic \n"
            Message += "            /scream - the most reasonable answer to everything \n"
            Message += "            /? to display this message\n"
            formmsg = cTimeSStr() + self[ID].Username
            formmsg += " has requested the list of commands"
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+self[ID].Username+"has requested the list of commands\n")
                except:
                    pass
            try:
                self.SendToID(ID,Message)
            except Exception:
                formmsg = cTimeSStr() + 'user logged off after request'
                self.printer.emit(formmsg)
            
        
def LookForCommands(Message):
    if len(Message)>=2 and Message[0] == "/":
        if Message[1] == "u":
            return ("none","none",Message[2:],"none")
        elif len(Message) > 4:
            # /w{p|i|d} "<username|IP:Port|IP|ID>" <Message> to whisper to a user
            if Message[1] == "w" and Message.count('"')>=2:
                c , Recipient , Message = Message.split('"',2)
                if c[2]=="p":
                    if Recipient.count(':')==1:
                        RIP , RPort = Recipient.split(':')
                        return (c[:3],RIP, Message,RPort)
                elif c[2]=="i" or c[2]=="d":
                    return (c[:3],Recipient, Message,"none")
                else:
                    return (c[:2],Recipient, Message,"none")
            # /n <username> change the username
            elif Message[1] == "n":
                Message = Message[3:]
                return ("n",Message,"none","none")
            elif Message[1] == "f":
                return ("f","none",Message,"none")
            elif Message[1] == "m" and Message[2] == "e":
                return ("me","none", Message[3:],"none")
            elif Message == "/panic":
                return ("panic","none","none","none")
            elif Message == "/scream":
                return ("scream","none","none","none")
            # no command
            else:
                return ("none","none",Message,"none")
        # /l to display all currently logged in Clients
        elif(Message == "/l"):
            return ("l","none","none","none")
        # /d to disconnect
        elif(Message == "/d"):
            return ("d","none","none","none")
        # /? to get a list of Commands
        elif(Message == "/?"):
            return ("?","none","none","none")
        # no command
        else:
            return ("none","none",Message,"none")
    # no command
    else:
        return ("none","none",Message,"none")
        


class ConnectionObject(QtCore.QThread):
    printer = QtCore.pyqtSignal(str)
    global Connections
    def __init__(self,i):
        QtCore.QThread.__init__(self)
        self.exiting = False
        global sock
        self.MyID = i
        try:
            self.client_socket, self.addr = sock.accept()
        except Exception as inst:
            self.printer.emit("Exception in ConnctionObject Constructor")
            self.printer.emit(str(inst.args))
            self.printer.emit("If the Server was just closed this exception is absolutely normal and even expected.")
            raise ExcBanned("")
        self.IP = self.client_socket.getpeername()[0]
        self.Port = self.client_socket.getpeername()[1]
        if self.IP in Connections.Banned:
            raise ExcBanned("Banned IP tried to connect")
        # TODO Maybe check if IP:Port pair is already logged in (First check if this is even possible)
        self.IsLoggedIn = False
        self.Muted = False
        self.CommandRights = False
        self.Username = "/Username Not Set Yet"


    def __call__(self):
        if self.Muted:
            MyInfo = "(M) "
            MyInfo += str(self.IP)
        elif not self.CommandRights:
            MyInfo = "(D) "
            MyInfo += str(self.IP)
        else:
            MyInfo = str(self.IP)
        MyInfo += ":"
        MyInfo += str(self.Port)
        MyInfo += " as "
        MyInfo += self.Username
        MyInfo += " with ID "
        MyInfo += str(self.MyID)
        return MyInfo
        
    def SetUsername(self):
        while True:
            try:
                self.client_socket.send(("Please Choose your username: ").encode("utf8"))
                Username = self.client_socket.recv(32767).decode("utf8")
                if len(Username) == 0:
                    raise socket.error
                requHist = False
                if Username == "requHist":
                    requHist = True
                    Username = self.client_socket.recv(32767).decode("utf8")
                    if len(Username) == 0:
                        raise socket.error
                    
                Username = Username[1:]
                if len(Username) == 2 and Username[0]=="/" and Username[1]=="d":
                    raise socket.error
                if len(Username) >= 2 and Username[0]=="/" and Username[1]=="f":
                    self.client_socket.send(("Please do NOT use files as your Username ").encode("utf8"))
                    continue
                self.Username = Connections.CheckUsername(Username)
                if requHist:
                    if MakeHistory:
                        try:
                            with open('ClientChatHistory.txt', 'r') as content_file:
                                ClientChatHistory = "\n\nChatHistory:\n\n"
                                ClientChatHistory += content_file.read()
                        except:
                            ClientChatHistory = "No Chat History"
                    else:
                        ClientChatHistory = "Chat History is disabled by the Server"
                    self.client_socket.send(ClientChatHistory.encode("utf8"))
                break
            except NameTaken as inst:
                self.client_socket.send((inst.Message).encode("utf8"))
        Message = str(self.IP)
        Message += ":"
        Message += str(self.Port)
        Message += " has joined as \""
        Message += self.Username
        Message += "\" with ID "
        Message += str(self.MyID)
        formmsg = cTimeSStr() + Message
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(cTimeSStr()+Message+'\n')
            except:
                pass
        self.IsLoggedIn = True
        self.CommandRights = True
        Connections.SendToAll(Message)
        Connections.SendToAll_Updated_Client_List()
            
    def send(self,Message):
        Message = cTimeStr() + Message
        Message = Message.encode("utf8")
        self.client_socket.send(Message)
        
    def ListenForMessage(self):
        global Connections
        Message = self.client_socket.recv(32767).decode("utf8")
        if len(Message) == 0:
            raise socket.error()
        Message = Message[1:]
        if not self.Muted:
            Connections.HandleMessage(self.MyID,Message)

    def Kick(self):
        self.IsLoggedIn = False
        self.client_socket.close()
        msg = self.Username + " has been Kicked"
        formmsg = cTimeSStr() + msg
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(formmsg+'\n')
            except:
                pass
        Connections.SendToAll(msg)

    def Mute(self):
        self.Muted = not self.Muted
        if self.Muted:
            msg = self.Username + " has been Muted"
        else:
            msg = self.Username + " is no longer Muted"
        formmsg = cTimeSStr() + msg
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(formmsg+'\n')
            except:
                pass
        Connections.SendToAll(msg)
        Connections.SendToAll_Updated_Client_List()

    def Ban(self):
        Connections.Banned.append(self.IP)
        self.IsLoggedIn = False
        self.client_socket.close()
        msg = "The IP "+self.IP
        msg += " has been Banned"
        formmsg = cTimeSStr() + msg
        self.printer.emit(formmsg)
        if MakeHistory:
            try:
                with open('ChatHistory.txt','a') as text_file:
                    text_file.write(formmsg+'\n')
            except:
                pass
        Connections.SendToAll(msg)



class handle_client(QtCore.QThread):
    printer = QtCore.pyqtSignal(str)
    def __init__(self,MyID):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.MyID = MyID

    def run(self):
        global Connections
        try:
            formmsg = cTimeSStr() + "New Connection:"
            formmsg += str(Connections[self.MyID].client_socket)
            self.printer.emit(formmsg)
            Connections[self.MyID].SetUsername()
            while True:
                Connections[self.MyID].ListenForMessage()
        except socket.error:
            Connections[self.MyID].IsLoggedIn = False
            Message = Connections[self.MyID].Username
            Message += " has disconnected"
            formmsg = cTimeSStr() + Message
            self.printer.emit(formmsg)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(cTimeSStr()+Message+'\n')
                except:
                    pass
            if Connections[self.MyID].Username != "/Username Not Set Yet":
                Connections.SendToAllButOne(self.MyID,Message)
                Connections.SendToAll_Updated_Client_List()
        finally:
            try:
                Connections[self.MyID].client_socket.close()
            except Exception:
                pass
    
    def print(self,msg):
        self.printer.emit(msg)


class Server(QtCore.QThread):
    receiver = QtCore.pyqtSignal(str)
    ConnectCheckBoxUnset = QtCore.pyqtSignal()
    ServerUserListUpdater = QtCore.pyqtSignal()
    fail = QtCore.pyqtSignal(str)
    def __init__(self,IP,Port):
        QtCore.QThread.__init__(self)
        self.exiting = False
        self.IP = IP
        self.Port = Port

    def run(self):
        global Connections
        global sock
        global threadList
        
        try:
            Connections = ConnectionList()
            Connections.printer.connect(self.printer)
            Connections.ServerUserListUpdater.connect(self.ServerUserListUpdater)
            sock = socket.socket()
            sock.bind((self.IP,self.Port))  # Set the Number to 0 to get a random free Port
        except Exception as inst:
            self.fail.emit(str(inst.args))
            sock.close()
            self.exiting = True
            self.exit()
            #raise Exception("The Server has stopped")
        else:
        
            Message = '\n'
            Message += ServerVersionAuthor
            Message += '\n'
            Message += str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            Message += ": Server started with IP and Port: \'"
            Message += str(self.IP)
            Message += "\',"
            Message += str(self.Port)
            if MakeHistory:
                try:
                    with open('ChatHistory.txt','a') as text_file:
                        text_file.write(Message+'\n')
                except:
                    pass
                try:
                    with open('ClientChatHistory.txt','a') as text_file:
                        text_file.write(Message+"\n")
                except:
                    pass
            self.receiver.emit(Message)
            threadList = []
            sock.listen() #maybe add a fixed number but a "reasonable value" is chosen automatically
            
            i = 0
            
            while not self.exiting: 
                try:
                    Connections.append(ConnectionObject(i))
                except ExcBanned:
                    continue
                threadList.append(handle_client(i))
                threadList[i].printer.connect(self.printer)
                Connections[i].printer.connect(self.printer)
                threadList[i].start()
                i+=1

    def printer(self,msg):
        self.receiver.emit(msg)

    
#--------------------------------------------------------------------------------------------------------------------------



class MainWindow(QtWidgets.QMainWindow, Ui_ServerInterface): 
    global bConnected
    global Connections
    global sock

    def __init__(self, ThePalette, TheFontFamily, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.FontFamily = TheFontFamily
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(9)
        self.setFont(newFont)
        self.setPalette(ThePalette)
        
        
        #self.retranslateUi(self)
        global bConnected
        
        
        
        self.PortField.setText("32005")
        myIP = str(socket.gethostbyname(socket.gethostname()))
        
        if platform.system() == 'Linux':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            myIP =  str(s.getsockname()[0])
            del s
            
        #if platform.system() == 'Linux':
        self.IPField.setText(myIP)
            
        self.ConnectCheckBox.clicked.connect(self.on_ConnectBoxChanged) 
        self.SendButton.clicked.connect(self.on_sendButtonClicked)
        self.MuteButton.clicked.connect(self.Mute)
        self.BanButton.clicked.connect(self.Ban)
        self.KickButton.clicked.connect(self.Kick)
        self.InputField.returnPressed.connect(self.on_sendButtonClicked)
        self.FontSizeBox.valueChanged.connect(self.ChangeFontSize)
        
        if MakeHistory:
            try:
                with open('ChatHistory.txt', 'r') as content_file:
                    History = "\n\nChatHistory:\n\n"
                    History += content_file.read()
            except:
                History = "No Chat History"
        else:
            History = "Chat History is disabled by the Server"
        self.print_message(History)
        

    def on_sendButtonClicked(self):
        msg = self.InputField.text()
        self.InputField.clear()
        if self.ConnectCheckBox.isChecked():
            if len(msg) >= 2 and msg[0] == "/":
                if msg[1] == "n" and msg.count('"')>=2:
                    c , ID , NewUsername = msg.split('"',2)
                    try:
                        ID = int(ID)
                    except Exception:
                        self.print_message("ID must be an integer")
                    else:
                        try:
                            NewUsername = Connections.CheckUsername(NewUsername)
                        except NameTaken as inst:
                            self.print_message(inst.Message)
                        else:
                            if len(Connections) > ID and ID >= 0 and Connections[ID].IsLoggedIn:
                                Connections[ID].Username = NewUsername
                                Connections.SendToAll_Updated_Client_List()
                            else:
                                self.print_message("Invalid ID")
                elif msg[1] == "r" and len(msg) > 3:
                    ID = msg[2:]
                    try:
                        ID = int(ID)
                    except Exception:
                        self.print_message("ID must be an integer")
                    else:
                        if len(Connections) > ID and ID >= 0 and Connections[ID].IsLoggedIn:
                            if Connections[ID].CommandRights:
                                Connections[ID].CommandRights = False
                                msg = " can no longer use commands"
                            else:
                                Connections[ID].CommandRights = True
                                msg = " can use commands again"
                            msg = Connections[ID].Username + msg
                            formmsg = cTimeSStr() + msg
                            self.print_message(formmsg)
                            if MakeHistory:
                                try:
                                    with open('ChatHistory.txt','a') as text_file:
                                        text_file.write(cTimeSStr()+msg+'\n')
                                except:
                                    pass
                            Connections.SendToAll_Updated_Client_List()
                            Connections.SendToAll(msg)
                        else:
                            self.print_message("Invalid ID")
                elif msg == "/?":
                    sCommands  = "/n \"<ID>\" <Name>   to Rename a User\n"
                    sCommands += "/r <ID>   revoke a users right to use commands or regrant rights\n"
                    sCommands += "/? to display this message"
                    self.print_message(sCommands)
                else:
                    msg = "   SERVER   : " + msg
                    formmsg = cTimeSStr() + msg
                    self.print_message(formmsg)
                    if MakeHistory:
                        try:
                            with open('ChatHistory.txt','a') as text_file:
                                text_file.write(cTimeSStr()+msg+'\n')
                        except:
                            pass
                    Connections.SendToAll(msg)
            else:
                msg = "   SERVER   : " + msg
                formmsg = cTimeSStr() + msg
                self.print_message(formmsg)
                if MakeHistory:
                    try:
                        with open('ChatHistory.txt','a') as text_file:
                            text_file.write(cTimeSStr()+msg+'\n')
                    except:
                        pass
                Connections.SendToAll(msg)
        else:
            msg = "   SERVER   : " + msg
            msg = cTimeSStr() + msg
            self.print_message(msg)


    
    
    def on_ConnectBoxChanged(self):
        global bConnected
        global sock
        if self.ConnectCheckBox.isChecked() :
            self.print_message("Trying to deploy...")
            IP = self.IPField.text()
            Port = int(self.PortField.text())
            try:
                self.NewServer = Server(IP,Port)
                self.NewServer.start()
                self.NewServer.receiver.connect(self.print_message)
                self.NewServer.ConnectCheckBoxUnset.connect(self.ConnectCheckBoxUnset)
                self.NewServer.ServerUserListUpdater.connect(self.UpdateUserList)
                self.NewServer.fail.connect(self.FailInServer)
                self.print_message("... Deployed ...")
            except Exception as inst:
                self.print_message("Could not deploy Sever")
                self.print_message(str(inst.args))
                self.NewServer.exiting = True
                self.OnlineList.clear()
                Connections.CloseAll()
                sock.close()
                del sock
                self.NewServer.exit()
                self.ConnectCheckBox.setChecked(False)
            finally:
                bConnected = self.ConnectCheckBox.isChecked()
        else:
            self.ConnectCheckBoxUnset()


    def ConnectCheckBoxUnset(self):
        global bConnected
        global threadList
        global sock
        e = 0
        self.print_message("... Closing Server ...\n")
        try:
            sock.close()
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        del sock
        i=0
        try:
            while i < len(threadList):
                try:
                    threadList[i].exiting = True
                except Exception as inst:
                    self.print_message(inst.args)
                    e += 1
                i+=1
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        try:
            self.NewServer.exiting = True
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        self.OnlineList.clear()
        try:
            Connections.CloseAll()
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        i=0
        try:
            while i < len(threadList):
                try:
                    threadList[i].exit()
                except Exception as inst:
                    self.print_message(inst.args)
                    e += 1
                i+=1
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        try:
            self.NewServer.exit()
        except Exception as inst:
            self.print_message(inst.args)
            e += 1
        self.ConnectCheckBox.setChecked(False)
        bConnected = self.ConnectCheckBox.isChecked()
        if e>0:
            msg = str(e)
            msg += " Exceptions occured during the Termination of all Server/Client Threads"
            self.print_message(msg)
        self.print_message("Sever Closed\n\n")
            
    def FailInServer(self,msg):
        self.ConnectCheckBoxUnset()
        self.print_message("An Exception occured in the Server Thread")
        self.print_message(msg)

    def print_message(self,msg):
        if type(msg) != str:
            msg = str(msg)
        self.ChatDisplay.append(msg)
        
    def retranslateUi(self, ClientInterface):
        global WindowTitle
        _translate = QtCore.QCoreApplication.translate
        ClientInterface.setWindowTitle(_translate("ClientInterface", WindowTitle))
        self.PortField.setPlaceholderText(_translate("ServerInterface", "Port"))
        self.MuteButton.setText(_translate("ServerInterface", "Mute"))
        self.IPField.setPlaceholderText(_translate("ServerInterface", "IP"))
        self.FontText.setText(_translate("ServerInterface", "Set Font Size"))
        self.SendButton.setText(_translate("ServerInterface", "Send"))
        self.ConnectCheckBox.setText(_translate("ServerInterface", "SetUp"))
        self.BanButton.setText(_translate("ServerInterface", "Ban"))
        self.KickButton.setText(_translate("ServerInterface", "Kick"))
        self.InputField.setPlaceholderText(_translate("ServerInterface", "Message"))
        
    def UpdateUserList(self):
        self.OnlineList.clear()
        i=0
        while i < len(Connections) :
            if Connections[i].IsLoggedIn:
                item = QtWidgets.QListWidgetItem()
                item.setData(0 , Connections[i]())
                item.setData(1 , Connections[i].MyID)
                item.setText(Connections[i]())
                self.OnlineList.addItem(item)
            i+=1
        
    def Mute(self):
        if self.ConnectCheckBox.isChecked():
            try:
                Connections[self.OnlineList.currentItem().data(1)].Mute()
            except:
                pass

    def Kick(self):
        if self.ConnectCheckBox.isChecked():
            try:
                Connections[self.OnlineList.currentItem().data(1)].Kick()
            except:
                pass

    def Ban(self):
        if self.ConnectCheckBox.isChecked():
            try:
                Connections[self.OnlineList.currentItem().data(1)].Ban()
            except:
                pass
        
    def ChangeFontSize(self):
        Size = self.FontSizeBox.value()
        newFont = QtGui.QFont()
        newFont.setFamily(self.FontFamily)
        newFont.setPointSize(Size)
        self.setFont(newFont)
        self.centralwidget.setFont(newFont)



def main():
    global bConnected
    bConnected = False
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")

    form = MainWindow(AMaDiA_Colour.Dark()[0],"Arial")
    form.show()
    sys.exit(app.exec_())
 
if __name__=="__main__":
    main()