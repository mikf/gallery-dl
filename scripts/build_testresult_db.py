#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Collect results of extractor unit tests"""

import sys
import os.path
import datetime

import util
from gallery_dl import extractor, job, config
from test.test_results import setup_test_config


# filter test cases

tests = [
    (idx, extr, url, result)

    for extr in extractor.extractors()
    if hasattr(extr, "test") and extr.test
    if len(sys.argv) <= 1 or extr.category in sys.argv

    for idx, (url, result) in enumerate(extr._get_tests())
    if result
]


# setup target directory

path = util.path("archive", "testdb", str(datetime.date.today()))
os.makedirs(path, exist_ok=True)


for idx, extr, url, result in tests:

    # filename
    name = "{}-{}-{}.json".format(extr.category, extr.subcategory, idx)
    print(name)

    # config values
    setup_test_config()

    if "options" in result:
        for key, value in result["options"]:
            key = key.split(".")
            config.set(key[:-1], key[-1], value)
    if "range" in result:
        config.set((), "image-range"  , result["range"])
        config.set((), "chapter-range", result["range"])

    # write test data
    try:
        with open(os.path.join(path, name), "w") as outfile:
            job.DataJob(url, file=outfile, ensure_ascii=False).run()
    except KeyboardInterrupt:
        sys.exit()
