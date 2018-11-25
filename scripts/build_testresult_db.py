#!/usr/bin/env python

import sys
import os.path
import datetime

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
from gallery_dl import extractor, job, config
from test.test_results import setup_test_config


# filter test cases

tests = [
    (idx, extr, url, result)

    for extr in extractor.extractors()
    if hasattr(extr, "test") and extr.test
    if len(sys.argv) <= 1 or extr.category in sys.argv

    for idx, (url, result) in enumerate(extr.test)
    if result
]


# setup target directory

path = os.path.join(ROOTDIR, "archive/testdb", str(datetime.date.today()))
os.makedirs(path, exist_ok=True)


for idx, extr, url, result in tests:

    # filename
    name = "{}-{}-{}.json".format(extr.category, extr.subcategory, idx)
    print(name)

    # config values
    setup_test_config()

    if "options" in result:
        for key, value in result["options"]:
            config.set(key.split("."), value)
    if "range" in result:
        config.set(("image-range",), result["range"])
        config.set(("chapter-range",), result["range"])

    # write test data
    try:
        with open(os.path.join(path, name), "w") as outfile:
            job.DataJob(url, file=outfile, ensure_ascii=False).run()
    except KeyboardInterrupt:
        sys.exit()
