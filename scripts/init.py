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


def init_extractor_module(opts):
    try:
        create_extractor_module(opts)
    except FileExistsError:
        LOG.warning("… already present")
    except Exception as exc:
        LOG.error("%s: %s", exc.__class__.__name__, exc, exc_info=exc)

    try:
        create_test_results_file(opts)
    except FileExistsError:
        LOG.warning("… already present")
    except Exception as exc:
        LOG.error("%s: %s", exc.__class__.__name__, exc, exc_info=exc)

    if msg := insert_into_modules_list(opts):
        LOG.warning(msg)

    if opts.get("site_name"):
        if msg := insert_into_supportedsites(opts):
            LOG.warning(msg)


###############################################################################
# File Creation ###############################################################

def create_extractor_module(opts=NONE):
    category = opts["category"]

    path = util.path("gallery_dl", "extractor", f"{category}.py")
    LOG.info("Creating '%s'", trim_path(path))

    type = opts.get("type")
    if type == "manga":
        generate_extractors = generate_extractors_manga
    elif type == "user":
        generate_extractors = generate_extractors_user
    else:
        generate_extractors = generate_extractors_basic

    with util.open(path, opts["open_mode"]) as fp:
        if copyright := opts.get("copyright", ""):
            copyright = f"\n# Copyright {dt.date.today().year} {copyright}\n#"

        fp.write(f'''\
{ENCODING}{copyright}
{LICENSE}
"""Extractors for {opts["root"]}/"""

{generate_extractors(opts)}\
''')


def generate_extractors_basic(opts):
    cat = opts["category"]
    root = opts["root"]

    return f'''\
from .common import Extractor, Message
from .. import text

{build_base_pattern(opts)}

class {cat.capitalize()}Extractor(Extractor):
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{root}"
'''


def generate_extractors_manga(opts):
    cat = opts["category"]
    ccat = cat.capitalize()

    return f'''\
from .common import ChapterExtractor, MangaExtractor
from .. import text

{build_base_pattern(opts)}

class {ccat}Base():
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{opts["root"]}"


class {ccat}ChapterExtractor({ccat}Base, ChapterExtractor):
    """Extractor for {cat} manga chapters"""
    pattern = rf"{{BASE_PATTERN}}/PATH"
    example = ""

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
    example = ""

    def __init__(self, match):
        url = f"{{self.root}}/PATH"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        results = []

        while True:
            results.append((url, None))

        return results
'''


def generate_extractors_user(opts):
    cat = opts["category"]
    ccat = cat.capitalize()
    root = opts["root"]

    return f'''\
from .common import Extractor, Message, Dispatch
from .. import text

{build_base_pattern(opts)}
USER_PATTERN = rf"{{BASE_PATTERN}}/([^/?#]+)"

class {ccat}Extractor(Extractor):
    """Base class for {cat} extractors"""
    category = "{cat}"
    root = "{root}"


class {ccat}UserExtractor(Dispatch, {ccat}Extractor)
    """Extractor for {ccat} user profiles"""
    pattern = rf"{{USER_PATTERN}}/?(?:$|\\?|#)"
    example = "{root}/USER/"

    def items(self):
        base = f"{{self.root}}/"
        return self._dispatch_extractors((
            ({ccat}InfoExtractor, f"{{base}}info"),
        ), ("posts",))
'''


def build_base_pattern(opts):
    domain = opts["domain"]
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

def create_test_results_file(opts=NONE):
    path = util.path("test", "results", f"{opts['category']}.py")
    LOG.info("Creating '%s'", trim_path(path))

    import_stmt = generate_test_result_import(opts)
    with util.open(path, "x") as fp:
        fp.write(f"""\
{ENCODING}
{LICENSE}
{import_stmt}

__tests__ = (

)
""")


def generate_test_result_import(opts):
    category = opts["category"]

    if category[0].isdecimal():
        import_stmt = f"""\
gallery_dl = __import__("gallery_dl.extractor.{category}")
_{category} = getattr(gallery_dl.extractor, "{category}")
"""
    else:
        import_stmt = f"""\
from gallery_dl.extractor import {category}
"""

    return import_stmt


###############################################################################
# Code Modification ###########################################################

def insert_into_modules_list(opts=NONE):
    category = opts["category"]
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


def insert_into_supportedsites(opts):
    category = opts["category"]
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
    line = f'''    "{category}"{ws}: "{opts['site_name']}",\n'''
    lines.insert(idx, line)

    with util.lazy(path) as fp:
        fp.writelines(lines)


###############################################################################
# General #####################################################################

def trim_path(path):
    return path[len(util.ROOTDIR)+1:]


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)

    parser.add_argument("-s", "--site", metavar="TITLE")
    parser.add_argument("-t", "--type", metavar="TYPE")
    parser.add_argument("-c", "--copyright", metavar="NAME")
    parser.add_argument(
        "-C",
        action="store_const", const="Mike Fährmann", dest="copyright")
    parser.add_argument(
        "-F", "--force",
        action="store_const", const="w", default="x", dest="open_mode")
    parser.add_argument(
        "-M", "--manga",
        action="store_const", const="manga", dest="type")
    parser.add_argument(
        "-B", "--base",
        action="store_const", const="base", dest="type")
    parser.add_argument(
        "-U", "--user",
        action="store_const", const="user", dest="type")

    parser.add_argument("category")
    parser.add_argument("root")

    return parser.parse_args()


def parse_opts(args=None):
    args = parse_args(args)

    opts = {
        "category"   : args.category,
        "site_name"  : args.site,
        "type"       : args.type,
        "open_mode"  : args.open_mode,
        "copyright"  : args.copyright,
    }

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

        opts["root"] = root
        opts["domain"] = domain
    else:
        opts["root"] = opts["domain"] = ""

    return opts


def main():
    opts = parse_opts()
    init_extractor_module(opts)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s",
    )
    main()
