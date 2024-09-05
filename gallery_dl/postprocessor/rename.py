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
            job.register_hooks({
                "prepare": self.rename_from,
            }, options)

        elif new:
            self._old = self._apply_pathfmt
            self._new = self._apply_format(new)
            job.register_hooks({
                "skip"         : self.rename_to_skip,
                "prepare-after": self.rename_to_pafter,
            }, options)

        else:
            raise ValueError("Option 'from' or 'to' is required")

    def rename_from(self, pathfmt):
        name_old = self._old(pathfmt)
        path_old = pathfmt.realdirectory + name_old

        if os.path.exists(path_old):
            name_new = self._new(pathfmt)
            path_new = pathfmt.realdirectory + name_new
            self._rename(path_old, name_old, path_new, name_new)

    def rename_to_skip(self, pathfmt):
        name_old = self._old(pathfmt)
        path_old = pathfmt.realdirectory + name_old

        if os.path.exists(path_old):
            pathfmt.filename = name_new = self._new(pathfmt)
            pathfmt.path = pathfmt.directory + name_new
            pathfmt.realpath = path_new = pathfmt.realdirectory + name_new
            self._rename(path_old, name_old, path_new, name_new)

    def rename_to_pafter(self, pathfmt):
        pathfmt.filename = name_new = self._new(pathfmt)
        pathfmt.path = pathfmt.directory + name_new
        pathfmt.realpath = pathfmt.realdirectory + name_new
        pathfmt.kwdict["_file_recheck"] = True

    def _rename(self, path_old, name_old, path_new, name_new):
        if self.skip and os.path.exists(path_new):
            return self.log.warning(
                "Not renaming '%s' to '%s' since another file with the "
                "same name exists", name_old, name_new)

        self.log.info("'%s' -> '%s'", name_old, name_new)
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
