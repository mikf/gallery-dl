# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import json
import time
import errno
import logging
import operator
import collections
from . import extractor, downloader, postprocessor
from . import config, text, util, output, exception
from .extractor.message import Message


class Job():
    """Base class for Job-types"""
    ulog = None

    def __init__(self, extr, parent=None):
        if isinstance(extr, str):
            extr = extractor.find(extr)
        if not extr:
            raise exception.NoExtractorError()
        self.extractor = extr
        self.pathfmt = None

        self._logger_extra = {
            "job"      : self,
            "extractor": extr,
            "path"     : output.PathfmtProxy(self),
            "keywords" : output.KwdictProxy(self),
        }
        extr.log = self._wrap_logger(extr.log)
        extr.log.debug("Using %s for '%s'", extr.__class__.__name__, extr.url)

        self.status = 0
        self.pred_url = self._prepare_predicates("image", True)
        self.pred_queue = self._prepare_predicates("chapter", False)
        self.kwdict = {}

        # user-supplied metadata
        kwdict = self.extractor.config("keywords")
        if kwdict:
            self.kwdict.update(kwdict)

        # data from parent job
        if parent:
            pextr = parent.extractor

            # transfer (sub)category
            if pextr.config("category-transfer", pextr.categorytransfer):
                extr.category = pextr.category
                extr.subcategory = pextr.subcategory

            # transfer parent directory
            extr._parentdir = pextr._parentdir

            # reuse connection adapters
            extr.session.adapters = pextr.session.adapters

    def run(self):
        """Execute or run the job"""
        sleep = self.extractor.config("sleep-extractor")
        if sleep:
            time.sleep(sleep)
        try:
            log = self.extractor.log
            for msg in self.extractor:
                self.dispatch(msg)
        except exception.StopExtraction as exc:
            if exc.message:
                log.error(exc.message)
            self.status |= exc.code
        except exception.GalleryDLException as exc:
            log.error("%s: %s", exc.__class__.__name__, exc)
            self.status |= exc.code
        except OSError as exc:
            log.error("Unable to download data:  %s: %s",
                      exc.__class__.__name__, exc)
            log.debug("", exc_info=True)
            self.status |= 128
        except Exception as exc:
            log.error(("An unexpected error occurred: %s - %s. "
                       "Please run gallery-dl again with the --verbose flag, "
                       "copy its output and report this issue on "
                       "https://github.com/mikf/gallery-dl/issues ."),
                      exc.__class__.__name__, exc)
            log.debug("", exc_info=True)
            self.status |= 1
        except BaseException:
            self.status |= 1
            raise
        finally:
            self.handle_finalize()
        return self.status

    def dispatch(self, msg):
        """Call the appropriate message handler"""
        if msg[0] == Message.Url:
            _, url, kwds = msg
            if self.pred_url(url, kwds):
                self.update_kwdict(kwds)
                self.handle_url(url, kwds)

        elif msg[0] == Message.Directory:
            self.update_kwdict(msg[1])
            self.handle_directory(msg[1])

        elif msg[0] == Message.Queue:
            _, url, kwds = msg
            if self.pred_queue(url, kwds):
                self.handle_queue(url, kwds)

        elif msg[0] == Message.Version:
            if msg[1] != 1:
                raise "unsupported message-version ({}, {})".format(
                    self.extractor.category, msg[1]
                )
            # TODO: support for multiple message versions

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
        if self.kwdict:
            kwdict.update(self.kwdict)

    def _prepare_predicates(self, target, skip=True):
        predicates = []

        if self.extractor.config(target + "-unique"):
            predicates.append(util.UniquePredicate())

        pfilter = self.extractor.config(target + "-filter")
        if pfilter:
            try:
                pred = util.FilterPredicate(pfilter, target)
            except (SyntaxError, ValueError, TypeError) as exc:
                self.extractor.log.warning(exc)
            else:
                predicates.append(pred)

        prange = self.extractor.config(target + "-range")
        if prange:
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
        return output.LoggerAdapter(logger, self._logger_extra)

    def _write_unsupported(self, url):
        if self.ulog:
            self.ulog.info(url)


