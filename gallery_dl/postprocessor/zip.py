# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Add files to ZIP archive"""

from .common import PostProcessor
import zipfile


class ZipPP(PostProcessor):

    def __init__(self, options):
        PostProcessor.__init__(self)

    def run(self, pathfmt):
        with zipfile.ZipFile(pathfmt.realdirectory + ".zip", "a") as zfile:
            zfile.write(pathfmt.realpath, pathfmt.filename)


__postprocessor__ = ZipPP
