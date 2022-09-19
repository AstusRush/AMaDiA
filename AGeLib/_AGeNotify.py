#region General Import
from ._import_temp import *
#endregion General Import


try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from ._AGeApp import AGeApp
except:
    pass

#region local helper function duplicates
def _NC_App():
    # type: () -> AGeApp
    """
    Convenient shortcut for `QtWidgets.QApplication.instance()` \n
    (This function is a copy of its implementation in AGeFunctions to avoid cyclic imports.\n
    It is used here (instead of calling QtWidgets.QApplication.instance() directly) so that the linter recognizes AGeApp specific methods and members.)
    """
    return QtWidgets.QApplication.instance()
#endregion local helper function duplicates


#region Time Format Functions

def cTimeStr():
    """
    Returns the time (excluding seconds) as a string\n
    %H:%M
    """
    return str(datetime.datetime.now().strftime('%H:%M'))

def cTimeSStr():
    """
    Returns the time (including seconds) as a string\n
    %H:%M:%S
    """
    return str(datetime.datetime.now().strftime('%H:%M:%S'))

def cTimeFullStr(separator = None):
    """
    Returns the date and time as a string\n
    If given uses `separator` to separate the values\n
    %Y.%m.%d-%H:%M:%S or separator.join(['%Y','%m','%d','%H','%M','%S'])
    """
    if separator == None:
        return str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    else:
        TheFormat = separator.join(['%Y','%m','%d','%H','%M','%S'])
        return str(datetime.datetime.now().strftime(TheFormat))
        
#endregion



#region Notifications and exceptions

#CRITICAL: Remove common_exceptions from AGeLib and move it to AMaDiA! Only AMaDiA needs this list (and must even add to this list to use it!) and it is not a good list anyways! It is specific to AMaDiA's needs and thus it should only be in AMaDiA!
common_exceptions = (TypeError , SyntaxError , re.error ,  AttributeError , ValueError , NotImplementedError , Exception , RuntimeError , ImportError)

def ExceptionOutput(exc_info = None, extraInfo = True):
    # type: (tuple[type[BaseException],BaseException,traceback.TracebackType]|None,bool) -> str
    """
    Console output for exceptions\n
    Use in `except:`: Error = ExceptionOutput(sys.exc_info())\n
    Prints Time, ExceptionType, Filename+Line and (if extraInfo in not False) the exception description to the console\n
    Returns a string
    """
    try:
        if False: #CLEANUP: The new code (in the else case) seems to be stable; therefore, this old code can be removed.
            if exc_info == None:
                exc_info = True
            return NC(exc=exc_info)
        else:
            print(cTimeSStr(),":")
            if exc_info==None:
                exc_type, exc_obj, exc_tb = sys.exc_info()
            else:
                exc_type, exc_obj, exc_tb = exc_info
            fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            if extraInfo:
                print(exc_type, " in", fName, " line", exc_tb.tb_lineno ,": ", exc_obj)
            else:
                print(exc_type, " in", fName, " line", exc_tb.tb_lineno)
            return str(exc_type)+": "+str(exc_obj)
    except common_exceptions as inst: #TODO: Better Exceptions output formatting
        print("An exception occurred while trying to print an exception!")
        print(inst)
        return ""
        

def trap_exc_during_debug(*args): # *args = (type, value, traceback)
    """
    This function is used to intercept all exceptions and print them to the console while keeping the application running. \n
    This way try-except-blocks are not always required which make development with AGeIDE possible. \n
    Catching all exceptions may seem very unreasonable and contrary to "good practice" but I have very good reasons for doing this. \n
    As a general note: I am aware how many holy programming rules I break with AGeLib but it's way more fun this way.
    """
    #TODO: Keyboardinterrupt (and some other exceptions) should be allowed to exit the application
    #           However open a dialogue that asks if the application should really be closed as Keyboardinterrupt can be very useful to abort a function call without closing the program!
    print(cTimeSStr(), ":  An unhandled exception occurred:")
    try:
        exc_type, exc_obj, exc_tb = args
        traceback.print_exception(exc_type, exc_obj, exc_tb)
    except:
        print(args)
    print()
    NC(1,"An unhandled exception occurred!!!",exc=args)

# -----------------------------------------------------------------------------------------------------------------