class DownloadJob(Job):
    """Download images into appropriate directory/filename locations"""

    def __init__(self, url, parent=None, kwdict=None):
        Job.__init__(self, url, parent)
        self.log = self.get_logger("download")
        self.blacklist = None
        self.archive = None
        self.sleep = None
        self.hooks = ()
        self.downloaders = {}
        self.out = output.select()

        if parent:
            self.visited = parent.visited
            pfmt = parent.pathfmt
            if pfmt and parent.extractor.config("parent-directory"):
                self.extractor._parentdir = pfmt.directory
            if parent.extractor.config("parent-metadata"):
                if parent.kwdict:
                    self.kwdict.update(parent.kwdict)
                if kwdict:
                    self.kwdict.update(kwdict)
        else:
            self.visited = set()

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

        if archive and archive.check(kwdict):
            pathfmt.fix_extension()
            self.handle_skip()
            return

        if pathfmt.exists():
            if archive:
                archive.add(kwdict)
            self.handle_skip()
            return

        if self.sleep:
            time.sleep(self.sleep)

        # download from URL
        if not self.download(url):

            # use fallback URLs if available
            for num, url in enumerate(kwdict.get("_fallback", ()), 1):
                util.remove_file(pathfmt.temppath)
                self.log.info("Trying fallback URL #%d", num)
                if self.download(url):
                    break
            else:
                # download failed
                self.status |= 4
                self.log.error("Failed to download %s",
                               pathfmt.filename or url)
                return

        if not pathfmt.temppath:
            if archive:
                archive.add(kwdict)
            self.handle_skip()
            return

        # run post processors
        if "file" in hooks:
            for callback in hooks["file"]:
                callback(pathfmt)

        # download succeeded
        pathfmt.finalize()
        self.out.success(pathfmt.path, 0)
        self._skipcnt = 0
        if archive:
            archive.add(kwdict)
        if "after" in hooks:
            for callback in hooks["after"]:
                callback(pathfmt)

    def handle_directory(self, kwdict):
        """Set and create the target directory for downloads"""
        if not self.pathfmt:
            self.initialize(kwdict)
        else:
            self.pathfmt.set_directory(kwdict)
        if "post" in self.hooks:
            for callback in self.hooks["post"]:
                callback(self.pathfmt)

    def handle_queue(self, url, kwdict):
        if url in self.visited:
            return
        self.visited.add(url)

        cls = kwdict.get("_extractor")
        if cls:
            extr = cls.from_url(url)
        else:
            extr = extractor.find(url)
            if extr:
                if self.blacklist is None:
                    self.blacklist = self._build_blacklist()
                if extr.category in self.blacklist:
                    extr = None

        if extr:
            self.status |= self.__class__(extr, self, kwdict).run()
        else:
            self._write_unsupported(url)

    def handle_finalize(self):
        pathfmt = self.pathfmt
        if self.archive:
            self.archive.close()
        if pathfmt:
            self.extractor._store_cookies()
            if "finalize" in self.hooks:
                status = self.status
                for callback in self.hooks["finalize"]:
                    callback(pathfmt, status)

    def handle_skip(self):
        pathfmt = self.pathfmt
        self.out.skip(pathfmt.path)
        if "skip" in self.hooks:
            for callback in self.hooks["skip"]:
                callback(pathfmt)
        if self._skipexc:
            self._skipcnt += 1
            if self._skipcnt >= self._skipmax:
                raise self._skipexc()

    def download(self, url):
        """Download 'url'"""
        scheme = url.partition(":")[0]
        downloader = self.get_downloader(scheme)
        if downloader:
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
        config = self.extractor.config
        pathfmt = self.pathfmt = util.PathFormat(self.extractor)
        if kwdict:
            pathfmt.set_directory(kwdict)

        self.sleep = config("sleep")
        if not config("download", True):
            # monkey-patch method to do nothing and always return True
            self.download = pathfmt.fix_extension

        archive = config("archive")
        if archive:
            path = util.expand_path(archive)
            try:
                if "{" in path:
                    path = util.Formatter(path).format_map(kwdict)
                self.archive = util.DownloadArchive(path, self.extractor)
            except Exception as exc:
                self.extractor.log.warning(
                    "Failed to open download archive at '%s' ('%s: %s')",
                    path, exc.__class__.__name__, exc)
            else:
                self.extractor.log.debug("Using download archive '%s'", path)

        skip = config("skip", True)
        if skip:
            self._skipexc = None
            if skip == "enumerate":
                pathfmt.check_file = pathfmt._enum_file
            elif isinstance(skip, str):
                skip, _, smax = skip.partition(":")
                if skip == "abort":
                    self._skipexc = exception.StopExtraction
                elif skip == "exit":
                    self._skipexc = sys.exit
                self._skipcnt = 0
                self._skipmax = text.parse_int(smax)
        else:
            # monkey-patch methods to always return False
            pathfmt.exists = lambda x=None: False
            if self.archive:
                self.archive.check = pathfmt.exists

        postprocessors = self.extractor.config_accumulate("postprocessors")
        if postprocessors:
            self.hooks = collections.defaultdict(list)
            pp_log = self.get_logger("postprocessor")
            pp_list = []
            category = self.extractor.category
            basecategory = self.extractor.basecategory

            for pp_dict in postprocessors:

                whitelist = pp_dict.get("whitelist")
                if whitelist and category not in whitelist and \
                        basecategory not in whitelist:
                    continue

                blacklist = pp_dict.get("blacklist")
                if blacklist and (
                        category in blacklist or basecategory in blacklist):
                    continue

                name = pp_dict.get("name")
                pp_cls = postprocessor.find(name)
                if not pp_cls:
                    pp_log.warning("module '%s' not found", name)
                    continue
                try:
                    pp_obj = pp_cls(self, pp_dict)
                except Exception as exc:
                    pp_log.error("'%s' initialization failed:  %s: %s",
                                 name, exc.__class__.__name__, exc)
                else:
                    pp_list.append(pp_obj)

            if pp_list:
                self.extractor.log.debug(
                    "Active postprocessor modules: %s", pp_list)
                if "init" in self.hooks:
                    for callback in self.hooks["init"]:
                        callback(pathfmt)

    def _build_blacklist(self):
        wlist = self.extractor.config("whitelist")
        if wlist is not None:
            if isinstance(wlist, str):
                wlist = wlist.split(",")

            # build a set of all categories
            blist = set()
            add = blist.add
            update = blist.update
            get = operator.itemgetter(0)

            for extr in extractor._list_classes():
                category = extr.category
                if category:
                    add(category)
                else:
                    update(map(get, extr.instances))

            # remove whitelisted categories
            blist.difference_update(wlist)
            return blist

        blist = self.extractor.config("blacklist")
        if blist is not None:
            if isinstance(blist, str):
                blist = blist.split(",")
            blist = set(blist)
        else:
            blist = {self.extractor.category}
        blist |= util.SPECIAL_EXTRACTORS
        return blist


