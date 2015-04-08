# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

__author__     = "Mike Fährmann"
__copyright__  = "Copyright 2014, 2015 Mike Fährmann"

__license__    = "GPLv2"
__version__    = "0.2"
__maintainer__ = "Mike Fährmann"
__email__      = "mike_faehrmann@web.de"

import os
import sys
import argparse
import configparser

from .download import DownloadManager

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
        "urls",
        nargs="+", metavar="URL",
        help="url to download images from"
    )
    return parser.parse_args()

def parse_config_file(path):
    config = configparser.ConfigParser(
        interpolation=None,
    )
    config.optionxform = lambda opt: opt
    config.read(os.path.expanduser(path))
    return config

def main():
    opts = parse_cmdline_options()
    conf = parse_config_file(opts.config)
    dlmgr = DownloadManager(opts, conf)

    for url in opts.urls:
        dlmgr.add(url)
