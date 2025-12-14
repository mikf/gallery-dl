# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
from .. import util, formatter
import subprocess
import os


if util.WINDOWS:
    def quote(s):
        s = s.replace('"', '\\"')
        return f'"{s}"'
else:
    from shlex import quote


def trim(args):
    return (args.partition(" ") if isinstance(args, str) else args)[0]


class ExecPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        if cmds := options.get("commands"):
            self.cmds = [self._prepare_cmd(c) for c in cmds]
            execute = self.exec_many
        else:
            execute, self.args = self._prepare_cmd(options["command"])
            if options.get("async", False):
                self._exec = self._popen

        self.verbose = options.get("verbose", True)
        self.session = False
        self.creationflags = 0
        if options.get("session"):
            if util.WINDOWS:
                self.creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                self.session = True

        events = options.get("event")
        if events is None:
            events = ("after",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: execute for event in events}, options)

        if self._archive_init(job, options):
            self._archive_register(job)

    def _prepare_cmd(self, cmd):
        if isinstance(cmd, str):
            self._sub = util.re(
                r"\{(_directory|_filename|_(?:temp)?path|)\}").sub
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
        kwdict["_temppath"] = pathfmt.temppath
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
        if archive := self.archive:
            if archive.check(pathfmt.kwdict):
                return
            self.archive = False

        retcode = 0
        for execute, args in self.cmds:
            self.args = args
            if retcode := execute(pathfmt):
                # non-zero exit status
                break

        if archive:
            self.archive = archive
            archive.add(pathfmt.kwdict)
        return retcode

    def _exec(self, args, shell):
        if retcode := self._popen(args, shell).wait():
            self.log.warning("'%s' returned with non-zero exit status (%d)",
                             args if self.verbose else trim(args), retcode)
        return retcode

    def _popen(self, args, shell):
        self.log.debug("Running '%s'", args if self.verbose else trim(args))
        return util.Popen(
            args,
            shell=shell,
            creationflags=self.creationflags,
            start_new_session=self.session,
        )

    def _replace(self, match):
        name = match[1]
        if name == "_directory":
            return quote(self.pathfmt.realdirectory)
        if name == "_filename":
            return quote(self.pathfmt.filename)
        if name == "_temppath":
            return quote(self.pathfmt.temppath)
        return quote(self.pathfmt.realpath)


__postprocessor__ = ExecPP