class NotificationEvent(QtCore.QEvent):
    try:
        EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType(5000))
    except:
        EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    EVENT_ID = EVENT_TYPE.value if QtVersion == "PyQt6" else EVENT_TYPE # type: ignore
    def __init__(self, N):
        QtCore.QEvent.__init__(self, NotificationEvent.EVENT_TYPE)
        self.N = N

class NC: # Notification Class
    """
    This is the basic notification class of AGeLib.  \n
    All notifications are stored and accessible via the Notification Window which is opened by pressing the Notification button of any (AWWF) window.   \n
    Notifications are used to communicate with the user and can be used for exception handling as they provide space for an entire bug report.   \n
    They contain the version number of all modules that are in MainApp.ModuleVersions and can extract all information from exceptions.   \n
    There are various levels of notifications: lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
    The notification sends itself automatically. If you want to modify the notification before it is send set `send=False` and call `.send()` after the modifications are done.  \n
    If you don't set `send=False` and this method is called during a mutex is locked processEvents should be set to `False`.   \n
    `processEvents` ensures that the notifications is immediately.   \n
    The creation is very flexible. Here are a few examples:   \n
    ```python
    NC(10,"This message is directly displayed in the top bar and should be held very short and not contain any linebreaks (a single linebreak is ok in spacial cases)")
    NC("This creates a normal notification")
    NC(2,"This creates a warning")
    NC((2,"A tuple with level and message is also acceptable"))
    NC("This generates an error notification with the last caught exception",exc = sys.exc_info())
    NC("This notification includes the callstack",tb=True)
    ```
    Even this is valid: `NC()` (Though not recommended)   \n
    `lvl=0` can be useful if you want to create a notification in a function (with `Notification = NC(lvl=0,send=False)`), fill it with information dynamically and return it for the caller.
    The caller can then send the Notification. If `lvl=0` the MainApp will ignore the notification thus the caller does not need to care whether the function actually had anything to notify the user about.   \n
    If you want to notify the user about exceptions `exc` should be `True` or `sys.exc_info()`. If the exception should be logged but is usually not important set `lvl=4`.
    If the exception is not critical but should be noted as it might lead to unwanted behaviour set `lvl=2` to warn the user.
    Exception notifications should set `msg` to give a short description that a regular user can understand (for example `msg="The input could not be interpreted."` or `msg="Could not connect to the website."`).
    It is also useful to set `input` to log the input that lead to the error. This should also include any settings that were used.   \n
    Only `lvl=int`,`time=datetime.datetime.now()`,`send=bool`,`unique=bool`, and `exc=True or sys.exc_info()` need a specific data type.
    Everything else will be stored (msg will be converted into a string before storing). The access methods will return a string (and cast all input to a string before saving)
    but the variables can still be accessed directly with the data type that was given to the init.  \n
    Please note that `err` and `tb` are ignored when `exc != None` as they will be extracted from the exception.  \n
    `tb` should be a string containing the callstack or `True` to generate a callstack. \n \n
    Setting `log=False` will suppress the S_New_Notification signal, prevent the notification to appear in the tooltip of following notifications
    and cause the notification to not be saved in the Notification_List. \n
    `log=False` will thus make most of the information in the notification completely inaccessible and make the notification easy to miss. \n
    `log=False` is only meant as a convenient way to change the text, tooltip and icon of the Error_Label without overwriting other recent notifications and without flooding the Notification_List! \n
    `unique=True` will ensure that a notification with this exact `msg` will only be displayed once during the runtime of the application. \n
    For example `unique=True` is used by widgets that use QWebengine to inform the user that the QWebengine module could not be imported and explain what this module is used for and how to install it.
    Since there can be multiple instances of the same widget `unique=True` ensures that the user is not flooded by several identical notifications.
    """
    def __init__(self, lvl=None, msg=None, time=None, input=None, err=None, tb=None, exc=None, win=None, func=None, DplStr=None, log=True, unique=False, send=True, processEvents=True):
        # type: (      int,      str,      datetime.datetime,str, str,      str|bool,tuple[type[BaseException],BaseException,traceback.TracebackType]|bool,str,str,str,bool,bool,bool,bool) -> None
        """
        Creates a new notification object  \n
        The creation is very flexible. Here are a few examples:   \n
        ```python
        NC(10,"This message is directly displayed in the top bar and should be held short and without linebreaks")
        NC("This creates a normal notification")
        NC(2,"This creates a warning")
        NC((2,"A tuple with level and message is also acceptable"))
        NC("This generates an error notification with the last caught exception",exc = sys.exc_info())
        NC("This notification includes the callstack",tb=True)
        ```
        lvl: 0 = Nothing , 1 = Error , 2 = Warning , 3 = Notification , 4 = Advanced Mode Notification , 10 = Direct Notification  \n
        `exc = True` or `sys.exc_info()`   \n
        `tb` should be a string containing the callstack or `True` to generate a callstack
        """
        #TODO: Also implement logging with the logging module and use that as output
        self._time_time = timetime()
        self._init_Values()
        self._was_send = False
        self.log = log
        try:
            self._time = datetime.datetime.now() if time == None else time
            self.Time = self._time.strftime('%H:%M:%S')
            self.DplStr = DplStr
            self.Window = win
            self.Function = func
            self.Input = input
            self.unique = unique
            if exc:
                if exc == True:
                    self.exc_type, self.exc_obj, self.exc_tb = sys.exc_info()
                else:
                    self.exc_type, self.exc_obj, self.exc_tb = exc
                if not self.exc_tb is None: fName = os.path.split(self.exc_tb.tb_frame.f_code.co_filename)[1]
                else: fName = "UNKNOWN"
                try:
                    if type(lvl)==str:
                        self.level = 1
                        self.Message = lvl
                    elif msg==None and type(lvl) == tuple:
                        self.level, self.Message = lvl[0], lvl[1]
                    else:
                        self.level = 1 if lvl == None else lvl
                        self.Message = str(msg) if msg!=None else None
                except: # Catches the case that "msg" is of a data type that can not perform the compare "msg==None"
                    if type(lvl)==str:
                        self.level = 1
                        self.Message = lvl
                    elif type(msg)==type(None) and type(lvl) == tuple:
                        self.level, self.Message = lvl[0], lvl[1]
                    else:
                        self.level = 1 if lvl == None else lvl
                        self.Message = str(msg) if type(msg)!=type(None) else None
                #self.ErrorTraceback = str(self.exc_type)+"  in "+str(fName)+"  line "+str(self.exc_tb.tb_lineno)+"\n\n"+"".join(traceback.format_tb(self.exc_tb))#str(traceback.format_exc())#[:-1]) # maybe: Use traceback.format_exc() to get full traceback or something like traceback.extract_stack()[:-1] ([:-1] removes the NC.__init__())
                self.ErrorTraceback = "".join(traceback.format_exception(self.exc_type, self.exc_obj, self.exc_tb))
                print(self.Time,":")
                if not self.exc_tb is None: lineno = self.exc_tb.tb_lineno
                else: lineno = "UNKNOWN"
                if len(str(self.exc_obj))<150:
                    self.Error = str(self.exc_type)+": "+str(self.exc_obj)
                    print(self.exc_type, " in", fName, " line", lineno,": ", self.exc_obj)
                else:
                    self.Error = str(self.exc_type)
                    self.ErrorLongDesc = str(self.exc_obj)
                    print(self.exc_type, " in", fName, " line", lineno)
                print(self.ErrorTraceback)
            else:
                try:
                    if type(lvl)==str:
                        self.level = 3
                        self.Message = lvl
                    elif msg==None and type(lvl) == tuple:
                        self.level, self.Message = lvl[0], lvl[1]
                    else:
                        self.level = 3 if lvl == None else lvl
                        self.Message = str(msg) if msg!=None else None
                except: # Catches the case that "msg" is of a data type that can not perform the compare "msg==None"
                    if type(lvl)==str:
                        self.level = 3
                        self.Message = lvl
                    elif type(msg)==type(None) and type(lvl) == tuple:
                        self.level, self.Message = lvl[0], lvl[1]
                    else:
                        self.level = 3 if lvl == None else lvl
                        self.Message = str(msg) if type(msg)!=type(None) else None
                self.Error = err
                if tb == True:
                    self.ErrorTraceback = ""
                    try:
                        for i in traceback.format_stack()[0:-1]:
                            self.ErrorTraceback += str(i)
                    except:
                        self.ErrorTraceback = "Could not extract callstack"
                else:
                    self.ErrorTraceback = tb
            self.GenerateLevelName()
            #TODO: The lvl is 1 and no DplStr was given there should be a small chance that the DplStr is set to "I'm afraid I can't do that, Dave.". This could be done by generating a random number and using modulo.
            #       But the chance should be less than 1/100. Maybe something like 1/250? or 1/200?
            if send == True:
                self.send(processEvents=processEvents)
        except common_exceptions as inst: #TODO: Clean this up and 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            self._init_Values()
            print(cTimeSStr(),": An exception occurred while trying to create a Notification")
            print(inst)
            self._time = datetime.datetime.now() if time == None else time
            self.Time = self._time.strftime('%H:%M:%S')
            self.Message = "An exception occurred while trying to create a Notification"
            self.exc_obj = inst
            self.Error = str(inst)
            self.GenerateLevelName()
            self.send(force=True, processEvents=processEvents)
    
    def _init_Values(self):
        self.exc_type, self.exc_obj, self.exc_tb = None,None,None
        self._time, self.Time, self.Error = None,None,None
        self.Window, self.ErrorTraceback, self.Function = None,None,None
        self.level, self.Level, self.Message = 1,"Notification level 1",None
        self.Input, self.ErrorLongDesc = None,None
        self.DplStr, self.TTStr = None,None
        self.icon = QtGui.QIcon()
        try:
            self.Flash = _NC_App().NCF_NONE
        except common_exceptions as inst: #TODO: Use better exception output formating and print a short explanation where this exception occurred and what it means
            print(inst)
            self.Flash = None
        self.itemDict = {"Time:\n":self.Time,"Level: ":self.Level,"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input}
  #---------- send, print ----------#
    def send(self,force=False,processEvents=True):
        # type: (bool,bool) -> None
        """
        Displays this notification   \n
        This method is thread save but this object should not be modified after using send   \n
        If this method is called during a mutex is locked processEvents should be set to `False`   \n
        A notification can only be send once. `force=True` allows to send an already send notification again
        """
        if force or not self._was_send:
            self._was_send = True
            e = NotificationEvent(self)
            QtWidgets.QApplication.postEvent(QtCore.QThread.currentThread(), e)
            if processEvents:
                _NC_App().processEvents()
            elif QtVersion == "PyQt6": # type: ignore
                self._event_garbage_collection_protection_for_PyQt6_with_delayed_processing = e
            e # We need this here to keep the garbage collector from deleting this event before it is processed when using PyQt6 because PyQt6 is... let's call it special... but in a bad way
    
    def print(self):
        """Prints this notification to the console"""
        print("\n",self.Level, "at",self.Time,"\nMessage:",self.Message)
        if self.Error != None:
            print("Error:",self.Error,"Traceback:",self.ErrorTraceback,"\n")
  #---------- items, unpack ----------#
    def items(self):
        """
        Returns self.itemDict.items()   \n
        self.itemDict contains all relevant data about this notification.  \n
        Please note that not all values are strings and should be converted before diplaying them.
        This allows `if v!=None:` to filter out all empty entries.    \n
        The keys already end with `:\\n` thus it is advised to simply use `k+str(v)` for formatting.  \n
        For an example how to use this method see the source code of `NotificationInfoWidget`.
        """
        self.itemDict = {"Time:\n":self.Time,"Level: ":"({})\n{}".format(str(self.level),self.Level),"Message:\n":self.Message,
                        "Error:\n":self.Error,"Error Description:\n":self.ErrorLongDesc,"Error Traceback:\n":self.ErrorTraceback,
                        "Function:\n":self.Function,"Window:\n":self.Window,"Input:\n":self.Input,"Versions:\n":_NC_App().ModuleVersions}
        return self.itemDict.items()

    def unpack(self): #CLEANUP: remove unpack
        """DEPRECATED: Returns a tuple `(int(level),str(Message),str(Time))`"""
        return (self.level, str(self.Message), self.Time)
  #---------- access variables ----------#
    def l(self, level=None):
        # type: (typing.Optional[int]) -> int
        """
        Returns int(level)  \n
        An int can be given to change the level
        """
        if level != None:
            self.level = level
            self.GenerateLevelName()
        return self.level

    def m(self, message=None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(Message)  \n
        A str can be given to change the Message
        """
        if message != None:
            self.Message = str(message)
        if self.Message == None and self.Error != None:
            return str(self.Error)
        else:
            return str(self.Message)
        
    def DPS(self, DplStr = None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(DplStr)  \n
        DplStr is the string that is intended to be displayed directly   \n
        A str can be given to change the DplStr
        """
        if DplStr != None:
            self.DplStr = str(DplStr)
        elif self.DplStr == None:
            if self.level == 10:
                self.DplStr = self.m()
            else:
                self.DplStr = self.Level + " at " + self.t()
        return str(self.DplStr)
        
    def TTS(self, TTStr = None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(TTStr)  \n
        TTStr is the string that is intended to be displayed as the tool tip   \n
        A str can be given to change the TTStr
        """
        if TTStr != None:
            self.TTStr = str(TTStr)
        elif self.TTStr == None:
            if self.level == 10:
                self.TTStr = self.Level + " at " + self.t()
            else:
                self.TTStr = self.m()
        return str(self.TTStr)

    def t(self, time=None):
        # type: (typing.Optional[datetime.datetime]) -> str
        """
        Returns the time as %H:%M:%S  \n
        datetime.datetime.now() can be given to change the time
        """
        if time != None:
            self._time = time
            self.Time = self._time.strftime('%H:%M:%S')
        return self.Time

    def e(self, Error=None, ErrorTraceback=None):
        # type: (typing.Optional[BaseException],typing.Optional[str]) -> str
        """
        Returns str(Error)  \n
        strings can be given to change the Error and ErrorTraceback
        """
        if Error != None:
            self.Error = str(Error)
        if ErrorTraceback != None:
            self.ErrorTraceback = str(ErrorTraceback)
        return str(self.Error)

    def tb(self, ErrorTraceback=None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(ErrorTraceback)  \n
        A str can be given to change the ErrorTraceback
        """
        if ErrorTraceback != None:
            self.ErrorTraceback = str(ErrorTraceback)
        return str(self.ErrorTraceback)

    def f(self, func=None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(Function)  \n
        A str can be given to change the Function  \n
        Function is the name of the function from which this notification originates
        """
        if func != None:
            self.Function = str(func)
        return str(self.Function)

    def w(self, win=None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(Window)  \n
        A str can be given to change the Window  \n
        Window is the name of the window from which this notification originates
        """
        if win != None:
            self.Window = str(win)
        return str(self.Window)

    def i(self, input=None):
        # type: (typing.Optional[str]) -> str
        """
        Returns str(Input)  \n
        A str can be given to change the Input  \n
        Input is the (user-)input that caused this notification
        """
        if input != None:
            self.Input = str(input)
        return str(self.Input)
  #---------- GenerateLevelName ----------#
    def GenerateLevelName(self):
        # type: () -> str
        """
        Generates str(self.Level) from int(self.level)
        """
        try:
            if self.level == 0:
                self.Level = "Empty Notification"
                self.icon = QtGui.QIcon()
                self.Flash = _NC_App().NCF_NONE
            elif self.level == 1:
                self.Level = "Error"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical)
                self.Flash = _NC_App().NCF_r
            elif self.level == 2:
                self.Level = "Warning"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning)
                self.Flash = _NC_App().NCF_y
            elif self.level == 3:
                self.Level = "Notification"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
                self.Flash = _NC_App().NCF_b
            elif self.level == 4:
                self.Level = "Advanced Mode Notification"
                self.icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
                self.Flash = _NC_App().NCF_b
            elif self.level == 10:
                self.Level = "Direct Notification"
                self.icon = QtGui.QIcon()
                self.Flash = _NC_App().NCF_NONE
            else:
                self.Level = "Notification level "+str(self.level)
                self.Flash = _NC_App().NCF_b
            return self.Level
        except common_exceptions as inst:
            print(inst)
            return "Could not generate Level Name"
  #---------- __...__ ----------#
    def __add__(self,other):
        if self.Error != None:
            return str(self.Error) + str(other)
        else:
            return str(self.Message) + str(other)

    def __radd__(self,other):
        if self.Error != None:
            return str(other) + str(self.Error)
        else:
            return str(other) + str(self.Message)

    def __call__(self):
        return str(self.Message)

    def __str__(self):
        if self.Error != None:
            if self.Message == None:
                return "Exception at "+str(self.Time)+":\n"+str(self.Error)
            else:
                return str(self.Level)+" at "+str(self.Time)+":\n"+str(self.Message)+"\n"+str(self.Error)
        else:
            return str(self.Level)+" at "+str(self.Time)+":\n"+str(self.Message)

#endregion
