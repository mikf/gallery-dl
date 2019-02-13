# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import shutil
import logging
from . import config, util


# --------------------------------------------------------------------
# Logging

LOG_FORMAT = "[{name}][{levelname}] {message}"
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO


class Logger(logging.Logger):
    """Custom logger that includes extractor and job info in log records"""
    extractor = util.NONE
    job = util.NONE

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None,
                   factory=logging._logRecordFactory):
        rv = factory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        rv.extractor = self.extractor
        rv.job = self.job
        return rv


def initialize_logging(loglevel):
    """Setup basic logging functionality before configfiles have been loaded"""
    # convert levelnames to lowercase
    for level in (10, 20, 30, 40, 50):
        name = logging.getLevelName(level)
        logging.addLevelName(level, name.lower())

    # register custom Logging class
    logging.Logger.manager.setLoggerClass(Logger)

    # setup basic logging to stderr
    formatter = logging.Formatter(LOG_FORMAT, LOG_FORMAT_DATE, "{")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(loglevel)
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    root.addHandler(handler)

    return logging.getLogger("gallery-dl")


def setup_logging_handler(key, fmt=LOG_FORMAT, lvl=LOG_LEVEL):
    """Setup a new logging handler"""
    opts = config.interpolate(("output", key))
    if not opts:
        return None
    if not isinstance(opts, dict):
        opts = {"path": opts}

    path = opts.get("path")
    mode = opts.get("mode", "w")
    encoding = opts.get("encoding", "utf-8")
    try:
        path = util.expand_path(path)
        handler = logging.FileHandler(path, mode, encoding)
    except (OSError, ValueError) as exc:
        logging.getLogger("gallery-dl").warning(
            "%s: %s", key, exc)
        return None
    except TypeError as exc:
        logging.getLogger("gallery-dl").warning(
            "%s: missing or invalid path (%s)", key, exc)
        return None

    level = opts.get("level", lvl)
    logfmt = opts.get("format", fmt)
    datefmt = opts.get("format-date", LOG_FORMAT_DATE)
    formatter = logging.Formatter(logfmt, datefmt, "{")
    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


def configure_logging_handler(key, handler):
    """Configure a logging handler"""
    opts = config.interpolate(("output", key))
    if not opts:
        return
    if isinstance(opts, str):
        opts = {"format": opts}
    if handler.level == LOG_LEVEL and "level" in opts:
        handler.setLevel(opts["level"])
    if "format" in opts or "format-date" in opts:
        logfmt = opts.get("format", LOG_FORMAT)
        datefmt = opts.get("format-date", LOG_FORMAT_DATE)
        formatter = logging.Formatter(logfmt, datefmt, "{")
        handler.setFormatter(formatter)


# --------------------------------------------------------------------
# Utility functions

def replace_std_streams(errors="replace"):
    """Replace standard streams and set their error handlers to 'errors'"""
    for name in ("stdout", "stdin", "stderr"):
        stream = getattr(sys, name)
        setattr(sys, name, stream.__class__(
            stream.buffer,
            errors=errors,
            newline=stream.newlines,
            line_buffering=stream.line_buffering,
        ))


# --------------------------------------------------------------------
# Downloader output

def select():
    """Automatically select a suitable output class"""
    pdict = {
        "default": PipeOutput,
        "pipe": PipeOutput,
        "term": TerminalOutput,
        "terminal": TerminalOutput,
        "color": ColorOutput,
        "null": NullOutput,
    }
    omode = config.get(("output", "mode"), "auto").lower()
    if omode in pdict:
        return pdict[omode]()
    elif omode == "auto":
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            return ColorOutput() if ANSI else TerminalOutput()
        else:
            return PipeOutput()
    else:
        raise Exception("invalid output mode: " + omode)


class NullOutput():

    def start(self, path):
        """Print a message indicating the start of a download"""

    def skip(self, path):
        """Print a message indicating that a download has been skipped"""

    def success(self, path, tries):
        """Print a message indicating the completion of a download"""


class PipeOutput(NullOutput):

    def skip(self, path):
        print(CHAR_SKIP, path, sep="", flush=True)

    def success(self, path, tries):
        print(path, flush=True)


class TerminalOutput(NullOutput):

    def __init__(self):
        self.short = config.get(("output", "shorten"), True)
        if self.short:
            self.width = shutil.get_terminal_size().columns - OFFSET

    def start(self, path):
        print(self.shorten("  " + path), end="", flush=True)

    def skip(self, path):
        print(self.shorten(CHAR_SKIP + path))

    def success(self, path, tries):
        print("\r", self.shorten(CHAR_SUCCESS + path), sep="")

    def shorten(self, txt):
        """Reduce the length of 'txt' to the width of the terminal"""
        if self.short and len(txt) > self.width:
            hwidth = self.width // 2 - OFFSET
            return "".join((
                txt[:hwidth-1],
                CHAR_ELLIPSIES,
                txt[-hwidth-(self.width % 2):]
            ))
        return txt


class ColorOutput(TerminalOutput):

    def start(self, path):
        print(self.shorten(path), end="", flush=True)

    def skip(self, path):
        print("\033[2m", self.shorten(path), "\033[0m", sep="")

    def success(self, path, tries):
        print("\r\033[1;32m", self.shorten(path), "\033[0m", sep="")


if os.name == "nt":
    ANSI = os.environ.get("TERM") == "ANSI"
    OFFSET = 1
    CHAR_SKIP = "# "
    CHAR_SUCCESS = "* "
    CHAR_ELLIPSIES = "..."
else:
    ANSI = True
    OFFSET = 0
    CHAR_SKIP = "# "
    CHAR_SUCCESS = "✔ "
    CHAR_ELLIPSIES = "…"
