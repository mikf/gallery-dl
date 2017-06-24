# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Command line option parsing"""

import argparse
import logging
import json
from .version import __version__

log = logging.getLogger("option")


class ConfigAction(argparse.Action):
    """Set argparse results as config values"""
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.options.append(((self.dest,), values))


class ConfigConstAction(argparse.Action):
    """Set argparse const values as config values"""
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.options.append(((self.dest,), self.const))


class ParseAction(argparse.Action):
    """Parse <key>=<value> options and set them as config values"""
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            key, value = values.split("=", 1)
            try:
                value = json.loads(value)
            except ValueError:
                pass
            key = key.split(".")
            namespace.options.append((key, value))
        except ValueError:
            log.warning("Invalid '<key>=<value>' pair: %s", values)


class Formatter(argparse.HelpFormatter):
    """Custom HelpFormatter class to customize help output"""
    def __init__(self, *args, **kwargs):
        super().__init__(max_help_position=50, *args, **kwargs)

    def _format_action_invocation(self, action):
        opts = action.option_strings[:]
        if opts:
            if action.nargs != 0:
                args_string = self._format_args(action, "ARG")
                opts[-1] += " " + args_string
            return ', '.join(opts)
        else:
            return self._metavar_formatter(action, action.dest)(1)[0]


def build_parser():
    """Build and configure an ArgumentParser object"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]... URL...",
        formatter_class=Formatter,
    )
    parser.add_argument(
        "-g", "--get-urls", dest="list_urls", action="count",
        help="Print URLs instead of downloading",
    )
    parser.add_argument(
        "-j", "--dump-json", dest="list_data", action="store_true",
        help="Print JSON information",
    )
    parser.add_argument(
        "-d", "--dest",
        metavar="DEST", action=ConfigAction, dest="base-directory",
        help="Destination directory",
    )
    parser.add_argument(
        "-u", "--username",
        metavar="USER", action=ConfigAction, dest="username",
    )
    parser.add_argument(
        "-p", "--password",
        metavar="PASS", action=ConfigAction, dest="password",
    )
    parser.add_argument(
        "--netrc",
        action=ConfigConstAction, nargs=0, dest="netrc", const=True,
        help="Use .netrc authentication data",
    )
    parser.add_argument(
        "-i", "--input-file",
        metavar="FILE", dest="inputfile",
        help="Download URLs found in local FILE ('-' for stdin)",
    )
    parser.add_argument(
        "--images",
        metavar="ITEM-SPEC", action=ConfigAction, dest="images",
        help=("Specify which images to download through a comma seperated list"
              " of indices or index-ranges; "
              "for example '--images -2,4,6-8,10-' will download images with "
              "index 1, 2, 4, 6, 7, 8 and 10 up to the last one")
    )
    parser.add_argument(
        "--chapters",
        metavar="ITEM-SPEC", action=ConfigAction, dest="chapters",
        help=("Same as '--images' except for chapters")
    )
    parser.add_argument(
        "--abort-on-skip",
        action=ConfigConstAction, nargs=0, dest="skip", const="abort",
        help=("Abort extractor run if a file download would normally be "
              "skipped, i.e. if a file with the same filename already exists")
    )
    parser.add_argument(
        "-R", "--retries",
        metavar="RETRIES", action=ConfigAction, dest="retries", type=int,
        help="Number of retries (default: 5)",
    )
    parser.add_argument(
        "--http-timeout",
        metavar="SECONDS", action=ConfigAction, dest="timeout", type=float,
        help="Timeout for HTTP connections (defaut: no timeout)",
    )
    parser.add_argument(
        "-c", "--config",
        metavar="CFG", dest="cfgfiles", action="append",
        help="Additional configuration files",
    )
    parser.add_argument(
        "--config-yaml",
        metavar="CFG", dest="yamlfiles", action="append",
        help="Additional configuration files (YAML format)",
    )
    parser.add_argument(
        "--ignore-config", dest="load_config", action="store_false",
        help="Do not read the default configuration files",
    )
    parser.add_argument(
        "-o", "--option",
        metavar="OPT", action=ParseAction, dest="options", default=[],
        help="Additional '<key>=<value>' option values",
    )
    parser.add_argument(
        "--write-unsupported", metavar="FILE", dest="unsupportedfile",
        help=("Write URLs, which get emitted by other extractors but cannot "
              "be handled, to FILE"),
    )
    parser.add_argument(
        "--list-extractors", dest="list_extractors", action="store_true",
        help=("Print a list of extractor classes "
              "with description and example URL"),
    )
    parser.add_argument(
        "--list-keywords", dest="list_keywords", action="store_true",
        help="Print a list of available keywords for the given URLs",
    )
    parser.add_argument(
        "--list-modules", dest="list_modules", action="store_true",
        help="Print a list of available modules/supported sites",
    )
    parser.add_argument(
        "-q", "--quiet", dest="loglevel", action="store_const",
        const=logging.ERROR, default=logging.INFO,
        help="Activate quiet mode",
    )
    parser.add_argument(
        "-v", "--verbose", dest="loglevel", action="store_const",
        const=logging.DEBUG, default=logging.INFO,
        help="Print various debugging information",
    )
    parser.add_argument(
        "--version", action="version", version=__version__,
        help="Print program version and exit"
    )
    parser.add_argument(
        "urls",
        nargs="*", metavar="URL",
        help="Url to download images from"
    )
    return parser
