"""
AGeLib Exception Handling and Notifications
"""
try:
    from AGeLib.AGeMain import NC,common_exceptions,ExceptionOutput
except ModuleNotFoundError:
    from AGeMain import NC,common_exceptions,ExceptionOutput