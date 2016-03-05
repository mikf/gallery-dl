# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sqlite3
import pickle
import time
import tempfile
import os
from . import config

class CacheInvalidError(Exception):
    pass

def init_database():
    global _db
    path_default = os.path.join(tempfile.gettempdir(), ".gallery-dl.cache")
    path = config.get(("cache", "file"), path_default)
    # timeout = config.get(("cache", "timeout"), 30)
    _db = sqlite3.connect(path, timeout=30)
    _db.execute("CREATE TABLE IF NOT EXISTS data ("
                    "key TEXT PRIMARY KEY,"
                    "value TEXT,"
                    "expires INTEGER"
                ")")

def cache(max_age=3600):
    """decorator - cache function return values in memory and database"""
    def wrap(func):
        key = "{}.{}".format(func.__module__, func.__name__)

        def wrapped(*args):
            timestamp = time.time()
            try:
                result = lookup_cache(timestamp)
            except CacheInvalidError:
                try:
                    result = func(*args)
                    expires = int(timestamp+max_age)
                    _cache[key] = (result, expires)
                    _db.execute("INSERT OR REPLACE INTO data VALUES (?,?,?)",
                                (key, pickle.dumps(result), expires))
                finally:
                    _db.commit()
            return result

        def lookup_cache(timestamp):
            try:
                result, expires = _cache[key]
                if timestamp < expires:
                    return result
            except KeyError:
                pass
            result, expires = lookup_database(timestamp)
            _cache[key] = (result, expires)
            return result

        def lookup_database(timestamp):
            try:
                cursor = _db.cursor()
                cursor.execute("BEGIN EXCLUSIVE")
                cursor.execute("SELECT value, expires FROM data WHERE key=?",
                               (key,))
                result, expires = cursor.fetchone()
                if timestamp < expires:
                    _db.commit()
                    return pickle.loads(result), expires
            except Exception as e:
                print(e)
            raise CacheInvalidError()

        return wrapped
    return wrap

# --------------------------------------------------------------------
# internals

_db = None
_cache = {}

# @cache(50)
# def f():
    # time.sleep(15)
    # print("called f()")
    # return 1

# init_database()

# for i in range(10):
    # print(f())
    # time.sleep(1)
# print(f())