class SimulationJob(DownloadJob):
    """Simulate the extraction process without downloading anything"""

    def handle_url(self, url, kwdict):
        if not kwdict["extension"]:
            kwdict["extension"] = "jpg"
        self.pathfmt.set_filename(kwdict)
        self.out.skip(self.pathfmt.path)
        if self.sleep:
            time.sleep(self.sleep)
        if self.archive:
            self.archive.add(kwdict)

    def handle_directory(self, kwdict):
        if not self.pathfmt:
            self.initialize()


class KeywordJob(Job):
    """Print available keywords"""

    def handle_url(self, url, kwdict):
        print("\nKeywords for filenames and --filter:")
        print("------------------------------------")
        self.print_kwdict(kwdict)
        raise exception.StopExtraction()

    def handle_directory(self, kwdict):
        print("Keywords for directory names:")
        print("-----------------------------")
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
            print("Keywords for --chapter-filter:")
            print("------------------------------")
            self.print_kwdict(kwdict)
            if extr or self.extractor.categorytransfer:
                print()
                KeywordJob(extr or url, self).run()
        raise exception.StopExtraction()

    @staticmethod
    def print_kwdict(kwdict, prefix=""):
        """Print key-value pairs in 'kwdict' with formatting"""
        suffix = "]" if prefix else ""
        for key, value in sorted(kwdict.items()):
            if key[0] == "_":
                continue
            key = prefix + key + suffix

            if isinstance(value, dict):
                KeywordJob.print_kwdict(value, key + "[")

            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    KeywordJob.print_kwdict(value[0], key + "[][")
                else:
                    print(key, "[]", sep="")
                    for val in value:
                        print("  -", val)

            else:
                # string or number
                print(key, "\n  ", value, sep="")


class UrlJob(Job):
    """Print download urls"""
    maxdepth = 1

    def __init__(self, url, parent=None, depth=1):
        Job.__init__(self, url, parent)
        self.depth = depth
        if depth >= self.maxdepth:
            self.handle_queue = self.handle_url

    @staticmethod
    def handle_url(url, kwdict):
        print(url)
        if "_fallback" in kwdict:
            for url in kwdict["_fallback"]:
                print("|", url)

    def handle_queue(self, url, _):
        try:
            UrlJob(url, self, self.depth + 1).run()
        except exception.NoExtractorError:
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
        pc("Request interval", "sleep-request", ex.request_interval)

        return 0

    def _print_multi(self, title, *values):
        print(title, "\n  ", " / ".join(json.dumps(v) for v in values), sep="")

    def _print_config(self, title, optname, value):
        optval = self.extractor.config(optname, util.SENTINEL)
        if optval is not util.SENTINEL:
            print(title, "(custom):\n ", json.dumps(optval))
            print(title, "(default):\n ", json.dumps(value))
        elif value:
            print(title, "(default):\n ", json.dumps(value))


class DataJob(Job):
    """Collect extractor results and dump them"""

    def __init__(self, url, parent=None, file=sys.stdout, ensure_ascii=True):
        Job.__init__(self, url, parent)
        self.file = file
        self.data = []
        self.ascii = config.get(("output",), "ascii", ensure_ascii)

        private = config.get(("output",), "private")
        self.filter = (lambda x: x) if private else util.filter_dict

    def run(self):
        sleep = self.extractor.config("sleep-extractor")
        if sleep:
            time.sleep(sleep)

        # collect data
        try:
            for msg in self.extractor:
                self.dispatch(msg)
        except exception.StopExtraction:
            pass
        except Exception as exc:
            self.data.append((exc.__class__.__name__, str(exc)))
        except BaseException:
            pass

        # convert numbers to string
        if config.get(("output",), "num-to-str", False):
            for msg in self.data:
                util.transform_dict(msg[-1], util.number_to_string)

        # dump to 'file'
        try:
            util.dump_json(self.data, self.file, self.ascii, 2)
            self.file.flush()
        except Exception:
            pass

        return 0

    def handle_url(self, url, kwdict):
        self.data.append((Message.Url, url, self.filter(kwdict)))

    def handle_directory(self, kwdict):
        self.data.append((Message.Directory, self.filter(kwdict)))

    def handle_queue(self, url, kwdict):
        self.data.append((Message.Queue, url, self.filter(kwdict)))
