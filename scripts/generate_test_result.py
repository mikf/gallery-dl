#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generate test result data"""

import logging
import argparse
import json
import util
from pyprint import pyprint
from gallery_dl import extractor, job, config

LOG = logging.getLogger("gen-test")


def module_name(opts):
    category = opts["category"]
    if category[0].isdecimal():
        return f"_{category}"
    return category


def generate_test_result(args):
    head = generate_head(args)

    if args.only_matching:
        opts = meta = None
    else:
        if args.options:
            args.options_parsed = options = {}
            for opt in args.options:
                key, _, value = opt.partition("=")
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
                options[key] = value
                config.set((), key, value)
        if args.range:
            config.set((), "image-range"  , args.range)
            config.set((), "chapter-range", args.range)

        djob = job.DataJob(args.extr, file=None)
        djob.filter = dict.copy
        djob.run()

        opts = generate_opts(args, djob.data_urls, djob.exception)
        ool = (len(opts) > 1 or "#options" in opts)

        if args.metadata:
            meta = generate_meta(args, djob.data_meta)
        else:
            meta = None

    result = pyprint(head, oneline=False, lmin=9)
    if opts:
        result = result[:-2] + pyprint(opts, oneline=ool, lmin=9)[1:]
    if meta:
        result = result[:-1] + pyprint(meta, sort=sort_key)[1:]
    return result + ",\n\n"


def generate_head(args):
    head = {}
    cls = args.cls

    head["#url"] = args.extr.url
    if args.comment is not None:
        head["#comment"] = args.comment
    if args.base or args.cat != cls.category or args.sub != cls.subcategory:
        head["#category"] = (args.base, args.cat, args.sub)
    head["#class"] = args.cls

    return head


def generate_opts(args, urls, exc=None):
    opts = {}

    if args.options:
        opts["#options"] = args.options_parsed

    if args.range:
        opts["#range"] = args.range

    if exc:
        opts["#exception"] = exc.__class__
    elif not urls:
        opts["#count"] = 0
    elif len(urls) == 1:
        opts["#results"] = urls[0]
    elif len(urls) < args.limit_urls:
        opts["#results"] = tuple(urls)
    else:
        import re
        opts["#pattern"] = re.escape(urls[0])
        opts["#count"] = len(urls)

    return opts


def generate_meta(args, data):
    if not data:
        return {}

    for kwdict in data:
        delete = ["category", "subcategory"]
        for key in kwdict:
            if not key or key[0] == "_":
                delete.append(key)
        for key in delete:
            del kwdict[key]

    return data[0]


def sort_key(key, value):
    if not value:
        return 0
    if isinstance(value, str) and "\n" in value:
        return 7000
    if isinstance(value, list) and len(value) > 1:
        return 8000
    if isinstance(value, dict):
        return 9000
    return 0


def insert_test_result(args, result, lines):
    idx_block = None
    flag = False

    for idx, line in enumerate(lines):
        line = line.lstrip()
        if not line:
            continue
        elif line[0] == "{":
            idx_block = idx
        elif line.startswith('"#class"'):
            if args.cls.__name__ in line:
                flag = True
            elif flag:
                flag = None
                break

    if idx_block is None or flag is not None:
        lines.insert(-1, result)
    else:
        lines.insert(idx_block, result)


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("-c", "--comment", default=None)
    parser.add_argument("-C", dest="comment", action="store_const", const="")
    parser.add_argument("-g", "--git", action="store_true")
    parser.add_argument("-l", "--limit_urls", type=int, default=10)
    parser.add_argument("-m", "--metadata", action="store_true")
    parser.add_argument("-o", "--option", dest="options", action="append")
    parser.add_argument("-O", "--only-matching", action="store_true")
    parser.add_argument("-r", "--range")
    parser.add_argument("URL")

    return parser.parse_args()


def main():
    args = parse_args()
    args.url = args.URL

    extr = extractor.find(args.url)
    if extr is None:
        LOG.error("Unsupported URL '%s'", args.url)
        raise SystemExit(1)

    args.extr = extr
    args.cls = extr.__class__
    args.cat = extr.category
    args.sub = extr.subcategory
    args.base = extr.basecategory

    LOG.info("Collecting data for '%s'", args.url)
    result = generate_test_result(args)

    path = util.path("test", "results", f"{args.cat}.py")
    path_tr = util.trim(path)
    LOG.info("Writing '%s' results to '%s'", args.url, path_tr)
    with util.lines(path) as lines:
        insert_test_result(args, result, lines)

    if args.git:
        LOG.info("git add %s", path_tr)
        util.git("add", "--", path_tr)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
