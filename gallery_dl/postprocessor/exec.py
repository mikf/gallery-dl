# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
from .. import util, formatter
import os
import re


if util.WINDOWS:
    def quote(s):
        return '"' + s.replace('"', '\\"') + '"'
else:
    from shlex import quote


class ExecPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        if options.get("async", False):
            self._exec = self._exec_async

        args = options["command"]
        if isinstance(args, str):
            self.args = args
            self._sub = re.compile(r"\{(_directory|_filename|_path|)\}").sub
            execute = self.exec_string
        else:
            self.args = [formatter.parse(arg) for arg in args]
            execute = self.exec_list

        events = options.get("event")
        if events is None:
            events = ("after",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: execute for event in events}, options)

        self._init_archive(job, options)

    def exec_list(self, pathfmt):
        archive = self.archive
        kwdict = pathfmt.kwdict

        if archive and archive.check(kwdict):
            return

        kwdict["_directory"] = pathfmt.realdirectory
        kwdict["_filename"] = pathfmt.filename
        kwdict["_path"] = pathfmt.realpath

        args = [arg.format_map(kwdict) for arg in self.args]
        args[0] = os.path.expanduser(args[0])
        self._exec(args, False)

        if archive:
            archive.add(kwdict)

    def exec_string(self, pathfmt):
        archive = self.archive
        if archive and archive.check(pathfmt.kwdict):
            return

        self.pathfmt = pathfmt
        args = self._sub(self._replace, self.args)
        self._exec(args, True)

        if archive:
            archive.add(pathfmt.kwdict)

    def _exec(self, args, shell):
        self.log.debug("Running '%s'", args)
        retcode = util.Popen(args, shell=shell).wait()
        if retcode:
            self.log.warning("'%s' returned with non-zero exit status (%d)",
                             args, retcode)

    def _exec_async(self, args, shell):
        self.log.debug("Running '%s'", args)
        util.Popen(args, shell=shell)

    def _replace(self, match):
        name = match.group(1)
        if name == "_directory":
            return quote(self.pathfmt.realdirectory)
        if name == "_filename":
            return quote(self.pathfmt.filename)
        return quote(self.pathfmt.realpath)


__postprocessor__ = ExecPP
