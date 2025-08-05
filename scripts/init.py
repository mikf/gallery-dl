#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Initialize extractor modules"""

import re
import logging
import argparse
import datetime as dt
import util  # noqa

from gallery_dl import text

LOG = logging.getLogger("init")
NONE = {}
ENCODING = """\
# -*- coding: utf-8 -*-
"""
LICENSE = """\
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
"""


def init_extractor_module(args):
    if args.init_module:
        try:
            create_extractor_module(args)
        except FileExistsError:
            LOG.warning("… already present")
        except Exception as exc:
            LOG.error("%s: %s", exc.__class__.__name__, exc, exc_info=exc)

        if msg := insert_into_modules_list(args):
            LOG.warning(msg)

    try:
        create_test_results_file(args)
    except FileExistsError:
        LOG.warning("… already present")
    except Exception as exc:
        LOG.error("%s: %s", exc.__class__.__name__, exc, exc_info=exc)

    if args.site_name:
        if msg := insert_into_supportedsites(args):
            LOG.warning(msg)


###############################################################################
# File Creation ###############################################################

def create_extractor_module(args):
    category = args.category

    path = util.path("gallery_dl", "extractor", f"{category}.py")
    LOG.info("Creating '%s'", util.trim(path))

    type = args.type
    if type == "manga":
        generate_extractors = generate_extractors_manga
    elif type == "user":
        generate_extractors = generate_extractors_user
    else:
        generate_extractors = generate_extractors_basic

    with util.open(path, args.open_mode) as fp:
        if copyright := args.copyright:
            copyright = f"\n# Copyright {dt.date.today().year} {copyright}\n#"

        fp.write(f'''\
{ENCODING}{copyright}
{LICENSE}
"""Extractors for {args.root}/"""

{generate_extractors(args)}\
''')


def generate_extractors_basic(args):
    cat = args.category

    return f'''\
from .common import Extractor, Message
from .. import text

{build_base_pattern(args)}

class {cat.capitalize()}Extractor(Extractor):
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{args.root}"
'''


def generate_extractors_manga(args):
    cat = args.category
    ccat = cat.capitalize()

    return f'''\
from .common import ChapterExtractor, MangaExtractor
from .. import text

{build_base_pattern(args)}

class {ccat}Base():
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{args.root}"


class {ccat}ChapterExtractor({ccat}Base, ChapterExtractor):
    """Extractor for {cat} manga chapters"""
    pattern = rf"{{BASE_PATTERN}}/PATH"
    example = "{args.root}/..."

    def __init__(self, match):
        url = f"{{self.root}}/PATH"
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        chapter, sep, minor = chapter.partition(".")

        return {{
            "manga"   : text.unescape(manga),
            "manga_id": text.parse_int(manga_id),
            "title"   : "",
            "volume"  : text.parse_int(volume),
            "chapter" : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : text.parse_int(chapter_id),
            "lang"    : "en",
            "language": "English",
        }}

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(page, "", "")
        ]


class {ccat}MangaExtractor({ccat}Base, MangaExtractor):
    """Extractor for {cat} manga"""
    chapterclass = {ccat}ChapterExtractor
    pattern = rf"{{BASE_PATTERN}}/PATH"
    example = "{args.root}/..."

    def __init__(self, match):
        url = f"{{self.root}}/PATH"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        results = []

        while True:
            results.append((url, None))

        return results
'''


def generate_extractors_user(args):
    cat = args.category
    ccat = cat.capitalize()

    return f'''\
from .common import Extractor, Message, Dispatch
from .. import text

{build_base_pattern(args)}
USER_PATTERN = rf"{{BASE_PATTERN}}/([^/?#]+)"

class {ccat}Extractor(Extractor):
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{args.root}"


class {ccat}UserExtractor(Dispatch, {ccat}Extractor)
    """Extractor for {cat} user profiles"""
    pattern = rf"{{USER_PATTERN}}/?(?:$|\\?|#)"
    example = "{args.root}/USER/"

    def items(self):
        base = f"{{self.root}}/"
        return self._dispatch_extractors((
            ({ccat}InfoExtractor, f"{{base}}info"),
        ), ("posts",))
'''


