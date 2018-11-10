# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from __future__ import unicode_literals, print_function

__author__ = "Mike Fährmann"
__copyright__ = "Copyright 2014-2018 Mike Fährmann"
__license__ = "GPLv2"
__maintainer__ = "Mike Fährmann"
__email__ = "mike_faehrmann@web.de"

import sys

if sys.hexversion < 0x3040000:
    sys.exit("Python 3.4+ required")

import json
import logging
from . import version, config, option, extractor, job, util, exception

__version__ = version.__version__
log = logging.getLogger("gallery-dl")

LOG_FORMAT = "[{name}][{levelname}] {message}"
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO

def initialize_logging(loglevel):
    """Setup basic logging functionality before configfiles have been loaded"""
    # convert levelnames to lowercase
    for level in (10, 20, 30, 40, 50):
        name = logging.getLevelName(level)
        logging.addLevelName(level, name.lower())
    # setup basic logging to stderr
    formatter = logging.Formatter(LOG_FORMAT, LOG_FORMAT_DATE, "{")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(loglevel)
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    root.addHandler(handler)


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
        log.warning("%s: %s", key, exc)
        return None
    except TypeError as exc:
        log.warning("%s: missing or invalid path (%s)", key, exc)
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


def progress(urls, pformat):
    """Wrapper around urls to output a simple progress indicator"""
    if pformat is True:
        pformat = "[{current}/{total}] {url}"
    pinfo = {"total": len(urls)}
    for pinfo["current"], pinfo["url"] in enumerate(urls, 1):
        print(pformat.format_map(pinfo), file=sys.stderr)
        yield pinfo["url"]


def parse_inputfile(file):
    """Filter and process strings from an input file.

    Lines starting with '#' and empty lines will be ignored.
    Lines starting with '-' will be interpreted as a key-value pair separated
      by an '='. where 'key' is a dot-separated option name and 'value' is a
      JSON-parsable value for it. These config options will be applied while
      processing the next URL.
    Lines starting with '-G' are the same as above, except these options will
      be valid for all following URLs, i.e. they are Global.
    Everything else will be used as potential URL.

    Example input file:

    # settings global options
    -G base-directory = "/tmp/"
    -G skip = false

    # setting local options for the next URL
    -filename="spaces_are_optional.jpg"
    -skip    = true

    https://example.org/

    # next URL uses default filename and 'skip' is false.
    https://example.com/index.htm
    """
    gconf = []
    lconf = []

    for line in file:
        line = line.strip()

        if not line or line[0] == "#":
            # empty line or comment
            continue

        elif line[0] == "-":
            # config spec
            if len(line) >= 2 and line[1] == "G":
                conf = gconf
                line = line[2:]
            else:
                conf = lconf
                line = line[1:]

            key, sep, value = line.partition("=")
            if not sep:
                log.warning("input file: invalid <key>=<value> pair: %s", line)
                continue

            try:
                value = json.loads(value.strip())
            except ValueError as exc:
                log.warning("input file: unable to parse '%s': %s", value, exc)
                continue

            conf.append((key.strip().split("."), value))

        else:
            # url
            if gconf or lconf:
                yield util.ExtendedUrl(line, gconf, lconf)
                gconf = []
                lconf = []
            else:
                yield line


def main():
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            replace_std_streams()

        parser = option.build_parser()
        args = parser.parse_args()

        initialize_logging(args.loglevel)

        # configuration
        if args.load_config:
            config.load()
        if args.cfgfiles:
            config.load(*args.cfgfiles, strict=True)
        if args.yamlfiles:
            config.load(*args.yamlfiles, format="yaml", strict=True)
        for key, value in args.options:
            config.set(key, value)
        config.set(("_",), {})

        # stream logging handler
        configure_logging_handler("log", logging.getLogger().handlers[0])

        # file logging handler
        handler = setup_logging_handler("logfile", lvl=args.loglevel)
        if handler:
            logging.getLogger().addHandler(handler)

        # loglevels
        if args.loglevel >= logging.ERROR:
            config.set(("output", "mode"), "null")
        elif args.loglevel <= logging.DEBUG:
            import platform
            import subprocess
            import os.path
            import requests

            head = ""
            try:
                out, err = subprocess.Popen(
                    ("git",  "rev-parse", "--short", "HEAD"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                ).communicate()
                if out and not err:
                    head = " - Git HEAD: " + out.decode().rstrip()
            except (OSError, subprocess.SubprocessError):
                pass

            log.debug("Version %s%s", __version__, head)
            log.debug("Python %s - %s",
                      platform.python_version(), platform.platform())
            try:
                log.debug("requests %s - urllib3 %s",
                          requests.__version__,
                          requests.packages.urllib3.__version__)
            except AttributeError:
                pass

        if args.list_modules:
            for module_name in extractor.modules:
                print(module_name)
        elif args.list_extractors:
            for extr in extractor.extractors():
                if not extr.__doc__:
                    continue
                print(extr.__name__)
                print(extr.__doc__)
                print("Category:", extr.category,
                      "- Subcategory:", extr.subcategory)
                if hasattr(extr, "test") and extr.test:
                    print("Example :", extr.test[0][0])
                print()
        else:
            if not args.urls and not args.inputfile:
                parser.error(
                    "The following arguments are required: URL\n"
                    "Use 'gallery-dl --help' to get a list of all options.")

            if args.list_urls:
                jobtype = job.UrlJob
                jobtype.maxdepth = args.list_urls
            elif args.list_keywords:
                jobtype = job.KeywordJob
            elif args.list_data:
                jobtype = job.DataJob
            elif args.simulate:
                jobtype = job.SimulationJob
            else:
                jobtype = job.DownloadJob

            urls = args.urls
            if args.inputfile:
                try:
                    if args.inputfile == "-":
                        file = sys.stdin
                    else:
                        file = open(args.inputfile, encoding="utf-8")
                    urls += parse_inputfile(file)
                    file.close()
                except OSError as exc:
                    log.warning("input file: %s", exc)

            # unsupported file logging handler
            handler = setup_logging_handler("unsupportedfile", fmt="{message}")
            if handler:
                ulog = logging.getLogger("unsupported")
                ulog.addHandler(handler)
                ulog.propagate = False
                job.Job.ulog = ulog

            pformat = config.get(("output", "progress"), True)
            if pformat and len(urls) > 1 and args.loglevel < logging.ERROR:
                urls = progress(urls, pformat)

            for url in urls:
                try:
                    log.debug("Starting %s for '%s'", jobtype.__name__, url)
                    if isinstance(url, util.ExtendedUrl):
                        for key, value in url.gconfig:
                            config.set(key, value)
                        with config.apply(url.lconfig):
                            jobtype(url.value).run()
                    else:
                        jobtype(url).run()
                except exception.NoExtractorError:
                    log.error("No suitable extractor found for '%s'", url)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt", file=sys.stderr)
    except BrokenPipeError:
        pass
    except IOError as exc:
        import errno
        if exc.errno != errno.EPIPE:
            raise
