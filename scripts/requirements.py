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

    pkg, eq, version = pkg.partition("==")
    if eq:
        u = f"https://pypi.org/pypi/{pkg}/{version}/json"
    else:
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

    def append(file):
        files.append(((file["filename"], file["digests"]["sha256"])))

    py3 = None
    wheel = (0, None)
    files = result["files"]
    for u in d["urls"]:
        if u.get("yanked"):
            continue
        if not args.sdist and u["packagetype"] == "sdist":
            continue

        v = u["python_version"]
        if v == "py3":
            py3 = u
            continue

        if args.freethreaded and args.freethreaded(u["filename"]):
            continue
        if args.architecture and not args.architecture(u["filename"]):
            continue
        if args.platform and not args.platform(u["filename"]):
            continue

        if v == "cp314":
            wheel = (99, ())
        elif v.startswith("cp3"):
            if f"-{v}t-" in u["filename"]:
                continue
            v = int(v[3:])
            if v > wheel[0]:
                wheel = (v, [u])
            elif v == wheel[0]:
                wheel[1].append(u)
            continue
        else:
            continue

        append(u)

    if not files and wheel[0]:
        for u in wheel[1]:
            append(u)
    if not files and py3:
        append(py3)

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
    pkgl = pkg.partition("==")[0].lower()
    pkgl, ex, extras = pkgl.partition("[")
    if pkgl in args.exclude:
        return
    if pkgl not in results:
        if ex:
            pkg = pkg.partition("[")[0]
        results[pkgl] = info = package_hashes(pkg, args)

        if args.dependencies > level:
            for dep in info["dependencies"]:
                collect(dep, args, level+1, pkg)

        if not level:
            if ex:
                extras = (extras[:-1],)
            else:
                extras = info["extras"] if args.Extra else args.extra
            for extra in extras:
                for dep in info["extras"][extra]:
                    collect(dep, args, level+1, f"{pkgl}[{extra}]")
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
            if args.filenames:
                for name, sha256 in pkg["files"]:
                    write(f'    # {name} \\\n')
            if pkg["parents"]:
                parents = sorted(set(pkg["parents"]))
                write(f'    # from {", ".join(parents)}\n')


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("-a", "--architecture", action="append", default=[])
    parser.add_argument("-d", "--dependencies", action="count", default=0)
    parser.add_argument("-D", "--Dependencies",
                        dest="dependencies", action="store_const", const=128)
    parser.add_argument("-e", "--extra", action="append", default=[])
    parser.add_argument("-E", "--Extra", action="store_true")
    parser.add_argument("-f", "--freethreaded", action="store_true")
    parser.add_argument("-F", "--filenames", action="store_true")
    parser.add_argument("-i", "--input")
    parser.add_argument("-N", "--no-clobber", default="w",
                        dest="mode", action="store_const", const="x")
    parser.add_argument("-o", "--output")
    parser.add_argument("-O", "--Output")
    parser.add_argument("-p", "--platform", action="append", default=[])
    parser.add_argument("-s", "--sdist", action="store_true")
    parser.add_argument("-x", "--exclude", action="append", default=[])

    parser.add_argument("--x32", "--x86", action="store_true")
    parser.add_argument("--x64", "--x86_64", "--x86-64", "--amd64",
                        action="store_true")
    parser.add_argument("--arm64", action="store_true")

    parser.add_argument("--windows", action="store_true")
    parser.add_argument("--linux", action="store_true")
    parser.add_argument("--manylinux", "--glibc", action="store_true")
    parser.add_argument("--musllinux", action="store_true")
    parser.add_argument("--macosx", "--osx", action="store_true")

    parser.add_argument("PKGS", nargs="*")
    args = parser.parse_args()

    if args.input:
        pkgs = args.PKGS
        with util.open(args.input) as fp:
            for line in fp:
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                pkgs.append(line)

    if args.Output:
        if not args.pkgs:
            args.pkgs = (args.Output,)
        args.output = util.path("requirements", args.Output.lower())
    else:
        args.pkgs = args.PKGS

    if args.freethreaded:
        args.freethreaded = False
    else:
        args.freethreaded = re.compile(
            r"p\d+t-").search

    if args.x32:
        args.architecture.append("win32")
    if args.x64:
        args.architecture.append("x86_64")
        args.architecture.append("amd64")
    if args.arm64:
        args.architecture.append("universal2")
        args.architecture.append("aarch64")
        args.architecture.append("arm64")
    if args.architecture:
        args.architecture = re.compile(
            fr"_(?:{'|'.join(args.architecture)})\.").search

    if args.windows:
        args.platform.append("win")
    if args.linux:
        args.platform.append("manylinux\\d*")
        args.platform.append("musllinux")
    if args.manylinux:
        args.platform.append("manylinux")
    if args.musllinux:
        args.platform.append("musllinux")
    if args.macosx:
        args.platform.append("macosx")
    if args.platform:
        args.platform = re.compile(
            fr"-(?:{'|'.join(args.platform)})_").search

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
