# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

__author__     = "Mike Fährmann"
__copyright__  = "Copyright 2014, 2015 Mike Fährmann"

__license__    = "GPLv2"
__version__    = "0.3.2"
__maintainer__ = "Mike Fährmann"
__email__      = "mike_faehrmann@web.de"

import os
import sys
import argparse
from . import config, download

def parse_cmdline_options():
    parser = argparse.ArgumentParser(
        description='Download images from various sources')
    parser.add_argument(
        "-c", "--config",
        default="~/.config/gallery/config", metavar="CFG",
        help="alternate configuration file"
    )
    parser.add_argument(
        "-d", "--dest",
        metavar="DEST",
        help="destination directory"
    )
    parser.add_argument(
        "-o", "--option",
        metavar="OPT", action="append", default=[],
        help="option value",
    )
    parser.add_argument(
        "urls",
        nargs="+", metavar="URL",
        help="url to download images from"
    )
    return parser.parse_args()

def main():
    config.load()
    args = parse_cmdline_options()
    for opt in args.option:
        try:
            key, value = opt.split("=", 1)
            config.set(key.split("."), value)
        except TypeError:
            pass
    dlmgr = download.DownloadManager(args)

    try:
        for url in args.urls:
            dlmgr.add(url)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
