"""
This module provides functions to convert python objects into python code that can then be executed to reproduce the original object. \n
Furthermore, the created code is formated in a way to be easily readable and editable by a human. \n
Automatic imports are also provided such that the execution of the generated code only requires that AGeLib is loaded if Qt is required (to provide the distribution independent bindings).
"""
from ._AGeToPy import(
    topy,
    _topy,
    formatObject,
    formatImp,
    format_,
    writeToFile,
)
