# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import errno
import logging
import functools
import collections

from . import (
    extractor,
    downloader,
    postprocessor,
    archive,
    config,
    exception,
    formatter,
    output,
    path,
    text,
    util,
    version,
)
from .extractor.message import Message
stdout_write = output.stdout_write
FLAGS = util.FLAGS


class Job():
    """Base class for Job types"""
    ulog = None
    _logger_adapter = output.LoggerAdapter

    def __init__(self, extr, parent=None):
        if isinstance(extr, str):
            extr = extractor.find(extr)
        if not extr:
            raise exception.NoExtractorError()

        self.extractor = extr
        self.pathfmt = None
        self.status = 0
        self.kwdict = {}
        self.kwdict_eval = False

        if cfgpath := self._build_config_path(parent):
            if isinstance(cfgpath, list):
                extr.config = extr._config_shared
                extr.config_accumulate = extr._config_shared_accumulate
            extr._cfgpath = cfgpath

        if actions := extr.config("actions"):
            from .actions import LoggerAdapter, parse_logging
            self._logger_adapter = LoggerAdapter
            self._logger_actions = parse_logging(actions)

        path_proxy = output.PathfmtProxy(self)
        self._logger_extra = {
            "job"      : self,
            "extractor": extr,
            "path"     : path_proxy,
            "keywords" : output.KwdictProxy(self),
        }
        extr.log = self._wrap_logger(extr.log)
        extr.log.debug("Using %s for '%s'", extr.__class__.__name__, extr.url)

        self.metadata_url = extr.config2("metadata-url", "url-metadata")
        self.metadata_http = extr.config2("metadata-http", "http-metadata")
        metadata_path = extr.config2("metadata-path", "path-metadata")
        metadata_version = extr.config2("metadata-version", "version-metadata")
        metadata_extractor = extr.config2(
            "metadata-extractor", "extractor-metadata")

        if metadata_path:
            self.kwdict[metadata_path] = path_proxy
        if metadata_extractor:
            self.kwdict[metadata_extractor] = extr
        if metadata_version:
            self.kwdict[metadata_version] = {
                "version"         : version.__version__,
                "is_executable"   : util.EXECUTABLE,
                "current_git_head": util.git_head()
            }
        # user-supplied metadata
        if kwdict := extr.config("keywords"):
            if extr.config("keywords-eval"):
                self.kwdict_eval = []
                for key, value in kwdict.items():
                    if isinstance(value, str):
                        fmt = formatter.parse(value, None, util.identity)
                        self.kwdict_eval.append((key, fmt.format_map))
                    else:
                        self.kwdict[key] = value
            else:
                self.kwdict.update(kwdict)

    def _build_config_path(self, parent):
        extr = self.extractor
        cfgpath = []

        if parent:
            pextr = parent.extractor
            if extr.category == pextr.category or \
                    extr.category in parent.parents:
                parents = parent.parents
            else:
                parents = parent.parents + (pextr.category,)
            self.parents = parents

            if pextr.config("category-transfer", pextr.categorytransfer):
                extr.category = pextr.category
                extr.subcategory = pextr.subcategory
                return pextr._cfgpath

            if parents:
                sub = extr.subcategory
                for category in parents:
                    cat = f"{category}>{extr.category}"
                    cfgpath.append((cat, sub))
                    cfgpath.append((category + ">*", sub))
                cfgpath.append((extr.category, sub))
        else:
            self.parents = ()

        if extr.basecategory:
            if not cfgpath:
                cfgpath.append((extr.category, extr.subcategory))
            if extr.basesubcategory:
                cfgpath.append((extr.basesubcategory, extr.subcategory))
            cfgpath.append((extr.basecategory, extr.subcategory))

        return cfgpath

    def run(self):
        """Execute or run the job"""
        extractor = self.extractor
        log = extractor.log
        msg = None

        self._init()

        # sleep before extractor start
        sleep = util.build_duration_func(
            extractor.config("sleep-extractor"))
        if sleep is not None:
            extractor.sleep(sleep(), "extractor")

        try:
            for msg in extractor:
                self.dispatch(msg)
        except exception.StopExtraction as exc:
            if exc.depth > 1 and exc.target != extractor.__class__.subcategory:
                exc.depth -= 1
                raise
            pass
        except exception.AbortExtraction as exc:
            log.traceback(exc)
            log.error(exc.message)
            self.status |= exc.code
        except (exception.TerminateExtraction, exception.RestartExtraction):
            raise
        except exception.GalleryDLException as exc:
            log.error("%s: %s", exc.__class__.__name__, exc)
            log.traceback(exc)
            self.status |= exc.code
        except OSError as exc:
            log.traceback(exc)
            if (name := exc.__class__.__name__) == "JSONDecodeError":
                log.error("Failed to parse JSON data:  %s: %s", name, exc)
                self.status |= 1
            else:  # regular OSError
                log.error("Unable to download data:  %s: %s", name, exc)
                self.status |= 128
        except Exception as exc:
            log.error(("An unexpected error occurred: %s - %s. "
                       "Please run gallery-dl again with the --verbose flag, "
                       "copy its output and report this issue on "
                       "https://github.com/mikf/gallery-dl/issues ."),
                      exc.__class__.__name__, exc)
            log.traceback(exc)
            self.status |= 1
        except BaseException:
            self.status |= 1
            raise
        else:
            if msg is None:
                log.info("No results for %s", extractor.url)
        finally:
            self.handle_finalize()
            extractor.finalize()

        if s := extractor.status:
            self.status |= s
        return self.status

    def dispatch(self, msg):
        """Call the appropriate message handler"""
        if msg[0] == Message.Url:
            _, url, kwdict = msg
            if self.metadata_url:
                kwdict[self.metadata_url] = url
            if self.pred_url(url, kwdict):
                self.update_kwdict(kwdict)
                self.handle_url(url, kwdict)
            if FLAGS.FILE is not None:
                FLAGS.process("FILE")

        elif msg[0] == Message.Directory:
            self.update_kwdict(msg[1])
            self.handle_directory(msg[1])

        elif msg[0] == Message.Queue:
            _, url, kwdict = msg
            if self.metadata_url:
                kwdict[self.metadata_url] = url
            if self.pred_queue(url, kwdict):
                self.update_kwdict(kwdict)
                self.handle_queue(url, kwdict)
            if FLAGS.CHILD is not None:
                FLAGS.process("CHILD")

    def handle_url(self, url, kwdict):
        """Handle Message.Url"""

    def handle_directory(self, kwdict):
        """Handle Message.Directory"""

    def handle_queue(self, url, kwdict):
        """Handle Message.Queue"""

    def handle_finalize(self):
        """Handle job finalization"""

    def update_kwdict(self, kwdict):
        """Update 'kwdict' with additional metadata"""
        extr = self.extractor
        kwdict["category"] = extr.category
        kwdict["subcategory"] = extr.subcategory
        if self.metadata_http:
            kwdict.pop(self.metadata_http, None)
        if extr.kwdict:
            kwdict.update(extr.kwdict)
        if self.kwdict:
            kwdict.update(self.kwdict)
        if self.kwdict_eval:
            for key, valuegen in self.kwdict_eval:
                kwdict[key] = valuegen(kwdict)

    def _init(self):
        self.extractor.initialize()
        self.pred_url = self._prepare_predicates("image", True)
        self.pred_queue = self._prepare_predicates("chapter", False)

    def _prepare_predicates(self, target, skip=True):
        predicates = []

        if self.extractor.config(f"{target}-unique"):
            predicates.append(util.UniquePredicate())

        if pfilter := self.extractor.config(f"{target}-filter"):
            try:
                pred = util.FilterPredicate(pfilter, target)
            except (SyntaxError, ValueError, TypeError) as exc:
                self.extractor.log.warning(exc)
            else:
                predicates.append(pred)

        if prange := self.extractor.config(f"{target}-range"):
            try:
                pred = util.RangePredicate(prange)
            except ValueError as exc:
                self.extractor.log.warning(
                    "invalid %s range: %s", target, exc)
            else:
                if skip and pred.lower > 1 and not pfilter:
                    pred.index += self.extractor.skip(pred.lower - 1)
                predicates.append(pred)

        return util.build_predicate(predicates)

    def get_logger(self, name):
        return self._wrap_logger(logging.getLogger(name))

    def _wrap_logger(self, logger):
        return self._logger_adapter(logger, self)

    def _write_unsupported(self, url):
        if self.ulog is not None:
            self.ulog.info(url)


