#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.util as util


class TestISO639_1(unittest.TestCase):

    def test_code_to_language(self):
        self.assertEqual(util.code_to_language("en"), "English")
        self.assertEqual(util.code_to_language("FR"), "French")
        self.assertEqual(util.code_to_language("xx"), "English")
        self.assertEqual(util.code_to_language("xx", default=None), None)

    def test_language_to_code(self):
        self.assertEqual(util.language_to_code("English"), "en")
        self.assertEqual(util.language_to_code("fRENch"), "fr")
        self.assertEqual(util.language_to_code("xx"), "en")
        self.assertEqual(util.language_to_code("xx", default=None), None)


if __name__ == '__main__':
    unittest.main()
