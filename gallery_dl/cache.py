# -*- coding: utf-8 -*-

# Copyright 2016-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Decorators to keep function results in an in-memory and database cache"""

import sqlite3
import pickle
import time
import os
import functools
from . import config, util


class CacheDecorator():
    """Simplified in-memory cache"""
    def __init__(self, func, keyarg):
        self.func = func
        self.cache = {}
        self.keyarg = keyarg

    def __get__(self, instance, cls):
        return functools.partial(self.__call__, instance)

    def __call__(self, *args, **kwargs):
        key = "" if self.keyarg is None else args[self.keyarg]
        try:
            value = self.cache[key]
        except KeyError:
            value = self.cache[key] = self.func(*args, **kwargs)
        return value

    def update(self, key, value):
        self.cache[key] = value

    def invalidate(self, key=""):
        try:
            del self.cache[key]
        except KeyError:
            pass


class MemoryCacheDecorator(CacheDecorator):
    """In-memory cache"""
    def __init__(self, func, keyarg, maxage):
        CacheDecorator.__init__(self, func, keyarg)
        self.maxage = maxage

    def __call__(self, *args, **kwargs):
        key = "" if self.keyarg is None else args[self.keyarg]
        timestamp = int(time.time())
        try:
            value, expires = self.cache[key]
        except KeyError:
            expires = 0
        if expires <= timestamp:
            value = self.func(*args, **kwargs)
            expires = timestamp + self.maxage
            self.cache[key] = value, expires
        return value

    def update(self, key, value):
        self.cache[key] = value, int(time.time()) + self.maxage


class DatabaseCacheDecorator():
    """Database cache"""
    db = None
    _init = True

    def __init__(self, func, keyarg, maxage):
        self.key = "%s.%s" % (func.__module__, func.__name__)
        self.func = func
        self.cache = {}
        self.keyarg = keyarg
        self.maxage = maxage

    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        key = "" if self.keyarg is None else args[self.keyarg]
        timestamp = int(time.time())

        # in-memory cache lookup
        try:
            value, expires = self.cache[key]
            if expires > timestamp:
                return value
        except KeyError:
            pass

        # database lookup
        fullkey = "%s-%s" % (self.key, key)
        with self.database() as db:
            cursor = db.cursor()
            try:
                cursor.execute("BEGIN EXCLUSIVE")
            except sqlite3.OperationalError:
                pass  # Silently swallow exception - workaround for Python 3.6
            cursor.execute(
                "SELECT value, expires FROM data WHERE key=? LIMIT 1",
                (fullkey,),
            )
            result = cursor.fetchone()

            if result and result[1] > timestamp:
                value, expires = result
                value = pickle.loads(value)
            else:
                value = self.func(*args, **kwargs)
                expires = timestamp + self.maxage
                cursor.execute(
                    "INSERT OR REPLACE INTO data VALUES (?,?,?)",
                    (fullkey, pickle.dumps(value), expires),
                )

        self.cache[key] = value, expires
        return value

    def update(self, key, value):
        expires = int(time.time()) + self.maxage
        self.cache[key] = value, expires
        with self.database() as db:
            db.execute(
                "INSERT OR REPLACE INTO data VALUES (?,?,?)",
                ("%s-%s" % (self.key, key), pickle.dumps(value), expires),
            )

    def invalidate(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass
        with self.database() as db:
            db.execute(
                "DELETE FROM data WHERE key=?",
                ("%s-%s" % (self.key, key),),
            )

    def database(self):
        if self._init:
            self.db.execute(
                "CREATE TABLE IF NOT EXISTS data "
                "(key TEXT PRIMARY KEY, value TEXT, expires INTEGER)"
            )
            DatabaseCacheDecorator._init = False
        return self.db


def memcache(maxage=None, keyarg=None):
    if maxage:
        def wrap(func):
            return MemoryCacheDecorator(func, keyarg, maxage)
    else:
        def wrap(func):
            return CacheDecorator(func, keyarg)
    return wrap


def cache(maxage=3600, keyarg=None):
    def wrap(func):
        return DatabaseCacheDecorator(func, keyarg, maxage)
    return wrap


def clear(module):
    """Delete database entries for 'module'"""
    db = DatabaseCacheDecorator.db
    if not db:
        return None

    rowcount = 0
    cursor = db.cursor()

    try:
        if module == "ALL":
            cursor.execute("DELETE FROM data")
        else:
            cursor.execute(
                "DELETE FROM data "
                "WHERE key LIKE 'gallery_dl.extractor.' || ? || '.%'",
                (module.lower(),)
            )
    except sqlite3.OperationalError:
        pass  # database not initialized, cannot be modified, etc.
    else:
        rowcount = cursor.rowcount
        db.commit()
        if rowcount:
            cursor.execute("VACUUM")
    return rowcount


def _path():
    path = config.get(("cache",), "file", util.SENTINEL)
    if path is not util.SENTINEL:
        return util.expand_path(path)

    if util.WINDOWS:
        cachedir = os.environ.get("APPDATA", "~")
    else:
        cachedir = os.environ.get("XDG_CACHE_HOME", "~/.cache")

    cachedir = util.expand_path(os.path.join(cachedir, "gallery-dl"))
    os.makedirs(cachedir, exist_ok=True)
    return os.path.join(cachedir, "cache.sqlite3")


try:
    dbfile = _path()

    # restrict access permissions for new db files
    os.close(os.open(dbfile, os.O_CREAT | os.O_RDONLY, 0o600))

    DatabaseCacheDecorator.db = sqlite3.connect(
        dbfile, timeout=60, check_same_thread=False)
except (OSError, TypeError, sqlite3.OperationalError):
    cache = memcache  # noqa: F811
