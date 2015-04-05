# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

""" """

import os
import sys
import re
import sqlite3
import importlib


class DownloadManager():

    def __init__(self, opts, conf):
        self.opts = opts
        self.conf = conf
        self.downloaders = {}

    def add(self, extr):
        if self.opts.dest:
            dest = self.opts.dest
        elif extr.category in self.conf:
            dest = self.conf[extr.category].get("destination", "/tmp/")
        else:
            dest = self.conf["general"].get("destination", "/tmp/")
        dest = os.path.join(dest, extr.category, extr.directory)
        os.makedirs(dest, exist_ok=True)

        for url, filename in extr:
            path = os.path.join(dest, filename)
            if os.path.exists(path):
                self.print_skip(path)
                continue
            dl = self.get_downloader(extr, url)
            self.print_start(path)
            tries = dl.download(url, path)
            self.print_success(path, tries)

    def get_downloader(self, extr, url):
        end   = url.find("://")
        proto = url[:end] if end != -1 else "http"
        if proto not in self.downloaders:
            # import downloader
            module = importlib.import_module("."+proto, __package__)
            self.downloaders[proto] = module.Downloader
        return self.downloaders[proto](extr)

    @staticmethod
    def print_start(path):
        print(path, end="")
        sys.stdout.flush()

    @staticmethod
    def print_skip(path):
        print("\033[2m", path, "\033[0m", sep="")

    @staticmethod
    def print_success(path, tries):
        if tries == 0:
            print("\r", end="")
        print("\r\033[1;32m", path, "\033[0m", sep="")


class ExtractorFinder():

    def __init__(self, config):
        self.config = config
        self.match_list = list()
        if "database" in config["general"]:
            path = os.path.expanduser(config["general"]["database"])
            conn = sqlite3.connect(path)
            self.load_from_database(conn)
        self.load_from_config(config)

    def match(self, url):
        for category, regex in self.match_list:
            match = regex.match(url)
            if match:
                module = importlib.import_module("."+category, __package__)
                return module.Extractor(match, self.config)
        return None

    def load_from_database(self, db):
        query = (
            "SELECT regex.re, category.name "
            "FROM   regex JOIN category "
            "ON     regex.category_id = category.id"
        )
        for row in db.execute(query):
            self.add_match(row[1], row[0])

    def load_from_config(self, conf):
        for category in conf:
            for key, value in conf[category].items():
                if(key.startswith("regex")):
                    self.add_match(category, value)

    def add_match(self, category, regex):
        try:
            # print(category, regex)
            self.match_list.append( (category, re.compile(regex)) )
        except:
            print("[Warning] [{0}] failed to compile regular expression '{1}'"
                  .format(category, regex))
