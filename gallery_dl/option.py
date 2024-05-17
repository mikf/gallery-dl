# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Command line option parsing"""

import argparse
import logging
import sys
from . import job, util, version


class ConfigAction(argparse.Action):
    """Set argparse results as config values"""
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.options.append(((), self.dest, values))


class ConfigConstAction(argparse.Action):
    """Set argparse const values as config values"""
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.options.append(((), self.dest, self.const))


class AppendCommandAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None) or []
        val = self.const.copy()
        val["command"] = values
        items.append(val)
        setattr(namespace, self.dest, items)


class DeprecatedConfigConstAction(argparse.Action):
    """Set argparse const values as config values + deprecation warning"""
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stderr.write(
            "warning: {} is deprecated. Use {} instead.\n".format(
                "/".join(self.option_strings), self.choices))
        namespace.options.append(((), self.dest, self.const))


class ConfigParseAction(argparse.Action):
    """Parse KEY=VALUE config options"""
    def __call__(self, parser, namespace, values, option_string=None):
        key, value = _parse_option(values)
        key = key.split(".")  # splitting an empty string becomes [""]
        namespace.options.append((key[:-1], key[-1], value))


class PPParseAction(argparse.Action):
    """Parse KEY=VALUE post processor options"""
    def __call__(self, parser, namespace, values, option_string=None):
        key, value = _parse_option(values)
        namespace.options_pp[key] = value


class InputfileAction(argparse.Action):
    """Collect input files"""
    def __call__(self, parser, namespace, value, option_string=None):
        namespace.input_files.append((value, self.const))


class MtimeAction(argparse.Action):
    """Configure mtime post processors"""
    def __call__(self, parser, namespace, value, option_string=None):
        namespace.postprocessors.append({
            "name": "mtime",
            "value": "{" + (self.const or value) + "}",
        })


class UgoiraAction(argparse.Action):
    """Configure ugoira post processors"""
    def __call__(self, parser, namespace, value, option_string=None):
        if self.const:
            value = self.const
        else:
            value = value.strip().lower()

        if value in ("webm", "vp9"):
            pp = {
                "extension"        : "webm",
                "ffmpeg-args"      : ("-c:v", "libvpx-vp9",
                                      "-crf", "12",
                                      "-b:v", "0", "-an"),
            }
        elif value == "vp9-lossless":
            pp = {
                "extension"        : "webm",
                "ffmpeg-args"      : ("-c:v", "libvpx-vp9",
                                      "-lossless", "1",
                                      "-pix_fmt", "yuv420p", "-an"),
            }
        elif value == "vp8":
            pp = {
                "extension"        : "webm",
                "ffmpeg-args"      : ("-c:v", "libvpx",
                                      "-crf", "4",
                                      "-b:v", "5000k", "-an"),
            }
        elif value == "mp4":
            pp = {
                "extension"        : "mp4",
                "ffmpeg-args"      : ("-c:v", "libx264", "-an", "-b:v", "5M"),
                "libx264-prevent-odd": True,
            }
        elif value == "gif":
            pp = {
                "extension"        : "gif",
                "ffmpeg-args"      : ("-filter_complex", "[0:v] split [a][b];"
                                      "[a] palettegen [p];[b][p] paletteuse"),
                "repeat-last-frame": False,
            }
        elif value in ("mkv", "copy"):
            pp = {
                "extension"        : "mkv",
                "ffmpeg-args"      : ("-c:v", "copy"),
                "repeat-last-frame": False,
            }
        else:
            parser.error("Unsupported Ugoira format '{}'".format(value))

        pp["name"] = "ugoira"
        pp["whitelist"] = ("pixiv", "danbooru")

        namespace.options.append(((), "ugoira", True))
        namespace.postprocessors.append(pp)


class Formatter(argparse.HelpFormatter):
    """Custom HelpFormatter class to customize help output"""
    def __init__(self, prog):
        argparse.HelpFormatter.__init__(self, prog, max_help_position=30)

    def _format_action_invocation(self, action, join=", ".join):
        opts = action.option_strings
        if action.metavar:
            opts = opts.copy()
            opts[-1] += " " + action.metavar
        return join(opts)


