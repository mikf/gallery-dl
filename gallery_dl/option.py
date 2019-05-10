# -*- coding: utf-8 -*-

# Copyright 2017-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Command line option parsing"""

import argparse
import logging
import json
from . import job, version


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
        key, _, value = values.partition("=")
        try:
            value = json.loads(value)
        except ValueError:
            pass
        key = key.split(".")
        namespace.options.append((key, value))


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
        add_help=False,
    )

    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-h", "--help",
        action="help",
        help="Print this help message and exit",
    )
    general.add_argument(
        "--version",
        action="version", version=version.__version__,
        help="Print program version and exit",
    )
    general.add_argument(
        "-d", "--dest",
        dest="base-directory", metavar="DEST", action=ConfigAction,
        help="Destination directory",
    )
    general.add_argument(
        "-i", "--input-file",
        dest="inputfile", metavar="FILE",
        help="Download URLs found in FILE ('-' for stdin)",
    )
    general.add_argument(
        "--cookies",
        dest="cookies", metavar="FILE", action=ConfigAction,
        help="File to load additional cookies from",
    )
    general.add_argument(
        "--proxy",
        dest="proxy", metavar="URL", action=ConfigAction,
        help="Use the specified proxy",
    )
    general.add_argument(
        "--clear-cache",
        dest="clear_cache", action="store_true",
        help="Delete all cached login sessions, cookies, etc.",
    )

    output = parser.add_argument_group("Output Options")
    output.add_argument(
        "-q", "--quiet",
        dest="loglevel", default=logging.INFO,
        action="store_const", const=logging.ERROR,
        help="Activate quiet mode",
    )
    output.add_argument(
        "-v", "--verbose",
        dest="loglevel",
        action="store_const", const=logging.DEBUG,
        help="Print various debugging information",
    )
    output.add_argument(
        "-g", "--get-urls",
        dest="list_urls", action="count",
        help="Print URLs instead of downloading",
    )
    output.add_argument(
        "-j", "--dump-json",
        dest="jobtype", action="store_const", const=job.DataJob,
        help="Print JSON information",
    )
    output.add_argument(
        "-s", "--simulate",
        dest="jobtype", action="store_const", const=job.SimulationJob,
        help="Simulate data extraction; do not download anything",
    )
    output.add_argument(
        "-K", "--list-keywords",
        dest="jobtype", action="store_const", const=job.KeywordJob,
        help=("Print a list of available keywords and example values "
              "for the given URLs"),
    )
    output.add_argument(
        "--list-modules",
        dest="list_modules", action="store_true",
        help="Print a list of available extractor modules",
    )
    output.add_argument(
        "--list-extractors",
        dest="list_extractors", action="store_true",
        help=("Print a list of extractor classes "
              "with description, (sub)category and example URL"),
    )
    output.add_argument(
        "--write-log",
        dest="logfile", metavar="FILE", action=ConfigAction,
        help="Write logging output to FILE",
    )
    output.add_argument(
        "--write-unsupported",
        dest="unsupportedfile", metavar="FILE", action=ConfigAction,
        help=("Write URLs, which get emitted by other extractors but cannot "
              "be handled, to FILE"),
    )

    downloader = parser.add_argument_group("Downloader Options")
    downloader.add_argument(
        "-r", "--limit-rate",
        dest="rate", metavar="RATE", action=ConfigAction,
        help="Maximum download rate (e.g. 500k or 2.5M)",
    )
    downloader.add_argument(
        "-R", "--retries",
        dest="retries", metavar="RETRIES", type=int, action=ConfigAction,
        help="Number of retries (default: 5)",
    )
    downloader.add_argument(
        "--http-timeout",
        dest="timeout", metavar="SECONDS", type=float, action=ConfigAction,
        help="Timeout for HTTP connections (defaut: 30.0)",
    )
    downloader.add_argument(
        "--sleep",
        dest="sleep", metavar="SECONDS", type=float, action=ConfigAction,
        help="Number of seconds to sleep before each download",
    )
    downloader.add_argument(
        "--no-part",
        dest="part", nargs=0, action=ConfigConstAction, const=False,
        help="Do not use .part files",
    )
    downloader.add_argument(
        "--no-check-certificate",
        dest="verify", nargs=0, action=ConfigConstAction, const=False,
        help="Disable HTTPS certificate validation",
    )
    downloader.add_argument(
        "--abort-on-skip",
        dest="skip", nargs=0, action=ConfigConstAction, const="abort",
        help=("Abort extractor run if a file download would normally be "
              "skipped, i.e. if a file with the same filename already exists"),
    )

    configuration = parser.add_argument_group("Configuration Options")
    configuration.add_argument(
        "-c", "--config",
        dest="cfgfiles", metavar="FILE", action="append",
        help="Additional configuration files",
    )
    configuration.add_argument(
        "--config-yaml",
        dest="yamlfiles", metavar="FILE", action="append",
        help=argparse.SUPPRESS,
    )
    configuration.add_argument(
        "-o", "--option",
        dest="options", metavar="OPT", action=ParseAction, default=[],
        help="Additional '<key>=<value>' option values",
    )
    configuration.add_argument(
        "--ignore-config",
        dest="load_config", action="store_false",
        help="Do not read the default configuration files",
    )

    authentication = parser.add_argument_group("Authentication Options")
    authentication.add_argument(
        "-u", "--username",
        dest="username", metavar="USER", action=ConfigAction,
        help="Username to login with",
    )
    authentication.add_argument(
        "-p", "--password",
        dest="password", metavar="PASS", action=ConfigAction,
        help="Password belonging to the given username",
    )
    authentication.add_argument(
        "--netrc",
        dest="netrc", nargs=0, action=ConfigConstAction, const=True,
        help="Enable .netrc authentication data",
    )

    selection = parser.add_argument_group("Selection Options")
    selection.add_argument(
        "--download-archive",
        dest="archive", metavar="FILE", action=ConfigAction,
        help=("Record all downloaded files in the archive file and "
              "skip downloading any file already in it."),
    )
    selection.add_argument(
        "--range",
        dest="image-range", metavar="RANGE", action=ConfigAction,
        help=("Index-range(s) specifying which images to download. "
              "For example '5-10' or '1,3-5,10-'"),
    )
    selection.add_argument(
        "--chapter-range",
        dest="chapter-range", metavar="RANGE", action=ConfigAction,
        help=("Like '--range', but applies to manga-chapters "
              "and other delegated URLs"),
    )
    selection.add_argument(
        "--filter",
        dest="image-filter", metavar="EXPR", action=ConfigAction,
        help=("Python expression controlling which images to download. "
              "Files for which the expression evaluates to False are ignored. "
              "Available keys are the filename-specific ones listed by '-K'. "
              "Example: --filter \"image_width >= 1000 and "
              "rating in ('s', 'q')\""),
    )
    selection.add_argument(
        "--chapter-filter",
        dest="chapter-filter", metavar="EXPR", action=ConfigAction,
        help=("Like '--filter', but applies to manga-chapters "
              "and other delegated URLs"),
    )

    postprocessor = parser.add_argument_group("Post-processing Options")
    postprocessor.add_argument(
        "--zip",
        dest="postprocessors",
        action="append_const", const={"name": "zip"},
        help="Store downloaded files in a ZIP archive",
    )
    postprocessor.add_argument(
        "--ugoira-conv",
        dest="postprocessors",
        action="append_const", const={"name": "ugoira", "ffmpeg-args": (
            "-c:v", "libvpx", "-crf", "4", "-b:v", "5000k", "-an")},
        help="Convert Pixiv Ugoira to WebM (requires FFmpeg)",
    )
    postprocessor.add_argument(
        "--write-metadata",
        dest="postprocessors",
        action="append_const", const={"name": "metadata"},
        help="Write metadata to separate JSON files",
    )
    postprocessor.add_argument(
        "--write-tags",
        dest="postprocessors",
        action="append_const", const={"name": "metadata", "mode": "tags"},
        help="Write image tags to separate text files",
    )

    parser.add_argument(
        "urls",
        metavar="URL", nargs="*",
        help=argparse.SUPPRESS,
    )

    return parser
