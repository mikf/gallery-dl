#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, cache, config, util  # noqa E402
from gallery_dl.extractor.common import CACHE_MEMORY as CACHE  # noqa E402


def setUpModule():
    if cache.DATABASE is None:
        import atexit
        import tempfile
        dbpath = tempfile.mkstemp()[1]
        config.set(("cache",), "file", dbpath)
        atexit.register(util.remove_file, dbpath)


class TestCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extr = extr = extractor.find("noop")
        cls.cache = extr.cache
        cls.cache_update = extr.cache_update

    def setUp(self):
        CACHE.clear()

    def tearDown(self):
        CACHE.clear()

    def _eq(self, func, expected, args, **kwargs):
        self.assertEqual(
            self.extr.cache(func, *args, **kwargs),
            expected,
            f"{func.__name__}({args}, {kwargs})",
        )

    def test_keyarg_mem_simple(self):
        def ka(a, b, c):
            return a+b+c

        self._eq(ka, 3, (1, 1, 1), _key=2)
        self._eq(ka, 6, (2, 2, 2), _key=2)

        self._eq(ka, 3, (0, 0, 1), _key=2)
        self._eq(ka, 3, (9, 9, 1), _key=2)
        self._eq(ka, 6, (0, 0, 2), _key=2)
        self._eq(ka, 6, (9, 9, 2), _key=2)

    def test_keyarg_mem(self):
        def ka(a, b, c):
            return a+b+c

        self._eq(ka, 3, (1, 1, 1), _key=2, _exp=10)
        self._eq(ka, 6, (2, 2, 2), _key=2, _exp=10)

        self._eq(ka, 3, (0, 0, 1), _key=2, _exp=10)
        self._eq(ka, 3, (9, 9, 1), _key=2, _exp=10)
        self._eq(ka, 6, (0, 0, 2), _key=2, _exp=10)
        self._eq(ka, 6, (9, 9, 2), _key=2, _exp=10)

    def test_keyarg_db(self):
        def ka(a, b, c):
            return a+b+c

        self._eq(ka, 3, (1, 1, 1), _key=2, _exp=10, _mem=False)
        self._eq(ka, 6, (2, 2, 2), _key=2, _exp=10, _mem=False)

        self._eq(ka, 3, (0, 0, 1), _key=2, _exp=10, _mem=False)
        self._eq(ka, 3, (9, 9, 1), _key=2, _exp=10, _mem=False)
        self._eq(ka, 6, (0, 0, 2), _key=2, _exp=10, _mem=False)
        self._eq(ka, 6, (9, 9, 2), _key=2, _exp=10, _mem=False)

    def test_expires_mem(self):
        def ex(a, b, c):
            return a+b+c

        with patch("time.time") as tmock:
            tmock.return_value = 8.001
            self._eq(ex, 3, (1, 1, 1), _key=None, _exp=2)
            self._eq(ex, 3, (2, 2, 2), _key=None, _exp=2)
            self._eq(ex, 3, (3, 3, 3), _key=None, _exp=2)

            # value is still cached after 1 second
            tmock.return_value += 1.0
            self._eq(ex, 3, (3, 3, 3), _key=None, _exp=2)
            self._eq(ex, 3, (2, 2, 2), _key=None, _exp=2)
            self._eq(ex, 3, (1, 1, 1), _key=None, _exp=2)

            # new value after '_exp' seconds
            tmock.return_value += 1.0
            self._eq(ex, 9, (3, 3, 3), _key=None, _exp=2)
            self._eq(ex, 9, (2, 2, 2), _key=None, _exp=2)
            self._eq(ex, 9, (1, 1, 1), _key=None, _exp=2)

    def test_expires_db(self):
        def ex(a, b, c):
            return a+b+c

        self.cache_update(ex, None)  # delete old db entry
        with patch("time.time") as tmock:
            tmock.return_value = 8.999
            self._eq(ex, 3, (1, 1, 1), _key=None, _exp=2, _mem=False)
            self._eq(ex, 3, (2, 2, 2), _key=None, _exp=2, _mem=False)
            self._eq(ex, 3, (3, 3, 3), _key=None, _exp=2, _mem=False)

            # value is still cached after 1 second
            tmock.return_value += 1.0
            self._eq(ex, 3, (3, 3, 3), _key=None, _exp=2, _mem=False)
            self._eq(ex, 3, (2, 2, 2), _key=None, _exp=2, _mem=False)
            self._eq(ex, 3, (1, 1, 1), _key=None, _exp=2, _mem=False)

            # new value after '_exp' seconds
            tmock.return_value += 1.0
            self._eq(ex, 9, (3, 3, 3), _key=None, _exp=2, _mem=False)
            self._eq(ex, 9, (2, 2, 2), _key=None, _exp=2, _mem=False)
            self._eq(ex, 9, (1, 1, 1), _key=None, _exp=2, _mem=False)

    def test_update_mem_simple(self):
        def up(a, b, c):
            return a+b+c

        self._eq(up, 3, (1, 1, 1))
        self.cache_update(up, 1, 0)
        self.cache_update(up, 2, 9)
        self._eq(up, 0, (1, 0, 0))
        self._eq(up, 9, (2, 0, 0))

    def test_update_mem(self):
        def up(a, b, c):
            return a+b+c

        self._eq(up, 3, (1, 1, 1), _exp=10)
        self.cache_update(up, 1, 0, _exp=10)
        self.cache_update(up, 2, 9, _exp=10)
        self._eq(up, 0, (1, 0, 0), _exp=10)
        self._eq(up, 9, (2, 0, 0), _exp=10)

    def test_update_db(self):
        def up(a, b, c):
            return a+b+c

        self.cache_update(up, 1, None)  # delete old db entry
        self._eq(up, 3, (1, 1, 1), _exp=10, _mem=False)

        self.cache_update(up, 1, 0, _exp=10)
        self.cache_update(up, 2, 9, _exp=10)
        self._eq(up, 0, (1, 0, 0), _exp=10, _mem=False)
        self._eq(up, 9, (2, 0, 0), _exp=10, _mem=False)

    def test_invalidate_mem_simple(self):
        def inv(a, b, c):
            return a+b+c

        self._eq(inv, 3, (1, 1, 1))
        self.cache_update(inv, 1, None, _mem=True)
        self.cache_update(inv, 2, None, _mem=True)
        self._eq(inv, 1, (1, 0, 0))
        self._eq(inv, 2, (2, 0, 0))

    def test_invalidate_mem(self):
        def inv(a, b, c):
            return a+b+c

        self._eq(inv, 3, (1, 1, 1), _exp=10)
        self.cache_update(inv, 1, None, _mem=True)
        self.cache_update(inv, 2, None, _mem=True)
        self._eq(inv, 1, (1, 0, 0), _exp=10)
        self._eq(inv, 2, (2, 0, 0), _exp=10)

    def test_invalidate_db(self):
        def inv(a, b, c):
            return a+b+c

        self.cache_update(inv, 1, None)  # delete old db entry
        self._eq(inv, 3, (1, 1, 1), _exp=10, _mem=False)

        self.cache_update(inv, 1, None)
        self.cache_update(inv, 2, None)
        self._eq(inv, 1, (1, 0, 0), _exp=10, _mem=False)
        self._eq(inv, 2, (2, 0, 0), _exp=10, _mem=False)

    def test_database_read(self):
        def db(a, b, c):
            return a+b+c
        db.__module__ = "test"

        # delete old db entries
        self.cache_update(db, 1, None)
        self.cache_update(db, 2, None)

        # initialize cache
        self._eq(db, 3, (1, 1, 1), _mem=False)
        self.cache_update(db, 2, 6)

        # check and clear the in-memory portion of said cache
        self.assertEqual(CACHE["test.db-1"], (3, 0))
        self.assertEqual(CACHE["test.db-1"], (3, 0))
        CACHE.clear()
        self.assertEqual(CACHE, {})

        # fetch results from database
        self._eq(db, 3, (1, 0, 0), _mem=False)
        self._eq(db, 6, (2, 0, 0), _mem=False)

        # check in-memory cache updates
        self.assertEqual(CACHE["test.db-1"], (3, 0))
        self.assertEqual(CACHE["test.db-2"], (6, 0))


if __name__ == "__main__":
    unittest.main()
