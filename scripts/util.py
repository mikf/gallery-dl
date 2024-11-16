# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import io
import sys

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))


def path(*segments, join=os.path.join):
    result = join(ROOTDIR, *segments)
    os.makedirs(os.path.dirname(result), exist_ok=True)
    return result


class lazy():

    def __init__(self, path):
        self.path = path
        self.buffer = io.StringIO()

    def __enter__(self):
        return self.buffer

    def __exit__(self, exc_type, exc_value, traceback):
        # get content of old file
        try:
            with open(self.path, encoding="utf-8") as fp:
                old = fp.read()
        except Exception:
            old = None

        # get new content
        new = self.buffer.getvalue()

        if new != old:
            # rewrite entire file
            with open(self.path, "w", encoding="utf-8") as fp:
                fp.write(new)
        else:
            # only update atime and mtime
            os.utime(self.path)
