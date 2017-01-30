#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.iso639_1 as iso639_1


class TestISO639_1(unittest.TestCase):

    def test_code_to_language(self):
        self.assertEqual(iso639_1.code_to_language("en"), "English")
        self.assertEqual(iso639_1.code_to_language("FR"), "French")
        self.assertEqual(iso639_1.code_to_language("xx"), "English")
        self.assertEqual(iso639_1.code_to_language("xx", default=None), None)

    def test_language_to_code(self):
        self.assertEqual(iso639_1.language_to_code("English"), "en")
        self.assertEqual(iso639_1.language_to_code("fRENch"), "fr")
        self.assertEqual(iso639_1.language_to_code("xx"), "en")
        self.assertEqual(iso639_1.language_to_code("xx", default=None), None)


if __name__ == '__main__':
    unittest.main()
