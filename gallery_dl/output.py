# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import shutil
import logging
import unicodedata
from . import config, util, formatter


# --------------------------------------------------------------------
# Logging

LOG_FORMAT = "[{name}][{levelname}] {message}"
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO


class Logger(logging.Logger):
    """Custom logger that includes extra info in log records"""

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None,
                   factory=logging._logRecordFactory):
        rv = factory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        if extra:
            rv.__dict__.update(extra)
        return rv


class LoggerAdapter():
    """Trimmed-down version of logging.LoggingAdapter"""
    __slots__ = ("logger", "extra")

    def __init__(self, logger, extra):
        self.logger = logger
        self.extra = extra

    def debug(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.DEBUG):
            kwargs["extra"] = self.extra
            self.logger._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.INFO):
            kwargs["extra"] = self.extra
            self.logger._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.WARNING):
            kwargs["extra"] = self.extra
            self.logger._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.ERROR):
            kwargs["extra"] = self.extra
            self.logger._log(logging.ERROR, msg, args, **kwargs)


class PathfmtProxy():
    __slots__ = ("job",)

    def __init__(self, job):
        self.job = job

    def __getattribute__(self, name):
        pathfmt = object.__getattribute__(self, "job").pathfmt
        return pathfmt.__dict__.get(name) if pathfmt else None

    def __str__(self):
        pathfmt = object.__getattribute__(self, "job").pathfmt
        if pathfmt:
            return pathfmt.path or pathfmt.directory
        return ""


class KwdictProxy():
    __slots__ = ("job",)

    def __init__(self, job):
        self.job = job

    def __getattribute__(self, name):
        pathfmt = object.__getattribute__(self, "job").pathfmt
        return pathfmt.kwdict.get(name) if pathfmt else None


class Formatter(logging.Formatter):
    """Custom formatter that supports different formats per loglevel"""

    def __init__(self, fmt, datefmt):
        if isinstance(fmt, dict):
            for key in ("debug", "info", "warning", "error"):
                value = fmt[key] if key in fmt else LOG_FORMAT
                fmt[key] = (formatter.parse(value).format_map,
                            "{asctime" in value)
        else:
            if fmt == LOG_FORMAT:
                fmt = (fmt.format_map, False)
            else:
                fmt = (formatter.parse(fmt).format_map, "{asctime" in fmt)
            fmt = {"debug": fmt, "info": fmt, "warning": fmt, "error": fmt}

        self.formats = fmt
        self.datefmt = datefmt

    def format(self, record):
        record.message = record.getMessage()
        fmt, asctime = self.formats[record.levelname]
        if asctime:
            record.asctime = self.formatTime(record, self.datefmt)
        msg = fmt(record.__dict__)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            msg = msg + "\n" + record.exc_text
        if record.stack_info:
            msg = msg + "\n" + record.stack_info
        return msg


def initialize_logging(loglevel):
    """Setup basic logging functionality before configfiles have been loaded"""
    # convert levelnames to lowercase
    for level in (10, 20, 30, 40, 50):
        name = logging.getLevelName(level)
        logging.addLevelName(level, name.lower())

    # register custom Logging class
    logging.Logger.manager.setLoggerClass(Logger)

    # setup basic logging to stderr
    formatter = Formatter(LOG_FORMAT, LOG_FORMAT_DATE)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(loglevel)
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    root.addHandler(handler)

    return logging.getLogger("gallery-dl")


def configure_logging(loglevel):
    root = logging.getLogger()
    minlevel = loglevel

    # stream logging handler
    handler = root.handlers[0]
    opts = config.interpolate(("output",), "log")
    if opts:
        if isinstance(opts, str):
            opts = {"format": opts}
        if handler.level == LOG_LEVEL and "level" in opts:
            handler.setLevel(opts["level"])
        if "format" in opts or "format-date" in opts:
            handler.setFormatter(Formatter(
                opts.get("format", LOG_FORMAT),
                opts.get("format-date", LOG_FORMAT_DATE),
            ))
        if minlevel > handler.level:
            minlevel = handler.level

    # file logging handler
    handler = setup_logging_handler("logfile", lvl=loglevel)
    if handler:
        root.addHandler(handler)
        if minlevel > handler.level:
            minlevel = handler.level

    root.setLevel(minlevel)


