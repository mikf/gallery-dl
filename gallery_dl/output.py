# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import shutil
import platform

def select():
    """Automatically select a suitable printer class"""
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        return ColorPrinter if ANSI else TerminalPrinter
    else:
        return Printer


class Printer():

    @staticmethod
    def start(path):
        """Print a message indicating the start of a download"""
        pass

    @staticmethod
    def skip(path):
        """Print a message indicating that a download has been skipped"""
        print(CHAR_SKIP, path, sep="", flush=True)

    @staticmethod
    def success(path, tries):
        """Print a message indicating the completion of a download"""
        print(path, flush=True)

    @staticmethod
    def error(file, error, tries, max_tries):
        """Print a message indicating an error during download"""
        pass


class TerminalPrinter():

    @staticmethod
    def start(path):
        """Print a message indicating the start of a download"""
        _safeprint(_shorten(" " + path), end="", flush=True)

    @staticmethod
    def skip(path):
        """Print a message indicating that a download has been skipped"""
        _safeprint(_shorten(CHAR_SKIP + path))

    @staticmethod
    def success(path, tries):
        """Print a message indicating the completion of a download"""
        print("\r", end="")
        _safeprint(_shorten(CHAR_SUCCESS + path))

    @staticmethod
    def error(file, error, tries, max_tries):
        """Print a message indicating an error during download"""
        if tries <= 1 and hasattr(file, "name"):
            print("\r", end="")
            _safeprint(_shorten(CHAR_ERROR + file.name))
        print("[Error] ", end="")
        _safeprint(error, end="")
        print(" (", tries, "/", max_tries, ")", sep="")


class ColorPrinter():

    @staticmethod
    def start(path):
        """Print a message indicating the start of a download"""
        print(_shorten(path), end="", flush=True)

    @staticmethod
    def skip(path):
        """Print a message indicating that a download has been skipped"""
        print("\033[2m", _shorten(path), "\033[0m", sep="")

    @staticmethod
    def success(path, tries):
        """Print a message indicating the completion of a download"""
        if tries == 0:
            print("\r", end="")
        print("\r\033[1;32m", _shorten(path), "\033[0m", sep="")

    @staticmethod
    def error(file, error, tries, max_tries):
        """Print a message indicating an error during download"""
        if tries <= 1 and hasattr(file, "name"):
            print("\r\033[1;31m", _shorten(file.name), sep="")
        print("\033[0;31m[Error]\033[0m ", error, " (", tries, "/", max_tries, ")", sep="")


def _shorten(txt):
    """Reduce the length of 'txt' to the width of the terminal"""
    width = shutil.get_terminal_size().columns - OFFSET
    if len(txt) > width:
        hwidth = width // 2 - OFFSET
        return "".join((txt[:hwidth-1], CHAR_ELLIPSIES, txt[-hwidth-(width%2):]))
    return txt

def _safeprint(txt, **kwargs):
    """Handle unicode errors and replace invalid characters"""
    try:
        print(txt, **kwargs)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding
        txt = txt.encode(enc, errors="replace").decode(enc)
        print(txt, **kwargs)

if platform.system() == "Windows":
    ANSI = os.environ.get("TERM") == "ANSI"
    OFFSET = 1
    CHAR_SKIP = "#"
    CHAR_ERROR = "!"
    CHAR_SUCCESS = "*"
    CHAR_ELLIPSIES = "..."
else:
    ANSI = True
    OFFSET = 0
    CHAR_SKIP = "#"
    CHAR_ERROR = "❌"
    CHAR_SUCCESS = "✔"
    CHAR_ELLIPSIES = "…"
