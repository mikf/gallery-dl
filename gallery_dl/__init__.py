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


def progress(urls, pformat):
    """Wrapper around urls to output a simple progress indicator"""
    if pformat is True:
        pformat = "[{current}/{total}] {url}\n"
    else:
        pformat += "\n"

    pinfo = {"total": len(urls)}
    for pinfo["current"], pinfo["url"] in enumerate(urls, 1):
        output.stderr_write(pformat.format_map(pinfo))
        yield pinfo["url"]


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
            config.load(args.configs_yaml, strict=True, load=yaml.safe_load)
        if args.configs_toml:
            try:
                import tomllib as toml
            except ImportError:
                import toml
            config.load(args.configs_toml, strict=True, load=toml.loads)
        if args.filename:
            filename = args.filename
            if filename == "/O":
                filename = "{filename}.{extension}"
            elif filename.startswith("\\f"):
                filename = "\f" + filename[2:]
            config.set((), "filename", filename)
        if args.directory:
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
        if util.WINDOWS and config.get(("output",), "ansi"):
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
        if args.loglevel >= logging.ERROR:
            config.set(("output",), "mode", "null")
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
            fmt = "{}\n{}\nCategory: {} - Subcategory: {}{}\n\n".format

            for extr in extractor.extractors():
                if not extr.__doc__:
                    continue
                test = next(extr._get_tests(), None)
                write(fmt(
                    extr.__name__, extr.__doc__,
                    extr.category, extr.subcategory,
                    "\nExample : " + test[0] if test else "",
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
            if not args.urls and not args.inputfiles:
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

            urls = args.urls
            if args.inputfiles:
                for inputfile in args.inputfiles:
                    try:
                        if inputfile == "-":
                            if sys.stdin:
                                urls += util.parse_inputfile(sys.stdin, log)
                            else:
                                log.warning(
                                    "input file: stdin is not readable")
                        else:
                            with open(inputfile, encoding="utf-8") as file:
                                urls += util.parse_inputfile(file, log)
                    except OSError as exc:
                        log.warning("input file: %s", exc)

            # unsupported file logging handler
            handler = output.setup_logging_handler(
                "unsupportedfile", fmt="{message}")
            if handler:
                ulog = logging.getLogger("unsupported")
                ulog.addHandler(handler)
                ulog.propagate = False
                job.Job.ulog = ulog

            pformat = config.get(("output",), "progress", True)
            if pformat and len(urls) > 1 and args.loglevel < logging.ERROR:
                urls = progress(urls, pformat)
            else:
                urls = iter(urls)

            retval = 0
            url = next(urls, None)

            while url is not None:
                try:
                    log.debug("Starting %s for '%s'", jobtype.__name__, url)
                    if isinstance(url, util.ExtendedUrl):
                        for opts in url.gconfig:
                            config.set(*opts)
                        with config.apply(url.lconfig):
                            retval |= jobtype(url.value).run()
                    else:
                        retval |= jobtype(url).run()
                except exception.TerminateExtraction:
                    pass
                except exception.RestartExtraction:
                    log.debug("Restarting '%s'", url)
                    continue
                except exception.NoExtractorError:
                    log.error("Unsupported URL '%s'", url)
                    retval |= 64

                url = next(urls, None)

            return retval

    except KeyboardInterrupt:
        sys.exit("\nKeyboardInterrupt")
    except BrokenPipeError:
        pass
    except OSError as exc:
        import errno
        if exc.errno != errno.EPIPE:
            raise
    return 1
