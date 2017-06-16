#!/usr/bin/env python

import sys
import os.path
import datetime

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
from gallery_dl import extractor, job, config

tests = [
   ([url[0] for url in extr.test if url[1]], extr)
   for extr in extractor.extractors()
   if hasattr(extr, "test")
]

if len(sys.argv) > 1:
    tests = [
        (urls, extr)
        for urls, extr in tests
        if extr.category in sys.argv
    ]

path = os.path.join(ROOTDIR, "archive/testdb", str(datetime.date.today()))
os.makedirs(path, exist_ok=True)
config.load()

for urls, extr in tests:
    for i, url in enumerate(urls):
        name = "%s-%s-%d.json" % (extr.category, extr.subcategory, i)
        print(name)
        with open(os.path.join(path, name), "w") as outfile:
            job.DataJob(url, outfile).run()
