#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Find missing settings in docs/gallery.conf"""

import json
import util
import sys
import re

from gallery_dl import text, extractor


def read(fname):
    path = util.path("docs", fname)
    try:
        with open(path) as fp:
            return fp.read()
    except Exception as exc:
        sys.exit("Unable to read {} ({}: {})".format(
            path, exc.__class__.__name__, exc))


DOCS = read("configuration.rst")
CONF = json.loads(read("gallery-dl.conf"))
EXTRS = list(extractor._list_classes())


def opts_general(type):
    # general opts
    opts = re.findall(
        r"(?m)^{}\.\*\.([\w-]+)".format(type),
        DOCS)
    extr = CONF[type]

    return {
        type + ".*." + opt
        for opt in opts
        if opt not in extr
    }


def opts_category(type):
    # site opts
    opts = re.findall(
        r"(?m)^{}\.(?!\*)([\w-]+)\.([\w-]+)(?:\.([\w-]+))?".format(type),
        DOCS)
    extr = CONF[type]

    result = set()
    for category, sub, opt in opts:
        if category[0] == "[":
            category = category[1:-1]
        category_opts = extr.get(category)
        if not category_opts:
            result.add(category + ".*")
            continue

        if not opt:
            opt = sub
            sub = None
        elif sub:
            category_opts = category_opts.get(sub) or ()
        if opt not in category_opts:
            if sub:
                opt = sub + "." + opt
            result.add(category + "." + opt)
    return result


def userpass():
    block = text.extr(DOCS, "extractor.*.username", "extractor.*.")
    extr = CONF["extractor"]

    result = set()
    for category in text.extract_iter(block, "* ``", "``"):
        opts = extr[category]
        if "username" not in opts or "password" not in opts:
            result.add(category)
    return result


def sleeprequest():
    block = text.extr(DOCS, "extractor.*.sleep-request", "extractor.*.")

    sleep = {}
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue

        if line[0] == "*":
            value = line.strip('* `"')
            if value == "0":
                break
        elif line[0] == "`":
            cat, _, sub = line.strip("`,").partition(":")
            sleep[cat.strip("[]")] = value

    result = {}
    for extr in EXTRS:
        value = sleep.get(extr.category)
        if value:
            category = extr.category
        else:
            value = sleep.get(extr.basecategory)
            if value:
                category = extr.basecategory
            else:
                continue

        min, _, max = value.partition("-")
        tup = (float(min), float(max))
        if tup != extr.request_interval:
            result[category] = extr.request_interval
    return result


write = sys.stdout.write

opts = set()
opts.update(opts_general("extractor"))
opts.update(opts_general("downloader"))
opts.update(opts_category("extractor"))
opts.update(opts_category("downloader"))
if opts:
    write("Missing Options:\n")
    for opt in sorted(opts):
        write("    {}\n".format(opt))
    write("\n")


categories = userpass()
if categories:
    write("Missing username & password:\n")
    for cat in sorted(categories):
        write("    {}\n".format(cat))
    write("\n")


categories = sleeprequest()
if categories:
    write("Wrong sleep_request:\n")
    for cat, value in sorted(categories.items()):
        write("    {}: {}\n".format(cat, value))
    write("\n")
