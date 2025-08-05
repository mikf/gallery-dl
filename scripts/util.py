# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import io
import sys
import builtins

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))


def path(*segments):
    result = os.path.join(ROOTDIR, *segments)
    os.makedirs(os.path.dirname(result), exist_ok=True)
    return result


def trim(path):
    return path[len(ROOTDIR)+1:]


def open(path, mode="r"):
    return builtins.open(path, mode, encoding="utf-8", newline="\n")


class lazy():

    def __init__(self, path):
        self.path = path
        self.buffer = io.StringIO()

    def __enter__(self):
        return self.buffer

    def __exit__(self, exc_type, exc_value, traceback):
        # get content of old file
        try:
            with builtins.open(self.path, encoding="utf-8", newline="") as fp:
                old = fp.read()
        except Exception:
            old = None

        # get new content
        new = self.buffer.getvalue()

        if new != old:
            # rewrite entire file
            with builtins.open(
                    self.path, "w", encoding="utf-8", newline="") as fp:
                fp.write(new)
        else:
            # only update atime and mtime
            os.utime(self.path)
