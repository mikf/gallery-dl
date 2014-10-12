__author__     = "Mike Fährmann"
__copyright__  = "Copyright 2014, Mike Fährmann"

__license__    = "GPLv3"
__version__    = "0.4"
__maintainer__ = "Mike Fährmann"
__email__      = "mike_faehrmann@web.de"

import os
import sys
import argparse
import configparser

from . import extractor
from . import downloader

def parse_cmdline_options():
    p = argparse.ArgumentParser(
        description='Download images from various sources')
    p.add_argument("-c", "--config",
        default="~/.config/gallery/config", metavar="CFG", help="alternate configuration file")
    p.add_argument("-d", "--dest",
        metavar="DEST", help="destination directory")
    p.add_argument("urls", nargs="+",
        metavar="URL", help="url to download images from")
    return p.parse_args()

def parse_config_file(path):
    config = configparser.ConfigParser(
        interpolation=None,
    )
    config.optionxform = lambda opt:opt
    config.read(os.path.expanduser(path))
    return config

def main():
    opts = parse_cmdline_options()
    conf = parse_config_file(opts.config)
    extf = extractor.ExtractorFinder(conf)
    dlmg = downloader.DownloadManager(opts, conf)

    for url in opts.urls:
        ex = extf.match(url)
        dlmg.add(ex)
