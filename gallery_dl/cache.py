# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utilities for caching function results"""

import os
import time
import logging
from . import config, util

log = logging.getLogger("cache")
DATABASE = PATH = ERR = None


def database():
    global DATABASE, ERR

    try:
        path_ = path()

        if path_ != ":memory:":
            # restrict access permissions for new db files
            os.close(os.open(path_, os.O_CREAT | os.O_RDONLY, 0o600))

        import sqlite3
        DATABASE = sqlite3.connect(path_, timeout=60, check_same_thread=False)
    except Exception as exc:
        log.debug("Failed to connect to SQLite3 database (%s: %s)",
                  exc.__class__.__name__, exc)
        ERR = exc
    else:
        log.debug("Connected to SQLite3 database '%s'", path_)
        DATABASE.execute(
            "CREATE TABLE IF NOT EXISTS data "
            "(key TEXT PRIMARY KEY, value TEXT, expires INTEGER)")

    globals()["database"] = lambda: DATABASE
    return DATABASE


def path():
    global PATH

    path = config.get(("cache",), "file", util.SENTINEL)
    if path is not util.SENTINEL:
        return util.expand_path(path)

    if util.WINDOWS:
        cachedir = os.environ.get("APPDATA", "~")
    else:
        cachedir = os.environ.get("XDG_CACHE_HOME", "~/.cache")

    cachedir = util.expand_path(os.path.join(cachedir, "gallery-dl"))
    os.makedirs(cachedir, exist_ok=True)
    PATH = os.path.join(cachedir, "cache.sqlite3")

    globals()["path"] = lambda: PATH
    return PATH


def error(ret=1):
    log.error("No database connection (%s: %s)", ERR.__class__.__name__, ERR)
    return ret


def get(module):
    if (db := database()) is None:
        return

    try:
        if module == "ALL":
            return db.execute(
                "SELECT * FROM data")
        if module == "VAL":
            return db.execute(
                "SELECT * FROM data WHERE expires > ?",
                (int(time.time()),))
        if module == "EXP":
            return db.execute(
                "SELECT * FROM data WHERE expires < ? AND expires <> 0",
                (int(time.time()),))
        return db.execute(
            "SELECT * FROM data "
            "WHERE key LIKE 'gallery_dl.extractor.' || ? || '.%'",
            (module.lower(),))
    except Exception:
        pass  # database not initialized, cannot be modified, etc.
    return


def clear(module):
    """Delete database entries for 'module'"""
    if (db := database()) is None:
        return

    rowcount = 0
    cursor = db.cursor()

    try:
        if module == "ALL":
            cursor.execute("DELETE FROM data")
        elif module == "EXP":
            cursor.execute(
                "DELETE FROM data WHERE expires < ? AND expires <> 0",
                (int(time.time()),))
        else:
            cursor.execute(
                "DELETE FROM data "
                "WHERE key LIKE 'gallery_dl.extractor.' || ? || '.%'",
                (module.lower(),))
    except Exception:
        pass  # database not initialized, cannot be modified, etc.
    else:
        rowcount = cursor.rowcount
        db.commit()
    return rowcount
