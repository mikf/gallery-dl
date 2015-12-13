#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
from  gallery_dl import extractor, jobs, config

class TestExttractors(unittest.TestCase):

    def test_extractors(self):
        config.load()
        for extr in extractor.extractors():
            if not hasattr(extr, "test"):
                continue
            print(extr)
            for url, result in extr.test:
                print(url)
                self.run_test(url, result)

    def run_test(self, url, result):
        hjob = jobs.HashJob(url)
        hjob.run()
        if "url" in result:
            self.assertEqual(hjob.hash_url.hexdigest(), result["url"])
        if "keyword" in result:
            self.assertEqual(hjob.hash_keyword.hexdigest(), result["keyword"])

if __name__ == '__main__':
    unittest.main(warnings='ignore')
