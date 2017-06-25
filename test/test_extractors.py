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
        config.set(("extractor", "username"), name)
        config.set(("extractor", "password"), name)
        config.set(("extractor", "nijie", "username"), email)
        config.set(("extractor", "seiga", "username"), email)

    def _run_test(self, extr, url, result):
        content = "content" in result if result else False
        tjob = job.TestJob(url, content)
        self.assertEqual(extr, tjob.extractor.__class__)
        if not result:
            return
        if "exception" in result:
            self.assertRaises(result["exception"], tjob.run)
            return
        tjob.run()
        if "url" in result:
            self.assertEqual(tjob.hash_url.hexdigest(), result["url"])
        if "keyword" in result:
            self.assertEqual(tjob.hash_keyword.hexdigest(), result["keyword"])
        if "content" in result:
            self.assertEqual(tjob.hash_content.hexdigest(), result["content"])


# dynamically generate tests
def _generate_test(extr, tcase):
    def test(self):
        url, result = tcase
        print("\n", url, sep="")
        self._run_test(extr, url, result)
    return test


skip = [
    # dont work on travis-ci
    "exhentai", "kissmanga", "mangafox", "dynastyscans", "nijie",
    # temporary issues
    "chronos", "coreimg",
]
# enable selective testing for direct calls
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
