#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
from gallery_dl import extractor, job, config


class TestExtractors(unittest.TestCase):

    def setUp(self):
        config.load()
        config.set(("cache", "file"), ":memory:")

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


# dynamically genetate tests
def _generate_test(extr, tcase):
    def test(self):
        url, result = tcase
        print("\n", url, sep="")
        self._run_test(extr, url, result)
    return test


for extr in extractor.extractors():
    # disable extractors that require authentication for now
    if hasattr(extr, "login"):
        continue
    if hasattr(extr, "test") and extr.test:
        name = "test_" + extr.__name__ + "_"
        for num, tcase in enumerate(extr.test, 1):
            test = _generate_test(extr, tcase)
            test.__name__ = name + str(num)
            setattr(TestExtractors, test.__name__, test)
del test

if __name__ == '__main__':
    unittest.main(warnings='ignore')
