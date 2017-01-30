# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
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

import argparse
import json
from . import config, extractor, job, exception
from .version import __version__


def build_cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Download images from various sources')
    parser.add_argument(
        "-g", "--get-urls", dest="list_urls", action="store_true",
        help="print download urls",
    )
    parser.add_argument(
        "-d", "--dest",
        metavar="DEST",
        help="destination directory",
    )
    parser.add_argument(
        "-u", "--username",
        metavar="USER"
    )
    parser.add_argument(
        "-p", "--password",
        metavar="PASS"
    )
    parser.add_argument(
        "-i", "--input-file",
        metavar="FILE", dest="inputfile",
        help="download URLs found in local FILE",
    )
    parser.add_argument(
        "-c", "--config",
        metavar="CFG", dest="cfgfiles", action="append",
        help="additional configuration files",
    )
    parser.add_argument(
        "-o", "--option",
        metavar="OPT", action="append", default=[],
        help="additional 'key=value' option values",
    )
    parser.add_argument(
        "--list-extractors", dest="list_extractors", action="store_true",
        help=("print a list of extractor classes "
              "with description and example URL"),
    )
    parser.add_argument(
        "--list-keywords", dest="list_keywords", action="store_true",
        help="print a list of available keywords for the given URLs",
    )
    parser.add_argument(
        "--list-modules", dest="list_modules", action="store_true",
        help="print a list of available modules/supported sites",
    )
    parser.add_argument(
        "--version", action="version", version=__version__,
        help="print program version and exit"
    )
    parser.add_argument(
        "urls",
        nargs="*", metavar="URL",
        help="url to download images from"
    )
    return parser


def parse_option(opt):
    try:
        key, value = opt.split("=", 1)
        try:
            value = json.loads(value)
        except ValueError:
            pass
        config.set(key.split("."), value)
    except ValueError:
        print("Invalid 'key=value' pair:", opt, file=sys.stderr)


def sanatize_input(file):
    for line in file:
        line = line.strip()
        if line:
            yield line


def main():
    try:
        config.load()
        parser = build_cmdline_parser()
        args = parser.parse_args()

        if args.cfgfiles:
            config.load(*args.cfgfiles, strict=True)

        if args.dest:
            config.set(("base-directory",), args.dest)
        if args.username:
            config.set(("username",), args.username)
        if args.password:
            config.set(("password",), args.password)

        for opt in args.option:
            parse_option(opt)

        if args.list_modules:
            for module_name in extractor.modules:
                print(module_name)
        elif args.list_extractors:
            for extr in extractor.extractors():
                print(extr.__name__)
                if extr.__doc__:
                    print(extr.__doc__)
                if hasattr(extr, "test") and extr.test:
                    print("Example:", extr.test[0][0])
                print()
        else:
            if not args.urls and not args.inputfile:
                parser.error("the following arguments are required: URL")

            if args.list_urls:
                jobtype = job.UrlJob
            elif args.list_keywords:
                jobtype = job.KeywordJob
            else:
                jobtype = job.DownloadJob

            urls = args.urls
            if args.inputfile:
                try:
                    if args.inputfile == "-":
                        file = sys.stdin
                    else:
                        file = open(args.inputfile)
                    import itertools
                    urls = itertools.chain(urls, sanatize_input(file))
                except OSError as e:
                    print(e)

            for url in urls:
                try:
                    jobtype(url).run()
                except exception.NoExtractorError:
                    print("No suitable extractor found for URL '", url, "'",
                          sep="", file=sys.stderr)
                except exception.AuthenticationError:
                    print("Authentication failed. Please provide a valid "
                          "username/password pair.", file=sys.stderr)
                except exception.AuthorizationError:
                    print("You do not have permission to access the resource ",
                          "at '", url, "'", sep="", file=sys.stderr)
                except exception.NotFoundError as err:
                    res = str(err) or "resource (gallery/image/user)"
                    print("The ", res, " at '", url, "' does not exist",
                          sep="", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt", file=sys.stderr)
    except BrokenPipeError:
        pass
    except IOError as err:
        import errno
        if err.errno != errno.EPIPE:
            raise