def build_base_pattern(args):
    domain = args.domain
    if domain.count(".") > 1:
        subdomain, domain, tld = domain.rsplit(".", 2)
        domain = f"{domain}.{tld}"
        if subdomain == "www":
            subdomain = "(?:www\\.)?"
        else:
            subdomain = re.escape(subdomain + ".")
    else:
        subdomain = "(?:www\\.)?"

    return f"""\
BASE_PATTERN = r"(?:https?://)?{subdomain}{re.escape(domain)}"
"""


###############################################################################
# Test Results ################################################################

def create_test_results_file(args):
    path = util.path("test", "results", f"{args.category}.py")
    LOG.info("Creating '%s'", util.trim(path))

    import_stmt = generate_test_result_import(args)
    with util.open(path, "x") as fp:
        fp.write(f"""\
{ENCODING}
{LICENSE}
{import_stmt}

__tests__ = (
)
""")


def generate_test_result_import(args):
    cat = args.category

    if cat[0].isdecimal():
        import_stmt = f"""\
gallery_dl = __import__("gallery_dl.extractor.{cat}")
_{cat} = getattr(gallery_dl.extractor, "{cat}")
"""
    else:
        import_stmt = f"""\
from gallery_dl.extractor import {cat}
"""

    return import_stmt


###############################################################################
# Code Modification ###########################################################

def insert_into_modules_list(args):
    category = args.category
    LOG.info("Adding '%s' to gallery_dl/extractor/__init__.py modules list",
             category)

    path = util.path("gallery_dl", "extractor", "__init__.py")
    with util.open(path) as fp:
        lines = fp.readlines()

    module_name = f'    "{category}",\n'
    if module_name in lines:
        return "… already present"

    compare = False
    for idx, line in enumerate(lines):
        if compare:
            cat = text.extr(line, '"', '"')
            if cat == category:
                return "… already present"
            if cat > category or cat == "booru":
                break
        elif line.startswith("modules = "):
            compare = True

    lines.insert(idx, module_name)
    with util.lazy(path) as fp:
        fp.writelines(lines)


def insert_into_supportedsites(args):
    category = args.category
    LOG.info("Adding '%s' to scripts/supportedsites.py category list",
             category)

    path = util.path("scripts", "supportedsites.py")
    with util.open(path) as fp:
        lines = fp.readlines()

    compare = False
    for idx, line in enumerate(lines):
        if compare:
            cat = text.extr(line, '"', '"')
            if cat == category:
                return "… already present"
            if cat > category:
                break
        elif line.startswith("CATEGORY_MAP = "):
            compare = True

    ws = " " * max(15 - len(category), 0)
    line = f'''    "{category}"{ws}: "{args.site_name}",\n'''
    lines.insert(idx, line)

    with util.lazy(path) as fp:
        fp.writelines(lines)


###############################################################################
# General #####################################################################

def parse_args(args=None):
    parser = argparse.ArgumentParser(args)

    parser.add_argument(
        "-s", "--site",
        dest="site_name", metavar="TITLE")
    parser.add_argument(
        "-c", "--copyright",
        dest="copyright", metavar="NAME")
    parser.add_argument(
        "-C",
        dest="copyright", action="store_const", const="Mike Fährmann")
    parser.add_argument(
        "-F", "--force",
        dest="open_mode", action="store_const", const="w", default="x")
    parser.add_argument(
        "-M", "--no-module",
        dest="init_module", action="store_false")
    parser.add_argument(
        "-t", "--type",
        dest="type", metavar="TYPE")
    parser.add_argument(
        "--manga",
        dest="type", action="store_const", const="manga")
    parser.add_argument(
        "--base",
        dest="type", action="store_const", const="base")
    parser.add_argument(
        "--user",
        dest="type", action="store_const", const="user")

    parser.add_argument("category")
    parser.add_argument("root", nargs="?")

    args = parser.parse_args()

    if root := args.root:
        if "://" in root:
            root = root.rstrip("/")
            domain = root[root.find("://")+3:]
        else:
            root = root.strip(":/")
            domain = root
            root = f"https://{root}"

        if domain.startswith("www."):
            domain = domain[4:]

        args.root = root
        args.domain = domain
    elif args.init_module:
        parser.error("'root' URL required")
    else:
        args.domain = ""

    return args


def main():
    args = parse_args()
    init_extractor_module(args)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
