# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
from .. import util
import subprocess


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
            execute = self.exec_string
        else:
            self.args = [util.Formatter(arg) for arg in args]
            execute = self.exec_list

        events = options.get("event")
        if events is None:
            events = ("after",)
        elif isinstance(events, str):
            events = events.split(",")
        for event in events:
            job.hooks[event].append(execute)

    def exec_list(self, pathfmt, status=None):
        if status:
            return

        kwdict = pathfmt.kwdict
        kwdict["_directory"] = pathfmt.realdirectory
        kwdict["_filename"] = pathfmt.filename
        kwdict["_path"] = pathfmt.realpath

        args = [arg.format_map(kwdict) for arg in self.args]
        self._exec(args, False)

    def exec_string(self, pathfmt, status=None):
        if status:
            return

        if status is None and pathfmt.realpath:
            args = self.args.replace("{}", quote(pathfmt.realpath))
        else:
            args = self.args.replace("{}", quote(pathfmt.realdirectory))

        self._exec(args, True)

    def _exec(self, args, shell):
        self.log.debug("Running '%s'", args)
        retcode = subprocess.Popen(args, shell=shell).wait()
        if retcode:
            self.log.warning("'%s' returned with non-zero exit status (%d)",
                             args, retcode)

    def _exec_async(self, args, shell):
        self.log.debug("Running '%s'", args)
        subprocess.Popen(args, shell=shell)


__postprocessor__ = ExecPP
