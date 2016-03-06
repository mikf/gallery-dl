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
    _db = sqlite3.connect(path, timeout=30, check_same_thread=False)
    _db.execute("CREATE TABLE IF NOT EXISTS data ("
                    "key TEXT PRIMARY KEY,"
                    "value TEXT,"
                    "expires INTEGER"
                ")")

def cache(maxage=3600, keyarg=None):
    """decorator - cache function return values in memory and database"""
    def wrap(func):
        gkey = "{}.{}".format(func.__module__, func.__name__)

        def wrapped(*args):
            timestamp = time.time()
            if keyarg is not None:
                key = "{}-{}".format(gkey, args[keyarg])
            else:
                key = gkey

            try:
                result = lookup_cache(key, timestamp)
            except CacheInvalidError:
                try:
                    result = func(*args)
                    expires = int(timestamp+maxage)
                    _cache[key] = (result, expires)
                    _db.execute("INSERT OR REPLACE INTO data VALUES (?,?,?)",
                                (key, pickle.dumps(result), expires))
                finally:
                    _db.commit()
            return result

        def lookup_cache(key, timestamp):
            try:
                result, expires = _cache[key]
                if timestamp < expires:
                    return result
            except KeyError:
                pass
            result, expires = lookup_database(key, timestamp)
            _cache[key] = (result, expires)
            return result

        def lookup_database(key, timestamp):
            try:
                cursor = _db.cursor()
                cursor.execute("BEGIN EXCLUSIVE")
                cursor.execute("SELECT value, expires FROM data WHERE key=?",
                               (key,))
                result, expires = cursor.fetchone()
                if timestamp < expires:
                    _db.commit()
                    return pickle.loads(result), expires
            except TypeError:
                pass
            raise CacheInvalidError()

        return wrapped
    return wrap

# --------------------------------------------------------------------
# internals

_db = None
_cache = {}
