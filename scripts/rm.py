#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Delete an extractor module"""

import os
import re
import logging
import argparse
import util

LOG = logging.getLogger("rm")


def remove_file(args, path):
    try:
        os.unlink(path)
    except Exception:
        pass


def remove_from_docs_configurationrst(args, path):
    with util.lines(path) as lines:
        needle = f'{args.category}`'
        for idx, line in enumerate(lines):
            if needle in line:
                lines[idx] = ""

        rm = False
        needle = f'extractor.{args.category}.'
        for idx, line in enumerate(lines):
            if rm:
                lines[idx] = ""
                if line == "\n":
                    rm -= 1
            elif line.startswith(needle):
                lines[idx] = ""
                rm = 2


def remove_from_docs_gallerydlconf(args, path):
    rm = False
    needle = f'        "{args.category}":\n'

    with util.lines(path) as lines:
        for idx, line in enumerate(lines):
            if rm:
                lines[idx] = ""
                if line.startswith("        }"):
                    break
            elif line == needle:
                lines[idx] = ""
                rm = True


def remove_from_extractor_init(args, path):
    needle = f'    "{args.category}",\n'

    with util.lines(path) as lines:
        try:
            lines.remove(needle)
        except ValueError:
            pass


def remove_from_scripts_supportedsites(args, path):
    pattern = re.compile(
        r'\s+(\w+\[)?'
        f'"{args.category}"'
        r'(: (\{)?|\] = )')

    with util.lines(path) as lines:
        for idx, line in enumerate(lines):
            if pattern.match(line):
                lines[idx] = ""


def update_docs_supportedsites(args, path):
    import supportedsites
    supportedsites.main()


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)

    parser.add_argument("-g", "--git", action="store_true")
    parser.add_argument("CATEGORY")

    args = parser.parse_args()
    args.category = args.cat = args.CATEGORY
    return args


def main():
    args = parse_args()

    files = [
        (util.path("gallery_dl", "extractor", f"{args.category}.py"),
         remove_file),

        (util.path("test", "results", f"{args.category}.py"),
         remove_file),

        (util.path("docs", "configuration.rst"),
         remove_from_docs_configurationrst),

        (util.path("docs", "gallery-dl.conf"),
         remove_from_docs_gallerydlconf),

        (util.path("gallery_dl", "extractor", "__init__.py"),
         remove_from_extractor_init),

        (util.path("scripts", "supportedsites.py"),
         remove_from_scripts_supportedsites),

        (util.path("docs", "supportedsites.md"),
         update_docs_supportedsites),
    ]

    for path, func in files:
        path_tr = util.trim(path)
        LOG.info(path_tr)

        func(args, path)

        if args.git:
            util.git("add", "--", path_tr)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
