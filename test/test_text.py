#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.text as text

class TestText(unittest.TestCase):

    def test_remove_html(self):
        cases = (
            "Hello World.",
            " Hello  World. ",
            "Hello<br/>World.",
            "<div><span class='a'>Hello</span><strong>World.</strong></div>"
        )
        result = "Hello World."
        for case in cases:
            self.assertEqual(text.remove_html(case), result)

    def test_filename_from_url(self):
        cases = (
            "http://example.org/v2/filename.ext",
            "http://example.org/v2/filename.ext?param=value#fragment",
            "example.org/filename.ext",
            "/filename.ext",
            "filename.ext",
        )
        result = "filename.ext"
        for case in cases:
            self.assertEqual(text.filename_from_url(case), result)

    def test_clean_path(self):
        cases = {
            "Hello World." : ("Hello World.", "Hello World."),
            "Hello/World/.": ("Hello_World_.", "Hello_World_."),
            r'<Hello>:|"World\*?': (
                '_Hello____World___', r'<Hello>:|"World\*?'
            ),
        }
        for case, result in cases.items():
            self.assertEqual(text.clean_path_windows(case), result[0])
            self.assertEqual(text.clean_path_posix  (case), result[1])

if __name__ == '__main__':
    unittest.main()
