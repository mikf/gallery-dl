# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import json
import hashlib
from . import extractor, downloader, config, util, output, exception
from .extractor.message import Message


class Job():
    """Base class for Job-types"""
    ufile = None

    def __init__(self, url):
        self.url = url
        self.extractor = extractor.find(url)
        if self.extractor is None:
            raise exception.NoExtractorError(url)
        self.extractor.log.debug(
            "Using %s for %s", self.extractor.__class__.__name__, url)

        items = config.get(("images",))
        if items:
            pred = util.RangePredicate(items)
            if pred.lower > 1:
                pred.index += self.extractor.skip(pred.lower - 1)
            self.pred_url = pred
        else:
            self.pred_url = True

        items = config.get(("chapters",))
        self.pred_queue = util.RangePredicate(items) if items else True

    def run(self):
        """Execute or run the job"""
        try:
            log = self.extractor.log
            for msg in self.extractor:
                self.dispatch(msg)
        except exception.AuthenticationError:
            log.error("Authentication failed. Please provide a valid "
                      "username/password pair.")
        except exception.AuthorizationError:
            log.error("You do not have permission to access the resource "
                      "at '%s'", self.url)
        except exception.NotFoundError as err:
            res = str(err) or "resource (gallery/image/user)"
            log.error("The %s at '%s' does not exist", res, self.url)
        except exception.StopExtraction:
            pass
        except Exception as exc:
            msg = "An unexpected error occurred:"
            try:
                err = ": ".join(exc.args[0].reason.args[0].split(": ")[1:])
                log.error("%s: %s - %s", msg, exc.__class__.__name__, err)
                return
            except Exception:
                pass
            log.error(msg, exc_info=True)

    def dispatch(self, msg):
        """Call the appropriate message handler"""
        if msg[0] == Message.Url:
            if self.pred_url:
                self.update_kwdict(msg[2])
                self.handle_url(msg[1], msg[2])

        elif msg[0] == Message.Directory:
            self.update_kwdict(msg[1])
            self.handle_directory(msg[1])

        elif msg[0] == Message.Queue:
            if self.pred_queue:
                self.handle_queue(msg[1])

        elif msg[0] == Message.Headers:
            self.handle_headers(msg[1])

        elif msg[0] == Message.Cookies:
            self.handle_cookies(msg[1])

        elif msg[0] == Message.Version:
            if msg[1] != 1:
                raise "unsupported message-version ({}, {})".format(
                    self.extractor.category, msg[1]
                )
            # TODO: support for multiple message versions

    def handle_url(self, url, keywords):
        """Handle Message.Url"""

    def handle_directory(self, keywords):
        """Handle Message.Directory"""

    def handle_queue(self, url):
        """Handle Message.Queue"""

    def handle_headers(self, headers):
        """Handle Message.Headers"""

    def handle_cookies(self, cookies):
        """Handle Message.Cookies"""

    def update_kwdict(self, kwdict):
        """Add 'category' and 'subcategory' keywords"""
        kwdict["category"] = self.extractor.category
        kwdict["subcategory"] = self.extractor.subcategory

    def _write_unsupported(self, url):
        if self.ufile:
            print(url, file=self.ufile, flush=True)


class DownloadJob(Job):
    """Download images into appropriate directory/filename locations"""

    def __init__(self, url):
        Job.__init__(self, url)
        self.pathfmt = util.PathFormat(self.extractor)
        self.downloaders = {}
        self.out = output.select()

    def handle_url(self, url, keywords):
        """Download the resource specified in 'url'"""
        self.pathfmt.set_keywords(keywords)
        if self.pathfmt.exists():
            self.out.skip(self.pathfmt.path)
            return
        dlinstance = self.get_downloader(url)
        dlinstance.download(url, self.pathfmt)

    def handle_directory(self, keywords):
        """Set and create the target directory for downloads"""
        self.pathfmt.set_directory(keywords)

    def handle_queue(self, url):
        try:
            DownloadJob(url).run()
        except exception.NoExtractorError:
            self._write_unsupported(url)

    def handle_headers(self, headers):
        self.get_downloader("http:").set_headers(headers)

    def handle_cookies(self, cookies):
        self.get_downloader("http:").set_cookies(cookies)

    def get_downloader(self, url):
        """Return, and possibly construct, a downloader suitable for 'url'"""
        pos = url.find(":")
        scheme = url[:pos] if pos != -1 else "http"
        if scheme == "https":
            scheme = "http"
        instance = self.downloaders.get(scheme)
        if instance is None:
            klass = downloader.find(scheme)
            instance = klass(self.out)
            self.downloaders[scheme] = instance
        return instance