def _parse_option(opt):
    key, _, value = opt.partition("=")
    try:
        value = util.json_loads(value)
    except ValueError:
        pass
    return key, value


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
        "-f", "--filename",
        dest="filename", metavar="FORMAT",
        help=("Filename format string for downloaded files "
              "('/O' for \"original\" filenames)"),
    )
    general.add_argument(
        "-d", "--destination",
        dest="base-directory", metavar="PATH", action=ConfigAction,
        help="Target location for file downloads",
    )
    general.add_argument(
        "-D", "--directory",
        dest="directory", metavar="PATH",
        help="Exact location for file downloads",
    )
    general.add_argument(
        "-X", "--extractors",
        dest="extractor_sources", metavar="PATH", action="append",
        help="Load external extractors from PATH",
    )
    general.add_argument(
        "--proxy",
        dest="proxy", metavar="URL", action=ConfigAction,
        help="Use the specified proxy",
    )
    general.add_argument(
        "--source-address",
        dest="source-address", metavar="IP", action=ConfigAction,
        help="Client-side IP address to bind to",
    )
    general.add_argument(
        "--user-agent",
        dest="user-agent", metavar="UA", action=ConfigAction,
        help="User-Agent request header",
    )
    general.add_argument(
        "--clear-cache",
        dest="clear_cache", metavar="MODULE",
        help="Delete cached login sessions, cookies, etc. for MODULE "
             "(ALL to delete everything)",
    )

    input = parser.add_argument_group("Input Options")
    input.add_argument(
        "urls",
        metavar="URL", nargs="*",
        help=argparse.SUPPRESS,
    )
    input.add_argument(
        "-i", "--input-file",
        dest="input_files", metavar="FILE", action=InputfileAction, const=None,
        default=[],
        help=("Download URLs found in FILE ('-' for stdin). "
              "More than one --input-file can be specified"),
    )
    input.add_argument(
        "-I", "--input-file-comment",
        dest="input_files", metavar="FILE", action=InputfileAction, const="c",
        help=("Download URLs found in FILE. "
              "Comment them out after they were downloaded successfully."),
    )
    input.add_argument(
        "-x", "--input-file-delete",
        dest="input_files", metavar="FILE", action=InputfileAction, const="d",
        help=("Download URLs found in FILE. "
              "Delete them after they were downloaded successfully."),
    )

    output = parser.add_argument_group("Output Options")
    output.add_argument(
        "-q", "--quiet",
        dest="loglevel", default=logging.INFO,
        action="store_const", const=logging.ERROR,
        help="Activate quiet mode",
    )
    output.add_argument(
        "-w", "--warning",
        dest="loglevel",
        action="store_const", const=logging.WARNING,
        help="Print only warnings and errors",
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
        "-G", "--resolve-urls",
        dest="list_urls", action="store_const", const=128,
        help="Print URLs instead of downloading; resolve intermediary URLs",
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
        "-E", "--extractor-info",
        dest="jobtype", action="store_const", const=job.InfoJob,
        help="Print extractor defaults and settings",
    )
    output.add_argument(
        "-K", "--list-keywords",
        dest="jobtype", action="store_const", const=job.KeywordJob,
        help=("Print a list of available keywords and example values "
              "for the given URLs"),
    )
    output.add_argument(
        "-e", "--error-file",
        dest="errorfile", metavar="FILE", action=ConfigAction,
        help="Add input URLs which returned an error to FILE",
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
    output.add_argument(
        "--write-pages",
        dest="write-pages", nargs=0, action=ConfigConstAction, const=True,
        help=("Write downloaded intermediary pages to files "
              "in the current directory to debug problems"),
    )
    output.add_argument(
        "--no-colors",
        dest="colors", action="store_false",
        help=("Do not emit ANSI color codes in output"),
    )

    downloader = parser.add_argument_group("Downloader Options")
    downloader.add_argument(
        "-r", "--limit-rate",
        dest="rate", metavar="RATE", action=ConfigAction,
        help="Maximum download rate (e.g. 500k or 2.5M)",
    )
    downloader.add_argument(
        "-R", "--retries",
        dest="retries", metavar="N", type=int, action=ConfigAction,
        help=("Maximum number of retries for failed HTTP requests "
              "or -1 for infinite retries (default: 4)"),
    )
    downloader.add_argument(
        "--http-timeout",
        dest="timeout", metavar="SECONDS", type=float, action=ConfigAction,
        help="Timeout for HTTP connections (default: 30.0)",
    )
    downloader.add_argument(
        "--sleep",
        dest="sleep", metavar="SECONDS", action=ConfigAction,
        help=("Number of seconds to wait before each download. "
              "This can be either a constant value or a range "
              "(e.g. 2.7 or 2.0-3.5)"),
    )
    downloader.add_argument(
        "--sleep-request",
        dest="sleep-request", metavar="SECONDS", action=ConfigAction,
        help=("Number of seconds to wait between HTTP requests "
              "during data extraction"),
    )
    downloader.add_argument(
        "--sleep-extractor",
        dest="sleep-extractor", metavar="SECONDS", action=ConfigAction,
        help=("Number of seconds to wait before starting data extraction "
              "for an input URL"),
    )
    downloader.add_argument(
        "--filesize-min",
        dest="filesize-min", metavar="SIZE", action=ConfigAction,
        help="Do not download files smaller than SIZE (e.g. 500k or 2.5M)",
    )
    downloader.add_argument(
        "--filesize-max",
        dest="filesize-max", metavar="SIZE", action=ConfigAction,
        help="Do not download files larger than SIZE (e.g. 500k or 2.5M)",
    )
    downloader.add_argument(
        "--chunk-size",
        dest="chunk-size", metavar="SIZE", action=ConfigAction,
        help="Size of in-memory data chunks (default: 32k)",
    )
    downloader.add_argument(
        "--no-part",
        dest="part", nargs=0, action=ConfigConstAction, const=False,
        help="Do not use .part files",
    )
    downloader.add_argument(
        "--no-skip",
        dest="skip", nargs=0, action=ConfigConstAction, const=False,
        help="Do not skip downloads; overwrite existing files",
    )
    downloader.add_argument(
        "--no-mtime",
        dest="mtime", nargs=0, action=ConfigConstAction, const=False,
        help=("Do not set file modification times according to "
              "Last-Modified HTTP response headers")
    )
    downloader.add_argument(
        "--no-download",
        dest="download", nargs=0, action=ConfigConstAction, const=False,
        help=("Do not download any files")
    )
    downloader.add_argument(
        "--no-postprocessors",
        dest="postprocess", nargs=0, action=ConfigConstAction, const=False,
        help=("Do not run any post processors")
    )
    downloader.add_argument(
        "--no-check-certificate",
        dest="verify", nargs=0, action=ConfigConstAction, const=False,
        help="Disable HTTPS certificate validation",
    )

    configuration = parser.add_argument_group("Configuration Options")
    configuration.add_argument(
        "-o", "--option",
        dest="options", metavar="KEY=VALUE",
        action=ConfigParseAction, default=[],
        help=("Additional options. "
              "Example: -o browser=firefox")   ,
    )
    configuration.add_argument(
        "-c", "--config",
        dest="configs_json", metavar="FILE", action="append",
        help="Additional configuration files",
    )
    configuration.add_argument(
        "--config-yaml",
        dest="configs_yaml", metavar="FILE", action="append",
        help="Additional configuration files in YAML format",
    )
    configuration.add_argument(
        "--config-toml",
        dest="configs_toml", metavar="FILE", action="append",
        help="Additional configuration files in TOML format",
    )
    configuration.add_argument(
        "--config-create",
        dest="config_init", action="store_true",
        help="Create a basic configuration file",
    )
    configuration.add_argument(
        "--config-ignore",
        dest="config_load", action="store_false",
        help="Do not read default configuration files",
    )
    configuration.add_argument(
        "--ignore-config",
        dest="config_load", action="store_false",
        help=argparse.SUPPRESS,
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

    cookies = parser.add_argument_group("Cookie Options")
    cookies.add_argument(
        "-C", "--cookies",
        dest="cookies", metavar="FILE", action=ConfigAction,
        help="File to load additional cookies from",
    )
    cookies.add_argument(
        "--cookies-export",
        dest="cookies-update", metavar="FILE", action=ConfigAction,
        help="Export session cookies to FILE",
    )
    cookies.add_argument(
        "--cookies-from-browser",
        dest="cookies_from_browser",
        metavar="BROWSER[/DOMAIN][+KEYRING][:PROFILE][::CONTAINER]",
        help=("Name of the browser to load cookies from, with optional "
              "domain prefixed with '/', "
              "keyring name prefixed with '+', "
              "profile prefixed with ':', and "
              "container prefixed with '::' ('none' for no container)"),
    )

    selection = parser.add_argument_group("Selection Options")
    selection.add_argument(
        "--download-archive",
        dest="archive", metavar="FILE", action=ConfigAction,
        help=("Record all downloaded or skipped files in FILE and "
              "skip downloading any file already in it"),
    )
    selection.add_argument(
        "-A", "--abort",
        dest="abort", metavar="N", type=int,
        help=("Stop current extractor run "
              "after N consecutive file downloads were skipped"),
    )
    selection.add_argument(
        "-T", "--terminate",
        dest="terminate", metavar="N", type=int,
        help=("Stop current and parent extractor runs "
              "after N consecutive file downloads were skipped"),
    )
    selection.add_argument(
        "--range",
        dest="image-range", metavar="RANGE", action=ConfigAction,
        help=("Index range(s) specifying which files to download. "
              "These can be either a constant value, range, or slice "
              "(e.g. '5', '8-20', or '1:24:3')"),
    )
    selection.add_argument(
        "--chapter-range",
        dest="chapter-range", metavar="RANGE", action=ConfigAction,
        help=("Like '--range', but applies to manga chapters "
              "and other delegated URLs"),
    )
    selection.add_argument(
        "--filter",
        dest="image-filter", metavar="EXPR", action=ConfigAction,
        help=("Python expression controlling which files to download. "
              "Files for which the expression evaluates to False are ignored. "
              "Available keys are the filename-specific ones listed by '-K'. "
              "Example: --filter \"image_width >= 1000 and "
              "rating in ('s', 'q')\""),
    )
    selection.add_argument(
        "--chapter-filter",
        dest="chapter-filter", metavar="EXPR", action=ConfigAction,
        help=("Like '--filter', but applies to manga chapters "
              "and other delegated URLs"),
    )

    infojson = {
        "name"    : "metadata",
        "event"   : "init",
        "filename": "info.json",
    }
    postprocessor = parser.add_argument_group("Post-processing Options")
    postprocessor.add_argument(
        "-P", "--postprocessor",
        dest="postprocessors", metavar="NAME", action="append", default=[],
        help="Activate the specified post processor",
    )
    postprocessor.add_argument(
        "-O", "--postprocessor-option",
        dest="options_pp", metavar="KEY=VALUE",
        action=PPParseAction, default={},
        help="Additional post processor options",
    )
    postprocessor.add_argument(
        "--write-metadata",
        dest="postprocessors",
        action="append_const", const="metadata",
        help="Write metadata to separate JSON files",
    )
    postprocessor.add_argument(
        "--write-info-json",
        dest="postprocessors",
        action="append_const", const=infojson,
        help="Write gallery metadata to a info.json file",
    )
    postprocessor.add_argument(
        "--write-infojson",
        dest="postprocessors",
        action="append_const", const=infojson,
        help=argparse.SUPPRESS,
    )
    postprocessor.add_argument(
        "--write-tags",
        dest="postprocessors",
        action="append_const", const={"name": "metadata", "mode": "tags"},
        help="Write image tags to separate text files",
    )
    postprocessor.add_argument(
        "--zip",
        dest="postprocessors",
        action="append_const", const="zip",
        help="Store downloaded files in a ZIP archive",
    )
    postprocessor.add_argument(
        "--cbz",
        dest="postprocessors",
        action="append_const", const={
            "name"     : "zip",
            "extension": "cbz",
        },
        help="Store downloaded files in a CBZ archive",
    )
    postprocessor.add_argument(
        "--mtime",
        dest="postprocessors", metavar="NAME", action=MtimeAction,
        help=("Set file modification times according to metadata "
              "selected by NAME. Examples: 'date' or 'status[date]'"),
    )
    postprocessor.add_argument(
        "--mtime-from-date",
        dest="postprocessors", nargs=0, action=MtimeAction,
        const="date|status[date]",
        help=argparse.SUPPRESS,
    )
    postprocessor.add_argument(
        "--ugoira",
        dest="postprocessors", metavar="FORMAT", action=UgoiraAction,
        help=("Convert Pixiv Ugoira to FORMAT using FFmpeg. "
              "Supported formats are 'webm', 'mp4', 'gif', "
              "'vp8', 'vp9', 'vp9-lossless', 'copy'."),
    )
    postprocessor.add_argument(
        "--ugoira-conv",
        dest="postprocessors", nargs=0, action=UgoiraAction, const="vp8",
        help=argparse.SUPPRESS,
    )
    postprocessor.add_argument(
        "--ugoira-conv-lossless",
        dest="postprocessors", nargs=0, action=UgoiraAction,
        const="vp9-lossless",
        help=argparse.SUPPRESS,
    )
    postprocessor.add_argument(
        "--ugoira-conv-copy",
        dest="postprocessors", nargs=0, action=UgoiraAction, const="copy",
        help=argparse.SUPPRESS,
    )
    postprocessor.add_argument(
        "--exec",
        dest="postprocessors", metavar="CMD",
        action=AppendCommandAction, const={"name": "exec"},
        help=("Execute CMD for each downloaded file. "
              "Supported replacement fields are "
              "{} or {_path}, {_directory}, {_filename}. "
              "Example: --exec \"convert {} {}.png && rm {}\""),
    )
    postprocessor.add_argument(
        "--exec-after",
        dest="postprocessors", metavar="CMD",
        action=AppendCommandAction, const={
            "name": "exec", "event": "finalize"},
        help=("Execute CMD after all files were downloaded. "
              "Example: --exec-after \"cd {_directory} "
              "&& convert * ../doc.pdf\""),
    )

    return parser
