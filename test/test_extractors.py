#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import unittest
from gallery_dl import extractor, job, config


class TestExtractors(unittest.TestCase):

    def setUp(self):
        name = "gallerydl"
        email = "gallerydl@openaliasbox.org"
        config.set(("cache", "file"), ":memory:")
        config.set(("username",), name)
        config.set(("password",), name)
        config.set(("extractor", "nijie", "username"), email)
        config.set(("extractor", "seiga", "username"), email)

    def _run_test(self, extr, url, result):
        hjob = job.HashJob(url, "content" in result)
        self.assertEqual(extr, hjob.extractor.__class__)
        if "exception" in result:
            self.assertRaises(result["exception"], hjob.run)
            return
        hjob.run()
        if "url" in result:
            self.assertEqual(hjob.hash_url.hexdigest(), result["url"])
        if "keyword" in result:
            self.assertEqual(hjob.hash_keyword.hexdigest(), result["keyword"])
        if "content" in result:
            self.assertEqual(hjob.hash_content.hexdigest(), result["content"])


# dynamically genertate tests
def _generate_test(extr, tcase):
    def test(self):
        url, result = tcase
        print("\n", url, sep="")
        self._run_test(extr, url, result)
    return test


# enable selective testing for direct calls
skip = ["exhentai", "kissmanga", "mangafox"]
if __name__ == '__main__' and len(sys.argv) > 1:
    extractors = [
        extr for extr in extractor.extractors()
        if extr.category in sys.argv
    ]
    del sys.argv[1:]
else:
    extractors = [
        extr for extr in extractor.extractors()
        if extr.category not in skip
    ]


for extr in extractors:
    if hasattr(extr, "test") and extr.test:
        name = "test_" + extr.__name__ + "_"
        for num, tcase in enumerate(extr.test, 1):
            test = _generate_test(extr, tcase)
            test.__name__ = name + str(num)
            setattr(TestExtractors, test.__name__, test)
            del test

if __name__ == '__main__':
    unittest.main(warnings='ignore')