def setup_logging_handler(key, fmt=LOG_FORMAT, lvl=LOG_LEVEL):
    """Setup a new logging handler"""
    opts = config.interpolate(("output",), key)
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

    handler.setLevel(opts.get("level", lvl))
    handler.setFormatter(Formatter(
        opts.get("format", fmt),
        opts.get("format-date", LOG_FORMAT_DATE),
    ))
    return handler


# --------------------------------------------------------------------
# Utility functions

def stdout_write_flush(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def stderr_write_flush(s):
    sys.stderr.write(s)
    sys.stderr.flush()


if sys.stdout.line_buffering:
    def stdout_write(s):
        sys.stdout.write(s)
else:
    stdout_write = stdout_write_flush


if sys.stderr.line_buffering:
    def stderr_write(s):
        sys.stderr.write(s)
else:
    stderr_write = stderr_write_flush


def replace_std_streams(errors="replace"):
    """Replace standard streams and set their error handlers to 'errors'"""
    for name in ("stdout", "stdin", "stderr"):
        stream = getattr(sys, name)
        if stream:
            setattr(sys, name, stream.__class__(
                stream.buffer,
                errors=errors,
                newline=stream.newlines,
                line_buffering=stream.line_buffering,
            ))


# --------------------------------------------------------------------
# Downloader output

def select():
    """Select a suitable output class"""
    mode = config.get(("output",), "mode")

    if mode is None or mode == "auto":
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            output = ColorOutput() if ANSI else TerminalOutput()
        else:
            output = PipeOutput()
    elif isinstance(mode, dict):
        output = CustomOutput(mode)
    else:
        output = {
            "default" : PipeOutput,
            "pipe"    : PipeOutput,
            "term"    : TerminalOutput,
            "terminal": TerminalOutput,
            "color"   : ColorOutput,
            "null"    : NullOutput,
        }[mode.lower()]()

    if not config.get(("output",), "skip", True):
        output.skip = util.identity
    return output


class NullOutput():

    def start(self, path):
        """Print a message indicating the start of a download"""

    def skip(self, path):
        """Print a message indicating that a download has been skipped"""

    def success(self, path):
        """Print a message indicating the completion of a download"""

    def progress(self, bytes_total, bytes_downloaded, bytes_per_second):
        """Display download progress"""


class PipeOutput(NullOutput):

    def skip(self, path):
        stdout_write(CHAR_SKIP + path + "\n")

    def success(self, path):
        stdout_write(path + "\n")


class TerminalOutput():

    def __init__(self):
        shorten = config.get(("output",), "shorten", True)
        if shorten:
            func = shorten_string_eaw if shorten == "eaw" else shorten_string
            limit = shutil.get_terminal_size().columns - OFFSET
            sep = CHAR_ELLIPSIES
            self.shorten = lambda txt: func(txt, limit, sep)
        else:
            self.shorten = util.identity

    def start(self, path):
        stdout_write_flush(self.shorten("  " + path))

    def skip(self, path):
        stdout_write(self.shorten(CHAR_SKIP + path) + "\n")

    def success(self, path):
        stdout_write("\r" + self.shorten(CHAR_SUCCESS + path) + "\n")

    def progress(self, bytes_total, bytes_downloaded, bytes_per_second):
        bdl = util.format_value(bytes_downloaded)
        bps = util.format_value(bytes_per_second)
        if bytes_total is None:
            stderr_write("\r{:>7}B {:>7}B/s ".format(bdl, bps))
        else:
            stderr_write("\r{:>3}% {:>7}B {:>7}B/s ".format(
                bytes_downloaded * 100 // bytes_total, bdl, bps))


class ColorOutput(TerminalOutput):

    def __init__(self):
        TerminalOutput.__init__(self)

        colors = config.get(("output",), "colors") or {}
        self.color_skip = "\033[{}m".format(
            colors.get("skip", "2"))
        self.color_success = "\r\033[{}m".format(
            colors.get("success", "1;32"))

    def start(self, path):
        stdout_write_flush(self.shorten(path))

    def skip(self, path):
        stdout_write(self.color_skip + self.shorten(path) + "\033[0m\n")

    def success(self, path):
        stdout_write(self.color_success + self.shorten(path) + "\033[0m\n")


class CustomOutput():

    def __init__(self, options):

        fmt_skip = options.get("skip")
        fmt_start = options.get("start")
        fmt_success = options.get("success")
        off_skip = off_start = off_success = 0

        if isinstance(fmt_skip, list):
            off_skip, fmt_skip = fmt_skip
        if isinstance(fmt_start, list):
            off_start, fmt_start = fmt_start
        if isinstance(fmt_success, list):
            off_success, fmt_success = fmt_success

        shorten = config.get(("output",), "shorten", True)
        if shorten:
            func = shorten_string_eaw if shorten == "eaw" else shorten_string
            width = shutil.get_terminal_size().columns

            self._fmt_skip = self._make_func(
                func, fmt_skip, width - off_skip)
            self._fmt_start = self._make_func(
                func, fmt_start, width - off_start)
            self._fmt_success = self._make_func(
                func, fmt_success, width - off_success)
        else:
            self._fmt_skip = fmt_skip.format
            self._fmt_start = fmt_start.format
            self._fmt_success = fmt_success.format

        self._fmt_progress = (options.get("progress") or
                              "\r{0:>7}B {1:>7}B/s ").format
        self._fmt_progress_total = (options.get("progress-total") or
                                    "\r{3:>3}% {0:>7}B {1:>7}B/s ").format

    @staticmethod
    def _make_func(shorten, format_string, limit):
        fmt = format_string.format
        return lambda txt: fmt(shorten(txt, limit, CHAR_ELLIPSIES))

    def start(self, path):
        stdout_write_flush(self._fmt_start(path))

    def skip(self, path):
        stdout_write(self._fmt_skip(path))

    def success(self, path):
        stdout_write(self._fmt_success(path))

    def progress(self, bytes_total, bytes_downloaded, bytes_per_second):
        bdl = util.format_value(bytes_downloaded)
        bps = util.format_value(bytes_per_second)
        if bytes_total is None:
            stderr_write(self._fmt_progress(bdl, bps))
        else:
            stderr_write(self._fmt_progress_total(
                bdl, bps, util.format_value(bytes_total),
                bytes_downloaded * 100 // bytes_total))


class EAWCache(dict):

    def __missing__(self, key):
        width = self[key] = \
            2 if unicodedata.east_asian_width(key) in "WF" else 1
        return width


def shorten_string(txt, limit, sep="…"):
    """Limit width of 'txt'; assume all characters have a width of 1"""
    if len(txt) <= limit:
        return txt
    limit -= len(sep)
    return txt[:limit // 2] + sep + txt[-((limit+1) // 2):]


def shorten_string_eaw(txt, limit, sep="…", cache=EAWCache()):
    """Limit width of 'txt'; check for east-asian characters with width > 1"""
    char_widths = [cache[c] for c in txt]
    text_width = sum(char_widths)

    if text_width <= limit:
        # no shortening required
        return txt

    limit -= len(sep)
    if text_width == len(txt):
        # all characters have a width of 1
        return txt[:limit // 2] + sep + txt[-((limit+1) // 2):]

    # wide characters
    left = 0
    lwidth = limit // 2
    while True:
        lwidth -= char_widths[left]
        if lwidth < 0:
            break
        left += 1

    right = -1
    rwidth = (limit+1) // 2 + (lwidth + char_widths[left])
    while True:
        rwidth -= char_widths[right]
        if rwidth < 0:
            break
        right -= 1

    return txt[:left] + sep + txt[right+1:]


if util.WINDOWS:
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
