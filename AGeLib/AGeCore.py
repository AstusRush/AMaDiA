"""
This module can be imported with
```python
from AGeLib.AGeCore import *
```
to import the most basic classes for ease of access. \n
This module does not itself define any classes or functions.
"""
#region General Import
from ._import_temp import Version as AGeLibVersion
#endregion General Import


#region Import
from ._AGeNotify import ExceptionOutput, NC
from ._AGeApp import AGeApp
from ._AGeFunctions import App, advancedMode
from ._AGeAWWF import AWWF
#endregion Import
MainApp = AGeApp

