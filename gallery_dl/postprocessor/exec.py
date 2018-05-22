# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
import subprocess


class ExecPP(PostProcessor):

    def __init__(self, options):
        PostProcessor.__init__(self)
        self.args = options["args"]

    def run(self, pathfmt):
        args = [
            arg.format_map(pathfmt.keywords)
            for arg in self.args
        ]
        subprocess.Popen(args)


__postprocessor__ = ExecPP
