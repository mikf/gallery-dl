#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build a standalone executable using PyInstaller"""

import PyInstaller.__main__
import argparse
import util
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--os")
    parser.add_argument("-a", "--arch")
    parser.add_argument("-e", "--extension")
    args = parser.parse_args()

    name = "gallery-dl"
    if args.os:
        name = "{}_{}".format(name, args.os.partition("-")[0].lower())
    if args.arch == "x86":
        name += "_x86"
    if args.extension:
        name = "{}.{}".format(name, args.extension.lower())

    PyInstaller.__main__.run([
        "--onefile",
        "--console",
        "--name", name,
        "--additional-hooks-dir", util.path("scripts"),
        "--distpath", util.path("dist"),
        "--workpath", util.path("build"),
        "--specpath", util.path("build"),
        util.path("gallery_dl", "__main__.py"),
    ])


if __name__ == "__main__":
    sys.exit(main())