class DownloadJob(Job):
    """Download images into appropriate directory/filename locations"""

    def __init__(self, url, parent=None):
        Job.__init__(self, url, parent)
        self.log = self.get_logger("download")
        self.fallback = None
        self.archive = None
        self.sleep = None
        self.hooks = ()
        self.downloaders = {}
        self.out = output.select()
        self.visited = parent.visited if parent else set()
        self._extractor_filter = None
        self._skipcnt = 0

    def handle_url(self, url, kwdict):
        """Download the resource specified in 'url'"""
        hooks = self.hooks
        pathfmt = self.pathfmt
        archive = self.archive

        # prepare download
        pathfmt.set_filename(kwdict)

        if "prepare" in hooks:
            for callback in hooks["prepare"]:
                callback(pathfmt)

        if archive is not None and archive.check(kwdict):
            pathfmt.fix_extension()
            self.handle_skip()
            return

        if pathfmt.extension and not self.metadata_http:
            pathfmt.build_path()

            if pathfmt.exists():
                if archive is not None and self._archive_write_skip:
                    archive.add(kwdict)
                self.handle_skip()
                return

        if "prepare-after" in hooks:
            for callback in hooks["prepare-after"]:
                callback(pathfmt)

            if kwdict.pop("_file_recheck", False) and pathfmt.exists():
                if archive is not None and self._archive_write_skip:
                    archive.add(kwdict)
                self.handle_skip()
                return

        if self.sleep is not None:
            self.extractor.sleep(self.sleep(), "download")

        # download from URL
        if not self.download(url):

            # use fallback URLs if available/enabled
            fallback = kwdict.get("_fallback", ()) if self.fallback else ()
            for num, url in enumerate(fallback, 1):
                util.remove_file(pathfmt.temppath)
                self.log.info("Trying fallback URL #%d", num)
                if self.download(url):
                    break
            else:
                # download failed
                self.status |= 4
                self.log.error("Failed to download %s",
                               pathfmt.filename or url)
                if "error" in hooks:
                    for callback in hooks["error"]:
                        callback(pathfmt)
                return

        if not pathfmt.temppath:
            if archive is not None and self._archive_write_skip:
                archive.add(kwdict)
            self.handle_skip()
            return

        # run post processors
        if "file" in hooks:
            for callback in hooks["file"]:
                callback(pathfmt)

        # download succeeded
        pathfmt.finalize()
        self.out.success(pathfmt.path)
        self._skipcnt = 0
        if archive is not None and self._archive_write_file:
            archive.add(kwdict)
        if "after" in hooks:
            for callback in hooks["after"]:
                callback(pathfmt)
        if archive is not None and self._archive_write_after:
            archive.add(kwdict)

    def handle_directory(self, kwdict):
        """Set and create the target directory for downloads"""
        if self.pathfmt is None:
            self.initialize(kwdict)
        else:
            if "post-after" in self.hooks:
                for callback in self.hooks["post-after"]:
                    callback(self.pathfmt)
            if FLAGS.POST is not None:
                FLAGS.process("POST")
            self.pathfmt.set_directory(kwdict)
        if "post" in self.hooks:
            for callback in self.hooks["post"]:
                callback(self.pathfmt)

    def handle_queue(self, url, kwdict):
        if url in self.visited:
            return
        self.visited.add(url)

        if cls := kwdict.get("_extractor"):
            extr = cls.from_url(url)
        else:
            if extr := extractor.find(url):
                if self._extractor_filter is None:
                    self._extractor_filter = self._build_extractor_filter()
                if not self._extractor_filter(extr):
                    extr = None

        if extr:
            job = self.__class__(extr, self)
            pfmt = self.pathfmt
            pextr = self.extractor

            if pfmt and pextr.config("parent-directory"):
                extr._parentdir = pfmt.directory
            else:
                extr._parentdir = pextr._parentdir

            if pmeta := pextr.config2("parent-metadata", "metadata-parent"):
                if isinstance(pmeta, str):
                    data = self.kwdict.copy()
                    if kwdict:
                        data.update(kwdict)
                    job.kwdict[pmeta] = data
                else:
                    if self.kwdict:
                        job.kwdict.update(self.kwdict)
                    if kwdict:
                        job.kwdict.update(kwdict)

            while True:
                try:
                    if pextr.config("parent-skip"):
                        job._skipcnt = self._skipcnt
                        status = job.run()
                        self._skipcnt = job._skipcnt
                    else:
                        status = job.run()

                    if status:
                        self.status |= status
                        if (status & 95 and   # not FormatError or OSError
                                "_fallback" in kwdict and self.fallback):
                            fallback = kwdict["_fallback"] = \
                                iter(kwdict["_fallback"])
                            try:
                                url = next(fallback)
                            except StopIteration:
                                pass
                            else:
                                pextr.log.info("Downloading fallback URL")
                                text.nameext_from_url(url, kwdict)
                                if kwdict["filename"].startswith((
                                        "HLS", "DASH")):
                                    kwdict["filename"] = url.rsplit("/", 2)[-2]
                                if url.startswith("ytdl:"):
                                    kwdict["extension"] = "mp4"
                                self.handle_url(url, kwdict)
                    break
                except exception.RestartExtraction:
                    pass

        else:
            self._write_unsupported(url)

    def handle_finalize(self):
        if self.archive:
            if not self.status:
                self.archive.finalize()
            self.archive.close()

        if pathfmt := self.pathfmt:
            hooks = self.hooks
            if "post-after" in hooks:
                for callback in hooks["post-after"]:
                    callback(pathfmt)

            self.extractor.cookies_store()

            if self.status:
                if "finalize-error" in hooks:
                    for callback in hooks["finalize-error"]:
                        callback(pathfmt)
            else:
                if "finalize-success" in hooks:
                    for callback in hooks["finalize-success"]:
                        callback(pathfmt)
            if "finalize" in hooks:
                for callback in hooks["finalize"]:
                    callback(pathfmt)

    def handle_skip(self):
        pathfmt = self.pathfmt
        if "skip" in self.hooks:
            for callback in self.hooks["skip"]:
                callback(pathfmt)
        self.out.skip(pathfmt.path)

        if self._skipexc:
            if self._skipftr is None or self._skipftr(pathfmt.kwdict):
                self._skipcnt += 1
                if self._skipcnt >= self._skipmax:
                    raise self._skipexc

    def download(self, url):
        """Download 'url'"""
        if downloader := self.get_downloader(url[:url.find(":")]):
            try:
                return downloader.download(url, self.pathfmt)
            except OSError as exc:
                if exc.errno == errno.ENOSPC:
                    raise
                self.log.warning("%s: %s", exc.__class__.__name__, exc)
                return False
        self._write_unsupported(url)
        return False

    def get_downloader(self, scheme):
        """Return a downloader suitable for 'scheme'"""
        try:
            return self.downloaders[scheme]
        except KeyError:
            pass

        cls = downloader.find(scheme)
        if cls and config.get(("downloader", cls.scheme), "enabled", True):
            instance = cls(self)
        else:
            instance = None
            self.log.error("'%s:' URLs are not supported/enabled", scheme)

        if cls and cls.scheme == "http":
            self.downloaders["http"] = self.downloaders["https"] = instance
        else:
            self.downloaders[scheme] = instance
        return instance

    def initialize(self, kwdict=None):
        """Delayed initialization of PathFormat, etc."""
        extr = self.extractor
        cfg = extr.config

        pathfmt = self.pathfmt = path.PathFormat(extr)
        if kwdict is not None:
            pathfmt.set_directory(kwdict)

        self.sleep = util.build_duration_func(cfg("sleep"))
        self.fallback = cfg("fallback", True)
        if not cfg("download", True):
            # monkey-patch method to do nothing and always return True
            self.download = pathfmt.fix_extension

        if archive_path := cfg("archive"):
            archive_table = cfg("archive-table")
            archive_prefix = cfg("archive-prefix")
            if archive_prefix is None:
                archive_prefix = extr.category if archive_table is None else ""

            archive_format = cfg("archive-format")
            if archive_format is None:
                archive_format = extr.archive_fmt

            try:
                self.archive = archive.connect(
                    archive_path,
                    archive_prefix,
                    archive_format,
                    archive_table,
                    cfg("archive-mode"),
                    cfg("archive-pragma"),
                    kwdict,
                )
            except Exception as exc:
                extr.log.warning(
                    "Failed to open download archive at '%s' (%s: %s)",
                    archive_path, exc.__class__.__name__, exc)
            else:
                extr.log.debug("Using download archive '%s'", archive_path)

                events = cfg("archive-event")
                if events is None:
                    self._archive_write_file = True
                    self._archive_write_skip = False
                    self._archive_write_after = False
                else:
                    if isinstance(events, str):
                        events = events.split(",")
                    self._archive_write_file = ("file" in events)
                    self._archive_write_skip = ("skip" in events)
                    self._archive_write_after = ("after" in events)

        if skip := cfg("skip", True):
            self._skipexc = None
            if skip == "enumerate":
                pathfmt.check_file = pathfmt._enum_file
            elif isinstance(skip, str):
                skip, _, smax = skip.partition(":")
                if skip == "abort":
                    smax, _, sarg = smax.partition(":")
                    self._skipexc = exception.StopExtraction(sarg or None)
                elif skip == "terminate":
                    self._skipexc = exception.TerminateExtraction
                elif skip == "exit":
                    self._skipexc = SystemExit
                self._skipmax = text.parse_int(smax)

                if skip_filter := cfg("skip-filter"):
                    self._skipftr = util.compile_filter(skip_filter)
                else:
                    self._skipftr = None
        else:
            # monkey-patch methods to always return False
            pathfmt.exists = lambda x=None: False
            if self.archive is not None:
                self.archive.check = pathfmt.exists

        if not cfg("postprocess", True):
            return

        if postprocessors := extr.config_accumulate("postprocessors"):
            self.hooks = collections.defaultdict(list)

            pp_log = self.get_logger("postprocessor")
            pp_conf = config.get((), "postprocessor") or {}
            pp_opts = cfg("postprocessor-options")
            pp_list = []

            for pp_dict in postprocessors:
                if isinstance(pp_dict, str):
                    pp_dict = pp_conf.get(pp_dict) or {"name": pp_dict}
                elif "type" in pp_dict:
                    pp_type = pp_dict["type"]
                    if pp_type in pp_conf:
                        pp = pp_conf[pp_type].copy()
                        pp.update(pp_dict)
                        pp_dict = pp
                    if "name" not in pp_dict:
                        pp_dict["name"] = pp_type
                if pp_opts:
                    pp_dict = pp_dict.copy()
                    pp_dict.update(pp_opts)

                clist = pp_dict.get("whitelist")
                if clist is not None:
                    negate = False
                else:
                    clist = pp_dict.get("blacklist")
                    negate = True
                if clist and not util.build_extractor_filter(
                        clist, negate)(extr):
                    continue

                name = pp_dict.get("name", "")
                if "__init__" not in pp_dict:
                    name, sep, event = name.rpartition("@")
                    if sep:
                        pp_dict["name"] = name
                        if "event" not in pp_dict:
                            pp_dict["event"] = event
                    else:
                        name = event

                    name, sep, mode = name.rpartition("/")
                    if sep:
                        pp_dict["name"] = name
                        if "mode" not in pp_dict:
                            pp_dict["mode"] = mode
                    else:
                        name = mode

                    pp_dict["__init__"] = None

                pp_cls = postprocessor.find(name)
                if pp_cls is None:
                    pp_log.warning("module '%s' not found", name)
                    continue
                try:
                    pp_obj = pp_cls(self, pp_dict)
                except Exception as exc:
                    pp_log.traceback(exc)
                    pp_log.error("'%s' initialization failed:  %s: %s",
                                 name, exc.__class__.__name__, exc)
                else:
                    pp_list.append(pp_obj)

            if pp_list:
                extr.log.debug("Active postprocessor modules: %s", pp_list)
                if "init" in self.hooks:
                    for callback in self.hooks["init"]:
                        callback(pathfmt)

    def register_hooks(self, hooks, options=None):
        expr = options.get("filter") if options else None

        if expr:
            condition = util.compile_filter(expr)
            for hook, callback in hooks.items():
                self.hooks[hook].append(functools.partial(
                    _call_hook_condition, callback, condition))
        else:
            for hook, callback in hooks.items():
                self.hooks[hook].append(callback)

    def _build_extractor_filter(self):
        clist = self.extractor.config("whitelist")
        if clist is not None:
            negate = False
            special = None
        else:
            clist = self.extractor.config("blacklist")
            negate = True
            special = util.SPECIAL_EXTRACTORS
            if clist is None:
                clist = (self.extractor.category,)

        return util.build_extractor_filter(clist, negate, special)


