# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utilities for caching function results"""

import sqlite3
import pickle
import os
from . import config, util

DATABASE = None


def database():
    global DATABASE

    try:
        path = _path()

        if path != ":memory:":
            # restrict access permissions for new db files
            os.close(os.open(path, os.O_CREAT | os.O_RDONLY, 0o600))

        DATABASE = sqlite3.connect(path, timeout=60, check_same_thread=False)
        DATABASE.execute(
            "CREATE TABLE IF NOT EXISTS data "
            "(key TEXT PRIMARY KEY, value TEXT, expires INTEGER)")
    except Exception:
        pass

    globals()["database"] = lambda: DATABASE
    return DATABASE


def update(module, name, value, expires=0):
    if db := database():
        with db:
            db.execute("INSERT OR REPLACE INTO data VALUES (?,?,?)",
                       (f"{module}.{name}", pickle.dumps(value), expires))


def clear(module):
    """Delete database entries for 'module'"""
    db = database()
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
