#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.util as util


class TestISO639_1(unittest.TestCase):

    def test_code_to_language(self):
        d = "default"
        self._run_test(util.code_to_language, {
            ("en",): "English",
            ("FR",): "French",
            ("xx",): None,
            (""  ,): None,
            (None,): None,
            ("en", d): "English",
            ("FR", d): "French",
            ("xx", d): d,
            (""  , d): d,
            (None, d): d,
        })

    def test_language_to_code(self):
        d = "default"
        self._run_test(util.language_to_code, {
            ("English",): "en",
            ("fRENch",): "fr",
            ("xx",): None,
            (""  ,): None,
            (None,): None,
            ("English", d): "en",
            ("fRENch", d): "fr",
            ("xx", d): d,
            (""  , d): d,
            (None, d): d,
        })

    def _run_test(self, func, tests):
        for args, result in tests.items():
            self.assertEqual(func(*args), result)


if __name__ == '__main__':
    unittest.main()
