#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Create testdata for extractor tests"""

import argparse
from  gallery_dl import job, config

TESTDATA_FMT = """
    test = [("{}", {{
        "url": "{}",
        "keyword": "{}",
        "content": "{}",
    }})]
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", action="store_true")
    parser.add_argument("urls", nargs="*")
    args = parser.parse_args()

    config.load()
    for url in args.urls:
        hjob = job.HashJob(url, content=args.content)
        hjob.run()
        print(hjob.extractor.__class__.__name__)
        print(TESTDATA_FMT.format(url, hjob.hash_url.hexdigest(),
            hjob.hash_keyword.hexdigest(), hjob.hash_content.hexdigest()))

if __name__ == '__main__':
    main()
