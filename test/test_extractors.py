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
        config.set(("downloader", "part"), False)

    def tearDown(self):
        config.clear()

    def _run_test(self, extr, url, result):
        if result:
            if "options" in result:
                for key, value in result["options"]:
                    config.set(key.split("."), value)
            content = "content" in result
        else:
            content = False

        tjob = job.TestJob(url, content=content)
        self.assertEqual(extr, tjob.extractor.__class__)

        if not result:
            return
        if "exception" in result:
            self.assertRaises(result["exception"], tjob.run)
            return

        tjob.run()
        if "url" in result:
            self.assertEqual(result["url"], tjob.hash_url.hexdigest())
        if "keyword" in result:
            self.assertEqual(result["keyword"], tjob.hash_keyword.hexdigest())
        if "content" in result:
            self.assertEqual(result["content"], tjob.hash_content.hexdigest())
        if "count" in result:
            self.assertEqual(len(tjob.urllist), int(result["count"]))
        if "pattern" in result:
            for url in tjob.urllist:
                self.assertRegex(url, result["pattern"])


# dynamically generate tests
def _generate_test(extr, tcase):
    def test(self):
        url, result = tcase
        print("\n", url, sep="")
        self._run_test(extr, url, result)
    return test


skip = [
    # don't work on travis-ci
    "exhentai", "kissmanga", "mangafox", "dynastyscans", "nijie",
    "archivedmoe", "archiveofsins", "thebarchive",
    # temporary issues
    "nyafuu",
    "mangazuki",
]
# enable selective testing for direct calls
if __name__ == '__main__' and len(sys.argv) > 1:
    if sys.argv[1].lower() == "all":
        extractors = extractor.extractors()
    else:
        extractors = [
            extr for extr in extractor.extractors()
            if extr.category in sys.argv or
            hasattr(extr, "basecategory") and extr.basecategory in sys.argv
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
