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
import util

LOG = logging.getLogger("gen-test")


def module_name(opts):
    category = opts["category"]
    if category[0].isdecimal():
        return f"_{category}"
    return category


def generate_test_result(args):
    cls = args.cls
    extr = args.extr

    if args.comment is not None:
        comment = args.comment if isinstance(args.comment, str) else ""
        comment = (
            f'    "#comment": "{comment}",\n')
    else:
        comment = ""

    if (args.base or args.cat != cls.category or args.sub != cls.subcategory):
        categories = (
            f'    "#category": ("{args.base}", "{args.cat}", "{args.sub}"),\n')
    else:
        categories = ""

    extr_name = args.cls.__name__
    module_name = args.extr.__module__.rpartition(".")[2]

    head = f"""
{{
    "#url"     : "{extr.url}",
{comment}\
{categories}\
    "#class"   : {module_name}.{extr_name},
"""

    tail = """\
},
"""

    from gallery_dl.extractor import common

    if isinstance(extr, common.GalleryExtractor):
        body = """
    "#pattern" : r"",
    "#count"   : 123,
"""
    elif isinstance(extr, common.MangaExtractor):
        extr_name = extr_name.replace("MangaEx", "ChapterEx")
        body = f"""
    "#pattern" : {module_name}.{extr_name}.pattern,
    "#count"   : 123,
"""
    else:
        body = ""

    return f"{head}{body}{tail}"


def collect_extractor_results(extr):
    return ()


def insert_test_result(args, result):
    path = util.path("test", "results", f"{args.cat}.py")
    LOG.info("Adding '%s:%s' test result into '%s'", args.cat, args.sub, path)

    with util.open(path) as fp:
        lines = fp.readlines()

    lines.insert(-2, result)

    with util.lazy(path) as fp:
        fp.writelines(lines)


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("-c", "--comment", default=None)
    parser.add_argument("-C", dest="comment", action="store_const", const="")
    parser.add_argument("URL")

    return parser.parse_args()


def main():
    args = parse_args()
    args.url = args.URL

    from gallery_dl.extractor import find
    extr = find(args.url)
    if extr is None:
        LOG.error("Unsupported URL '%s'", args.url)
        raise SystemExit(1)

    args.extr = extr
    args.cls = extr.__class__
    args.cat = extr.category
    args.sub = extr.subcategory
    args.base = extr.basecategory

    result = generate_test_result(args)
    insert_test_result(args, result)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
