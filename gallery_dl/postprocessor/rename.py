# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Rename files"""

from .common import PostProcessor
from .. import formatter
import os


class RenamePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        self.skip = options.get("skip", True)
        old = options.get("from")
        new = options.get("to")

        if old:
            self._old = self._apply_format(old)
            self._new = (self._apply_format(new) if new else
                         self._apply_pathfmt)
        elif new:
            self._old = self._apply_pathfmt
            self._new = self._apply_format(new)
        else:
            raise ValueError("Option 'from' or 'to' is required")

        job.register_hooks({"prepare": self.run}, options)

    def run(self, pathfmt):
        old = self._old(pathfmt)
        path_old = pathfmt.realdirectory + old

        if os.path.exists(path_old):
            new = self._new(pathfmt)
            path_new = pathfmt.realdirectory + new

            if self.skip and os.path.exists(path_new):
                return self.log.warning(
                    "Not renaming '%s' to '%s' since another file with the "
                    "same name exists", old, new)

            self.log.info("'%s' -> '%s'", old, new)
            os.replace(path_old, path_new)

    def _apply_pathfmt(self, pathfmt):
        return pathfmt.build_filename(pathfmt.kwdict)

    def _apply_format(self, format_string):
        fmt = formatter.parse(format_string).format_map

        def apply(pathfmt):
            return pathfmt.clean_path(pathfmt.clean_segment(fmt(
                pathfmt.kwdict)))

        return apply


__postprocessor__ = RenamePP
