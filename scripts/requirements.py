#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import util
import sys
import re
import argparse
import requests

session = None
results = {}


def package_hashes(pkg, args):
    global session
    if session is None:
        session = requests.Session()

    u = f"https://pypi.org/pypi/{pkg}/json"
    d = session.get(u).json()
    if not (i := d.get("info")):
        return

    n = i["name"]
    results[n.lower()] = result = {
        "name"   : n,
        "version": i["version"],
        "files"  : [],
        "dependencies": [],
        "extras" : {},
        "parents": [],
    }

    files = result["files"]
    for u in d["urls"]:
        if u.get("yanked"):
            continue
        if not args.sdist and u["packagetype"] == "sdist":
            continue
        if not (u["python_version"] == "py3" or
                u["python_version"] == "cp314"):
            continue
        if not args.musllinux and "-musllinux" in u["filename"]:
            continue
        if not args.freethreaded and "-cp314t" in u["filename"]:
            continue
        files.append(((u["filename"], u["digests"]["sha256"])))

    for d in i["requires_dist"] or ():
        name = re.sub(r"([\w-]+).+", r"\1", d).lower()

        pos = d.find(" extra == ")
        if pos < 0:
            result["dependencies"].append(name)
        else:
            extra = d[pos+11:d.find('"', pos+11)]
            if e := result["extras"].get(extra):
                e.append(name)
            else:
                result["extras"][extra] = [name]

    return result


def collect(pkg, args, level=0, parent=None):
    pkg = pkg.replace("_", "-")
    pkgl = pkg.lower()
    if pkgl in args.exclude:
        return
    if pkgl not in results:
        results[pkgl] = info = package_hashes(pkg, args)

        if args.dependencies > level:
            for dep in info["dependencies"]:
                collect(dep, args, level+1, pkg)

        if not level:
            extras = info["extras"] if args.Extra else args.extra
            for extra in extras:
                for dep in info["extras"][extra]:
                    collect(dep, args, level+1, f"{pkg}[{extra}]")
    if parent:
        results[pkgl]["parents"].append(parent)


def output(write, args):
    pkgs = list(results.values())
    pkgs.sort(key=lambda p: (
        bool(p["parents"]), len(p["files"]), p["name"].lower()))

    first = True
    for pkg in pkgs:
        if pkg["files"]:
            if first:
                first = False
            else:
                write("\n")

            write(f'{pkg["name"]}=={pkg["version"]} \\\n')
            for name, sha256 in pkg["files"]:
                write(f'    --hash=sha256:{sha256} \\\n')
            if pkg["parents"]:
                parents = sorted(set(pkg["parents"]))
                write(f'    # from {", ".join(parents)}\n')


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("-d", "--dependencies", action="count", default=0)
    parser.add_argument("-D", "--Dependencies",
                        dest="dependencies", action="store_const", const=128)
    parser.add_argument("-e", "--extra", action="append", default=[])
    parser.add_argument("-E", "--Extra", action="store_true")
    parser.add_argument("-f", "--freethreaded", action="store_true")
    parser.add_argument("-m", "--musllinux", action="store_true")
    parser.add_argument("-N", "--no-clobber", default="w",
                        dest="mode", action="store_const", const="x")
    parser.add_argument("-o", "--output", )
    parser.add_argument("-O", "--Output")
    parser.add_argument("-s", "--sdist", action="store_true")
    parser.add_argument("-x", "--exclude", action="append", default=[])
    parser.add_argument("PKGS", nargs="*")

    args = parser.parse_args()

    if args.Output:
        args.pkgs = (args.Output,)
        args.output = util.path("requirements", args.Output.lower())
    else:
        args.pkgs = args.PKGS

    return args


def main():
    args = parse_args()
    for pkg in args.pkgs:
        collect(pkg, args)

    if not args.output or args.output == "-":
        output(sys.stdout.write, args)
    else:
        with util.lazy(args.output, args.mode) as fp:
            output(fp.write, args)


if __name__ == "__main__":
    main()
