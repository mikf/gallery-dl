# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import json
import hashlib
from . import extractor, downloader, path, output, exception
from .extractor.message import Message


class Job():
    """Base class for Job-types"""

    def __init__(self, url):
        self.extractor = extractor.find(url)
        if self.extractor is None:
            raise exception.NoExtractorError(url)

    def run(self):
        """Execute or run the job"""
        for msg in self.extractor:
            if msg[0] == Message.Url:
                self.update_kwdict(msg[2])
                self.handle_url(msg[1], msg[2])

            elif msg[0] == Message.Directory:
                self.update_kwdict(msg[1])
                self.handle_directory(msg[1])

            elif msg[0] == Message.Queue:
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

    def handle_url(self, url, kexwords):
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


class DownloadJob(Job):
    """Download images into appropriate directory/filename locations"""

    def __init__(self, url):
        Job.__init__(self, url)
        self.pathfmt = path.PathFormat(self.extractor)
        self.downloaders = {}
        self.queue = None
        self.out = output.select()

    def run(self):
        Job.run(self)
        if self.queue:
            for url in self.queue:
                try:
                    DownloadJob(url).run()
                except exception.NoExtractorError:
                    pass

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
        """Add url to work-queue"""
        try:
            self.queue.append(url)
        except AttributeError:
            self.queue = [url]

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

    def run(self):
        for msg in self.extractor:
            if msg[0] == Message.Url:
                print("Keywords for filenames:")
                self.update_kwdict(msg[2])
                self.print_keywords(msg[2])
                return
            elif msg[0] == Message.Directory:
                print("Keywords for directory names:")
                self.update_kwdict(msg[1])
                self.print_keywords(msg[1])

    @staticmethod
    def print_keywords(keywords):
        """Print key-value pairs with formatting"""
        offset = max(map(len, keywords.keys())) + 1
        for key, value in sorted(keywords.items()):
            print(key, ":", " "*(offset-len(key)), value, sep="")
        print()


class UrlJob(Job):
    """Print download urls"""

    def handle_url(self, url, _):
        print(url)

    def handle_queue(self, url):
        try:
            UrlJob(url).run()
        except exception.NoExtractorError:
            pass


class HashJob(DownloadJob):
    """Generate SHA1 hashes for extractor results"""

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
