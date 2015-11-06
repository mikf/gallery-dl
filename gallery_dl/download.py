# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import importlib
from . import config, extractor, text
from .extractor.common import Message

class DownloadManager():

    def __init__(self, opts):
        self.opts = opts
        self.modules = {}

    def add(self, url):
        job = DownloadJob(self, url)
        job.run()

    def get_downloader_module(self, scheme):
        """Return a downloader module suitable for 'scheme'"""
        module = self.modules.get(scheme)
        if module is None:
            module = importlib.import_module(".downloader."+scheme, __package__)
            self.modules[scheme] = module
        return module

    def get_base_directory(self):
        """Return the base-destination-directory for downloads"""
        if self.opts.dest:
            return self.opts.dest
        else:
            return config.get(("base-directory",), default="/tmp/")


class DownloadJob():

    def __init__(self, mngr, url):
        self.mngr = mngr
        self.extractor, self.info = extractor.find(url)
        if self.extractor is None:
            print(url, ": No extractor found", sep="", file=sys.stderr)
            return
        self.directory = mngr.get_base_directory()
        self.downloaders = {}
        self.filename_fmt = config.get(
            ("extractor", self.info["category"], "filename"),
            default=self.info["filename"]
        )
        segments = config.get(
            ("extractor", self.info["category"], "directory"),
            default=self.info["directory"]
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
                        self.info.category, msg[1]
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
        downloader = self.get_downloader(url)
        self.print_start(path)
        tries = downloader.download(url, path)
        self.print_success(path, tries)

    def set_directory(self, msg):
        """Set and create the target directory for downloads"""
        self.directory = os.path.join(
            self.mngr.get_base_directory(),
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
        downloader = self.downloaders.get(scheme)
        if downloader is None:
            module = self.mngr.get_downloader_module(scheme)
            downloader = module.Downloader()
            self.downloaders[scheme] = downloader
        return downloader

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
