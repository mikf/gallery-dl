# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Download Archives"""

import os
import logging
from . import util, formatter

log = logging.getLogger("archive")


def connect(path, prefix, format,
            table=None, mode=None, pragma=None, kwdict=None, cache_key=None):
    keygen = formatter.parse(prefix + format).format_map

    if isinstance(path, str) and path.startswith(
            ("postgres://", "postgresql://")):
        if mode == "memory":
            cls = DownloadArchivePostgresqlMemory
        else:
            cls = DownloadArchivePostgresql
    else:
        path = util.expand_path(path)
        if kwdict is not None and "{" in path:
            path = formatter.parse(path).format_map(kwdict)
        if mode == "memory":
            cls = DownloadArchiveMemory
        else:
            cls = DownloadArchive

    if kwdict is not None and table:
        table = formatter.parse(table).format_map(kwdict)

    return cls(path, keygen, table, pragma, cache_key)


def sanitize(name):
    return '"' + name.replace('"', "_") + '"'


class DownloadArchive():
    _sqlite3 = None

    def __init__(self, path, keygen, table=None, pragma=None, cache_key=None):
        if self._sqlite3 is None:
            DownloadArchive._sqlite3 = __import__("sqlite3")

        try:
            con = self._sqlite3.connect(
                path, timeout=60, check_same_thread=False)
        except self._sqlite3.OperationalError:
            os.makedirs(os.path.dirname(path))
            con = self._sqlite3.connect(
                path, timeout=60, check_same_thread=False)
        con.isolation_level = None

        self.keygen = keygen
        self.connection = con
        self.close = con.close
        self.cursor = cursor = con.cursor()
        self._cache_key = cache_key or "_archive_key"

        table = "archive" if table is None else sanitize(table)
        self._stmt_select = (
            "SELECT 1 "
            "FROM " + table + " "
            "WHERE entry=? "
            "LIMIT 1")
        self._stmt_insert = (
            "INSERT OR IGNORE INTO " + table + " "
            "(entry) VALUES (?)")

        if pragma:
            for stmt in pragma:
                cursor.execute("PRAGMA " + stmt)

        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS " + table + " "
                           "(entry TEXT PRIMARY KEY) WITHOUT ROWID")
        except self._sqlite3.OperationalError:
            # fallback for missing WITHOUT ROWID support (#553)
            cursor.execute("CREATE TABLE IF NOT EXISTS " + table + " "
                           "(entry TEXT PRIMARY KEY)")

    def add(self, kwdict):
        """Add item described by 'kwdict' to archive"""
        key = kwdict.get(self._cache_key) or self.keygen(kwdict)
        self.cursor.execute(self._stmt_insert, (key,))

    def check(self, kwdict):
        """Return True if the item described by 'kwdict' exists in archive"""
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        self.cursor.execute(self._stmt_select, (key,))
        return self.cursor.fetchone()

    def finalize(self):
        pass


class DownloadArchiveMemory(DownloadArchive):

    def __init__(self, path, keygen, table=None, pragma=None, cache_key=None):
        DownloadArchive.__init__(
            self, path, keygen, table, pragma, cache_key)
        self.keys = set()

    def add(self, kwdict):
        self.keys.add(
            kwdict.get(self._cache_key) or
            self.keygen(kwdict))

    def check(self, kwdict):
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        if key in self.keys:
            return True
        self.cursor.execute(self._stmt_select, (key,))
        return self.cursor.fetchone()

    def finalize(self):
        if not self.keys:
            return

        cursor = self.cursor
        with self.connection:
            try:
                cursor.execute("BEGIN")
            except self._sqlite3.OperationalError:
                pass

            stmt = self._stmt_insert
            if len(self.keys) < 100:
                for key in self.keys:
                    cursor.execute(stmt, (key,))
            else:
                cursor.executemany(stmt, ((key,) for key in self.keys))


class DownloadArchivePostgresql():
    _psycopg = None

    def __init__(self, uri, keygen, table=None, pragma=None, cache_key=None):
        if self._psycopg is None:
            DownloadArchivePostgresql._psycopg = __import__("psycopg")

        self.connection = con = self._psycopg.connect(uri)
        self.cursor = cursor = con.cursor()
        self.close = con.close
        self.keygen = keygen
        self._cache_key = cache_key or "_archive_key"

        table = "archive" if table is None else sanitize(table)
        self._stmt_select = (
            "SELECT true "
            "FROM " + table + " "
            "WHERE entry=%s "
            "LIMIT 1")
        self._stmt_insert = (
            "INSERT INTO " + table + " (entry) "
            "VALUES (%s) "
            "ON CONFLICT DO NOTHING")

        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS " + table + " "
                           "(entry TEXT PRIMARY KEY)")
            con.commit()
        except Exception as exc:
            log.error("%s: %s when creating '%s' table: %s",
                      con, exc.__class__.__name__, table, exc)
            con.rollback()
            raise

    def add(self, kwdict):
        key = kwdict.get(self._cache_key) or self.keygen(kwdict)
        try:
            self.cursor.execute(self._stmt_insert, (key,))
            self.connection.commit()
        except Exception as exc:
            log.error("%s: %s when writing entry: %s",
                      self.connection, exc.__class__.__name__, exc)
            self.connection.rollback()

    def check(self, kwdict):
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        try:
            self.cursor.execute(self._stmt_select, (key,))
            return self.cursor.fetchone()
        except Exception as exc:
            log.error("%s: %s when checking entry: %s",
                      self.connection, exc.__class__.__name__, exc)
            self.connection.rollback()
            return False

    def finalize(self):
        pass


class DownloadArchivePostgresqlMemory(DownloadArchivePostgresql):

    def __init__(self, path, keygen, table=None, pragma=None, cache_key=None):
        DownloadArchivePostgresql.__init__(
            self, path, keygen, table, pragma, cache_key)
        self.keys = set()

    def add(self, kwdict):
        self.keys.add(
            kwdict.get(self._cache_key) or
            self.keygen(kwdict))

    def check(self, kwdict):
        key = kwdict[self._cache_key] = self.keygen(kwdict)
        if key in self.keys:
            return True
        try:
            self.cursor.execute(self._stmt_select, (key,))
            return self.cursor.fetchone()
        except Exception as exc:
            log.error("%s: %s when checking entry: %s",
                      self.connection, exc.__class__.__name__, exc)
            self.connection.rollback()
            return False

    def finalize(self):
        if not self.keys:
            return
        try:
            self.cursor.executemany(
                self._stmt_insert,
                ((key,) for key in self.keys))
            self.connection.commit()
        except Exception as exc:
            log.error("%s: %s when writing entries: %s",
                      self.connection, exc.__class__.__name__, exc)
            self.connection.rollback()
