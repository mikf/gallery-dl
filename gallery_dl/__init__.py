# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import logging
from . import version, config, option, output, extractor, job, util, exception

__author__ = "Mike Fährmann"
__copyright__ = "Copyright 2014-2023 Mike Fährmann"
__license__ = "GPLv2"
__maintainer__ = "Mike Fährmann"
__email__ = "mike_faehrmann@web.de"
__version__ = version.__version__


def main():
    try:
        parser = option.build_parser()
        args = parser.parse_args()
        log = output.initialize_logging(args.loglevel)

        # configuration
        if args.config_load:
            config.load()
        if args.configs_json:
            config.load(args.configs_json, strict=True)
        if args.configs_yaml:
            import yaml
            config.load(args.configs_yaml, strict=True, loads=yaml.safe_load)
        if args.configs_toml:
            try:
                import tomllib as toml
            except ImportError:
                import toml
            config.load(args.configs_toml, strict=True, loads=toml.loads)
        if not args.colors:
            output.ANSI = False
            config.set((), "colors", False)
            if util.WINDOWS:
                config.set(("output",), "ansi", False)
        if args.filename:
            filename = args.filename
            if filename == "/O":
                filename = "{filename}.{extension}"
            elif filename.startswith("\\f"):
                filename = "\f" + filename[2:]
            config.set((), "filename", filename)
        if args.directory is not None:
            config.set((), "base-directory", args.directory)
            config.set((), "directory", ())
        if args.postprocessors:
            config.set((), "postprocessors", args.postprocessors)
        if args.abort:
            config.set((), "skip", "abort:" + str(args.abort))
        if args.terminate:
            config.set((), "skip", "terminate:" + str(args.terminate))
        if args.cookies_from_browser:
            browser, _, profile = args.cookies_from_browser.partition(":")
            browser, _, keyring = browser.partition("+")
            browser, _, domain = browser.partition("/")
            if profile.startswith(":"):
                container = profile[1:]
                profile = None
            else:
                profile, _, container = profile.partition("::")
            config.set((), "cookies", (
                browser, profile, keyring, container, domain))
        if args.options_pp:
            config.set((), "postprocessor-options", args.options_pp)
        for opts in args.options:
            config.set(*opts)

        output.configure_standard_streams()

        # signals
        signals = config.get((), "signals-ignore")
        if signals:
            import signal
            if isinstance(signals, str):
                signals = signals.split(",")
            for signal_name in signals:
                signal_num = getattr(signal, signal_name, None)
                if signal_num is None:
                    log.warning("signal '%s' is not defined", signal_name)
                else:
                    signal.signal(signal_num, signal.SIG_IGN)

        # enable ANSI escape sequences on Windows
        if util.WINDOWS and config.get(("output",), "ansi", True):
            from ctypes import windll, wintypes, byref
            kernel32 = windll.kernel32
            mode = wintypes.DWORD()

            for handle_id in (-11, -12):  # stdout and stderr
                handle = kernel32.GetStdHandle(handle_id)
                kernel32.GetConsoleMode(handle, byref(mode))
                if not mode.value & 0x4:
                    mode.value |= 0x4
                    kernel32.SetConsoleMode(handle, mode)

            output.ANSI = True

        # format string separator
        separator = config.get((), "format-separator")
        if separator:
            from . import formatter
            formatter._SEPARATOR = separator

        # eval globals
        path = config.get((), "globals")
        if path:
            util.GLOBALS.update(util.import_file(path).__dict__)

        # loglevels
        output.configure_logging(args.loglevel)
        if args.loglevel >= logging.WARNING:
            config.set(("output",), "mode", "null")
            config.set(("downloader",), "progress", None)
        elif args.loglevel <= logging.DEBUG:
            import platform
            import requests

            extra = ""
            if util.EXECUTABLE:
                extra = " - Executable"
            else:
                git_head = util.git_head()
                if git_head:
                    extra = " - Git HEAD: " + git_head

            log.debug("Version %s%s", __version__, extra)
            log.debug("Python %s - %s",
                      platform.python_version(), platform.platform())
            try:
                log.debug("requests %s - urllib3 %s",
                          requests.__version__,
                          requests.packages.urllib3.__version__)
            except AttributeError:
                pass

            log.debug("Configuration Files %s", config._files)

        # extractor modules
        modules = config.get(("extractor",), "modules")
        if modules is not None:
            if isinstance(modules, str):
                modules = modules.split(",")
            extractor.modules = modules

        # external modules
        if args.extractor_sources:
            sources = args.extractor_sources
            sources.append(None)
        else:
            sources = config.get(("extractor",), "module-sources")

        if sources:
            import os
            modules = []

            for source in sources:
                if source:
                    path = util.expand_path(source)
                    try:
                        files = os.listdir(path)
                        modules.append(extractor._modules_path(path, files))
                    except Exception as exc:
                        log.warning("Unable to load modules from %s (%s: %s)",
                                    path, exc.__class__.__name__, exc)
                else:
                    modules.append(extractor._modules_internal())

            if len(modules) > 1:
                import itertools
                extractor._module_iter = itertools.chain(*modules)
            elif not modules:
                extractor._module_iter = ()
            else:
                extractor._module_iter = iter(modules[0])

        if args.list_modules:
            extractor.modules.append("")
            sys.stdout.write("\n".join(extractor.modules))

        elif args.list_extractors:
            write = sys.stdout.write
            fmt = ("{}{}\nCategory: {} - Subcategory: {}"
                   "\nExample : {}\n\n").format

            for extr in extractor.extractors():
                write(fmt(
                    extr.__name__,
                    "\n" + extr.__doc__ if extr.__doc__ else "",
                    extr.category, extr.subcategory,
                    extr.example,
                ))

        elif args.clear_cache:
            from . import cache
            log = logging.getLogger("cache")
            cnt = cache.clear(args.clear_cache)

            if cnt is None:
                log.error("Database file not available")
            else:
                log.info(
                    "Deleted %d %s from '%s'",
                    cnt, "entry" if cnt == 1 else "entries", cache._path(),
                )

        elif args.config_init:
            return config.initialize()

        else:
            if not args.urls and not args.input_files:
                parser.error(
                    "The following arguments are required: URL\n"
                    "Use 'gallery-dl --help' to get a list of all options.")

            if args.list_urls:
                jobtype = job.UrlJob
                jobtype.maxdepth = args.list_urls
                if config.get(("output",), "fallback", True):
                    jobtype.handle_url = \
                        staticmethod(jobtype.handle_url_fallback)
            else:
                jobtype = args.jobtype or job.DownloadJob

            input_manager = InputManager()
            input_manager.log = input_log = logging.getLogger("inputfile")

            # unsupported file logging handler
            handler = output.setup_logging_handler(
                "unsupportedfile", fmt="{message}")
            if handler:
                ulog = job.Job.ulog = logging.getLogger("unsupported")
                ulog.addHandler(handler)
                ulog.propagate = False

            # error file logging handler
            handler = output.setup_logging_handler(
                "errorfile", fmt="{message}", mode="a")
            if handler:
                elog = input_manager.err = logging.getLogger("errorfile")
                elog.addHandler(handler)
                elog.propagate = False

            # collect input URLs
            input_manager.add_list(args.urls)

            if args.input_files:
                for input_file, action in args.input_files:
                    try:
                        path = util.expand_path(input_file)
                        input_manager.add_file(path, action)
                    except Exception as exc:
                        input_log.error(exc)
                        return getattr(exc, "code", 128)

            pformat = config.get(("output",), "progress", True)
            if pformat and len(input_manager.urls) > 1 and \
                    args.loglevel < logging.ERROR:
                input_manager.progress(pformat)

            # process input URLs
            retval = 0
            for url in input_manager:
                try:
                    log.debug("Starting %s for '%s'", jobtype.__name__, url)

                    if isinstance(url, ExtendedUrl):
                        for opts in url.gconfig:
                            config.set(*opts)
                        with config.apply(url.lconfig):
                            status = jobtype(url.value).run()
                    else:
                        status = jobtype(url).run()

                    if status:
                        retval |= status
                        input_manager.error()
                    else:
                        input_manager.success()

                except exception.TerminateExtraction:
                    pass
                except exception.RestartExtraction:
                    log.debug("Restarting '%s'", url)
                    continue
                except exception.NoExtractorError:
                    log.error("Unsupported URL '%s'", url)
                    retval |= 64
                    input_manager.error()

                input_manager.next()
            return retval

    except KeyboardInterrupt:
        raise SystemExit("\nKeyboardInterrupt")
    except BrokenPipeError:
        pass
    except OSError as exc:
        import errno
        if exc.errno != errno.EPIPE:
            raise
    return 1


