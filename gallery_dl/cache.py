# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Decorators to keep function results in an in-memory and database cache"""

import sqlite3
import pickle
import time
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

    def invalidate(self, key):
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
        if expires < timestamp:
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
        cursor = self.cursor()
        try:
            cursor.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError:
            pass  # Silently swallow exception - workaround for Python 3.6
        try:
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
        finally:
            self.db.commit()
        self.cache[key] = value, expires
        return value

    def update(self, key, value):
        expires = int(time.time()) + self.maxage
        self.cache[key] = value, expires
        self.cursor().execute(
            "INSERT OR REPLACE INTO data VALUES (?,?,?)",
            ("%s-%s" % (self.key, key), pickle.dumps(value), expires),
        )

    def invalidate(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass
        self.cursor().execute(
            "DELETE FROM data WHERE key=? LIMIT 1",
            ("%s-%s" % (self.key, key),),
        )

    def cursor(self):
        if self._init:
            self.db.execute(
                "CREATE TABLE IF NOT EXISTS data "
                "(key TEXT PRIMARY KEY, value TEXT, expires INTEGER)"
            )
            DatabaseCacheDecorator._init = False
        return self.db.cursor()


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


def clear():
    """Delete all database entries"""
    db = DatabaseCacheDecorator.db

    if db:
        rowcount = 0
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM data")
        except sqlite3.OperationalError:
            pass  # database is not initialized,  can't be modified, etc.
        else:
            rowcount = cursor.rowcount
            db.commit()
            cursor.execute("VACUUM")
        return rowcount

    return None


def _path():
    path = config.get(("cache", "file"), -1)

    if path == -1:
        import tempfile
        import os.path
        return os.path.join(tempfile.gettempdir(), ".gallery-dl.cache")

    return util.expand_path(path)


try:
    DatabaseCacheDecorator.db = sqlite3.connect(
        _path(), timeout=30, check_same_thread=False)
except (TypeError, sqlite3.OperationalError):
    cache = memcache  # noqa: F811