def _call_hook_condition(callback, condition, pathfmt):
    if condition(pathfmt.kwdict):
        callback(pathfmt)


class SimulationJob(DownloadJob):
    """Simulate the extraction process without downloading anything"""

    def handle_url(self, url, kwdict):
        ext = kwdict["extension"] or "jpg"
        kwdict["extension"] = self.pathfmt.extension_map(ext, ext)
        if self.sleep is not None:
            self.extractor.sleep(self.sleep(), "download")
        if self.archive is not None and self._archive_write_skip:
            self.archive.add(kwdict)
        self.out.skip(self.pathfmt.build_filename(kwdict))

    def handle_directory(self, kwdict):
        if self.pathfmt is None:
            self.initialize()


class KeywordJob(Job):
    """Print available keywords"""

    def __init__(self, url, parent=None):
        Job.__init__(self, url, parent)
        self.private = config.get(("output",), "private")

    def handle_url(self, url, kwdict):
        stdout_write("\nKeywords for filenames and --filter:\n"
                     "------------------------------------\n")

        if self.metadata_http and url.startswith("http"):
            kwdict[self.metadata_http] = util.extract_headers(
                self.extractor.request(url, method="HEAD"))

        self.print_kwdict(kwdict)
        raise exception.StopExtraction()

    def handle_directory(self, kwdict):
        stdout_write("Keywords for directory names:\n"
                     "-----------------------------\n")
        self.print_kwdict(kwdict)

    def handle_queue(self, url, kwdict):
        extr = None
        if "_extractor" in kwdict:
            extr = kwdict["_extractor"].from_url(url)

        if not util.filter_dict(kwdict):
            self.extractor.log.info(
                "This extractor only spawns other extractors "
                "and does not provide any metadata on its own.")

            if extr:
                self.extractor.log.info(
                    "Showing results for '%s' instead:\n", url)
                KeywordJob(extr, self).run()
            else:
                self.extractor.log.info(
                    "Try 'gallery-dl -K \"%s\"' instead.", url)
        else:
            stdout_write("Keywords for --chapter-filter:\n"
                         "------------------------------\n")
            self.print_kwdict(kwdict)
            if extr or self.extractor.categorytransfer:
                stdout_write("\n")
                KeywordJob(extr or url, self).run()
        raise exception.StopExtraction()

    def print_kwdict(self, kwdict, prefix="", markers=None):
        """Print key-value pairs in 'kwdict' with formatting"""
        write = sys.stdout.write
        suffix = "']" if prefix else ""

        markerid = id(kwdict)
        if markers is None:
            markers = {markerid}
        elif markerid in markers:
            write(f"{prefix[:-2]}\n  <circular reference>\n")
            return  # ignore circular reference
        else:
            markers.add(markerid)

        for key, value in sorted(kwdict.items()):
            if key[0] == "_" and not self.private:
                continue
            key = prefix + key + suffix

            if isinstance(value, dict):
                self.print_kwdict(value, key + "['", markers)

            elif isinstance(value, list):
                if not value:
                    pass
                elif isinstance(value[0], dict):
                    self.print_kwdict(value[0], key + "[N]['", markers)
                else:
                    fmt = ("  {:>%s} {}\n" % len(str(len(value)))).format
                    write(key + "[N]\n")
                    for idx, val in enumerate(value, 0):
                        write(fmt(idx, val))

            else:
                # string or number
                write(f"{key}\n  {value}\n")

        markers.remove(markerid)


