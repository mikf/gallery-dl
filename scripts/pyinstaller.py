#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build a standalone executable using PyInstaller"""

import argparse
import util
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--os")
    parser.add_argument("-a", "--arch")
    parser.add_argument("-l", "--label")
    parser.add_argument("-e", "--extension")
    parser.add_argument("-p", "--print", action="store_true")
    args = parser.parse_args()

    if args.label:
        label = args.label
    else:
        label = ""
        if args.os:
            os = args.os.partition("-")[0].lower()
            if os == "ubuntu":
                os = "linux"
            label += os
        if args.arch == "x86":
            label += "_x86"

    if args.print:
        return print(label)

    name = "gallery-dl"
    if label:
        name = "{}_{}".format(name, label)
    if args.extension:
        name = "{}.{}".format(name, args.extension.lower())

    import PyInstaller.__main__
    return PyInstaller.__main__.run([
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