class InputManager():

    def __init__(self):
        self.urls = []
        self.files = ()
        self.log = self.err = None

        self._url = ""
        self._item = None
        self._index = 0
        self._pformat = None

    def add_url(self, url):
        self.urls.append(url)

    def add_list(self, urls):
        self.urls += urls

    def add_file(self, path, action=None):
        """Process an input file.

        Lines starting with '#' and empty lines will be ignored.
        Lines starting with '-' will be interpreted as a key-value pair
          separated by an '='. where
          'key' is a dot-separated option name and
          'value' is a JSON-parsable string.
          These configuration options will be applied
          while processing the next URL only.
        Lines starting with '-G' are the same as above, except these options
          will be applied for *all* following URLs, i.e. they are Global.
        Everything else will be used as a potential URL.

        Example input file:

        # settings global options
        -G base-directory = "/tmp/"
        -G skip = false

        # setting local options for the next URL
        -filename="spaces_are_optional.jpg"
        -skip    = true

        https://example.org/

        # next URL uses default filename and 'skip' is false.
        https://example.com/index.htm # comment1
        https://example.com/404.htm   # comment2
        """
        if path == "-" and not action:
            try:
                lines = sys.stdin.readlines()
            except Exception:
                raise exception.InputFileError("stdin is not readable")
            path = None
        else:
            try:
                with open(path, encoding="utf-8") as fp:
                    lines = fp.readlines()
            except Exception as exc:
                raise exception.InputFileError(str(exc))

            if self.files:
                self.files[path] = lines
            else:
                self.files = {path: lines}

            if action == "c":
                action = self._action_comment
            elif action == "d":
                action = self._action_delete
            else:
                action = None

        gconf = []
        lconf = []
        indicies = []
        strip_comment = None
        append = self.urls.append

        for n, line in enumerate(lines):
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
                    if action:
                        indicies.append(n)

                key, sep, value = line.partition("=")
                if not sep:
                    raise exception.InputFileError(
                        "Invalid KEY=VALUE pair '%s' on line %s in %s",
                        line, n+1, path)

                try:
                    value = util.json_loads(value.strip())
                except ValueError as exc:
                    self.log.debug("%s: %s", exc.__class__.__name__, exc)
                    raise exception.InputFileError(
                        "Unable to parse '%s' on line %s in %s",
                        value, n+1, path)

                key = key.strip().split(".")
                conf.append((key[:-1], key[-1], value))

            else:
                # url
                if " #" in line or "\t#" in line:
                    if strip_comment is None:
                        import re
                        strip_comment = re.compile(r"\s+#.*").sub
                    line = strip_comment("", line)
                if gconf or lconf:
                    url = ExtendedUrl(line, gconf, lconf)
                    gconf = []
                    lconf = []
                else:
                    url = line

                if action:
                    indicies.append(n)
                    append((url, path, action, indicies))
                    indicies = []
                else:
                    append(url)

    def progress(self, pformat=True):
        if pformat is True:
            pformat = "[{current}/{total}] {url}\n"
        else:
            pformat += "\n"
        self._pformat = pformat.format_map

    def next(self):
        self._index += 1

    def success(self):
        if self._item:
            self._rewrite()

    def error(self):
        if self.err:
            if self._item:
                url, path, action, indicies = self._item
                lines = self.files[path]
                out = "".join(lines[i] for i in indicies)
                if out and out[-1] == "\n":
                    out = out[:-1]
                self._rewrite()
            else:
                out = str(self._url)
            self.err.info(out)

    def _rewrite(self):
        url, path, action, indicies = self._item
        lines = self.files[path]
        action(lines, indicies)
        try:
            with open(path, "w", encoding="utf-8") as fp:
                fp.writelines(lines)
        except Exception as exc:
            self.log.warning(
                "Unable to update '%s' (%s: %s)",
                path, exc.__class__.__name__, exc)

    @staticmethod
    def _action_comment(lines, indicies):
        for i in indicies:
            lines[i] = "# " + lines[i]

    @staticmethod
    def _action_delete(lines, indicies):
        for i in indicies:
            lines[i] = ""

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        try:
            url = self.urls[self._index]
        except IndexError:
            raise StopIteration

        if isinstance(url, tuple):
            self._item = url
            url = url[0]
        else:
            self._item = None
        self._url = url

        if self._pformat:
            output.stderr_write(self._pformat({
                "total"  : len(self.urls),
                "current": self._index + 1,
                "url"    : url,
            }))
        return url


class ExtendedUrl():
    """URL with attached config key-value pairs"""
    __slots__ = ("value", "gconfig", "lconfig")

    def __init__(self, url, gconf, lconf):
        self.value = url
        self.gconfig = gconf
        self.lconfig = lconf

    def __str__(self):
        return self.value