class UrlJob(Job):
    """Print download urls"""
    maxdepth = 1

    def __init__(self, url, parent=None, depth=1):
        Job.__init__(self, url, parent)
        self.depth = depth
        if depth >= self.maxdepth:
            self.handle_queue = self.handle_url

    def handle_url(self, url, _):
        stdout_write(url + "\n")

    def handle_url_fallback(self, url, kwdict):
        stdout_write(url + "\n")
        if "_fallback" in kwdict:
            for url in kwdict["_fallback"]:
                stdout_write(f"| {url}\n")

    def handle_queue(self, url, kwdict):
        if cls := kwdict.get("_extractor"):
            extr = cls.from_url(url)
        else:
            extr = extractor.find(url)

        if extr:
            self.status |= self.__class__(extr, self, self.depth + 1).run()
        else:
            self._write_unsupported(url)


class InfoJob(Job):
    """Print extractor defaults and settings"""

    def run(self):
        ex = self.extractor
        pm = self._print_multi
        pc = self._print_config

        if ex.basecategory:
            pm("Category / Subcategory / Basecategory",
               ex.category, ex.subcategory, ex.basecategory)
        else:
            pm("Category / Subcategory", ex.category, ex.subcategory)

        pc("Filename format", "filename", ex.filename_fmt)
        pc("Directory format", "directory", ex.directory_fmt)
        pc("Archive format", "archive-format", ex.archive_fmt)
        pc("Request interval", "sleep-request", ex.request_interval)

        return 0

    def _print_multi(self, title, *values):
        stdout_write(
            f"{title}\n  {' / '.join(map(util.json_dumps, values))}\n\n")

    def _print_config(self, title, optname, value):
        optval = self.extractor.config(optname, util.SENTINEL)
        if optval is not util.SENTINEL:
            stdout_write(
                f"{title} (custom):\n  {util.json_dumps(optval)}\n"
                f"{title} (default):\n  {util.json_dumps(value)}\n\n")
        elif value:
            stdout_write(
                f"{title} (default):\n  {util.json_dumps(value)}\n\n")


