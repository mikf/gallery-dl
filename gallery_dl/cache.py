# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Decorator to keep function results in a in-memory and database cache"""

import sqlite3
import pickle
import time
import tempfile
import os.path
import functools
from . import config, util


class CacheInvalidError(Exception):
    """A cache entry is either expired or does not exist"""
    pass


class CacheModule():
    """Base class for cache modules"""
    def __init__(self):
        pass

    def __getitem__(self, key):
        raise CacheInvalidError()

    def __setitem__(self, key, item):
        pass

    def __delitem__(self, key):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *exc_info):
        pass


class CacheChain(CacheModule):

    def __init__(self, modules=[]):
        CacheModule.__init__(self)
        self.modules = modules

    def __getitem__(self, key):
        num = 0
        for module in self.modules:
            try:
                value = module[key]
                break
            except CacheInvalidError:
                num += 1
        else:
            raise CacheInvalidError()
        while num:
            num -= 1
            self.modules[num][key[0]] = value
        return value

    def __setitem__(self, key, item):
        for module in self.modules:
            module.__setitem__(key, item)

    def __delitem__(self, key):
        for module in self.modules:
            module.__delitem__(key)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for module in self.modules:
            module.__exit__(exc_type, exc_value, exc_traceback)


class MemoryCache(CacheModule):
    """In-memory cache module"""
    def __init__(self):
        CacheModule.__init__(self)
        self.cache = {}

    def __getitem__(self, key):
        key, timestamp = key
        try:
            value, expires = self.cache[key]
            if timestamp < expires:
                return value, expires
        except KeyError:
            pass
        raise CacheInvalidError()

    def __setitem__(self, key, item):
        self.cache[key] = item

    def __delitem__(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass


class DatabaseCache(CacheModule):
    """Database cache module"""
    def __init__(self):
        CacheModule.__init__(self)
        path_default = os.path.join(tempfile.gettempdir(), ".gallery-dl.cache")
        path = config.get(("cache", "file"), path_default)
        if path is None:
            raise RuntimeError()
        path = util.expand_path(path)
        self.db = sqlite3.connect(path, timeout=30, check_same_thread=False)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS data ("
            "key TEXT PRIMARY KEY,"
            "value TEXT,"
            "expires INTEGER"
            ")"
        )

    def __getitem__(self, key):
        key, timestamp = key
        try:
            cursor = self.db.cursor()
            try:
                cursor.execute("BEGIN EXCLUSIVE")
            except sqlite3.OperationalError:
                """workaround for python 3.6"""
            cursor.execute(
                "SELECT value, expires "
                "FROM data "
                "WHERE key=?",
                (key,)
            )
            value, expires = cursor.fetchone()
            if timestamp < expires:
                self.commit()
                return pickle.loads(value), expires
        except TypeError:
            pass
        raise CacheInvalidError()

    def __setitem__(self, key, item):
        value, expires = item
        self.db.execute("INSERT OR REPLACE INTO data VALUES (?,?,?)",
                        (key, pickle.dumps(value), expires))

    def __delitem__(self, key):
        self.db.execute("DELETE FROM data WHERE key=?", (key,))

    def __exit__(self, *exc_info):
        self.commit()

    def commit(self):
        self.db.commit()


class CacheDecorator():

    def __init__(self, func, module, maxage, keyarg):
        self.func = func
        self.key = "%s.%s" % (func.__module__, func.__name__)
        self.cache = module
        self.maxage = maxage
        self.keyarg = keyarg

    def __call__(self, *args, **kwargs):
        timestamp = time.time()
        if self.keyarg is None:
            key = self.key
        else:
            key = "%s-%s" % (self.key, args[self.keyarg])
        try:
            result, _ = self.cache[key, timestamp]
        except CacheInvalidError:
            with self.cache:
                result = self.func(*args, **kwargs)
                expires = int(timestamp + self.maxage)
                self.cache[key] = result, expires
        return result

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def invalidate(self, key=None):
        key = "%s-%s" % (self.key, key) if key else self.key
        del self.cache[key]

    def update(self, key, result):
        key = "%s-%s" % (self.key, key) if key else self.key
        expires = int(time.time() + self.maxage)
        self.cache[key] = result, expires


def build_cache_decorator(*modules):
    if len(modules) > 1:
        module = CacheChain(modules)
    else:
        module = modules[0]

    def decorator(maxage=3600, keyarg=None):
        def wrap(func):
            return CacheDecorator(func, module, maxage, keyarg)
        return wrap
    return decorator


MEMCACHE = MemoryCache()
memcache = build_cache_decorator(MEMCACHE)

try:
    DBCACHE = DatabaseCache()
    cache = build_cache_decorator(MEMCACHE, DBCACHE)
except (RuntimeError, sqlite3.OperationalError):
    DBCACHE = None
    cache = memcache