class KeywordJob(Job):
    """Print available keywords"""

    def handle_url(self, url, keywords):
        print("\nKeywords for filenames:")
        print("-----------------------")
        self.print_keywords(keywords)
        raise exception.StopExtraction()

    def handle_directory(self, keywords):
        print("Keywords for directory names:")
        print("-----------------------------")
        self.print_keywords(keywords)

    @staticmethod
    def print_keywords(keywords, prefix=""):
        """Print key-value pairs with formatting"""
        suffix = "]" if prefix else ""
        for key, value in sorted(keywords.items()):
            key = prefix + key + suffix

            if isinstance(value, dict):
                KeywordJob.print_keywords(value, key + "[")

            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    KeywordJob.print_keywords(value[0], key + "[][")
                else:
                    print(key, "[]", sep="")
                    for val in value:
                        print("  -", val)

            else:
                # string or number
                print(key, "\n  ", value, sep="")


class UrlJob(Job):
    """Print download urls"""
    maxdepth = -1

    def __init__(self, url, depth=1):
        Job.__init__(self, url)
        self.depth = depth
        if depth == self.maxdepth:
            self.handle_queue = print

    @staticmethod
    def handle_url(url, _):
        print(url)

    def handle_queue(self, url):
        try:
            UrlJob(url, self.depth + 1).run()
        except exception.NoExtractorError:
            self._write_unsupported(url)


class TestJob(DownloadJob):
    """Generate test-results for extractor runs"""

    class HashIO():
        """Minimal file-like interface"""

        def __init__(self, hashobj):
            self.hashobj = hashobj
            self.path = ""
            self.has_extension = True

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def open(self):
            return self

        def write(self, content):
            """Update SHA1 hash"""
            self.hashobj.update(content)

    def __init__(self, url, content=False):
        DownloadJob.__init__(self, url)
        self.content = content
        self.hash_url = hashlib.sha1()
        self.hash_keyword = hashlib.sha1()
        self.hash_content = hashlib.sha1()
        if content:
            self.fileobj = self.HashIO(self.hash_content)

    def run(self):
        for msg in self.extractor:
            self.dispatch(msg)

    def handle_url(self, url, keywords):
        self.update_url(url)
        self.update_keyword(keywords)
        self.update_content(url)

    def handle_directory(self, keywords):
        self.update_keyword(keywords)

    def handle_queue(self, url):
        self.update_url(url)

    def update_url(self, url):
        """Update the URL hash"""
        self.hash_url.update(url.encode())

    def update_keyword(self, kwdict):
        """Update the keyword hash"""
        self.hash_keyword.update(
            json.dumps(kwdict, sort_keys=True).encode()
        )

    def update_content(self, url):
        """Update the content hash"""
        if self.content:
            self.get_downloader(url).download(url, self.fileobj)


class DataJob(Job):
    """Collect extractor results and dump them"""

    def __init__(self, url, file=sys.stdout):
        Job.__init__(self, url)
        self.file = file
        self.data = []
        self.ensure_ascii = config.get(("output", "ascii"), True)

    def run(self):
        # collect data
        try:
            for msg in self.extractor:
                if msg[0] in (Message.Headers, Message.Cookies):
                    copy = (msg[0], dict(msg[1]))
                else:
                    copy = [
                        part.copy() if hasattr(part, "copy") else part
                        for part in msg
                    ]
                self.data.append(copy)
        except Exception as exc:
            self.data.append((exc.__class__.__name__, str(exc)))

        # dump to 'file'
        json.dump(
            self.data, self.file,
            sort_keys=True, indent=2, ensure_ascii=self.ensure_ascii
        )
        self.file.write("\n")
