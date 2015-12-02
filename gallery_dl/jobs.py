# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import tempfile
from . import config, extractor, downloader, text, output
from .extractor.message import Message

class DownloadJob():

    def __init__(self, url):
        self.extractor = extractor.find(url)
        if self.extractor is None:
            print(url, ": No extractor found", sep="", file=sys.stderr)
            return
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
        """Execute/Run the download job"""
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

        if self.queue:
            for url in self.queue:
                DownloadJob(url).run()

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


class KeywordJob():

    def __init__(self, url):
        self.extractor = extractor.find(url)
        if self.extractor is None:
            print(url, ": No extractor found", sep="", file=sys.stderr)
            return

    def run(self):
        """Execute/Run the download job"""
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
        offset = max(map(len, keywords.keys())) + 1
        for key, value in sorted(keywords.items()):
            print(key, ":", " "*(offset-len(key)), value, sep="")
        print()
