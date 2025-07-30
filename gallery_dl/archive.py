# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Download Archives"""

import os
import sqlite3
from sqlalchemy import text

from . import formatter, util


class DownloadArchive():

    def __init__(self, path, format_string, pragma=None,
                 cache_key="_archive_key"):
        con = sqlite3.connect(path, timeout=60, check_same_thread=False)
        con.isolation_level = None

        from . import config
        if pragma:
            for stmt in pragma:
                con.execute("PRAGMA " + stmt)
        elif config.get(("extractor",), "archive-pragma"):
            con.execute("PRAGMA synchronous = NORMAL")
            con.execute("PRAGMA journal_mode = WAL")

        self.close = con.close
        self.cursor = con.cursor()
        self.keygen = formatter.parse(format_string).format_map

        self._cache_key = cache_key
        self._cache_update = None
        self._cache_index = 0

        try:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS archive "
                "(entry TEXT PRIMARY KEY) WITHOUT ROWID")
        except sqlite3.OperationalError:
            # fallback for missing WITHOUT ROWID support (#553)
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS archive "
                "(entry TEXT PRIMARY KEY)")

    def check(self, kwdict):
        """Return True if the item described by 'kwdict' exists in archive"""
        key = kwdict.get(self._cache_key) or self.keygen(kwdict)
        self.cursor.execute(
            "SELECT 1 FROM archive WHERE entry = ? LIMIT 1", (key,))
        return self.cursor.fetchone()

    def add(self, kwdict):
        """Add item described by 'kwdict' to archive"""
        key = kwdict.get(self._cache_key) or self.keygen(kwdict)
        self.cursor.execute(
            "INSERT OR IGNORE INTO archive (entry) VALUES (?)", (key,))

    def finalize(self):
        pass

    def _cache(self, kwdict, cache_key="_archive_key"):
        update = self._cache_update
        if update:
            update(kwdict)
        else:
            self._cache_key = cache_key
            self._cache_update = kwdict.update
            self._cache_index = self.cursor.lastrowid

    def _invalidate_cache(self, kwdict=None):
        if kwdict:
            kwdict.pop(self._cache_key, None)
        self._cache_update = None


class DownloadArchiveMemory(DownloadArchive):

    def __init__(self, path, format_string, pragma=None,
                 cache_key="_archive_key"):
        DownloadArchive.__init__(
            self, ":memory:", format_string, pragma, cache_key)
        self.cursor.execute(
            "ATTACH DATABASE ? AS 'ref'", (util.expand_path(path),))
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS ref.archive "
            "(entry TEXT PRIMARY KEY) WITHOUT ROWID")

        self.path = path
        self._check_db = None

    def check(self, kwdict):
        key = kwdict.get(self._cache_key)
        if key is None:
            key = kwdict[self._cache_key] = self.keygen(kwdict)

        self.cursor.execute(
            "SELECT 1 FROM archive WHERE entry = ? LIMIT 1", (key,))
        if self.cursor.fetchone():
            return True

        if self._check_db is None:
            try:
                self.cursor.execute(
                    "SELECT 1 FROM ref.archive WHERE entry = ? LIMIT 1",
                    (key,))
                self._check_db = True
            except sqlite3.OperationalError:
                self._check_db = False

        if self._check_db:
            self.cursor.execute(
                "SELECT 1 FROM ref.archive WHERE entry = ? LIMIT 1", (key,))
            if self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT OR IGNORE INTO archive (entry) VALUES (?)", (key,))
                return True

        return False

    def finalize(self):
        if self._cache_update:
            self._invalidate_cache()

        con = sqlite3.connect(self.path, timeout=60, check_same_thread=False)
        con.isolation_level = None
        cur = con.cursor()

        try:
            cur.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError:
            pass
        else:
            try:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS archive "
                    "(entry TEXT PRIMARY KEY) WITHOUT ROWID")
            except sqlite3.OperationalError:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS archive "
                    "(entry TEXT PRIMARY KEY)")

            cur.execute("INSERT OR IGNORE INTO archive SELECT * FROM main.archive")
            con.commit()
        finally:
            con.close()
