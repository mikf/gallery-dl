#!/usr/bin/env python

import sys
import os.path
import urllib.parse

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
import gallery_dl.extractor


categories = {}
skip = ["test", "recursive"]
for extr in gallery_dl.extractor.extractors():
    if extr.category in skip:
        continue
    try:
        categories[extr.category]["sc"].append(extr.subcategory)
    except KeyError:
        url = extr.__doc__.split()[-1]
        if "." not in url[-5:-2]:
            url = sys.modules[extr.__module__].__doc__.split()[-1]
            url = urllib.parse.urlsplit(url).netloc
        if url.startswith("www."):
            url = url[4:]
        categories[extr.category] = {
            "url": url,
            "sc": [extr.subcategory],
        }

outfile = sys.argv[1] if len(sys.argv) > 1 else "supportedsites.rst"
with open(os.path.join(ROOTDIR, outfile), "w") as file:
    file.write("Supported Sites\n"
               "===============\n")
    for info in sorted(categories.values(), key=lambda x: x["url"]):
        file.write("- " + info["url"] + "\n")
