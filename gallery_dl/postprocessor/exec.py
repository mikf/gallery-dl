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

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)

        try:
            self.args = options["command"]
            self.args[0]  # test if 'args' is subscriptable
        except (KeyError, IndexError, TypeError):
            raise TypeError("option 'command' must be a non-empty list")

        if options.get("async", False):
            self._exec = subprocess.Popen

    def run(self, pathfmt):
        self._exec([
            arg.format_map(pathfmt.keywords)
            for arg in self.args
        ])

    def _exec(self, args):
        retcode = subprocess.Popen(args).wait()
        if retcode:
            self.log.warning(
                "executing '%s' returned non-zero exit status %d",
                " ".join(args), retcode)


__postprocessor__ = ExecPP
