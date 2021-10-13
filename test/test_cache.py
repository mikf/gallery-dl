#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import patch

import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import config, util  # noqa E402

dbpath = tempfile.mkstemp()[1]
config.set(("cache",), "file", dbpath)
from gallery_dl import cache  # noqa E402
cache._init()


#  def tearDownModule():
#      util.remove_file(dbpath)


class TestCache(unittest.TestCase):

    def test_decorator(self):

        @cache.memcache()
        def mc1():
            pass

        @cache.memcache(maxage=10)
        def mc2():
            pass

        @cache.cache()
        def dbc():
            pass

        self.assertIsInstance(mc1, cache.CacheDecorator)
        self.assertIsInstance(mc2, cache.MemoryCacheDecorator)
        self.assertIsInstance(dbc, cache.DatabaseCacheDecorator)

    def test_keyarg_mem_simple(self):
        @cache.memcache(keyarg=2)
        def ka(a, b, c):
            return a+b+c

        self.assertEqual(ka(1, 1, 1), 3)
        self.assertEqual(ka(2, 2, 2), 6)

        self.assertEqual(ka(0, 0, 1), 3)
        self.assertEqual(ka(9, 9, 1), 3)
        self.assertEqual(ka(0, 0, 2), 6)
        self.assertEqual(ka(9, 9, 2), 6)

    def test_keyarg_mem(self):
        @cache.memcache(keyarg=2, maxage=10)
        def ka(a, b, c):
            return a+b+c

        self.assertEqual(ka(1, 1, 1), 3)
        self.assertEqual(ka(2, 2, 2), 6)

        self.assertEqual(ka(0, 0, 1), 3)
        self.assertEqual(ka(9, 9, 1), 3)
        self.assertEqual(ka(0, 0, 2), 6)
        self.assertEqual(ka(9, 9, 2), 6)

    def test_keyarg_db(self):
        @cache.cache(keyarg=2, maxage=10)
        def ka(a, b, c):
            return a+b+c

        self.assertEqual(ka(1, 1, 1), 3)
        self.assertEqual(ka(2, 2, 2), 6)

        self.assertEqual(ka(0, 0, 1), 3)
        self.assertEqual(ka(9, 9, 1), 3)
        self.assertEqual(ka(0, 0, 2), 6)
        self.assertEqual(ka(9, 9, 2), 6)

    def test_expires_mem(self):
        @cache.memcache(maxage=2)
        def ex(a, b, c):
            return a+b+c

        with patch("time.time") as tmock:
            tmock.return_value = 0.001
            self.assertEqual(ex(1, 1, 1), 3)
            self.assertEqual(ex(2, 2, 2), 3)
            self.assertEqual(ex(3, 3, 3), 3)

            # value is still cached after 1 second
            tmock.return_value += 1.0
            self.assertEqual(ex(3, 3, 3), 3)
            self.assertEqual(ex(2, 2, 2), 3)
            self.assertEqual(ex(1, 1, 1), 3)

            # new value after 'maxage' seconds
            tmock.return_value += 1.0
            self.assertEqual(ex(3, 3, 3), 9)
            self.assertEqual(ex(2, 2, 2), 9)
            self.assertEqual(ex(1, 1, 1), 9)

    def test_expires_db(self):
        @cache.cache(maxage=2)
        def ex(a, b, c):
            return a+b+c

        with patch("time.time") as tmock:
            tmock.return_value = 0.999
            self.assertEqual(ex(1, 1, 1), 3)
            self.assertEqual(ex(2, 2, 2), 3)
            self.assertEqual(ex(3, 3, 3), 3)

            # value is still cached after 1 second
            tmock.return_value += 1.0
            self.assertEqual(ex(3, 3, 3), 3)
            self.assertEqual(ex(2, 2, 2), 3)
            self.assertEqual(ex(1, 1, 1), 3)

            # new value after 'maxage' seconds
            tmock.return_value += 1.0
            self.assertEqual(ex(3, 3, 3), 9)
            self.assertEqual(ex(2, 2, 2), 9)
            self.assertEqual(ex(1, 1, 1), 9)

    def test_update_mem_simple(self):
        @cache.memcache(keyarg=0)
        def up(a, b, c):
            return a+b+c

        self.assertEqual(up(1, 1, 1), 3)
        up.update(1, 0)
        up.update(2, 9)
        self.assertEqual(up(1, 0, 0), 0)
        self.assertEqual(up(2, 0, 0), 9)

    def test_update_mem(self):
        @cache.memcache(keyarg=0, maxage=10)
        def up(a, b, c):
            return a+b+c

        self.assertEqual(up(1, 1, 1), 3)
        up.update(1, 0)
        up.update(2, 9)
        self.assertEqual(up(1, 0, 0), 0)
        self.assertEqual(up(2, 0, 0), 9)

    def test_update_db(self):
        @cache.cache(keyarg=0, maxage=10)
        def up(a, b, c):
            return a+b+c

        self.assertEqual(up(1, 1, 1), 3)
        up.update(1, 0)
        up.update(2, 9)
        self.assertEqual(up(1, 0, 0), 0)
        self.assertEqual(up(2, 0, 0), 9)

    def test_invalidate_mem_simple(self):
        @cache.memcache(keyarg=0)
        def inv(a, b, c):
            return a+b+c

        self.assertEqual(inv(1, 1, 1), 3)
        inv.invalidate(1)
        inv.invalidate(2)
        self.assertEqual(inv(1, 0, 0), 1)
        self.assertEqual(inv(2, 0, 0), 2)

    def test_invalidate_mem(self):
        @cache.memcache(keyarg=0, maxage=10)
        def inv(a, b, c):
            return a+b+c

        self.assertEqual(inv(1, 1, 1), 3)
        inv.invalidate(1)
        inv.invalidate(2)
        self.assertEqual(inv(1, 0, 0), 1)
        self.assertEqual(inv(2, 0, 0), 2)

    def test_invalidate_db(self):
        @cache.cache(keyarg=0, maxage=10)
        def inv(a, b, c):
            return a+b+c

        self.assertEqual(inv(1, 1, 1), 3)
        inv.invalidate(1)
        inv.invalidate(2)
        self.assertEqual(inv(1, 0, 0), 1)
        self.assertEqual(inv(2, 0, 0), 2)

    def test_database_read(self):
        @cache.cache(keyarg=0, maxage=10)
        def db(a, b, c):
            return a+b+c

        # initialize cache
        self.assertEqual(db(1, 1, 1), 3)
        db.update(2, 6)

        # check and clear the in-memory portion of said cache
        self.assertEqual(db.cache[1][0], 3)
        self.assertEqual(db.cache[2][0], 6)
        db.cache.clear()
        self.assertEqual(db.cache, {})

        # fetch results from database
        self.assertEqual(db(1, 0, 0), 3)
        self.assertEqual(db(2, 0, 0), 6)

        # check in-memory cache updates
        self.assertEqual(db.cache[1][0], 3)
        self.assertEqual(db.cache[2][0], 6)


if __name__ == '__main__':
    unittest.main()
