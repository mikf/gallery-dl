# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from __future__ import unicode_literals, print_function

__author__ = "Mike Fährmann"
__copyright__ = "Copyright 2014-2017 Mike Fährmann"
__license__ = "GPLv2"
__maintainer__ = "Mike Fährmann"
__email__ = "mike_faehrmann@web.de"

import sys

if sys.hexversion < 0x3030000:
    print("Python 3.3+ required", file=sys.stderr)
    sys.exit(1)

import json
import logging
from . import version, config, option, extractor, job, util, exception

__version__ = version.__version__
log = logging.getLogger("gallery-dl")


def initialize_logging(loglevel, formatter):
    """Setup basic logging functionality before configfiles have been loaded"""
    # convert levelnames to lowercase
    for level in (10, 20, 30, 40, 50):
        name = logging.getLevelName(level)
        logging.addLevelName(level, name.lower())
    # setup basic logging to stderr
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(loglevel)
    root.addHandler(handler)


def progress(urls, pformat):
    """Wrapper around urls to output a simple progress indicator"""
    if pformat is True:
        pformat = "[{current}/{total}] {url}"
    pinfo = {"total": len(urls)}
    for pinfo["current"], pinfo["url"] in enumerate(urls, 1):
        print(pformat.format_map(pinfo), file=sys.stderr)
        yield pinfo["url"]


def prepare_range(rangespec, target):
    if rangespec:
        range = util.optimize_range(util.parse_range(rangespec))
        if range:
            config.set(("_", target, "range"), range)
        else:
            log.warning("invalid/empty %s range", target)


def prepare_filter(filterexpr, target):
    if filterexpr:
        try:
            name = "<{} filter>".format(target)
            codeobj = compile(filterexpr, name, "eval")
            config.set(("_", target, "filter"), codeobj)
        except (SyntaxError, ValueError, TypeError) as exc:
            log.warning(exc)


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
        parser = option.build_parser()
        args = parser.parse_args()

        formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
        initialize_logging(args.loglevel, formatter)

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

        # logfile
        logfile = config.interpolate(("output", "logfile"))
        if logfile:
            try:
                path = util.expand_path(logfile)
                handler = logging.FileHandler(path, "w")
            except OSError as exc:
                log.warning("log file: %s", exc)
            else:
                handler.setFormatter(formatter)
                logging.getLogger().addHandler(handler)

        # loglevels
        if args.loglevel >= logging.ERROR:
            config.set(("output", "mode"), "null")
        elif args.loglevel <= logging.DEBUG:
            import platform
            import requests
            log.debug("Version %s", __version__)
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
            else:
                jobtype = job.DownloadJob

            urls = args.urls
            if args.inputfile:
                try:
                    if args.inputfile == "-":
                        file = sys.stdin
                    else:
                        file = open(args.inputfile)
                    urls += parse_inputfile(file)
                    file.close()
                except OSError as exc:
                    log.warning("input file: %s", exc)

            unsupportedfile = config.interpolate(("output", "unsupportedfile"))
            if unsupportedfile:
                try:
                    path = util.expand_path(unsupportedfile)
                    job.Job.ufile = open(path, "w")
                except OSError as exc:
                    log.warning("unsupported-URL file: %s", exc)

            prepare_range(args.image_range, "image")
            prepare_range(args.chapter_range, "chapter")
            prepare_filter(args.image_filter, "image")
            prepare_filter(args.chapter_filter, "chapter")

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
