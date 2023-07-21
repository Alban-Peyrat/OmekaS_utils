# -*- coding: utf-8 -*- 

def erase_trailing_slash(path):
    """Erase the last character if it's a slash or backslash.

    Return a string."""
    if path[-1:] in ["/", "\\"]:
        return path[:len(path)-1]
    else:
        return path

def define_logger_level(level):
    """Returns the logger level for the logging library.

    Defaults to INFO"""
    level = level.strip().upper()
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        return "INFO"
    else:
        return level