# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

__author__     = "Mike Fährmann"
__copyright__  = "Copyright 2014, 2015 Mike Fährmann"

__license__    = "GPLv2"
__version__    = "0.3.3"
__maintainer__ = "Mike Fährmann"
__email__      = "mike_faehrmann@web.de"

import os
import sys
import argparse
from . import config, jobs

def build_cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Download images from various sources')
    parser.add_argument(
        "-c", "--config",
        metavar="CFG", dest="cfgfiles", action="append",
        help="additional configuration files",
    )
    parser.add_argument(
        "-d", "--dest",
        metavar="DEST",
        help="destination directory",
    )
    parser.add_argument(
        "-o", "--option",
        metavar="OPT", action="append", default=[],
        help="option value",
    )
    parser.add_argument(
        "--list-modules", dest="list_modules", action="store_true",
        help="print a list of available modules/supported sites",
    )
    parser.add_argument(
        "--list-keywords", dest="keywords", action="store_true",
        help="print a list of available keywords for the given URLs",
    )
    parser.add_argument(
        "urls",
        nargs="*", metavar="URL",
        help="url to download images from"
    )
    return parser

def main():
    try:
        config.load()
        parser = build_cmdline_parser()
        args = parser.parse_args()

        if args.cfgfiles:
            config.load(*args.cfgfiles, strict=True)

        if args.dest:
            config.set(("base-directory",), args.dest)

        for opt in args.option:
            try:
                key, value = opt.split("=", 1)
                config.set(key.split("."), value)
            except TypeError:
                pass

        if args.list_modules:
            for module_name in extractor.modules:
                print(module_name)
        else:
            if not args.urls:
                parser.error("the following arguments are required: URL")
            jobtype = jobs.KeywordJob if args.keywords else jobs.DownloadJob
            for url in args.urls:
                jobtype(url).run()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
