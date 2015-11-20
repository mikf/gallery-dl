# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
from . import config, extractor, downloader, text
from .extractor.common import Message

class DownloadJob():

    def __init__(self, url):
        # self.extractor, self.info = extractor.find(url)
        self.extractor = extractor.find(url)
        if self.extractor is None:
            print(url, ": No extractor found", sep="", file=sys.stderr)
            return
        self.directory = self.get_base_directory()
        self.downloaders = {}
        self.filename_fmt = config.get(
            ("extractor", self.extractor.category, "filename"),
            default=self.extractor.filename_fmt
        )
        segments = config.get(
            ("extractor", self.extractor.category, "directory"),
            default=self.extractor.directory_fmt
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

            elif msg[0] == Message.Version:
                if msg[1] != 1:
                    raise "unsupported message-version ({}, {})".format(
                        self.extractor.category, msg[1]
                    )
                # TODO: support for multiple message versions

    def download(self, msg):
        """Download the resource specified in 'msg'"""
        _, url, metadata = msg
        filename = text.clean_path(self.filename_fmt.format(**metadata))
        path = os.path.join(self.directory, filename)
        if os.path.exists(path):
            self.print_skip(path)
            return
        dlinstance = self.get_downloader(url)
        self.print_start(path)
        tries = dlinstance.download(url, path)
        self.print_success(path, tries)

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
            instance = klass()
            self.downloaders[scheme] = instance
        return instance

    @staticmethod
    def get_base_directory():
        """Return the base-destination-directory for downloads"""
        return config.get(("base-directory",), default="/tmp/")

    @staticmethod
    def print_start(path):
        """Print a message indicating the start of a download"""
        print(path, end="")
        sys.stdout.flush()

    @staticmethod
    def print_skip(path):
        """Print a message indicating that a download has been skipped"""
        print("\033[2m", path, "\033[0m", sep="")

    @staticmethod
    def print_success(path, tries):
        """Print a message indicating the completion of a download"""
        if tries == 0:
            print("\r", end="")
        print("\r\033[1;32m", path, "\033[0m", sep="")


class KeywordJob():

    def __init__(self, url):
        # self.extractor, self.info = extractor.find(url)
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
