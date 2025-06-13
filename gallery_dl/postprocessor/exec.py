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


if util.WINDOWS:
    def quote(s):
        return '"' + s.replace('"', '\\"') + '"'
else:
    from shlex import quote


class ExecPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        cmds = options.get("commands")
        if cmds:
            self.cmds = [self._prepare_cmd(c) for c in cmds]
            execute = self.exec_many
        else:
            execute, self.args = self._prepare_cmd(options["command"])
            if options.get("async", False):
                self._exec = self._exec_async

        events = options.get("event")
        if events is None:
            events = ("after",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: execute for event in events}, options)

        self._init_archive(job, options)

    def _prepare_cmd(self, cmd):
        if isinstance(cmd, str):
            self._sub = util.re(r"\{(_directory|_filename|_path|)\}").sub
            return self.exec_string, cmd
        else:
            return self.exec_list, [formatter.parse(arg) for arg in cmd]

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
        retcode = self._exec(args, False)

        if archive:
            archive.add(kwdict)
        return retcode

    def exec_string(self, pathfmt):
        archive = self.archive
        if archive and archive.check(pathfmt.kwdict):
            return

        self.pathfmt = pathfmt
        args = self._sub(self._replace, self.args)
        retcode = self._exec(args, True)

        if archive:
            archive.add(pathfmt.kwdict)
        return retcode

    def exec_many(self, pathfmt):
        archive = self.archive
        if archive:
            if archive.check(pathfmt.kwdict):
                return
            self.archive = False

        retcode = 0
        for execute, args in self.cmds:
            self.args = args
            retcode = execute(pathfmt)
            if retcode:
                # non-zero exit status
                break

        if archive:
            self.archive = archive
            archive.add(pathfmt.kwdict)
        return retcode

    def _exec(self, args, shell):
        self.log.debug("Running '%s'", args)
        retcode = util.Popen(args, shell=shell).wait()
        if retcode:
            self.log.warning("'%s' returned with non-zero exit status (%d)",
                             args, retcode)
        return retcode

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