class DataJob(Job):
    """Collect extractor results and dump them"""
    resolve = False

    def __init__(self, url, parent=None, file=sys.stdout, ensure_ascii=True,
                 resolve=False):
        Job.__init__(self, url, parent)
        self.file = file
        self.data = []
        self.data_urls = []
        self.data_post = []
        self.data_meta = []
        self.exception = None
        self.ascii = config.get(("output",), "ascii", ensure_ascii)
        self.resolve = 128 if resolve is True else (resolve or self.resolve)

        private = config.get(("output",), "private")
        self.filter = dict.copy if private else util.filter_dict

        if self.resolve > 0:
            self.handle_queue = self.handle_queue_resolve

    def run(self):
        self._init()

        extractor = self.extractor
        sleep = util.build_duration_func(
            extractor.config("sleep-extractor"))
        if sleep is not None:
            extractor.sleep(sleep(), "extractor")

        # collect data
        try:
            for msg in extractor:
                self.dispatch(msg)
        except exception.StopExtraction:
            pass
        except Exception as exc:
            self.exception = exc
            self.data.append((-1, {
                "error"  : exc.__class__.__name__,
                "message": str(exc),
            }))
        except BaseException:
            pass

        # convert numbers to string
        if config.get(("output",), "num-to-str", False):
            for msg in self.data:
                util.transform_dict(msg[-1], util.number_to_string)

        if self.file:
            # dump to 'file'
            try:
                util.dump_json(self.data, self.file, self.ascii, 2)
                self.file.flush()
            except Exception:
                pass

        return 0

    def handle_url(self, url, kwdict):
        kwdict = self.filter(kwdict)
        self.data_urls.append(url)
        self.data_meta.append(kwdict)
        self.data.append((Message.Url, url, kwdict))

    def handle_directory(self, kwdict):
        kwdict = self.filter(kwdict)
        self.data_post.append(kwdict)
        self.data.append((Message.Directory, kwdict))

    def handle_queue(self, url, kwdict):
        kwdict = self.filter(kwdict)
        self.data_urls.append(url)
        self.data_meta.append(kwdict)
        self.data.append((Message.Queue, url, kwdict))

    def handle_queue_resolve(self, url, kwdict):
        if cls := kwdict.get("_extractor"):
            extr = cls.from_url(url)
        else:
            extr = extractor.find(url)

        if not extr:
            kwdict = self.filter(kwdict)
            self.data_urls.append(url)
            self.data_meta.append(kwdict)
            return self.data.append((Message.Queue, url, kwdict))

        job = self.__class__(extr, self, None, self.ascii, self.resolve-1)
        job.data = self.data
        job.data_urls = self.data_urls
        job.data_post = self.data_post
        job.data_meta = self.data_meta
        job.run()
