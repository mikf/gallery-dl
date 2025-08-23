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


def init_extractor(args):
    category = args.category

    files = [(util.path("test", "results", f"{category}.py"),
              generate_test, False)]
    if args.init_module:
        files.append((util.path("gallery_dl", "extractor", f"{category}.py"),
                      generate_module, False))
        files.append((util.path("gallery_dl", "extractor", "__init__.py"),
                      insert_into_modules_list, True))
    if args.site_name:
        files.append((util.path("scripts", "supportedsites.py"),
                      insert_into_supportedsites, True))

    for path, func, lines in files:
        LOG.info(util.trim(path))

        if lines:
            with util.lines(path) as lines:
                if not func(args, lines):
                    LOG.warning("'%s' already present", category)
        else:
            try:
                with util.open(path, args.open_mode) as fp:
                    fp.write(func(args))
            except FileExistsError:
                LOG.warning("File already present")
            except Exception as exc:
                LOG.error("%s: %s", exc.__class__.__name__, exc, exc_info=exc)

        if args.git:
            util.git("add", path)


###############################################################################
# Extractor ###################################################################

def generate_module(args):
    type = args.type
    if type == "manga":
        generate_extractors = generate_extractors_manga
    elif type == "user":
        generate_extractors = generate_extractors_user
    else:
        generate_extractors = generate_extractors_basic

    if copyright := args.copyright:
        copyright = f"\n# Copyright {dt.date.today().year} {copyright}\n#"

    return f'''\
{ENCODING}{copyright}
{LICENSE}
"""Extractors for {args.root}/"""

{generate_extractors(args)}\
'''


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

def generate_test(args):
    category = args.category

    if category[0].isdecimal():
        import_stmt = f"""\
gallery_dl = __import__("gallery_dl.extractor.{category}")
_{category} = getattr(gallery_dl.extractor, "{category}")
"""
    else:
        import_stmt = f"""\
from gallery_dl.extractor import {category}
"""

    return f"""\
{ENCODING}
{LICENSE}
{import_stmt}

__tests__ = (
)
"""


###############################################################################
# Modules List ################################################################

def insert_into_modules_list(args, lines):
    category = args.category

    module_name = f'    "{category}",\n'
    if module_name in lines:
        return False

    compare = False
    for idx, line in enumerate(lines):
        if compare:
            cat = text.extr(line, '"', '"')
            if cat == category:
                return False
            if cat > category or cat == "booru":
                break
        elif line.startswith("modules = "):
            compare = True

    lines.insert(idx, module_name)
    return True


###############################################################################
# Supported Sites #############################################################

def insert_into_supportedsites(args, lines):
    category = args.category

    compare = False
    for idx, line in enumerate(lines):
        if compare:
            cat = text.extr(line, '"', '"')
            if cat == category:
                return False
            if cat > category:
                break
        elif line.startswith("CATEGORY_MAP = "):
            compare = True

    ws = " " * max(15 - len(category), 0)
    line = f'''    "{category}"{ws}: "{args.site_name}",\n'''
    lines.insert(idx, line)
    return True


###############################################################################
# Command-Line Options ########################################################

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
        "-g", "--git",
        dest="git", action="store_true")
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
    init_extractor(args)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
