# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Download Archives"""

import os
import sqlite3
from . import formatter


class DownloadArchive():

    def __init__(self, path, format_string, pragma=None,
                 cache_key="_archive_key"):
        try:
            con = sqlite3.connect(path, timeout=60, check_same_thread=False)
        except sqlite3.OperationalError:
            os.makedirs(os.path.dirname(path))
            con = sqlite3.connect(path, timeout=60, check_same_thread=False)
        con.isolation_level = None

        self.keygen = formatter.parse(format_string).format_map
        self.connection = con
        self.close = con.close
        self.cursor = cursor = con.cursor()
        self._cache_key = cache_key

        if pragma:
            for stmt in pragma:
                cursor.execute("PRAGMA " + stmt)

        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS archive "
                           "(entry TEXT PRIMARY KEY) WITHOUT ROWID")
        except sqlite3.OperationalError:
            # fallback for missing WITHOUT ROWID support (#553)
            cursor.execute("CREATE TABLE IF NOT EXISTS archive "
                           "(entry TEXT PRIMARY KEY)")

    def add(self, kwdict):
        """Add item described by 'kwdict' to archive"""
        key = kwdict.get(self._cache_key) or self.keygen(kwdict)
        self.cursor.execute(
            "INSERT OR IGNORE INTO archive (entry) VALUES (?)", (key,))

    def check(self, kwdict):
        """Return True if the item described by 'kwdict' exists in archive"""
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        self.cursor.execute(
            "SELECT 1 FROM archive WHERE entry=? LIMIT 1", (key,))
        return self.cursor.fetchone()

    def finalize(self):
        pass


class DownloadArchiveMemory(DownloadArchive):

    def __init__(self, path, format_string, pragma=None,
                 cache_key="_archive_key"):
        DownloadArchive.__init__(self, path, format_string, pragma, cache_key)
        self.keys = set()

    def add(self, kwdict):
        self.keys.add(
            kwdict.get(self._cache_key) or
            self.keygen(kwdict))

    def check(self, kwdict):
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        if key in self.keys:
            return True
        self.cursor.execute(
            "SELECT 1 FROM archive WHERE entry=? LIMIT 1", (key,))
        return self.cursor.fetchone()

    def finalize(self):
        if not self.keys:
            return

        cursor = self.cursor
        with self.connection:
            try:
                cursor.execute("BEGIN")
            except sqlite3.OperationalError:
                pass

            stmt = "INSERT OR IGNORE INTO archive (entry) VALUES (?)"
            if len(self.keys) < 100:
                for key in self.keys:
                    cursor.execute(stmt, (key,))
            else:
                cursor.executemany(stmt, ((key,) for key in self.keys))
