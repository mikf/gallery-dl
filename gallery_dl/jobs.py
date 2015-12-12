# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import json
import hashlib
from . import config, extractor, downloader, text, output, exceptions
from .extractor.message import Message

class Job():
    """Base class for Job-types"""

    def __init__(self, url):
        self.extractor = extractor.find(url)
        if self.extractor is None:
            raise exceptions.NoExtractorError(url)

    def run(self):
        """Execute or run the job"""
        pass


class DownloadJob(Job):
    """Download images into appropriate directory/filename locations"""

    def __init__(self, url):
        Job.__init__(self, url)
        self.directory = self.get_base_directory()
        self.downloaders = {}
        self.queue = None
        self.printer = output.select()
        key = ["extractor", self.extractor.category]
        if self.extractor.subcategory:
            key.append(self.extractor.subcategory)
        self.filename_fmt = config.interpolate(
            key + ["filename_fmt"], default=self.extractor.filename_fmt
        )
        segments = config.interpolate(
            key + ["directory_fmt"], default=self.extractor.directory_fmt
        )
        self.directory_fmt = os.path.join(*segments)

    def run(self):
        if self.extractor is None:
            return

        for msg in self.extractor:
            if msg[0] == Message.Url:
                self.download(msg)

            elif msg[0] == Message.Headers:
                self.get_downloader("http:").set_headers(msg[1])

            elif msg[0] == Message.Cookies:
                self.get_downloader("http:").set_cookies(msg[1])

            elif msg[0] == Message.Directory:
                self.set_directory(msg)

            elif msg[0] == Message.Queue:
                self.enqueue(msg[1])

            elif msg[0] == Message.Version:
                if msg[1] != 1:
                    raise "unsupported message-version ({}, {})".format(
                        self.extractor.category, msg[1]
                    )
                # TODO: support for multiple message versions
            self.run_queue()

    def run_queue(self):
        """Run all jobs stored in queue"""
        if not self.queue:
            return
        for url in self.queue:
            try:
                DownloadJob(url).run()
            except exceptions.NoExtractorError:
                pass

    def download(self, msg):
        """Download the resource specified in 'msg'"""
        _, url, metadata = msg
        filename = text.clean_path(self.filename_fmt.format(**metadata))
        path = os.path.join(self.directory, filename)
        if os.path.exists(path):
            self.printer.skip(path)
            return
        dlinstance = self.get_downloader(url)
        self.printer.start(path)
        tries = dlinstance.download(url, path)
        self.printer.success(path, tries)

    def set_directory(self, msg):
        """Set and create the target directory for downloads"""
        self.directory = os.path.join(
            self.get_base_directory(),
            self.directory_fmt.format(**{
                key: text.clean_path(value) for key, value in msg[1].items()
            })
        )
        os.makedirs(self.directory, exist_ok=True)

    def get_downloader(self, url):
        """Return, and possibly construct, a downloader suitable for 'url'"""
        pos = url.find(":")
        scheme = url[:pos] if pos != -1 else "http"
        if scheme == "https":
            scheme = "http"
        instance = self.downloaders.get(scheme)
        if instance is None:
            klass = downloader.find(scheme)
            instance = klass(self.printer)
            self.downloaders[scheme] = instance
        return instance

    def enqueue(self, url):
        """Add url to work-queue"""
        try:
            self.queue.append(url)
        except AttributeError:
            self.queue = [url]

    @staticmethod
    def get_base_directory():
        """Return the base-destination-directory for downloads"""
        bdir = config.get(("base-directory",), default=(".", "gallery-dl"))
        if not isinstance(bdir, str):
            bdir = os.path.join(*bdir)
        return os.path.expanduser(os.path.expandvars(bdir))


class KeywordJob(Job):
    """Print available keywords"""

    def run(self):
        if self.extractor is None:
            return
        for msg in self.extractor:
            if msg[0] == Message.Url:
                print("Keywords for filenames:")
                self.print_keywords(msg[2])
                return
            elif msg[0] == Message.Directory:
                print("Keywords for directory names:")
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

    def run(self):
        if self.extractor is None:
            return
        for msg in self.extractor:
            if msg[0] == Message.Url:
                print(msg[1])


class HashJob(DownloadJob):
    """Generate SHA1 hashes for extractor results"""

    def __init__(self, url):
        DownloadJob.__init__(self, url)
        self.hash_url     = hashlib.sha1()
        self.hash_keyword = hashlib.sha1()

    def download(self, msg):
        self.update_url(msg[1])
        self.update_keyword(msg[2])

    def set_directory(self, msg):
        self.update_keyword(msg[1])

    def enqueue(self, url):
        self.update_url(url)

    def update_url(self, url):
        self.hash_url.update(url.encode())

    def update_keyword(self, kwdict):
        self.hash_keyword.update(
            json.dumps(kwdict, sort_keys=True).encode()
        )
