#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
from  gallery_dl import extractor, job, config, cache

class TestExtractors(unittest.TestCase):

    def setUp(self):
        config.load()
        config.set(("cache", "file"), ":memory:")

    def run_test(self, extr, url, result):
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


def generate_test(extr):
    def test(self):
        print("\n", extr.__name__, sep="")
        for url, result in extr.test:
            print(url)
            self.run_test(extr, url, result)
    return test


if __name__ == '__main__':
    import sys
    extractors = extractor.extractors()
    if len(sys.argv) > 1:
        extractors = filter(lambda x: x.category in sys.argv, extractors)
    for extr in extractors:
        if hasattr(extr, "test") and extr.test:
            name = "test_" + extr.__name__
            test = generate_test(extr)
            setattr(TestExtractors, name, test)
    del sys.argv[1:]
    unittest.main(warnings='ignore')
